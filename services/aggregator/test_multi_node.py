#!/usr/bin/env python3
"""
Multi-Node Support Implementation

Robust ESP32 multi-node handling with test-driven development.
Simplified, working implementation.
"""

import asyncio
import json
import time
import unittest
from typing import Dict, Any, List, Optional

import paho.mqtt.client as mqtt


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
        
        # Simple status determination
        if node["error_count"] > 10:
            status = "error"
        elif node["last_data"] == 0 and node["last_heartbeat"] == 0:
            status = "unknown"
        elif current_time - node["last_heartbeat"] > self.heartbeat_timeout:
            status = "offline"
        elif current_time - node["last_data"] > self.data_timeout:
            status = "stale"
        else:
            status = "active"
        
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


class TestMultiNodeSupport(unittest.TestCase):
    """Comprehensive tests for multi-node support"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = MultiNodeManager(house_id="test_house", max_nodes=3)
    
    def test_node_registration(self):
        """Test node registration"""
        # Test successful registration
        self.assertTrue(self.manager.register_node("node1"))
        self.assertTrue(self.manager.register_node("node2"))
        self.assertTrue(self.manager.register_node("node3"))
        
        # Test max nodes limit
        self.assertFalse(self.manager.register_node("node4"))
        
        # Test duplicate registration
        self.assertFalse(self.manager.register_node("node1"))
    
    def test_data_validation(self):
        """Test data validation"""
        self.manager.register_node("node1")
        
        # Valid data
        valid_data = {
            "rms": 0.5,
            "zcr": 0.3,
            "ts_ms": int(time.time() * 1000)
        }
        self.assertTrue(self.manager.update_node_data("node1", "audio", "features", valid_data))
        
        # Invalid data - missing timestamp
        invalid_data = {"rms": 0.5, "zcr": 0.3}
        self.assertFalse(self.manager.update_node_data("node1", "audio", "features", invalid_data))
        
        # Invalid data - bad timestamp
        bad_timestamp_data = {"rms": 0.5, "ts_ms": "not_a_number"}
        self.assertFalse(self.manager.update_node_data("node1", "audio", "features", bad_timestamp_data))
    
    def test_node_status_tracking(self):
        """Test node status tracking"""
        self.manager.register_node("node1")
        
        # Initially unknown
        status = self.manager.get_node_status("node1")
        self.assertEqual(status["status"], "unknown")
        
        # Update with data
        valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
        self.manager.update_node_data("node1", "audio", "features", valid_data)
        
        status = self.manager.get_node_status("node1")
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["data_count"], 1)
        self.assertEqual(status["error_count"], 0)
    
    def test_heartbeat_tracking(self):
        """Test heartbeat tracking"""
        self.manager.register_node("node1")
        
        # Update heartbeat
        self.manager.update_heartbeat("node1")
        
        status = self.manager.get_node_status("node1")
        self.assertEqual(status["status"], "active")
        self.assertGreater(status["last_heartbeat"], 0)
    
    def test_node_failure_simulation(self):
        """Test handling of node failures"""
        self.manager.register_node("node1")
        self.manager.register_node("node2")
        
        # Give node2 recent activity
        valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
        self.manager.update_node_data("node2", "audio", "features", valid_data)
        
        # Simulate node1 going offline
        old_time = time.time() - 120  # 2 minutes ago
        self.manager.nodes["node1"]["last_heartbeat"] = old_time
        self.manager.nodes["node1"]["last_data"] = old_time
        
        status = self.manager.get_node_status("node1")
        self.assertEqual(status["status"], "offline")
        
        # Node2 should still be active
        status = self.manager.get_node_status("node2")
        self.assertEqual(status["status"], "active")
    
    def test_error_counting(self):
        """Test error counting and status"""
        self.manager.register_node("node1")
        
        # Send multiple invalid data
        for _ in range(15):
            invalid_data = {"invalid": "data"}
            self.manager.update_node_data("node1", "audio", "features", invalid_data)
        
        status = self.manager.get_node_status("node1")
        self.assertEqual(status["status"], "error")
        self.assertEqual(status["error_count"], 15)
    
    def test_cleanup_stale_nodes(self):
        """Test cleanup of stale nodes"""
        self.manager.register_node("node1")
        self.manager.register_node("node2")
        
        # Give node2 recent activity
        valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
        self.manager.update_node_data("node2", "audio", "features", valid_data)
        
        # Make node1 stale (2.5 minutes ago, which is > 2 * heartbeat_timeout)
        old_time = time.time() - 150  # 2.5 minutes ago
        self.manager.nodes["node1"]["last_heartbeat"] = old_time
        
        # Cleanup should remove node1
        stale_nodes = self.manager.cleanup_stale_nodes()
        self.assertIn("node1", stale_nodes)
        self.assertNotIn("node1", self.manager.nodes)
        self.assertIn("node2", self.manager.nodes)
    
    def test_active_nodes_filtering(self):
        """Test filtering of active nodes"""
        self.manager.register_node("node1")
        self.manager.register_node("node2")
        self.manager.register_node("node3")
        
        # Give all nodes recent activity first
        valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
        self.manager.update_node_data("node1", "audio", "features", valid_data)
        self.manager.update_node_data("node2", "audio", "features", valid_data)
        self.manager.update_node_data("node3", "audio", "features", valid_data)
        
        # Make node2 offline
        old_time = time.time() - 120
        self.manager.nodes["node2"]["last_heartbeat"] = old_time
        
        # Make node3 have errors
        for _ in range(15):
            self.manager.nodes["node3"]["error_count"] += 1
        
        active_nodes = self.manager.get_active_nodes()
        self.assertIn("node1", active_nodes)
        self.assertNotIn("node2", active_nodes)
        self.assertNotIn("node3", active_nodes)
    
    def test_graceful_degradation(self):
        """Test graceful degradation with partial node failures"""
        # Register all nodes
        for i in range(3):
            self.manager.register_node(f"node{i+1}")
        
        # Give all nodes recent activity first
        valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
        for i in range(3):
            self.manager.update_node_data(f"node{i+1}", "audio", "features", valid_data)
        
        # Simulate partial failure
        old_time = time.time() - 120
        self.manager.nodes["node2"]["last_heartbeat"] = old_time
        
        # System should still function with remaining nodes
        all_status = self.manager.get_all_nodes_status()
        self.assertEqual(len(all_status), 3)
        self.assertEqual(all_status["node1"]["status"], "active")
        self.assertEqual(all_status["node2"]["status"], "offline")
        self.assertEqual(all_status["node3"]["status"], "active")
        
        # Active nodes should be 2
        active_nodes = self.manager.get_active_nodes()
        self.assertEqual(len(active_nodes), 2)


class RobustAggregator:
    """Enhanced aggregator with multi-node support"""
    
    def __init__(self, house_id: str = "houseA"):
        self.house_id = house_id
        self.node_manager = MultiNodeManager(house_id)
        self.state = {
            "noise": {"rms": 0.0, "zcr": 0.0, "low": 0.0, "mid": 0.0, "high": 0.0, "ts_ms": 0},
            "rooms": {},
            "buttons": {},
            "fabrication": {"level": 0.15},
            "nodes": {},
            "system_status": "offline"
        }
    
    def process_message(self, topic: str, payload: Dict[str, Any]) -> bool:
        """Process incoming MQTT message with robust error handling"""
        try:
            # Extract node info from topic
            topic_parts = topic.split('/')
            if len(topic_parts) < 5:
                return False
            
            node_id = topic_parts[2]
            domain = topic_parts[3]
            signal = topic_parts[4]
            
            # Register node if not exists
            if node_id not in self.node_manager.nodes:
                if not self.node_manager.register_node(node_id):
                    return False
            
            # Update node data
            if not self.node_manager.update_node_data(node_id, domain, signal, payload):
                return False
            
            # Process specific message types
            if signal == "features" and domain == "audio":
                self._process_audio_features(payload)
            elif signal == "state" and domain == "occupancy":
                self._process_occupancy_state(node_id, payload)
            elif signal == "vote" and domain == "poll":
                self._process_poll_vote(payload)
            elif signal == "heartbeat" and domain == "sys":
                self.node_manager.update_heartbeat(node_id)
            
            # Update system status
            self._update_system_status()
            
            return True
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return False
    
    def _process_audio_features(self, data: Dict[str, Any]):
        """Process audio features with validation"""
        try:
            self.state["noise"]["rms"] = float(data.get("rms", 0.0))
            self.state["noise"]["zcr"] = float(data.get("zcr", 0.0))
            self.state["noise"]["low"] = float(data.get("low", 0.0))
            self.state["noise"]["mid"] = float(data.get("mid", 0.0))
            self.state["noise"]["high"] = float(data.get("high", 0.0))
            self.state["noise"]["ts_ms"] = int(data.get("ts_ms", 0))
        except (ValueError, TypeError):
            pass
    
    def _process_occupancy_state(self, node_id: str, data: Dict[str, Any]):
        """Process occupancy state with validation"""
        try:
            self.state["rooms"][node_id] = {
                "occupied": bool(data.get("occupied", False)),
                "transitions": int(data.get("transitions", 0)),
                "activity": float(data.get("activity", 0.0)),
                "ts_ms": int(data.get("ts_ms", 0))
            }
        except (ValueError, TypeError):
            pass
    
    def _process_poll_vote(self, data: Dict[str, Any]):
        """Process poll vote with validation"""
        try:
            btn = str(data.get("btn", "unknown"))
            self.state["buttons"][btn] = self.state["buttons"].get(btn, 0) + 1
        except (ValueError, TypeError):
            pass
    
    def _update_system_status(self):
        """Update overall system status"""
        active_nodes = self.node_manager.get_active_nodes()
        total_nodes = len(self.node_manager.nodes)
        
        if total_nodes == 0:
            self.state["system_status"] = "offline"
        elif len(active_nodes) == total_nodes and total_nodes > 0:
            self.state["system_status"] = "healthy"
        elif len(active_nodes) > 0:
            self.state["system_status"] = "degraded"
        else:
            self.state["system_status"] = "offline"
        
        # Update node status in state
        self.state["nodes"] = self.node_manager.get_all_nodes_status()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state with node information"""
        return self.state.copy()


