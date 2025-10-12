// pir.h
#pragma once

struct PIRStatus {
  bool occupied;
  int transitions;     // Number of state changes in last second
  float activity;      // Activity level 0.0-1.0 based on recent motion
};

void pir_begin();
PIRStatus pir_status();  // Get comprehensive PIR status
