# Raspberry Pi Hub Deployment Architecture

## Overview

The Raspberry Pi 5 serves as the **central hub** for the Whispering Machine system, running all core services locally and providing the touchscreen UI for party tracking.

### Hardware
- **Raspberry Pi 5** (hub node)
- **INMP441 I²S Microphone** (wired to Pi GPIO)
- **7" Touchscreen** (primary UI display)
- **Network**: GL-MT300N-V2 travel router (LAN for Pi + ESP32 nodes)
- **Tailscale**: Pi only (advertises LAN route to unRAID)

### Network Topology
```
Internet
  ↓
GL-MT300N-V2 Router (LAN: 192.168.8.x)
  ├─ Raspberry Pi 5 (hub, Tailscale client)
  ├─ ESP32 node1 (WiFi)
  └─ ESP32 node2 (WiFi)
  
Pi Tailscale ←→ unRAID (faster-whisper on port 10300)
```

**Key Design**: Pi is the only device that talks to unRAID (via Tailscale). ESP32 nodes only talk to Pi's MQTT broker.

---

## Services Architecture

### Running on Pi (Docker Compose)
1. **Mosquitto** - MQTT broker (port 1883 internal, 1884 host)
2. **Aggregator** - Subscribes to all nodes, computes metrics, publishes UI state
3. **UI** - FastAPI + WebSocket, serves party tracker on touchscreen
4. **Audio Bridge** (NEW) - Captures from INMP441, transcribes via unRAID Whisper

### Running on unRAID (External)
- **faster-whisper** - Transcription service (port 10300, Wyoming protocol)

### Running on ESP32 Nodes (Firmware)
- Audio features, PIR, encoder, button, LED ring (unchanged)
- Publish to Pi's MQTT broker at `192.168.8.x:1883`

---

## Audio Bridge Service (New)

**Purpose**: Capture audio from Pi's INMP441 mic, chunk into WAV segments, send to unRAID for transcription, publish results to MQTT.

### Implementation
- **Location**: `services/audio_bridge/`
- **Language**: Python 3.10
- **Dependencies**: `pyaudio`, `wave`, `httpx`, `paho-mqtt`

### Flow
```
ALSA (INMP441) → Audio Bridge
  ↓ (chunk 2-5s WAV)
HTTP POST → unRAID faster-whisper (Wyoming)
  ↓ (transcript JSON)
Audio Bridge → MQTT publish
  ↓
party/<house>/pihub/speech/transcript
```

### MQTT Message Schema
```json
{
  "text": "hello there",
  "confidence": 0.95,
  "duration_ms": 2340,
  "model": "tiny-int8",
  "trigger": "manual|vad|button",
  "ts_ms": 1234567890
}
```

### Configuration (`.env`)
```bash
# Audio capture
AUDIO_DEVICE_INDEX=0
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_DURATION_MS=3000
AUDIO_SILENCE_THRESHOLD=500

# Whisper service
WHISPER_URL=http://100.x.x.x:10300  # Tailscale IP of unRAID
WHISPER_MODEL=tiny-int8
WHISPER_LANGUAGE=en

# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_HOUSE_ID=houseA
```

---

## Pi Stack Structure

```
pi/
├── compose.yml              # Docker Compose for Pi services
├── .env.example             # Template for secrets
├── README.md                # Pi-specific setup guide
└── overlays/
    └── i2s-mems.txt         # I²S overlay config for INMP441
```

### `pi/compose.yml` (Draft)
```yaml
version: '3.8'

services:
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: pi_mosquitto
    ports:
      - "1883:1883"
      - "1884:1884"
    volumes:
      - ../infra/mosquitto.conf:/mosquitto/config/mosquitto.conf
    restart: unless-stopped

  aggregator:
    build:
      context: ../services/aggregator
    container_name: pi_aggregator
    depends_on:
      - mosquitto
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
      - HOUSE_ID=${HOUSE_ID:-houseA}
    restart: unless-stopped

  ui:
    build:
      context: ../services/ui
    container_name: pi_ui
    depends_on:
      - mosquitto
    ports:
      - "8000:8000"
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    restart: unless-stopped

  audio_bridge:
    build:
      context: ../services/audio_bridge
    container_name: pi_audio_bridge
    depends_on:
      - mosquitto
    devices:
      - /dev/snd:/dev/snd  # ALSA audio devices
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
      - WHISPER_URL=${WHISPER_URL}
      - AUDIO_DEVICE_INDEX=${AUDIO_DEVICE_INDEX:-0}
    restart: unless-stopped
```

