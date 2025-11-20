from __future__ import annotations

import asyncio
import json
import os
import threading
import time
from typing import Any

import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

HOUSE_ID = os.getenv("HOUSE_ID", "houseA")
BROKER_HOST = os.getenv("BROKER_HOST", "mosquitto")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))
UI_PORT = int(os.getenv("UI_PORT", "8000"))

TOPIC_BASE = f"party/{HOUSE_ID}"
STATE_TOPIC = f"{TOPIC_BASE}/ui/state"
RAW_TOPIC = f"{TOPIC_BASE}/#"

# Use lifespan context manager for startup/shutdown
from contextlib import asynccontextmanager

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

async def debug_fanout():
    while True:
        debug_data = await _debug_queue.get()
        dead = set()
        for ws in list(_debug_subscribers):
            try:
                await ws.send_json(debug_data)
            except Exception:
                dead.add(ws)
        _debug_subscribers.difference_update(dead)

async def party_fanout():
    while True:
        party_data = await _party_queue.get()
        print(f"[UI] Party fanout sending data to {len(_party_subscribers)} subscribers: {party_data['topic']}")
        print(f"[UI] Party fanout data sample: {str(party_data)[:200]}...")
        dead = set()
        for ws in list(_party_subscribers):
            try:
                await ws.send_json(party_data)
            except Exception as e:
                print(f"[UI] Party fanout error sending to WebSocket: {e}")
                dead.add(ws)
        _party_subscribers.difference_update(dead)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _loop
    _loop = asyncio.get_running_loop()
    print(f"[UI] FastAPI lifespan startup triggered")

    # Start MQTT client in its own thread; pass loop/queue via userdata
    def mqtt_thread():
        print(f"[UI] MQTT thread starting...")
        import uuid
        client_id = f"wm-ui-{uuid.uuid4().hex[:8]}"
        
        global _mqtt_client
        _mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            userdata={
                "loop": _loop, 
                "queue": _queue, 
                "debug_queue": _debug_queue,
                "party_queue": _party_queue,
                "timestamp": lambda: int(time.time() * 1000)
            },
        )
        c = _mqtt_client
        c.on_connect = on_connect
        c.on_message = on_message
        print(f"[UI] Callbacks registered: on_connect={c.on_connect}, on_message={c.on_message}")
        
        print(f"[UI] Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT} with client ID: {client_id}")
        result = c.connect(BROKER_HOST, BROKER_PORT, 60)
        print(f"[UI] MQTT connect result: {result}")
        
        if result == 0:
            print(f"[UI] MQTT connect successful, starting loop...")
            c.loop_forever()
        else:
            print(f"[UI] Failed to connect to MQTT broker")

    import threading

    threading.Thread(target=mqtt_thread, daemon=True).start()
    
    # Start the fanout tasks
    asyncio.create_task(fanout())
    asyncio.create_task(debug_fanout())
    asyncio.create_task(party_fanout())
    
    yield
    
    print(f"[UI] FastAPI lifespan shutdown triggered")

app = FastAPI(lifespan=lifespan)

# Mount static files for JS modules
app.mount("/js", StaticFiles(directory="static/js"), name="js")

ui_state: dict[str, Any] = {
    "noise": {"rms": 0.0},
    "rooms": {},
    "buttons": {},
    "fabrication": {"level": 0.15},
}
_subscribers: set[WebSocket] = set()
_debug_subscribers: set[WebSocket] = set()
_party_subscribers: set[WebSocket] = set()
_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
_debug_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
_party_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
_loop: asyncio.AbstractEventLoop | None = None
_mqtt_client: mqtt.Client | None = None


def on_connect(client, userdata, flags, reason_code, properties=None):
    try:
        print(f"[UI] on_connect called with reason_code: {reason_code}")
        if reason_code == 0:
            print(f"[UI] Connected to MQTT broker successfully")
            print(f"[UI] Subscribing to {STATE_TOPIC}...")
            result1 = client.subscribe(STATE_TOPIC, qos=1)
            print(f"[UI] Subscribe result for {STATE_TOPIC}: {result1}")
            print(f"[UI] Subscribing to {RAW_TOPIC}...")
            result2 = client.subscribe(RAW_TOPIC, qos=1)
            print(f"[UI] Subscribe result for {RAW_TOPIC}: {result2}")
            print(f"[UI] Subscribed to topics: {STATE_TOPIC}, {RAW_TOPIC}")
            
            # Test subscription by publishing a test message
            test_topic = f"{TOPIC_BASE}/test/subscription"
            test_payload = '{"test": "subscription_working"}'
            print(f"[UI] Publishing test message to {test_topic}")
            client.publish(test_topic, test_payload, qos=1)
        else:
            print(f"[UI] Failed to connect to MQTT broker. Reason code: {reason_code}")
    except Exception as e:
        print(f"[UI] Exception in on_connect: {e}")
        import traceback
        traceback.print_exc()


