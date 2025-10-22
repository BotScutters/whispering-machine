# Tickets (Well-scoped, agent-ready)

> Contribute via small PRs. Every ticket lists **Acceptance** and **How to test**.

---

## 🚨 CRITICAL PATH: Pi Hub Deployment (MVP Deadline)

These tickets must be completed to get the Pi hub running for the MVP demo.

### T-021: Pi Bootstrap Script & I²S Setup
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Create one-time Pi setup script for hardware and software initialization.

**Tasks**:
- Create `scripts/pi_bootstrap.sh` with:
  - System package updates
  - Docker + Docker Compose plugin installation
  - Tailscale installation (optional)
  - I²S overlay enablement for INMP441
  - User added to `docker` and `audio` groups
  - Repo clone to `/home/pi/whispering-machine`
- Create `pi/.env.example` with all required environment variables
- Create `pi/README.md` with wiring diagram and setup instructions

**Acceptance**:
- Script runs without errors on fresh Pi 5
- `arecord -l` shows I²S device after reboot
- Docker and Compose are functional
- User can run `docker compose` without `sudo`

**Test**:
```bash
ssh pi@192.168.8.x
curl -sSL https://raw.githubusercontent.com/USER/whispering-machine/main/scripts/pi_bootstrap.sh | bash
# Reboot
arecord -l  # Should show I²S device
docker --version
docker compose version
```

**Estimated Time**: 2-3 hours

---

### T-022: Pi Docker Compose Stack
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Create Pi-specific compose file that runs all services locally.

**Tasks**:
- Create `pi/compose.yml` with services:
  - `mosquitto` (MQTT broker)
  - `aggregator` (reuse existing, point to local broker)
  - `ui` (reuse existing, point to local broker)
- Ensure services use relative paths to existing service directories
- Add health checks for all services
- Configure proper restart policies
- Document environment variables in `pi/.env.example`

**Acceptance**:
- `docker compose -f pi/compose.yml up -d` starts all services
- MQTT broker reachable at `localhost:1883` and `0.0.0.0:1884`
- UI accessible at `http://localhost:8000`
- All services show healthy in `docker ps`

**Test**:
```bash
cd /home/pi/whispering-machine
docker compose -f pi/compose.yml up -d
docker ps  # All services running
mosquitto_pub -h localhost -t test -m "hello"
curl http://localhost:8000  # UI loads
```

**Estimated Time**: 2-3 hours

---

### T-023: Audio Bridge Service (Pi INMP441 → Whisper)
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Capture audio from Pi's INMP441, send to unRAID Whisper, publish transcripts to MQTT.

**Tasks**:
- Create `services/audio_bridge/` with:
  - `Dockerfile` (Python 3.10, PyAudio, httpx, paho-mqtt)
  - `app.py` (main service logic)
  - `requirements.txt`
  - `audio_capture.py` (ALSA/PyAudio wrapper)
  - `whisper_client.py` (Wyoming protocol client)
  - `mqtt_publisher.py` (transcript publishing)
- Implement audio capture loop (chunk to 2-5s WAV)
- Implement HTTP POST to Whisper service
- Implement MQTT publish to `party/<house>/pihub/speech/transcript`
- Add trigger modes: manual, VAD (voice activity detection), button
- Add error handling, retries, logging

**Acceptance**:
- Service starts and connects to MQTT
- Captures audio from INMP441 (verify with logs)
- Sends WAV chunks to Whisper service
- Publishes transcripts to MQTT within 5 seconds
- Gracefully handles Whisper service downtime

**Test**:
```bash
# On Pi
docker logs pi_audio_bridge --tail 50
# Should show: "Audio bridge started", "Captured chunk", "Transcript: ..."

# Subscribe to transcripts
mosquitto_sub -h localhost -t 'party/+/pihub/speech/transcript'
# Speak near mic, should see transcript within 5s
```

**Estimated Time**: 4-6 hours

---

### T-024: Pi Deployment Script
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Automate deployment from unRAID to Pi via SSH.

**Tasks**:
- Create `scripts/pi_deploy.sh` with:
  - SSH to Pi (using key or password)
  - Pull latest from GitHub
  - Run `docker compose -f pi/compose.yml up -d --build`
  - Show logs and status
- Add configuration via environment variables or command-line args
- Add error handling and rollback on failure
- Document usage in script header and `pi/README.md`

