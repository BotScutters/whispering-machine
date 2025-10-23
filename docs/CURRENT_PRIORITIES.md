# Current Priorities (Party Night: MacBook Interface)

## Status: 🚨 CRITICAL - 3 Days to Party Night

**Last Updated**: October 21, 2025

**MAJOR PIVOT**: Pi is dead. MacBook now serves as the central hub, driving 7" touchscreen and running all services. Focus on creating a compelling "unreliable narrator" that works even with spotty ESP32 sensors.

**Timeline**: 3 days remaining - focus on party-ready interface only.

---

## Party Night Requirements

### Core Vision
> "The Whispering Machine listens. Scattered through the room, its small sensor nodes observe light, movement, and fragments of speech–quietly feeding them into a shared digital mind. The system murmurs back in text and light, a half-comprehending echo of the conversations and energies that surround it. It is playful, confident, and untrustworthy."

### Technical Requirements
- **MacBook**: Runs all services, drives 7" touchscreen, lid can be closed
- **Audio**: MacBook built-in mic → Whisper transcription via Tailscale
- **Sensors**: 3 ESP32 nodes (even if unreliable/garbage signals)
- **Interface**: Compelling, unreliable narrator aesthetic
- **Runtime**: 6+ hours standalone operation
- **Robustness**: Works with 0-3 functioning sensors

---

## 🚨 CRITICAL PATH (3 Days to Party)

**Goal**: MacBook-based party interface that whispers what it hears, even when it's not sure.

**Estimated Total Time**: 22-28 hours

### Day 1: Foundation (8-10 hours)
**T-028: MacBook Service Stack** (2-3 hours)
- Docker compose for MacBook
- All services running locally
- **Blocker**: Must work before anything else

**T-029: MacBook Audio Bridge** (3-4 hours) ⭐ MOST COMPLEX
- Built-in mic capture with lid closed
- Whisper transcription via Tailscale
- **Critical**: Audio is core to the experience

**T-030: Multi-Node Support** (2-3 hours)
- Handle 3 ESP32 nodes
- Robust to unreliable signals
- **Depends on**: T-028

**Checkpoint**: MacBook running all services, 3 nodes connected, audio transcription working

### Day 2: Interface & Intelligence (8-10 hours)
**T-031: Party Interface UI** (4-5 hours) ⭐ MOST VISIBLE
- 7" touchscreen optimized
- Unreliable narrator aesthetic
- **Critical**: This is what people see

**T-032: LLM Agent Service** (3-4 hours)
- Generate unsettling observations
- Incorporate sensor data + randomness
- **Key**: Makes it "intelligent-sounding"

**T-033: Robust Data Processing** (2-3 hours)
- Handle garbage sensor data gracefully
- Confidence indicators
- **Important**: System works even when sensors fail

**Checkpoint**: Compelling interface with intelligent observations, works with unreliable sensors

### Day 3: Polish & Deploy (6-8 hours)
**T-034: Touchscreen Setup** (2-3 hours)
- Closed-lid MacBook operation
- External display configuration
- **Important**: Hide the MacBook

**T-035: Party Mode Deployment** (2-3 hours)
- End-to-end testing
- Emergency procedures
- **Critical**: Must work on party night

**Checkpoint**: Ready for party night, tested for 6+ hours

---

## Key Technical Challenges

### 1. MacBook Closed-Lid Operation
**Challenge**: Run services and capture audio with lid closed
**Research Needed**: macOS behavior, Core Audio, power management
**Fallback**: Leave lid open, display black screen

### 2. Unreliable Sensor Handling
**Challenge**: Make garbage signals compelling, not broken
**Approach**: Embrace uncertainty as part of the aesthetic
**Implementation**: Confidence indicators, partial data, plausible fakes

### 3. LLM Integration
**Challenge**: Generate unsettling observations without being obvious
**Approach**: Mix real sensor data with randomness
**Implementation**: Rate limiting, fallback responses, varied prompts

### 4. 6+ Hour Runtime
**Challenge**: System stability for entire party
**Approach**: Robust error handling, auto-recovery, monitoring
**Implementation**: Health checks, graceful degradation, logging

---

## Architecture Overview

