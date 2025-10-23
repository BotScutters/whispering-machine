#!/usr/bin/env python3
"""
Comprehensive Tests for Display Manager

Tests display configuration, touch interactions, easter eggs, and recovery mechanisms.
All tests designed to run in Docker containers on unRAID.
"""

import asyncio
import json
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app import (
    DisplayManager, PartyModeManager, DisplayConfig, TouchEvent, TouchInteraction,
    DisplayState
)


class TestDisplayManager(unittest.TestCase):
    """Test display manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = DisplayConfig()
        self.display_manager = DisplayManager(self.config)
    
    def test_display_config_creation(self):
        """Test display configuration creation"""
        config = DisplayConfig()
        
        self.assertEqual(config.primary_display, "external")
        self.assertEqual(config.resolution, "1024x600")
        self.assertEqual(config.brightness, 80)
        self.assertTrue(config.disable_screensaver)
        self.assertTrue(config.disable_sleep)
        self.assertTrue(config.touch_calibration)
        self.assertTrue(config.party_mode)
    
    def test_touch_event_creation(self):
        """Test touch event creation"""
        event = TouchEvent(
            event_type=TouchInteraction.TAP,
            x=100,
            y=200,
            timestamp=time.time(),
            pressure=0.8,
            duration=0.1
        )
        
        self.assertEqual(event.event_type, TouchInteraction.TAP)
        self.assertEqual(event.x, 100)
        self.assertEqual(event.y, 200)
        self.assertEqual(event.pressure, 0.8)
        self.assertEqual(event.duration, 0.1)
    
    @patch('subprocess.run')
    async def test_display_state_detection(self, mock_run):
        """Test display state detection"""
        # Mock system_profiler output
        mock_output = {
            'SPDisplaysDataType': [
                {'_name': 'Built-in Retina Display'},
                {'_name': 'External USB Display'}
            ]
        }
        
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps(mock_output)
        
        await self.display_manager._detect_display_state()
        
        self.assertNotEqual(self.display_manager.current_state, DisplayState.UNKNOWN)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    async def test_power_management_disable(self, mock_run):
        """Test power management disabling"""
        mock_run.return_value.returncode = 0
        
        await self.display_manager._disable_power_management()
        
        # Should call pmset commands
        self.assertEqual(mock_run.call_count, 2)
        calls = [call[0][0] for call in mock_run.call_args_list]
        self.assertIn(['pmset', '-a', 'displaysleep', '0'], calls)
        self.assertIn(['pmset', '-a', 'sleep', '0'], calls)
    
    def test_touch_event_recording(self):
        """Test touch event recording"""
        event = TouchEvent(
            event_type=TouchInteraction.TAP,
            x=100,
            y=200,
            timestamp=time.time()
        )
        
        self.display_manager.record_touch_event(event)
        
        self.assertEqual(len(self.display_manager.touch_history), 1)
        self.assertEqual(self.display_manager.touch_history[0], event)
    
    def test_touch_history_limit(self):
        """Test touch history limit"""
        # Add more than 100 events
        for i in range(150):
            event = TouchEvent(
                event_type=TouchInteraction.TAP,
                x=i,
                y=i,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        # Should only keep last 100
        self.assertEqual(len(self.display_manager.touch_history), 100)
        self.assertEqual(self.display_manager.touch_history[0].x, 50)  # First kept event
    
    def test_interaction_stats(self):
        """Test interaction statistics"""
        # Add some touch events
        for i in range(5):
            event = TouchEvent(
                event_type=TouchInteraction.TAP,
                x=i * 100,
                y=i * 100,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        stats = self.display_manager.get_interaction_stats()
        
        self.assertEqual(stats['total_interactions'], 5)
        self.assertIn('patterns', stats)
        self.assertIn('easter_eggs', stats)
        self.assertIn('current_state', stats)
    
    def test_konami_code_detection(self):
        """Test Konami code detection"""
        # Add swipe events to simulate Konami code
        for i in range(10):
            event = TouchEvent(
                event_type=TouchInteraction.SWIPE,
                x=100,
                y=100,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        detected = self.display_manager._detect_konami_code()
        self.assertTrue(detected)
    
    def test_secret_pattern_detection(self):
        """Test secret tap pattern detection"""
        # Add corner taps
        corners = [(25, 25), (975, 25), (25, 575), (975, 575), (50, 50)]
        
        for x, y in corners:
            event = TouchEvent(
                event_type=TouchInteraction.TAP,
                x=x,
                y=y,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        detected = self.display_manager._detect_secret_pattern()
        self.assertTrue(detected)
    
    def test_long_press_pattern_detection(self):
        """Test long press pattern detection"""
        # Add long press events
        for i in range(3):
            event = TouchEvent(
                event_type=TouchInteraction.LONG_PRESS,
                x=100,
                y=100,
                timestamp=time.time(),
                duration=2.0
            )
            self.display_manager.record_touch_event(event)
        
        detected = self.display_manager._detect_long_press_pattern()
        self.assertTrue(detected)
    
    def test_multi_touch_pattern_detection(self):
        """Test multi-touch pattern detection"""
        # Add multi-touch events
        for i in range(2):
            event = TouchEvent(
                event_type=TouchInteraction.MULTI_TOUCH,
                x=100,
                y=100,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        detected = self.display_manager._detect_multi_touch_pattern()
        self.assertTrue(detected)
    
    async def test_easter_egg_triggers(self):
        """Test easter egg triggering"""
        # Mock MQTT client
        self.display_manager.mqtt_client = MagicMock()
        
        # Trigger Konami code easter egg
        await self.display_manager._trigger_konami_easter_egg()
        
        self.assertTrue(self.display_manager.easter_eggs['konami_code'])
        self.display_manager.mqtt_client.publish.assert_called()
    
    async def test_recovery_mechanism(self):
        """Test recovery mechanism"""
        # Mock subprocess calls
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Attempt recovery
            success = await self.display_manager._attempt_recovery()
            
            self.assertTrue(success)
            self.assertEqual(self.display_manager.recovery_attempts, 1)
    
    async def test_max_recovery_attempts(self):
        """Test maximum recovery attempts"""
        # Set max attempts
        self.display_manager.recovery_attempts = 5
        
        # Attempt recovery
        success = await self.display_manager._attempt_recovery()
        
        self.assertFalse(success)
        self.assertEqual(self.display_manager.recovery_attempts, 5)


class TestPartyModeManager(unittest.TestCase):
    """Test party mode manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.party_manager = PartyModeManager()
    
    def test_party_mode_creation(self):
        """Test party mode manager creation"""
        self.assertFalse(self.party_manager.party_mode_active)
        self.assertIsNone(self.party_manager.display_manager)
        self.assertGreater(self.party_manager.startup_time, 0)
    
    async def test_party_mode_startup(self):
        """Test party mode startup"""
        with patch.object(DisplayManager, 'initialize', return_value=True):
            success = await self.party_manager.start_party_mode()
            
            self.assertTrue(success)
            self.assertTrue(self.party_manager.party_mode_active)
            self.assertIsNotNone(self.party_manager.display_manager)
    
    async def test_party_mode_startup_failure(self):
        """Test party mode startup failure"""
        with patch.object(DisplayManager, 'initialize', return_value=False):
            success = await self.party_manager.start_party_mode()
            
            self.assertFalse(success)
            self.assertFalse(self.party_manager.party_mode_active)
    
    async def test_party_mode_stop(self):
        """Test party mode stop"""
        # Start party mode first
        with patch.object(DisplayManager, 'initialize', return_value=True):
            await self.party_manager.start_party_mode()
        
        # Mock cleanup
        with patch.object(DisplayManager, 'cleanup') as mock_cleanup:
            await self.party_manager.stop_party_mode()
            
            self.assertFalse(self.party_manager.party_mode_active)
            mock_cleanup.assert_called_once()
    
    def test_party_mode_stats(self):
        """Test party mode statistics"""
        stats = self.party_manager.get_party_mode_stats()
        
        self.assertIn('active', stats)
        self.assertIn('uptime', stats)
        self.assertIn('display_manager', stats)
        self.assertFalse(stats['active'])
        self.assertIsNone(stats['display_manager'])


