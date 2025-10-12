# Testing Guide

## Manual Testing

### Debug UI Validation

**Access**: http://localhost:8000/debug

#### Connection Status
- [ ] WS indicator turns green when page loads
- [ ] MQTT indicator turns green when messages flow
- [ ] Indicators turn red when disconnected

#### Signal Plotting
- [ ] Node selector populates with discovered nodes (node1, node2, etc.)
- [ ] Can select and add any signal (audio.rms, occupancy.activity, etc.)
- [ ] Signals appear as colored tags above chart
- [ ] Chart updates in real-time with live data
- [ ] Time range buttons work (5s, 30s, 1m, 5m, 1h)
- [ ] Log scale toggle works (linear ↔ logarithmic)
- [ ] Click signal name to toggle visibility
- [ ] Click color dot to cycle colors
- [ ] Click × to remove signal
- [ ] Signal config persists across page reloads

#### Audio Status Table
- [ ] Table shows all nodes as columns
- [ ] RMS, ZCR, low, mid, high update in real-time
- [ ] Values are numeric (6 decimal places)
- [ ] Tooltips appear on hover with descriptions
- [ ] Tooltips stay within window bounds

#### Occupancy Status Table
- [ ] Shows occupied (YES/NO), activity (%), transitions
- [ ] Activity rises/falls with motion
- [ ] Transitions spike when waving hand
- [ ] All metrics update in real-time

#### LED Ring Simulator
- [ ] Shows circular visualization for each node
- [ ] Displays correct number of LEDs (8)
- [ ] RGB colors match physical LEDs
- [ ] Glow effects on brighter LEDs
- [ ] Mode name displayed correctly
- [ ] Brightness and speed shown

#### Encoder & Button Status
- [ ] Shows per-node encoder position and delta
- [ ] Delta shows incremental changes (not static)
- [ ] Button state shows pressed/released
- [ ] Event type (press/release) displayed
- [ ] Updates in real-time

#### MQTT Debugger
- [ ] Messages appear in log
- [ ] Filter works (substring or regex)
- [ ] Clear button empties log
- [ ] Shows topic, payload, timestamp
- [ ] Most recent messages at top

---

## MQTT Testing

### Publish Test Messages

**Audio features**:
```bash
mosquitto_pub -h localhost -p 1884 -t "party/houseA/test/audio/features" \
  -m '{"rms":0.005,"zcr":0.15,"low":0.002,"mid":0.003,"high":0.001,"ts_ms":1234567890}'
```

**Occupancy**:
```bash
mosquitto_pub -h localhost -p 1884 -t "party/houseA/test/occupancy/state" \
  -m '{"occupied":true,"activity":0.8,"transitions":5,"ts_ms":1234567890}'
```

**Ring state**:
```bash
mosquitto_pub -h localhost -p 1884 -t "party/houseA/test/ring/state" \
  -m '{"mode":3,"brightness":0.5,"speed":1.0,"color":16729088,"pixel_count":8,"pixels":[16711680,16776960,65280,65535,255,8388863,16711935,16729344],"ts_ms":1234567890}'
```

### Subscribe to All Topics

```bash
mosquitto_sub -h localhost -p 1884 -t "party/houseA/#" -v
```

Expected topics:
- `party/houseA/node1/audio/features`
- `party/houseA/node1/occupancy/state`
- `party/houseA/node1/ring/state`
- `party/houseA/node1/input/encoder`
- `party/houseA/node1/input/button`
- `party/houseA/node1/sys/heartbeat`

(Same for node2, node3, etc.)

---

## Firmware Testing

### Build and Deploy
```bash
cd firmware/wm_node
pio run -e node1-ota -t upload
```

### Serial Monitor
```bash
pio device monitor -e node1-usb
```

Expected boot sequence:
```
[BOOT] node=node1 house=houseA sha=... built=...
[WiFi] Connecting to ...
[WiFi] Connected: IP ...
[NTP] Time synced: ...
[MQTT] Connected to mosquitto:1883
[BOOT] Topics:
  party/houseA/node1/audio/features
  party/houseA/node1/occupancy/state
  ...
```

### Sensor Validation
- **Audio**: Make noise → RMS increases
- **PIR**: Wave hand → activity rises, transitions spike
- **Encoder**: Rotate → position changes, delta shows direction
- **Button**: Press → mode cycles, event published
- **LED Ring**: Visual confirmation of mode changes

---

## Component Testing (Future: Unit Tests)

### Core Utilities
- `getNestedValue()` / `setNestedValue()` - nested object access
- `decodeRGB()` - 32-bit to RGB conversion
- `boostSaturation()` - color visibility enhancement
- `parseTopic()` - MQTT topic parsing

### State Manager
- Subscriptions trigger on updates
- Wildcard patterns match correctly
- Batch updates work
- Clear/reset functionality

### Components
- BaseComponent lifecycle (init, update, render, destroy)
- StatusTable with different configs
- SignalChart add/remove signals
- LEDRingViz color decoding
- MQTTDebugger filtering

---

## Integration Testing

### Service Dependencies
- [ ] MQTT broker running
- [ ] Aggregator subscribing to topics
- [ ] UI WebSocket connections working
- [ ] ESP32 nodes publishing data

### Data Flow
```
ESP32 → MQTT Broker → Aggregator → MQTT (ui/state)
                    ↓
                    UI (/ws/debug) → State Manager → Components → DOM
```

- [ ] Messages flow through all layers
- [ ] No data loss or corruption
- [ ] Timestamps synchronized
- [ ] Schema validation passes

### Error Handling
- [ ] UI gracefully handles broker disconnect
- [ ] Reconnects automatically
- [ ] Shows connection status
- [ ] No crashes on malformed messages

---

## Performance Testing

### Metrics to Monitor
- **Message Rate**: ~50 messages/second (10 Hz × 5 topics × 2 nodes)
- **UI Update Rate**: ~3 FPS (300ms interval)
- **Memory Usage**: Should stay stable (no leaks)
- **CPU Usage**: < 5% for UI, < 10% per ESP32

### Load Testing
- 3-4 nodes publishing simultaneously
- Run for 24+ hours
- Check for memory growth, CPU spikes
- Verify localStorage doesn't grow unbounded

---

## Regression Testing Checklist

After any major change, verify:
- [ ] All status tables update
- [ ] Charts plot correctly
- [ ] LED ring visualization works
- [ ] MQTT debugger shows messages
- [ ] Connection indicators accurate
- [ ] Signal config persists
- [ ] Tooltips work
- [ ] No console errors
- [ ] All routes work (/,  /debug, /debug-simple)

---

## Automated Testing (Future)

### Unit Tests (Jest/Vitest)
- Core utilities (utils.js)
- State manager (subscribe, update, get)
- Topic pattern matching
- RGB color conversion

### Integration Tests (Playwright)
- Page loads correctly
- WebSocket connects
- Charts render
- User interactions work

### E2E Tests
- Full system with actual MQTT broker
- Publish test messages
- Verify UI updates
- Check all panels

---

## Test Environment

### Local Development
- Docker Compose with all services
- ESP32 nodes on local network
- Browser: Chrome/Firefox (ES6 module support required)

### Deployment Testing
- Same as local but on production hardware
- 24/7 stability testing
- Real-world sensor validation


