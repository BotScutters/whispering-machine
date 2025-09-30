// mqtt_bus.cpp
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"
#include "topics.h"

static WiFiClient s_wifi;
static PubSubClient s_mqtt(s_wifi);
static MqttHandler s_handler;

static void _cb(char* topic, uint8_t* payload, unsigned int len) {
  if (s_handler) s_handler(topic, (const char*)payload, (size_t)len);
}

void mqtt_begin(MqttHandler on_msg) {
  s_handler = on_msg;
  s_mqtt.setServer(WM_BROKER_HOST, WM_BROKER_PORT);
  s_mqtt.setCallback(_cb);
}

void ensure_mqtt() {
  if (s_mqtt.connected()) return;
  Serial.printf("[MQTT] Connecting to %s:%d ...\n", WM_BROKER_HOST, WM_BROKER_PORT);
  while (!s_mqtt.connected()) {
    String cid = String("wm-") + WM_NODE_ID + "-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (s_mqtt.connect(cid.c_str())) {
      Serial.printf("[MQTT] Connected. Subscribing %s\n", t_ring_cmd().c_str());
      s_mqtt.subscribe(t_ring_cmd().c_str(), 0);
    } else {
      Serial.printf("[MQTT] rc=%d retrying...\n", s_mqtt.state());
      delay(500);
    }
  }
}

bool mqtt_publish(const char* topic, const char* payload, bool retain) {
  return s_mqtt.publish(topic, payload, retain);
}

void mqtt_loop() { s_mqtt.loop(); }
