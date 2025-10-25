# Agent Handoff: Testing-Driven Debugging for Whispering Machine

## 🎯 **Mission**: Debug MQTT and Service Issues Through Comprehensive Testing

You're taking over a **testing-driven debugging** mission for the Whispering Machine project. The previous agent has cleaned up the repository and established testing infrastructure. Your job is to use this testing framework to systematically identify and fix the root causes of current issues.

---

## 📋 **Current State Summary**

### ✅ **What's Working**
- **WSL2 laptop hub** running all services via Docker Compose
- **ESP32 nodes** connecting to MQTT broker and publishing sensor data
- **UI service** healthy and accessible at `localhost:8000`
- **LLM Agent** healthy and generating observations
- **MQTT broker** running and receiving messages
- **Integration tests** passing (MQTT connectivity, service communication, web interfaces)

### ❌ **Issues Identified by Testing**
- **Aggregator service**: Fails to start within timeout
- **WSL2 Display Manager**: Fails to start within timeout
- **LLM messages**: Reach UI backend but don't appear in MQTT Debugger component
- **Party UI**: Blank despite backend receiving messages

### 🔍 **Key Mystery**
The **LLM messages are reaching the UI backend** (confirmed in logs) and **appearing in browser console**, but **NOT in the MQTT Debugger component**. This suggests a frontend message routing issue.

---

## 🧪 **Testing Infrastructure Available**

### **Test Suite Commands**
```bash
# Run comprehensive test suite
python3 test_suite.py

# Run specific test types
make test-unit      # Unit tests for individual services
make test-integration  # Integration tests between services
make test-external  # External Docker container tests
```

### **Test Results Location**
- **Test Report**: `test_report.json`
- **Test Logs**: Available in terminal output
- **Service Logs**: `docker logs <container_name>`

### **Current Test Status**
- ✅ **Integration Tests**: All passing
- ✅ **UI Service**: Healthy
- ✅ **LLM Agent**: Healthy
- ❌ **Aggregator**: Startup timeout
- ❌ **WSL2 Display Manager**: Startup timeout

---

## 🎯 **Your Mission: T-001 & T-002**

### **T-001: Establish Comprehensive Test Suite** (CRITICAL)
**Goal**: Use testing to systematically identify and fix MQTT and other issues

**Tasks**:
1. **Debug service startup failures** revealed by testing
   - Investigate why aggregator fails to start
   - Investigate why wsl2_display_manager fails to start
   - Check Docker logs for specific error messages
   - Fix startup issues systematically

2. **Create comprehensive MQTT message flow tests**
   - Test each component of the message pipeline
   - Identify exactly where LLM messages are lost
   - Create specific tests for MQTT routing issues

3. **Enhance test coverage**
   - Add UI component tests for message display
   - Add end-to-end tests for complete system behavior
   - Add performance tests for long-running scenarios

**Acceptance**:
- All services start successfully
- Test suite reveals root causes of current issues
- Comprehensive test coverage for MQTT message flow
- New developers can run tests immediately

### **T-002: Debug MQTT Issues Through Testing** (HIGH)
**Goal**: Use testing to systematically identify and fix MQTT routing issues

**Tasks**:
1. **Create specific tests for MQTT message routing**
   - Test LLM Agent → MQTT Broker → UI Backend → WebSocket → Frontend
   - Test each step of the message pipeline
   - Identify exactly where messages are lost

2. **Debug the LLM message mystery**
   - Messages reach UI backend ✅
   - Messages appear in browser console ✅
   - Messages DON'T appear in MQTT Debugger ❌
   - Party UI doesn't display content ❌

3. **Fix issues revealed by testing**
   - Address root causes systematically
   - Verify fixes with comprehensive tests

**Acceptance**:
- LLM messages appear in MQTT Debugger
- Party UI displays LLM content
- All message types route correctly
- End-to-end message flow works reliably

---

## 🔧 **Debugging Tools Available**

