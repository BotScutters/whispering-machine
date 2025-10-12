# Current Priorities (Phase 1: Debug & Calibration)

## Status: Building Debug/Calibration Infrastructure

We're currently in the debug and calibration phase, focusing on validating sensor data and building tools for tuning the system.

## Recently Completed ✅

### 1. Debug UI Improvements
- **T-015**: ✅ Modular signal plotting
- **Result**: Can plot any numeric signal from any node, with visibility toggles and color customization
- **Impact**: Full flexibility for sensor calibration and validation

### 2. ESP32 Audio Features
- **T-009**: ✅ Implemented ZCR and 3-band frequency analysis
- **Result**: ZCR, low, mid, high bands now computed using IIR filters
- **Impact**: Ready for mood detection and audio-reactive behaviors

### 3. Encoder/Button Signals
- **T-014**: ✅ Fixed encoder delta calculation and button events
- **Result**: Delta shows incremental changes, button press/release events, NTP time sync
- **Impact**: User interaction ready, synchronized timestamps across nodes

## Current Issues to Address

### 1. PIR Sensor Enhancement (High Priority)
- **T-013**: Publish raw PIR values for proximity detection
- **Current Issue**: Only boolean occupancy; can't tune proximity thresholds
- **Impact**: Need for proximity-responsive LED behaviors

### 5. LED Ring State Publishing (Medium Priority)
- **T-017**: Publish LED ring state for validation
- **Current Issue**: No visibility into actual LED ring state
- **Impact**: Can't validate LED behaviors in debug UI

### 6. Generic Node/Signal Routing (Medium Priority)
- **T-018**: Remove hard-coded node assumptions in aggregator
- **Current Issue**: Adding nodes requires code changes
- **Impact**: Scalability for multi-room deployment

## Recommended Next Steps

1. **T-013 (PIR raw values)** - High Priority
   - Add proximity sensing capabilities
   - Enable better occupancy detection tuning
   - Foundation for proximity-responsive LED behaviors

2. **T-017 (LED ring state publishing)** - High Priority
   - Visibility into actual LED ring state
   - Validate behaviors in debug UI
   - Required before building complex LED modes

3. **T-012 (LED ring behavior system)** - Medium Priority
   - Implement comprehensive LED modes
   - Connect to sensor ensemble (audio + PIR + encoder)
   - Create interactive experiences

4. **T-018 (Generic node/signal routing)** - Medium Priority
   - Remove hard-coded node assumptions
   - Enable easier multi-node scaling
   - Prepare for Raspberry Pi integration

5. **T-002 (Mood detection)** - Medium Priority
   - Now that audio features work, implement spike detection
   - Enable mood-based LED behaviors
   - Foundation for event logging

6. **T-019 & T-020 (Audio transcription system)** - Future Priority
   - Event-triggered audio clip recording on ESP32
   - Server-side Whisper transcription
   - Dual-mode: real-time features + transcription capability

## Current System State

### Working ✅
- ✅ MQTT pub/sub infrastructure
- ✅ ESP32 nodes with full audio features (RMS, ZCR, 3-band)
- ✅ Debug UI with modular signal plotting
- ✅ Status tables for audio, encoder, button, occupancy
- ✅ MQTT message log with filtering
- ✅ Encoder position/delta tracking
- ✅ Button press/release events
- ✅ NTP time synchronization across nodes
- ✅ Per-node signal visualization

### Partially Working 🔄
- Occupancy (boolean only, no raw values for proximity)
- LED ring (local control only, no state publishing)

### Not Yet Implemented ❌
- PIR raw value sensing
- LED ring state publishing
- LED behavior modes and mode cycling
- Mood detection and spike analysis
- Generic node auto-discovery
- Persistence layer

## Notes
- Focus on debug/calibration tools before production features
- Maintain modularity for multi-node scalability
- Prioritize visibility into raw sensor data over polished UI
- Build interaction patterns incrementally with validation at each step