**Acceptance**:
- Script runs from unRAID without errors
- Connects to Pi via SSH
- Pulls latest code
- Rebuilds and restarts services
- Shows deployment status and logs

**Test**:
```bash
# On unRAID
./scripts/pi_deploy.sh
# Should show: "Connecting to Pi...", "Pulling repo...", "Building...", "Services started"
# Verify on Pi that services are updated
```

**Estimated Time**: 1-2 hours

---

### T-025: ESP32 Firmware Config for Pi MQTT Broker
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Update ESP32 firmware to connect to Pi's MQTT broker instead of unRAID.

**Tasks**:
- Update `firmware/wm_node/secrets.ini` with Pi IP address
- Verify MQTT connection to Pi broker
- Test all MQTT topics (audio, occupancy, encoder, button, ring)
- Update `firmware/wm_node/README.md` with new broker config

**Acceptance**:
- ESP32 nodes connect to Pi MQTT broker at `192.168.8.x:1883`
- All topics publish successfully
- Debug UI on Pi shows ESP32 data

**Test**:
```bash
# On Pi
mosquitto_sub -h localhost -t 'party/+/+/+/+' -v
# Should see messages from node1 and node2
```

**Estimated Time**: 30 minutes

---

### T-026: UI Transcript Panel
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Add transcript display to party tracker UI.

**Tasks**:
- Create `services/ui/static/js/components/transcript-panel.js`
- Subscribe to `party/<house>/pihub/speech/transcript` in state manager
- Display last 10 transcripts with timestamps
- Add confidence indicator (color-coded)
- Style for touchscreen readability
- Add to party tracker UI (not debug UI)

**Acceptance**:
- Transcript panel appears in UI
- Shows latest transcripts in real-time
- Timestamps are human-readable
- Confidence shown visually (green/yellow/red)

**Test**:
- Speak near Pi mic
- Transcript appears in UI within 5 seconds
- Multiple transcripts stack correctly

**Estimated Time**: 2-3 hours

---

### T-027: Party Tracker UI (Touchscreen)
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Create simplified party tracker UI for Pi touchscreen.

**Tasks**:
- Create `services/ui/static/party.html` (new page)
- Create `services/ui/static/js/pages/party-app.js`
- Reuse components: `StatusTable`, `LEDRingViz`, `ConnectionStatus`
- Add new `TranscriptPanel` component
- Design for 7" touchscreen (1024x600)
- Large, touch-friendly buttons and text
- Show: occupancy, transcripts, LED states, connection status
- Add route in `services/ui/main.py` for `/party`

**Acceptance**:
- Party tracker loads at `http://localhost:8000/party`
- Readable on 7" touchscreen
- Shows all nodes (ESP32 + Pi hub)
- Updates in real-time
- Touch-friendly interface

**Test**:
- Load UI on Pi touchscreen
- Verify all data updates
- Test touch interactions
- Leave running for 1 hour, verify stability

**Estimated Time**: 4-6 hours

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

## T-019 Debug UI: Refactor to Modular Architecture ✅ DONE
**Goal:** Refactor debug UI from monolithic 1500+ line file to clean, modular, reusable components.
**Priority:** MEDIUM (not blocking features, but improves maintainability)
**Completed:**
- ✅ **Phase 1**: Extracted core utilities (config, state-manager, mqtt-client, utils)
- ✅ **Phase 2**: Extracted UI components (base-component, status-table, led-ring-viz, signal-chart, etc.)
- ✅ **Phase 3**: Created page orchestrator (debug-app.js) and refactored HTML
- ✅ **Testing**: Validated end-to-end functionality, fixed getNestedValue bug
**Architecture:**
- 12 modular files (4 core, 6 components, 1 orchestrator, 1 HTML template)
- Component-based with BaseComponent abstract class
- Centralized state management with observer pattern
- StatusTable component reused 4 times (Audio, Occupancy, Encoder, Button)
- Configuration-driven rendering (zero code duplication)
**Results:**
- Before: 1 file (1573 lines) → After: 12 files (avg 204 lines/file)
- Adding new panel: Before 200+ lines → After 10 lines
- All existing functionality preserved
- Ready for party tracker UI reuse
**Details:** See `docs/T-019_UI_REFACTOR.md` for complete architecture spec

---
(Keep adding more tickets as scope increases.)
