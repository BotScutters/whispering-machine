from __future__ import annotations

import json
import os
import time
from typing import Any

import orjson
import paho.mqtt.client as mqtt
from pydantic import BaseModel

HOUSE_ID = os.getenv("HOUSE_ID", "houseA")
BROKER_HOST = os.getenv("BROKER_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))

TOPIC_BASE = f"party/{HOUSE_ID}"
STATE_TOPIC = f"{TOPIC_BASE}/ui/state"


class AudioFeatures(BaseModel):
    rms: float
    zcr: float
    low: float
    mid: float
    high: float
    ts_ms: int


class Occupancy(BaseModel):
    occupied: bool
    ts_ms: int


state: dict[str, Any] = {
    "noise": {"rms": 0.0, "zcr": 0.0, "low": 0.0, "mid": 0.0, "high": 0.0, "ts_ms": 0},
    "rooms": {},
    "buttons": {},
    "fabrication": {"level": 0.15},
}


def on_connect(client, userdata, flags, reason_code, properties=None):
    # v2 signature; subscribe after connect/auto-reconnect
    client.subscribe(f"{TOPIC_BASE}/+/audio/features", qos=0)
    client.subscribe(f"{TOPIC_BASE}/+/occupancy/state", qos=0)
    client.subscribe(f"{TOPIC_BASE}/+/poll/vote", qos=0)


def on_message(client, userdata, msg):
    global state
    try:
        data = json.loads(msg.payload.decode("utf-8", "ignore"))
    except Exception:
        return

    if msg.topic.endswith("/audio/features"):
        try:
            af = AudioFeatures(**data)
            state["noise"]["rms"] = af.rms
            state["noise"]["zcr"] = af.zcr
            state["noise"]["low"] = af.low
            state["noise"]["mid"] = af.mid
            state["noise"]["high"] = af.high
            state["noise"]["ts_ms"] = af.ts_ms
        except Exception:
            pass

    elif msg.topic.endswith("/occupancy/state"):
        try:
            oc = Occupancy(**data)
            node_id = msg.topic.split("/")[2]
            state["rooms"][node_id] = {"occupied": bool(oc.occupied), "ts_ms": oc.ts_ms}
        except Exception:
            pass

    elif msg.topic.endswith("/poll/vote"):
        btn = str(data.get("btn", "unknown"))
        state["buttons"][btn] = state["buttons"].get(btn, 0) + 1


def publish_state_forever(client: mqtt.Client):
    while True:
        client.publish(STATE_TOPIC, orjson.dumps(state), qos=0, retain=True)
        time.sleep(0.2)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="wm-aggregator")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()
    try:
        publish_state_forever(client)
    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
