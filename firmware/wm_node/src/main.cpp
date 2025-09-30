#include <Arduino.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>
#include "wm_version.h"

#include "config.h"
#include "topics.h"
#include "wifi_ota.h"
#include "mqtt_bus.h"
#include "ring.h"
#include "i2s_audio.h"
#include "pir.h"
#include "encoder.h"

static void on_mqtt(const char* topic, const char* payload, size_t len) {
  // Only ring/cmd for now: {"on":true,"b":0.3}
  if (strcmp(topic, t_ring_cmd().c_str()) == 0) {
    bool on = true; float b = 0.2f;
    // tiny parse without full JSON dep; but we have ArduinoJson anyway
    StaticJsonDocument<128> j;
    DeserializationError e = deserializeJson(j, payload, len);
    if (!e) {
      if (j.containsKey("on")) on = j["on"];
      if (j.containsKey("b"))  b = j["b"];
    }
    ring_set(on, b);
  }
}

void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.printf("[BOOT] node=%s house=%s sha=%s built=%s\n",
    WM_NODE_ID, WM_HOUSE_ID, WM_GIT_SHA, WM_BUILD_UTC);

  ring_begin();
  ring_set(true, 0.05f); delay(150); ring_set(false, 0);

  pir_begin();
  i2s_audio_begin();
  encoder_begin();

  ensure_wifi();
  ota_begin();
  mqtt_begin(on_mqtt);
  ensure_mqtt();

  Serial.printf("[BOOT] Topics:\n  %s\n  %s\n  %s\n  %s\n  %s\n",
    t_features().c_str(), t_pir().c_str(), t_ring_cmd().c_str(),
    t_enc().c_str(), t_btn().c_str());
}

void loop() {
  ensure_wifi();
  ensure_mqtt();
  mqtt_loop();
  ArduinoOTA.handle();
  encoder_service();

  static uint32_t t_fast=0, t_slow=0, hb_ms=0;
  uint32_t t = millis();

  // Heartbeat every 5s (twinkle)
  if (t - hb_ms >= 5000) {
    hb_ms = t;
    StaticJsonDocument<96> j;
    j["ts_ms"] = t;
    char out[96]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_hb().c_str(), out, false);

    int ix = (t / 5000) % NEOPIXEL_COUNT;
    ring_twinkle_pixel(ix, 120, 20, 20);
  }

  // Audio features @ ~10 Hz
  if (t - t_fast >= 100) {
    t_fast = t;
    float rms = i2s_audio_rms();
    StaticJsonDocument<160> j;
    j["rms"] = rms;
    j["zcr"] = 0.0; j["low"] = 0.0; j["mid"] = 0.0; j["high"] = 0.0;
    j["ts_ms"] = t;
    char out[160]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_features().c_str(), out, false);
  }

  // PIR every 1s
  if (t - t_slow >= 1000) {
    t_slow = t;
    bool occ = pir_occupied();
    StaticJsonDocument<96> j;
    j["occupied"] = occ;
    j["ts_ms"] = t;
    char out[96]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_pir().c_str(), out, false);
  }
}
