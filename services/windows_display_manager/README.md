# Windows Touchscreen Setup & Party Mode

Comprehensive Windows laptop configuration for Waveshare 7" touchscreen operation with delightful human interactions and robust error handling.

## 🎯 Overview

The Windows touchscreen system maintains all the delightful features while being compatible with Windows hardware:

- **Robust**: Handles hardware failures, reconnections, and edge cases gracefully
- **Delightful**: Provides moments of whimsy and discovery through easter eggs
- **Windows-Compatible**: Uses Windows APIs and PowerShell for system management
- **Human-Centered**: Optimized for real-world party interactions

## 🎪 Party Mode Features

### Core Functionality
- **Windows Display Management**: Automatic configuration of external displays
- **Power Management**: Disables sleep/screensaver during party using Windows APIs
- **Touch Calibration**: Automatic touchscreen calibration and validation
- **Generic USB Touchscreen Support**: Works with Waveshare and other USB touchscreens

### Delightful Interactions (Windows Edition)
- **Easter Eggs**: Hidden features discoverable through touch patterns
- **Konami Code**: Classic gaming easter egg with Windows-specific messages
- **Secret Patterns**: Corner tap sequences reveal hidden features
- **Long Press Reveals**: Debug mode and system information
- **Multi-Touch Magic**: Visual effects and particle bursts

### Robust Recovery
- **Node Reconnection**: Seamless handling of ESP32 nodes going offline/online
- **Display Recovery**: Automatic recovery from display configuration failures
- **Error Cooldown**: Prevents excessive recovery attempts
- **Graceful Degradation**: System continues working with partial failures

## 🚀 Quick Start

### Prerequisites
- Windows 10/11 laptop
- Docker Desktop for Windows
- PowerShell (included with Windows)
- Waveshare 7" USB touchscreen

### Automatic Setup
```cmd
# Start party mode with automatic configuration
scripts\start_windows_party_mode.bat
```

### Manual Setup
```cmd
# 1. Configure power management
powercfg /change monitor-timeout-ac 0
powercfg /change standby-timeout-ac 0

# 2. Start services
docker compose -f windows/compose.yml up -d

# 3. Access party interface
start http://localhost:8000/party
```

## 🎮 Easter Eggs & Interactions (Windows Edition)

### Konami Code
**Pattern**: Up-Up-Down-Down-Left-Right-Left-Right-B-A (as swipes)
**Effect**: Retro glitch effects, "The Windows machine remembers..." message
**Duration**: 5 seconds

### Secret Tap Pattern
**Pattern**: 5 taps in screen corners
**Effect**: Reveals hidden features, "You found the Windows secret..." message
**Duration**: 3 seconds

### Long Press Reveal
**Pattern**: 3 consecutive long presses
**Effect**: Shows debug overlay with Windows system information
**Duration**: 10 seconds

### Multi-Touch Magic
**Pattern**: 2 consecutive multi-touch gestures
**Effect**: Particle burst animation, "Windows magic detected..." message
**Duration**: 2 seconds

## 🔧 Configuration

### Windows Display Settings
```cmd
# Resolution
set EXTERNAL_DISPLAY_RESOLUTION=1024x600

# Brightness (0-100)
set BRIGHTNESS_PERCENT=80

# Touchscreen device
set WINDOWS_TOUCHSCREEN_DEVICE=USB Touchscreen
```

### Touch Calibration
Calibration data is stored in `%USERPROFILE%\.whispering_machine\windows_touch_calibration.json`:
```json
{
  "calibrated": true,
  "platform": "windows",
  "timestamp": "2025-01-27T12:00:00",
  "resolution": "1024x600",
  "touch_offset_x": 0,
  "touch_offset_y": 0,
  "touch_scale_x": 1.0,
  "touch_scale_y": 1.0,
  "touchscreen_device": "USB Touchscreen",
  "driver_info": "Generic USB Touchscreen Driver",
  "party_mode": true,
  "delightful_interactions": {
    "easter_eggs_enabled": true,
    "konami_code": false,
    "secret_patterns": false,
    "long_press_reveal": false,
    "multi_touch_magic": false
  }
}
```

### MQTT Integration
Touch interactions are published to MQTT topics:
- `party/<house_id>/display/interactions/insights` - Interaction patterns
- `party/<house_id>/display/easter_egg/<type>` - Easter egg triggers
- `party/<house_id>/display/status` - Display status updates

## 🧪 Testing

### Run Tests in Docker
```cmd
# Build Windows display manager
docker compose -f infra/docker-compose.yml build windows_display_manager

# Run tests
docker run --rm -v %CD%\services\windows_display_manager:/app infra-windows_display_manager python test_windows_display_manager.py
```

### Test Coverage
- **Windows Display Configuration**: Power management, resolution, brightness
- **Touch Interactions**: Event recording, pattern detection, easter eggs
- **Recovery Mechanisms**: Error handling, cooldown logic, graceful degradation
- **Edge Cases**: Invalid data, concurrent access, PowerShell failures

## 🛠️ Troubleshooting

### Common Issues

