# Sensor Reference Guide

This document provides technical details on all sensor implementations and signal interpretations.

## Audio Features (INMP441 I²S Microphone)

### Overview
16 kHz sample rate, 1024-sample window (~64ms), published at ~10 Hz

### Signals

#### RMS (Root Mean Square)
- **Range**: 0.0 to ~1.0 (normalized amplitude)
- **Meaning**: Overall sound intensity/loudness
- **Typical Values**:
  - Silence/Background: 0.0001-0.001
  - Speech: 0.01-0.1
  - Music: 0.05-0.3
  - Loud events: >0.3
- **Use Cases**: Volume detection, noise level monitoring, trigger thresholds

#### ZCR (Zero-Crossing Rate)
- **Range**: 0.0 to 1.0 (crossings per sample)
- **Meaning**: Frequency content indicator
  - Low ZCR (0.01-0.1): Predominantly low frequencies (bass, rumble)
  - Medium ZCR (0.1-0.4): Mixed content (music, conversation)
  - High ZCR (0.4-0.8): High frequencies (hiss, cymbals, sibilance)
- **Typical Values**:
  - Silence: 0.01-0.1
  - Speech: 0.2-0.5
  - Music: 0.1-0.3
  - Whistle: 0.5-0.8
- **Use Cases**: Audio classification, speech detection, timbre analysis

#### Low Band (~0-300 Hz)
- **Implementation**: 2nd order Butterworth lowpass @ 300Hz
- **Captures**: Bass, rumble, footsteps, thunder, low drums
- **Typical Values**: 0.0001-0.05
- **Use Cases**: Beat detection, bass response for LED pulsing

#### Mid Band (~300-3000 Hz)
- **Implementation**: Bandpass approximation
- **Captures**: Voice fundamentals, musical midrange, most speech content
- **Typical Values**: 0.0001-0.1
- **Use Cases**: Speech detection, melody tracking

#### High Band (~3000+ Hz)
- **Implementation**: 2nd order Butterworth highpass @ 3000Hz
- **Captures**: Treble, sibilance, cymbals, high-frequency percussion
- **Typical Values**: 0.00001-0.01
- **Use Cases**: Brightness/excitement detection, cymbal hits

### Implementation Notes
- Biquad IIR filters for frequency separation
- Decimated processing (every 4th sample) for CPU efficiency
- Exponential smoothing (α=0.15) for temporal stability
- Static buffer allocation to avoid stack overflow

### Tuning Frequency Bands

Edit `firmware/wm_node/src/i2s_audio.cpp` to adjust filter coefficients:

**Low Band Cutoff** (currently 300 Hz):
- Increase cutoff: Increase b0/b1/b2, decrease a2
- Decrease cutoff: Decrease b0/b1/b2, increase a2

**High Band Cutoff** (currently 3000 Hz):
- Increase cutoff: Adjust a1 toward -1.5
- Decrease cutoff: Adjust a1 toward -0.5

Proper filter design requires calculating biquad coefficients for desired cutoff frequencies.

---

## Occupancy (PIR Sensor - AM312)

### Overview
Digital PIR motion sensor, published at 10 Hz

### Signals

#### Occupied (Boolean)
- **Range**: true/false
- **Meaning**: Motion detected in sensor field of view
- **Characteristics**:
  - Triggers on IR changes (movement)
  - Typical detection range: 3-7 meters
  - Field of view: ~110 degrees
  - Cooldown: ~2-3 seconds after motion stops
- **Use Cases**: Presence detection, activity monitoring, LED triggering

#### Activity (Float)
- **Range**: 0.0 to 1.0
- **Meaning**: Percentage of time motion was detected over last 10 seconds
- **Characteristics**:
  - Computed from rolling 100-sample history at 10 Hz
  - Smooth metric for gradual LED responses
  - 0.0 = no motion, 1.0 = continuous motion
- **Use Cases**: LED intensity modulation, proximity sensing, activity level tracking

#### Transitions (Integer)
- **Range**: 0 to ~20 (typical)
- **Meaning**: Number of motion state changes in last second
- **Characteristics**:
  - High values indicate rapid/erratic motion
  - Low values indicate steady state or slow movement
  - Useful for detecting motion type (calm vs. active)
- **Use Cases**: Motion pattern detection, debugging sensor behavior

### Future Enhancements
- Configurable history window size
- Adjustable publish rate
- Motion pattern classification (walking, gesturing, etc.)

