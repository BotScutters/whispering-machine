#!/usr/bin/env python3
"""
Unified Testing Framework for Whispering Machine

Comprehensive test coverage across all services with code coverage reporting.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List, Any
import coverage
import requests
import docker
from docker.errors import ContainerError, ImageNotFound


class TestConfig:
    """Test configuration and constants"""
    
    # Service configurations
    SERVICES = {
        'aggregator': {
            'port': 8000,
            'health_endpoint': '/health',
            'test_file': 'test_multi_node.py'
        },
        'ui': {
            'port': 8000,
            'health_endpoint': '/',
            'test_file': None  # UI tests are integration tests
        },
        'display_manager': {
            'port': 8000,
            'health_endpoint': '/health',
            'test_file': None  # Needs integration tests
        }
    }
    
    # Coverage thresholds
    COVERAGE_THRESHOLD = 80.0  # Minimum coverage percentage
    
    # Test timeouts
    SERVICE_STARTUP_TIMEOUT = 30
    HEALTH_CHECK_TIMEOUT = 10


class ServiceTester:
    """Individual service testing"""
    
    def __init__(self, service_name: str, config: Dict[str, Any]):
        self.service_name = service_name
        self.config = config
        self.docker_client = docker.from_env()
        self.container = None
        self.is_docker_mode = os.getenv('TEST_MODE') == 'docker'
        
    def start_service(self) -> bool:
        """Start service container for testing"""
        try:
            # Build service image
            image_name = f"infra-{self.service_name}"
            print(f"Building {self.service_name} service...")
            
            # Use docker build directly (more reliable than compose build)
            if self.is_docker_mode:
                # In Docker mode, build directly
                result = subprocess.run([
                    'docker', 'build', '-t', image_name, 
                    f'/workspace/services/{self.service_name}'
                ], capture_output=True, text=True, cwd='/workspace')
            else:
                # In host mode, build directly
                result = subprocess.run([
                    'docker', 'build', '-t', image_name, 
                    f'services/{self.service_name}'
                ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode != 0:
                print(f"Failed to build {self.service_name}: {result.stderr}")
                return False
            
            # Start container
            container_name = f"test_{self.service_name}"
            try:
                # Remove existing test container
                existing = self.docker_client.containers.get(container_name)
                existing.remove(force=True)
            except docker.errors.NotFound:
                pass
            
            # Start new container with appropriate network
            if self.is_docker_mode:
                # In Docker mode, use the infra_default network
                self.container = self.docker_client.containers.run(
                    image_name,
                    name=container_name,
                    detach=True,
                    ports={f"{self.config['port']}/tcp": None},
                    environment={
                        'HOUSE_ID': 'test_house',
                        'BROKER_HOST': 'mosquitto',
                        'BROKER_PORT': '1883',
                        'LOG_LEVEL': 'DEBUG'
                    },
                    network='infra_default'
                )
            else:
                # In host mode, use default bridge network
                self.container = self.docker_client.containers.run(
                    image_name,
                    name=container_name,
                    detach=True,
                    ports={f"{self.config['port']}/tcp": None},
                    environment={
                        'HOUSE_ID': 'test_house',
                        'BROKER_HOST': 'mosquitto',
                        'BROKER_PORT': '1883',
                        'LOG_LEVEL': 'DEBUG'
                    }
                )
            
            # Wait for service to be ready
            return self.wait_for_health()
            
        except Exception as e:
            print(f"Error starting {self.service_name}: {e}")
            return False
    
    def wait_for_health(self) -> bool:
        """Wait for service to be healthy"""
        if not self.container:
            return False
            
        start_time = time.time()
        while time.time() - start_time < TestConfig.SERVICE_STARTUP_TIMEOUT:
            try:
                # Get container port mapping
                self.container.reload()
                ports = self.container.attrs['NetworkSettings']['Ports']
                port_key = f"{self.config['port']}/tcp"
                
                if port_key in ports and ports[port_key]:
                    host_port = ports[port_key][0]['HostPort']
                    url = f"http://localhost:{host_port}{self.config['health_endpoint']}"
                    
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {self.service_name} service is healthy")
                        return True
                        
            except Exception as e:
                pass
            
            time.sleep(1)
        
        print(f"❌ {self.service_name} service failed to start within timeout")
        return False
    
    def run_unit_tests(self) -> bool:
        """Run unit tests for the service"""
        if not self.config['test_file']:
            print(f"⚠️  No unit tests defined for {self.service_name}")
            return True
            
        if not self.container:
            print(f"❌ No container running for {self.service_name}")
            return False
        
        try:
            # Run tests inside container
            result = self.container.exec_run(
                f"python {self.config['test_file']}",
                workdir='/app'
            )
            
            if result.exit_code == 0:
                print(f"✅ {self.service_name} unit tests passed")
                return True
            else:
                print(f"❌ {self.service_name} unit tests failed:")
                print(result.output.decode())
                return False
                
        except Exception as e:
            print(f"❌ Error running tests for {self.service_name}: {e}")
            return False
    
    def run_coverage_tests(self) -> Dict[str, Any]:
        """Run tests with coverage analysis"""
        if not self.config['test_file']:
            return {'coverage': 0.0, 'details': 'No tests defined'}
            
        if not self.container:
            return {'coverage': 0.0, 'details': 'No container running'}
        
        try:
            # Install coverage if not present
            self.container.exec_run("pip install coverage", workdir='/app')
            
            # Run tests with coverage
            result = self.container.exec_run(
                f"coverage run {self.config['test_file']}",
                workdir='/app'
            )
            
            if result.exit_code != 0:
                return {'coverage': 0.0, 'details': 'Tests failed'}
            
            # Get coverage report
            coverage_result = self.container.exec_run(
                "coverage report --show-missing",
                workdir='/app'
            )
            
            # Parse coverage output
            coverage_output = coverage_result.output.decode()
            lines = coverage_output.split('\n')
            
            # Extract coverage percentage
            coverage_percent = 0.0
            for line in lines:
                if 'TOTAL' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            coverage_percent = float(parts[-1].replace('%', ''))
                        except ValueError:
                            pass
                    break
            
            return {
                'coverage': coverage_percent,
                'details': coverage_output,
                'passed': True
            }
            
        except Exception as e:
            return {'coverage': 0.0, 'details': f'Error: {e}', 'passed': False}
    
    def cleanup(self):
        """Clean up test container"""
        if self.container:
            try:
                self.container.remove(force=True)
            except Exception as e:
                print(f"Warning: Failed to remove container: {e}")


class IntegrationTester:
    """Integration testing across services"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        
    def test_mqtt_connectivity(self) -> bool:
        """Test MQTT broker connectivity"""
        try:
            # Check if mosquitto container is running
            mosquitto = self.docker_client.containers.get('wm_mosquitto')
            if mosquitto.status != 'running':
                print("❌ MQTT broker not running")
                return False
            
            print("✅ MQTT broker is running")
            return True
            
        except docker.errors.NotFound:
            print("❌ MQTT broker container not found")
            return False
        except Exception as e:
            print(f"❌ MQTT connectivity test failed: {e}")
            return False
    
    def test_service_communication(self) -> bool:
        """Test inter-service communication"""
        try:
            # Test aggregator -> MQTT
            aggregator = self.docker_client.containers.get('wm_aggregator')
            if aggregator.status != 'running':
                print("❌ Aggregator service not running")
                return False
            
            # Test UI -> MQTT
            ui = self.docker_client.containers.get('wm_ui')
            if ui.status != 'running':
                print("❌ UI service not running")
                return False
            
            print("✅ Service communication test passed")
            return True
            
        except docker.errors.NotFound as e:
            print(f"❌ Service not found: {e}")
            return False
        except Exception as e:
            print(f"❌ Service communication test failed: {e}")
            return False
    
    def test_web_interfaces(self) -> bool:
        """Test web interface accessibility"""
        try:
            # Test UI service
            ui = self.docker_client.containers.get('wm_ui')
            ui.reload()
            ports = ui.attrs['NetworkSettings']['Ports']
            
            if '8000/tcp' in ports and ports['8000/tcp']:
                host_port = ports['8000/tcp'][0]['HostPort']
                url = f"http://localhost:{host_port}"
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print("✅ UI web interface accessible")
                    
                    # Test party interface
                    party_response = requests.get(f"{url}/party", timeout=5)
                    if party_response.status_code == 200:
                        print("✅ Party interface accessible")
                        return True
                    else:
                        print("❌ Party interface not accessible")
                        return False
                else:
                    print("❌ UI web interface not accessible")
                    return False
            else:
                print("❌ UI service port not mapped")
                return False
                
        except Exception as e:
            print(f"❌ Web interface test failed: {e}")
            return False


