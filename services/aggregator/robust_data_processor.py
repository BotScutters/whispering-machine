#!/usr/bin/env python3
"""
Robust Data Processing Module

Handles garbage sensor data gracefully with validation, sanitization, and error recovery.
Critical for party environment where sensors may produce unreliable data.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import numpy as np
from pydantic import BaseModel, ValidationError, Field, validator


class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    quality: DataQuality
    sanitized_data: Optional[Dict[str, Any]] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class RobustAudioFeatures(BaseModel):
    """Robust audio features with validation and sanitization"""
    
    rms: float = Field(ge=0.0, le=1.0, description="RMS energy (0-1)")
    zcr: float = Field(ge=0.0, le=1.0, description="Zero crossing rate (0-1)")
    low: float = Field(ge=0.0, le=1.0, description="Low frequency energy (0-1)")
    mid: float = Field(ge=0.0, le=1.0, description="Mid frequency energy (0-1)")
    high: float = Field(ge=0.0, le=1.0, description="High frequency energy (0-1)")
    ts_ms: int = Field(gt=0, description="Timestamp in milliseconds")
    
    @validator('rms', 'zcr', 'low', 'mid', 'high')
    def validate_audio_values(cls, v):
        """Validate audio feature values"""
        if not isinstance(v, (int, float)):
            raise ValueError(f"Audio value must be numeric, got {type(v)}")
        
        # Handle NaN and infinity
        if np.isnan(v) or np.isinf(v):
            return 0.0
        
        # Clamp to valid range
        return max(0.0, min(1.0, float(v)))
    
    @validator('ts_ms')
    def validate_timestamp(cls, v):
        """Validate timestamp"""
        if not isinstance(v, (int, float)):
            raise ValueError(f"Timestamp must be numeric, got {type(v)}")
        
        current_ms = int(time.time() * 1000)
        
        # Check if timestamp is reasonable (within last 10 minutes)
        if abs(current_ms - int(v)) > 600000:
            raise ValueError(f"Timestamp too old or in future: {v}")
        
        return int(v)


class RobustOccupancy(BaseModel):
    """Robust occupancy data with validation"""
    
    occupied: bool
    transitions: int = Field(ge=0, description="Number of transitions")
    activity: float = Field(ge=0.0, le=1.0, description="Activity level (0-1)")
    ts_ms: int = Field(gt=0, description="Timestamp in milliseconds")
    
    @validator('transitions')
    def validate_transitions(cls, v):
        """Validate transition count"""
        if not isinstance(v, (int, float)):
            raise ValueError(f"Transitions must be numeric, got {type(v)}")
        
        # Clamp to reasonable range
        return max(0, min(1000, int(v)))
    
    @validator('activity')
    def validate_activity(cls, v):
        """Validate activity level"""
        if not isinstance(v, (int, float)):
            raise ValueError(f"Activity must be numeric, got {type(v)}")
        
        # Handle NaN and infinity
        if np.isnan(v) or np.isinf(v):
            return 0.0
        
        return max(0.0, min(1.0, float(v)))


class RobustEncoder(BaseModel):
    """Robust encoder data with validation"""
    
    pos: int = Field(description="Encoder position")
    delta: int = Field(description="Encoder delta")
    ts_ms: int = Field(gt=0, description="Timestamp in milliseconds")
    
    @validator('pos', 'delta')
    def validate_encoder_values(cls, v):
        """Validate encoder values"""
        if not isinstance(v, (int, float)):
            raise ValueError(f"Encoder value must be numeric, got {type(v)}")
        
        # Handle NaN and infinity
        if np.isnan(v) or np.isinf(v):
            return 0
        
        # Clamp to reasonable range
        return max(-10000, min(10000, int(v)))


class RobustButton(BaseModel):
    """Robust button data with validation"""
    
    pressed: bool
    event: Optional[str] = Field(default=None, description="Button event type")
    ts_ms: int = Field(gt=0, description="Timestamp in milliseconds")
    
    @validator('event')
    def validate_event(cls, v):
        """Validate button event"""
        if v is None:
            return None
        
        valid_events = ['press', 'release', 'hold', 'double', 'long']
        if v not in valid_events:
            return 'unknown'
        
        return v


class DataProcessor:
    """Robust data processor with validation and sanitization"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.stats = {
            'total_processed': 0,
            'valid_data': 0,
            'sanitized_data': 0,
            'invalid_data': 0,
            'quality_counts': {q.value: 0 for q in DataQuality}
        }
    
    def process_audio_features(self, data: Dict[str, Any], node_id: str) -> ValidationResult:
        """Process and validate audio features data"""
        self.stats['total_processed'] += 1
        
        try:
            # Attempt strict validation first
            validated = RobustAudioFeatures(**data)
            return ValidationResult(
                is_valid=True,
                quality=DataQuality.EXCELLENT,
                sanitized_data=validated.dict()
            )
            
        except ValidationError as e:
            # Try to sanitize the data
            sanitized = self._sanitize_audio_data(data)
            if sanitized:
                try:
                    validated = RobustAudioFeatures(**sanitized)
                    self.stats['sanitized_data'] += 1
                    return ValidationResult(
                        is_valid=True,
                        quality=DataQuality.GOOD,
                        sanitized_data=validated.dict(),
                        warnings=[f"Data sanitized: {str(e)}"]
                    )
                except ValidationError:
                    pass
            
            # Data is invalid
            self.stats['invalid_data'] += 1
            self.logger.warning(f"Invalid audio data from {node_id}: {e}")
            return ValidationResult(
                is_valid=False,
                quality=DataQuality.INVALID,
                errors=[str(e)]
            )
    
    def process_occupancy(self, data: Dict[str, Any], node_id: str) -> ValidationResult:
        """Process and validate occupancy data"""
        self.stats['total_processed'] += 1
        
        try:
            validated = RobustOccupancy(**data)
            return ValidationResult(
                is_valid=True,
                quality=DataQuality.EXCELLENT,
                sanitized_data=validated.dict()
            )
            
        except ValidationError as e:
            # Try to sanitize
            sanitized = self._sanitize_occupancy_data(data)
            if sanitized:
                try:
                    validated = RobustOccupancy(**sanitized)
                    self.stats['sanitized_data'] += 1
                    return ValidationResult(
                        is_valid=True,
                        quality=DataQuality.GOOD,
                        sanitized_data=validated.dict(),
                        warnings=[f"Data sanitized: {str(e)}"]
                    )
                except ValidationError:
                    pass
            
            self.stats['invalid_data'] += 1
            self.logger.warning(f"Invalid occupancy data from {node_id}: {e}")
            return ValidationResult(
                is_valid=False,
                quality=DataQuality.INVALID,
                errors=[str(e)]
            )
    
    def process_encoder(self, data: Dict[str, Any], node_id: str) -> ValidationResult:
        """Process and validate encoder data"""
        self.stats['total_processed'] += 1
        
        try:
            validated = RobustEncoder(**data)
            return ValidationResult(
                is_valid=True,
                quality=DataQuality.EXCELLENT,
                sanitized_data=validated.dict()
            )
            
        except ValidationError as e:
            sanitized = self._sanitize_encoder_data(data)
            if sanitized:
                try:
                    validated = RobustEncoder(**sanitized)
                    self.stats['sanitized_data'] += 1
                    return ValidationResult(
                        is_valid=True,
                        quality=DataQuality.GOOD,
                        sanitized_data=validated.dict(),
                        warnings=[f"Data sanitized: {str(e)}"]
                    )
                except ValidationError:
                    pass
            
            self.stats['invalid_data'] += 1
            self.logger.warning(f"Invalid encoder data from {node_id}: {e}")
            return ValidationResult(
                is_valid=False,
                quality=DataQuality.INVALID,
                errors=[str(e)]
            )
    
    def process_button(self, data: Dict[str, Any], node_id: str) -> ValidationResult:
        """Process and validate button data"""
        self.stats['total_processed'] += 1
        
        try:
            validated = RobustButton(**data)
            return ValidationResult(
                is_valid=True,
                quality=DataQuality.EXCELLENT,
                sanitized_data=validated.dict()
            )
            
        except ValidationError as e:
            sanitized = self._sanitize_button_data(data)
            if sanitized:
                try:
                    validated = RobustButton(**sanitized)
                    self.stats['sanitized_data'] += 1
                    return ValidationResult(
                        is_valid=True,
                        quality=DataQuality.GOOD,
                        sanitized_data=validated.dict(),
                        warnings=[f"Data sanitized: {str(e)}"]
                    )
                except ValidationError:
                    pass
            
            self.stats['invalid_data'] += 1
            self.logger.warning(f"Invalid button data from {node_id}: {e}")
            return ValidationResult(
                is_valid=False,
                quality=DataQuality.INVALID,
                errors=[str(e)]
            )
    
    def _sanitize_audio_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sanitize audio data"""
        sanitized = {}
        
        # Handle timestamp
        if 'ts_ms' in data:
            try:
                sanitized['ts_ms'] = int(data['ts_ms'])
            except (ValueError, TypeError):
                sanitized['ts_ms'] = int(time.time() * 1000)
        else:
            sanitized['ts_ms'] = int(time.time() * 1000)
        
        # Handle audio features
        audio_fields = ['rms', 'zcr', 'low', 'mid', 'high']
        for field in audio_fields:
            if field in data:
                try:
                    value = float(data[field])
                    if np.isnan(value) or np.isinf(value):
                        value = 0.0
                    sanitized[field] = max(0.0, min(1.0, value))
                except (ValueError, TypeError):
                    sanitized[field] = 0.0
            else:
                sanitized[field] = 0.0
        
        return sanitized
    
    def _sanitize_occupancy_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sanitize occupancy data"""
        sanitized = {}
        
        # Handle timestamp
        if 'ts_ms' in data:
            try:
                sanitized['ts_ms'] = int(data['ts_ms'])
            except (ValueError, TypeError):
                sanitized['ts_ms'] = int(time.time() * 1000)
        else:
            sanitized['ts_ms'] = int(time.time() * 1000)
        
        # Handle occupied
        if 'occupied' in data:
            sanitized['occupied'] = bool(data['occupied'])
        else:
            sanitized['occupied'] = False
        
        # Handle transitions
        if 'transitions' in data:
            try:
                sanitized['transitions'] = max(0, min(1000, int(data['transitions'])))
            except (ValueError, TypeError):
                sanitized['transitions'] = 0
        else:
            sanitized['transitions'] = 0
        
        # Handle activity
        if 'activity' in data:
            try:
                value = float(data['activity'])
                if np.isnan(value) or np.isinf(value):
                    value = 0.0
                sanitized['activity'] = max(0.0, min(1.0, value))
            except (ValueError, TypeError):
                sanitized['activity'] = 0.0
        else:
            sanitized['activity'] = 0.0
        
        return sanitized
    
    def _sanitize_encoder_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sanitize encoder data"""
        sanitized = {}
        
        # Handle timestamp
        if 'ts_ms' in data:
            try:
                sanitized['ts_ms'] = int(data['ts_ms'])
            except (ValueError, TypeError):
                sanitized['ts_ms'] = int(time.time() * 1000)
        else:
            sanitized['ts_ms'] = int(time.time() * 1000)
        
        # Handle position
        if 'pos' in data:
            try:
                sanitized['pos'] = max(-10000, min(10000, int(data['pos'])))
            except (ValueError, TypeError):
                sanitized['pos'] = 0
        else:
            sanitized['pos'] = 0
        
        # Handle delta
        if 'delta' in data:
            try:
                value = float(data['delta'])
                if np.isnan(value) or np.isinf(value):
                    value = 0.0
                sanitized['delta'] = max(-10000, min(10000, int(value)))
            except (ValueError, TypeError, OverflowError):
                sanitized['delta'] = 0
        else:
            sanitized['delta'] = 0
        
        return sanitized
    
    def _sanitize_button_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sanitize button data"""
        sanitized = {}
        
        # Handle timestamp
        if 'ts_ms' in data:
            try:
                sanitized['ts_ms'] = int(data['ts_ms'])
            except (ValueError, TypeError):
                sanitized['ts_ms'] = int(time.time() * 1000)
        else:
            sanitized['ts_ms'] = int(time.time() * 1000)
        
        # Handle pressed
        if 'pressed' in data:
            sanitized['pressed'] = bool(data['pressed'])
        else:
            sanitized['pressed'] = False
        
        # Handle event
        if 'event' in data:
            event = str(data['event']).lower()
            valid_events = ['press', 'release', 'hold', 'double', 'long']
            if event in valid_events:
                sanitized['event'] = event
            else:
                sanitized['event'] = 'unknown'
        else:
            sanitized['event'] = None
        
        return sanitized
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.stats = {
            'total_processed': 0,
            'valid_data': 0,
            'sanitized_data': 0,
            'invalid_data': 0,
            'quality_counts': {q.value: 0 for q in DataQuality}
        }


