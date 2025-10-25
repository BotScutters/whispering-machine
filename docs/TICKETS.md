# Tickets (Well-scoped, agent-ready)

> Contribute via small PRs. Every ticket lists **Acceptance** and **How to test**.

---

## 🚨 CRITICAL PATH: WSL2 Party Interface Issues (Current Session)

**Context**: WSL2 services are running but multiple critical issues need immediate attention for party readiness.

### T-036: Fix Party UI Aesthetic and Responsiveness
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Redesign party UI for 1024x600 touchscreen with sophisticated, subtle aesthetic.

**Tasks**:
- Remove "WHISPERING MACHINE" jittery title (1990s nightmare)
- Remove "PARTY MODE - UNRELIABLE NARRATOR" subtitle
- Remove explicit labels like "this panel contains transcripts" and "this box contains AI observations"
- Redesign with subtle, classy, sophisticated aesthetic
- Make responsive for 1024x600 display
- Reuse debug UI components where appropriate
- Remove pale background, use better color scheme
- Make content self-explanatory without labels

**Acceptance**:
- UI looks sophisticated and subtle on 1024x600 touchscreen
- No explicit labels telling users what things are
- Content is self-explanatory through design
- Responsive layout works properly
- Aesthetic matches debug UI quality

**Test**:
- Load on 1024x600 touchscreen
- Verify no explicit labels
- Test touch interactions
- Compare aesthetic to debug UI

**Estimated Time**: 3-4 hours

---

### T-037: Fix MQTT Connection Issues
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Resolve MQTT connectivity problems preventing ESP32 nodes from connecting.

**Tasks**:
- Investigate why MQTT shows red status in debug/party UI
- Fix mosquitto port configuration (currently 1883:1883 AND 1884:1884)
- Ensure ESP32 nodes can connect to broker at 192.168.50.240:1883
- Test MQTT message flow from ESP32 to UI
- Fix any authentication or network issues

**Acceptance**:
- MQTT status shows green in debug/party UI
- ESP32 nodes successfully connect to broker
- Messages flow from ESP32 → MQTT → UI
- Debug page shows incoming messages

**Test**:
- Check MQTT status in debug UI
- Monitor MQTT messages: `mosquitto_sub -h localhost -t "party/+/+/+/+"`
- Test ESP32 node connection
- Verify message flow end-to-end

**Estimated Time**: 2-3 hours

---

### T-038: Fix Whisper and LLM Agent Services
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Get Whisper transcription and LLM agent services working properly.

**Tasks**:
- Fix Whisper service connection (currently red status)
- Fix LLM agent service (currently red status)
- Ensure proper Tailscale integration for Whisper
- Test audio transcription flow
- Test LLM observation generation

**Acceptance**:
- Whisper status shows green in party UI
- LLM agent status shows green in party UI
- Audio transcription works end-to-end
- LLM observations appear in UI

**Test**:
- Check service status in party UI
- Test audio capture and transcription
- Verify LLM observations appear
- Monitor service logs

**Estimated Time**: 2-3 hours

---

### T-039: Install PlatformIO in WSL2 Environment
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Enable ESP32 firmware development and OTA updates from WSL2.

**Tasks**:
- Install PlatformIO in WSL2 environment
- Configure for ESP32 development
- Test USB and OTA upload capabilities
- Update ESP32 node configurations
- Test firmware updates

**Acceptance**:
- PlatformIO installed and working in WSL2
- Can upload firmware via USB and OTA
- ESP32 nodes respond to updates
- Development workflow works smoothly

**Test**:
- Install PlatformIO
- Test `pio run -e node1-usb -t upload`
- Test `pio run -e node1-ota -t upload`
- Verify ESP32 nodes update successfully

**Estimated Time**: 1-2 hours

---

### T-040: Configure GL-iNet Travel Router Network
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Set up travel router for party network with Tailscale integration.

**Tasks**:
- Configure GL-iNet router to host local WiFi network
- Set up laptop to connect to router network
- Configure ESP32 nodes to connect to router network
- Set up Tailscale connection for Whisper service
- Test end-to-end network connectivity

