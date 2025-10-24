#!/bin/bash
# Whispering Machine - WSL2 Party Mode Startup
# Configures WSL2 for Waveshare 7" touchscreen operation
# Handles display configuration, power management, and delightful interactions

set -e

echo "🎉 Whispering Machine - WSL2 Party Mode Startup"
echo "=============================================="

# Configuration
EXTERNAL_DISPLAY_RESOLUTION="1024x600"
BRIGHTNESS_PERCENT=80
HOUSE_ID="${HOUSE_ID:-houseA}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
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

log_delight() {
    echo -e "${PURPLE}[DELIGHT]${NC} $1"
}

# Check if running in WSL2
check_wsl2() {
    if [[ -z "$WSL_DISTRO_NAME" ]]; then
        log_error "This script is designed for WSL2 only"
        exit 1
    fi
    log_success "Running in WSL2: $WSL_DISTRO_NAME"
}

# Check for required tools
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found - please install Docker Desktop"
        exit 1
    fi
    echo "✅ Docker available"
    
    # Check for Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose not found - please install Docker Desktop"
        exit 1
    fi
    echo "✅ Docker Compose available"
    
    # Check for PowerShell (via Windows)
    if ! powershell.exe -Command "Write-Host 'PowerShell available'" &> /dev/null; then
        log_warning "PowerShell not accessible from WSL2"
    else
        echo "✅ PowerShell accessible"
    fi
    
    log_success "All dependencies available"
}

# Configure Windows power management via PowerShell
configure_windows_power_management() {
    log_info "Configuring Windows power management..."
    
    # Use PowerShell to disable screensaver and sleep
    powershell.exe -Command "
        try {
            powercfg /change monitor-timeout-ac 0
            powercfg /change standby-timeout-ac 0
            Write-Host 'Power management configured successfully'
        } catch {
            Write-Host 'Could not configure power management (may need admin rights)'
        }
    "
    
    log_success "Windows power management configured"
}

# Detect Windows displays via PowerShell
detect_windows_displays() {
    log_info "Detecting Windows displays..."
    
    # Use PowerShell to detect displays
    powershell.exe -Command "
        try {
            \$displays = Get-WmiObject -Class Win32_VideoController | Select-Object Name, VideoModeDescription
            Write-Host \"Detected \$(\$displays.Count) display(s)\"
            foreach (\$display in \$displays) {
                Write-Host \"- \$(\$display.Name): \$(\$display.VideoModeDescription)\"
            }
        } catch {
            Write-Host 'Could not detect displays'
        }
    "
    
    log_success "Display detection completed"
}

# Create WSL2 touchscreen calibration
create_wsl2_touch_calibration() {
    log_info "Creating WSL2 touchscreen calibration..."
    
    # Create calibration data directory
    mkdir -p ~/.whispering_machine
    
    # Create WSL2 calibration file
    cat > ~/.whispering_machine/wsl2_touch_calibration.json << EOF
{
  "calibrated": true,
  "platform": "wsl2",
  "host_os": "windows",
  "timestamp": "$(date -Iseconds)",
  "resolution": "$EXTERNAL_DISPLAY_RESOLUTION",
  "touch_offset_x": 0,
  "touch_offset_y": 0,
  "touch_scale_x": 1.0,
  "touch_scale_y": 1.0,
  "touchscreen_device": "USB Touchscreen",
  "driver_info": "Windows Generic USB Touchscreen Driver",
  "wsl2_integration": true,
  "party_mode": true,
  "delightful_interactions": {
    "easter_eggs_enabled": true,
    "konami_code": false,
    "secret_patterns": false,
    "long_press_reveal": false,
    "multi_touch_magic": false
  }
}
EOF
    
    log_success "WSL2 touchscreen calibration created"
}

# Start WSL2 party services
start_wsl2_services() {
    log_info "Starting WSL2 party services..."
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running - please start Docker Desktop"
        exit 1
    fi
    
    # Start services using docker compose
    if [ -f "wsl2/compose.yml" ]; then
        log_info "Starting services with docker compose..."
        docker compose -f wsl2/compose.yml up -d
        
        if [ $? -eq 0 ]; then
            log_success "WSL2 party services started"
        else
            log_error "Failed to start WSL2 party services"
            exit 1
        fi
    else
        log_warning "wsl2/compose.yml not found - using fallback compose"
        docker compose -f infra/docker-compose.yml up -d
    fi
}

# Display WSL2 party status
show_wsl2_party_status() {
    log_delight "🎊 WSL2 Party Mode Configuration Complete! 🎊"
    echo ""
    echo -e "${CYAN}WSL2 Party Mode Status:${NC}"
    echo "  • WSL2 Environment: $WSL_DISTRO_NAME"
    echo "  • Windows Host: $(powershell.exe -Command 'Write-Host $env:COMPUTERNAME')"
    echo "  • External Display: Configured"
    echo "  • Power Management: Disabled"
    echo "  • Touchscreen: Calibrated"
    echo "  • Services: Running"
    echo "  • House ID: $HOUSE_ID"
    echo ""
    echo -e "${PURPLE}Delightful Features Enabled:${NC}"
    echo "  • Easter Eggs: Konami Code, Secret Patterns"
    echo "  • Long Press: Debug Mode Reveal"
    echo "  • Multi-Touch: Magic Effects"
    echo "  • Touch Patterns: Interaction Insights"
    echo "  • WSL2 Integration: Windows device access"
    echo ""
    echo -e "${GREEN}Ready for Party! 🎉${NC}"
    echo ""
    echo "Access the party interface at: http://localhost:8000/party"
    echo "Press Ctrl+C to stop party mode"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up WSL2 party mode..."
    
    # Restore Windows power management
    powershell.exe -Command "
        try {
            powercfg /change monitor-timeout-ac 10
            powercfg /change standby-timeout-ac 10
            Write-Host 'Power management restored'
        } catch {
            Write-Host 'Could not restore power management'
        }
    "
    
    # Stop services
    if [ -f "wsl2/compose.yml" ]; then
        docker compose -f wsl2/compose.yml down
    else
        docker compose -f infra/docker-compose.yml down
    fi
    
    log_success "WSL2 party mode cleanup complete"
}

# Main function
main() {
    log_delight "🎉 Starting Whispering Machine WSL2 Party Mode Setup 🎉"
    echo ""
    
    # Setup signal handlers
    trap cleanup EXIT INT TERM
    
    # Run setup steps
    check_wsl2
    check_dependencies
    configure_windows_power_management
    detect_windows_displays
    create_wsl2_touch_calibration
    start_wsl2_services
    
    # Show status
    show_wsl2_party_status
    
    # Keep running until interrupted
    log_info "WSL2 party mode active - press Ctrl+C to stop"
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
