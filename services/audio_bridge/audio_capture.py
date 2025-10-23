"""
Audio Capture Module

Handles audio capture from MacBook built-in microphone using PyAudio.
Designed to work with MacBook lid closed.
"""

import asyncio
import logging
import time
import wave
from typing import Optional, Tuple

import numpy as np
import pyaudio

logger = logging.getLogger(__name__)

class AudioCapture:
    def __init__(
        self,
        device_index: int = 0,
        sample_rate: int = 16000,
        chunk_duration_ms: int = 3000,
        silence_threshold: int = 500
    ):
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.silence_threshold = silence_threshold
        
        # Calculate chunk size
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        
        # PyAudio instance
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.capturing = False
        
        logger.info(f"Audio capture initialized: device={device_index}, rate={sample_rate}, chunk={chunk_duration_ms}ms")
    
    def list_audio_devices(self) -> list:
        """List available audio devices"""
        if not self.pyaudio_instance:
            self.pyaudio_instance = pyaudio.PyAudio()
        
        devices = []
        for i in range(self.pyaudio_instance.get_device_count()):
            info = self.pyaudio_instance.get_device_info_by_index(i)
            devices.append({
                'index': i,
                'name': info['name'],
                'channels': info['maxInputChannels'],
                'sample_rate': info['defaultSampleRate']
            })
        
        return devices
    
    def get_default_device(self) -> int:
        """Get the default input device index"""
        if not self.pyaudio_instance:
            self.pyaudio_instance = pyaudio.PyAudio()
        
        try:
            default_info = self.pyaudio_instance.get_default_input_device_info()
            return default_info['index']
        except Exception as e:
            logger.error(f"Failed to get default device: {e}")
            return 0
    
    async def start(self):
        """Start audio capture"""
        try:
            if not self.pyaudio_instance:
                self.pyaudio_instance = pyaudio.PyAudio()
            
            # Get device info
            device_info = self.pyaudio_instance.get_device_info_by_index(self.device_index)
            logger.info(f"Using audio device: {device_info['name']}")
            
            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,  # Mono
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None  # We'll use blocking reads
            )
            
            self.capturing = True
            logger.info("Audio capture started")
            
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            raise
    
    async def stop(self):
        """Stop audio capture"""
        self.capturing = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
        
        logger.info("Audio capture stopped")
    
    def is_capturing(self) -> bool:
        """Check if audio capture is active"""
        return self.capturing and self.stream is not None
    
    async def capture_chunk(self) -> Tuple[Optional[bytes], int]:
        """Capture a chunk of audio data"""
        if not self.is_capturing():
            return None, 0
        
        try:
            # Read audio data
            audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            
            # Convert to numpy array for analysis
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Check for silence
            rms = np.sqrt(np.mean(audio_array**2))
            if rms < self.silence_threshold:
                logger.debug(f"Silent chunk detected (RMS: {rms})")
                return None, 0
            
            # Calculate actual duration
            duration_ms = int(len(audio_data) / (self.sample_rate * 2) * 1000)  # 2 bytes per sample
            
            logger.debug(f"Captured audio chunk: {len(audio_data)} bytes, RMS: {rms:.1f}, duration: {duration_ms}ms")
            
            return audio_data, duration_ms
            
        except Exception as e:
            logger.error(f"Error capturing audio chunk: {e}")
            return None, 0
    
    def create_wav_data(self, audio_data: bytes) -> bytes:
        """Convert raw audio data to WAV format"""
        import io
        
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data)
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()
    
    def get_audio_level(self, audio_data: bytes) -> float:
        """Get audio level (RMS) from audio data"""
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_array**2))
        return float(rms)
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.capturing:
            asyncio.create_task(self.stop())