**Acceptance**:
- Router hosts local WiFi network
- Laptop connects to router network
- ESP32 nodes connect to router network
- Tailscale connection works for Whisper
- All devices can communicate

**Test**:
- Configure router settings
- Test device connections
- Verify Tailscale connectivity
- Test ESP32 → MQTT → UI flow

**Estimated Time**: 2-3 hours

---

### T-041: Fix Debug Mode Activation Mystery
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: Understand and fix debug mode activation behavior.

**Tasks**:
- Investigate why debug mode shows "Debug mode active" vs "Touch to interact"
- Fix inconsistent debug mode behavior
- Ensure touch interactions work properly
- Remove confusing debug mode indicators

**Acceptance**:
- Debug mode behavior is consistent
- Touch interactions work reliably
- No confusing debug mode indicators
- Clear interaction feedback

**Test**:
- Test debug mode activation
- Test touch interactions
- Verify consistent behavior
- Check interaction feedback

**Estimated Time**: 1 hour

---

## 🚨 CRITICAL PATH: MacBook Party Interface (3 Days to Party)

**Architecture**: MacBook runs all services, drives 7" touchscreen, connects to ESP32 nodes + Whisper via Tailscale. Interface must be robust to unreliable sensors and work standalone for 6+ hours.

### T-028: MacBook Service Stack Setup
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Set up MacBook to run all services locally with Docker.

**Tasks**:
- Create `macbook/compose.yml` with services:
  - `mosquitto` (MQTT broker)
  - `aggregator` (processes all node data)
  - `ui` (serves party interface)
  - `audio_bridge` (MacBook mic → Whisper)
  - `llm_agent` (NEW - generates observations)
- Create `macbook/.env.example` with MacBook-specific config
- Add MacBook-specific Dockerfile optimizations
- Configure for closed-lid operation (if possible)

**Acceptance**:
- `docker compose -f macbook/compose.yml up -d` starts all services
- Services run with MacBook lid closed (test 30 minutes)
- MQTT broker reachable at `localhost:1883`
- UI accessible at `http://localhost:8000/party`

**Test**:
```bash
cd /path/to/whispering-machine
docker compose -f macbook/compose.yml up -d
docker ps  # All services running
# Close MacBook lid, wait 30 min, reopen - services still running
```

**Estimated Time**: 2-3 hours

---

### T-029: MacBook Audio Bridge (Built-in Mic → Whisper)
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Capture audio from MacBook built-in microphone, send to Whisper, publish transcripts.

**Tasks**:
- Create `services/audio_bridge/` (reuse from Pi design)
- Implement macOS audio capture (Core Audio / AVAudioEngine)
- Handle closed-lid audio capture (research macOS behavior)
- Implement HTTP client for Whisper (Wyoming protocol)
- Publish transcripts to `party/<house>/macbook/speech/transcript`
- Add fallback for when Whisper is unavailable
- Implement audio chunking (2-5 second segments)

**Acceptance**:
- Captures audio from MacBook mic with lid closed
- Sends audio chunks to Whisper via Tailscale
- Publishes transcripts to MQTT within 5 seconds
- Gracefully handles Whisper downtime
- Works for 6+ hours without intervention

**Test**:
```bash
# With MacBook lid closed
docker logs macbook_audio_bridge --tail 50
mosquitto_sub -h localhost -t 'party/+/macbook/speech/transcript'
# Speak near MacBook, should see transcript within 5s
# Leave running overnight, verify still working
```

**Estimated Time**: 3-4 hours

---

### T-030: ESP32 Multi-Node Support (3 Nodes)
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Support 3 ESP32 nodes with robust handling of unreliable signals.

**Tasks**:
- Update aggregator to handle 3 nodes (node1, node2, node3)
- Add node health monitoring (heartbeat timeout detection)
- Implement graceful degradation when nodes go offline
- Add signal quality scoring (detect "garbage" signals)
- Update UI to show node status (online/offline/degraded)
- Add node discovery (auto-detect new nodes)

