# Whispering Machine

> **A sophisticated party monitoring system with ESP32 sensors, real-time audio transcription, and AI-powered observations**

## 🎯 **What It Does**

The Whispering Machine creates an immersive party experience by:
- **Monitoring the environment** with ESP32 sensor nodes (audio features, occupancy, LED rings)
- **Transcribing conversations** in real-time using Whisper AI
- **Generating AI observations** about party dynamics and atmosphere
- **Displaying everything** on a beautiful, real-time web interface

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    WSL2 Laptop Hub                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   MQTT      │  │  Aggregator │  │     UI      │      │
│  │  Broker     │  │   Service   │  │   Service   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Audio     │  │    LLM      │  │   WSL2      │      │
│  │   Bridge    │  │   Agent     │  │  Display    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ MQTT (WiFi)
                              │
┌─────────────────────────────────────────────────────────────┐
│                    ESP32 Sensor Nodes                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Node 1    │  │   Node 2    │  │   Node 3    │      │
│  │  Audio +    │  │  Audio +    │  │  Audio +    │      │
│  │ Occupancy   │  │ Occupancy   │  │ Occupancy   │      │
│  │ LED Ring    │  │ LED Ring    │  │ LED Ring    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- WSL2 with Docker and Docker Compose
- ESP32 development environment (PlatformIO)
- Python 3.10+

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd whispering-machine
```

### **2. Start Services**
```bash
# Start all services
docker compose -f wsl2/compose.yml up -d

# Verify services are running
docker ps
```

### **3. Access the UI**
- **Debug Interface**: http://localhost:8000/debug
- **Party Interface**: http://localhost:8000/party

### **4. Flash ESP32 Nodes**
```bash
# Flash node 1 (first time)
cd firmware/wm_node
pio run -e node1-usb -t upload

# Flash node 2 (first time)  
pio run -e node2-usb -t upload

# Subsequent updates (OTA)
pio run -e node1-ota -t upload
pio run -e node2-ota -t upload
```

### **5. Configure ESP32 Nodes**
Edit `firmware/wm_node/config/nodes.ini` to set:
- WiFi credentials
- MQTT broker IP (your WSL2 laptop IP)
- Node-specific settings

## 🧪 **Testing**

The project includes comprehensive testing infrastructure:

```bash
# Run all tests
make test-all

# Run specific test categories
make test-unit        # Unit tests
make test-integration # Integration tests  
make test-ui         # UI component tests
make test-e2e        # End-to-end tests

# Quick LLM message flow test
make test-llm
```

## 📁 **Project Structure**

```
whispering-machine/
├── services/           # Backend services
│   ├── aggregator/     # MQTT message aggregation
│   ├── ui/            # Web interface
│   ├── llm_agent/     # AI observations
│   └── audio_bridge/  # Audio transcription
├── firmware/           # ESP32 code
│   └── wm_node/       # Sensor node firmware
├── wsl2/              # WSL2 deployment configs
├── schemas/           # MQTT message schemas
├── docs/              # Documentation
└── test_*.py         # Test suites
```

## 🔧 **Development**

### **Service Development**
```bash
# Start infrastructure only
docker compose -f wsl2/compose.yml up mosquitto -d

# Run individual services locally
cd services/aggregator
python app.py
```

### **Firmware Development**
```bash
cd firmware/wm_node
pio run -e node1-usb    # Build for node 1
pio run -e node2-usb    # Build for node 2
pio run -e node1-ota    # OTA update node 1
```

### **Testing Changes**
```bash
# Run tests after changes
make test-all

# Quick verification
make test-llm
```

## 📊 **MQTT Topics**

The system uses structured MQTT topics:

```
party/{house_id}/{node_id}/{domain}/{signal}
```

**Examples:**
- `party/hidden_house/node1/audio/features`
- `party/hidden_house/node2/occupancy/state`
- `party/hidden_house/llm_agent/observations/observation`
- `party/hidden_house/audio_bridge/speech/transcript`

## 🎨 **UI Components**

- **Debug Interface**: Real-time MQTT message monitoring
- **Party Interface**: Immersive party experience display
- **MQTT Debugger**: Message flow visualization
- **Signal Charts**: Real-time sensor data plotting
- **LED Ring Visualization**: ESP32 LED ring status

## 🔍 **Troubleshooting**

### **Services Not Starting**
```bash
# Check service logs
docker logs wsl2_aggregator
docker logs wsl2_ui
docker logs wsl2_llm_agent

# Restart services
docker compose -f wsl2/compose.yml restart
```

### **ESP32 Connection Issues**
```bash
# Check WiFi configuration
# Verify MQTT broker IP address
# Check ESP32 serial output
```

### **MQTT Message Issues**
```bash
# Run MQTT flow tests
make test-llm

# Check MQTT broker logs
docker logs mosquitto
```

## 📚 **Documentation**

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Development Tickets](docs/TICKETS.md)
- [Testing Guide](TESTING.md)
- [Agent Memory](docs/AGENT_MEMORY.md)

## 🤝 **Contributing**

1. **Pick a ticket** from `docs/TICKETS.md`
2. **Run tests** to verify current state: `make test-all`
3. **Make changes** following the testing-driven approach
4. **Verify fixes** with comprehensive tests
5. **Update documentation** as needed

## 🎉 **Party Mode**

When everything is working:
- ESP32 nodes are publishing sensor data
- Audio is being transcribed in real-time
- AI is generating observations about the party
- The UI displays everything beautifully
- LED rings react to the environment

**Welcome to the Whispering Machine!** 🎊