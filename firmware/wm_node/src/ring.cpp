// ring.cpp
#include <Adafruit_NeoPixel.h>
#include "config.h"

static Adafruit_NeoPixel s_ring(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

void ring_begin() {
  s_ring.begin();
  s_ring.clear();
  s_ring.show();
}

void ring_set(bool on, float b) {
  uint8_t level = (uint8_t)(constrain(b, 0.0f, 1.0f) * 255.0f);
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    s_ring.setPixelColor(i, on ? s_ring.Color(level, level/2, level/2) : 0);
  }
  s_ring.show();
}

void ring_twinkle_pixel(int idx, uint8_t r, uint8_t g, uint8_t b) {
  if (idx < 0) idx = 0;
  if (idx >= NEOPIXEL_COUNT) idx = NEOPIXEL_COUNT - 1;
  s_ring.clear();
  s_ring.setPixelColor(idx, s_ring.Color(r, g, b));
  s_ring.show();
}
