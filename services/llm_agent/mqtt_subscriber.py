"""
MQTT Subscriber Module

Handles subscribing to sensor data and publishing observations.
"""

import asyncio
import json
import logging
import time
from typing import Callable, Dict, Any, Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MQTTSubscriber:
    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        house_id: str = "houseA",
        on_message: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        self.broker = broker
        self.port = port
        self.house_id = house_id
        self.on_message_callback = on_message
        self.connected = False
        
        # MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        logger.info(f"MQTT subscriber initialized: {broker}:{port}, house={house_id}")
    
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback for MQTT connection"""
        if reason_code == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
            
            # Subscribe to sensor data topics
            sensor_topic = f"party/{self.house_id}/+/+/+"
            client.subscribe(sensor_topic, qos=1)
            logger.info(f"Subscribed to sensor topics: {sensor_topic}")
            
        else:
            self.connected = False
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        """Callback for MQTT disconnection"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for MQTT messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            logger.debug(f"Received message on {topic}: {payload}")
            
            # Call the message handler
            if self.on_message_callback:
                self.on_message_callback(topic, payload)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_publish(self, client, userdata, mid, reason_code, properties=None):
        """Callback for MQTT publish"""
        if reason_code == 0:
            logger.debug(f"Message published successfully (mid: {mid})")
        else:
            logger.error(f"Failed to publish message: {reason_code}")
    
    async def connect(self):
        """Connect to MQTT broker"""
        try:
            # Connect in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.connect(self.broker, self.port, 60)
            )
            
            # Start the client loop
            await loop.run_in_executor(
                None,
                lambda: self.client.loop_start()
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
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.loop_stop()
            )
            await loop.run_in_executor(
                None,
                lambda: self.client.disconnect()
            )
            self.connected = False
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker"""
        return self.connected
    
    async def publish_observation(self, observation: Dict[str, Any]):
        """Publish an observation to MQTT"""
        if not self.connected:
            logger.warning("MQTT not connected, cannot publish observation")
            return
        
        try:
            # Add timestamp
            observation["ts_ms"] = int(time.time() * 1000)
            
            # Publish to topic
            topic = f"party/{self.house_id}/llm_agent/observations/observation"
            payload = json.dumps(observation)
            
            # Publish in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.publish(topic, payload, qos=1)
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published observation to {topic}")
            else:
                logger.error(f"Failed to publish observation: {result.rc}")
                
        except Exception as e:
            logger.error(f"Error publishing observation: {e}")
    
    async def publish_heartbeat(self):
        """Publish heartbeat to MQTT"""
        if not self.connected:
            return
        
        try:
            message = {
                "service": "llm_agent",
                "status": "running",
                "ts_ms": int(time.time() * 1000)
            }
            
            topic = f"party/{self.house_id}/llm_agent/sys/heartbeat"
            payload = json.dumps(message)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.publish(topic, payload, qos=1)
            )
            
        except Exception as e:
            logger.error(f"Error publishing heartbeat: {e}")
