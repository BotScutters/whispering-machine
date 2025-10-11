# Roadmap (High-level)

**Phase 1 (Current - Debug & Calibration):**
- ✅ Stable broker + aggregator + UI loop
- ✅ Debug UI with modular signal plotting
- ✅ ESP32 audio feature extraction (RMS, ZCR, 3-band frequency)
- ✅ Encoder/button signal debugging with NTP time sync
- ✅ Status tables for all sensor signals
- 🔄 PIR raw value publishing for proximity tuning
- 🔄 LED ring state publishing for validation

**Phase 2 (LED & Interaction):**
- LED ring behavior system with multiple modes
- LED ring state publishing for validation
- Encoder button mode cycling
- Audio-reactive + occupancy-responsive patterns
- Enhanced PIR with proximity detection
- Fabrication toggles and badges

**Phase 3 (Persistence & Polish):**
- Persistence layer (SQLite/Parquet) + daily export
- Aggregator mood detection and publishing
- Event-clip upload + Whisper keywords
- Multi-room view, trend minisparklines
- Installation polish (kiosk, resilience, kill switch)

**Non-goals (for now):**
- Continuous raw audio streaming
- Fancy GPU-based on-device DSP