---

## Encoder & Button (Rotary Encoder EC11)

### Overview
Mechanical rotary encoder with integrated push button

### Encoder Signals

#### Position
- **Range**: Integer, unbounded (cumulative)
- **Meaning**: Total encoder rotation since boot
- **Direction**: Increases clockwise, decreases counter-clockwise
- **Resolution**: Typically 4 steps per detent (mechanical encoder)

#### Delta
- **Range**: Integer (typically -5 to +5 per message)
- **Meaning**: Change in position since last publish
- **Positive**: Clockwise rotation
- **Negative**: Counter-clockwise rotation
- **Zero**: No movement
- **Publish Rate**: ~5 Hz when moving, ~1 Hz when idle

### Button Signals

#### Pressed (Boolean)
- **Range**: true/false
- **Meaning**: Current button state
- **true**: Button is pressed
- **false**: Button is released

#### Event (String)
- **Values**: "press" | "release"
- **Meaning**: Explicit event type for edge detection
- **Use Cases**: Mode cycling, command triggering

### Implementation Notes
- Interrupt-driven quadrature decoding
- Software debouncing (25ms for button)
- Visual feedback via LED ring twinkles
- Hardware debouncing recommended (0.1µF caps)

---

## LED Ring (WS2812 - 8 pixels)

### Overview
8-pixel addressable RGB LED ring driven by GPIO5

### Current Implementation
- Local control only (no state publishing yet)
- Command topic: `party/<house>/<node>/ring/cmd`
- Parameters: `{"on": bool, "b": float}` where b is brightness 0.0-1.0

### Planned Enhancements (T-017, T-012)
- State publishing at 1-5 Hz with per-pixel RGB values
- Multiple behavior modes (idle breathing, audio-reactive, etc.)
- Encoder button for mode cycling
- Encoder rotation for parameter adjustment
- Ensemble-based activation (audio + PIR + encoder)

---

## System Signals

### Heartbeat
- **Topic**: `party/<house>/<node>/sys/heartbeat`
- **Payload**: `{"ts_ms": int}`
- **Rate**: Every 5 seconds
- **Purpose**: Liveness monitoring, timestamp validation

### Timestamps

All `ts_ms` fields contain Unix timestamps in milliseconds synchronized via NTP.

**NTP Configuration**:
- Servers: pool.ntp.org, time.nist.gov
- Timezone: PST (UTC-8)
- Sync on WiFi connect
- Fallback to `millis()` if NTP unavailable

**Validation**:
- Proper timestamp: ~1728000000000 (October 2024 range)
- Millis fallback: Small values (~4000000 = ~67 minutes uptime)

---

## Message Schemas

All MQTT message schemas are defined in `schemas/` directory:
- `audio_features.json`
- `occupancy.json`
- `encoder.json`
- `button.json`
- `heartbeat.json`

---

## Future Sensor Additions

### Audio Snippets for Transcription
**Feasibility**: ESP32 can record short audio clips (1-5 seconds) and upload
**Challenges**:
- Storage: Need SD card or upload to server immediately
- Bandwidth: 16kHz 16-bit mono = ~32 KB/second
- Privacy: Must be event-triggered, not continuous
- Processing: Transcription happens on server/Pi, not ESP32

**Recommended Approach** (See T-019, T-020):
1. Continue publishing audio features for real-time responsiveness
2. Add separate "event clip" recording triggered by:
   - High RMS spike (loud event)
   - Button press (manual capture)
   - Specific ZCR patterns (speech detection)
3. Upload clips to UnRAID/Pi via HTTP POST
4. Server-side Whisper transcription
5. Publish transcribed text back to MQTT: `party/<house>/<node>/audio/transcript`

This dual-mode approach gives you both:
- **Real-time**: Audio features for immediate LED/mood response (10 Hz)
- **Transcription**: High-quality audio clips when interesting events occur

**Technical Details**:
- Circular buffer: 5-10 seconds continuous capture
- Clip size: ~160 KB per 5-second clip (16kHz 16-bit mono)
- Throttling: Max 1 clip per 30 seconds
- Privacy: Event-triggered only, configurable via MQTT

### Additional Sensors (Raspberry Pi)
- Camera (motion detection, person detection)
- Temperature/Humidity (BME280)
- Air quality (CCS811)
- Ambient light (BH1750 - deprecated for nodes, could be Pi-attached)

