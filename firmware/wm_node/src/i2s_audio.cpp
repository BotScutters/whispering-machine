// i2s_audio.cpp
#include <Arduino.h>
#include "driver/i2s.h"
#include "config.h"

static const i2s_port_t I2S_PORT = I2S_NUM_0;
static const int SAMPLE_RATE = 16000;
static const int SAMPLES = 1024;
static float g_rms = 0.0f;

void i2s_audio_begin() {
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

float i2s_audio_rms() {
  int32_t buf[SAMPLES];
  size_t bytes_read = 0;
  if (i2s_read(I2S_PORT, (void*)buf, sizeof(buf), &bytes_read, 10 / portTICK_PERIOD_MS) != ESP_OK)
    return g_rms;
  if (bytes_read == 0) return g_rms;
  int n = bytes_read / sizeof(int32_t);
  double sumsq = 0.0;
  for (int i = 0; i < n; i++) {
    int32_t v = (buf[i] >> 8);            // 24-bit left-justified
    float f = (float)v / 8388608.0f;      // 2^23
    sumsq += (double)f * (double)f;
  }
  float rms = sqrtf((float)(sumsq / n));
  g_rms = 0.85f * g_rms + 0.15f * rms;    // smooth
  return g_rms;
}
