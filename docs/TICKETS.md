# Tickets (Well-scoped, agent-ready)

> Contribute via small PRs. Every ticket lists **Acceptance** and **How to test**.

---

## T-001 UI: Replace loudness bar with smoothing + sparkline
**Goal:** Visually stable loudness with a 30s sparkline.
**Tasks:**
- Add client-side EWMA smoothing of `noise.rms`.
- Keep last 30s values; render a simple sparkline (SVG).
**Acceptance:**
- Line never “tears”; updates at ~5 Hz smoothly.
**Test:**
- Publish stepped RMS values; visually confirm smoothing.

## T-002 Aggregator: Spike detection + mood topic
**Goal:** Emit `party/<house>/mood` based on recent RMS.
**Tasks:**
- Maintain 10 s sliding window; detect spikes over mean+Nσ.
- Publish `idle|busy|spike|alert`.
**Acceptance:**
- Publishing increasing RMS flips mood to spike; decays back in ~5–10 s.
**Test:**
- Simulate RMS; check `mosquitto_sub -t 'party/+/mood'`.

## T-003 LED Daemon (Pi): Map mood→effects
**Goal:** Implement 5 effects; param by payload.
**Tasks:**
- rpi_ws281x init; non-blocking loop (asyncio or time-sliced).
- Map moods: idle pulse, busy swirl, spike flicker, alert red, poll rainbow.
**Acceptance:**
- Mood changes <100 ms; no flicker at 30% brightness.
**Test:**
- Publish moods manually; verify visually.

## T-004 ESP32: PIR sensor debouncing + retention
**Goal:** Improve PIR reliability and state persistence.
**Tasks:**
- Add hardware debouncing (0.1 µF caps) or software debouncing
- Implement retained MQTT messages for state persistence
- Add `on_boot` health publish
**Acceptance:**
- No chattering; retains last state after broker restart.
**Test:**
- Restart broker; `mosquitto_sub` shows retained state.

## T-005 ESP32: Enhanced PIR sensor features
**Goal:** Improve PIR sensor reliability and add advanced occupancy detection.
**Tasks:**
- Add hardware debouncing improvements
- Implement occupancy confidence scoring
- Add motion history tracking for better detection
**Acceptance:** 
- More reliable occupancy detection with fewer false positives.
**Test:** 
- Test with various motion patterns; verify improved accuracy.

## T-006 Aggregator: Persistence layer
**Goal:** Save highlights to SQLite/Parquet.
**Tasks:**
- Append-only write when spikes or button tallies change.
**Acceptance:**
- File grows with events; on restart, no crash if file exists.
**Test:**
- Force spikes; inspect file (row count increases).

## T-007 UI: Kiosk polish + privacy banner
**Goal:** Footer banner + fabrication badge.
**Tasks:**
- Always-on footer; shows “Fabrication ~X%”.
- Add “Pause Listening” button (publishes `party/<house>/control/pause`).
**Acceptance:**
- Banner is visible; pause toggles a visual state.
**Test:**
- Click pause; UI badge flips, aggregator logs it.

## T-008 Aggregator: Control channel wiring
**Goal:** Honor pause.
**Tasks:**
- Subscribe `control/pause`; when true, suppress event clips and mark state.
**Acceptance:**
- UI reflects paused; no clip triggers while paused.
**Test:**
- Publish pause true; ensure behavior.

## T-009 ESP32: Audio feature extraction - ZCR and frequency bands ✅ DONE
**Goal:** Implement ZCR and 3-band frequency analysis (currently pegged at 0).
**Tasks:**
- ✅ Implement zero-crossing rate calculation in I²S audio processing
- ✅ Add 3-band IIR filters (low/mid/high) for frequency analysis using biquad filters
- ✅ Optimize computation to maintain ~10 Hz publish rate
- ✅ Added AudioFeatures struct for clean API
**Acceptance:**
- ✅ ZCR, low, mid, high values change with different audio inputs
- ✅ Performance maintained at ~10 Hz
**Test:**
- Play pink noise / sine wave; verify all features respond appropriately
- Check audio status table in debug UI for non-zero values

## T-010 DevEx: Development scripts
**Goal:** Standardize dev commands for UnRAID environment.
**Tasks:**
- `./dev.sh up`, `down`, `logs`, `pub-noise`, `lint`, `fmt`.
**Acceptance:**
- Commands run on UnRAID with Docker installed.
**Test:**
- Call each command; green.