```
MacBook (Closed Lid)
├─ Docker Services
│  ├─ mosquitto (MQTT broker)
│  ├─ aggregator (processes sensor data)
│  ├─ ui (party interface)
│  ├─ audio_bridge (mic → Whisper)
│  └─ llm_agent (generates observations)
├─ Built-in Microphone
└─ External Display (7" touchscreen)

ESP32 Nodes (3x, potentially unreliable)
├─ node1 (audio, PIR, encoder, LED)
├─ node2 (audio, PIR, encoder, LED)
└─ node3 (audio, PIR, encoder, LED)

Tailscale Tunnel
└─ unRAID (faster-whisper transcription)
```

---

## Design Principles

### Unreliable Narrator Aesthetic
- **Playful, confident, untrustworthy**
- Show partial information
- Inject plausible but uncertain data
- Use confidence indicators (high/medium/low/unknown)
- Embrace sensor failures as part of the experience

### Robust Operation
- **Works with 0-3 sensors**
- Graceful degradation when nodes fail
- 6+ hour runtime without intervention
- Closed-lid MacBook operation
- Emergency recovery procedures

### Party-Ready Interface
- **7" touchscreen optimized**
- Large, readable text from 3 feet away
- Touch-friendly interactions
- Full-screen, no browser chrome
- Compelling even when sensors fail

---

## Deferred (Post-Party)

These are valuable but not critical for party night:

- **Pi hub tickets (T-021-T027)**: Pi is dead
- **Sensor debugging**: Fix INMP441 wiring issues
- **LED refinement**: Mode adjustments
- **Generic node auto-discovery**: Nice-to-have
- **Mood detection**: Future enhancement
- **Audio tuning**: Can tune live if needed

---

## Risk Assessment

### High Risk
- **T-029 (Audio Bridge)**: Complex macOS audio capture, closed-lid behavior
  - Mitigation: Research thoroughly, test early, have fallback plan
- **T-031 (Party Interface)**: Most visible, must be compelling
  - Mitigation: Start with simple version, iterate quickly

### Medium Risk
- **T-032 (LLM Agent)**: API dependencies, rate limiting
  - Mitigation: Implement fallback responses, test with API disabled
- **T-034 (Touchscreen Setup)**: macOS display management
  - Mitigation: Test on actual hardware early

### Low Risk
- **T-028 (Service Stack)**: Reusing existing services
- **T-030 (Multi-Node)**: Extending existing aggregator
- **T-033 (Robust Processing)**: Software-only changes
- **T-035 (Deployment)**: Scripting and testing

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

---

## Emergency Procedures

### If MacBook Fails
- **Backup**: Use unRAID services + laptop
- **Fallback**: Debug UI on laptop screen
- **Recovery**: Quick restart script

### If Sensors All Fail
- **Behavior**: Show "unreliable" status
- **Fallback**: Generate plausible fake data
- **Recovery**: Manual sensor restart

### If Whisper Fails
- **Behavior**: Show "listening..." without transcripts
- **Fallback**: Use audio features only
- **Recovery**: Restart audio bridge service

### If Network Fails
- **Behavior**: Show cached data
- **Fallback**: Local-only mode
- **Recovery**: Network restart

---

## Party Night Checklist

### Pre-Party (Day 3)
- [ ] Full system test (6+ hours)
- [ ] Emergency procedures tested
- [ ] Backup plan verified
- [ ] MacBook battery charged
- [ ] Touchscreen calibrated
- [ ] Network stable

### Party Night Setup
- [ ] MacBook in party mode
- [ ] Lid closed, external display active
- [ ] All services running
- [ ] ESP32 nodes powered
- [ ] Touchscreen displaying interface
- [ ] Emergency procedures ready

### During Party
- [ ] Monitor system health
- [ ] Check for error logs
- [ ] Verify observations are generating
- [ ] Ensure interface remains compelling
- [ ] Be ready to intervene if needed

---

## Notes

- **Focus**: Party-ready interface, not perfect sensors
- **Aesthetic**: Unreliable narrator is the goal, not bug-free operation
- **Timeline**: 3 days is tight but doable with focused effort
- **Testing**: Must test with actual hardware early and often
- **Backup**: Always have a fallback plan

**The machine whispers what it hears, even when it's not sure what it heard.** 🎭