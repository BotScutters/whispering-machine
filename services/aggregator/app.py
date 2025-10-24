#!/usr/bin/env python3
"""
Enhanced Aggregator with Multi-Node Support

Robust ESP32 multi-node handling for the Whispering Machine.
Handles 3 nodes gracefully with failure detection and recovery.
"""

import json
import os
import time
from typing import Any, Dict, List

import orjson
import paho.mqtt.client as mqtt
from pydantic import BaseModel

from robust_data_processor import DataProcessor, ErrorRecoveryManager

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
    transitions: int = 0
    activity: float = 0.0
    ts_ms: int


class MultiNodeManager:
    """Manages multiple ESP32 nodes with robust error handling"""
    
    def __init__(self, house_id: str = "houseA", max_nodes: int = 3):
        self.house_id = house_id
        self.max_nodes = max_nodes
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.node_timeouts: Dict[str, float] = {}
        self.heartbeat_timeout = 60.0  # 60 seconds
        self.data_timeout = 30.0  # 30 seconds
        
    def register_node(self, node_id: str) -> bool:
        """Register a new node"""
        if len(self.nodes) >= self.max_nodes:
            return False
        
        self.nodes[node_id] = {
            "status": "unknown",
            "last_heartbeat": 0,
            "last_data": 0,
            "data_count": 0,
            "error_count": 0,
            "domains": {}
        }
        self.node_timeouts[node_id] = time.time()
        return True
    
    def update_node_data(self, node_id: str, domain: str, signal: str, data: Dict[str, Any]) -> bool:
        """Update node data with validation"""
        if node_id not in self.nodes:
            return False
        
        try:
            # Validate data structure
            if not self._validate_data(data):
                self.nodes[node_id]["error_count"] += 1
                return False
            
            # Update node data
            if domain not in self.nodes[node_id]["domains"]:
                self.nodes[node_id]["domains"][domain] = {}
            
            self.nodes[node_id]["domains"][domain][signal] = data
            self.nodes[node_id]["last_data"] = time.time()
            self.nodes[node_id]["data_count"] += 1
            self.nodes[node_id]["status"] = "active"
            
            return True
            
        except Exception:
            self.nodes[node_id]["error_count"] += 1
            return False
    
    def update_heartbeat(self, node_id: str) -> bool:
        """Update node heartbeat"""
        if node_id not in self.nodes:
            return False
        
        self.nodes[node_id]["last_heartbeat"] = time.time()
        self.nodes[node_id]["status"] = "active"
        return True
    
    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        """Get comprehensive node status"""
        if node_id not in self.nodes:
            return {"status": "not_found"}
        
        node = self.nodes[node_id]
        current_time = time.time()
        
        # Determine status - prioritize recent data over heartbeat
        if node["error_count"] > 10:
            status = "error"
        elif node["last_data"] == 0 and node["last_heartbeat"] == 0:
            status = "unknown"
        elif node["last_data"] > 0 and current_time - node["last_data"] <= self.data_timeout:
            status = "active"
        elif node["last_heartbeat"] > 0 and current_time - node["last_heartbeat"] <= self.heartbeat_timeout:
            status = "active"
        elif current_time - node["last_heartbeat"] > self.heartbeat_timeout:
            status = "offline"
        elif current_time - node["last_data"] > self.data_timeout:
            status = "stale"
        else:
            status = "unknown"
        
        return {
            "status": status,
            "last_heartbeat": node["last_heartbeat"],
            "last_data": node["last_data"],
            "data_count": node["data_count"],
            "error_count": node["error_count"],
            "domains": list(node["domains"].keys()),
            "uptime": current_time - self.node_timeouts.get(node_id, current_time)
        }
    
    def get_all_nodes_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all nodes"""
        return {node_id: self.get_node_status(node_id) for node_id in self.nodes.keys()}
    
    def get_active_nodes(self) -> List[str]:
        """Get list of active nodes"""
        return [node_id for node_id in self.nodes.keys() 
                if self.get_node_status(node_id)["status"] == "active"]
    
    def cleanup_stale_nodes(self) -> List[str]:
        """Remove nodes that have been offline too long"""
        current_time = time.time()
        stale_nodes = []
        
        for node_id, node in list(self.nodes.items()):
            if current_time - node["last_heartbeat"] > self.heartbeat_timeout * 2:
                stale_nodes.append(node_id)
        
        # Remove stale nodes
        for node_id in stale_nodes:
            del self.nodes[node_id]
            if node_id in self.node_timeouts:
                del self.node_timeouts[node_id]
        
        return stale_nodes
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate incoming data structure"""
        if not isinstance(data, dict):
            return False
        
        # Check for required timestamp
        if "ts_ms" not in data:
            return False
        
        # Validate timestamp
        try:
            ts_ms = int(data["ts_ms"])
            current_ms = int(time.time() * 1000)
            # Timestamp should be within last 5 minutes
            if abs(current_ms - ts_ms) > 300000:
                return False
        except (ValueError, TypeError):
            return False
        
        return True


