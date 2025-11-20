# Whispering Machine - Development Tickets

> **Current Architecture**: WSL2 laptop hub with ESP32 nodes, GL-iNet travel router, Tailscale to unRAID Whisper service
> **Target**: Party-ready system with sophisticated UI and reliable MQTT message routing

## 🎯 **NEXT PRIORITIES**

### **CRITICAL: T-006 - Fix Party UI Data Connection**
The Party UI currently looks "stupid" with empty panels. Need to connect real sensor data to make it actually display meaningful information.

### **HIGH: T-007 - Implement Node Name Mapping System**  
Replace technical `node1`, `node2`, `node3` with party-friendly names like "patio", "kitchen", "living room" for better user experience.

### **HIGH: T-008 - Enhance LLM Observations with Real Data Integration**
Current LLM observations are "garbage" - need to make them reflect actual party dynamics and sensor data instead of generic content.

### **HIGH: T-009 - Implement Actual Audio Recording and Processing**
Replace mock audio bridge with real microphone capture and Whisper transcription to enable conversation-aware observations.

---

## ✅ COMPLETED: Testing-Driven Debugging

### T-001: Establish Comprehensive Test Suite
**Status**: ✅ COMPLETED  
**Priority**: CRITICAL  
**Goal**: Test-driven debugging to identify and fix MQTT and other issues

**Completed**:
- ✅ Fixed and enhanced test suite for WSL2 environment
- ✅ Created comprehensive integration tests for MQTT message flow
- ✅ Added UI component tests for message display
- ✅ Created end-to-end tests for complete system behavior
- ✅ Added Makefile with easy test targets (`make test-all`, `make test-llm`)
- ✅ Documented testing procedures in README and GETTING_STARTED

**Result**: Comprehensive testing infrastructure now enables confident development

---

### T-002: Debug MQTT Issues Through Testing
**Status**: ✅ COMPLETED  
**Priority**: HIGH  
**Goal**: Use testing to systematically identify and fix MQTT routing issues

**Completed**:
- ✅ Created targeted LLM message flow integration test
- ✅ Identified root cause: FastAPI startup event not triggering MQTT client
- ✅ Fixed UI backend MQTT client initialization with lifespan context manager
- ✅ Verified LLM messages now flow correctly: Agent → MQTT → UI Backend → WebSocket
- ✅ All MQTT routing tests now pass

**Result**: LLM message routing is working reliably

---

## ✅ COMPLETED: Repository Cleanup

### T-003: Remove MacBook-Specific Code and Documentation
**Status**: ✅ COMPLETED  
**Priority**: HIGH  
**Goal**: Remove obsolete MacBook references and code

**Completed**:
- ✅ Removed MacBook references from active service code
- ✅ Updated MQTT topics from `macbook/` to `audio_bridge/`
- ✅ Fixed service descriptions and documentation strings
- ✅ Verified no MacBook references in active code

**Result**: Clean codebase focused on WSL2 laptop hub architecture

---

### T-005: Consolidate and Update Documentation
**Status**: ✅ COMPLETED  
**Priority**: HIGH  
**Goal**: Clear, accurate documentation for new developers

**Completed**:
- ✅ Created comprehensive README.md with architecture overview
- ✅ Created GETTING_STARTED.md with 10-minute setup guide
- ✅ Updated project structure documentation
- ✅ Added troubleshooting section and development workflow

**Result**: New developers can follow clear documentation to get started

---

## 🎉 PARTY UI OVERHAUL: Making It Actually Interesting

### T-006: Fix Party UI Data Connection
**Status**: ✅ COMPLETED  
**Priority**: CRITICAL  
**Goal**: Connect actual sensor data to Party UI display

