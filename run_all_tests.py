#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Runs all tests: unit, integration, UI components, and end-to-end
"""

import subprocess
import sys
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSuiteRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def log_result(self, test_suite: str, success: bool, details: str = "", duration: float = 0):
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_suite}: {details} ({duration:.1f}s)")
        self.test_results[test_suite] = {
            "success": success,
            "details": details,
            "duration": duration
        }
    
    def run_test_file(self, test_file: str, test_name: str) -> bool:
        """Run a single test file and return success status"""
        try:
            logger.info(f"\n🔍 Running {test_name}...")
            start_time = time.time()
            
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, timeout=60)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.log_result(test_name, True, "All tests passed", duration)
                return True
            else:
                self.log_result(test_name, False, f"Tests failed: {result.stderr}", duration)
                return False
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_result(test_name, False, "Test timeout (60s)", duration)
            return False
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(test_name, False, str(e), duration)
            return False
    
    def run_unit_tests(self) -> bool:
        """Run unit tests for individual services"""
        logger.info("🧪 Running Unit Tests...")
        
        unit_tests = [
            ("test_suite.py", "Service Unit Tests"),
        ]
        
        all_passed = True
        for test_file, test_name in unit_tests:
            if not self.run_test_file(test_file, test_name):
                all_passed = False
        
        return all_passed
    
    def run_integration_tests(self) -> bool:
        """Run integration tests for service interactions"""
        logger.info("🔗 Running Integration Tests...")
        
        integration_tests = [
            ("test_llm_message_flow.py", "LLM Message Flow Integration"),
        ]
        
        all_passed = True
        for test_file, test_name in integration_tests:
            if not self.run_test_file(test_file, test_name):
                all_passed = False
        
        return all_passed
    
    def run_ui_component_tests(self) -> bool:
        """Run UI component tests"""
        logger.info("🖥️  Running UI Component Tests...")
        
        ui_tests = [
            ("test_ui_components.py", "UI Component Integration"),
        ]
        
        all_passed = True
        for test_file, test_name in ui_tests:
            if not self.run_test_file(test_file, test_name):
                all_passed = False
        
        return all_passed
    
    def run_end_to_end_tests(self) -> bool:
        """Run end-to-end system tests"""
        logger.info("🌐 Running End-to-End Tests...")
        
        # For now, we'll use the LLM message flow as our end-to-end test
        # In the future, this could include full UI interaction tests
        return self.run_test_file("test_llm_message_flow.py", "End-to-End System Test")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        logger.info("=" * 80)
        
        # Run all test categories
        test_categories = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("UI Component Tests", self.run_ui_component_tests),
            ("End-to-End Tests", self.run_end_to_end_tests),
        ]
        
        category_results = {}
        for category_name, test_func in test_categories:
            logger.info(f"\n📋 {category_name}")
            logger.info("-" * 40)
            try:
                result = test_func()
                category_results[category_name] = result
            except Exception as e:
                logger.error(f"❌ ERROR in {category_name}: {e}")
                category_results[category_name] = False
        
        # Overall summary
        total_duration = time.time() - self.start_time
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE TEST SUITE SUMMARY")
        logger.info("=" * 80)
        
        passed_categories = sum(1 for result in category_results.values() if result)
        total_categories = len(category_results)
        
        for category_name, result in category_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {category_name}")
        
        logger.info(f"\n🎯 Overall: {passed_categories}/{total_categories} test categories passed")
        logger.info(f"⏱️  Total Duration: {total_duration:.1f} seconds")
        
        if passed_categories == total_categories:
            logger.info("🎉 ALL TEST CATEGORIES PASSED!")
            logger.info("✅ System is ready for development and deployment")
        else:
            logger.info("⚠️  SOME TEST CATEGORIES FAILED")
            logger.info("🔧 Review failed tests before proceeding")
        
        return {
            "summary": {
                "passed_categories": passed_categories,
                "total_categories": total_categories,
                "success_rate": passed_categories / total_categories if total_categories > 0 else 0,
                "total_duration": total_duration
            },
            "category_results": category_results,
            "test_results": self.test_results
        }

def main():
    runner = TestSuiteRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    if results["summary"]["passed_categories"] == results["summary"]["total_categories"]:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()




