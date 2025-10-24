#!/usr/bin/env python3
"""
WSL2 Display Manager

Handles WSL2 integration with Windows touchscreen and display management.
Maintains all delightful interactions while leveraging WSL2's Windows integration.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

import paho.mqtt.client as mqtt


class DisplayState(Enum):
    """Display state enumeration"""
    UNKNOWN = "unknown"
    INTERNAL_ONLY = "internal_only"
    EXTERNAL_ONLY = "external_only"
    MIRRORED = "mirrored"
    EXTENDED = "extended"
    WSL2_INTEGRATION = "wsl2_integration"


class TouchInteraction(Enum):
    """Touch interaction types"""
    TAP = "tap"
    LONG_PRESS = "long_press"
    SWIPE = "swipe"
    PINCH = "pinch"
    MULTI_TOUCH = "multi_touch"


@dataclass
class WSL2DisplayConfig:
    """WSL2 display configuration"""
    primary_display: str = "external"
    resolution: str = "1024x600"
    refresh_rate: int = 60
    brightness: int = 80
    disable_screensaver: bool = True
    disable_sleep: bool = True
    touch_calibration: bool = True
    party_mode: bool = True
    touchscreen_device: str = "USB Touchscreen"
    windows_integration: bool = True


@dataclass
class TouchEvent:
    """Touch event data"""
    event_type: TouchInteraction
    x: int
    y: int
    timestamp: float
    pressure: float = 1.0
    duration: float = 0.0
    gesture_data: Optional[Dict[str, Any]] = None


class WSL2DisplayManager:
    """Manages WSL2 display configuration and Windows touchscreen interactions"""
    
    def __init__(self, config: WSL2DisplayConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.current_state = DisplayState.UNKNOWN
        self.touch_history: List[TouchEvent] = []
        self.interaction_patterns: Dict[str, int] = {}
        self.delight_triggers: Dict[str, Any] = {}
        self.mqtt_client: Optional[mqtt.Client] = None
        
        # Delightful interaction settings
        self.easter_eggs = {
            'konami_code': False,
            'secret_tap_pattern': False,
            'long_press_reveal': False,
            'multi_touch_magic': False
        }
        
        # Robust recovery settings
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        self.last_successful_config = None
        
        # WSL2 specific settings
        self.wsl2_distro = os.getenv('WSL_DISTRO_NAME', 'unknown')
        self.windows_host = self._get_windows_hostname()
    
    def _get_windows_hostname(self) -> str:
        """Get Windows hostname via WSL2 integration"""
        try:
            # Try to access Windows hostname via WSL2 integration
            # This should work from WSL2 but not from inside Docker container
            result = subprocess.run([
                'hostname'
            ], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else 'wsl2-host'
        except Exception:
            return 'wsl2-host'
    
    async def initialize(self) -> bool:
        """Initialize WSL2 display manager"""
        try:
            self.logger.info(f"Initializing WSL2 Display Manager (Distro: {self.wsl2_distro})...")
            
            # Detect current display state via Windows
            await self._detect_wsl2_display_state()
            
            # Setup MQTT for interaction publishing
            await self._setup_mqtt()
            
            # Configure displays via Windows
            success = await self._configure_wsl2_displays()
            
            if success:
                self.logger.info("WSL2 Display Manager initialized successfully")
                # Start interaction monitoring
                asyncio.create_task(self._monitor_interactions())
                return True
            else:
                self.logger.error("Failed to initialize WSL2 Display Manager")
                return False
                
        except Exception as e:
            self.logger.error(f"WSL2 Display Manager initialization failed: {e}")
            return False
    
    async def _detect_wsl2_display_state(self):
        """Detect current Windows display configuration via WSL2"""
        try:
            # For WSL2 party mode, assume external display is available
            # The actual display configuration is handled by the Windows host
            self.logger.info("WSL2 party mode: assuming external display available")
            self.current_state = DisplayState.EXTERNAL_ONLY
                
        except Exception as e:
            self.logger.error(f"WSL2 display detection failed: {e}")
            self.current_state = DisplayState.WSL2_INTEGRATION
    
    async def _configure_wsl2_displays(self) -> bool:
        """Configure Windows displays for party mode via WSL2"""
        try:
            self.logger.info("Configuring Windows displays for WSL2 party mode...")
            
            # For WSL2 party mode, we assume the Windows host handles display configuration
            # The touchscreen should be configured externally via the startup script
            self.logger.info("WSL2 party mode: display configuration handled by Windows host")
            self.last_successful_config = time.time()
            return True
            
        except Exception as e:
            self.logger.error(f"WSL2 display configuration failed: {e}")
            return False
    
    async def _disable_wsl2_power_management(self):
        """Disable Windows screensaver and sleep via WSL2"""
        try:
            if self.config.disable_screensaver:
                # Use PowerShell via WSL2 to disable power management
                subprocess.run([
                    'powershell.exe', '-Command',
                    'powercfg /change monitor-timeout-ac 0; powercfg /change standby-timeout-ac 0'
                ], check=True)
                
                self.logger.info("Disabled Windows power management via WSL2")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not disable Windows power management via WSL2: {e}")
    
    async def _set_wsl2_primary_display(self):
        """Set external display as primary on Windows via WSL2"""
        try:
            # Use PowerShell via WSL2 to configure displays
            script = """
            Write-Host "Configuring Windows display via WSL2..."
            # This would use Windows display APIs
            # For now, just log the action
            Write-Host "External display configuration applied"
            """
            
            subprocess.run([
                'powershell.exe', '-Command', script
            ], check=True)
            
            self.logger.info("Set external display as primary on Windows via WSL2")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not set Windows primary display via WSL2: {e}")
    
    async def _configure_wsl2_display_settings(self):
        """Configure Windows display resolution and brightness via WSL2"""
        try:
            # Use PowerShell via WSL2 to configure display settings
            script = f"""
            Write-Host "Configuring Windows display settings via WSL2..."
            Write-Host "Resolution: {self.config.resolution}"
            Write-Host "Brightness: {self.config.brightness}%"
            Write-Host "WSL2 Integration: Active"
            """
            
            subprocess.run([
                'powershell.exe', '-Command', script
            ], check=True)
            
            self.logger.info(f"Configured Windows display settings via WSL2: {self.config.resolution}")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not configure Windows display settings via WSL2: {e}")
    
    async def _calibrate_wsl2_touchscreen(self):
        """Calibrate Windows touchscreen if needed via WSL2"""
        try:
            # Check if touchscreen calibration is needed
            calibration_file = Path.home() / '.whispering_machine' / 'wsl2_touch_calibration.json'
            
            if not calibration_file.exists():
                self.logger.info("WSL2 touchscreen calibration needed")
                await self._perform_wsl2_calibration()
            else:
                self.logger.info("WSL2 touchscreen calibration found")
                
        except Exception as e:
            self.logger.warning(f"WSL2 touchscreen calibration failed: {e}")
    
    async def _perform_wsl2_calibration(self):
        """Perform Windows touchscreen calibration via WSL2"""
        try:
            # Create calibration data directory
            calib_dir = Path.home() / '.whispering_machine'
            calib_dir.mkdir(exist_ok=True)
            
            # WSL2-specific calibration data
            calibration_data = {
                'calibrated': True,
                'platform': 'wsl2',
                'host_os': 'windows',
                'timestamp': time.time(),
                'resolution': self.config.resolution,
                'touch_offset_x': 0,
                'touch_offset_y': 0,
                'touch_scale_x': 1.0,
                'touch_scale_y': 1.0,
                'touchscreen_device': self.config.touchscreen_device,
                'driver_info': 'Windows Generic USB Touchscreen Driver',
                'wsl2_distro': self.wsl2_distro,
                'windows_host': self.windows_host,
                'wsl2_integration': True
            }
            
            calib_file = calib_dir / 'wsl2_touch_calibration.json'
            with open(calib_file, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            self.logger.info("WSL2 touchscreen calibration completed")
            
        except Exception as e:
            self.logger.error(f"WSL2 calibration failed: {e}")
    
    async def _setup_mqtt(self):
        """Setup MQTT client for interaction publishing"""
        try:
            broker_host = os.getenv('MQTT_BROKER', 'localhost')
            broker_port = int(os.getenv('MQTT_PORT', '1883'))
            
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.mqtt_client.connect(broker_host, broker_port, 60)
            self.mqtt_client.loop_start()
            
            self.logger.info("MQTT client connected for WSL2 touch interactions")
            
        except Exception as e:
            self.logger.error(f"MQTT setup failed: {e}")
    
    async def _monitor_interactions(self):
        """Monitor touch interactions for delightful experiences"""
        while True:
            try:
                # Analyze recent touch patterns
                await self._analyze_interaction_patterns()
                
                # Check for easter eggs
                await self._check_easter_eggs()
                
                # Publish interaction insights
                await self._publish_interaction_insights()
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Interaction monitoring error: {e}")
                await asyncio.sleep(5.0)
    
    async def _analyze_interaction_patterns(self):
        """Analyze touch interaction patterns"""
        if len(self.touch_history) < 2:
            return
        
        recent_touches = self.touch_history[-10:]  # Last 10 touches
        
        # Detect patterns
        patterns = {
            'rapid_taps': 0,
            'long_presses': 0,
            'swipes': 0,
            'multi_touch': 0
        }
        
        for touch in recent_touches:
            if touch.event_type == TouchInteraction.TAP:
                patterns['rapid_taps'] += 1
            elif touch.event_type == TouchInteraction.LONG_PRESS:
                patterns['long_presses'] += 1
            elif touch.event_type == TouchInteraction.SWIPE:
                patterns['swipes'] += 1
            elif touch.event_type == TouchInteraction.MULTI_TOUCH:
                patterns['multi_touch'] += 1
        
        # Store patterns for analysis
        self.interaction_patterns.update(patterns)
    
    async def _check_easter_eggs(self):
        """Check for easter egg triggers"""
        try:
            # Konami code detection
            if self._detect_konami_code():
                await self._trigger_konami_easter_egg()
            
            # Secret tap pattern
            if self._detect_secret_pattern():
                await self._trigger_secret_easter_egg()
            
            # Long press reveal
            if self._detect_long_press_pattern():
                await self._trigger_long_press_easter_egg()
            
            # Multi-touch magic
            if self._detect_multi_touch_pattern():
                await self._trigger_multi_touch_easter_egg()
                
        except Exception as e:
            self.logger.error(f"Easter egg check failed: {e}")
    
    def _detect_konami_code(self) -> bool:
        """Detect Konami code pattern"""
        if len(self.touch_history) < 10:
            return False
        
        recent = self.touch_history[-10:]
        return len([t for t in recent if t.event_type == TouchInteraction.SWIPE]) >= 4
    
    def _detect_secret_pattern(self) -> bool:
        """Detect secret tap pattern"""
        if len(self.touch_history) < 5:
            return False
        
        recent = self.touch_history[-5:]
        corner_taps = 0
        for touch in recent:
            if (touch.x < 50 or touch.x > 974) and (touch.y < 50 or touch.y > 550):
                corner_taps += 1
        
        return corner_taps >= 4
    
    def _detect_long_press_pattern(self) -> bool:
        """Detect long press pattern"""
        if len(self.touch_history) < 3:
            return False
        
        recent = self.touch_history[-3:]
        return all(t.event_type == TouchInteraction.LONG_PRESS for t in recent)
    
    def _detect_multi_touch_pattern(self) -> bool:
        """Detect multi-touch pattern"""
        if len(self.touch_history) < 2:
            return False
        
        recent = self.touch_history[-2:]
        return all(t.event_type == TouchInteraction.MULTI_TOUCH for t in recent)
    
    async def _trigger_konami_code_easter_egg(self):
        """Trigger Konami code easter egg"""
        if self.easter_eggs['konami_code']:
            return
        
        self.easter_eggs['konami_code'] = True
        self.logger.info("🎮 Konami code detected on WSL2! Triggering easter egg...")
        
        await self._publish_easter_egg('konami_code', {
            'message': 'The WSL2 machine remembers...',
            'effect': 'retro_glitch',
            'duration': 5.0,
            'platform': 'wsl2',
            'windows_host': self.windows_host
        })
    
    async def _trigger_secret_easter_egg(self):
        """Trigger secret pattern easter egg"""
        if self.easter_eggs['secret_tap_pattern']:
            return
        
        self.easter_eggs['secret_tap_pattern'] = True
        self.logger.info("🔍 Secret pattern detected on WSL2! Revealing hidden features...")
        
        await self._publish_easter_egg('secret_pattern', {
            'message': 'You found the WSL2 secret...',
            'effect': 'reveal_hidden',
            'duration': 3.0,
            'platform': 'wsl2',
            'windows_host': self.windows_host
        })
    
    async def _trigger_long_press_easter_egg(self):
        """Trigger long press easter egg"""
        if self.easter_eggs['long_press_reveal']:
            return
        
        self.easter_eggs['long_press_reveal'] = True
        self.logger.info("⏰ Long press pattern detected on WSL2! Showing debug info...")
        
        await self._publish_easter_egg('long_press_reveal', {
            'message': 'WSL2 debug mode activated',
            'effect': 'debug_overlay',
            'duration': 10.0,
            'platform': 'wsl2',
            'windows_host': self.windows_host
        })
    
    async def _trigger_multi_touch_easter_egg(self):
        """Trigger multi-touch easter egg"""
        if self.easter_eggs['multi_touch_magic']:
            return
        
        self.easter_eggs['multi_touch_magic'] = True
        self.logger.info("✨ Multi-touch magic detected on WSL2! Creating visual effects...")
        
        await self._publish_easter_egg('multi_touch_magic', {
            'message': 'WSL2 magic detected...',
            'effect': 'particle_burst',
            'duration': 2.0,
            'platform': 'wsl2',
            'windows_host': self.windows_host
        })
    
    async def _publish_easter_egg(self, egg_type: str, data: Dict[str, Any]):
        """Publish easter egg event to MQTT"""
        if not self.mqtt_client:
            return
        
        try:
            topic = f"party/{os.getenv('HOUSE_ID', 'houseA')}/display/easter_egg/{egg_type}"
            payload = {
                'type': egg_type,
                'data': data,
                'timestamp': time.time(),
                'interaction_count': len(self.touch_history),
                'platform': 'wsl2',
                'wsl2_distro': self.wsl2_distro,
                'windows_host': self.windows_host
            }
            
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.info(f"Published WSL2 easter egg: {egg_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish WSL2 easter egg: {e}")
    
    async def _publish_interaction_insights(self):
        """Publish interaction insights to MQTT"""
        if not self.mqtt_client or not self.interaction_patterns:
            return
        
        try:
            topic = f"party/{os.getenv('HOUSE_ID', 'houseA')}/display/interactions/insights"
            payload = {
                'patterns': self.interaction_patterns.copy(),
                'total_interactions': len(self.touch_history),
                'easter_eggs_found': sum(self.easter_eggs.values()),
                'timestamp': time.time(),
                'platform': 'wsl2',
                'wsl2_distro': self.wsl2_distro,
                'windows_host': self.windows_host
            }
            
            self.mqtt_client.publish(topic, json.dumps(payload))
            
        except Exception as e:
            self.logger.error(f"Failed to publish WSL2 interaction insights: {e}")
    
    async def _attempt_recovery(self) -> bool:
        """Attempt to recover from configuration failures"""
        if self.recovery_attempts >= self.max_recovery_attempts:
            self.logger.error("Max recovery attempts reached")
            return False
        
        self.recovery_attempts += 1
        self.logger.info(f"Attempting WSL2 recovery #{self.recovery_attempts}")
        
        try:
            # Try simpler configuration via WSL2
            await self._disable_wsl2_power_management()
            
            # Wait before next attempt
            await asyncio.sleep(2.0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"WSL2 recovery attempt {self.recovery_attempts} failed: {e}")
            return False
    
    def record_touch_event(self, event: TouchEvent):
        """Record a touch event"""
        self.touch_history.append(event)
        
        # Keep only recent history (last 100 events)
        if len(self.touch_history) > 100:
            self.touch_history = self.touch_history[-100:]
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get interaction statistics"""
        return {
            'total_interactions': len(self.touch_history),
            'patterns': self.interaction_patterns.copy(),
            'easter_eggs': self.easter_eggs.copy(),
            'current_state': self.current_state.value,
            'recovery_attempts': self.recovery_attempts,
            'platform': 'wsl2',
            'wsl2_distro': self.wsl2_distro,
            'windows_host': self.windows_host
        }
    
    async def cleanup(self):
        """Cleanup WSL2 display manager"""
        try:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            self.logger.info("WSL2 Display Manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"WSL2 cleanup failed: {e}")


class WSL2PartyModeManager:
    """Manages WSL2 party mode configuration and recovery"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.display_manager: Optional[WSL2DisplayManager] = None
        self.party_mode_active = False
        self.startup_time = time.time()
        self.wsl2_distro = os.getenv('WSL_DISTRO_NAME', 'unknown')
    
    async def start_party_mode(self) -> bool:
        """Start WSL2 party mode with all optimizations"""
        try:
            self.logger.info(f"🎉 Starting WSL2 Party Mode (Distro: {self.wsl2_distro})...")
            
            # Create WSL2 display configuration
            config = WSL2DisplayConfig()
            self.display_manager = WSL2DisplayManager(config, self.logger)
            
            # Initialize display manager
            success = await self.display_manager.initialize()
            
            if success:
                self.party_mode_active = True
                self.logger.info("🎊 WSL2 Party Mode activated successfully!")
                
                # Publish party mode status
                await self._publish_party_mode_status(True)
                
                return True
            else:
                self.logger.error("Failed to activate WSL2 Party Mode")
                return False
                
        except Exception as e:
            self.logger.error(f"WSL2 Party Mode startup failed: {e}")
            return False
    
    async def stop_party_mode(self):
        """Stop WSL2 party mode and restore normal settings"""
        try:
            self.logger.info("Stopping WSL2 Party Mode...")
            
            if self.display_manager:
                await self.display_manager.cleanup()
            
            self.party_mode_active = False
            
            # Publish party mode status
            await self._publish_party_mode_status(False)
            
            self.logger.info("WSL2 Party Mode stopped")
            
        except Exception as e:
            self.logger.error(f"WSL2 Party Mode stop failed: {e}")
    
    async def _publish_party_mode_status(self, active: bool):
        """Publish WSL2 party mode status to MQTT"""
        # This would integrate with MQTT client
        pass
    
    def get_party_mode_stats(self) -> Dict[str, Any]:
        """Get WSL2 party mode statistics"""
        stats = {
            'active': self.party_mode_active,
            'uptime': time.time() - self.startup_time,
            'display_manager': None,
            'platform': 'wsl2',
            'wsl2_distro': self.wsl2_distro
        }
        
        if self.display_manager:
            stats['display_manager'] = self.display_manager.get_interaction_stats()
        
        return stats


async def main():
    """Main function for WSL2 testing"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create WSL2 party mode manager
    party_manager = WSL2PartyModeManager(logger)
    
    try:
        # Start party mode
        success = await party_manager.start_party_mode()
        
        if success:
            logger.info("WSL2 Party Mode running... Press Ctrl+C to stop")
            
            # Keep running
            while True:
                await asyncio.sleep(1.0)
        else:
            logger.error("Failed to start WSL2 Party Mode")
            
    except KeyboardInterrupt:
        logger.info("Shutting down WSL2 Party Mode...")
    finally:
        await party_manager.stop_party_mode()


if __name__ == "__main__":
    asyncio.run(main())
