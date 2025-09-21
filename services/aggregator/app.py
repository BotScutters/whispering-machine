from __future__ import annotations
import json, os, time
from typing import Any, Dict
import orjson
import paho.mqtt.client as mqtt
from pydantic import BaseModel

HOUSE_ID = os.getenv("HOUSE_ID","houseA")
BROKER_HOST = os.getenv("BROKER_HOST","mosquitto")
BROKER_PORT = int(os.getenv("BROKER_PORT","1883"))
TOPIC_BASE = f"party/{HOUSE_ID}"
STATE_TOPIC = f"{TOPIC_BASE}/ui/state"

class AudioFeatures(BaseModel):
    rms: float; zcr: float; low: float; mid: float; high: float; ts_ms: int

class Occupancy(BaseModel):
    occupied: bool; lux: float | None = None; ts_ms: int

state: Dict[str, Any] = {
    "noise": {"rms": 0.0, "ts_ms": 0},
    "rooms": {}, "buttons": {}, "fabrication": {"level": 0.15},
}

def on_connect(c, u, f, rc):
    c.subscribe(f"{TOPIC_BASE}/+/audio/features")
    c.subscribe(f"{TOPIC_BASE}/+/occupancy/state")
    c.subscribe(f"{TOPIC_BASE}/+/poll/vote")

def on_message(c, u, msg):
    global state
    try: data = json.loads(msg.payload.decode("utf-8","ignore"))
    except: return
    if msg.topic.endswith("/audio/features"):
        try:
            af = AudioFeatures(**data); state["noise"] |= {"rms": af.rms, "ts_ms": af.ts_ms}
        except: pass
    elif msg.topic.endswith("/occupancy/state"):
        try:
            oc = Occupancy(**data); node_id = msg.topic.split("/")[2]
            state["rooms"][node_id] = bool(oc.occupied)
        except: pass
    elif msg.topic.endswith("/poll/vote"):
        b = str(data.get("btn","unknown")); state["buttons"][b] = state["buttons"].get(b,0)+1

def publish_state_forever(c: mqtt.Client):
    while True:
        c.publish(STATE_TOPIC, orjson.dumps(state), qos=0, retain=True)
        time.sleep(0.2)

def main():
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="wm-aggregator")
    c.on_connect = on_connect; c.on_message = on_message
    c.connect(BROKER_HOST, BROKER_PORT, 60); c.loop_start()
    try: publish_state_forever(c)
    finally: c.loop_stop()

if __name__ == "__main__": main()
