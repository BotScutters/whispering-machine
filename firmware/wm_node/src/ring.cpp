// ring.cpp
#include <Adafruit_NeoPixel.h>
#include "config.h"
#include "ring.h"
#include <Arduino.h>

static Adafruit_NeoPixel s_ring(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// State tracking
static RingMode s_current_mode = MODE_IDLE_BREATHING;
static float s_brightness = 0.3f;
static float s_speed = 1.0f;
static uint32_t s_color_primary = 0xFF4400; // Warm orange default
static uint32_t s_last_update = 0;
static float s_phase = 0.0f; // Animation phase accumulator

void ring_begin() {
  s_ring.begin();
  s_ring.clear();
  s_ring.show();
  s_last_update = millis();
}

// Helper: HSV to RGB conversion (H: 0-360, S: 0-1, V: 0-1)
static uint32_t hsv_to_rgb(float h, float s, float v) {
  float c = v * s;
  float x = c * (1.0f - fabs(fmod(h / 60.0f, 2.0f) - 1.0f));
  float m = v - c;
  
  float r, g, b;
  if (h < 60) { r = c; g = x; b = 0; }
  else if (h < 120) { r = x; g = c; b = 0; }
  else if (h < 180) { r = 0; g = c; b = x; }
  else if (h < 240) { r = 0; g = x; b = c; }
  else if (h < 300) { r = x; g = 0; b = c; }
  else { r = c; g = 0; b = x; }
  
  uint8_t ri = (uint8_t)((r + m) * 255);
  uint8_t gi = (uint8_t)((g + m) * 255);
  uint8_t bi = (uint8_t)((b + m) * 255);
  
  return s_ring.Color(ri, gi, bi);
}

// Mode implementations
static void mode_off() {
  s_ring.clear();
  s_ring.show();
}

static void mode_idle_breathing() {
  // Slow sine wave breathing (red/warm tone)
  float intensity = (sin(s_phase) + 1.0f) / 2.0f; // 0.0 to 1.0
  intensity = intensity * intensity; // Smoother curve
  uint8_t val = (uint8_t)(intensity * s_brightness * 80); // Max 80 for dim breathing
  
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    s_ring.setPixelColor(i, s_ring.Color(val, val/4, val/8)); // Warm red
  }
  s_ring.show();
}

static void mode_audio_reactive(float audio_rms) {
  // React to audio RMS with brightness and color
  // RMS is typically 0.0001-0.01 range, scale up significantly
  float intensity = constrain(audio_rms * 50000.0f, 0.0f, 1.0f); // Aggressive scaling
  
  // Color shifts with intensity: blue (quiet) -> cyan -> green -> yellow -> red (loud)
  uint32_t color;
  float brightness_val = intensity * s_brightness;
  
  if (intensity < 0.2f) {
    color = hsv_to_rgb(240, 1.0, brightness_val); // Blue
  } else if (intensity < 0.4f) {
    color = hsv_to_rgb(180, 1.0, brightness_val); // Cyan
  } else if (intensity < 0.6f) {
    color = hsv_to_rgb(120, 1.0, brightness_val); // Green
  } else if (intensity < 0.8f) {
    color = hsv_to_rgb(60, 1.0, brightness_val);  // Yellow
  } else {
    color = hsv_to_rgb(0, 1.0, brightness_val); // Red
  }
  
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    s_ring.setPixelColor(i, color);
  }
  s_ring.show();
}

static void mode_rainbow() {
  // Rotating rainbow around the ring
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    float hue = fmod(s_phase * 50 + (i * 360.0f / NEOPIXEL_COUNT), 360.0f);
    uint32_t color = hsv_to_rgb(hue, 1.0f, s_brightness);
    s_ring.setPixelColor(i, color);
  }
  s_ring.show();
}

static void mode_aurora() {
  // Flowing aurora borealis effect (green/blue waves)
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    float wave1 = sin(s_phase + i * 0.3f);
    float wave2 = sin(s_phase * 0.7f - i * 0.2f);
    float intensity = (wave1 + wave2 + 2.0f) / 4.0f; // 0.0 to 1.0
    
    // Mix of cyan and green
    float hue = 160 + intensity * 40; // 160-200 range (cyan to green)
    uint32_t color = hsv_to_rgb(hue, 0.8f, intensity * s_brightness);
    s_ring.setPixelColor(i, color);
  }
  s_ring.show();
}

static void mode_occupancy_pulse(float pir_activity) {
  // Pulse based on PIR activity level
  float pulse_intensity = pir_activity * (sin(s_phase * 3) + 1.0f) / 2.0f;
  uint8_t val = (uint8_t)(pulse_intensity * s_brightness * 200);
  
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    s_ring.setPixelColor(i, s_ring.Color(val/2, val, val/3)); // Greenish
  }
  s_ring.show();
}

void ring_update(float audio_rms, float pir_activity) {
  uint32_t now = millis();
  float dt = (now - s_last_update) / 1000.0f; // Delta time in seconds
  s_last_update = now;
  
  // Update animation phase based on speed
  s_phase += dt * s_speed;
  
  // Execute current mode
  switch (s_current_mode) {
    case MODE_OFF: mode_off(); break;
    case MODE_IDLE_BREATHING: mode_idle_breathing(); break;
    case MODE_AUDIO_REACTIVE: mode_audio_reactive(audio_rms); break;
    case MODE_RAINBOW: mode_rainbow(); break;
    case MODE_AURORA: mode_aurora(); break;
    case MODE_OCCUPANCY_PULSE: mode_occupancy_pulse(pir_activity); break;
    default: mode_off(); break;
  }
}

RingState ring_get_state() {
  RingState state;
  state.mode = s_current_mode;
  state.brightness = s_brightness;
  state.speed = s_speed;
  state.color_primary = s_color_primary;
  
  // Capture current pixel states for debug visualization (full RGB)
  for (int i = 0; i < NEOPIXEL_COUNT && i < 24; i++) {
    state.pixels[i] = s_ring.getPixelColor(i);
  }
  
  return state;
}

void ring_set_mode(RingMode mode) {
  s_current_mode = mode;
  s_phase = 0.0f; // Reset animation phase on mode change
}

void ring_adjust_param(int delta) {
  // Adjust speed parameter based on encoder delta
  s_speed += delta * 0.1f;
  s_speed = constrain(s_speed, 0.1f, 5.0f);
}

// Legacy API for MQTT remote control
void ring_set(bool on, float b) {
  if (!on) {
    s_current_mode = MODE_OFF;
  } else {
    s_brightness = constrain(b, 0.0f, 1.0f);
    if (s_current_mode == MODE_OFF) {
      s_current_mode = MODE_IDLE_BREATHING; // Default to breathing when turned on
    }
  }
}
