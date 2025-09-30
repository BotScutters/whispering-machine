// encoder.cpp
#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"
#include "topics.h"
#include "mqtt_bus.h"
#include "ring.h"

static volatile int32_t g_pos = 0;
static volatile int32_t g_delta = 0;
static volatile uint8_t g_prev = 0;

IRAM_ATTR static void enc_isr() {
  uint8_t a = (uint8_t)digitalRead(ENCODER_PIN_A);
  uint8_t b = (uint8_t)digitalRead(ENCODER_PIN_B);
  uint8_t st = (a << 1) | b;
  static const int8_t tbl[16] = {
     0,-1, 1, 0,
     1, 0, 0,-1,
    -1, 0, 0, 1,
     0, 1,-1, 0
  };
  int8_t d = tbl[(g_prev << 2) | st];
  if (d) { g_pos += d; g_delta += d; }
  g_prev = st;
}

static bool btn_last = true;              // using pull-up
static uint32_t btn_last_ms = 0;
static const uint32_t BTN_DEBOUNCE_MS = 25;

void encoder_begin() {
  pinMode(ENCODER_PIN_A, INPUT_PULLUP);
  pinMode(ENCODER_PIN_B, INPUT_PULLUP);
  pinMode(ENCODER_PIN_SW, INPUT_PULLUP);
  g_prev = ((uint8_t)digitalRead(ENCODER_PIN_A) << 1) |
           ((uint8_t)digitalRead(ENCODER_PIN_B));
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A), enc_isr, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B), enc_isr, CHANGE);
}

void encoder_service() {
  static uint32_t last_pub = 0;
  uint32_t now = millis();

  // Coalesce delta ~150ms
  if (now - last_pub >= 150) {
    int32_t d = 0, p = 0;
    noInterrupts(); d = g_delta; g_delta = 0; p = g_pos; interrupts();
    if (d != 0) {
      // local feedback
      if (d > 0) ring_twinkle_pixel(0, 0, 32, 0);
      else       ring_twinkle_pixel(0, 32, 0, 0);

      StaticJsonDocument<128> j;
      j["pos"] = p; j["delta"] = d; j["ts_ms"] = now;
      char out[128]; size_t n = serializeJson(j, out, sizeof(out));
      mqtt_publish(t_enc().c_str(), out, false);
    }
    last_pub = now;
  }

  // Button edges
  bool sw = digitalRead(ENCODER_PIN_SW);
  if (sw != btn_last && (now - btn_last_ms) >= BTN_DEBOUNCE_MS) {
    btn_last = sw; btn_last_ms = now;
    StaticJsonDocument<96> j;
    j["pressed"] = (sw == LOW);
    j["ts_ms"] = now;
    char out[96]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_btn().c_str(), out, false);

    if (sw == LOW) ring_twinkle_pixel(1, 0, 0, 40);
  }
}