## T-011 ESP32: Multi-node deployment automation
**Goal:** Streamline deployment to multiple ESP32 nodes.
**Tasks:**
- Create `scripts/build_all.sh` for OTA updates to all nodes
- Add `scripts/flash_usb.sh` for initial USB flashing
- Implement `scripts/bump_version.sh` for version tracking
**Acceptance:**
- Single command updates all nodes via OTA.
**Test:**
- Run build script; verify all nodes receive updates.

## T-012 ESP32: LED ring behavior system
**Goal:** Implement comprehensive LED ring behavior system with multiple modes.
**Tasks:**
- Publish LED ring state at 1-5 Hz to `party/<house>/<node>/ring/state`
- Create behavior modes: idle breathing, audio-reactive, occupancy-responsive, swirling rainbow, aurora glow, siren
- Add encoder button to cycle through visualization modes
- Add encoder rotation to modify current mode parameters (speed, intensity, color, etc.)
- Implement ensemble-based "active mode" driven by audio + PIR with time smoothing
- Add per-pixel RGB state publishing for debug UI validation
**Acceptance:**
- LED ring publishes state; debug UI shows live ring simulation
- Button cycles modes; encoder modifies parameters
- Ring responds to audio intensity and occupancy changes
**Test:**
- Rotate encoder, press button; verify mode changes in debug UI
- Generate audio/motion; verify ring responds appropriately

## T-013 ESP32: PIR raw value publishing ✅ DONE
**Goal:** Publish raw PIR sensor values for calibration and proximity detection.
**Implementation:** Since AM312 is digital-only, added derived metrics:
- **activity**: Float 0.0-1.0 representing motion percentage over last 10 seconds
- **transitions**: Integer count of state changes in last second
- Publish rate increased to 10 Hz for smoother tracking
**Tasks:**
- ✅ Enhanced PIR firmware with activity tracking (100-sample rolling history)
- ✅ Added transitions counter for motion pattern detection
- ✅ Updated occupancy schema with activity and transitions fields
- ✅ Updated aggregator to handle new fields
- ✅ Updated debug UI with occupancy status table showing all metrics
- ✅ Added tooltips explaining each metric
- ✅ Updated SENSOR_REFERENCE.md with detailed signal documentation
**Acceptance:**
- ✅ Debug UI shows activity and transitions alongside occupied state
- ✅ User can plot occupancy.activity and occupancy.transitions on charts
- ✅ Values help inform motion pattern understanding
**Test:**
- ✅ Approach sensor; observe activity rise from 0.0 to 1.0
- ✅ Wave hand rapidly; observe transitions spike

## T-014 ESP32: Encoder/button signal debugging ✅ DONE
**Goal:** Fix encoder signal inconsistencies and improve button tracking.
**Tasks:**
- ✅ Debug encoder position/delta calculation issues
- ✅ Add button press/release events to `input/button` topic
- ✅ Verify encoder signals from all nodes reach aggregator correctly
- ✅ Add per-node encoder state to debug UI
- ✅ Add NTP time synchronization for accurate timestamps
**Acceptance:**
- ✅ Encoder delta shows incremental changes, not resets
- ✅ Button presses visible in debug UI
- ✅ Both node1 and node2 encoder signals distinguish properly
- ✅ Timestamps are synchronized across nodes
**Test:**
- ✅ Rotate encoder clockwise/counterclockwise; verify delta direction
- ✅ Press button; see event in MQTT log
- Deploy firmware and verify NTP sync in serial output

## T-015 Debug UI: Modular signal plotting ✅ DONE
**Goal:** Allow adding/removing any numeric signal from any node to charts.
**Tasks:**
- ✅ Create dynamic "Add Signal" interface for selecting node + signal path
- ✅ Support plotting arbitrary JSON paths (e.g., `node1.audio.rms`, `node2.occupancy.raw_value`)
- ✅ Allow multiple signals on same chart with auto-scaling
- ✅ Add per-signal visibility toggle and color picker
- ✅ Save chart configuration to localStorage
- ✅ Added status tables for audio and encoder signals
**Acceptance:**
- ✅ Can plot any combination of signals from any nodes
- ✅ Configuration persists across page refreshes
- ✅ Status tables auto-populate and update
**Test:**
- ✅ Add signals from multiple nodes; verify plotting
- ✅ Refresh page; verify configuration restored

