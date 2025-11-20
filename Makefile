# Whispering Machine - Test Suite Makefile
# Provides easy targets for running different test levels

.PHONY: test-all test-unit test-integration test-ui test-e2e test-llm test-clean help

# Default target
help:
	@echo "Whispering Machine Test Suite"
	@echo "=============================="
	@echo ""
	@echo "Available targets:"
	@echo "  test-all        - Run complete test suite (unit + integration + UI + e2e)"
	@echo "  test-unit       - Run unit tests for individual services"
	@echo "  test-integration - Run integration tests for service interactions"
	@echo "  test-ui         - Run UI component tests"
	@echo "  test-e2e        - Run end-to-end system tests"
	@echo "  test-llm        - Run LLM message flow tests specifically"
	@echo "  test-clean      - Clean up test artifacts"
	@echo "  help           - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make test-all           # Run everything"
	@echo "  make test-llm           # Quick LLM flow test"
	@echo "  make test-ui            # Test UI components only"

# Run complete test suite
test-all:
	@echo "🚀 Running Complete Test Suite..."
	python3 run_all_tests.py

# Run unit tests
test-unit:
	@echo "🧪 Running Unit Tests..."
	python3 test_suite.py

# Run integration tests
test-integration:
	@echo "🔗 Running Integration Tests..."
	python3 test_llm_message_flow.py

# Run UI component tests
test-ui:
	@echo "🖥️  Running UI Component Tests..."
	python3 test_ui_components.py

# Run end-to-end tests
test-e2e:
	@echo "🌐 Running End-to-End Tests..."
	python3 test_llm_message_flow.py

# Run LLM message flow tests specifically
test-llm:
	@echo "🤖 Running LLM Message Flow Tests..."
	python3 test_llm_message_flow.py

# Clean up test artifacts
test-clean:
	@echo "🧹 Cleaning up test artifacts..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Quick test for development
test-quick: test-llm
	@echo "⚡ Quick test complete"

# Test with verbose output
test-verbose:
	@echo "🔍 Running tests with verbose output..."
	python3 -u run_all_tests.py