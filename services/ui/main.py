from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

HOUSE_ID = os.getenv("HOUSE_ID", "houseA")
BROKER_HOST = os.getenv("BROKER_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))
UI_PORT = int(os.getenv("UI_PORT", "8000"))

TOPIC_BASE = f"party/{HOUSE_ID}"
STATE_TOPIC = f"{TOPIC_BASE}/ui/state"

app = FastAPI()

ui_state: dict[str, Any] = {
    "noise": {"rms": 0.0},
    "rooms": {},
    "buttons": {},
    "fabrication": {"level": 0.15},
}
_subscribers: set[WebSocket] = set()
_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
_loop: asyncio.AbstractEventLoop | None = None


def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(STATE_TOPIC, qos=0)


def on_message(client, userdata, msg):
    """Called in Paho's thread → schedule work onto the asyncio loop safely."""
    try:
        data = json.loads(msg.payload.decode("utf-8", "ignore"))
    except Exception:
        return
    loop: asyncio.AbstractEventLoop = userdata["loop"]
    queue: asyncio.Queue = userdata["queue"]
    loop.call_soon_threadsafe(queue.put_nowait, data)


@app.on_event("startup")
async def startup():
    global _loop
    _loop = asyncio.get_running_loop()

    # Start MQTT client in its own thread; pass loop/queue via userdata
    def mqtt_thread():
        c = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="wm-ui",
            userdata={"loop": _loop, "queue": _queue},
        )
        c.on_connect = on_connect
        c.on_message = on_message
        c.connect(BROKER_HOST, BROKER_PORT, 60)
        c.loop_forever()

    import threading

    threading.Thread(target=mqtt_thread, daemon=True).start()

    async def fanout():
        global ui_state
        while True:
            ui_state = await _queue.get()
            dead = set()
            for ws in list(_subscribers):
                try:
                    await ws.send_json(ui_state)
                except Exception:
                    dead.add(ws)
            _subscribers.difference_update(dead)

    asyncio.create_task(fanout())


@app.get("/")
def index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    _subscribers.add(ws)
    await ws.send_json(ui_state)
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        _subscribers.discard(ws)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=UI_PORT, reload=False)