**Acceptance**:
- All 3 nodes appear in UI
- UI shows node health status
- System works when 1-2 nodes are offline/degraded
- Garbage signals are filtered out or marked as unreliable
- New nodes auto-appear when they connect

**Test**:
```bash
# Start with all 3 nodes
mosquitto_sub -h localhost -t 'party/+/+/+/+' -v
# Disconnect node3, verify UI shows it as offline
# Reconnect node3, verify it reappears
# Test with garbage signals from node3
```

**Estimated Time**: 2-3 hours

---

### T-031: Party Interface UI (Touchscreen-Optimized)
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Create compelling party interface for 7" touchscreen that works standalone.

**Tasks**:
- Create `services/ui/static/party.html` (full-screen, no browser chrome)
- Create `services/ui/static/js/pages/party-app.js`
- Design for 7" touchscreen (1024x600, large text, touch-friendly)
- Implement "unreliable narrator" aesthetic:
  - Glitchy text effects
  - Partial/obscured information
  - Confidence indicators (high/medium/low/unknown)
  - Random data injection
- Add screensaver mode (black screen with subtle activity)
- Implement auto-refresh and error recovery

**Acceptance**:
- Loads full-screen on touchscreen
- Large, readable text from 3 feet away
- Touch interactions work reliably
- Runs for 6+ hours without browser refresh
- Handles network disconnections gracefully
- Shows "unreliable" aesthetic consistently

**Test**:
- Load on 7" touchscreen
- Test from 3 feet away (readability)
- Leave running overnight
- Test with network disconnection/reconnection
- Verify touch interactions work

**Estimated Time**: 4-5 hours

---

### T-032: LLM Agent Service (Observations & Interpretations)
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Generate intelligent-sounding observations from sensor data to "freak people out".

**Tasks**:
- Create `services/llm_agent/` service
- Implement OpenAI/Anthropic API client
- Create prompt templates for different scenarios:
  - Audio analysis ("I heard someone mention...")
  - Occupancy patterns ("The energy shifted when...")
  - LED interactions ("The lights responded to...")
  - Random observations ("I notice that...")
