#!/usr/bin/env python3
"""
Audio Bridge Service

Captures audio from MacBook built-in microphone, sends to Whisper for transcription,
and publishes transcripts to MQTT. Designed to work with MacBook lid closed.
"""

import asyncio
import logging
import os
import signal
import sys
import time
from typing import Optional

import httpx
import paho.mqtt.client as mqtt
from fastapi import FastAPI
from pydantic import BaseModel

from audio_capture import AudioCapture
from whisper_client import WhisperClient
from mqtt_publisher import MQTTPublisher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
HOUSE_ID = os.getenv('HOUSE_ID', 'houseA')
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
WHISPER_URL = os.getenv('WHISPER_URL', '')
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'tiny-int8')
WHISPER_LANGUAGE = os.getenv('WHISPER_LANGUAGE', 'en')
AUDIO_DEVICE_INDEX = int(os.getenv('AUDIO_DEVICE_INDEX', '0'))
AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', '16000'))
AUDIO_CHUNK_DURATION_MS = int(os.getenv('AUDIO_CHUNK_DURATION_MS', '3000'))
AUDIO_SILENCE_THRESHOLD = int(os.getenv('AUDIO_SILENCE_THRESHOLD', '500'))

class HealthResponse(BaseModel):
    status: str
    audio_capture: bool
    whisper_connected: bool
    mqtt_connected: bool
    uptime_seconds: float

class AudioBridgeService:
    def __init__(self):
        self.app = FastAPI(title="Audio Bridge Service")
        self.start_time = time.time()
        self.running = False
        
        # Components
        self.audio_capture: Optional[AudioCapture] = None
        self.whisper_client: Optional[WhisperClient] = None
        self.mqtt_publisher: Optional[MQTTPublisher] = None
        
        # Setup FastAPI routes
        self.setup_routes()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_routes(self):
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            return HealthResponse(
                status="healthy" if self.running else "starting",
                audio_capture=self.audio_capture is not None and self.audio_capture.is_capturing(),
                whisper_connected=self.whisper_client is not None and self.whisper_client.is_connected(),
                mqtt_connected=self.mqtt_publisher is not None and self.mqtt_publisher.is_connected(),
                uptime_seconds=time.time() - self.start_time
            )
        
        @self.app.get("/")
        async def root():
            return {"service": "audio_bridge", "status": "running"}
    
    def signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def initialize_components(self):
        """Initialize all service components"""
        try:
            # Initialize MQTT publisher
            logger.info("Initializing MQTT publisher...")
            self.mqtt_publisher = MQTTPublisher(
                broker=MQTT_BROKER,
                port=MQTT_PORT,
                house_id=HOUSE_ID
            )
            await self.mqtt_publisher.connect()
            
            # Initialize Whisper client
            if WHISPER_URL:
                logger.info(f"Initializing Whisper client for {WHISPER_URL}...")
                self.whisper_client = WhisperClient(
                    url=WHISPER_URL,
                    model=WHISPER_MODEL,
                    language=WHISPER_LANGUAGE
                )
                await self.whisper_client.test_connection()
            else:
                logger.warning("No WHISPER_URL provided, transcription disabled")
            
            # Initialize audio capture
            logger.info("Initializing audio capture...")
            self.audio_capture = AudioCapture(
                device_index=AUDIO_DEVICE_INDEX,
                sample_rate=AUDIO_SAMPLE_RATE,
                chunk_duration_ms=AUDIO_CHUNK_DURATION_MS,
                silence_threshold=AUDIO_SILENCE_THRESHOLD
            )
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    async def process_audio_chunk(self, audio_data: bytes, duration_ms: int):
        """Process a captured audio chunk"""
        try:
            # Send to Whisper for transcription
            if self.whisper_client and self.whisper_client.is_connected():
                transcript = await self.whisper_client.transcribe(audio_data)
                
                if transcript and transcript.strip():
                    # Publish transcript to MQTT
                    await self.mqtt_publisher.publish_transcript(
                        text=transcript,
                        confidence=0.95,  # TODO: Get actual confidence from Whisper
                        duration_ms=duration_ms,
                        model=WHISPER_MODEL,
                        trigger="continuous"
                    )
                    logger.info(f"Published transcript: {transcript[:50]}...")
                else:
                    logger.debug("No transcript generated (silence or error)")
            else:
                logger.debug("Whisper client not available, skipping transcription")
                
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    async def audio_capture_loop(self):
        """Main audio capture and processing loop"""
        logger.info("Starting audio capture loop...")
        
        while self.running:
            try:
                # Capture audio chunk
                audio_data, duration_ms = await self.audio_capture.capture_chunk()
                
                if audio_data:
                    # Process asynchronously
                    asyncio.create_task(self.process_audio_chunk(audio_data, duration_ms))
                else:
                    logger.debug("No audio data captured")
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in audio capture loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def run(self):
        """Main service loop"""
        logger.info("Starting Audio Bridge Service...")
        
        # Initialize components
        if not await self.initialize_components():
            logger.error("Failed to initialize components, exiting")
            return
        
        # Start audio capture
        self.running = True
        try:
            await self.audio_capture.start()
            logger.info("Audio capture started")
            
            # Start audio processing loop
            await self.audio_capture_loop()
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        self.running = False
        
        if self.audio_capture:
            await self.audio_capture.stop()
        
        if self.mqtt_publisher:
            await self.mqtt_publisher.disconnect()
        
        logger.info("Cleanup complete")

async def main():
    """Main entry point"""
    service = AudioBridgeService()
    
    # Start FastAPI server in background
    import uvicorn
    config = uvicorn.Config(
        service.app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Run server and service concurrently
    await asyncio.gather(
        server.serve(),
        service.run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)