## T-016 Debug UI: Enhanced MQTT debugger
**Goal:** Improve MQTT message inspection and filtering.
**Tasks:**
- Add topic tree view showing hierarchy
- Add message rate/frequency indicators per topic
- Implement JSON path search within payloads
- Add message replay/republish functionality
**Acceptance:**
- Can easily browse and filter MQTT topics
- Can see message rates and inspect payload details
**Test:**
- Filter by topic pattern; verify messages shown
- Check message rate indicators

## T-017 ESP32: LED ring state publishing
**Goal:** Publish LED ring state for debug UI validation.
**Tasks:**
- Add `ring/state` topic publishing at 1-5 Hz
- Include per-pixel RGB values: `{"pixels": [[r,g,b], ...], "brightness": float, "mode": string, "ts_ms": int}`
- Optimize payload size (consider compression or delta encoding)
**Acceptance:**
- Debug UI receives and renders LED ring state accurately
**Test:**
- Change LED patterns; verify debug UI simulation matches physical ring

## T-018 Aggregator: Generic node/signal routing
**Goal:** Remove hard-coded node names; support dynamic node discovery.
**Tasks:**
- Implement dynamic topic subscription: `party/<house>/+/+/+`
- Auto-discover nodes from incoming messages
- Support arbitrary signal types (not just audio/occupancy)
- Update UI state schema to be node-agnostic
**Acceptance:**
- Adding new nodes requires no aggregator code changes
- All node signals automatically routed to UI
**Test:**
- Add new node; verify auto-discovery and routing

## T-019 ESP32: Event-triggered audio clip recording
**Goal:** Record and upload short audio clips for transcription.
**Tasks:**
- Implement circular buffer for continuous audio capture (5-10 seconds)
- Add event triggers: RMS spike, button press, high ZCR (speech-like)
- Save triggered clips to SPIFFS or upload directly via HTTP POST
- Add clip metadata: trigger type, timestamp, node ID, pre/post-trigger duration
- Implement throttling to avoid overwhelming server (max 1 clip per 30s)
- Add configuration via MQTT: enable/disable recording, trigger thresholds
**Acceptance:**
- Button press captures 2s pre-trigger + 3s post-trigger audio
- RMS spike captures audio clip with metadata
- Clips uploaded to configured HTTP endpoint
- Throttling prevents excessive uploads
**Test:**
- Press button; verify clip captured and uploaded
- Generate loud sound; verify automatic clip capture
- Check throttling with rapid events

## T-020 Server: Audio transcription service
**Goal:** Receive audio clips and transcribe using Whisper.
**Tasks:**
- Create FastAPI service accepting WAV file uploads
- Implement Whisper transcription (whisper.cpp or faster-whisper)
- Publish transcribed text to MQTT: `party/<house>/<node>/audio/transcript`
- Add transcript metadata: confidence, language, duration
- Implement queue system for handling multiple simultaneous uploads
- Add error handling and fallback for transcription failures
- Optional: Speaker diarization for multi-person conversations
**Acceptance:**
- Service receives WAV files via HTTP POST
- Transcribes audio and publishes text to MQTT within 2-5 seconds
- Handles queue of multiple clips without blocking
- Error cases logged and reported
**Test:**
- Upload test audio clip; verify transcription published
- Upload multiple clips rapidly; verify queue handling
- Test with speech, music, noise; verify appropriate handling

## T-019 Debug UI: Refactor to Modular Architecture
**Goal:** Refactor debug UI from monolithic 1500+ line file to clean, modular, reusable components.
**Priority:** MEDIUM (not blocking features, but improves maintainability)
**Tasks:**
- **Phase 1**: Extract core utilities (config, state-manager, mqtt-client, utils)
- **Phase 2**: Extract UI components (base-component, status-table, led-ring-viz, signal-chart, etc.)
- **Phase 3**: Create page orchestrator (debug-app.js)
- **Phase 4**: Refactor CSS into modular files
- **Phase 5**: Add future-proofing (node type detection, dynamic signal discovery)
**Key Principles:**
- Component-based architecture with base class
- Centralized state management with observer pattern
- Configuration-driven rendering (reduce code duplication)
- Reusable components for party tracker UI
- Consistent patterns across all status tables (unify Encoder/Button with others)
**Acceptance:**
- Debug UI looks and behaves identically to current version
- No single file > 300 lines
- Can add new signal panel with < 50 lines of code
- Can add new node type with config change only
- All components extend BaseComponent or use clear interface
**Details:** See `docs/T-019_UI_REFACTOR.md` for complete architecture spec

---
(Keep adding more tickets as scope increases.)
