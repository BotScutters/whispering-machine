from __future__ import annotations
import asyncio, json, os
from typing import Any, Dict
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

HOUSE_ID = os.getenv("HOUSE_ID","houseA")
BROKER_HOST = os.getenv("BROKER_HOST","mosquitto")
BROKER_PORT = int(os.getenv("BROKER_PORT","1883"))
UI_PORT = int(os.getenv("UI_PORT","8000"))
TOPIC_BASE = f"party/{HOUSE_ID}"
STATE_TOPIC = f"{TOPIC_BASE}/ui/state"

app = FastAPI()
ui_state: Dict[str, Any] = {"noise":{"rms":0.0},"rooms":{},"buttons":{}}
_subs: set[WebSocket] = set()
_queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue()

def on_connect(c,u,f,rc): c.subscribe(STATE_TOPIC)
def on_message(c,u,msg):
    data = json.loads(msg.payload.decode("utf-8","ignore"))
    asyncio.run_coroutine_threadsafe(_queue.put(data), asyncio.get_event_loop())

@app.on_event("startup")
async def startup():
    def mqtt_thread():
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="wm-ui")
        c.on_connect = on_connect; c.on_message = on_message
        c.connect(BROKER_HOST, BROKER_PORT, 60); c.loop_forever()
    import threading; threading.Thread(target=mqtt_thread, daemon=True).start()
    async def fanout():
        global ui_state
        while True:
            ui_state = await _queue.get()
            dead=set()
            for ws in list(_subs):
                try: await ws.send_json(ui_state)
                except: dead.add(ws)
            _subs.difference_update(dead)
    asyncio.create_task(fanout())

@app.get("/")
def index():
    with open("static/index.html","r",encoding="utf-8") as f: return HTMLResponse(f.read())

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept(); _subs.add(ws); await ws.send_json(ui_state)
    try:
        while True: await asyncio.sleep(3600)
    finally: _subs.discard(ws)

if __name__ == "__main__":
    import uvicorn; uvicorn.run("main:app", host="0.0.0.0", port=UI_PORT, reload=False)
