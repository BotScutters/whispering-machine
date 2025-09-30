#include <Arduino.h>
#include <ArduinoOTA.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <BH1750.h>
#include <Adafruit_NeoPixel.h>
#include "driver/i2s.h"


// ----- Build-time config via -D flags -----
#ifndef WM_SSID
#define WM_SSID "Nook"
#endif
#ifndef WM_PASS
#define WM_PASS "pup_lick_WiFi!"
#endif
#ifndef WM_BROKER_HOST
#define WM_BROKER_HOST "192.168.50.69"
#endif
#ifndef WM_BROKER_PORT
#define WM_BROKER_PORT 1884
#endif
#ifndef WM_HOUSE_ID
#define WM_HOUSE_ID "houseA"
#endif
#ifndef WM_NODE_ID
#define WM_NODE_ID "testnode"
#endif

#ifndef I2S_BCLK
#define I2S_BCLK 26
#endif
#ifndef I2S_LRCL
#define I2S_LRCL 25
#endif
#ifndef I2S_DOUT
#define I2S_DOUT 22
#endif

#ifndef I2C_SDA
#define I2C_SDA 32
#endif
#ifndef I2C_SCL
#define I2C_SCL 33
#endif

#ifndef PIR_PIN
#define PIR_PIN 27
#endif

#ifndef NEOPIXEL_PIN
#define NEOPIXEL_PIN 5
#endif
#ifndef NEOPIXEL_COUNT
#define NEOPIXEL_COUNT 8
#endif

// ----- Globals -----
WiFiClient espClient;
PubSubClient mqtt(espClient);

BH1750 lightMeter;
Adafruit_NeoPixel ring(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

static float rms_smooth = 0.0f;

String topicBase() { return String("party/") + WM_HOUSE_ID + "/" + WM_NODE_ID; }
String tFeatures() { return topicBase() + "/audio/features"; }
String tLux()      { return topicBase() + "/light/lux"; }
String tPIR()      { return topicBase() + "/occupancy/state"; }
String tRingCmd()  { return topicBase() + "/ring/cmd"; }
String tHeartbeat(){ return topicBase() + "/sys/heartbeat"; }

// ----- I2S (INMP441) -----
static const i2s_port_t I2S_PORT = I2S_NUM_0;
static const int SAMPLE_RATE = 16000;
static const int SAMPLES = 1024;

void i2s_init() {
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 256,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  i2s_pin_config_t pins = {
    .bck_io_num = I2S_BCLK,
    .ws_io_num = I2S_LRCL,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_DOUT
  };
  i2s_driver_install(I2S_PORT, &cfg, 0, NULL);
  i2s_set_pin(I2S_PORT, &pins);
  i2s_set_clk(I2S_PORT, SAMPLE_RATE, I2S_BITS_PER_SAMPLE_32BIT, I2S_CHANNEL_MONO);
}

float compute_rms_from_i2s() {
  int32_t buf[SAMPLES];
  size_t bytes_read = 0;
  if (i2s_read(I2S_PORT, (void *)buf, sizeof(buf), &bytes_read, 10 / portTICK_PERIOD_MS) != ESP_OK) {
    return rms_smooth;
  }
  if (bytes_read == 0) return rms_smooth;
  int n = bytes_read / sizeof(int32_t);
  double sumsq = 0.0;
  for (int i = 0; i < n; i++) {
    int32_t v = (buf[i] >> 8); // 24-bit in 32-bit container
    float f = (float)v / 8388608.0f; // 2^23
    sumsq += (double)f * (double)f;
  }
  float rms = sqrtf((float)(sumsq / n));
  rms_smooth = 0.85f * rms_smooth + 0.15f * rms;
  return rms_smooth;
}

// ----- Utils -----
uint64_t now_ms() { return (uint64_t) millis(); }

void ring_set(bool on, float b) {
  uint8_t level = (uint8_t)(constrain(b, 0.0f, 1.0f) * 255.0f);
  for (int i = 0; i < NEOPIXEL_COUNT; i++) {
    ring.setPixelColor(i, on ? ring.Color(level, level / 2, level /2) : 0);
  }
  ring.show();
}

// ----- WiFi/MQTT -----
void wifi_scan_log() {
  Serial.println("[WiFi] Scanning...");
  int n = WiFi.scanNetworks();
  if (n <= 0) { Serial.println("[WiFi] No networks found"); return; }
  for (int i = 0; i < n; i++) {
    Serial.printf("  %2d) SSID:%s  RSSI:%d  %s  ch:%d\n",
      i, WiFi.SSID(i).c_str(), WiFi.RSSI(i),
      (WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "open" : "enc"),
      WiFi.channel(i));
  }
}

void ensure_wifi() {
  if (WiFi.status() == WL_CONNECTED) return;

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);                // reduce flakiness
  WiFi.setHostname(("wm-" + String(WM_NODE_ID)).c_str());

  static bool scanned = false;
  if (!scanned) { wifi_scan_log(); scanned = true; }

  Serial.printf("[WiFi] Connecting to \"%s\" ...\n", WM_SSID);
  WiFi.begin(WM_SSID, WM_PASS);

  uint32_t start = millis();
  wl_status_t last = WL_IDLE_STATUS;
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    wl_status_t st = WiFi.status();
    if (st != last) {
      last = st;
      Serial.printf("  status=%d\n", st); // prints transitions
    }
    delay(200);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WiFi] Connected, IP=%s RSSI=%d dBm\n",
      WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.printf("[WiFi] FAILED. status=%d (retries next loop)\n", WiFi.status());
  }
}

