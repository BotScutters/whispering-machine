# Whispering Machine – Architecture

## Overview
- **Sensors (ESP32 PlatformIO nodes):** publish MQTT topics under `party/<HOUSE_ID>/<node>/...`
- **Broker:** Mosquitto (container) on unRAID. Internal port 1883; host mapped 1884.
- **Aggregator (Python):** subscribes topics → validates → derives metrics → publishes unified UI state.
- **UI (FastAPI + WS):** serves debug dashboard with modular components; WebSocket fanout to browser.
- **Whisper (External):** faster-whisper service on UnRAID (port 10300) for audio transcription (managed outside this repo).
- **(Future) Transcriber Service:** thin wrapper that receives audio clips from ESP32, calls Whisper API, publishes transcripts to MQTT.

## Invariants
- Topics: `party/<house>/<node>/<domain>/<signal>`
- Message: **small JSON**, stable keys, unix `ts_ms`.
- Privacy: remote nodes stream **features**, **not** continuous raw audio; event clips are short & throttled.

## Data Flow (MVP)
ESP32 PlatformIO → MQTT → Aggregator → MQTT/WS → UI → User

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
- **Services:** `docker compose -f infra/docker-compose.yml up -d`
- **Firmware:** `pio run -e node1-usb -t upload` (see `firmware/wm_node/README.md`)
- **Pi deploy:** run UI & LED on Pi; point to unRAID broker (set `.env`).
