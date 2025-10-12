# Agent Memory Log (Append-only)

**Purpose:** Capture "gotchas" and project-specific learnings so future agents stop repeating mistakes.

## Entry Format
```markdown
### YYYY-MM-DD: [CONTEXT TITLE]
- **What Happened**: Brief description of the issue or discovery
- **Root Cause**: Why it happened or what was misunderstood
- **Rule/Lesson**: Clear, actionable guideline for future development
- **Impact**: How this affects the system (performance, reliability, etc.)
- **Links**: PR/commit/log references
- **Tags**: `#mqtt` `#docker` `#python` `#ui` etc. for categorization
```

## Active Memory Entries

### 2025-01-27: Paho MQTT v2 Callback Signature
- **What Happened**: UI/aggregator services crashed with "TypeError: on_connect() takes 4 positional arguments but 5 were given"
- **Root Cause**: Paho MQTT v2 changed callback signatures to include additional parameters
- **Rule/Lesson**: **Always use Paho v2 signature** `(client, userdata, flags, reason_code, properties=None)` in all MQTT services
- **Impact**: Service crashes on broker reconnection, breaks resilience
- **Links**: commit a6e308b
- **Tags**: `#mqtt` `#python` `#resilience`

### 2025-01-27: Docker Compose Port Configuration
- **What Happened**: Services failed to connect to MQTT broker using host port 1884
- **Root Cause**: Inside Docker Compose network, services should use service DNS names, not host ports
- **Rule/Lesson**: **Inside compose, always use service DNS + port 1883**. Host port 1884 is only for LAN/host tools like mosquitto_pub
- **Impact**: Service startup failures, development workflow confusion
- **Links**: Issue #123
- **Tags**: `#docker` `#mqtt` `#networking`

### 2025-01-27: ESP32 PlatformIO Implementation
- **What Happened**: ESP32 nodes implemented using PlatformIO instead of ESPHome for custom audio processing
- **Root Cause**: Need for custom I²S audio processing, encoder handling, and LED ring control
- **Rule/Lesson**: **ESP32 nodes use PlatformIO with Arduino framework** in `firmware/wm_node/`. Use `secrets.ini` for Wi-Fi config, DRY config with `common.ini` and per-node environments
- **Impact**: More control over hardware interfaces, custom audio feature extraction, OTA updates
- **Links**: `firmware/wm_node/README.md`
- **Tags**: `#esp32` `#platformio` `#firmware` `#audio`

### 2025-01-27: ESP32 MQTT Topic Structure
- **What Happened**: ESP32 nodes publish to specific topic patterns matching the aggregator expectations
- **Root Cause**: Need for consistent topic structure across all nodes for aggregator processing
- **Rule/Lesson**: **ESP32 topics follow `party/<house>/<node>/<domain>/<signal>` pattern**. Key topics: `audio/features`, `occupancy/state`, `input/encoder`, `input/button`, `sys/heartbeat`
- **Impact**: Enables proper aggregator processing and UI updates
- **Links**: `firmware/wm_node/src/topics.h`
- **Tags**: `#esp32` `#mqtt` `#topics` `#aggregator`

## Memory Categories

### MQTT Patterns
- Topic structure: `party/<house>/<node>/<domain>/<signal>`
- Message format: JSON with `ts_ms` timestamp
- Validation: Use Pydantic models for all payloads

### Docker & Infrastructure
- Service communication: Use DNS names within compose
- Port mapping: Host ports only for external tools
- Development: `docker compose -f infra/docker-compose.yml up -d`

### External Services
- **Whisper**: faster-whisper on UnRAID (port 10300), managed outside this repo
- **Integration**: This repo will build thin transcriber service to interface with Whisper API
- **Documentation**: See `docs/WHISPER_INTEGRATION.md` for setup and API details

### Python & AsyncIO
- Paho MQTT v2 callback signatures
- AsyncIO patterns for MQTT clients
- Structured logging with context

### UI & WebSocket
- Real-time updates via WebSocket
- State management through aggregator
- Visual feedback requirements

### ESP32 & Firmware
- PlatformIO with Arduino framework for custom hardware control
- I²S audio processing for feature extraction
- MQTT publishing with proper topic structure
- OTA updates via ArduinoOTA
- Hardware: INMP441 mic, PIR sensor, rotary encoder, WS2812 LED ring

## How to Add New Entries
1. Use the exact format above
2. Include all fields, even if some are brief
3. Add relevant tags for categorization
4. Keep entries focused and actionable
5. Update the cursor rules file if the lesson is critical
