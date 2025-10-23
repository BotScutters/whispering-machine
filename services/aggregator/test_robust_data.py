#!/usr/bin/env python3
"""
Comprehensive Tests for Robust Data Processing

Tests data validation, sanitization, and error recovery mechanisms.
All tests designed to run in Docker containers on unRAID.
"""

import json
import time
import unittest
from typing import Dict, Any

import numpy as np
from robust_data_processor import (
    DataProcessor, ErrorRecoveryManager, ValidationResult, DataQuality,
    RobustAudioFeatures, RobustOccupancy, RobustEncoder, RobustButton
)


class TestRobustDataProcessor(unittest.TestCase):
    """Test robust data processing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = DataProcessor()
        self.recovery_manager = ErrorRecoveryManager()
    
    def test_valid_audio_data(self):
        """Test processing of valid audio data"""
        valid_data = {
            'rms': 0.5,
            'zcr': 0.3,
            'low': 0.1,
            'mid': 0.2,
            'high': 0.3,
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_audio_features(valid_data, 'node1')
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.quality, DataQuality.EXCELLENT)
        self.assertIsNotNone(result.sanitized_data)
        self.assertEqual(len(result.errors), 0)
    
    def test_invalid_audio_data(self):
        """Test processing of invalid audio data"""
        invalid_data = {
            'rms': 'not_a_number',
            'zcr': 0.3,
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_audio_features(invalid_data, 'node1')
        
        # Should be sanitized, not invalid
        self.assertTrue(result.is_valid)
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
        self.assertGreater(len(result.warnings), 0)
    
    def test_sanitized_audio_data(self):
        """Test sanitization of malformed audio data"""
        malformed_data = {
            'rms': float('inf'),
            'zcr': float('nan'),
            'low': -0.5,
            'mid': 1.5,
            'high': 'invalid',
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_audio_features(malformed_data, 'node1')
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
        self.assertGreater(len(result.warnings), 0)
        
        # Check sanitized values
        sanitized = result.sanitized_data
        self.assertEqual(sanitized['rms'], 0.0)  # inf -> 0.0
        self.assertEqual(sanitized['zcr'], 0.0)  # nan -> 0.0
        self.assertEqual(sanitized['low'], 0.0)  # negative -> 0.0
        self.assertEqual(sanitized['mid'], 1.0)  # > 1.0 -> 1.0
        self.assertEqual(sanitized['high'], 0.0)  # invalid -> 0.0
    
    def test_missing_timestamp(self):
        """Test handling of missing timestamp"""
        data_without_timestamp = {
            'rms': 0.5,
            'zcr': 0.3,
            'low': 0.1,
            'mid': 0.2,
            'high': 0.3
        }
        
        result = self.processor.process_audio_features(data_without_timestamp, 'node1')
        
        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.sanitized_data)
        self.assertIn('ts_ms', result.sanitized_data)
        self.assertGreater(result.sanitized_data['ts_ms'], 0)
    
    def test_old_timestamp(self):
        """Test handling of old timestamp"""
        old_data = {
            'rms': 0.5,
            'zcr': 0.3,
            'low': 0.1,
            'mid': 0.2,
            'high': 0.3,
            'ts_ms': int(time.time() * 1000) - 700000  # 11+ minutes ago
        }
        
        result = self.processor.process_audio_features(old_data, 'node1')
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.quality, DataQuality.INVALID)
    
    def test_valid_occupancy_data(self):
        """Test processing of valid occupancy data"""
        valid_data = {
            'occupied': True,
            'transitions': 5,
            'activity': 0.7,
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_occupancy(valid_data, 'node1')
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.quality, DataQuality.EXCELLENT)
        self.assertIsNotNone(result.sanitized_data)
    
    def test_invalid_occupancy_data(self):
        """Test processing of invalid occupancy data"""
        invalid_data = {
            'occupied': 'yes',  # Should be boolean
            'transitions': -5,  # Should be >= 0
            'activity': 1.5,   # Should be <= 1.0
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_occupancy(invalid_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
        self.assertGreater(len(result.warnings), 0)
    
    def test_valid_encoder_data(self):
        """Test processing of valid encoder data"""
        valid_data = {
            'pos': 100,
            'delta': 5,
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_encoder(valid_data, 'node1')
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.quality, DataQuality.EXCELLENT)
        self.assertIsNotNone(result.sanitized_data)
    
    def test_invalid_encoder_data(self):
        """Test processing of invalid encoder data"""
        invalid_data = {
            'pos': 'invalid',
            'delta': float('inf'),
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_encoder(invalid_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
    
    def test_valid_button_data(self):
        """Test processing of valid button data"""
        valid_data = {
            'pressed': True,
            'event': 'press',
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_button(valid_data, 'node1')
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.quality, DataQuality.EXCELLENT)
        self.assertIsNotNone(result.sanitized_data)
    
    def test_invalid_button_data(self):
        """Test processing of invalid button data"""
        invalid_data = {
            'pressed': 'yes',  # Should be boolean
            'event': 'invalid_event',  # Should be valid event
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_button(invalid_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.EXCELLENT)  # String 'yes' converts to True
        self.assertIsNotNone(result.sanitized_data)
        self.assertEqual(result.sanitized_data['event'], 'unknown')
    
    def test_processing_stats(self):
        """Test processing statistics tracking"""
        # Process some data
        valid_data = {
            'rms': 0.5,
            'zcr': 0.3,
            'low': 0.1,
            'mid': 0.2,
            'high': 0.3,
            'ts_ms': int(time.time() * 1000)
        }
        
        self.processor.process_audio_features(valid_data, 'node1')
        
        stats = self.processor.get_stats()
        self.assertEqual(stats['total_processed'], 1)
        self.assertEqual(stats['valid_data'], 0)  # Not tracked separately
        self.assertEqual(stats['invalid_data'], 0)
    
    def test_stats_reset(self):
        """Test statistics reset functionality"""
        # Process some data
        valid_data = {
            'rms': 0.5,
            'zcr': 0.3,
            'low': 0.1,
            'mid': 0.2,
            'high': 0.3,
            'ts_ms': int(time.time() * 1000)
        }
        
        self.processor.process_audio_features(valid_data, 'node1')
        
        # Reset stats
        self.processor.reset_stats()
        
        stats = self.processor.get_stats()
        self.assertEqual(stats['total_processed'], 0)
        self.assertEqual(stats['invalid_data'], 0)


class TestErrorRecoveryManager(unittest.TestCase):
    """Test error recovery and graceful degradation"""
    
    def setUp(self):
        """Set up test environment"""
        self.recovery_manager = ErrorRecoveryManager()
    
    def test_recovery_attempt_logic(self):
        """Test recovery attempt logic"""
        node_id = 'node1'
        data_type = 'audio'
        
        # Should allow recovery initially
        self.assertTrue(self.recovery_manager.should_attempt_recovery(node_id, data_type))
        
        # Record some errors
        for _ in range(5):
            self.recovery_manager.record_error(node_id, data_type)
        
        # Wait for cooldown to pass
        import time
        time.sleep(0.1)  # Small delay to avoid cooldown
        
        # Should still allow recovery
        self.assertTrue(self.recovery_manager.should_attempt_recovery(node_id, data_type))
        
        # Record many errors (need more than 10 to trigger the limit)
        for _ in range(15):
            self.recovery_manager.record_error(node_id, data_type)
        
        # Should not allow recovery
        self.assertFalse(self.recovery_manager.should_attempt_recovery(node_id, data_type))
    
    def test_recovery_cooldown(self):
        """Test recovery cooldown mechanism"""
        node_id = 'node1'
        data_type = 'audio'
        
        # Record an error
        self.recovery_manager.record_error(node_id, data_type)
        
        # Should not allow immediate recovery
        self.assertFalse(self.recovery_manager.should_attempt_recovery(node_id, data_type))
    
    def test_audio_recovery(self):
        """Test audio data recovery"""
        raw_data = {'invalid': 'data'}
        
        recovered = self.recovery_manager.attempt_recovery('node1', 'audio', raw_data)
        
        self.assertIsNotNone(recovered)
        self.assertIn('rms', recovered)
        self.assertIn('zcr', recovered)
        self.assertIn('ts_ms', recovered)
        self.assertEqual(recovered['rms'], 0.0)
        self.assertEqual(recovered['zcr'], 0.0)
    
    def test_occupancy_recovery(self):
        """Test occupancy data recovery"""
        raw_data = {'invalid': 'data'}
        
        recovered = self.recovery_manager.attempt_recovery('node1', 'occupancy', raw_data)
        
        self.assertIsNotNone(recovered)
        self.assertIn('occupied', recovered)
        self.assertIn('transitions', recovered)
        self.assertIn('activity', recovered)
        self.assertIn('ts_ms', recovered)
        self.assertFalse(recovered['occupied'])
        self.assertEqual(recovered['transitions'], 0)
        self.assertEqual(recovered['activity'], 0.0)
    
    def test_encoder_recovery(self):
        """Test encoder data recovery"""
        raw_data = {'invalid': 'data'}
        
        recovered = self.recovery_manager.attempt_recovery('node1', 'encoder', raw_data)
        
        self.assertIsNotNone(recovered)
        self.assertIn('pos', recovered)
        self.assertIn('delta', recovered)
        self.assertIn('ts_ms', recovered)
        self.assertEqual(recovered['pos'], 0)
        self.assertEqual(recovered['delta'], 0)
    
    def test_button_recovery(self):
        """Test button data recovery"""
        raw_data = {'invalid': 'data'}
        
        recovered = self.recovery_manager.attempt_recovery('node1', 'button', raw_data)
        
        self.assertIsNotNone(recovered)
        self.assertIn('pressed', recovered)
        self.assertIn('event', recovered)
        self.assertIn('ts_ms', recovered)
        self.assertFalse(recovered['pressed'])
        self.assertIsNone(recovered['event'])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and extreme scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = DataProcessor()
    
    def test_empty_data(self):
        """Test handling of empty data"""
        empty_data = {}
        
        result = self.processor.process_audio_features(empty_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
    
    def test_none_values(self):
        """Test handling of None values"""
        none_data = {
            'rms': None,
            'zcr': None,
            'low': None,
            'mid': None,
            'high': None,
            'ts_ms': None
        }
        
        result = self.processor.process_audio_features(none_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
    
    def test_extreme_values(self):
        """Test handling of extreme values"""
        extreme_data = {
            'rms': 1e10,
            'zcr': -1e10,
            'low': float('inf'),
            'mid': float('-inf'),
            'high': float('nan'),
            'ts_ms': int(time.time() * 1000)
        }
        
        result = self.processor.process_audio_features(extreme_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.GOOD)
        self.assertIsNotNone(result.sanitized_data)
        
        # Check that extreme values are clamped
        sanitized = result.sanitized_data
        self.assertEqual(sanitized['rms'], 1.0)  # Clamped to 1.0
        self.assertEqual(sanitized['zcr'], 0.0)  # Clamped to 0.0
        self.assertEqual(sanitized['low'], 0.0)  # inf -> 0.0
        self.assertEqual(sanitized['mid'], 0.0)  # -inf -> 0.0
        self.assertEqual(sanitized['high'], 0.0)  # nan -> 0.0
    
    def test_malformed_json(self):
        """Test handling of malformed JSON-like data"""
        malformed_data = {
            'rms': '0.5',
            'zcr': '0.3',
            'low': '0.1',
            'mid': '0.2',
            'high': '0.3',
            'ts_ms': str(int(time.time() * 1000))
        }
        
        result = self.processor.process_audio_features(malformed_data, 'node1')
        
        self.assertTrue(result.is_valid)  # Should be sanitized
        self.assertEqual(result.quality, DataQuality.EXCELLENT)  # String numbers convert fine
        self.assertIsNotNone(result.sanitized_data)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
