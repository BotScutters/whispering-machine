# 🎯 Hardware Testing Guide - Windows Laptop + Waveshare Touchscreen

## 🚀 **Tomorrow's Mission: Get the Whispering Machine Running!**

### **Hardware Setup Checklist:**
- [ ] Windows gaming laptop (5+ years old)
- [ ] Waveshare 7" USB touchscreen
- [ ] ESP32 nodes (x3) with INMP441 mics, PIR sensors, encoders, LED rings
- [ ] USB cables and power supplies
- [ ] Network connection (WiFi or Ethernet)

---

## 📋 **Step-by-Step Hardware Testing Instructions**

### **Phase 1: Windows Laptop Setup (30 minutes)**

#### **1.1 Prerequisites Check**
```cmd
# Check Windows version
winver

# Check if Docker Desktop is installed
docker --version
docker compose version

# If Docker not installed:
# Download from: https://www.docker.com/products/docker-desktop/
# Install Docker Desktop for Windows
```

#### **1.2 Clone Repository**
```cmd
# Clone the repository
git clone https://github.com/YOUR_USERNAME/whispering-machine.git
cd whispering-machine

# Check that all files are present
dir
dir windows
dir scripts
```

#### **1.3 Environment Configuration**
```cmd
# Copy environment template
copy windows\env.example windows\.env

# Edit the .env file with your settings
notepad windows\.env
```

**Required .env settings:**
```ini
# Update these values:
HOUSE_ID=your_house_name
WHISPER_URL=http://YOUR_UNRAID_IP:9000/whisper
OPENAI_API_KEY=your_openai_key
# or
ANTHROPIC_API_KEY=your_anthropic_key
```

### **Phase 2: Touchscreen Setup (45 minutes)**

#### **2.1 Physical Connection**
1. **Connect Waveshare touchscreen to Windows laptop via USB**
2. **Connect external power supply to touchscreen**
3. **Wait for Windows to detect the device**

#### **2.2 Driver Installation**
```cmd
# Check if device is recognized
devmgmt.msc

# Look for:
# - "USB Input Device" under Human Interface Devices
# - "Generic USB Touchscreen" or similar
# - Any devices with yellow warning triangles

# If no touchscreen detected:
# - Try different USB ports
# - Check power supply connection
# - Restart Windows
```

#### **2.3 Display Configuration**
```cmd
# Open Display Settings
# Press Win + P to open projection options
# Select "Extend" or "Second screen only"

# Or use PowerShell to check displays
powershell -Command "Get-WmiObject -Class Win32_VideoController | Select-Object Name, VideoModeDescription"
```

#### **2.4 Touchscreen Calibration**
```cmd
# Run the party mode script (this will create calibration)
scripts\start_windows_party_mode.bat

# Check calibration file was created
type "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
```

### **Phase 3: Service Deployment (30 minutes)**

#### **3.1 Start Services**
```cmd
# Start all services
docker compose -f windows/compose.yml up -d

# Check service status
docker compose -f windows/compose.yml ps

# View logs if needed
docker compose -f windows/compose.yml logs
```

#### **3.2 Verify Services**
```cmd
# Check MQTT broker
curl http://localhost:1883

# Check UI service
start http://localhost:8000/party

# Check service health
docker compose -f windows/compose.yml ps
```

### **Phase 4: ESP32 Node Testing (60 minutes)**

#### **4.1 ESP32 Configuration**
```bash
# On your development machine (unRAID)
cd firmware/wm_node

# Update WiFi credentials
nano secrets.ini
# Set:
# WIFI_SSID=your_wifi_name
# WIFI_PASSWORD=your_wifi_password

# Update MQTT broker IP to Windows laptop
nano common.ini
# Set:
# MQTT_BROKER=192.168.1.XXX  # Windows laptop IP
# MQTT_PORT=1883
```

#### **4.2 Flash ESP32 Nodes**
```bash
# Flash each node
pio run -e node1-usb -t upload
pio run -e node2-usb -t upload  
pio run -e node3-usb -t upload

# Monitor serial output
pio device monitor
```

#### **4.3 Test ESP32 Connectivity**
```cmd
# On Windows laptop, monitor MQTT messages
# Install mosquitto client tools
# Download from: https://mosquitto.org/download/

# Subscribe to all messages
mosquitto_sub -h localhost -t "party/+/+/+/+"

# Should see messages like:
# party/your_house/node1/audio/features
# party/your_house/node1/sys/heartbeat
# party/your_house/node1/occupancy/state
```

### **Phase 5: Integration Testing (45 minutes)**

#### **5.1 Touchscreen Interaction Test**
1. **Open party interface**: `http://localhost:8000/party`
2. **Test basic touch**: Tap, swipe, long press
3. **Test easter eggs**:
   - **Konami Code**: Swipe up-up-down-down-left-right-left-right
   - **Secret Pattern**: Tap corners of screen
   - **Long Press**: Hold for 3+ seconds
   - **Multi-Touch**: Use two fingers

#### **5.2 Audio Capture Test**
```cmd
# Check audio devices
powershell -Command "Get-WmiObject -Class Win32_SoundDevice"

# Test audio bridge service
docker logs windows_audio_bridge

# Should see audio capture messages
```

#### **5.3 ESP32 Sensor Test**
1. **Audio Features**: Speak near ESP32 microphones
2. **Occupancy**: Wave hand in front of PIR sensors
3. **Encoder**: Turn rotary encoders
4. **LED Rings**: Should respond to audio/occupancy

