#!/usr/bin/env python3
"""
LLM Agent Service

Generates unsettling observations from sensor data using OpenAI or Anthropic APIs.
Designed to create an unreliable narrator aesthetic for the party interface.
"""

import asyncio
import json
import logging
import os
import random
import signal
import sys
import time
from typing import Dict, List, Optional, Any

import paho.mqtt.client as mqtt
from fastapi import FastAPI
from pydantic import BaseModel

from llm_client import LLMClient
from mqtt_subscriber import MQTTSubscriber
from observation_generator import ObservationGenerator

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
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
OBSERVATION_INTERVAL_MIN = int(os.getenv('OBSERVATION_INTERVAL_MIN', '2'))
OBSERVATION_INTERVAL_MAX = int(os.getenv('OBSERVATION_INTERVAL_MAX', '5'))

class HealthResponse(BaseModel):
    status: str
    llm_connected: bool
    mqtt_connected: bool
    observations_generated: int
    uptime_seconds: float

class LLMAgentService:
    def __init__(self):
        self.app = FastAPI(title="LLM Agent Service")
        self.start_time = time.time()
        self.running = False
        self.observations_generated = 0
        
        # Components
        self.llm_client: Optional[LLMClient] = None
        self.mqtt_subscriber: Optional[MQTTSubscriber] = None
        self.observation_generator: Optional[ObservationGenerator] = None
        
        # Sensor data cache
        self.sensor_data: Dict[str, Any] = {}
        self.last_observation_time = 0
        
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
                llm_connected=self.llm_client is not None and self.llm_client.is_connected(),
                mqtt_connected=self.mqtt_subscriber is not None and self.mqtt_subscriber.is_connected(),
                observations_generated=self.observations_generated,
                uptime_seconds=time.time() - self.start_time
            )
        
        @self.app.get("/")
        async def root():
            return {"service": "llm_agent", "status": "running"}
        
        @self.app.get("/sensor-data")
        async def get_sensor_data():
            return self.sensor_data
        
        @self.app.post("/generate-observation")
        async def generate_observation():
            if not self.observation_generator:
                return {"error": "Observation generator not initialized"}
            
            observation = await self.observation_generator.generate_observation(self.sensor_data)
            if observation:
                self.observations_generated += 1
                return {"observation": observation}
            else:
                return {"error": "Failed to generate observation"}
    
    def signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def initialize_components(self):
        """Initialize all service components"""
        try:
            # Initialize LLM client
            logger.info(f"Initializing LLM client ({LLM_PROVIDER})...")
            self.llm_client = LLMClient(
                provider=LLM_PROVIDER,
                model=LLM_MODEL,
                openai_api_key=OPENAI_API_KEY,
                anthropic_api_key=ANTHROPIC_API_KEY
            )
            await self.llm_client.test_connection()
            
            # Initialize MQTT subscriber
            logger.info("Initializing MQTT subscriber...")
            self.mqtt_subscriber = MQTTSubscriber(
                broker=MQTT_BROKER,
                port=MQTT_PORT,
                house_id=HOUSE_ID,
                on_message=self.handle_sensor_data
            )
            await self.mqtt_subscriber.connect()
            
            # Initialize observation generator
            logger.info("Initializing observation generator...")
            self.observation_generator = ObservationGenerator(
                llm_client=self.llm_client,
                house_id=HOUSE_ID
            )
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    def handle_sensor_data(self, topic: str, payload: Dict[str, Any]):
        """Handle incoming sensor data from MQTT"""
        try:
            # Extract node and domain from topic
            # Format: party/<house>/<node>/<domain>/<signal>
            topic_parts = topic.split('/')
            if len(topic_parts) >= 5:
                node = topic_parts[2]
                domain = topic_parts[3]
                signal = topic_parts[4]
                
                # Update sensor data cache
                if node not in self.sensor_data:
                    self.sensor_data[node] = {}
                if domain not in self.sensor_data[node]:
                    self.sensor_data[node][domain] = {}
                
                self.sensor_data[node][domain][signal] = payload
                
                logger.debug(f"Updated sensor data for {node}/{domain}/{signal}")
                
        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")
    
    async def observation_loop(self):
        """Main observation generation loop"""
        logger.info("Starting observation generation loop...")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check if it's time for a new observation
                time_since_last = current_time - self.last_observation_time
                interval = random.randint(OBSERVATION_INTERVAL_MIN * 60, OBSERVATION_INTERVAL_MAX * 60)
                
                if time_since_last >= interval and self.sensor_data:
                    # Generate observation
                    observation = await self.observation_generator.generate_observation(self.sensor_data)
                    
                    if observation:
                        # Publish observation to MQTT
                        await self.mqtt_subscriber.publish_observation(observation)
                        self.observations_generated += 1
                        self.last_observation_time = current_time
                        
                        logger.info(f"Generated observation: {observation['text'][:100]}...")
                    else:
                        logger.warning("Failed to generate observation")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in observation loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def run(self):
        """Main service loop"""
        logger.info("Starting LLM Agent Service...")
        
        # Initialize components
        if not await self.initialize_components():
            logger.error("Failed to initialize components, exiting")
            return
        
        # Start observation generation
        self.running = True
        try:
            # Start observation loop
            await self.observation_loop()
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        self.running = False
        
        if self.mqtt_subscriber:
            await self.mqtt_subscriber.disconnect()
        
        if self.llm_client:
            await self.llm_client.close()
        
        logger.info("Cleanup complete")

async def main():
    """Main entry point"""
    service = LLMAgentService()
    
    # Start FastAPI server in background
    import uvicorn
    config = uvicorn.Config(
        service.app,
        host="0.0.0.0",
        port=8000,
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