static void ota_begin() {
  ArduinoOTA.setHostname(("wm-" + String(WM_NODE_ID)).c_str());
  // Optionally set a password:
  // ArduinoOTA.setPassword("strong_password_here");
  ArduinoOTA.onStart([](){ Serial.println("[OTA] Start"); });
  ArduinoOTA.onEnd([](){ Serial.println("[OTA] End"); });
  ArduinoOTA.onError([](ota_error_t e){ Serial.printf("[OTA] Error %u\n", e); });
  ArduinoOTA.begin();
  Serial.println("[OTA] Ready");
}

void mqtt_cb(char* topic, byte* payload, unsigned int len) {
  String s; s.reserve(len);
  for (unsigned int i = 0; i < len; i++) s += (char)payload[i];
  Serial.printf("[MQTT] RX %s %s\n", topic, s.c_str());
  // Expect {"on":true,"b":0.3}
  bool on = true;
  float b = 0.2f;
  if (s.indexOf("\"on\":false") >= 0) on = false;
  int bi = s.indexOf("\"b\":");
  if (bi >= 0) {
    b = s.substring(bi + 4).toFloat();
  }
  ring_set(on, b);
}

void ensure_mqtt() {
  if (mqtt.connected()) return;
  mqtt.setServer(WM_BROKER_HOST, WM_BROKER_PORT);
  mqtt.setCallback(mqtt_cb);
  Serial.printf("[MQTT] Connecting to %s:%d ...\n", WM_BROKER_HOST, WM_BROKER_PORT);
  while (!mqtt.connected()) {
    String cid = String("wm-esps-") + WM_NODE_ID + "-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (mqtt.connect(cid.c_str())) {
      Serial.printf("[MQTT] Connected. Subscribing %s\n", tRingCmd().c_str());
      mqtt.subscribe(tRingCmd().c_str(), 0);
    } else {
      Serial.printf("[MQTT] rc=%d retrying...\n", mqtt.state());
      delay(500);
    }
  }
}

// ----- I2C scan + BH1750 init -----
void i2c_scan() {
  Serial.println("[I2C] Scanning...");
  byte count = 0;
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.printf("[I2C] Found device at 0x%02X\n", address);
      count++;
    }
  }
  if (count == 0) Serial.println("[I2C] No I2C devices found.");
}

bool bh1750_init_with_fallback() {
  // Try 0x23 then 0x5C
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE, 0x23)) {
    Serial.println("[BH1750] Init @0x23 OK");
    return true;
  }
  Serial.println("[BH1750] 0x23 NACK, trying 0x5C...");
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE, 0x5C)) {
    Serial.println("[BH1750] Init @0x5C OK");
    return true;
  }
  Serial.println("[BH1750] Init failed");
  return false;
}

// ----- Setup -----
void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(PIR_PIN, INPUT);

  Wire.begin(I2C_SDA, I2C_SCL);
  i2c_scan();
  bh1750_init_with_fallback();

  ring.begin();
  ring.clear();
  ring.show();
  // Brief blink to prove life
  ring_set(true, 0.02f);
  delay(200);
  ring_set(false, 0.0f);

  i2s_init();

  ensure_wifi();
  ota_begin();
  ensure_mqtt();

  Serial.printf("[BOOT] Topics:\n  %s\n  %s\n  %s\n  %s\n",
    tFeatures().c_str(), tLux().c_str(), tPIR().c_str(), tRingCmd().c_str());
}

// ----- Loop -----
void publish_json(const String& topic, const String& json) {
  mqtt.publish(topic.c_str(), json.c_str(), false);
}

void loop() {
  ensure_wifi();
  ensure_mqtt();
  mqtt.loop();
  ArduinoOTA.handle();

  static uint32_t t_fast = 0, t_slow = 0, t_hb = 0;
  uint32_t t = millis();

  // Heartbeat every 5s (also twinkle ring)
  if (t - t_hb >= 5000) {
    t_hb = t;
    String j = String("{\"ts_ms\":") + String((uint64_t)millis()) + "}";
    publish_json(tHeartbeat(), j);
    // twinkle one pixel to show we're alive
    int ix = (t / 5000) % NEOPIXEL_COUNT;
    ring.clear();
    ring.setPixelColor(ix, ring.Color(120, 20, 20));
    ring.show();
  }

  // Audio features ~10 Hz
  if (t - t_fast >= 100) {
    t_fast = t;
    float rms = compute_rms_from_i2s();
    String j = "{";
    j += "\"rms\":" + String(rms, 5) + ",";
    j += "\"zcr\":0.0,";
    j += "\"low\":0.0,\"mid\":0.0,\"high\":0.0,";
    j += "\"ts_ms\":" + String((uint64_t)millis());
    j += "}";
    publish_json(tFeatures(), j);
  }

  // Lux + PIR every 1s
  if (t - t_slow >= 1000) {
    t_slow = t;
    float lux = lightMeter.readLightLevel();
    String jl = "{";
    jl += "\"lux\":" + String(lux, 1) + ",";
    jl += "\"ts_ms\":" + String((uint64_t)millis());
    jl += "}";
    publish_json(tLux(), jl);

    int motion = digitalRead(PIR_PIN) == HIGH ? 1 : 0;
    String jp = "{";
    jp += "\"occupied\":" + String(motion ? "true" : "false") + ",";
    jp += "\"ts_ms\":" + String((uint64_t)millis());
    jp += "}";
    publish_json(tPIR(), jp);
  }
}
