# Roadmap (High-level)

**Last Updated**: October 11, 2025

---

## Phase 1: Debug & Calibration Infrastructure ✅ COMPLETE

**Goal**: Build robust debugging tools and validate all sensor signals.

**Completed**:
- ✅ Stable MQTT broker + aggregator + UI loop
- ✅ Modular debug UI with component architecture
- ✅ ESP32 audio features (RMS, ZCR, 3-band frequency analysis)
- ✅ PIR activity & transitions (proximity detection ready)
- ✅ Encoder/button signals with NTP time sync
- ✅ LED ring behavior system (5 modes + encoder control)
- ✅ LED ring state publishing with RGB visualization
- ✅ Comprehensive status tables for all sensors
- ✅ Modular signal plotting (any signal, any node)
- ✅ MQTT message debugger with filtering

**Result**: Complete debug/calibration infrastructure, all sensors validated, ready for production features.

---

## Phase 2: Party Tracker UI & Polish (NEXT)

**Goal**: Build public-facing UI and refine behaviors.

**Tasks**:
- Build party tracker UI (reuse debug components)
- Simplified public interface (mood, occupancy, interaction)
- Tune LED modes for real-world use
- Add ensemble-based "active mode" (audio + PIR smoothing)
- Implement mood detection (spike analysis)
- Multi-room visualization
- Fine-tune sensor thresholds and behaviors

**Key Features**:
- Real-time party mood visualization
- Occupancy heat map
- Audio energy timeline
- LED ring status display
- Minimal, elegant design

---

## Phase 3: Persistence & Advanced Features

**Goal**: Data persistence and advanced analysis.

**Tasks**:
- Persistence layer (SQLite/Parquet)
- Daily data export
- Historical trend visualization
- Audio clip recording + transcription (Whisper)
- Event detection and logging
- Multi-room aggregation
- Trend analysis with sparklines

**Key Features**:
- Historical party metrics
- Transcribed conversation snippets
- Long-term activity patterns
- Event timeline

---

## Phase 4: Multi-Room & Scaling

**Goal**: Deploy across multiple rooms/nodes.

**Tasks**:
- Generic node auto-discovery (T-018)
- Raspberry Pi hub node integration
- Per-room mood aggregation
- Cross-room coordination
- Installation hardening (kiosk mode, resilience)
- Kill switch for privacy

**Key Features**:
- Whole-house visualization
- Room-to-room activity flow
- Coordinated LED behaviors
- Centralized control

---

## Non-Goals (Explicitly Out of Scope)

- ❌ Continuous raw audio streaming (privacy violation)
- ❌ Heavy GPU-based DSP (unnecessary complexity)
- ❌ Video surveillance
- ❌ Individual speaker identification
- ❌ Cloud dependencies (stay local-first)

---

## Current Status: **Ready for Phase 2** 🚀

All Phase 1 infrastructure complete. Can proceed with party tracker UI or continue tuning existing features.

