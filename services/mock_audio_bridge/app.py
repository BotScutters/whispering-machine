#!/usr/bin/env python3
"""
Mock Audio Bridge Service
Generates mock transcripts for testing the party UI
"""

import asyncio
import json
import logging
import os
import random
import time
from typing import Optional

import paho.mqtt.client as mqtt
from fastapi import FastAPI
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
HOUSE_ID = os.getenv('HOUSE_ID', 'hidden_house')
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))

class HealthResponse(BaseModel):
    status: str
    mqtt_connected: bool
    transcripts_generated: int
    uptime_seconds: float

class MockAudioBridge:
    def __init__(self):
        self.app = FastAPI(title="Mock Audio Bridge Service")
        self.start_time = time.time()
        self.running = False
        self.transcripts_generated = 0
        
        # MQTT client
        self.mqtt_client: Optional[mqtt.Client] = None
        self.connected = False
        
        # Mock transcripts
        self.mock_transcripts = [
            "The silence here is... unsettling.",
            "I can hear footsteps that shouldn't be there.",
            "Something is moving in the other room.",
            "The air feels different now.",
            "I think someone is watching.",
            "The shadows seem to be shifting.",
            "There's a rhythm to the silence.",
            "I can feel the presence of something else.",
            "The house is breathing.",
            "Something is not right here.",
            "I hear whispers in the walls.",
            "The darkness is speaking.",
            "There's something behind the door.",
            "The silence is too perfect.",
            "I can sense movement without sound.",
            "The air itself seems to be listening.",
            "Something is waiting in the corner.",
            "The shadows are alive.",
            "I hear voices that aren't there.",
            "The house knows we're here."
        ]
        
        # Setup FastAPI routes
        self.setup_routes()
        
        # Setup MQTT client
        self.setup_mqtt()
    
    def setup_routes(self):
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            return HealthResponse(
                status="healthy" if self.running else "starting",
                mqtt_connected=self.connected,
                transcripts_generated=self.transcripts_generated,
                uptime_seconds=time.time() - self.start_time
            )
        
        @self.app.get("/")
        async def root():
            return {"service": "mock_audio_bridge", "status": "running"}
    
    def setup_mqtt(self):
        """Setup MQTT client"""
        import uuid
        client_id = f"wm-mock-audio-{uuid.uuid4().hex[:8]}"
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_publish = self._on_publish
        self.mqtt_client.on_message = self._on_message # Added for completeness, though not used for mock
        logger.info(f"MQTT client ID: {client_id}")

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback for MQTT connection"""
        if reason_code == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            self.connected = False
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        """Callback for MQTT disconnection"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")
    
    def _on_publish(self, client, userdata, mid, reason_code, properties=None):
        """Callback for MQTT publish"""
        if reason_code == 0:
            logger.debug(f"Message published successfully (mid: {mid})")
        else:
            logger.error(f"Failed to publish message: {reason_code}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for MQTT messages (not used for mock)"""
        logger.debug(f"Received unexpected message on {msg.topic}")
    
    async def connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
            
            # Connect in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            )
            
            # Start the client loop
            await loop.run_in_executor(
                None,
                lambda: self.mqtt_client.loop_start()
            )
            
            # Wait for connection
            for _ in range(30):  # 3 second timeout
                if self.connected:
                    break
                await asyncio.sleep(0.1)
            
            if not self.connected:
                raise Exception("Failed to connect to MQTT broker within timeout")
                
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise
    
    async def publish_transcript(self, text: str):
        """Publish a transcript to MQTT"""
        if not self.connected:
            logger.warning("MQTT not connected, cannot publish transcript")
            return
        
        try:
            transcript = {
                "text": text,
                "confidence": random.uniform(0.7, 0.95),
                "timestamp": int(time.time() * 1000),
                "source": "mock_audio_bridge",
                "ts_ms": int(time.time() * 1000)
            }
            
            topic = f"party/{HOUSE_ID}/llm_agent/transcripts/transcript"
            payload = json.dumps(transcript)
            
            # Publish in executor to avoid blocking
            loop = asyncio.get_event_loop()
            msg_info = await loop.run_in_executor(
                None,
                lambda: self.mqtt_client.publish(topic, payload, qos=1)
            )
            
            # Wait for the message to be published
            await loop.run_in_executor(None, msg_info.wait_for_publish)
            
            if msg_info.is_published():
                logger.info(f"Published transcript to {topic}: {text[:50]}...")
                self.transcripts_generated += 1
            else:
                logger.error(f"Failed to publish transcript: {msg_info.rc}")
                
        except Exception as e:
            logger.error(f"Error publishing transcript: {e}")
    
    async def transcript_loop(self):
        """Main transcript generation loop"""
        logger.info("Starting mock transcript generation loop...")
        
        while self.running:
            try:
                # Generate a random transcript every 10-30 seconds
                await asyncio.sleep(random.randint(10, 30))
                
                if self.connected:
                    transcript = random.choice(self.mock_transcripts)
                    await self.publish_transcript(transcript)
                
            except Exception as e:
                logger.error(f"Error in transcript loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def run(self):
        """Main service loop"""
        logger.info("Starting Mock Audio Bridge Service...")
        
        # Connect to MQTT
        await self.connect_mqtt()
        
        # Start transcript generation
        self.running = True
        try:
            await self.transcript_loop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        self.running = False
        
        if self.mqtt_client:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.mqtt_client.loop_stop()
            )
            await loop.run_in_executor(
                None,
                lambda: self.mqtt_client.disconnect()
            )
        
        logger.info("Cleanup complete")

async def main():
    """Main entry point"""
    service = MockAudioBridge()
    
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
