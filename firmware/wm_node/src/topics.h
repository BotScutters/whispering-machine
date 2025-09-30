#pragma once
#include "config.h"

inline String topic_base() {
  return String("party/") + WM_HOUSE_ID + "/" + WM_NODE_ID;
}
inline String t_features()  { return topic_base() + "/audio/features"; }
inline String t_pir()       { return topic_base() + "/occupancy/state"; }
inline String t_ring_cmd()  { return topic_base() + "/ring/cmd"; }
inline String t_hb()        { return topic_base() + "/sys/heartbeat"; }
inline String t_enc()       { return topic_base() + "/input/encoder"; }
inline String t_btn()       { return topic_base() + "/input/button"; }
