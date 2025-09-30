#pragma once
#include <Arduino.h>

// Build-time defs come from PlatformIO build_flags
#ifndef WM_HOUSE_ID
#define WM_HOUSE_ID "houseA"
#endif
#ifndef WM_NODE_ID
#define WM_NODE_ID "node"
#endif
#ifndef WM_BROKER_HOST
#define WM_BROKER_HOST "192.168.50.69"
#endif
#ifndef WM_BROKER_PORT
#define WM_BROKER_PORT 1884
#endif
#ifndef NEOPIXEL_PIN
#define NEOPIXEL_PIN 5
#endif
#ifndef NEOPIXEL_COUNT
#define NEOPIXEL_COUNT 8
#endif
#ifndef PIR_PIN
#define PIR_PIN 27
#endif
#ifndef ENCODER_PIN_A
#define ENCODER_PIN_A 14
#endif
#ifndef ENCODER_PIN_B
#define ENCODER_PIN_B 12
#endif
#ifndef ENCODER_PIN_SW
#define ENCODER_PIN_SW 15
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

inline String wm_hostname() {
  return String("wm-") + WM_NODE_ID;
}
