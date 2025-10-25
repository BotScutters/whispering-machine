# Whispering Machine - Development Makefile
# Common operations for development and deployment

.PHONY: help build upload monitor clean restart logs status

# Default target
help:
	@echo "Whispering Machine - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  build-node1     Build firmware for Node1"
	@echo "  build-node2     Build firmware for Node2"
	@echo "  build-node3     Build firmware for Node3"
	@echo "  upload-node1    Upload firmware to Node1 via OTA"
	@echo "  upload-node2    Upload firmware to Node2 via OTA"
	@echo "  upload-node3    Upload firmware to Node3 via OTA"
	@echo "  upload-node1-usb Upload firmware to Node1 via USB"
	@echo "  upload-node2-usb Upload firmware to Node2 via USB"
	@echo "  upload-node3-usb Upload firmware to Node3 via USB"
	@echo "  monitor-node1   Monitor Node1 serial output"
	@echo "  monitor-node2   Monitor Node2 serial output"
	@echo "  monitor-node3   Monitor Node3 serial output"
	@echo ""
	@echo "Services:"
	@echo "  start-wsl2      Start WSL2 party mode services"
	@echo "  start-windows   Start Windows party mode services"
	@echo "  restart-ui      Restart UI service only"
	@echo "  restart-mqtt    Restart MQTT broker only"
	@echo "  restart-all     Restart all services"
	@echo "  stop            Stop all services"
	@echo ""
	@echo "Monitoring:"
	@echo "  logs-ui         Show UI service logs"
	@echo "  logs-mqtt       Show MQTT broker logs"
	@echo "  logs-aggregator Show aggregator logs"
	@echo "  logs-all        Show all service logs"
	@echo "  status          Show service status"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           Clean build artifacts"
	@echo "  test-mqtt       Test MQTT message flow"
	@echo "  check-config    Validate configuration files"
	@echo "  check-ota-all   Check OTA availability for all nodes"
	@echo "  check-usb-port  Check USB port availability"

# PlatformIO path
PIO_PATH = ~/.local/bin
export PATH := $(PIO_PATH):$(PATH)

# Build firmware
build-node1: generate-version
	@echo "Building Node1 firmware..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node1-ota

build-node2: generate-version
	@echo "Building Node2 firmware..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node2-ota

build-node3: generate-version
	@echo "Building Node3 firmware..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node3-ota

# Generate version file
generate-version:
	@echo "Generating version file..."
	./scripts/generate_version.sh

# Upload firmware via OTA
upload-node1: build-node1
	@echo "Uploading Node1 firmware via OTA..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node1-ota -t upload

upload-node2: build-node2
	@echo "Uploading Node2 firmware via OTA..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node2-ota -t upload

upload-node3: build-node3
	@echo "Uploading Node3 firmware via OTA..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node3-ota -t upload

# Check USB port availability
check-usb-port:
	@echo "Checking USB port availability..."
	@if [ ! -e /dev/ttyUSB0 ] && [ ! -e /dev/ttyACM0 ]; then \
		echo ""; \
		echo "❌ No USB serial devices found!"; \
		echo ""; \
		echo "🔧 To share USB device with WSL2:"; \
		echo "   1. Open PowerShell as Administrator"; \
		echo "   2. List devices: usbipd wsl list"; \
		echo "   3. Attach device: usbipd attach --wsl --busid <BUSID>"; \
		echo ""; \
		echo "   Example: usbipd attach --wsl --busid 2-3"; \
		echo ""; \
		echo "💡 Note: You may need to re-attach after WSL2 restarts"; \
		echo ""; \
		exit 1; \
	fi
	@echo "✅ USB port detected: $$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)"

# Upload firmware via USB
upload-node1-usb: generate-version check-usb-port
	@echo "Uploading Node1 firmware via USB..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node1-usb -t upload

upload-node2-usb: generate-version check-usb-port
	@echo "Uploading Node2 firmware via USB..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node2-usb -t upload

upload-node3-usb: generate-version check-usb-port
	@echo "Uploading Node3 firmware via USB..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -e node3-usb -t upload

