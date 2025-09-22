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

## T-004 ESPHome: PIR node YAML hardening
**Goal:** De-bounce + battery-friendly PIR.
**Tasks:**
- `delayed_off`, `on_boot` health publish, retained birth message.
**Acceptance:**
- No chattering; retains last state after broker restart.
**Test:**
- Restart broker; `mosquitto_sub` shows retained state.

## T-005 ESPHome: BH1750 node + lux tiles
**Goal:** Add lux to UI; show day/night indicator.
**Tasks:**
- Publish `lux` 0.2–0.5 Hz; UI tile pill “bright/dim.”
**Acceptance:** 
- UI updates; pill matches thresholds.
**Test:** 
- Cover/uncover sensor; see tile change.

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

## T-009 ESP32 Audio (PlatformIO): Real RMS/ZCR/3-band
**Goal:** Replace placeholders.
**Tasks:**
- I2S 16 kHz mono; window 1 s; compute RMS, ZCR, 3 IIR bands.
**Acceptance:**
- Features change with tone/noise input.
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

---
(Keep adding more tickets as scope increases.)
