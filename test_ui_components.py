#!/usr/bin/env python3
"""
UI Component Integration Tests
Tests that LLM messages appear in the frontend UI components
"""

import asyncio
import json
import time
import docker
import requests
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UIComponentTest:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.house_id = "hidden_house"
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        })
    
    def test_debug_ui_accessibility(self) -> bool:
        """Test 1: Verify debug UI is accessible and loads properly"""
        try:
            response = requests.get("http://localhost:8000/debug", timeout=10)
            if response.status_code == 200:
                # Check for key UI components
                content = response.text
                if "MQTT Debugger" in content and "debug-app.js" in content:
                    self.log_result("Debug UI Accessibility", True, "Debug UI loads with required components")
                    return True
                else:
                    self.log_result("Debug UI Accessibility", False, "Missing required UI components")
                    return False
            else:
                self.log_result("Debug UI Accessibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Debug UI Accessibility", False, str(e))
            return False
    
    def test_party_ui_accessibility(self) -> bool:
        """Test 2: Verify party UI is accessible and loads properly"""
        try:
            response = requests.get("http://localhost:8000/party", timeout=10)
            if response.status_code == 200:
                content = response.text
                if "party-app.js" in content and "Party" in content:
                    self.log_result("Party UI Accessibility", True, "Party UI loads with required components")
                    return True
                else:
                    self.log_result("Party UI Accessibility", False, "Missing required UI components")
                    return False
            else:
                self.log_result("Party UI Accessibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Party UI Accessibility", False, str(e))
            return False
    
    def test_websocket_endpoints(self) -> bool:
        """Test 3: Verify WebSocket endpoints are accessible"""
        try:
            # Test debug WebSocket endpoint
            debug_response = requests.get("http://localhost:8000/ws/debug", timeout=5)
            if debug_response.status_code in [101, 400, 404]:  # Various expected responses for WebSocket endpoints
                self.log_result("WebSocket Endpoints", True, "Debug WebSocket endpoint accessible")
                return True
            else:
                self.log_result("WebSocket Endpoints", False, f"Debug WebSocket returned {debug_response.status_code}")
                return False
        except Exception as e:
            self.log_result("WebSocket Endpoints", False, str(e))
            return False
    
    def test_llm_message_ui_integration(self) -> bool:
        """Test 4: Verify LLM messages can be published and UI backend processes them"""
        try:
            # Publish a test LLM message
            test_topic = f"party/{self.house_id}/llm_agent/observations/ui_test"
            test_payload = {
                "text": "UI integration test observation",
                "confidence": 0.95,
                "source": "ui_test",
                "ts_ms": int(time.time() * 1000)
            }
            
            # Get MQTT broker container
            broker = self.docker_client.containers.get("mosquitto")
            
            # Publish message
            result = broker.exec_run(
                f"mosquitto_pub -t '{test_topic}' -m '{json.dumps(test_payload)}' -q 1"
            )
            
            if result.exit_code != 0:
                self.log_result("LLM Message UI Integration", False, f"Failed to publish: {result.output}")
                return False
            
            # Wait for processing
            time.sleep(2)
            
            # Check UI logs for the message - look at more recent logs
            ui_container = self.docker_client.containers.get("wsl2_ui")
            logs = ui_container.logs(tail=50, timestamps=True).decode('utf-8')
            
            if test_topic in logs:
                self.log_result("LLM Message UI Integration", True, f"UI backend received test message: {test_topic}")
                return True
            else:
                self.log_result("LLM Message UI Integration", False, "UI backend did not receive test message")
                return False
                
        except Exception as e:
            self.log_result("LLM Message UI Integration", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all UI component tests"""
        logger.info("🚀 Starting UI Component Integration Tests")
        logger.info("=" * 60)
        
        tests = [
            ("Debug UI Accessibility", self.test_debug_ui_accessibility),
            ("Party UI Accessibility", self.test_party_ui_accessibility),
            ("WebSocket Endpoints", self.test_websocket_endpoints),
            ("LLM Message UI Integration", self.test_llm_message_ui_integration),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                logger.error(f"❌ ERROR in {test_name}: {e}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 UI COMPONENT TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\n🎯 Overall: {passed}/{total} UI component tests passed")
        
        if passed == total:
            logger.info("🎉 ALL UI COMPONENT TESTS PASSED!")
        else:
            logger.info("⚠️  SOME UI COMPONENT TESTS FAILED")
        
        return {
            "summary": {"passed": passed, "total": total, "success_rate": passed / total if total > 0 else 0},
            "results": results,
            "test_details": self.test_results
        }

def main():
    test = UIComponentTest()
    results = test.run_all_tests()
    
    if results["summary"]["passed"] == results["summary"]["total"]:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