def on_message(client, userdata, msg):
    """Called in Paho's thread → schedule work onto the asyncio loop safely."""
    try:
        print(f"[UI] Received MQTT message: {msg.topic}")
        data = json.loads(msg.payload.decode("utf-8", "ignore"))
    except Exception as e:
        print(f"[UI] Error parsing MQTT message: {e}")
        return
    
    try:
        loop: asyncio.AbstractEventLoop = userdata["loop"]
        queue: asyncio.Queue = userdata["queue"]
        debug_queue: asyncio.Queue = userdata["debug_queue"]
        party_queue: asyncio.Queue = userdata["party_queue"]
        
        # Route messages based on topic
        print(f"[UI] Routing message: {msg.topic}")
        if msg.topic == STATE_TOPIC:
            print(f"[UI] Routing to state queue")
            loop.call_soon_threadsafe(queue.put_nowait, data)
        elif msg.topic.startswith("party/"):
            print(f"[UI] Routing party message: {msg.topic}")
            # All party messages go to both debug and party queues
            debug_data = {
                "topic": msg.topic,
                "payload": data,
                "timestamp": userdata["timestamp"]()
            }
            loop.call_soon_threadsafe(debug_queue.put_nowait, debug_data)
            
            # Also send to party queue for real-time display
            party_data = {
                "topic": msg.topic,
                "payload": data,
                "timestamp": userdata["timestamp"]()
            }
            print(f"[UI] Adding to party queue: {msg.topic}")
            loop.call_soon_threadsafe(party_queue.put_nowait, party_data)
        else:
            print(f"[UI] Routing to debug queue only: {msg.topic}")
            # Raw MQTT message for debugging
            debug_data = {
                "topic": msg.topic,
                "payload": data,
                "timestamp": userdata["timestamp"]()
            }
            loop.call_soon_threadsafe(debug_queue.put_nowait, debug_data)
    except Exception as e:
        print(f"[UI] Exception in on_message routing: {e}")
        import traceback
        traceback.print_exc()


@app.get("/")
def index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/debug")
def debug():
    """Modular debug UI with real-time sensor monitoring and signal plotting."""
    with open("static/debug.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/debug-simple")
def debug_simple():
    """Simple debug UI without Chart.js (fallback for troubleshooting)."""
    with open("static/debug-simple.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/audio-test")
def audio_test():
    """Simple audio recording test page."""
    with open("static/audio-test.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/party")
def party():
    """Touchscreen-optimized party interface with unreliable narrator aesthetic."""
    with open("static/party.html", encoding="utf-8") as f:
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


@app.websocket("/ws/debug")
async def ws_debug_endpoint(ws: WebSocket):
    await ws.accept()
    _debug_subscribers.add(ws)
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        _debug_subscribers.discard(ws)


@app.websocket("/ws/party")
async def ws_party_endpoint(ws: WebSocket):
    print(f"[UI] Party WebSocket connection attempt from {ws.client}")
    await ws.accept()
    print(f"[UI] Party WebSocket connected: {ws.client}")
    _party_subscribers.add(ws)
    
    try:
        while True:
            try:
                # Wait for messages from frontend
                data = await asyncio.wait_for(ws.receive_json(), timeout=1.0)
                
                # Handle incoming messages from frontend
                if 'topic' in data and 'payload' in data:
                    print(f"[UI] Received message from frontend: {data['topic']}")
                    
                    # Publish to MQTT broker
                    if _mqtt_client and _mqtt_client.is_connected():
                        print(f"[UI] Publishing to MQTT: {data['topic']}")
                        _mqtt_client.publish(data['topic'], json.dumps(data['payload']), qos=1)
                        
                        # Add to party queue to broadcast to other subscribers
                        party_data = {
                            "topic": data['topic'],
                            "payload": data['payload'],
                            "timestamp": int(time.time() * 1000)
                        }
                        await _party_queue.put(party_data)
                    else:
                        print(f"[UI] MQTT client not available, skipping publish")
                        
            except asyncio.TimeoutError:
                # No message received, continue
                pass
            except Exception as e:
                print(f"[UI] Error handling WebSocket message: {e}")
                
    finally:
        print(f"[UI] Party WebSocket disconnected: {ws.client}")
        _party_subscribers.discard(ws)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=UI_PORT, reload=False)
