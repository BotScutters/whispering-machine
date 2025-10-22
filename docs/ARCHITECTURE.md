# Whispering Machine – Architecture

## Overview

### Deployment Architecture (MVP)
- **Raspberry Pi 5 Hub:** Central controller running all services locally
  - **Mosquitto:** MQTT broker (port 1883 internal, 1884 host)
  - **Aggregator:** Subscribes to all nodes, computes metrics, publishes UI state
  - **UI:** FastAPI + WebSocket, serves party tracker on 7" touchscreen
  - **Audio Bridge:** Captures from INMP441 mic, sends to Whisper, publishes transcripts
- **ESP32 Nodes (x2):** Remote sensors publishing to Pi's MQTT broker
  - Audio features, PIR, encoder, button, LED ring
  - Connect via WiFi to local router (GL-MT300N-V2)
- **unRAID Server:** External transcription service (via Tailscale)
  - **faster-whisper:** Port 10300, Wyoming protocol (managed outside this repo)
  - Pi connects via Tailscale for audio transcription

### Network Topology
```
Internet → GL-MT300N-V2 Router (LAN: 192.168.8.x)
  ├─ Raspberry Pi 5 (hub, runs all services, Tailscale client)
  ├─ ESP32 node1 (WiFi, publishes to Pi MQTT)
  └─ ESP32 node2 (WiFi, publishes to Pi MQTT)

Pi Tailscale ←→ unRAID (faster-whisper transcription)
```

**Key Design**: Pi is self-contained and portable. Only needs internet for Whisper transcription.

## Invariants
- Topics: `party/<house>/<node>/<domain>/<signal>`
- Message: **small JSON**, stable keys, unix `ts_ms`.
- Privacy: remote nodes stream **features**, **not** continuous raw audio; event clips are short & throttled.

## Data Flow (MVP)

### Sensor Data Flow
```
ESP32 Nodes → MQTT (Pi) → Aggregator (Pi) → MQTT/WS → UI (Pi) → Touchscreen
```

### Transcription Flow
```
Pi INMP441 Mic → Audio Bridge (Pi) → HTTP → Whisper (unRAID) → Audio Bridge → MQTT (Pi) → UI
```

### User Interaction
```
Touchscreen → UI (Pi) → MQTT → ESP32 LED Rings
```

## Failure Modes
- Broker down: UI shows stale state; aggregator retries.
- Network flake: ESP nodes buffer minimal, but must tolerate loss.
- High noise: Aggregator caps UI update rate; LED daemon uses hysteresis.

## ESP32 Node Implementation
- **PlatformIO-based:** Custom Arduino framework firmware in `firmware/wm_node/`
- **Hardware:** ESP32 Dev Board + INMP441 (I²S mic) + PIR sensor + rotary encoder + WS2812 LED ring
- **Features:** Audio RMS/features, occupancy detection, encoder input, LED feedback, OTA updates
- **MQTT Topics:** `party/<house>/<node>/audio/features`, `occupancy/state`, `input/encoder`, `input/button`, `sys/heartbeat`
- **Configuration:** DRY config with `secrets.ini` (Wi-Fi), per-node environments for USB/OTA upload
- **Build:** `pio run -e node1-usb -t upload` (first time), `pio run -e node1-ota -t upload` (subsequent)

## Build/Run

### Development (unRAID)
```bash
# Test services locally before deploying to Pi
docker compose -f infra/docker-compose.yml up -d
```

### Production (Raspberry Pi)
```bash
# One-time bootstrap (on Pi)
curl -sSL https://raw.githubusercontent.com/USER/whispering-machine/main/scripts/pi_bootstrap.sh | bash
sudo reboot

# Deploy from unRAID
./scripts/pi_deploy.sh

# Or manually on Pi
cd /home/pi/whispering-machine
git pull
docker compose -f pi/compose.yml up -d --build
```

### ESP32 Firmware
```bash
# First time (USB)
cd firmware/wm_node
pio run -e node1-usb -t upload

# Subsequent updates (OTA)
pio run -e node1-ota -t upload
```

See `docs/PI_HUB_DEPLOYMENT.md` for complete deployment guide.
