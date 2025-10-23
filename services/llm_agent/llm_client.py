"""
LLM Client Module

Handles communication with OpenAI and Anthropic APIs for generating observations.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-3.5-turbo",
        openai_api_key: str = "",
        anthropic_api_key: str = ""
    ):
        self.provider = provider.lower()
        self.model = model
        self.connected = False
        
        # Initialize clients
        if self.provider == "openai" and openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            logger.info(f"OpenAI client initialized with model {model}")
        elif self.provider == "anthropic" and anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)
            logger.info(f"Anthropic client initialized with model {model}")
        else:
            logger.warning(f"No API key provided for {provider}")
    
    async def test_connection(self) -> bool:
        """Test connection to LLM service"""
        try:
            if self.provider == "openai" and hasattr(self, 'openai_client'):
                # Test with a simple completion
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                self.connected = True
                logger.info("OpenAI connection successful")
                return True
                
            elif self.provider == "anthropic" and hasattr(self, 'anthropic_client'):
                # Test with a simple message
                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                self.connected = True
                logger.info("Anthropic connection successful")
                return True
            else:
                logger.warning("No valid client available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to LLM service: {e}")
            self.connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to LLM service"""
        return self.connected
    
    async def generate_text(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """Generate text using the configured LLM"""
        if not self.connected:
            logger.warning("LLM client not connected")
            return None
        
        try:
            if self.provider == "openai" and hasattr(self, 'openai_client'):
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.8
                )
                return response.choices[0].message.content.strip()
                
            elif self.provider == "anthropic" and hasattr(self, 'anthropic_client'):
                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            else:
                logger.error("No valid client available")
                return None
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return None
    
    async def generate_observation(self, sensor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate an unsettling observation from sensor data"""
        if not self.connected:
            return None
        
        # Create prompt for observation generation
        prompt = self._create_observation_prompt(sensor_data)
        
        # Generate text
        text = await self.generate_text(prompt, max_tokens=150)
        
        if text:
            return {
                "text": text,
                "confidence": 0.85,  # LLM observations are inherently uncertain
                "source": "llm_agent",
                "model": self.model,
                "provider": self.provider,
                "timestamp": asyncio.get_event_loop().time()
            }
        
        return None
    
    def _create_observation_prompt(self, sensor_data: Dict[str, Any]) -> str:
        """Create a prompt for generating unsettling observations"""
        
        # Analyze sensor data
        analysis = self._analyze_sensor_data(sensor_data)
        
        prompt = f"""You are an unreliable narrator observing a party through various sensors. Generate a brief, unsettling observation about what might be happening based on this sensor data:

{analysis}

Generate a 1-2 sentence observation that is:
- Vaguely unsettling or mysterious
- Based on the sensor data but not literally describing it
- Written in a detached, observational tone
- Slightly ominous or foreboding
- Appropriate for a party atmosphere

Examples of good observations:
- "The patterns suggest something is moving between rooms that shouldn't be there."
- "The audio signatures don't match what should be happening at this hour."
- "There's a rhythm to the activity that feels... intentional."

Generate only the observation, no additional text:"""
        
        return prompt
    
    def _analyze_sensor_data(self, sensor_data: Dict[str, Any]) -> str:
        """Analyze sensor data and create a summary"""
        if not sensor_data:
            return "No sensor data available."
        
        analysis_parts = []
        
        for node, domains in sensor_data.items():
            analysis_parts.append(f"Node {node}:")
            
            for domain, signals in domains.items():
                if signals:
                    analysis_parts.append(f"  {domain}: {len(signals)} signals")
                    
                    # Add some specific details
                    for signal, data in signals.items():
                        if isinstance(data, dict) and 'ts_ms' in data:
                            age_seconds = (asyncio.get_event_loop().time() * 1000 - data['ts_ms']) / 1000
                            analysis_parts.append(f"    {signal}: {age_seconds:.1f}s ago")
        
        return "\n".join(analysis_parts) if analysis_parts else "No recent sensor activity."
    
    async def close(self):
        """Close the LLM client"""
        self.connected = False
        logger.info("LLM client closed")
