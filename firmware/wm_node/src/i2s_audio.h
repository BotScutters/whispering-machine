// i2s_audio.h
#pragma once

struct AudioFeatures {
  float rms;
  float zcr;
  float low;
  float mid;
  float high;
};

void i2s_audio_begin();
AudioFeatures i2s_audio_features();  // Get all audio features
