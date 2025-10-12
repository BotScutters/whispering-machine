// ring.h
#pragma once
#include <stdint.h>

// LED ring visualization modes
enum RingMode {
  MODE_OFF = 0,
  MODE_IDLE_BREATHING = 1,
  MODE_AUDIO_REACTIVE = 2,
  MODE_RAINBOW = 3,
  MODE_AURORA = 4,
  MODE_OCCUPANCY_PULSE = 5
};

// Ring state for publishing
struct RingState {
  RingMode mode;
  float brightness;        // 0.0-1.0
  float speed;            // Mode-specific parameter
  uint32_t color_primary; // RGB color for some modes
  uint32_t pixels[24];    // Per-pixel RGB colors as 32-bit values (for visualization)
};

// Initialize LED ring
void ring_begin();

// Update ring animation (call from main loop ~20-50 Hz)
void ring_update(float audio_rms, float pir_activity);

// Get current ring state for MQTT publishing
RingState ring_get_state();

// Set ring mode (for encoder button control)
void ring_set_mode(RingMode mode);

// Adjust mode parameter (for encoder rotation)
void ring_adjust_param(int delta);

// Legacy API for MQTT remote control
void ring_set(bool on, float brightness_0_to_1);
