#!/usr/bin/env python3
"""
Simple Multi-Node Test

Quick test to verify the enhanced aggregator works correctly.
"""

import time
import json
from app import MultiNodeManager


def test_multi_node_basic():
    """Test basic multi-node functionality"""
    print("Testing Multi-Node Manager...")
    
    manager = MultiNodeManager("test_house", max_nodes=3)
    
    # Test registration
    assert manager.register_node("node1")
    assert manager.register_node("node2")
    assert manager.register_node("node3")
    assert not manager.register_node("node4")  # Should fail
    
    # Test data update
    valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
    assert manager.update_node_data("node1", "audio", "features", valid_data)
    
    # Test status
    status = manager.get_node_status("node1")
    print(f"Node1 status: {status}")
    assert status["status"] == "active"
    assert status["data_count"] == 1
    
    # Test active nodes
    active_nodes = manager.get_active_nodes()
    assert "node1" in active_nodes
    
    print("✅ Multi-Node Manager tests passed!")


def test_robust_aggregator():
    """Test robust aggregator"""
    print("Testing Robust Aggregator...")
    
    # Test message processing with the global functions
    from app import state, node_manager, _update_system_status
    
    # Clear state first
    state["noise"]["rms"] = 0.0
    state["system_status"] = "offline"
    
    # Simulate processing a message
    topic = "party/test_house/node1/audio/features"
    payload = {"rms": 0.5, "zcr": 0.3, "low": 0.1, "mid": 0.2, "high": 0.3, "ts_ms": int(time.time() * 1000)}
    
    # Register node first
    assert node_manager.register_node("node1")
    
    # Update node data
    assert node_manager.update_node_data("node1", "audio", "features", payload)
    
    # Manually update the state like the on_message function would
    try:
        from app import AudioFeatures
        af = AudioFeatures(**payload)
        state["noise"]["rms"] = af.rms
        state["noise"]["zcr"] = af.zcr
        state["noise"]["low"] = af.low
        state["noise"]["mid"] = af.mid
        state["noise"]["high"] = af.high
        state["noise"]["ts_ms"] = af.ts_ms
    except Exception as e:
        print(f"Error updating state: {e}")
    
    # Update system status
    _update_system_status()
    
    print(f"State noise RMS: {state['noise']['rms']}")
    print(f"System status: {state['system_status']}")
    
    assert state["noise"]["rms"] == 0.5
    assert state["system_status"] == "healthy"
    
    print("✅ Robust Aggregator tests passed!")


def test_node_failure_scenarios():
    """Test node failure scenarios"""
    print("Testing Node Failure Scenarios...")
    
    manager = MultiNodeManager("test_house", max_nodes=3)
    
    # Register nodes
    for i in range(3):
        manager.register_node(f"node{i+1}")
    
    # Give all nodes recent activity
    valid_data = {"rms": 0.5, "ts_ms": int(time.time() * 1000)}
    for i in range(3):
        manager.update_node_data(f"node{i+1}", "audio", "features", valid_data)
    
    # Simulate node2 failure
    old_time = time.time() - 120  # 2 minutes ago
    manager.nodes["node2"]["last_heartbeat"] = old_time
    manager.nodes["node2"]["last_data"] = old_time
    
    # Check status
    status1 = manager.get_node_status("node1")
    status2 = manager.get_node_status("node2")
    status3 = manager.get_node_status("node3")
    
    assert status1["status"] == "active"
    assert status2["status"] == "offline"
    assert status3["status"] == "active"
    
    # Check active nodes
    active_nodes = manager.get_active_nodes()
    assert len(active_nodes) == 2
    assert "node1" in active_nodes
    assert "node2" not in active_nodes
    assert "node3" in active_nodes
    
    print("✅ Node Failure Scenarios tests passed!")


if __name__ == "__main__":
    print("Running Multi-Node Support Tests...")
    print("=" * 50)
    
    try:
        test_multi_node_basic()
        test_robust_aggregator()
        test_node_failure_scenarios()
        
        print("=" * 50)
        print("🎉 All tests passed! Multi-node support is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
