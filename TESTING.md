# Whispering Machine Test Suite

Comprehensive testing framework for the Whispering Machine project with code coverage analysis and automated CI/CD integration.

## 🧪 Test Framework Overview

The test suite provides:
- **Unit Testing**: Individual service testing with coverage analysis
- **Integration Testing**: Cross-service communication and MQTT connectivity
- **Coverage Analysis**: Code coverage reporting with 80% threshold
- **CI/CD Integration**: GitHub Actions workflow for automated testing
- **Local Development**: Quick test runner for development workflow

## 🚀 Quick Start

### Run All Tests
```bash
# Using the test runner script
./run_tests.sh

# Or using Python directly
python test_suite.py
```

### Run Specific Service Tests
```bash
# Test aggregator service
docker compose -f infra/docker-compose.yml build aggregator
docker run --rm -v $(pwd)/services/aggregator:/app infra-aggregator python test_multi_node.py

# Test with coverage
docker run --rm -v $(pwd)/services/aggregator:/app infra-aggregator coverage run test_multi_node.py && coverage report
```

## 📊 Test Coverage

The test suite enforces an **80% minimum coverage threshold** across all services:

- **Aggregator**: Multi-node support, data validation, error handling
- **UI Service**: WebSocket endpoints, static file serving, party interface
- **Audio Bridge**: Audio capture, Whisper integration, MQTT publishing
- **LLM Agent**: Observation generation, API integration, error handling

### Coverage Reports
- **Terminal**: Real-time coverage display during test runs
- **HTML**: Detailed HTML report in `htmlcov/` directory
- **XML**: CI/CD compatible report in `coverage.xml`

## 🔧 Test Configuration

### Service Test Configuration
Each service is configured in `TestConfig.SERVICES`:

```python
SERVICES = {
    'aggregator': {
        'port': 8000,
        'health_endpoint': '/health',
        'test_file': 'test_multi_node.py'
    },
    'ui': {
        'port': 8000,
        'health_endpoint': '/',
        'test_file': None  # Integration tests only
    },
    # ... other services
}
```

### Coverage Thresholds
- **Minimum Coverage**: 80%
- **Service Startup Timeout**: 30 seconds
- **Health Check Timeout**: 10 seconds

## 🏗️ Test Architecture

### TestRunner Class
Orchestrates the entire test suite:
- Infrastructure startup (MQTT broker)
- Service container management
- Test execution and result collection
- Coverage analysis and reporting
- Cleanup and resource management

### ServiceTester Class
Individual service testing:
- Container lifecycle management
- Health check monitoring
- Unit test execution
- Coverage analysis
- Resource cleanup

### IntegrationTester Class
Cross-service testing:
- MQTT broker connectivity
- Service-to-service communication
- Web interface accessibility
- End-to-end functionality

## 📋 Test Types

### Unit Tests
- **Aggregator**: Multi-node management, data validation, error handling
- **Audio Bridge**: Audio capture, Whisper client, MQTT publishing
- **LLM Agent**: Observation generation, API clients, error recovery

### Integration Tests
- **MQTT Connectivity**: Broker availability and message routing
- **Service Communication**: Inter-service message passing
- **Web Interfaces**: UI accessibility and party interface functionality

### Coverage Analysis
- **Line Coverage**: Percentage of code lines executed
- **Branch Coverage**: Percentage of conditional branches tested
- **Function Coverage**: Percentage of functions called
- **Class Coverage**: Percentage of classes instantiated

## 🔄 CI/CD Integration

### GitHub Actions Workflow
Automated testing on:
- **Push to main/develop**: Full test suite execution
- **Pull Requests**: Test validation with PR comments
- **Daily Schedule**: Continuous integration health checks

### Workflow Features
- **Service Dependencies**: Mosquitto MQTT broker
- **Docker Integration**: Container-based testing
- **Artifact Upload**: Test results and coverage reports
- **PR Comments**: Automated test result summaries

## 🛠️ Development Workflow

### Local Testing
1. **Quick Tests**: `./run_tests.sh` for full suite
2. **Service-Specific**: Individual service testing
3. **Coverage Analysis**: Detailed coverage reports
4. **Debug Mode**: Verbose output for troubleshooting

### Pre-Commit Testing
```bash
# Run tests before committing
./run_tests.sh

# Check coverage threshold
python -c "import json; r=json.load(open('test_report.json')); print('Coverage OK' if all(c['coverage']>=80 for c in r['coverage'].values()) else 'Coverage FAIL')"
```

### Continuous Integration
- **Automated**: GitHub Actions runs on every push/PR
- **Comprehensive**: Full test suite with coverage analysis
- **Reporting**: Detailed test results and coverage metrics
- **Quality Gates**: 80% coverage threshold enforcement

## 📈 Test Metrics

### Success Criteria
- **Unit Tests**: All service unit tests pass
- **Integration Tests**: MQTT connectivity and service communication
- **Coverage**: Minimum 80% code coverage across all services
- **Performance**: Service startup within 30-second timeout

### Failure Handling
- **Graceful Degradation**: Partial test failures don't crash suite
- **Detailed Reporting**: Comprehensive error messages and stack traces
- **Resource Cleanup**: Automatic container and network cleanup
- **Artifact Preservation**: Test results saved for analysis

## 🔍 Troubleshooting

### Common Issues
1. **Docker Not Running**: Ensure Docker daemon is active
2. **Port Conflicts**: Check for port 1883/8000 availability
3. **Service Timeouts**: Increase timeout values for slow systems
4. **Coverage Failures**: Add tests for uncovered code paths

### Debug Mode
```bash
# Enable verbose output
export TEST_DEBUG=1
python test_suite.py

# Run specific service tests
python -m pytest services/aggregator/test_multi_node.py -v
```

### Coverage Debugging
```bash
# Generate detailed coverage report
coverage run test_suite.py
coverage html
open htmlcov/index.html
```

## 📚 Test Documentation

### Adding New Tests
1. **Unit Tests**: Add to service-specific test files
2. **Integration Tests**: Extend `IntegrationTester` class
3. **Coverage**: Ensure new code is covered by tests
4. **Documentation**: Update this README with new test types

### Test Best Practices
- **Isolation**: Tests should not depend on external services
- **Deterministic**: Tests should produce consistent results
- **Fast**: Unit tests should complete quickly
- **Comprehensive**: Cover happy path, edge cases, and error conditions

## 🎯 Quality Assurance

The test suite ensures:
- **Code Quality**: 80% minimum coverage threshold
- **Service Reliability**: Health checks and connectivity tests
- **Integration Stability**: Cross-service communication validation
- **Deployment Readiness**: End-to-end functionality verification

This comprehensive testing framework maintains high code quality and system reliability as the Whispering Machine project scales toward production deployment.
