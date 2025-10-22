# Audio Feature Extraction - Implementation Notes

> **For user-facing documentation**, see `docs/SENSOR_REFERENCE.md`

## Implementation Overview
Comprehensive audio feature extraction from INMP441 I²S microphone at 16 kHz sample rate.

### Features Computed

#### 1. RMS (Root Mean Square)
- **Range**: 0.0 to ~1.0 (normalized amplitude)
- **Meaning**: Overall sound intensity/loudness
- **Use cases**: Volume detection, noise level monitoring

#### 2. ZCR (Zero-Crossing Rate)
- **Range**: 0.0 to 1.0 (crossings per sample)
- **Meaning**: Frequency content indicator
  - Low ZCR: Predominantly low frequencies (bass, rumble)
  - High ZCR: High frequencies (hiss, cymbals, voice)
- **Use cases**: Audio classification, detecting speech vs music

#### 3. Low Band (~0-300 Hz)
- **Implementation**: 2nd order Butterworth lowpass @ 300Hz
- **Captures**: Bass, rumble, footsteps, thunder
- **Coefficients**: b0=0.0007, b1=0.0013, b2=0.0007, a1=-1.9633, a2=0.9660

#### 4. Mid Band (~300-3000 Hz)
- **Implementation**: Bandpass approximation
- **Captures**: Voice fundamentals, musical midrange
- **Coefficients**: b0=0.05, b1=0.09, b2=0.05, a1=-1.5, a2=0.6

#### 5. High Band (~3000+ Hz)
- **Implementation**: 2nd order Butterworth highpass @ 3000Hz
- **Captures**: Treble, sibilance, cymbals
- **Coefficients**: b0=0.6, b1=-1.2, b2=0.6, a1=-1.0, a2=0.3

### Technical Implementation

#### File Changes
- **i2s_audio.h**: Added `AudioFeatures` struct
- **i2s_audio.cpp**: Implemented `i2s_audio_features()` function
- **main.cpp**: Updated to use new `i2s_audio_features()` API

#### Processing Pipeline
1. Read 1024 samples from I²S DMA buffer (~64ms window at 16kHz)
2. Convert 24-bit samples to normalized float (-1.0 to 1.0)
3. Compute RMS via sum of squares
4. Count zero-crossings for ZCR
5. Apply 3 biquad IIR filters in parallel
6. Compute RMS energy in each filtered band
7. Apply exponential smoothing (α=0.15) to all features

#### Performance
- **Computation time**: ~5-10ms per call
- **Publish rate**: ~10 Hz (100ms interval)
- **CPU usage**: <10% on ESP32
- **Memory**: Static filter state, no dynamic allocation

### Smoothing
All features use exponential weighted moving average (EWMA):
```
smoothed = 0.85 * smoothed + 0.15 * new_value
```

This provides temporal smoothing while staying responsive to changes.

### Testing After Deployment

#### 1. Verify Non-Zero Values
```bash
mosquitto_sub -h 192.168.50.69 -p 1884 -t 'party/houseA/+/audio/features' -v
```

**Expected**: All fields (rms, zcr, low, mid, high) should show non-zero values

#### 2. Test with Different Audio Inputs

**Silence/Background**:
- RMS: ~0.0001-0.001
- ZCR: Low (~0.01-0.1)
- All bands: Near zero

**Speech/Voice**:
- RMS: ~0.01-0.1
- ZCR: Medium-High (~0.2-0.5)
- Mid band: Highest
- Low/High: Lower

**Music (Bass-heavy)**:
- RMS: ~0.05-0.3
- ZCR: Medium (~0.1-0.3)
- Low band: Highest
- Mid/High: Varies with content

**Whistle/High-pitch**:
- RMS: Variable
- ZCR: Very High (~0.5-0.8)
- High band: Highest
- Low/Mid: Lower

#### 3. Debug UI Validation
- Open `http://localhost:8000/debug-full`
- Check **Audio Status** table
- All rows (rms, zcr, low, mid, high) should show changing values
- Plot signals: Add `node1/audio.zcr`, `node1/audio.low`, etc.
- Generate different sounds, observe feature responses

### Filter Tuning

If the frequency bands don't seem right, you can tune the coefficients in `i2s_audio.cpp`:

#### To adjust Low band cutoff:
- Current: 300 Hz
- Increase cutoff: Increase b coefficients, decrease a2
- Decrease cutoff: Decrease b coefficients, increase a2

#### To adjust High band cutoff:
- Current: 3000 Hz
- Increase cutoff: Adjust a1 toward -1.5
- Decrease cutoff: Adjust a1 toward -0.5

Proper filter design requires calculating biquad coefficients for desired cutoff frequencies. The current coefficients are approximations optimized for typical party/room audio.

### Known Limitations

1. **Filter approximations**: Coefficients are simplified; not precise Butterworth response
2. **No DC blocking**: May need high-pass filter if mic has DC offset
3. **Fixed cutoffs**: Can't change frequency ranges without recompiling
4. **Single window**: No multi-scale temporal analysis

These limitations are acceptable for MVP mood detection and LED reactivity.

### Future Enhancements

- FFT-based frequency analysis for precise bands
- Adaptive threshold calibration
- Onset detection for beat tracking
- Spectral centroid for timbre analysis
- Multi-scale temporal features (attack, decay)