**Completed**:
- ✅ Added `updateSensorStatusDisplay()` method with rich visualizations
- ✅ Implemented dynamic scaling for tiny sensor values (RMS scaled 1000x, ZCR scaled 125x)
- ✅ Created visual progress bars using block characters (█) for audio levels
- ✅ Added LED ring color preview boxes with live color rendering
- ✅ Implemented occupancy status with emoji indicators (●/○) and activity percentages
- ✅ Fixed browser caching issues with cache-busting parameters
- ✅ Verified real-time sensor data display from Node 2
- ✅ Enhanced styling with green accents and organized layout

**Result**: Party UI now displays rich, real-time sensor data with visual feedback bars, color previews, and properly scaled values for better readability.

**Test**: Verified Node 2 sensor data displays correctly with visual bars, color previews, and occupancy indicators

---

### T-007: Implement Node Name Mapping System
**Status**: ✅ COMPLETED  
**Priority**: HIGH  
**Goal**: Party-friendly node names instead of technical IDs

**Completed**:
- ✅ Added `NODE_NAMES` mapping in `services/ui/static/js/core/config.js`
- ✅ Created `getNodeName()` helper function for friendly name lookup
- ✅ Updated Party UI to display "Kitchen" instead of "node2"
- ✅ Implemented fallback to node ID if friendly name not found
- ✅ Verified friendly names display correctly in sensor status panel

**Result**: Party UI now shows "Kitchen", "Living Room", "Patio" instead of technical node IDs, making it more party-friendly.

**Test**: Verified "Kitchen" displays for node2 in the Party UI sensor panel

---

### T-008: Enhance LLM Observations with Real Data Integration
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Make LLM observations actually reflect party dynamics

**Context**: 
- Current LLM observations are "garbage" - generic and uninteresting
- Need observations that reflect actual sensor data and party activity
- Should comment on party being "loud", "active", "quiet" based on real signals
- Should subtly reference actual conversations without direct reporting

**Tasks**:
- Modify LLM agent to incorporate real sensor data into prompts
- Add party activity analysis based on audio levels, occupancy patterns
- Implement conversation-aware observations (subtle, not direct reporting)
- Create observation templates that reference actual party dynamics
- Add time-based context (party getting more/less active over time)

**Acceptance**:
- LLM observations mention actual party activity levels
- Observations reference specific rooms/nodes by friendly names
- Comments feel relevant to actual party state
- No generic "LLM garbage" - all observations feel contextual

**Test**:
- Create high/low activity scenarios, verify observations change
- Check observations reference actual sensor readings
- Verify friendly node names are used in observations

**Estimated Time**: 3-4 hours

---

### T-009: Implement Actual Audio Recording and Processing
**Status**: ✅ COMPLETED  
**Priority**: HIGH  
**Goal**: Real audio capture and transcription for conversation-aware observations

**Context**: 
- Current system has mock audio bridge - no real audio processing
- Need actual microphone capture and Whisper transcription
- LLM observations should be conversation-aware without direct reporting
- Audio processing enables sophisticated party commentary

**Tasks**:
- Implement real audio capture from system microphone
- Connect to Whisper transcription service
- Process audio for conversation context (not direct reporting)
- Feed conversation context to LLM agent for better observations
- Add audio level analysis for party activity detection

**Acceptance**:
- Real audio is captured and transcribed
- LLM observations reflect conversation context subtly
- Audio levels contribute to party activity analysis
- No direct conversation reporting - only contextual observations

**Test**:
- Speak near microphone, verify transcription works
- Check LLM observations reflect conversation context
- Verify audio levels affect party activity analysis

**Estimated Time**: 4-5 hours

**Completed**:
- ✅ Implemented browser-based audio recording using Web Audio API and MediaRecorder
- ✅ Created `AudioRecorder` component with automatic 3-second chunk capture
- ✅ Integrated microphone permission handling with automatic start on user interaction
- ✅ Implemented multi-service transcription attempt (Remote Whisper, Local Whisper, OpenAI)
- ✅ Added Wyoming protocol support for faster-whisper service
- ✅ Configured connection to remote Unraid Whisper service at `tiriage.porgy-palermo.ts.net:10300`
- ✅ Integrated transcription results with MQTT publishing to UI backend
- ✅ Added mock fallback for testing when remote service is unavailable
- ✅ Transcripts appear in Party UI "Transcripts" panel with full pipeline integration
- ✅ Audio recording starts automatically on first user click/keydown/touchstart

