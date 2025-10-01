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

## T-009 ESP32: Audio feature extraction optimization
**Goal:** Improve audio processing performance and accuracy.
**Tasks:**
- Optimize I²S 16 kHz mono processing; window 1 s
- Fine-tune RMS, ZCR, 3 IIR bands computation
- Add frequency domain analysis if needed
**Acceptance:**
- Features change with tone/noise input; stable performance.
**Test:**
- Play pink noise / sine; verify band behavior.

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

## T-012 ESP32: LED ring mood integration
**Goal:** Connect LED ring to aggregator mood topics.
**Tasks:**
- Subscribe to `party/<house>/mood` topics
- Map mood states to LED patterns (idle pulse, busy swirl, spike flicker, alert red)
- Implement smooth transitions between patterns
**Acceptance:**
- LED ring reflects real-time mood changes.
**Test:**
- Publish mood changes; verify LED patterns.

---
(Keep adding more tickets as scope increases.)
