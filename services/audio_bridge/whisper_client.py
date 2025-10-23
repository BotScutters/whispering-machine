"""
Whisper Client Module

Handles communication with faster-whisper service via Wyoming protocol.
"""

import asyncio
import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

class WhisperClient:
    def __init__(
        self,
        url: str,
        model: str = "tiny-int8",
        language: str = "en"
    ):
        self.url = url.rstrip('/')
        self.model = model
        self.language = language
        self.connected = False
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=5)
        )
        
        logger.info(f"Whisper client initialized: {url}, model={model}, language={language}")
    
    async def test_connection(self) -> bool:
        """Test connection to Whisper service"""
        try:
            # Try health check endpoint
            response = await self.client.get(f"{self.url}/health")
            if response.status_code == 200:
                self.connected = True
                logger.info("Whisper service connection successful")
                return True
            else:
                logger.warning(f"Whisper health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to connect to Whisper service: {e}")
            self.connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Whisper service"""
        return self.connected
    
    async def transcribe(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data using Whisper service"""
        if not self.connected:
            logger.debug("Whisper client not connected, skipping transcription")
            return None
        
        try:
            # Convert audio data to WAV format
            wav_data = self._create_wav_data(audio_data)
            
            # Prepare request data
            files = {
                'audio': ('audio.wav', wav_data, 'audio/wav')
            }
            
            data = {
                'model': self.model,
                'language': self.language,
                'task': 'transcribe'
            }
            
            # Send request to Whisper service
            start_time = time.time()
            response = await self.client.post(
                f"{self.url}/transcribe",
                files=files,
                data=data
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('text', '').strip()
                
                if transcript:
                    logger.info(f"Transcription successful ({duration:.2f}s): {transcript[:50]}...")
                    return transcript
                else:
                    logger.debug("Empty transcript received")
                    return None
            else:
                logger.error(f"Transcription failed: {response.status_code} - {response.text}")
                return None
                
        except httpx.TimeoutException:
            logger.error("Transcription request timed out")
            return None
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None
    
    def _create_wav_data(self, audio_data: bytes) -> bytes:
        """Convert raw audio data to WAV format"""
        import io
        import wave
        
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(audio_data)
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        self.connected = False
        logger.info("Whisper client closed")
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.connected:
            asyncio.create_task(self.close())