---

## Bootstrap & Deployment Scripts

### `scripts/pi_bootstrap.sh`
**Purpose**: One-time Pi setup (run on Pi via SSH)

**Tasks**:
1. Update system packages
2. Install Docker + Docker Compose plugin
3. Install Tailscale (optional, for unRAID access)
4. Enable I²S overlay for INMP441
5. Add user to `docker` group
6. Clone repo to `/home/pi/whispering-machine`

**Usage**:
```bash
ssh pi@192.168.8.x
curl -sSL https://raw.githubusercontent.com/USER/whispering-machine/main/scripts/pi_bootstrap.sh | bash
# Reboot after completion
```

### `scripts/pi_deploy.sh`
**Purpose**: Deploy updates from unRAID to Pi

**Tasks**:
1. SSH to Pi
2. Pull latest from GitHub
3. Run `docker compose -f pi/compose.yml up -d --build`
4. Show logs

**Usage** (from unRAID):
```bash
./scripts/pi_deploy.sh
```

**Environment**:
- `PI_HOST=192.168.8.x` (or Tailscale IP)
- `PI_USER=pi`
- `PI_SSH_KEY=~/.ssh/id_rsa`

---

## I²S INMP441 Wiring & Setup

### Wiring (Pi 5 GPIO)
| INMP441 Pin | Pi 5 GPIO Pin | BCM Pin | Function |
|-------------|---------------|---------|----------|
| VDD         | Pin 1         | 3.3V    | Power    |
| GND         | Pin 6         | GND     | Ground   |
| SD          | Pin 12        | GPIO18  | Data     |
| WS          | Pin 35        | GPIO19  | Word Sel |
| SCK         | Pin 40        | GPIO21  | Clock    |
| L/R         | GND           | -       | Left ch  |

### Enable I²S Overlay
**Edit** `/boot/firmware/config.txt`:
```bash
dtoverlay=i2s-mems
```

**Reboot**:
```bash
sudo reboot
```

**Verify**:
```bash
arecord -l
# Should show: card X: sndrpii2scard [snd_rpi_i2s_card]
```

### Test Recording
```bash
arecord -D plughw:X,0 -f S32_LE -r 16000 -c 1 -d 5 test.wav
aplay test.wav
```

---

## UI Updates for Pi Hub

### New UI Features
1. **Transcript Panel** - Show latest speech transcripts from Pi hub
2. **Hub Health** - Show Pi audio bridge status, Whisper connection
3. **Multi-Node View** - Unified view of all nodes (ESP32 + Pi hub)

### MQTT Topics to Display
- `party/<house>/pihub/speech/transcript` - Transcribed text
- `party/<house>/pihub/audio/features` - Pi mic audio features (optional)
- `party/<house>/pihub/sys/heartbeat` - Pi health

### Component Reuse
- `StatusTable` - Show transcript history
- `ConnectionStatus` - Add Whisper connection indicator
- `SignalChart` - Plot Pi audio features alongside ESP32

---

## Deployment Workflow

### Development (unRAID)
1. Make changes to code on unRAID
2. Test locally with `./dev.sh up`
3. Commit and push to GitHub

### Deployment (Pi)
1. Run `./scripts/pi_deploy.sh` from unRAID
2. Script SSHes to Pi, pulls repo, rebuilds containers
3. Verify on Pi touchscreen at `http://localhost:8000`

### Optional: Auto-Deploy on Boot
**Create** `/etc/systemd/system/whispering-machine.service`:
```ini
[Unit]
Description=Whispering Machine Services
After=network.target docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/whispering-machine
ExecStart=/usr/bin/docker compose -f pi/compose.yml up -d
ExecStop=/usr/bin/docker compose -f pi/compose.yml down

[Install]
WantedBy=multi-user.target
```

