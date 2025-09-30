// pir.cpp
#include <Arduino.h>
#include "config.h"

void pir_begin() {
  pinMode(PIR_PIN, INPUT);
}

bool pir_occupied() {
  return digitalRead(PIR_PIN) == HIGH;
}