# Monitor serial output
monitor-node1:
	@echo "Monitoring Node1 serial output..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio device monitor -e node1-usb

monitor-node2:
	@echo "Monitoring Node2 serial output..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio device monitor -e node2-usb

monitor-node3:
	@echo "Monitoring Node3 serial output..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio device monitor -e node3-usb

# Service management
start-wsl2:
	@echo "Starting WSL2 party mode..."
	./scripts/start_wsl2_party_mode.sh

start-windows:
	@echo "Starting Windows party mode..."
	./scripts/start_windows_party_mode.bat

restart-ui:
	@echo "Restarting UI service..."
	docker compose -f wsl2/compose.yml restart ui

restart-mqtt:
	@echo "Restarting MQTT broker..."
	docker compose -f wsl2/compose.yml restart mosquitto

restart-all:
	@echo "Restarting all services..."
	docker compose -f wsl2/compose.yml restart

stop:
	@echo "Stopping all services..."
	docker compose -f wsl2/compose.yml down

# Logging
logs-ui:
	docker compose -f wsl2/compose.yml logs -f ui

logs-mqtt:
	docker compose -f wsl2/compose.yml logs -f mosquitto

logs-aggregator:
	docker compose -f wsl2/compose.yml logs -f aggregator

logs-all:
	docker compose -f wsl2/compose.yml logs -f

status:
	@echo "Service Status:"
	docker compose -f wsl2/compose.yml ps

# Utilities
clean:
	@echo "Cleaning build artifacts..."
	cd firmware/wm_node && PATH="$(HOME)/.local/bin:$$PATH" pio run -t clean
	rm -rf firmware/wm_node/.pio

test-mqtt:
	@echo "Testing MQTT message flow..."
	@echo "Publishing test message..."
	docker run --rm --network whispering-machine-wsl2 eclipse-mosquitto:2 mosquitto_pub -h mosquitto -t "party/hidden_house/test" -m "test message"
	@echo "Subscribing to messages..."
	docker run --rm --network whispering-machine-wsl2 eclipse-mosquitto:2 mosquitto_sub -h mosquitto -t "party/hidden_house/+/+/+" -C 5

check-config:
	@echo "Checking configuration files..."
	@echo "WSL2 Environment:"
	@cat wsl2/.env | grep -E "(HOUSE_ID|BROKER_HOST|BROKER_PORT)"
	@echo ""
	@echo "ESP32 Configuration:"
	@cd firmware/wm_node && grep -E "(WM_BROKER_HOST|WM_BROKER_PORT|WM_HOUSE_ID)" config/common.ini

# Quick deployment commands
deploy-node2: build-node2 upload-node2
	@echo "Node2 deployment complete!"

deploy-all: build-node1 build-node2 build-node3 upload-node1 upload-node2 upload-node3
	@echo "All nodes deployment complete!"

# Diagnostic commands
check-ota-node1:
	@echo "Checking Node1 OTA availability..."
	@timeout 3 bash -c 'echo > /dev/tcp/192.168.8.143/3232' && echo "✅ Node1 OTA port open" || echo "❌ Node1 OTA port closed"

check-ota-node2:
	@echo "Checking Node2 OTA availability..."
	@timeout 3 bash -c 'echo > /dev/tcp/192.168.50.243/3232' && echo "✅ Node2 OTA port open" || echo "❌ Node2 OTA port closed"

check-ota-node3:
	@echo "Checking Node3 OTA availability..."
	@timeout 3 bash -c 'echo > /dev/tcp/192.168.50.72/3232' && echo "✅ Node3 OTA port open" || echo "❌ Node3 OTA port closed"

check-ota-all: check-ota-node1 check-ota-node2 check-ota-node3

# Emergency commands
emergency-restart:
	@echo "Emergency restart - stopping and starting all services..."
	docker compose -f wsl2/compose.yml down
	sleep 2
	docker compose -f wsl2/compose.yml up -d
	@echo "Services restarted!"

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	@echo "Installing PlatformIO..."
	python3 -m pip install --user --break-system-packages platformio
	@echo "Development setup complete!"
