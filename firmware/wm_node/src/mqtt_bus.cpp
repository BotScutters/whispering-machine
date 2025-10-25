// mqtt_bus.cpp
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"
#include "topics.h"
#include "mqtt_bus.h"

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
  
  // Debug network info
  Serial.printf("[MQTT] WiFi Status: %s\n", WiFi.status() == WL_CONNECTED ? "CONNECTED" : "DISCONNECTED");
  Serial.printf("[MQTT] Local IP: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("[MQTT] Gateway: %s\n", WiFi.gatewayIP().toString().c_str());
  Serial.printf("[MQTT] DNS: %s\n", WiFi.dnsIP().toString().c_str());
  Serial.printf("[MQTT] Connecting to %s:%d ...\n", WM_BROKER_HOST, WM_BROKER_PORT);
  
  while (!s_mqtt.connected()) {
    String cid = String("wm-") + WM_NODE_ID + "-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    Serial.printf("[MQTT] Attempting connection with client ID: %s\n", cid.c_str());
    
    if (s_mqtt.connect(cid.c_str())) {
      Serial.printf("[MQTT] Connected. Subscribing %s\n", t_ring_cmd().c_str());
      s_mqtt.subscribe(t_ring_cmd().c_str(), 0);
    } else {
      int state = s_mqtt.state();
      Serial.printf("[MQTT] Connection failed. State=%d (", state);
      switch(state) {
        case -4: Serial.print("MQTT_CONNECTION_TIMEOUT"); break;
        case -3: Serial.print("MQTT_CONNECTION_LOST"); break;
        case -2: Serial.print("MQTT_CONNECT_FAILED"); break;
        case -1: Serial.print("MQTT_DISCONNECTED"); break;
        case 0: Serial.print("MQTT_CONNECTED"); break;
        case 1: Serial.print("MQTT_CONNECT_BAD_PROTOCOL"); break;
        case 2: Serial.print("MQTT_CONNECT_BAD_CLIENT_ID"); break;
        case 3: Serial.print("MQTT_CONNECT_UNAVAILABLE"); break;
        case 4: Serial.print("MQTT_CONNECT_BAD_CREDENTIALS"); break;
        case 5: Serial.print("MQTT_CONNECT_UNAUTHORIZED"); break;
        default: Serial.print("UNKNOWN"); break;
      }
      Serial.printf(") retrying...\n");
      delay(500);
    }
  }
}

bool mqtt_publish(const char* topic, const char* payload, bool retain) {
  return s_mqtt.publish(topic, payload, retain);
}

void mqtt_loop() { s_mqtt.loop(); }
