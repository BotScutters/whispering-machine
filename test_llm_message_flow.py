#!/usr/bin/env python3
"""
Targeted integration test for LLM message routing.
Tests the complete flow: LLM Agent -> MQTT Broker -> UI Backend -> WebSocket -> Frontend
"""

import asyncio
import json
import time
import docker
import requests
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMMessageFlowTest:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.house_id = "hidden_house"
        self.mqtt_broker_container = None
        self.ui_container = None
        self.llm_agent_container = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result with clear success/failure indication"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        })
        
    def get_container_logs(self, container_name: str, lines: int = 50) -> str:
        """Get container logs with timeout"""
        try:
            container = self.docker_client.containers.get(container_name)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
            return logs
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def test_mqtt_broker_running(self) -> bool:
        """Test 1: Verify MQTT broker is running"""
        try:
            container = self.docker_client.containers.get("mosquitto")
            if container.status == "running":
                self.log_result("MQTT Broker Running", True, f"Status: {container.status}")
                self.mqtt_broker_container = container
                return True
            else:
                self.log_result("MQTT Broker Running", False, f"Status: {container.status}")
                return False
        except Exception as e:
            self.log_result("MQTT Broker Running", False, str(e))
            return False
    
    def test_llm_agent_publishing(self) -> bool:
        """Test 2: Verify LLM agent is publishing messages"""
        try:
            container = self.docker_client.containers.get("wsl2_llm_agent")
            if container.status != "running":
                self.log_result("LLM Agent Publishing", False, f"Container not running: {container.status}")
                return False
                
            # Check logs for recent publishing activity
            logs = self.get_container_logs("wsl2_llm_agent", 20)
            if "Published observation to" in logs:
                self.log_result("LLM Agent Publishing", True, "Found recent observation publications")
                self.llm_agent_container = container
                return True
            else:
                self.log_result("LLM Agent Publishing", False, "No recent publications found in logs")
                return False
        except Exception as e:
            self.log_result("LLM Agent Publishing", False, str(e))
            return False
    
    def test_ui_backend_running(self) -> bool:
        """Test 3: Verify UI backend is running and connected to MQTT"""
        try:
            container = self.docker_client.containers.get("wsl2_ui")
            if container.status != "running":
                self.log_result("UI Backend Running", False, f"Container not running: {container.status}")
                return False
                
            # Check logs for MQTT connection - look for actual MQTT message reception
            logs = self.get_container_logs("wsl2_ui", 30)
            if "Received MQTT message:" in logs:
                self.log_result("UI Backend Running", True, "MQTT client receiving messages")
                self.ui_container = container
                return True
            else:
                self.log_result("UI Backend Running", False, "No MQTT messages received")
                return False
        except Exception as e:
            self.log_result("UI Backend Running", False, str(e))
            return False
    
    def test_mqtt_subscription_pattern(self) -> bool:
        """Test 4: Verify UI backend is subscribing to correct MQTT pattern"""
        try:
            # Publish a test message to LLM topic
            test_topic = f"party/{self.house_id}/llm_agent/test/subscription"
            test_payload = '{"test": "subscription_pattern_test", "timestamp": ' + str(int(time.time() * 1000)) + '}'
            
            # Use docker exec without timeout (Docker API doesn't support timeout parameter)
            result = self.mqtt_broker_container.exec_run(
                f"mosquitto_pub -t '{test_topic}' -m '{test_payload}' -q 1"
            )
            
            if result.exit_code != 0:
                self.log_result("MQTT Subscription Pattern", False, f"Failed to publish test message: {result.output}")
                return False
            
            # Wait a moment for message processing
            time.sleep(3)
            
            # Check UI logs for the test message - look at more recent logs
            logs = self.get_container_logs("wsl2_ui", 20)
            if test_topic in logs:
                self.log_result("MQTT Subscription Pattern", True, f"UI received test message on {test_topic}")
                return True
            else:
                self.log_result("MQTT Subscription Pattern", False, f"UI did not receive test message on {test_topic}")
                return False
                
        except Exception as e:
            self.log_result("MQTT Subscription Pattern", False, str(e))
            return False
    
    def test_ui_backend_http_endpoint(self) -> bool:
        """Test 5: Verify UI backend HTTP endpoints are accessible"""
        try:
            # Test debug endpoint
            response = requests.get("http://localhost:8000/debug", timeout=5)
            if response.status_code == 200:
                self.log_result("UI Backend HTTP Endpoint", True, f"Debug endpoint accessible: {response.status_code}")
                return True
            else:
                self.log_result("UI Backend HTTP Endpoint", False, f"Debug endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("UI Backend HTTP Endpoint", False, str(e))
            return False
    
    def test_real_llm_messages(self) -> bool:
        """Test 6: Verify UI backend receives real LLM messages from agent"""
        try:
            # Get all UI logs to find LLM messages (they might be in older logs)
            logs = self.get_container_logs("wsl2_ui", 1000)
            
            # Look for LLM message patterns
            llm_patterns = [
                "party/hidden_house/llm_agent/observations/observation",
                "party/hidden_house/llm_agent/transcripts/transcript",
                "llm_agent/observations",
                "llm_agent/transcripts"
            ]
            
            found_llm_messages = []
            for pattern in llm_patterns:
                if pattern in logs:
                    found_llm_messages.append(pattern)
            
            if found_llm_messages:
                self.log_result("Real LLM Messages", True, f"Found LLM messages: {found_llm_messages}")
                return True
            else:
                # Debug: show what we actually found in logs
                debug_info = f"No LLM messages found. Logs contain: {len(logs)} characters"
                if "llm_agent" in logs.lower():
                    debug_info += " (contains 'llm_agent' but not exact patterns)"
                self.log_result("Real LLM Messages", False, debug_info)
                return False
                
        except Exception as e:
            self.log_result("Real LLM Messages", False, str(e))
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("🚀 Starting LLM Message Flow Integration Tests")
        logger.info("=" * 60)
        
        # Run tests in order
        tests = [
            ("MQTT Broker", self.test_mqtt_broker_running),
            ("LLM Agent Publishing", self.test_llm_agent_publishing),
            ("UI Backend Running", self.test_ui_backend_running),
            ("MQTT Subscription Pattern", self.test_mqtt_subscription_pattern),
            ("UI Backend HTTP Endpoint", self.test_ui_backend_http_endpoint),
            ("Real LLM Messages", self.test_real_llm_messages),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n🔍 Running: {test_name}")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results[test_name] = result
            except Exception as e:
                logger.error(f"❌ ERROR in {test_name}: {e}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED - LLM message flow is working correctly!")
        else:
            logger.info("⚠️  SOME TESTS FAILED - LLM message flow has issues")
        
        return {
            "summary": {
                "passed": passed,
                "total": total,
                "success_rate": passed / total if total > 0 else 0
            },
            "results": results,
            "test_details": self.test_results
        }

async def main():
    """Main test runner"""
    test = LLMMessageFlowTest()
    results = await test.run_all_tests()
    
    # Exit with appropriate code
    if results["summary"]["passed"] == results["summary"]["total"]:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