---

### T-010: Add Encoder Input Integration and Requests
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: Interactive encoder input system for party engagement

**Context**: 
- ESP32 nodes have encoder input capability
- System should detect encoder manipulations
- System should also request encoder interactions
- Creates interactive party experience

**Tasks**:
- Implement encoder input detection and processing
- Add encoder interaction requests from system
- Create encoder-based party games or interactions
- Display encoder activity in Party UI
- Add encoder data to LLM observation context

**Acceptance**:
- System detects encoder rotations/clicks
- System can request encoder interactions
- Encoder activity influences LLM observations
- Party UI shows encoder interaction status

**Test**:
- Rotate encoders, verify detection
- Check system requests encoder interactions
- Verify encoder data influences observations

**Estimated Time**: 2-3 hours

---

### T-011: Implement Long-Term Data Aggregation and Learning
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: System builds knowledge over party duration

**Context**: 
- System should remember and learn from party data over hours
- Should report statistics like "patio has been very active tonight"
- Should detect patterns and trends over time
- Creates sophisticated party commentary

**Tasks**:
- Implement persistent data storage for party sessions
- Add time-based data aggregation (hourly, nightly statistics)
- Create trend analysis for party activity patterns
- Implement learning system that builds on previous data
- Add sophisticated statistics reporting to LLM observations

**Acceptance**:
- System remembers party data across hours
- Reports meaningful statistics about node activity
- Detects patterns and trends over time
- LLM observations reference historical party data

**Test**:
- Run system for extended period, verify data persistence
- Check statistics reporting in observations
- Verify trend detection works over time

**Estimated Time**: 4-5 hours

---

## 🧪 TESTING INFRASTRUCTURE

### T-012: Establish Test-Driven Development Discipline
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Comprehensive testing at multiple levels

**Context**: Need stability and confidence through proper testing

**Requirements**:
- Every code file has associated `test_<filename>.py` or equivalent
- Unit tests for individual functions/classes
- Integration tests within packages
- External integration tests via Docker containers
- High-level end-to-end tests
- Documentation and Makefile targets for running tests

**Tasks**:
- Audit existing test infrastructure
- Create missing unit tests for all services
- Establish integration test patterns
- Create external test containers
- Add Makefile targets for all test levels
- Document testing strategy and procedures

**Acceptance**:
- Every service has comprehensive unit tests
- Integration tests cover service interactions
- External tests verify Docker container behavior
- Makefile provides easy test execution
- Test coverage is documented and tracked

**Test**:
- Run `make test-unit` - all unit tests pass
- Run `make test-integration` - all integration tests pass
- Run `make test-external` - all external tests pass
- Verify test coverage meets standards

**Estimated Time**: 4-6 hours

---

### T-007: Fix and Enhance Test Suite
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Reliable test suite that validates system behavior

**Context**: Existing test suite needs updates for WSL2 environment

**Tasks**:
- Fix `run_tests_docker.sh` for WSL2 environment
- Update test configurations for current service architecture
- Add tests for MQTT message routing
- Add tests for UI component behavior
- Add tests for LLM agent functionality
- Create performance tests for long-running scenarios

**Acceptance**:
- Test suite runs successfully in WSL2
- Tests cover all critical functionality
- Tests catch regressions reliably
- Performance tests validate 6+ hour operation

**Test**:
- Run full test suite - all tests pass
- Introduce bug, verify tests catch it
- Run performance tests for extended periods

**Estimated Time**: 3-4 hours

