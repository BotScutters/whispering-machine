// ring.h
#pragma once
void ring_begin();
void ring_set(bool on, float brightness_0_to_1);
void ring_twinkle_pixel(int idx, uint8_t r, uint8_t g, uint8_t b);
