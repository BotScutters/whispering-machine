# Getting Started Guide

> **Quick setup guide for new developers**

## 🎯 **Goal**
Get the Whispering Machine running locally in under 10 minutes.

## ⚡ **Quick Setup (5 minutes)**

### **1. Prerequisites Check**
```bash
# Verify Docker is running
docker --version
docker compose --version

# Verify Python
python3 --version  # Should be 3.10+
```

### **2. Start Services**
```bash
# Clone and enter directory
cd whispering-machine

# Start all services
docker compose -f wsl2/compose.yml up -d

# Wait 30 seconds for services to start
sleep 30
```

### **3. Verify Everything Works**
```bash
# Run quick test
make test-llm

# Should show: "🎉 ALL TESTS PASSED - LLM message flow is working correctly!"
```

### **4. Access the UI**
- **Debug Interface**: http://localhost:8000/debug
- **Party Interface**: http://localhost:8000/party

## 🔧 **ESP32 Setup (5 minutes)**

### **1. Install PlatformIO**
```bash
# Install PlatformIO
pip install platformio

# Verify installation
pio --version
```

### **2. Configure ESP32**
```bash
# Edit node configuration
nano firmware/wm_node/config/nodes.ini

# Set your WiFi credentials and MQTT broker IP
# MQTT broker IP = your WSL2 laptop IP address
```

### **3. Flash ESP32**
```bash
cd firmware/wm_node

# Flash node 1 (first time)
pio run -e node1-usb -t upload

# Flash node 2 (first time)
pio run -e node2-usb -t upload
```

## 🧪 **Testing Your Setup**

### **Run All Tests**
```bash
make test-all
```

### **Quick Verification**
```bash
# Test MQTT message flow
make test-llm

# Test UI components
make test-ui

# Test individual services
make test-unit
```

## 🎉 **Success Indicators**

You'll know everything is working when:

1. **Services Running**: `docker ps` shows 6 containers running
2. **Tests Passing**: `make test-all` shows all tests passing
3. **UI Accessible**: http://localhost:8000/debug loads properly
4. **ESP32 Connected**: LED rings on ESP32 nodes are active
5. **MQTT Messages**: Debug UI shows real-time MQTT messages

## 🚨 **Common Issues**

### **Services Won't Start**
```bash
# Check logs
docker logs wsl2_aggregator
docker logs wsl2_ui

# Restart services
docker compose -f wsl2/compose.yml restart
```

### **ESP32 Won't Connect**
- Check WiFi credentials in `firmware/wm_node/config/nodes.ini`
- Verify MQTT broker IP address
- Check ESP32 serial output for connection errors

### **Tests Failing**
```bash
# Run individual test categories to isolate issues
make test-unit
make test-integration
make test-ui
```

## 📚 **Next Steps**

Once you have everything running:

1. **Explore the UI**: Check out both debug and party interfaces
2. **Monitor MQTT**: Watch real-time message flow in debug UI
3. **Test ESP32**: Verify sensor data and LED ring responses
4. **Pick a Ticket**: Choose a development task from `docs/TICKETS.md`
5. **Run Tests**: Always run tests before and after changes

## 🎊 **Welcome to the Whispering Machine!**

You're now ready to contribute to this sophisticated party monitoring system. The testing infrastructure will help you make changes confidently, and the comprehensive documentation will guide you through the architecture.

**Happy coding!** 🚀




