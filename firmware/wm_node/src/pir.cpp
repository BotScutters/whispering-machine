// pir.cpp
#include <Arduino.h>
#include "config.h"
#include "pir.h"

// Track motion history for activity computation
static const int HISTORY_SIZE = 100;  // 100 samples at 10Hz = 10 seconds
static bool motion_history[HISTORY_SIZE] = {false};
static int history_idx = 0;
static int transition_count_1s = 0;
static uint32_t last_transition_time = 0;
static bool last_state = false;

void pir_begin() {
  pinMode(PIR_PIN, INPUT);
  last_state = digitalRead(PIR_PIN) == HIGH;
}

PIRStatus pir_status() {
  uint32_t now = millis();
  bool current = digitalRead(PIR_PIN) == HIGH;
  
  // Track transitions
  if (current != last_state) {
    transition_count_1s++;
    last_transition_time = now;
    last_state = current;
  }
  
  // Reset transition counter after 1 second of no transitions
  if (now - last_transition_time > 1000) {
    transition_count_1s = 0;
  }
  
  // Update circular history buffer
  motion_history[history_idx] = current;
  history_idx = (history_idx + 1) % HISTORY_SIZE;
  
  // Compute activity level: percentage of true values in history
  int active_count = 0;
  for (int i = 0; i < HISTORY_SIZE; i++) {
    if (motion_history[i]) active_count++;
  }
  float activity = (float)active_count / (float)HISTORY_SIZE;
  
  return {current, transition_count_1s, activity};
}
