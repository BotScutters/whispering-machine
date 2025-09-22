#!/bin/bash
# Whispering Machine Development Scripts
# Docker-based development for UnRAID environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEV_COMPOSE_FILE="infra/docker-compose.dev.yml"
MAIN_COMPOSE_FILE="infra/docker-compose.yml"
DEV_CONTAINER_NAME="whispering-machine-dev"
FORMATTER_CONTAINER_NAME="whispering-machine-formatter"
MQTT_TESTER_CONTAINER_NAME="whispering-machine-mqtt-tester"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available"
        exit 1
    fi
}

# Get compose command (docker-compose or docker compose)
get_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

# Run command in development container
run_in_dev_container() {
    local cmd="$1"
    local container_name="${2:-$DEV_CONTAINER_NAME}"
    
    log_info "Running in container: $cmd"
    docker exec "$container_name" /bin/bash -c "$cmd"
}

# Ensure dev container is running
ensure_dev_container() {
    local service_name="${1:-dev-tools}"
    local container_name=""
    
    # Map service names to container names
    case "$service_name" in
        "dev-tools")
            container_name="$DEV_CONTAINER_NAME"
            ;;
        "formatter")
            container_name="$FORMATTER_CONTAINER_NAME"
            ;;
        "mqtt-tester")
            container_name="$MQTT_TESTER_CONTAINER_NAME"
            ;;
        *)
            container_name="$service_name"
            ;;
    esac
    
    if ! docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        log_info "Starting development container..."
        COMPOSE_CMD=$(get_compose_cmd)
        if [ "$COMPOSE_CMD" = "docker-compose" ]; then
            docker-compose -f "$DEV_COMPOSE_FILE" up -d "$service_name"
        else
            docker compose -f "$DEV_COMPOSE_FILE" up -d "$service_name"
        fi
        
        # Wait a moment for container to be ready
        sleep 2
    fi
}

# Format Python code using Docker container
fmt() {
    log_info "Formatting Python code using Docker container..."
    check_docker
    ensure_dev_container "formatter"
    
    # Format all Python files using Black
    run_in_dev_container "find /app -name '*.py' -not -path '/app/venv/*' -not -path '/app/.venv/*' -not -path '*/__pycache__/*' -exec black --line-length 88 {} +" "$FORMATTER_CONTAINER_NAME"
    
    # Fix imports with isort
    run_in_dev_container "find /app -name '*.py' -not -path '/app/venv/*' -not -path '/app/.venv/*' -not -path '*/__pycache__/*' -exec isort {} +" "$FORMATTER_CONTAINER_NAME"
    
    # Auto-fix issues with Ruff
    run_in_dev_container "find /app -name '*.py' -not -path '/app/venv/*' -not -path '/app/.venv/*' -not -path '*/__pycache__/*' -exec ruff check --fix {} +" "$FORMATTER_CONTAINER_NAME"
    
    log_success "Code formatting complete"
}

# Lint Python code using Docker container
lint() {
    log_info "Linting Python code using Docker container..."
    check_docker
    ensure_dev_container "dev-tools"
    
    # Run ruff linting on all Python files
    run_in_dev_container "find /app -name '*.py' -not -path '/app/venv/*' -not -path '/app/.venv/*' -not -path '*/__pycache__/*' -exec ruff check {} +" "$DEV_CONTAINER_NAME"
    
    log_success "Linting complete"
}

# Start main development environment
up() {
    log_info "Starting main development environment..."
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    log_info "Using compose command: $COMPOSE_CMD"
    
    if [ "$COMPOSE_CMD" = "docker-compose" ]; then
        docker-compose -f "$MAIN_COMPOSE_FILE" up -d
    else
        docker compose -f "$MAIN_COMPOSE_FILE" up -d
    fi
    
    log_success "Main development environment started"
    log_info "UI available at: http://localhost:8000"
    log_info "MQTT broker available at: localhost:1884"
}

# Stop main development environment
down() {
    log_info "Stopping main development environment..."
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    if [ "$COMPOSE_CMD" = "docker-compose" ]; then
        docker-compose -f "$MAIN_COMPOSE_FILE" down
    else
        docker compose -f "$MAIN_COMPOSE_FILE" down
    fi
    
    log_success "Main development environment stopped"
}

# Show logs from main environment
logs() {
    log_info "Showing main development environment logs..."
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    if [ "$COMPOSE_CMD" = "docker-compose" ]; then
        docker-compose -f "$MAIN_COMPOSE_FILE" logs -f
    else
        docker compose -f "$MAIN_COMPOSE_FILE" logs -f
    fi
}

