// wifi_ota.cpp
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoOTA.h>
#include "config.h"

#ifndef WM_SSID
#define WM_SSID "ssid"
#endif
#ifndef WM_PASS
#define WM_PASS "password"
#endif

static bool wifi_scanned = false;

static void wifi_scan_log() {
  Serial.println("[WiFi] Scanning...");
  int n = WiFi.scanNetworks();
  if (n <= 0) { Serial.println("[WiFi] No networks found"); return; }
  for (int i = 0; i < n; i++) {
    Serial.printf("  %2d) %s RSSI:%d ch:%d %s\n", i,
      WiFi.SSID(i).c_str(), WiFi.RSSI(i), WiFi.channel(i),
      WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "open" : "enc");
  }
}

void ensure_wifi() {
  if (WiFi.status() == WL_CONNECTED) return;

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setHostname(wm_hostname().c_str());

  if (!wifi_scanned) { wifi_scan_log(); wifi_scanned = true; }

  Serial.printf("[WiFi] Connecting to \"%s\" ...\n", WM_SSID);
  WiFi.begin(WM_SSID, WM_PASS);

  uint32_t start = millis();
  wl_status_t last = WL_IDLE_STATUS;
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    wl_status_t st = WiFi.status();
    if (st != last) { last = st; Serial.printf("  status=%d\n", st); }
    delay(200);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WiFi] Connected, IP=%s RSSI=%d dBm\n",
      WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.printf("[WiFi] FAILED. status=%d\n", WiFi.status());
  }
}

void ota_begin() {
  ArduinoOTA.setHostname(wm_hostname().c_str());
  ArduinoOTA.onStart([](){ Serial.println("[OTA] Start"); });
  ArduinoOTA.onEnd([](){ Serial.println("[OTA] End"); });
  ArduinoOTA.onError([](ota_error_t e){ Serial.printf("[OTA] Error %u\n", e); });
  ArduinoOTA.begin();
  Serial.println("[OTA] Ready");
}