**Enable**:
```bash
sudo systemctl enable whispering-machine
sudo systemctl start whispering-machine
```

---

## Testing Checklist

### Bootstrap (One-Time)
- [ ] Pi boots and connects to WiFi
- [ ] Tailscale installed and authenticated
- [ ] I²S overlay enabled, INMP441 detected
- [ ] Docker + Compose installed
- [ ] Repo cloned to `/home/pi/whispering-machine`

### Deployment (Every Update)
- [ ] `pi_deploy.sh` completes without errors
- [ ] All containers start: `mosquitto`, `aggregator`, `ui`, `audio_bridge`
- [ ] MQTT broker reachable from ESP32 nodes
- [ ] UI loads on touchscreen at `http://localhost:8000`
- [ ] Audio bridge captures from INMP441
- [ ] Transcripts appear in UI within 5 seconds

### Integration
- [ ] ESP32 nodes publish to Pi MQTT broker
- [ ] Aggregator processes all node data
- [ ] UI shows all nodes (ESP32 + Pi hub)
- [ ] Audio bridge sends clips to unRAID Whisper
- [ ] Transcripts published to MQTT
- [ ] Touchscreen UI updates in real-time

---

## Troubleshooting

### MQTT Connection Issues
```bash
# On Pi, check if broker is running
docker logs pi_mosquitto

# From ESP32, test connection
mosquitto_pub -h 192.168.8.x -t test -m "hello"
```

### I²S Audio Issues
```bash
# Check if device is detected
arecord -l

# Test capture
arecord -D plughw:X,0 -f S32_LE -r 16000 -c 1 -d 5 test.wav

# Check permissions
groups $USER  # Should include 'audio'
```

### Whisper Connection Issues
```bash
# From Pi, test Tailscale connectivity
ping 100.x.x.x  # unRAID Tailscale IP

# Test Whisper endpoint
curl http://100.x.x.x:10300/health
```

### Container Logs
```bash
# On Pi
docker logs pi_audio_bridge --tail 50
docker logs pi_aggregator --tail 50
docker logs pi_ui --tail 50
```

---

## Performance Expectations

### Pi 5 Resources
- **CPU**: 4-core ARM Cortex-A76 @ 2.4 GHz
- **RAM**: 8 GB (recommended for this workload)
- **Expected Load**:
  - Mosquitto: ~5% CPU, ~50 MB RAM
  - Aggregator: ~10% CPU, ~100 MB RAM
  - UI: ~15% CPU, ~150 MB RAM
  - Audio Bridge: ~20% CPU, ~100 MB RAM
  - **Total**: ~50% CPU, ~400 MB RAM (plenty of headroom)

### Transcription Latency
- **Audio capture**: 2-5 seconds (chunk duration)
- **Network**: <100ms (Pi → unRAID via Tailscale)
- **Whisper**: 1-2 seconds (tiny-int8 on unRAID CPU)
- **MQTT publish**: <10ms
- **Total**: ~3-8 seconds end-to-end

---

## Future Enhancements

### Phase 2
- Build images on unRAID, push to GHCR
- Pi pulls pre-built images (faster deployment)
- GitHub Actions for CI/CD

### Phase 3
- Voice activity detection (VAD) for smarter recording
- Wake word detection ("Hey Party")
- Speaker diarization (who said what)
- Sentiment analysis (mood from speech)

---

## Definition of Done

**Success Criteria**:
1. Run `scripts/pi_bootstrap.sh` once on Pi → completes without errors
2. Run `scripts/pi_deploy.sh` from unRAID → deploys in <60 seconds
3. MQTT broker running on Pi, ESP32 nodes connected
4. Audio bridge captures from INMP441, sends to Whisper
5. Transcripts appear in UI within 5 seconds
6. Touchscreen shows live party tracker UI
7. System runs continuously without intervention

**Current Status**: Architecture defined, ready for implementation.