# Global state with multi-node support
state: Dict[str, Any] = {
    "noise": {"rms": 0.0, "zcr": 0.0, "low": 0.0, "mid": 0.0, "high": 0.0, "ts_ms": 0},
    "rooms": {},
    "buttons": {},
    "fabrication": {"level": 0.15},
    "nodes": {},
    "system_status": "offline"
}

# Multi-node manager
node_manager = MultiNodeManager(HOUSE_ID)

# Robust data processing
data_processor = DataProcessor()
error_recovery_manager = ErrorRecoveryManager()


def on_connect(client, userdata, flags, reason_code, properties=None):
    """MQTT connection callback"""
    if reason_code == 0:
        print(f"Connected to MQTT broker successfully")
        # Subscribe to all sensor topics
        client.subscribe(f"{TOPIC_BASE}/+/audio/features", qos=0)
        client.subscribe(f"{TOPIC_BASE}/+/occupancy/state", qos=0)
        client.subscribe(f"{TOPIC_BASE}/+/poll/vote", qos=0)
        client.subscribe(f"{TOPIC_BASE}/+/sys/heartbeat", qos=0)
        
        print(f"Subscribed to {TOPIC_BASE}/+/...")
    else:
        print(f"Failed to connect to MQTT broker. Reason code: {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties=None):
    """MQTT disconnection callback"""
    print(f"Disconnected from MQTT broker. Reason code: {reason_code}")


def on_log(client, userdata, level, buf):
    """MQTT logging callback"""
    print(f"MQTT Log: {buf}")


def on_message(client, userdata, msg):
    """MQTT message callback with multi-node support"""
    global state
    
    try:
        data = json.loads(msg.payload.decode("utf-8", "ignore"))
    except Exception:
        return
    
    # Extract node info from topic
    topic_parts = msg.topic.split('/')
    if len(topic_parts) < 5:
        return
    
    node_id = topic_parts[2]
    domain = topic_parts[3]
    signal = topic_parts[4]
    
    # Register node if not exists
    if node_id not in node_manager.nodes:
        if not node_manager.register_node(node_id):
            print(f"Failed to register node {node_id} (max nodes reached)")
            return
    
    # Update node data
    if not node_manager.update_node_data(node_id, domain, signal, data):
        print(f"Failed to update data for node {node_id}")
        return
    
    # Process specific message types with robust data processing
    if signal == "features" and domain == "audio":
        result = data_processor.process_audio_features(data, node_id)
        if result.is_valid and result.sanitized_data:
            af = result.sanitized_data
            state["noise"]["rms"] = af["rms"]
            state["noise"]["zcr"] = af["zcr"]
            state["noise"]["low"] = af["low"]
            state["noise"]["mid"] = af["mid"]
            state["noise"]["high"] = af["high"]
            state["noise"]["ts_ms"] = af["ts_ms"]
        elif not result.is_valid:
            # Attempt recovery
            recovered_data = error_recovery_manager.attempt_recovery(node_id, "audio", data)
            if recovered_data:
                af = recovered_data
                state["noise"]["rms"] = af["rms"]
                state["noise"]["zcr"] = af["zcr"]
                state["noise"]["low"] = af["low"]
                state["noise"]["mid"] = af["mid"]
                state["noise"]["high"] = af["high"]
                state["noise"]["ts_ms"] = af["ts_ms"]
    
    elif signal == "state" and domain == "occupancy":
        result = data_processor.process_occupancy(data, node_id)
        if result.is_valid and result.sanitized_data:
            oc = result.sanitized_data
            state["rooms"][node_id] = {
                "occupied": bool(oc["occupied"]),
                "transitions": oc["transitions"],
                "activity": oc["activity"],
                "ts_ms": oc["ts_ms"]
            }
        elif not result.is_valid:
            # Attempt recovery
            recovered_data = error_recovery_manager.attempt_recovery(node_id, "occupancy", data)
            if recovered_data:
                oc = recovered_data
                state["rooms"][node_id] = {
                    "occupied": bool(oc["occupied"]),
                    "transitions": oc["transitions"],
                    "activity": oc["activity"],
                    "ts_ms": oc["ts_ms"]
                }
    
    elif signal == "vote" and domain == "poll":
        btn = str(data.get("btn", "unknown"))
        state["buttons"][btn] = state["buttons"].get(btn, 0) + 1
    
    elif signal == "heartbeat" and domain == "sys":
        node_manager.update_heartbeat(node_id)
    
    # Update system status
    _update_system_status()


def _update_system_status():
    """Update overall system status"""
    global state
    
    active_nodes = node_manager.get_active_nodes()
    total_nodes = len(node_manager.nodes)
    
    if total_nodes == 0:
        state["system_status"] = "offline"
    elif len(active_nodes) == total_nodes and total_nodes > 0:
        state["system_status"] = "healthy"
    elif len(active_nodes) > 0:
        state["system_status"] = "degraded"
    else:
        state["system_status"] = "offline"
    
    # Update node status in state
    state["nodes"] = node_manager.get_all_nodes_status()


def publish_state_forever(client: mqtt.Client):
    """Publish state with multi-node information"""
    while True:
        # Update system status before publishing
        _update_system_status()
        
        # Clean up stale nodes periodically
        stale_nodes = node_manager.cleanup_stale_nodes()
        if stale_nodes:
            print(f"Cleaned up stale nodes: {stale_nodes}")
        
        client.publish(STATE_TOPIC, orjson.dumps(state), qos=0, retain=True)
        time.sleep(0.2)


def main():
    """Main aggregator function"""
    print(f"Starting Whispering Machine Aggregator for {HOUSE_ID}")
    print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
    
    # Generate unique client ID to avoid conflicts
    import uuid
    client_id = f"wm-aggregator-{uuid.uuid4().hex[:8]}"
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    
    try:
        print(f"Attempting to connect to MQTT broker with client ID: {client_id}")
        result = client.connect(BROKER_HOST, BROKER_PORT, 60)
        print(f"Connect result: {result}")
        
        if result == 0:
            print("Starting MQTT loop...")
            client.loop_start()
            
            # Wait a moment for connection to establish
            import time
            time.sleep(2)
            
            if client.is_connected():
                print("MQTT connection established successfully")
                try:
                    publish_state_forever(client)
                except KeyboardInterrupt:
                    print("Shutting down...")
                finally:
                    client.loop_stop()
                    client.disconnect()
            else:
                print("MQTT connection failed - not connected after 2 seconds")
        else:
            print(f"Failed to initiate MQTT connection. Result: {result}")
            
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()