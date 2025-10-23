# Tickets (Well-scoped, agent-ready)

> Contribute via small PRs. Every ticket lists **Acceptance** and **How to test**.

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