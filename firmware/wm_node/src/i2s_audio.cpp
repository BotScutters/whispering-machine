// i2s_audio.cpp
#include <Arduino.h>
#include "driver/i2s.h"
#include "config.h"
#include "i2s_audio.h"

static const i2s_port_t I2S_PORT = I2S_NUM_0;
static const int SAMPLE_RATE = 16000;
static const int SAMPLES = 1024;

// Smoothed feature values
static float g_rms = 0.0f;
static float g_zcr = 0.0f;
static float g_low = 0.0f;
static float g_mid = 0.0f;
static float g_high = 0.0f;

// Simple IIR filter state (biquad for each band)
static float low_y1 = 0, low_y2 = 0, low_x1 = 0, low_x2 = 0;
static float mid_y1 = 0, mid_y2 = 0, mid_x1 = 0, mid_x2 = 0;
static float high_y1 = 0, high_y2 = 0, high_x1 = 0, high_x2 = 0;

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

// Simple biquad IIR filter
static float biquad_filter(float x, float *y1, float *y2, float *x1, float *x2,
                           float b0, float b1, float b2, float a1, float a2) {
  float y = b0*x + b1*(*x1) + b2*(*x2) - a1*(*y1) - a2*(*y2);
  *x2 = *x1; *x1 = x;
  *y2 = *y1; *y1 = y;
  return y;
}

AudioFeatures i2s_audio_features() {
  int32_t buf[SAMPLES];
  size_t bytes_read = 0;
  if (i2s_read(I2S_PORT, (void*)buf, sizeof(buf), &bytes_read, 10 / portTICK_PERIOD_MS) != ESP_OK) {
    return {g_rms, g_zcr, g_low, g_mid, g_high};
  }
  if (bytes_read == 0) return {g_rms, g_zcr, g_low, g_mid, g_high};
  
  int n = bytes_read / sizeof(int32_t);
  
  // Convert samples to float and compute RMS + ZCR
  float samples[SAMPLES];
  double sumsq = 0.0;
  int zero_crossings = 0;
  float prev_sign = 0;
  
  for (int i = 0; i < n; i++) {
    int32_t v = (buf[i] >> 8);            // 24-bit left-justified
    samples[i] = (float)v / 8388608.0f;   // 2^23
    sumsq += (double)samples[i] * (double)samples[i];
    
    // Count zero crossings
    float curr_sign = (samples[i] >= 0) ? 1.0f : -1.0f;
    if (i > 0 && curr_sign != prev_sign) zero_crossings++;
    prev_sign = curr_sign;
  }
  
  // RMS
  float rms = sqrtf((float)(sumsq / n));
  g_rms = 0.85f * g_rms + 0.15f * rms;
  
  // ZCR (normalized by sample count)
  float zcr = (float)zero_crossings / (float)n;
  g_zcr = 0.85f * g_zcr + 0.15f * zcr;
  
  // 3-band frequency analysis using simple IIR filters
  // Coefficients for 16kHz sample rate (approximate)
  // Low: ~300 Hz lowpass
  // Mid: ~300-3000 Hz bandpass
  // High: ~3000 Hz highpass
  
  // Low band (2nd order Butterworth lowpass @ 300Hz)
  float low_b0 = 0.0007f, low_b1 = 0.0013f, low_b2 = 0.0007f;
  float low_a1 = -1.9633f, low_a2 = 0.9660f;
  
  // Mid band (approximation: highpass @ 300Hz then lowpass @ 3000Hz)
  float mid_b0 = 0.05f, mid_b1 = 0.09f, mid_b2 = 0.05f;
  float mid_a1 = -1.5f, mid_a2 = 0.6f;
  
  // High band (2nd order Butterworth highpass @ 3000Hz)
  float high_b0 = 0.6f, high_b1 = -1.2f, high_b2 = 0.6f;
  float high_a1 = -1.0f, high_a2 = 0.3f;
  
  // Apply filters and compute energy in each band
  double low_energy = 0, mid_energy = 0, high_energy = 0;
  
  for (int i = 0; i < n; i++) {
    float low_out = biquad_filter(samples[i], &low_y1, &low_y2, &low_x1, &low_x2,
                                   low_b0, low_b1, low_b2, low_a1, low_a2);
    float mid_out = biquad_filter(samples[i], &mid_y1, &mid_y2, &mid_x1, &mid_x2,
                                   mid_b0, mid_b1, mid_b2, mid_a1, mid_a2);
    float high_out = biquad_filter(samples[i], &high_y1, &high_y2, &high_x1, &high_x2,
                                    high_b0, high_b1, high_b2, high_a1, high_a2);
    
    low_energy += (double)low_out * (double)low_out;
    mid_energy += (double)mid_out * (double)mid_out;
    high_energy += (double)high_out * (double)high_out;
  }
  
  // Normalize by sample count and smooth
  float low = sqrtf((float)(low_energy / n));
  float mid = sqrtf((float)(mid_energy / n));
  float high = sqrtf((float)(high_energy / n));
  
  g_low = 0.85f * g_low + 0.15f * low;
  g_mid = 0.85f * g_mid + 0.15f * mid;
  g_high = 0.85f * g_high + 0.15f * high;
  
  return {g_rms, g_zcr, g_low, g_mid, g_high};
}