class TestTouchInteractions(unittest.TestCase):
    """Test touch interaction scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = DisplayConfig()
        self.display_manager = DisplayManager(self.config)
    
    def test_rapid_tap_interaction(self):
        """Test rapid tap interaction"""
        # Simulate rapid taps
        for i in range(10):
            event = TouchEvent(
                event_type=TouchInteraction.TAP,
                x=100 + i * 10,
                y=100 + i * 10,
                timestamp=time.time() + i * 0.1
            )
            self.display_manager.record_touch_event(event)
        
        # Analyze patterns
        asyncio.run(self.display_manager._analyze_interaction_patterns())
        
        self.assertGreater(self.display_manager.interaction_patterns.get('rapid_taps', 0), 0)
    
    def test_gesture_combination(self):
        """Test combination of gestures"""
        gestures = [
            TouchInteraction.TAP,
            TouchInteraction.LONG_PRESS,
            TouchInteraction.SWIPE,
            TouchInteraction.MULTI_TOUCH
        ]
        
        for gesture in gestures:
            event = TouchEvent(
                event_type=gesture,
                x=100,
                y=100,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        # Analyze patterns
        asyncio.run(self.display_manager._analyze_interaction_patterns())
        
        patterns = self.display_manager.interaction_patterns
        self.assertGreater(patterns.get('rapid_taps', 0), 0)
        self.assertGreater(patterns.get('long_presses', 0), 0)
        self.assertGreater(patterns.get('swipes', 0), 0)
        self.assertGreater(patterns.get('multi_touch', 0), 0)
    
    def test_edge_case_interactions(self):
        """Test edge case interactions"""
        # Test edge coordinates
        edge_coords = [
            (0, 0),           # Top-left
            (1023, 0),        # Top-right
            (0, 599),         # Bottom-left
            (1023, 599),      # Bottom-right
            (512, 300)        # Center
        ]
        
        for x, y in edge_coords:
            event = TouchEvent(
                event_type=TouchInteraction.TAP,
                x=x,
                y=y,
                timestamp=time.time()
            )
            self.display_manager.record_touch_event(event)
        
        self.assertEqual(len(self.display_manager.touch_history), 5)
    
    def test_pressure_sensitivity(self):
        """Test pressure sensitivity handling"""
        pressures = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for pressure in pressures:
            event = TouchEvent(
                event_type=TouchInteraction.TAP,
                x=100,
                y=100,
                timestamp=time.time(),
                pressure=pressure
            )
            self.display_manager.record_touch_event(event)
        
        # All events should be recorded regardless of pressure
        self.assertEqual(len(self.display_manager.touch_history), 5)


class TestRobustness(unittest.TestCase):
    """Test robustness and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = DisplayConfig()
        self.display_manager = DisplayManager(self.config)
    
    @patch('subprocess.run')
    async def test_subprocess_failure_handling(self, mock_run):
        """Test handling of subprocess failures"""
        mock_run.return_value.returncode = 1
        mock_run.side_effect = subprocess.CalledProcessError(1, 'test')
        
        # Should not crash
        await self.display_manager._disable_power_management()
        
        # Should handle gracefully
        self.assertIsNotNone(self.display_manager)
    
    async def test_mqtt_connection_failure(self):
        """Test MQTT connection failure handling"""
        with patch('paho.mqtt.client.Client') as mock_client:
            mock_client.return_value.connect.side_effect = Exception("Connection failed")
            
            # Should not crash
            await self.display_manager._setup_mqtt()
            
            # Should handle gracefully
            self.assertIsNotNone(self.display_manager)
    
    def test_invalid_touch_data(self):
        """Test handling of invalid touch data"""
        # Test with invalid coordinates
        invalid_events = [
            TouchEvent(TouchInteraction.TAP, -100, -100, time.time()),
            TouchEvent(TouchInteraction.TAP, 2000, 2000, time.time()),
            TouchEvent(TouchInteraction.TAP, float('inf'), float('nan'), time.time())
        ]
        
        for event in invalid_events:
            # Should not crash
            self.display_manager.record_touch_event(event)
        
        # Should record all events
        self.assertEqual(len(self.display_manager.touch_history), 3)
    
    async def test_concurrent_access(self):
        """Test concurrent access to touch history"""
        async def add_events():
            for i in range(10):
                event = TouchEvent(
                    event_type=TouchInteraction.TAP,
                    x=i,
                    y=i,
                    timestamp=time.time()
                )
                self.display_manager.record_touch_event(event)
                await asyncio.sleep(0.01)
        
        # Run multiple coroutines concurrently
        await asyncio.gather(*[add_events() for _ in range(3)])
        
        # Should handle concurrent access gracefully
        self.assertEqual(len(self.display_manager.touch_history), 30)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