#### **5.4 LLM Agent Test**
```cmd
# Check LLM agent logs
docker logs windows_llm_agent

# Should see observation generation
# Check MQTT for observation messages
mosquitto_sub -h localhost -t "party/+/llm_agent/observations/+"
```

---

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions:**

#### **Touchscreen Not Working**
```cmd
# Check device manager
devmgmt.msc

# Look for:
# - USB Input Device (should be present)
# - Generic USB Touchscreen (may not be present)

# Solutions:
# 1. Try different USB port
# 2. Restart Windows
# 3. Check power supply
# 4. Try different USB cable
```

#### **Services Won't Start**
```cmd
# Check Docker Desktop is running
docker info

# Check port conflicts
netstat -an | findstr :8000
netstat -an | findstr :1883

# Restart Docker Desktop
# Restart Windows if needed
```

#### **ESP32 Nodes Not Connecting**
```bash
# Check WiFi credentials
cat firmware/wm_node/secrets.ini

# Check MQTT broker IP
cat firmware/wm_node/common.ini

# Monitor serial output
pio device monitor

# Common issues:
# - Wrong WiFi password
# - Wrong MQTT broker IP
# - Network firewall blocking port 1883
```

#### **Audio Not Capturing**
```cmd
# Check audio devices
powershell -Command "Get-WmiObject -Class Win32_SoundDevice"

# Check audio bridge logs
docker logs windows_audio_bridge

# Common issues:
# - No microphone detected
# - Microphone permissions denied
# - Audio device index wrong
```

---

## 🎯 **Success Criteria Checklist**

### **Hardware Setup:**
- [ ] Windows laptop boots and runs Docker
- [ ] Waveshare touchscreen detected by Windows
- [ ] Touchscreen responds to touch input
- [ ] External display shows party interface

### **Service Deployment:**
- [ ] All Docker services start successfully
- [ ] MQTT broker accessible on port 1883
- [ ] Party UI accessible on port 8000
- [ ] Audio bridge capturing audio
- [ ] LLM agent generating observations

### **ESP32 Integration:**
- [ ] All 3 ESP32 nodes connect to WiFi
- [ ] ESP32 nodes publish to MQTT broker
- [ ] Audio features detected from microphones
- [ ] Occupancy detected from PIR sensors
- [ ] LED rings respond to sensor data

### **Touchscreen Interactions:**
- [ ] Basic touch input works
- [ ] Easter eggs trigger correctly
- [ ] Visual feedback appears
- [ ] MQTT interaction messages published

### **End-to-End Functionality:**
- [ ] ESP32 sensors → MQTT → Aggregator → UI
- [ ] Audio capture → Whisper → MQTT → UI
- [ ] Touch interactions → Display Manager → MQTT
- [ ] LLM observations → MQTT → UI
- [ ] System handles node disconnections gracefully

---

## 🎉 **Party Mode Activation**

### **Final Steps:**
1. **Run party mode script**: `scripts\start_windows_party_mode.bat`
2. **Access party interface**: `http://localhost:8000/party`
3. **Test all interactions**: Touch, sensors, audio, easter eggs
4. **Verify robustness**: Disconnect/reconnect ESP32 nodes
5. **Party ready**: System handles real-world chaos gracefully!

### **Expected Behavior:**
- **Touchscreen**: Responsive with visual feedback
- **ESP32 Nodes**: Publish sensor data continuously
- **Audio**: Captures and transcribes speech
- **LLM Agent**: Generates unsettling observations
- **Easter Eggs**: Hidden features discoverable through interaction
- **Recovery**: Automatic recovery from failures

---

## 🚨 **Emergency Procedures**

### **If Everything Breaks:**
1. **Stop all services**: `docker compose -f windows/compose.yml down`
2. **Restart Docker Desktop**
3. **Restart Windows**
4. **Re-run setup**: `scripts\start_windows_party_mode.bat`

### **If Touchscreen Stops Working:**
1. **Disconnect USB cable**
2. **Wait 10 seconds**
3. **Reconnect USB cable**
4. **Check Device Manager**

### **If ESP32 Nodes Stop Working:**
1. **Check WiFi connection**
2. **Check MQTT broker IP**
3. **Restart ESP32 nodes**
4. **Monitor serial output**

---

## 🎊 **You're Ready for Party Mode!**

Once all tests pass, you'll have a magical, robust, and delightful party experience that:

- **Handles Real-World Chaos**: Robust to hardware failures and unexpected interactions
- **Provides Moments of Wonder**: Easter eggs, secret patterns, and delightful discoveries  
- **Maintains Reliability**: Graceful degradation and automatic recovery
- **Delivers Magic**: Touchscreen interactions with visual effects and engaging feedback

**The Whispering Machine is ready to whisper its unsettling observations at your next party!** 🎭✨

---

## 📞 **Support**

If you run into issues:
1. **Check logs**: `docker compose -f windows/compose.yml logs`
2. **Check device manager**: `devmgmt.msc`
3. **Check network**: `ipconfig` and `ping` tests
4. **Restart services**: Stop and start Docker containers
5. **Restart Windows**: Sometimes a reboot fixes everything

**Good luck with the hardware testing! The software is solid - now let's make it dance with the hardware!** 🎉
