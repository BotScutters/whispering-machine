"""
MQTT Publisher Module

Handles publishing transcript data to MQTT broker.
"""

import asyncio
import json
import logging
import time
from typing import Optional

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MQTTPublisher:
    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        house_id: str = "houseA"
    ):
        self.broker = broker
        self.port = port
        self.house_id = house_id
        self.connected = False
        
        # MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        logger.info(f"MQTT publisher initialized: {broker}:{port}, house={house_id}")
    
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
    
    async def publish_transcript(
        self,
        text: str,
        confidence: float,
        duration_ms: int,
        model: str,
        trigger: str
    ):
        """Publish transcript to MQTT"""
        if not self.connected:
            logger.warning("MQTT not connected, cannot publish transcript")
            return
        
        try:
            # Create transcript message
            message = {
                "text": text,
                "confidence": confidence,
                "duration_ms": duration_ms,
                "model": model,
                "trigger": trigger,
                "ts_ms": int(time.time() * 1000)
            }
            
            # Publish to topic
            topic = f"party/{self.house_id}/macbook/speech/transcript"
            payload = json.dumps(message)
            
            # Publish in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.publish(topic, payload, qos=1)
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published transcript to {topic}")
            else:
                logger.error(f"Failed to publish transcript: {result.rc}")
                
        except Exception as e:
            logger.error(f"Error publishing transcript: {e}")
    
    async def publish_audio_features(
        self,
        rms: float,
        zcr: float,
        low_freq: float,
        mid_freq: float,
        high_freq: float
    ):
        """Publish audio features to MQTT"""
        if not self.connected:
            logger.warning("MQTT not connected, cannot publish audio features")
            return
        
        try:
            # Create audio features message
            message = {
                "rms": rms,
                "zcr": zcr,
                "low_freq": low_freq,
                "mid_freq": mid_freq,
                "high_freq": high_freq,
                "ts_ms": int(time.time() * 1000)
            }
            
            # Publish to topic
            topic = f"party/{self.house_id}/macbook/audio/features"
            payload = json.dumps(message)
            
            # Publish in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.publish(topic, payload, qos=1)
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published audio features to {topic}")
            else:
                logger.error(f"Failed to publish audio features: {result.rc}")
                
        except Exception as e:
            logger.error(f"Error publishing audio features: {e}")
    
    async def publish_heartbeat(self):
        """Publish heartbeat to MQTT"""
        if not self.connected:
            return
        
        try:
            message = {
                "service": "audio_bridge",
                "status": "running",
                "ts_ms": int(time.time() * 1000)
            }
            
            topic = f"party/{self.house_id}/macbook/sys/heartbeat"
            payload = json.dumps(message)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.publish(topic, payload, qos=1)
            )
            
        except Exception as e:
            logger.error(f"Error publishing heartbeat: {e}")
