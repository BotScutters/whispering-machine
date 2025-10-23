#!/usr/bin/env bash
"""
Docker-based Test Runner for unRAID

All testing runs inside Docker containers since we're on unRAID.
"""

set -e

echo "🧪 Whispering Machine - Docker Test Runner (unRAID)"
echo "=================================================="

# Check if Docker is available
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not available. Please ensure Docker is running."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "test_suite.py" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

echo "🐳 Building test runner container..."

# Create a test runner Dockerfile
cat > Dockerfile.test << 'EOF'
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy test requirements and install
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy test suite
COPY test_suite.py .
COPY pyproject.toml .

# Copy service directories for testing
COPY services/ services/
COPY infra/ infra/

# Set up test environment
ENV PYTHONPATH=/app
ENV TEST_MODE=docker

CMD ["python", "test_suite.py"]
EOF

# Build the test runner image
echo "📦 Building test runner image..."
docker build -f Dockerfile.test -t whispering-machine-test-runner .

# Start infrastructure
echo "🚀 Starting test infrastructure..."
docker compose -f infra/docker-compose.yml up -d mosquitto

# Wait for mosquitto to be ready
echo "⏳ Waiting for MQTT broker..."
sleep 10

# Run the test suite in Docker
echo "🧪 Running test suite in Docker container..."
docker run --rm \
    --network whispering-machine_default \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(pwd):/workspace \
    -w /workspace \
    whispering-machine-test-runner

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! System is ready for deployment."
else
    echo ""
    echo "💥 Some tests failed. Please review the output above."
fi

# Cleanup
echo "🧹 Cleaning up..."
docker compose -f infra/docker-compose.yml down
docker rmi whispering-machine-test-runner 2>/dev/null || true
rm -f Dockerfile.test

echo "✅ Test run completed."