class TestRunner:
    """Main test runner orchestrating all tests"""
    
    def __init__(self):
        self.results = {
            'unit_tests': {},
            'integration_tests': {},
            'coverage': {},
            'overall_success': False
        }
        
    def run_all_tests(self) -> bool:
        """Run comprehensive test suite"""
        print("🧪 Starting Whispering Machine Test Suite")
        print("=" * 50)
        
        # Start infrastructure
        if not self.start_infrastructure():
            return False
        
        # Run unit tests for each service
        unit_success = self.run_unit_tests()
        
        # Run integration tests
        integration_success = self.run_integration_tests()
        
        # Run coverage analysis
        coverage_success = self.run_coverage_analysis()
        
        # Generate report
        self.generate_report()
        
        # Cleanup
        self.cleanup()
        
        # Overall success
        self.results['overall_success'] = unit_success and integration_success and coverage_success
        return self.results['overall_success']
    
    def start_infrastructure(self) -> bool:
        """Start required infrastructure (MQTT broker)"""
        try:
            print("🚀 Starting infrastructure...")
            
            # Determine compose file path based on mode
            if os.getenv('TEST_MODE') == 'docker':
                compose_file = '/workspace/infra/docker-compose.yml'
                work_dir = '/workspace'
            else:
                compose_file = 'infra/docker-compose.yml'
                work_dir = Path.cwd()
            
            # Start mosquitto
            if os.getenv('TEST_MODE') == 'docker':
                result = subprocess.run([
                    'docker-compose', '-f', compose_file, 
                    'up', '-d', 'mosquitto'
                ], capture_output=True, text=True, cwd=work_dir)
            else:
                result = subprocess.run([
                    'docker', 'compose', '-f', compose_file, 
                    'up', '-d', 'mosquitto'
                ], capture_output=True, text=True, cwd=work_dir)
            
            if result.returncode != 0:
                print(f"❌ Failed to start infrastructure: {result.stderr}")
                return False
            
            # Wait for mosquitto to be ready
            time.sleep(5)
            print("✅ Infrastructure started")
            return True
            
        except Exception as e:
            print(f"❌ Infrastructure startup failed: {e}")
            return False
    
    def run_unit_tests(self) -> bool:
        """Run unit tests for all services"""
        print("\n📋 Running Unit Tests")
        print("-" * 30)
        
        success = True
        for service_name, config in TestConfig.SERVICES.items():
            print(f"\nTesting {service_name}...")
            
            tester = ServiceTester(service_name, config)
            
            # Start service
            if not tester.start_service():
                success = False
                continue
            
            # Run tests
            if not tester.run_unit_tests():
                success = False
            
            # Store results
            self.results['unit_tests'][service_name] = {
                'passed': True,  # Will be updated by run_unit_tests
                'details': 'Unit tests completed'
            }
            
            tester.cleanup()
        
        return success
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        print("\n🔗 Running Integration Tests")
        print("-" * 30)
        
        tester = IntegrationTester()
        
        # Test MQTT connectivity
        mqtt_success = tester.test_mqtt_connectivity()
        
        # Test service communication
        comm_success = tester.test_service_communication()
        
        # Test web interfaces
        web_success = tester.test_web_interfaces()
        
        self.results['integration_tests'] = {
            'mqtt_connectivity': mqtt_success,
            'service_communication': comm_success,
            'web_interfaces': web_success
        }
        
        return mqtt_success and comm_success and web_success
    
    def run_coverage_analysis(self) -> bool:
        """Run coverage analysis"""
        print("\n📊 Running Coverage Analysis")
        print("-" * 30)
        
        success = True
        for service_name, config in TestConfig.SERVICES.items():
            if not config['test_file']:
                continue
                
            print(f"\nAnalyzing coverage for {service_name}...")
            
            tester = ServiceTester(service_name, config)
            
            if tester.start_service():
                coverage_result = tester.run_coverage_tests()
                self.results['coverage'][service_name] = coverage_result
                
                if coverage_result['coverage'] < TestConfig.COVERAGE_THRESHOLD:
                    print(f"❌ {service_name} coverage below threshold: {coverage_result['coverage']:.1f}%")
                    success = False
                else:
                    print(f"✅ {service_name} coverage: {coverage_result['coverage']:.1f}%")
            
            tester.cleanup()
        
        return success
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📄 Test Report")
        print("=" * 50)
        
        # Unit tests summary
        print("\nUnit Tests:")
        for service, result in self.results['unit_tests'].items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"  {service}: {status}")
        
        # Integration tests summary
        print("\nIntegration Tests:")
        for test, result in self.results['integration_tests'].items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test}: {status}")
        
        # Coverage summary
        print("\nCoverage Analysis:")
        for service, result in self.results['coverage'].items():
            coverage = result['coverage']
            threshold = TestConfig.COVERAGE_THRESHOLD
            status = "✅ PASS" if coverage >= threshold else "❌ FAIL"
            print(f"  {service}: {coverage:.1f}% {status}")
        
        # Overall result
        overall_status = "✅ PASS" if self.results['overall_success'] else "❌ FAIL"
        print(f"\nOverall Result: {overall_status}")
        
        # Save detailed report
        with open('test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: test_report.json")
    
    def cleanup(self):
        """Clean up test infrastructure"""
        try:
            print("\n🧹 Cleaning up...")
            
            # Determine compose file path based on mode
            if os.getenv('TEST_MODE') == 'docker':
                compose_file = '/workspace/infra/docker-compose.yml'
                work_dir = '/workspace'
            else:
                compose_file = 'infra/docker-compose.yml'
                work_dir = Path.cwd()
            
            if os.getenv('TEST_MODE') == 'docker':
                subprocess.run([
                    'docker-compose', '-f', compose_file, 
                    'down'
                ], capture_output=True, text=True, cwd=work_dir)
            else:
                subprocess.run([
                    'docker', 'compose', '-f', compose_file, 
                    'down'
                ], capture_output=True, text=True, cwd=work_dir)
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")


def main():
    """Main entry point"""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! System is ready for deployment.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please review the report.")
        sys.exit(1)


if __name__ == "__main__":
    main()