class ErrorRecoveryManager:
    """Manages error recovery and graceful degradation"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}
        self.last_error_time = {}
        self.recovery_strategies = {
            'audio': self._recover_audio_data,
            'occupancy': self._recover_occupancy_data,
            'encoder': self._recover_encoder_data,
            'button': self._recover_button_data
        }
    
    def should_attempt_recovery(self, node_id: str, data_type: str) -> bool:
        """Determine if recovery should be attempted"""
        key = f"{node_id}:{data_type}"
        
        # If too many recent errors, skip recovery
        if self.error_counts.get(key, 0) > 10:
            return False
        
        # If recent error, wait before retry
        last_error = self.last_error_time.get(key, 0)
        if time.time() - last_error < 0.1:  # 0.1 second cooldown for testing
            return False
        
        return True
    
    def record_error(self, node_id: str, data_type: str):
        """Record an error for tracking"""
        key = f"{node_id}:{data_type}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        self.last_error_time[key] = time.time()
    
    def attempt_recovery(self, node_id: str, data_type: str, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to recover from bad data"""
        if not self.should_attempt_recovery(node_id, data_type):
            return None
        
        try:
            recovery_func = self.recovery_strategies.get(data_type)
            if recovery_func:
                recovered_data = recovery_func(raw_data)
                if recovered_data:
                    self.logger.info(f"Recovered {data_type} data for {node_id}")
                    return recovered_data
        except Exception as e:
            self.logger.error(f"Recovery failed for {node_id}:{data_type}: {e}")
        
        self.record_error(node_id, data_type)
        return None
    
    def _recover_audio_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recover audio data with defaults"""
        return {
            'rms': 0.0,
            'zcr': 0.0,
            'low': 0.0,
            'mid': 0.0,
            'high': 0.0,
            'ts_ms': int(time.time() * 1000)
        }
    
    def _recover_occupancy_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recover occupancy data with defaults"""
        return {
            'occupied': False,
            'transitions': 0,
            'activity': 0.0,
            'ts_ms': int(time.time() * 1000)
        }
    
    def _recover_encoder_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recover encoder data with defaults"""
        return {
            'pos': 0,
            'delta': 0,
            'ts_ms': int(time.time() * 1000)
        }
    
    def _recover_button_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recover button data with defaults"""
        return {
            'pressed': False,
            'event': None,
            'ts_ms': int(time.time() * 1000)
        }
