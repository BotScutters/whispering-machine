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
  ring_set_mode(MODE_IDLE_BREATHING); // Start in breathing mode
  ring_set(true, 0.3f); // Set default brightness

  pir_begin();
  i2s_audio_begin();
  encoder_begin();

  ensure_wifi();
  ota_begin();
  mqtt_begin(on_mqtt);
  ensure_mqtt();

  Serial.printf("[BOOT] Topics:\n  %s\n  %s\n  %s\n  %s\n  %s\n  %s\n",
    t_features().c_str(), t_pir().c_str(), t_ring_cmd().c_str(), t_ring_state().c_str(),
    t_enc().c_str(), t_btn().c_str());
}

void loop() {
  ensure_wifi();
  ensure_mqtt();
  mqtt_loop();
  ArduinoOTA.handle();
  encoder_service();

  static uint32_t t_fast=0, t_slow=0, t_ring=0, hb_ms=0;
  static float last_rms = 0.0f, last_activity = 0.0f;
  uint32_t t = millis();

  // Heartbeat every 5s
  if (t - hb_ms >= 5000) {
    hb_ms = t;
    StaticJsonDocument<96> j;
    j["ts_ms"] = get_timestamp_ms();
    char out[96]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_hb().c_str(), out, false);
  }

  // Audio features @ ~10 Hz
  if (t - t_fast >= 100) {
    t_fast = t;
    AudioFeatures af = i2s_audio_features();
    last_rms = af.rms; // Cache for ring update
    
    StaticJsonDocument<160> j;
    j["rms"] = af.rms;
    j["zcr"] = af.zcr;
    j["low"] = af.low;
    j["mid"] = af.mid;
    j["high"] = af.high;
    j["ts_ms"] = get_timestamp_ms();
    char out[160]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_features().c_str(), out, false);
  }

  // PIR every 100ms (10 Hz for smoother activity tracking)
  if (t - t_slow >= 100) {
    t_slow = t;
    PIRStatus pir = pir_status();
    last_activity = pir.activity; // Cache for ring update
    
    StaticJsonDocument<128> j;
    j["occupied"] = pir.occupied;
    j["transitions"] = pir.transitions;
    j["activity"] = pir.activity;
    j["ts_ms"] = get_timestamp_ms();
    char out[128]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_pir().c_str(), out, false);
  }

  // LED ring update @ ~50 Hz + publish state @ 5 Hz
  static uint32_t ring_update_ms = 0;
  if (t - ring_update_ms >= 20) { // 50 Hz update
    ring_update_ms = t;
    ring_update(last_rms, last_activity);
  }

  if (t - t_ring >= 200) { // 5 Hz publish
    t_ring = t;
    RingState rs = ring_get_state();
    
    StaticJsonDocument<512> j; // Sized for 8 LEDs × 32-bit RGB + overhead
    j["mode"] = rs.mode;
    j["brightness"] = rs.brightness;
    j["speed"] = rs.speed;
    j["color"] = rs.color_primary;
    j["pixel_count"] = rs.pixel_count;
    
    // Add per-pixel RGB array for debug visualization
    JsonArray pixels = j.createNestedArray("pixels");
    for (int i = 0; i < rs.pixel_count; i++) {
      pixels.add(rs.pixels[i]);
    }
    
    j["ts_ms"] = get_timestamp_ms();
    char out[512]; size_t n = serializeJson(j, out, sizeof(out));
    mqtt_publish(t_ring_state().c_str(), out, false);
  }
}
