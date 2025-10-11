# Encoder & Button Debugging Guide

## Changes Made in T-014

### NTP Time Synchronization
**File**: `src/wifi_ota.cpp`, `src/wifi_ota.h`

#### Clock Synchronization
**Problem**: Nodes used `millis()` for timestamps, resulting in relative timestamps since boot
**Solution**: Added NTP time synchronization on WiFi connect
- Syncs with `pool.ntp.org` and `time.nist.gov`
- Falls back to `millis()` if NTP unavailable
- All `ts_ms` fields now contain proper Unix timestamps in milliseconds

#### New Function: `get_timestamp_ms()`
Returns Unix timestamp in milliseconds if NTP synced, otherwise falls back to `millis()`

**Usage**: Replace `millis()` with `get_timestamp_ms()` in all MQTT publish calls

## Changes Made in T-014

### Encoder Signal Improvements
**File**: `src/encoder.cpp`

#### Delta Calculation Fix
**Problem**: Delta appeared static or reset unexpectedly
**Root Cause**: `g_delta` was reset to 0 immediately after reading, so it only accumulated changes within the 150ms coalesce window
**Solution**: 
- Delta now represents incremental change since last publish (still resets, but published consistently)
- Publish rate increased to 200ms (5 Hz) for smoother updates
- Added periodic heartbeat: publishes every 1 second even if no movement (for debug UI validation)

#### Expected Behavior After Update:
- **Position (`pos`)**: Cumulative encoder position, increases clockwise, decreases counter-clockwise
- **Delta (`delta`)**: Change since last publish
  - Positive delta = clockwise rotation
  - Negative delta = counter-clockwise rotation
  - Zero delta = no movement since last publish
- **Publish rate**: ~5 Hz when moving, ~1 Hz when idle

### Button Event Enhancements
**File**: `src/encoder.cpp`

#### Added Event Type Field
**Problem**: Only "pressed" boolean was published, hard to distinguish press from release
**Solution**: Added `"event"` field with values `"press"` or `"release"`

#### Message Format:
```json
{
  "pressed": true,
  "event": "press",
  "ts_ms": 1234567890
}
```

#### Expected Behavior:
- Press button: `{"pressed": true, "event": "press", "ts_ms": ...}`
- Release button: `{"pressed": false, "event": "release", "ts_ms": ...}`
- LED feedback: Pixel 1 flashes blue on press

## Debug UI Enhancements

### Status Tables
- **Encoder & Button Status** panel now shows:
  - Encoder table: pos and delta per node
  - Button table: state, last event, timestamp per node
- Tables auto-populate as data arrives
- Alphabetically sorted by node

### Signal Plotting
- Can now plot `encoder.pos` and `encoder.delta` from any node
- Add via "Add Signal" interface
- Data flows through `nodeData.encoder` structure

## Testing After Deployment

### 1. Verify Encoder Delta
```bash
mosquitto_sub -h 192.168.50.69 -p 1884 -t 'party/houseA/+/input/encoder' -v
```

**Expected**: 
- Rotate clockwise: see positive deltas
- Rotate counter-clockwise: see negative deltas
- Stop rotating: deltas go to 0, but periodic updates continue

### 2. Verify Button Events
```bash
mosquitto_sub -h 192.168.50.69 -p 1884 -t 'party/houseA/+/input/button' -v
```

**Expected**:
- Press button: `{"pressed":true,"event":"press",...}`
- Release button: `{"pressed":false,"event":"release",...}`

### 3. Debug UI Validation
- Open `http://localhost:8000/debug-full`
- Check **Encoder & Button Status** panel
- Should show real-time pos/delta/button state for all nodes
- Add `encoder.pos` or `encoder.delta` signals to chart
- Rotate encoder, observe live plotting

## Common Issues & Solutions

### Encoder Bouncing / Wrong Counts
**Symptoms**: Position jumps erratically, counts in wrong direction
**Solutions**:
1. Add hardware debouncing: 0.1 µF capacitors from Pin A to GND and Pin B to GND
2. Check wiring: ensure common ground, proper pullup configuration
3. Try different coalesce window (adjust `200` in line 48 of encoder.cpp)

### Button Chattering
**Symptoms**: Multiple press/release events for single button press
**Solutions**:
1. Current debounce is 25ms - may need to increase
2. Add hardware debouncing: 0.1 µF capacitor across switch pins
3. Increase `BTN_DEBOUNCE_MS` in encoder.cpp

### Node-Specific Behavior Differences
**Symptoms**: node1 and node2 encoders behave differently
**Possible Causes**:
1. Different encoder hardware quality
2. Wiring differences (cable length, connector quality)
3. Different noise environments
4. One encoder may be defective

**Debugging**:
- Use debug UI to plot both `node1/encoder.pos` and `node2/encoder.pos` simultaneously
- Compare delta values - should be similar for similar rotation speeds
- Check MQTT message rates in debug log

## Next Steps

After deploying these changes:
1. Validate delta calculation works as expected
2. Verify button press/release events appear correctly
3. Compare node1 vs node2 encoder behavior
4. Tune debounce values if needed
5. Consider hardware improvements (caps, shielded cables)

