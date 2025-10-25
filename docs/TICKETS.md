# Whispering Machine - Development Tickets

> **Current Architecture**: WSL2 laptop hub with ESP32 nodes, GL-iNet travel router, Tailscale to unRAID Whisper service
> **Target**: Party-ready system with sophisticated UI and reliable MQTT message routing

---

## 🚨 CRITICAL PATH: Testing-Driven Debugging

### T-001: Establish Comprehensive Test Suite
**Status**: TODO  
**Priority**: CRITICAL  
**Goal**: Test-driven debugging to identify and fix MQTT and other issues

**Context**: 
- MQTT message routing issues persist despite multiple attempts
- Other bugs exist that haven't been systematically identified
- Need testing infrastructure to enable fresh eyes and faster debugging
- Testing will reveal root causes of current issues

**Tasks**:
- Fix and enhance existing test suite for WSL2 environment
- Create comprehensive integration tests for MQTT message flow
- Add UI component tests for message display
- Create end-to-end tests for complete system behavior
- Add performance tests for long-running scenarios
- Document testing procedures and make them accessible

**Acceptance**:
- Test suite runs successfully in WSL2 environment
- Tests cover all critical functionality including MQTT routing
- Tests catch regressions reliably
- New developers can run tests immediately
- Tests reveal root causes of current issues

**Test**:
- Run `make test-all` - all tests pass
- Introduce bug, verify tests catch it
- Run tests with fresh eyes to identify issues

**Estimated Time**: 3-4 hours

---

### T-002: Debug MQTT Issues Through Testing
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Use testing to systematically identify and fix MQTT routing issues

**Context**: 
- LLM messages reach UI backend but not frontend components
- Multiple debugging attempts haven't resolved the issue
- Need systematic approach to identify root cause

**Tasks**:
- Create specific tests for MQTT message routing
- Test each component of the message flow pipeline
- Identify exactly where messages are lost
- Fix issues revealed by testing
- Verify fixes with comprehensive tests

**Acceptance**:
- MQTT message routing works reliably
- LLM messages appear in MQTT Debugger
- Party UI displays LLM content
- All message types route correctly

**Test**:
- Run MQTT routing tests
- Verify end-to-end message flow
- Test with different message types and volumes

**Estimated Time**: 2-3 hours

---

## 🧹 REPOSITORY CLEANUP

### T-003: Remove MacBook-Specific Code and Documentation
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Remove obsolete MacBook references and code

**Context**: MacBook is no longer the target platform - WSL2 laptop is the hub

**Tasks**:
- Audit entire repository for MacBook references
- Remove `macbook/` directory and all contents
- Update documentation to remove MacBook mentions
- Remove MacBook-specific Docker configurations
- Update README and architecture docs
- Preserve any valuable MacBook-specific code in comments/docs

**Acceptance**:
- No MacBook references in active code
- `macbook/` directory completely removed
- Documentation reflects WSL2 laptop as hub
- No confusion for new developers

**Test**:
- Search repository for "macbook" - should return only historical references
- Verify no MacBook-specific code in active services
- Check that documentation is clear about current architecture

**Estimated Time**: 1-2 hours

---

### T-004: Remove Windows-Specific Code and Documentation  
**Status**: TODO  
**Priority**: MEDIUM  
**Goal**: Remove obsolete Windows-specific code

**Context**: Windows directory may contain outdated configurations

**Tasks**:
- Audit `windows/` directory for obsolete content
- Remove Windows-specific configurations that are no longer needed
- Update documentation to remove Windows-specific instructions
- Preserve any valuable Windows-specific code in comments/docs

**Acceptance**:
- No obsolete Windows-specific code in active use
- Documentation reflects current WSL2 setup
- No confusion for new developers

**Test**:
- Verify Windows directory doesn't contain active configurations
- Check that documentation is clear about WSL2 setup

**Estimated Time**: 1 hour

---

### T-005: Consolidate and Update Documentation
**Status**: TODO  
**Priority**: HIGH  
**Goal**: Clear, accurate documentation for new developers

**Context**: Multiple outdated docs causing confusion

**Tasks**:
- Audit all documentation files for accuracy
- Remove outdated architecture descriptions
- Consolidate duplicate information
- Update README with current setup instructions
- Create clear getting-started guide
- Update architecture diagrams

**Acceptance**:
- Single source of truth for each topic
- Documentation matches current codebase
- New developers can follow docs without confusion
- Clear separation between historical and current information

**Test**:
- New developer follows docs to set up system
- All documentation links work
- No contradictory information

**Estimated Time**: 2-3 hours

---

## 🧪 TESTING INFRASTRUCTURE

### T-006: Establish Test-Driven Development Discipline
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