### **Docker Commands**
```bash
# Check service status
docker ps

# View service logs
docker logs wsl2_aggregator
docker logs wsl2_wsl2_display_manager
docker logs wsl2_ui
docker logs wsl2_llm_agent

# Restart services
docker restart wsl2_aggregator
docker restart wsl2_wsl2_display_manager
```

### **MQTT Debugging**
```bash
# Subscribe to all messages
docker exec mosquitto mosquitto_sub -t "party/hidden_house/#" -v

# Test specific topics
docker exec mosquitto mosquitto_sub -t "party/hidden_house/llm_agent/#" -v
```

### **Web Interface**
- **Debug UI**: `http://localhost:8000/debug`
- **Party UI**: `http://localhost:8000/party`
- **Browser Console**: Check for JavaScript errors and LLM message logs

---

## 📁 **Key Files to Focus On**

### **Service Configuration**
- `wsl2/compose.yml` - Docker Compose configuration
- `wsl2/.env` - Environment variables

### **UI Components**
- `services/ui/main.py` - UI backend with MQTT handling
- `services/ui/static/js/core/mqtt-client.js` - MQTT client implementation
- `services/ui/static/js/core/config.js` - Topic patterns and configuration
- `services/ui/static/js/components/mqtt-debugger.js` - MQTT Debugger component
- `services/ui/static/js/pages/debug-app.js` - Debug app with LLM handlers

### **LLM Agent**
- `services/llm_agent/mqtt_subscriber.py` - MQTT client for LLM agent

### **Test Infrastructure**
- `test_suite.py` - Main test suite
- `requirements-test.txt` - Test dependencies
- `test_report.json` - Current test results

---

## 🚀 **Getting Started**

### **Step 1: Run the Test Suite**
```bash
cd /home/scbut/src/whispering-machine
python3 test_suite.py
```

### **Step 2: Investigate Service Failures**
```bash
# Check which services are failing
docker ps

# Look at specific service logs
docker logs wsl2_aggregator --tail 50
docker logs wsl2_wsl2_display_manager --tail 50
```

### **Step 3: Debug MQTT Message Flow**
```bash
# Monitor MQTT messages
docker exec mosquitto mosquitto_sub -t "party/hidden_house/#" -v

# Check UI backend logs for LLM messages
docker logs wsl2_ui --tail 100 | grep -E "(llm_agent|observation)"
```

### **Step 4: Test UI Components**
- Open `http://localhost:8000/debug` in browser
- Check browser console for LLM message logs
- Verify MQTT Debugger component behavior

---

## 🎯 **Success Criteria**

**You've succeeded when**:
- [ ] All services start successfully (no timeout failures)
- [ ] LLM messages appear in MQTT Debugger component
- [ ] Party UI displays LLM content properly
- [ ] Test suite comprehensively covers MQTT message flow
- [ ] Root causes of issues are identified and documented
- [ ] Fixes are verified through testing

---

## 📚 **Context for Understanding**

### **Architecture**
- **WSL2 laptop** runs all services via Docker Compose
- **ESP32 nodes** publish sensor data to MQTT broker
- **LLM Agent** generates observations from sensor data
- **UI** displays real-time data via WebSocket connections

### **MQTT Topic Structure**
- ESP32: `party/hidden_house/node1/audio/features`
- LLM Agent: `party/hidden_house/llm_agent/observations/observation`
- Mock Audio: `party/hidden_house/llm_agent/transcripts/transcript`

### **Previous Debugging Attempts**
- ✅ Fixed QoS mismatch (UI now subscribes QoS=1)
- ✅ Added capture groups to LLM topic patterns
- ❌ LLM messages still don't appear in MQTT Debugger
- ❌ Service startup failures remain

---

## 🎭 **The Whispering Machine**

> "The machine whispers what it hears, even when it's not sure what it heard."

Your mission is to make sure the machine can actually whisper - that the LLM observations and transcripts flow properly through the system and appear in the UI where people can see them.

**Good luck! The testing infrastructure is your friend - use it to systematically identify and fix the issues.** 🧪✨
