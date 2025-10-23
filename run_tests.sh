#!/usr/bin/env bash
"""
Quick Test Runner for Local Development

Simple script to run tests locally without full CI/CD setup.
"""

set -e

echo "🧪 Whispering Machine - Quick Test Runner"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "test_suite.py" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

# Install test dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing test dependencies..."
source venv/bin/activate
pip install -r requirements-test.txt

# Run the test suite
echo "🚀 Running test suite..."
python test_suite.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! System is ready for deployment."
else
    echo ""
    echo "💥 Some tests failed. Please review the output above."
    exit 1
fi
