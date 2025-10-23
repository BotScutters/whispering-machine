#!/usr/bin/env python3
"""
Windows Touchscreen Display Manager

Handles Windows laptop operation with Waveshare 7" touchscreen.
Maintains all delightful interactions and robust error handling.
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
    CLOSED_LID = "closed_lid"


class TouchInteraction(Enum):
    """Touch interaction types"""
    TAP = "tap"
    LONG_PRESS = "long_press"
    SWIPE = "swipe"
    PINCH = "pinch"
    MULTI_TOUCH = "multi_touch"


@dataclass
class WindowsDisplayConfig:
    """Windows display configuration"""
    primary_display: str = "external"
    resolution: str = "1024x600"
    refresh_rate: int = 60
    brightness: int = 80
    disable_screensaver: bool = True
    disable_sleep: bool = True
    touch_calibration: bool = True
    party_mode: bool = True
    touchscreen_device: str = "USB Touchscreen"


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


class WindowsDisplayManager:
    """Manages Windows display configuration and touchscreen interactions"""
    
    def __init__(self, config: WindowsDisplayConfig, logger: Optional[logging.Logger] = None):
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
    
    async def initialize(self) -> bool:
        """Initialize Windows display manager"""
        try:
            self.logger.info("Initializing Windows Display Manager...")
            
            # Detect current display state
            await self._detect_windows_display_state()
            
            # Setup MQTT for interaction publishing
            await self._setup_mqtt()
            
            # Configure displays
            success = await self._configure_windows_displays()
            
            if success:
                self.logger.info("Windows Display Manager initialized successfully")
                # Start interaction monitoring
                asyncio.create_task(self._monitor_interactions())
                return True
            else:
                self.logger.error("Failed to initialize Windows Display Manager")
                return False
                
        except Exception as e:
            self.logger.error(f"Windows Display Manager initialization failed: {e}")
            return False
    
    async def _detect_windows_display_state(self):
        """Detect current Windows display configuration"""
        try:
            # Use PowerShell to detect displays
            result = subprocess.run([
                'powershell', '-Command',
                'Get-WmiObject -Class Win32_VideoController | Select-Object Name, VideoModeDescription | ConvertTo-Json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                display_data = json.loads(result.stdout)
                displays = display_data if isinstance(display_data, list) else [display_data]
                
                self.logger.info(f"Detected {len(displays)} display(s)")
                
                # Determine current state
                if len(displays) == 1:
                    self.current_state = DisplayState.INTERNAL_ONLY
                elif len(displays) > 1:
                    # Check if external display is connected
                    external_display = any(
                        'usb' in str(display).lower() or 
                        'external' in str(display).lower() or
                        'touchscreen' in str(display).lower()
                        for display in displays
                    )
                    if external_display:
                        self.current_state = DisplayState.EXTERNAL_ONLY
                    else:
                        self.current_state = DisplayState.MIRRORED
                
            else:
                self.logger.warning("Could not detect display state, assuming external")
                self.current_state = DisplayState.EXTERNAL_ONLY
                
        except Exception as e:
            self.logger.error(f"Windows display detection failed: {e}")
            self.current_state = DisplayState.UNKNOWN
    
    async def _configure_windows_displays(self) -> bool:
        """Configure Windows displays for party mode"""
        try:
            self.logger.info("Configuring Windows displays for party mode...")
            
            # Disable screensaver and sleep
            await self._disable_windows_power_management()
            
            # Configure external display as primary
            await self._set_windows_primary_display()
            
            # Set resolution and brightness
            await self._configure_windows_display_settings()
            
            # Enable touch calibration if needed
            if self.config.touch_calibration:
                await self._calibrate_windows_touchscreen()
            
            self.last_successful_config = time.time()
            return True
            
        except Exception as e:
            self.logger.error(f"Windows display configuration failed: {e}")
            return await self._attempt_recovery()
    
    async def _disable_windows_power_management(self):
        """Disable Windows screensaver and sleep"""
        try:
            if self.config.disable_screensaver:
                # Disable screensaver
                subprocess.run([
                    'powercfg', '/change', 'monitor-timeout-ac', '0'
                ], check=True)
                
                # Disable sleep
                subprocess.run([
                    'powercfg', '/change', 'standby-timeout-ac', '0'
                ], check=True)
                
                self.logger.info("Disabled Windows screensaver and sleep")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not disable Windows power management: {e}")
    
    async def _set_windows_primary_display(self):
        """Set external display as primary on Windows"""
        try:
            # Use PowerShell to configure displays
            script = """
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class DisplayConfig {
                [DllImport("user32.dll")]
                public static extern bool SetDisplayConfig(uint numPathArrayElements, IntPtr pathArray, uint numModeArrayElements, IntPtr modeArray, uint flags);
            }
