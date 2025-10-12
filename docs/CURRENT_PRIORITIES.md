# Current Priorities (Phase 1: Debug & Calibration)

## Status: Debug Infrastructure Complete, LED System Ready

**Last Updated**: October 11, 2025

We've completed the core debug infrastructure and have a fully functional LED ring behavior system. Focus is now on tuning, validation, and preparing for the party tracker UI.

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

## Next Priorities

### Immediate (Optional Tuning)
1. **Audio Reactive Mode Tuning**
   - Adjust RMS scaling if too sensitive/insensitive
   - Test with various audio levels (silence, conversation, music)
   
2. **PIR Activity Calibration**
   - Validate activity metric accuracy
   - Test proximity responsiveness
   - Tune for LED intensity modulation

3. **LED Mode Refinement**
   - Test all modes in real-world conditions
   - Adjust speeds, colors, intensities as needed
   - Document preferred modes for different scenarios

### Short-Term Features
4. **T-018: Generic Node Auto-Discovery**
   - Remove hard-coded node names
   - Dynamic signal discovery
   - Prepare for 3rd node and Raspberry Pi hub

5. **Party Tracker UI (New Ticket)**
   - Reuse modular components from debug UI
   - Build simplified public-facing interface
   - Focus on occupancy, mood, interaction tracking

### Medium-Term Features
6. **T-020: Audio Clip Recording & Transcription**
   - Event-triggered audio snippets on ESP32
   - Whisper transcription service
   - MQTT publish of transcribed text

7. **T-002: Mood Detection**
   - Audio spike analysis
   - Activity-based mood inference
   - LED behavior driven by mood state

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

