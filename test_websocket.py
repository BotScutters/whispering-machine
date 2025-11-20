#!/usr/bin/env python3
"""
Test WebSocket connection to Party UI
"""
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_party_websocket():
    """Test WebSocket connection to Party UI"""
    try:
        logger.info("Testing WebSocket connection to Party UI...")
        
        # Connect to the party WebSocket endpoint
        uri = "ws://localhost:8000/ws/party"
        logger.info(f"Connecting to: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✅ WebSocket connected successfully!")
            
            # Wait for any messages
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"Received message: {message}")
            except asyncio.TimeoutError:
                logger.info("No messages received within 5 seconds")
            
            # Send a test message
            test_message = {"test": "websocket_test", "timestamp": 1234567890}
            await websocket.send(json.dumps(test_message))
            logger.info("Sent test message")
            
    except Exception as e:
        logger.error(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_party_websocket())




