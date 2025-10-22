# Current Priorities (MVP: Pi Hub Deployment)

## Status: 🚨 CRITICAL - Pi Hub Integration Required for MVP

**Last Updated**: October 14, 2025

**MAJOR ARCHITECTURE SHIFT**: Moving from unRAID-hosted services to Raspberry Pi 5 hub as the central controller. All services (MQTT, Aggregator, UI) will run on Pi, with ESP32 nodes connecting to Pi's broker. Pi will use Tailscale to reach unRAID's faster-whisper service for transcription.

**Timeline**: Few working days remaining - focus on critical path only.

---

## Recently Completed ✅

### T-009: Audio Feature Extraction ✅
- Implemented ZCR (zero-crossing rate)
- Implemented 3-band IIR filters (low 0-300Hz, mid 300-3000Hz, high 3000Hz+)
- Biquad filter implementation with optimized performance
- All audio features now reporting non-zero values

### T-013: PIR Activity & Transitions ✅
- Added activity metric (0.0-1.0) representing motion over 10 seconds
- Added transitions counter for motion pattern detection
- Increased publish rate to 10 Hz for smoother tracking
- Enables proximity-responsive behaviors

### T-014: Encoder/Button Debugging ✅
- Fixed encoder delta calculation (incremental changes)
- Added button press/release event types
- Implemented NTP time synchronization across all nodes
- All timestamps now synchronized

### T-015: Debug UI Modular Signal Plotting ✅
- Can plot any numeric signal from any node
- Signal visibility toggles, color customization
- Time range controls (5s to 1h)
- Log scale toggle
- LocalStorage persistence

### T-012a: LED Ring Behavior System ✅
- 5 visualization modes (Idle Breathing, Audio Reactive, Rainbow, Aurora, Occupancy Pulse)
- Encoder button cycles modes
- Encoder rotation adjusts animation speed
- Ring state published at 5 Hz with full RGB per-pixel data
- Debug UI shows live LED ring visualization

### T-019: Debug UI Refactor ✅
- Transformed from 1573-line monolith to 12 modular files
- Component-based architecture with BaseComponent
- Centralized state management with observer pattern
- StatusTable component reused 4 times
- Ready for party tracker UI code reuse

---

## Current System State

### Fully Working ✅
- ✅ ESP32 nodes with all sensors (audio, PIR, encoder, button, LED ring)
- ✅ Audio features: RMS, ZCR, 3-band frequency analysis
- ✅ PIR: occupied, activity, transitions
- ✅ Encoder: position, delta with speed adjustment
- ✅ Button: press/release events with mode cycling
- ✅ LED Ring: 5 modes, encoder control, full RGB visualization
- ✅ Debug UI: Modular signal plotting, status tables, LED simulator
- ✅ MQTT message debugger with filtering
- ✅ NTP time synchronization
- ✅ Connection status indicators

### Ready for Next Phase
- Sensor calibration and tuning (all signals visible)
- LED behavior refinement (modes working, needs tuning)
- Party tracker UI development (components ready to reuse)

---

## 🚨 CRITICAL PATH (MVP Deadline)

**Goal**: Get Pi hub running with all services, ESP32 nodes connected, and transcription working.

**Estimated Total Time**: 15-20 hours

### Phase 1: Pi Infrastructure (CRITICAL)
**T-021: Pi Bootstrap Script** (2-3 hours)
- One-time Pi setup: Docker, I²S, Tailscale
- **Blocker**: Must complete before any other Pi work
- **Owner**: Start immediately

**T-022: Pi Docker Compose Stack** (2-3 hours)
- Migrate MQTT, Aggregator, UI to Pi
- **Depends on**: T-021
- **Owner**: Start after bootstrap tested

**T-025: ESP32 Firmware Config** (30 minutes)
- Point ESP32 nodes to Pi MQTT broker
- **Depends on**: T-022
- **Owner**: Quick win after Pi stack running

### Phase 2: Audio Transcription (CRITICAL)
**T-023: Audio Bridge Service** (4-6 hours)
- Pi INMP441 → unRAID Whisper → MQTT
- **Depends on**: T-022 (needs MQTT broker)
- **Owner**: Can start in parallel with T-025

### Phase 3: Deployment & UI (HIGH)
**T-024: Pi Deployment Script** (1-2 hours)
- Automate unRAID → Pi deployment
- **Depends on**: T-022
- **Owner**: Start after stack working

**T-027: Party Tracker UI** (4-6 hours)
- Touchscreen-optimized UI with transcripts
- **Depends on**: T-023 (needs transcript data)
- **Owner**: Start after transcription working

**T-026: Transcript Panel Component** (2-3 hours)
- Reusable transcript display component
- **Depends on**: T-023
- **Owner**: Part of T-027, can be concurrent

---

## Execution Plan (Recommended Order)

### Day 1: Pi Foundation
1. ✅ **T-021** - Bootstrap Pi (morning)
2. ✅ **T-022** - Pi compose stack (afternoon)
3. ✅ **T-025** - ESP32 config (evening)
4. **Checkpoint**: ESP32 nodes publishing to Pi, UI showing data

### Day 2: Audio Pipeline
5. ✅ **T-023** - Audio bridge (full day)
6. **Checkpoint**: Transcripts appearing in MQTT

### Day 3: Polish & Deploy
7. ✅ **T-024** - Deployment script (morning)
8. ✅ **T-027** - Party tracker UI (afternoon/evening)
9. **Checkpoint**: Full system running on Pi, ready for demo

---

## Deferred (Post-MVP)

These are valuable but not critical for MVP:

- **T-018**: Generic node auto-discovery (nice-to-have)
- **T-001**: Loudness sparkline (polish)
- **T-002**: Mood detection (future enhancement)
- **Audio tuning**: RMS scaling, PIR calibration (can tune live)
- **LED refinement**: Mode adjustments (working well enough)

---

## Architecture Status

### Infrastructure ✅
- Docker Compose setup with MQTT broker, aggregator, UI
- ESP32 PlatformIO firmware with OTA updates
- FastAPI backend with WebSocket support
- Modular JavaScript frontend architecture

### Documentation ✅
- ARCHITECTURE.md - System overview
- SENSOR_REFERENCE.md - Detailed sensor signal documentation
- TICKETS.md - Well-scoped work items
- ROADMAP.md - High-level milestones
- AGENT_MEMORY.md - Project-specific gotchas
- T-019_UI_REFACTOR.md - UI architecture spec
- Cursor rules - Development guidelines

### Testing ✅
- Manual testing via debug UI
- MQTT message validation
- Per-node sensor readouts
- Live signal plotting and validation

---

## Notes
- Debug infrastructure is now production-ready
- All planned Phase 1 features complete
- Ready to move to Phase 2 (party tracker) or continue with sensor tuning
- Modular architecture makes adding features fast and safe

