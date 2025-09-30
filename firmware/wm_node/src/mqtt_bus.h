// mqtt_bus.h
#pragma once
#include <functional>

using MqttHandler = std::function<void(const char* topic, const char* payload, size_t len)>;

void mqtt_begin(MqttHandler on_msg);
void ensure_mqtt();
bool mqtt_publish(const char* topic, const char* payload, bool retain=false);
void mqtt_loop();