- Add data injection (sensor data + randomness)
- Publish observations to `party/<house>/macbook/observations`
- Implement rate limiting (don't spam API)
- Add fallback responses when API unavailable

**Acceptance**:
- Generates observations every 2-5 minutes
- Observations sound intelligent and slightly unsettling
- Incorporates real sensor data when available
- Works when sensors are unreliable
- Gracefully handles API failures
- Observations appear in party UI

**Test**:
```bash
mosquitto_sub -h localhost -t 'party/+/macbook/observations'
# Should see observations every few minutes
# Test with API disabled (fallback responses)
# Test with unreliable sensor data
```

**Estimated Time**: 3-4 hours

---

### T-033: Robust Data Processing (Unreliable Sensors)
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Make the system compelling even with garbage/unreliable sensor data.

**Tasks**:
- Implement signal quality assessment:
  - Detect constant zeros (loose connection)
  - Detect random spikes (interference)
  - Detect unrealistic values (wiring issues)
- Add data interpolation/filling for missing values
- Implement "unreliable narrator" data presentation:
  - Show confidence levels
  - Display partial information
  - Add "unknown" states
  - Inject plausible but fake data
- Create fallback behaviors when sensors fail
- Add system status indicators (what's working/broken)

**Acceptance**:
- System works compellingly with 0-3 working sensors
- Garbage signals are handled gracefully
- UI shows appropriate confidence levels
- Fallback behaviors are engaging, not broken
- System status is clear to observers

**Test**:
- Test with all sensors working
- Test with 1 sensor working
- Test with all sensors sending garbage
- Test with sensors going offline mid-party
- Verify UI remains compelling in all cases

**Estimated Time**: 2-3 hours

---

### T-034: Touchscreen Display Setup & Optimization
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Optimize MacBook for driving 7" touchscreen in party setting.

**Tasks**:
- Research MacBook closed-lid operation:
  - Audio capture with lid closed
  - Display output to external monitor
  - Power management settings
- Create display configuration script:
  - Set external monitor as primary
  - Disable internal display
  - Configure for 1024x600 resolution
  - Disable screen saver/sleep
- Add touchscreen calibration (if needed)
- Create startup script for party mode
- Add emergency recovery procedures

**Acceptance**:
- MacBook runs with lid closed
- Audio capture works with lid closed
- External display shows party interface
- No screen saver or sleep during party
- Touchscreen input works correctly
- Can recover from display issues

**Test**:
- Close MacBook lid, verify external display works
- Test audio capture with lid closed
- Leave running for 6+ hours
- Test touchscreen input
- Test recovery from display sleep

**Estimated Time**: 2-3 hours

---

### T-035: Party Mode Deployment & Testing
**Status**: TODO  
**Priority**: HIGH  
**Goal**: End-to-end testing and deployment for party night.

**Tasks**:
- Create `scripts/party_deploy.sh` for MacBook setup
- Add party mode configuration:
  - Disable notifications
  - Set high performance mode
  - Configure network priorities
  - Set up monitoring/logging
- Create emergency procedures:
  - Quick restart script
  - Fallback to debug mode
  - Manual override controls
- Add party night checklist
- Create backup plan (what if MacBook fails?)

**Acceptance**:
- One-command deployment to party mode
- System runs reliably for 6+ hours
- Emergency procedures work
- Backup plan is ready
- Party night checklist is complete

**Test**:
- Run full party simulation (6+ hours)
- Test emergency procedures
- Verify backup plan works
- Complete party night checklist

**Estimated Time**: 2-3 hours

---

## Deferred (Post-Party)

These are valuable but not critical for party night:

- **T-021-T027**: Pi hub tickets (Pi is dead)
- **T-018**: Generic node auto-discovery (nice-to-have)
- **T-001**: Loudness sparkline (polish)
- **T-002**: Mood detection (future enhancement)
- **Sensor debugging**: Fix INMP441 wiring issues (post-party)
- **LED refinement**: Mode adjustments (working well enough)

---

## Execution Plan (3 Days to Party)

### Day 1: Foundation (8-10 hours)
1. ✅ **T-028** - MacBook service stack (morning)
2. ✅ **T-029** - MacBook audio bridge (afternoon)
3. ✅ **T-030** - Multi-node support (evening)
4. **Checkpoint**: MacBook running all services, 3 nodes connected, audio transcription working

### Day 2: Interface & Intelligence (8-10 hours)
5. ✅ **T-031** - Party interface UI (morning)
6. ✅ **T-032** - LLM agent service (afternoon)
7. ✅ **T-033** - Robust data processing (evening)
8. **Checkpoint**: Compelling interface with intelligent observations, works with unreliable sensors

### Day 3: Polish & Deploy (6-8 hours)
9. ✅ **T-034** - Touchscreen setup (morning)
10. ✅ **T-035** - Party mode deployment (afternoon)
11. **Checkpoint**: Ready for party night, tested for 6+ hours

**Total**: 22-28 hours over 3 days

---

## Key Design Principles

### Unreliable Narrator Aesthetic
- **Playful, confident, untrustworthy**
- Show partial information
- Inject plausible but uncertain data
- Use confidence indicators
- Embrace sensor failures as part of the experience

### Robust Operation
- **Works with 0-3 sensors**
- Graceful degradation
- 6+ hour runtime
- Closed-lid MacBook operation
- Emergency recovery procedures

### Party-Ready Interface
- **7" touchscreen optimized**
- Large, readable text
- Touch-friendly interactions
- Full-screen, no browser chrome
- Compelling even when sensors fail

---

## Success Criteria

**Party-ready when**:
- [ ] MacBook runs all services with lid closed
- [ ] 7" touchscreen shows compelling interface
- [ ] Audio transcription works via Tailscale
- [ ] 3 ESP32 nodes supported (even if unreliable)
- [ ] LLM generates unsettling observations
- [ ] System works with garbage sensor data
- [ ] Runs for 6+ hours without intervention
- [ ] Emergency procedures tested
- [ ] Backup plan ready

**The machine whispers what it hears, even when it's not sure what it heard.** 🎭