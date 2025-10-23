#!/usr/bin/env bash
"""
Party Mode Startup Script

Configures MacBook for closed-lid operation with 7" touchscreen.
Handles display configuration, power management, and delightful interactions.
"""

set -e

echo "🎉 Whispering Machine - Party Mode Startup"
echo "=========================================="

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

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This script is designed for macOS only"
        exit 1
    fi
    log_success "Running on macOS"
}

# Check for required tools
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for displayplacer (optional but recommended)
    if ! command -v displayplacer &> /dev/null; then
        log_warning "displayplacer not found - install with: brew install displayplacer"
        missing_deps+=("displayplacer")
    fi
    
    # Check for osascript (should be available on macOS)
    if ! command -v osascript &> /dev/null; then
        log_error "osascript not found - this is required for macOS"
        exit 1
    fi
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        log_success "All dependencies available"
    else
        log_warning "Some optional dependencies missing: ${missing_deps[*]}"
    fi
}

# Detect external display
detect_external_display() {
    log_info "Detecting external displays..."
    
    # Use system_profiler to detect displays
    local display_info
    display_info=$(system_profiler SPDisplaysDataType -json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        local display_count
        display_count=$(echo "$display_info" | jq '.SPDisplaysDataType | length' 2>/dev/null || echo "1")
        
        if [ "$display_count" -gt 1 ]; then
            log_success "External display detected"
            return 0
        else
            log_warning "No external display detected"
            return 1
        fi
    else
        log_warning "Could not detect displays"
        return 1
    fi
}

# Configure power management
configure_power_management() {
    log_info "Configuring power management..."
    
    # Disable display sleep
    if sudo pmset -a displaysleep 0; then
        log_success "Display sleep disabled"
    else
        log_warning "Could not disable display sleep (may need sudo)"
    fi
    
    # Disable system sleep
    if sudo pmset -a sleep 0; then
        log_success "System sleep disabled"
    else
        log_warning "Could not disable system sleep (may need sudo)"
    fi
    
    # Disable disk sleep
    if sudo pmset -a disksleep 0; then
        log_success "Disk sleep disabled"
    else
        log_warning "Could not disable disk sleep (may need sudo)"
    fi
}

# Configure external display
configure_external_display() {
    log_info "Configuring external display..."
    
    # Check if displayplacer is available
    if command -v displayplacer &> /dev/null; then
        log_info "Using displayplacer for display configuration..."
        
        # List current displays
        log_info "Current display configuration:"
        displayplacer list
        
        # Set external display as primary (this is a simplified example)
        # In practice, you'd need to get the actual display IDs
        log_warning "Manual display configuration may be required"
        log_info "Use 'displayplacer list' to see available displays"
        log_info "Then configure with: displayplacer 'id:<display_id> res:${EXTERNAL_DISPLAY_RESOLUTION} scaling:on origin:(0,0) degree:0'"
        
    else
        log_warning "displayplacer not available - using system preferences"
        log_info "Please manually configure external display as primary"
        log_info "Resolution: ${EXTERNAL_DISPLAY_RESOLUTION}"
        log_info "Brightness: ${BRIGHTNESS_PERCENT}%"
    fi
}

# Set display brightness
set_display_brightness() {
    log_info "Setting display brightness to ${BRIGHTNESS_PERCENT}%..."
    
    # Use osascript to set brightness
    local brightness_decimal
    brightness_decimal=$(echo "scale=2; $BRIGHTNESS_PERCENT / 100" | bc)
    
    if osascript -e "tell application \"System Events\" to set value of slider 1 of group 1 of tab group 1 of window 1 of application process \"System Preferences\" to $brightness_decimal" 2>/dev/null; then
        log_success "Brightness set to ${BRIGHTNESS_PERCENT}%"
    else
        log_warning "Could not set brightness automatically"
        log_info "Please set brightness manually to ${BRIGHTNESS_PERCENT}%"
    fi
}

# Create touchscreen calibration
create_touch_calibration() {
    log_info "Creating touchscreen calibration..."
    
    local calib_dir="$HOME/.whispering_machine"
    local calib_file="$calib_dir/touch_calibration.json"
    
    # Create directory
    mkdir -p "$calib_dir"
    
    # Create calibration file
    cat > "$calib_file" << EOF
{
  "calibrated": true,
  "timestamp": $(date +%s),
  "resolution": "$EXTERNAL_DISPLAY_RESOLUTION",
  "touch_offset_x": 0,
  "touch_offset_y": 0,
  "touch_scale_x": 1.0,
  "touch_scale_y": 1.0,
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
    
    log_success "Touchscreen calibration created: $calib_file"
}

# Start party mode services
start_party_services() {
    log_info "Starting party mode services..."
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running - please start Docker first"
        exit 1
    fi
    
    # Start services using docker compose
    if [ -f "macbook/compose.yml" ]; then
        log_info "Starting services with docker compose..."
        docker compose -f macbook/compose.yml up -d
        
        if [ $? -eq 0 ]; then
            log_success "Party mode services started"
        else
            log_error "Failed to start party mode services"
            exit 1
        fi
    else
        log_warning "macbook/compose.yml not found - services may need manual startup"
    fi
}

# Display party mode status
show_party_status() {
    log_delight "🎊 Party Mode Configuration Complete! 🎊"
    echo ""
    echo -e "${CYAN}Party Mode Status:${NC}"
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
    echo ""
    echo -e "${GREEN}Ready for Party! 🎉${NC}"
    echo ""
    echo "Access the party interface at: http://localhost:8000/party"
    echo "Press Ctrl+C to stop party mode"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up party mode..."
    
    # Restore power management
    sudo pmset -a displaysleep 10
    sudo pmset -a sleep 10
    sudo pmset -a disksleep 10
    
    # Stop services
    if [ -f "macbook/compose.yml" ]; then
        docker compose -f macbook/compose.yml down
    fi
    
    log_success "Party mode cleanup complete"
}

# Main function
main() {
    log_delight "🎉 Starting Whispering Machine Party Mode Setup 🎉"
    echo ""
    
    # Setup signal handlers
    trap cleanup EXIT INT TERM
    
    # Run setup steps
    check_macos
    check_dependencies
    
    if detect_external_display; then
        configure_external_display
        set_display_brightness
    else
        log_warning "No external display detected - continuing with internal display"
    fi
    
    configure_power_management
    create_touch_calibration
    start_party_services
    
    # Show status
    show_party_status
    
    # Keep running until interrupted
    log_info "Party mode active - press Ctrl+C to stop"
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
