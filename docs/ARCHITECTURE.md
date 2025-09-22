# Whispering Machine – Architecture

## Overview
- **Sensors (ESP32/ESPHome & custom audio):** publish MQTT topics under `party/<HOUSE_ID>/<node>/...`
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
ESP32/ESPHome → MQTT → Aggregator → MQTT/WS → UI → User

## Failure Modes
- Broker down: UI shows stale state; aggregator retries.
- Network flake: ESP nodes buffer minimal, but must tolerate loss.
- High noise: Aggregator caps UI update rate; LED daemon uses hysteresis.

## Build/Run
- Dev: `docker compose -f infra/docker-compose.yml up -d`
- Pi deploy: run UI & LED on Pi; point to unRAID broker (set `.env`).