#### Touchscreen Not Working
```cmd
# Check USB device recognition
devmgmt.msc

# Check calibration file
type "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"

# Recalibrate
del "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
scripts\start_windows_party_mode.bat
```

#### External Display Not Detected
```cmd
# Check display detection
powershell -Command "Get-WmiObject -Class Win32_VideoController | Select-Object Name, VideoModeDescription | ConvertTo-Json"

# Manual display configuration
# Use Windows Display Settings (Win + P)
```

#### Power Management Issues
```cmd
# Check current settings
powercfg /query

# Reset to defaults
powercfg /change monitor-timeout-ac 10
powercfg /change standby-timeout-ac 10
```

#### Services Not Starting
```cmd
# Check Docker
docker info

# Check compose file
docker compose -f windows/compose.yml config

# View logs
docker compose -f windows/compose.yml logs
```

### Recovery Procedures

#### Display Recovery
1. Disconnect touchscreen
2. Wait 5 seconds
3. Reconnect touchscreen
4. Run `scripts\start_windows_party_mode.bat`

#### Service Recovery
1. Stop services: `docker compose -f windows/compose.yml down`
2. Restart Docker Desktop
3. Start services: `docker compose -f windows/compose.yml up -d`

#### Full Reset
1. Stop party mode: `Ctrl+C`
2. Reset power settings: `powercfg /change monitor-timeout-ac 10 && powercfg /change standby-timeout-ac 10`
3. Remove calibration: `del "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"`
4. Restart: `scripts\start_windows_party_mode.bat`

## 🎨 Human-Centered Design

### Interaction Philosophy
- **Discoverability**: Features are discoverable through exploration
- **Feedback**: Clear visual and audio feedback for all interactions
- **Forgiveness**: System handles mistakes gracefully
- **Delight**: Unexpected moments of joy and whimsy

### Robustness Principles
- **Graceful Degradation**: System works with partial failures
- **Self-Recovery**: Automatic recovery from common issues
- **Error Tolerance**: Handles invalid input gracefully
- **State Persistence**: Maintains state across reconnections

### Party-Ready Features
- **No Sleep**: Prevents accidental sleep during party
- **Touch Optimized**: Large touch targets, clear feedback
- **Visual Effects**: Engaging animations and transitions
- **Easter Eggs**: Hidden features for discovery and delight

## 📊 Monitoring & Analytics

### Interaction Tracking
- **Touch Patterns**: Frequency and types of interactions
- **Easter Egg Discovery**: Which easter eggs have been found
- **Error Rates**: Frequency of configuration failures
- **Recovery Success**: Success rate of automatic recovery

### Performance Metrics
- **Display Response Time**: Touch input to visual feedback
- **Service Uptime**: Availability of party mode services
- **Recovery Time**: Time to recover from failures
- **User Engagement**: Interaction frequency and patterns

## 🔮 Windows-Specific Features

### PowerShell Integration
- **Display Detection**: Uses WMI to detect displays
- **Power Management**: Uses powercfg for sleep/screensaver control
- **System Information**: Retrieves Windows-specific system data

### USB Touchscreen Support
- **Generic Drivers**: Works with standard USB touchscreen drivers
- **Waveshare Compatibility**: Specifically tested with Waveshare 7" touchscreen
- **Calibration**: Automatic calibration for different touchscreen models

### Windows APIs
- **Display Configuration**: Uses Windows display APIs
- **Power Management**: Uses Windows power management APIs
- **Device Management**: Uses Windows device management APIs

## 🎉 Party Mode Success Criteria

### Technical Requirements
- ✅ Windows laptop runs with external display
- ✅ External display shows party interface
- ✅ Touch input works correctly
- ✅ No screen saver or sleep during party
- ✅ Automatic recovery from failures

### Human Experience Goals
- ✅ Moments of delight and discovery
- ✅ Robust to unexpected interactions
- ✅ Seamless node reconnection
- ✅ Engaging visual feedback
- ✅ Hidden features for exploration

## 🚀 Migration from MacBook

### What Changes
- **Display Management**: macOS APIs → Windows APIs
- **Power Management**: pmset → powercfg
- **Audio Capture**: macOS-specific → Windows-compatible
- **Touchscreen**: macOS drivers → Windows generic drivers

### What Stays the Same
- **All Services**: MQTT, Aggregator, UI, Audio Bridge, LLM Agent
- **Easter Eggs**: All delightful interactions preserved
- **Robustness**: All error handling and recovery mechanisms
- **Human Experience**: Same moments of delight and discovery

The Windows touchscreen system creates the same magical, robust, and delightful experience while being compatible with Windows hardware and the Waveshare touchscreen! 🎊✨

## 🎯 Why Windows is the Right Choice

1. **Touchscreen Compatibility**: Windows has excellent generic USB touchscreen support
2. **Power**: 5-year-old gaming laptop has plenty of power for all services
3. **Docker Support**: Full Docker Desktop support for all containerized services
4. **Timeline**: Minimal code changes needed - most services are already platform-agnostic
5. **Reliability**: Windows is more predictable for hardware compatibility than macOS

This solution maintains all the delightful features while solving the hardware compatibility issue! 🌟