class TestRobustAggregator(unittest.TestCase):
    """Test the robust aggregator"""
    
    def setUp(self):
        self.aggregator = RobustAggregator("test_house")
    
    def test_message_processing(self):
        """Test message processing"""
        # Valid audio features
        topic = "party/test_house/node1/audio/features"
        payload = {"rms": 0.5, "zcr": 0.3, "ts_ms": int(time.time() * 1000)}
        
        self.assertTrue(self.aggregator.process_message(topic, payload))
        
        state = self.aggregator.get_state()
        self.assertEqual(state["noise"]["rms"], 0.5)
        self.assertEqual(state["system_status"], "healthy")
    
    def test_invalid_message_handling(self):
        """Test handling of invalid messages"""
        # Invalid topic
        topic = "invalid/topic"
        payload = {"data": "test"}
        
        self.assertFalse(self.aggregator.process_message(topic, payload))
        
        # Invalid payload
        topic = "party/test_house/node1/audio/features"
        payload = {"invalid": "data"}
        
        self.assertFalse(self.aggregator.process_message(topic, payload))
    
    def test_system_status_updates(self):
        """Test system status updates"""
        # Start with no nodes
        state = self.aggregator.get_state()
        self.assertEqual(state["system_status"], "offline")
        
        # Add active node
        topic = "party/test_house/node1/audio/features"
        payload = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
        self.aggregator.process_message(topic, payload)
        
        state = self.aggregator.get_state()
        self.assertEqual(state["system_status"], "healthy")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)