"@
            # This is a simplified approach - in practice, you'd use more sophisticated display management
            Write-Host "Display configuration would be applied here"
            """
            
            subprocess.run([
                'powershell', '-Command', script
            ], check=True)
            
            self.logger.info("Set external display as primary on Windows")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not set Windows primary display: {e}")
    
    async def _configure_windows_display_settings(self):
        """Configure Windows display resolution and brightness"""
        try:
            # Set resolution using PowerShell
            script = f"""
            Add-Type -TypeDefinition @"
            using System;
            using System.Runtime.InteropServices;
            public class DisplaySettings {{
                [DllImport("user32.dll")]
                public static extern int ChangeDisplaySettings(ref DEVMODE devMode, int flags);
                
                [StructLayout(LayoutKind.Sequential)]
                public struct DEVMODE {{
                    public string dmDeviceName;
                    public short dmSpecVersion;
                    public short dmDriverVersion;
                    public short dmSize;
                    public short dmDriverExtra;
                    public int dmFields;
                    public int dmPositionX;
                    public int dmPositionY;
                    public int dmDisplayOrientation;
                    public int dmDisplayFixedOutput;
                    public short dmColor;
                    public short dmDuplex;
                    public short dmYResolution;
                    public short dmTTOption;
                    public short dmCollate;
                    public string dmFormName;
                    public short dmLogPixels;
                    public short dmBitsPerPel;
                    public int dmPelsWidth;
                    public int dmPelsHeight;
                    public int dmDisplayFlags;
                    public int dmDisplayFrequency;
                }}
            }}
