# Whispering Machine – Architecture

## Overview
- **Sensors (ESP32 PlatformIO nodes):** publish MQTT topics under `party/<HOUSE_ID>/<node>/...`
- **Broker:** Mosquitto (container) on unRAID for dev. Internal port 1883; host mapped 1884 (avoid conflicts).
- **Aggregator (Python):** subscribes topics → validates → derives metrics → publishes unified UI state to `party/<HOUSE_ID>/ui/state` at ~5 Hz.
- **UI (FastAPI + WS):** serves dashboard; opens WS; pushes state to touchscreen.
- **LED Daemon (Pi target):** subscribes mood topics → drives WS2812 via level-shifted GPIO.
- **(Optional) UnRAID workers:** receive uploaded event clips → transcribe (Whisper) → keywords → MQTT.

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