# Start development tools containers
dev-up() {
    log_info "Starting development tools containers..."
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    if [ "$COMPOSE_CMD" = "docker-compose" ]; then
        docker-compose -f "$DEV_COMPOSE_FILE" up -d
    else
        docker compose -f "$DEV_COMPOSE_FILE" up -d
    fi
    
    log_success "Development tools containers started"
    log_info "Available containers:"
    log_info "  - $DEV_CONTAINER_NAME (general dev tools)"
    log_info "  - $FORMATTER_CONTAINER_NAME (formatting)"
    log_info "  - $MQTT_TESTER_CONTAINER_NAME (MQTT testing)"
}

# Stop development tools containers
dev-down() {
    log_info "Stopping development tools containers..."
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    if [ "$COMPOSE_CMD" = "docker-compose" ]; then
        docker-compose -f "$DEV_COMPOSE_FILE" down
    else
        docker compose -f "$DEV_COMPOSE_FILE" down
    fi
    
    log_success "Development tools containers stopped"
}

# Interactive shell in development container
shell() {
    log_info "Starting interactive shell in development container..."
    check_docker
    ensure_dev_container "dev-tools"
    
    log_info "Entering development container (type 'exit' to leave)..."
    docker exec -it "$DEV_CONTAINER_NAME" /bin/bash
}

# Publish test noise data using Docker container
pub_noise() {
    log_info "Publishing test noise data to MQTT using Docker container..."
    check_docker
    ensure_dev_container "mqtt-tester"
    
    # Get current timestamp
    local timestamp=$(date +%s000)
    
    # Publish test audio features
    run_in_dev_container "mosquitto_pub -h mosquitto -p 1883 -t 'party/house1/kitchen/audio/features' -m '{\"ts_ms\":$timestamp,\"rms\":0.5,\"zcr\":0.3,\"bands\":{\"low\":0.2,\"mid\":0.3,\"high\":0.1}}'" "$MQTT_TESTER_CONTAINER_NAME"
    
    # Publish test occupancy
    run_in_dev_container "mosquitto_pub -h mosquitto -p 1883 -t 'party/house1/kitchen/occupancy/state' -m '{\"ts_ms\":$timestamp,\"occupied\":true}'" "$MQTT_TESTER_CONTAINER_NAME"
    
    log_success "Test data published to MQTT broker"
}

# Subscribe to all MQTT topics using Docker container
sub_all() {
    log_info "Subscribing to all MQTT topics using Docker container..."
    check_docker
    ensure_dev_container "mqtt-tester"
    
    log_info "Starting MQTT subscription (Ctrl+C to stop)..."
    run_in_dev_container "mosquitto_sub -h mosquitto -p 1883 -t 'party/+/+/+/+'" "$MQTT_TESTER_CONTAINER_NAME"
}

# Clean up development environment
clean() {
    log_info "Cleaning up development environment..."
    check_docker
    
    # Stop both main and dev environments
    COMPOSE_CMD=$(get_compose_cmd)
    if [ "$COMPOSE_CMD" = "docker-compose" ]; then
        docker-compose -f "$MAIN_COMPOSE_FILE" down -v
        docker-compose -f "$DEV_COMPOSE_FILE" down
    else
        docker compose -f "$MAIN_COMPOSE_FILE" down -v
        docker compose -f "$DEV_COMPOSE_FILE" down
    fi
    
    # Remove any dangling images/containers
    docker system prune -f
    
    log_success "Cleanup complete"
}

# Show help
help() {
    echo "Whispering Machine Development Scripts (Docker-based)"
    echo ""
    echo "Usage: ./dev.sh <command>"
    echo ""
    echo "Main Environment Commands:"
    echo "  up        Start main development environment (services)"
    echo "  down      Stop main development environment"
    echo "  logs      Show main development environment logs"
    echo ""
    echo "Development Tools Commands:"
    echo "  dev-up    Start development tools containers"
    echo "  dev-down  Stop development tools containers"
    echo "  shell     Interactive shell in development container"
    echo ""
    echo "Code Quality Commands:"
    echo "  fmt       Format Python code using Docker (black + ruff + isort)"
    echo "  lint      Lint Python code using Docker (ruff)"
    echo ""
    echo "MQTT Testing Commands:"
    echo "  pub-noise Publish test noise data to MQTT using Docker"
    echo "  sub-all   Subscribe to all MQTT topics using Docker"
    echo ""
    echo "Utility Commands:"
    echo "  clean     Stop and clean up all environments"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh dev-up      # Start development tools containers"
    echo "  ./dev.sh up          # Start the main development environment"
    echo "  ./dev.sh fmt         # Format all Python code using Docker"
    echo "  ./dev.sh pub-noise   # Send test data to MQTT using Docker"
    echo "  ./dev.sh shell       # Enter interactive development container"
}

# Main command handling
case "${1:-help}" in
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs
        ;;
    dev-up)
        dev-up
        ;;
    dev-down)
        dev-down
        ;;
    shell)
        shell
        ;;
    fmt)
        fmt
        ;;
    lint)
        lint
        ;;
    pub-noise)
        pub_noise
        ;;
    sub-all)
        sub_all
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
