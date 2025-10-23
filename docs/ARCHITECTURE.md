# Whispering Machine – Architecture

## Overview

### Deployment Architecture (Party Night)
- **MacBook Hub:** Central controller running all services locally
  - **Mosquitto:** MQTT broker (port 1883 internal, 1884 host)
  - **Aggregator:** Subscribes to all nodes, computes metrics, publishes UI state
  - **UI:** FastAPI + WebSocket, serves party interface on 7" touchscreen
  - **Audio Bridge:** Captures from MacBook built-in mic, sends to Whisper, publishes transcripts
  - **LLM Agent:** Generates intelligent observations from sensor data
- **ESP32 Nodes (x3):** Remote sensors publishing to MacBook's MQTT broker
  - Audio features, PIR, encoder, button, LED ring (potentially unreliable)
  - Connect via WiFi to local router
- **unRAID Server:** External transcription service (via Tailscale)
  - **faster-whisper:** Port 10300, Wyoming protocol (managed outside this repo)
  - MacBook connects via Tailscale for audio transcription

### Network Topology
```
Internet → Local Router (WiFi)
  ├─ MacBook (hub, runs all services, Tailscale client, lid closed)
  │  ├─ Built-in Microphone
  │  └─ External Display (7" touchscreen)
  ├─ ESP32 node1 (WiFi, publishes to MacBook MQTT)
  ├─ ESP32 node2 (WiFi, publishes to MacBook MQTT)
  └─ ESP32 node3 (WiFi, publishes to MacBook MQTT)

MacBook Tailscale ←→ unRAID (faster-whisper transcription)
```

**Key Design**: MacBook is self-contained and portable. Runs with lid closed, drives external touchscreen. Only needs internet for Whisper transcription.

## Invariants
- Topics: `party/<house>/<node>/<domain>/<signal>`
- Message: **small JSON**, stable keys, unix `ts_ms`.
- Privacy: remote nodes stream **features**, **not** continuous raw audio; event clips are short & throttled.

## Data Flow (Party Night)

### Sensor Data Flow
```
ESP32 Nodes (x3) → MQTT (MacBook) → Aggregator (MacBook) → MQTT/WS → UI (MacBook) → Touchscreen
```

### Transcription Flow
```
MacBook Built-in Mic → Audio Bridge (MacBook) → HTTP → Whisper (unRAID) → Audio Bridge → MQTT (MacBook) → UI
```

### Intelligence Flow
```
Sensor Data + Randomness → LLM Agent (MacBook) → Observations → MQTT (MacBook) → UI
```

### User Interaction
```
Touchscreen → UI (MacBook) → MQTT → ESP32 LED Rings
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
# Test services locally before deploying to MacBook
docker compose -f infra/docker-compose.yml up -d
```

### Production (MacBook)
```bash
# Party mode setup
cd /path/to/whispering-machine
docker compose -f macbook/compose.yml up -d

# Party mode deployment
./scripts/party_deploy.sh

# Access party interface
# http://localhost:8000/party
```

### ESP32 Firmware
```bash
# First time (USB)
cd firmware/wm_node
pio run -e node1-usb -t upload

# Subsequent updates (OTA)
pio run -e node1-ota -t upload
```

See `docs/CURRENT_PRIORITIES.md` for party night execution plan.