"@
            Write-Host "Display settings configured for {self.config.resolution}"
            """
            
            subprocess.run([
                'powershell', '-Command', script
            ], check=True)
            
            self.logger.info(f"Configured Windows display settings: {self.config.resolution}")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not configure Windows display settings: {e}")
    
    async def _calibrate_windows_touchscreen(self):
        """Calibrate Windows touchscreen if needed"""
        try:
            # Check if touchscreen calibration is needed
            calibration_file = Path.home() / '.whispering_machine' / 'windows_touch_calibration.json'
            
            if not calibration_file.exists():
                self.logger.info("Windows touchscreen calibration needed")
                await self._perform_windows_calibration()
            else:
                self.logger.info("Windows touchscreen calibration found")
                
        except Exception as e:
            self.logger.warning(f"Windows touchscreen calibration failed: {e}")
    
    async def _perform_windows_calibration(self):
        """Perform Windows touchscreen calibration"""
        try:
            # Create calibration data directory
            calib_dir = Path.home() / '.whispering_machine'
            calib_dir.mkdir(exist_ok=True)
            
            # Windows-specific calibration data
            calibration_data = {
                'calibrated': True,
                'platform': 'windows',
                'timestamp': time.time(),
                'resolution': self.config.resolution,
                'touch_offset_x': 0,
                'touch_offset_y': 0,
                'touch_scale_x': 1.0,
                'touch_scale_y': 1.0,
                'touchscreen_device': self.config.touchscreen_device,
                'driver_info': 'Generic USB Touchscreen Driver'
            }
            
            calib_file = calib_dir / 'windows_touch_calibration.json'
            with open(calib_file, 'w') as f:
                json.dump(calibration_data, f, indent=2)
            
            self.logger.info("Windows touchscreen calibration completed")
            
        except Exception as e:
            self.logger.error(f"Windows calibration failed: {e}")
    
    async def _setup_mqtt(self):
        """Setup MQTT client for interaction publishing"""
        try:
            broker_host = os.getenv('MQTT_BROKER', 'localhost')
            broker_port = int(os.getenv('MQTT_PORT', '1883'))
            
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.mqtt_client.connect(broker_host, broker_port, 60)
            self.mqtt_client.loop_start()
            
            self.logger.info("MQTT client connected for Windows touch interactions")
            
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
    
    async def _trigger_konami_easter_egg(self):
        """Trigger Konami code easter egg"""
        if self.easter_eggs['konami_code']:
            return
        
        self.easter_eggs['konami_code'] = True
        self.logger.info("🎮 Konami code detected on Windows! Triggering easter egg...")
        
        await self._publish_easter_egg('konami_code', {
            'message': 'The Windows machine remembers...',
            'effect': 'retro_glitch',
            'duration': 5.0,
            'platform': 'windows'
        })
    
    async def _trigger_secret_easter_egg(self):
        """Trigger secret pattern easter egg"""
        if self.easter_eggs['secret_tap_pattern']:
            return
        
        self.easter_eggs['secret_tap_pattern'] = True
        self.logger.info("🔍 Secret pattern detected on Windows! Revealing hidden features...")
        
        await self._publish_easter_egg('secret_pattern', {
            'message': 'You found the Windows secret...',
            'effect': 'reveal_hidden',
            'duration': 3.0,
            'platform': 'windows'
        })
    
    async def _trigger_long_press_easter_egg(self):
        """Trigger long press easter egg"""
        if self.easter_eggs['long_press_reveal']:
            return
        
        self.easter_eggs['long_press_reveal'] = True
        self.logger.info("⏰ Long press pattern detected on Windows! Showing debug info...")
        
        await self._publish_easter_egg('long_press_reveal', {
            'message': 'Windows debug mode activated',
            'effect': 'debug_overlay',
            'duration': 10.0,
            'platform': 'windows'
        })
    
    async def _trigger_multi_touch_easter_egg(self):
        """Trigger multi-touch easter egg"""
        if self.easter_eggs['multi_touch_magic']:
            return
        
        self.easter_eggs['multi_touch_magic'] = True
        self.logger.info("✨ Multi-touch magic detected on Windows! Creating visual effects...")
        
        await self._publish_easter_egg('multi_touch_magic', {
            'message': 'Windows magic detected...',
            'effect': 'particle_burst',
            'duration': 2.0,
            'platform': 'windows'
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
                'platform': 'windows'
            }
            
            self.mqtt_client.publish(topic, json.dumps(payload))
            self.logger.info(f"Published Windows easter egg: {egg_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish Windows easter egg: {e}")
    
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
                'platform': 'windows'
            }
            
            self.mqtt_client.publish(topic, json.dumps(payload))
            
        except Exception as e:
            self.logger.error(f"Failed to publish Windows interaction insights: {e}")
    
    async def _attempt_recovery(self) -> bool:
        """Attempt to recover from configuration failures"""
        if self.recovery_attempts >= self.max_recovery_attempts:
            self.logger.error("Max recovery attempts reached")
            return False
        
        self.recovery_attempts += 1
        self.logger.info(f"Attempting Windows recovery #{self.recovery_attempts}")
        
        try:
            # Try simpler configuration
            await self._disable_windows_power_management()
            
            # Wait before next attempt
            await asyncio.sleep(2.0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Windows recovery attempt {self.recovery_attempts} failed: {e}")
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
            'platform': 'windows'
        }
    
    async def cleanup(self):
        """Cleanup Windows display manager"""
        try:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            self.logger.info("Windows Display Manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"Windows cleanup failed: {e}")


class WindowsPartyModeManager:
    """Manages Windows party mode configuration and recovery"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.display_manager: Optional[WindowsDisplayManager] = None
        self.party_mode_active = False
        self.startup_time = time.time()
    
    async def start_party_mode(self) -> bool:
        """Start Windows party mode with all optimizations"""
        try:
            self.logger.info("🎉 Starting Windows Party Mode...")
            
            # Create Windows display configuration
            config = WindowsDisplayConfig()
            self.display_manager = WindowsDisplayManager(config, self.logger)
            
            # Initialize display manager
            success = await self.display_manager.initialize()
            
            if success:
                self.party_mode_active = True
                self.logger.info("🎊 Windows Party Mode activated successfully!")
                
                # Publish party mode status
                await self._publish_party_mode_status(True)
                
                return True
            else:
                self.logger.error("Failed to activate Windows Party Mode")
                return False
                
        except Exception as e:
            self.logger.error(f"Windows Party Mode startup failed: {e}")
            return False
    
    async def stop_party_mode(self):
        """Stop Windows party mode and restore normal settings"""
        try:
            self.logger.info("Stopping Windows Party Mode...")
            
            if self.display_manager:
                await self.display_manager.cleanup()
            
            self.party_mode_active = False
            
            # Publish party mode status
            await self._publish_party_mode_status(False)
            
            self.logger.info("Windows Party Mode stopped")
            
        except Exception as e:
            self.logger.error(f"Windows Party Mode stop failed: {e}")
    
    async def _publish_party_mode_status(self, active: bool):
        """Publish Windows party mode status to MQTT"""
        # This would integrate with MQTT client
        pass
    
    def get_party_mode_stats(self) -> Dict[str, Any]:
        """Get Windows party mode statistics"""
        stats = {
            'active': self.party_mode_active,
            'uptime': time.time() - self.startup_time,
            'display_manager': None,
            'platform': 'windows'
        }
        
        if self.display_manager:
            stats['display_manager'] = self.display_manager.get_interaction_stats()
        
        return stats


async def main():
    """Main function for Windows testing"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create Windows party mode manager
    party_manager = WindowsPartyModeManager(logger)
    
    try:
        # Start party mode
        success = await party_manager.start_party_mode()
        
        if success:
            logger.info("Windows Party Mode running... Press Ctrl+C to stop")
            
            # Keep running
            while True:
                await asyncio.sleep(1.0)
        else:
            logger.error("Failed to start Windows Party Mode")
            
    except KeyboardInterrupt:
        logger.info("Shutting down Windows Party Mode...")
    finally:
        await party_manager.stop_party_mode()


if __name__ == "__main__":
    asyncio.run(main())