---

## 🎨 UI IMPROVEMENTS

### T-008: Fix Party UI Content Display
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Party UI displays LLM content properly

**Context**: Party UI is blank despite backend receiving messages

**Tasks**:
- Debug why Party UI doesn't display LLM content
- Fix message routing from backend to Party UI frontend
- Ensure Party UI components receive and display messages
- Test Party UI with real LLM content
- Verify Party UI works on 1024x600 touchscreen

**Acceptance**:
- Party UI displays LLM observations
- Party UI displays LLM transcripts
- Content updates in real-time
- UI works properly on touchscreen

**Test**:
- Load Party UI, verify content appears
- Test with real LLM messages
- Verify touchscreen interaction

**Estimated Time**: 2-3 hours

---

### T-009: Improve Debug UI Performance
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: Smooth Debug UI performance with high message volume

**Context**: Debug UI can be choppy with many messages

**Tasks**:
- Optimize MQTT Debugger rendering
- Implement better message throttling
- Add message filtering options
- Optimize chart rendering
- Add performance monitoring

**Acceptance**:
- Debug UI remains smooth with high message volume
- Message filtering works effectively
- Performance is acceptable for development use

**Test**:
- Run system with high message volume
- Verify UI remains responsive
- Test message filtering functionality

**Estimated Time**: 2-3 hours

---

## 🔧 INFRASTRUCTURE

### T-010: Fix OTA Updates from WSL2
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: ESP32 OTA updates work from WSL2 environment

**Context**: OTA works from MacBook but not from WSL2

**Tasks**:
- Debug WSL2 networking issues for OTA
- Test different network configurations
- Verify ESP32 OTA listener accessibility
- Create reliable OTA update process
- Document OTA troubleshooting

**Acceptance**:
- OTA updates work from WSL2
- Process is reliable and documented
- Troubleshooting guide available

**Test**:
- Upload firmware via OTA from WSL2
- Verify ESP32 nodes update successfully
- Test with different network configurations

**Estimated Time**: 2-3 hours

---

### T-011: Complete Travel Router Setup
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: GL-iNet router configured for party network

**Context**: Router setup started but not completed

**Tasks**:
- Complete GL-iNet router configuration
- Set up Tailscale on router for unRAID access
- Test end-to-end network connectivity
- Document router configuration
- Create router troubleshooting guide

**Acceptance**:
- Router hosts stable local network
- Tailscale connection to unRAID works
- All devices can communicate reliably
- Configuration is documented

**Test**:
- Test laptop and ESP32 connectivity
- Verify Tailscale connection
- Test Whisper service access

**Estimated Time**: 2-3 hours

---

## 📋 EXECUTION PRIORITY (TODAY - Next Few Hours)

### Phase 1: Testing Infrastructure (IMMEDIATE)
1. **T-001**: Establish comprehensive test suite
2. **T-002**: Debug MQTT issues through testing

### Phase 2: Repository Cleanup (IMMEDIATE)  
3. **T-003**: Remove MacBook-specific code
4. **T-004**: Remove Windows-specific code
5. **T-005**: Consolidate documentation

### Phase 3: Standardization (FOLLOWING)
6. **T-006**: Standardize MQTT topic structure
7. **T-007**: Fix Party UI content display

### Phase 4: Polish and Infrastructure (LATER)
8. **T-008**: Improve Debug UI performance
9. **T-009**: Fix OTA updates from WSL2
10. **T-010**: Complete travel router setup

---

## 🎯 SUCCESS CRITERIA

**System is ready when**:
- [ ] LLM messages appear in MQTT Debugger
- [ ] Party UI displays LLM content
- [ ] MQTT topic structure is consistent
- [ ] Repository is clean and well-documented
- [ ] Test suite is comprehensive and reliable
- [ ] New developers can contribute without confusion

**The machine whispers what it hears, even when it's not sure what it heard.** 🎭