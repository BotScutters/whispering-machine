"""
Observation Generator Module

Generates unsettling observations from sensor data using LLM.
"""

import asyncio
import logging
import random
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ObservationGenerator:
    def __init__(
        self,
        llm_client,
        house_id: str = "houseA"
    ):
        self.llm_client = llm_client
        self.house_id = house_id
        
        # Observation templates for fallback
        self.fallback_observations = [
            "The patterns in the data suggest something is not quite right.",
            "There's a rhythm to the activity that feels... intentional.",
            "The sensor readings don't match what should be happening.",
            "Something is moving between rooms that shouldn't be there.",
            "The audio signatures are inconsistent with the expected patterns.",
            "There's a pattern emerging that wasn't there before.",
            "The data suggests activity in areas that should be quiet.",
            "Something is interfering with the normal sensor readings.",
            "The patterns indicate movement that doesn't match the expected flow.",
            "There's a disturbance in the usual data patterns."
        ]
        
        logger.info("Observation generator initialized")
    
    async def generate_observation(self, sensor_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate an unsettling observation from sensor data"""
        try:
            # Try to generate with LLM first
            if self.llm_client and self.llm_client.is_connected():
                observation = await self.llm_client.generate_observation(sensor_data)
                if observation:
                    return observation
            
            # Fallback to template-based generation
            return await self._generate_fallback_observation(sensor_data)
            
        except Exception as e:
            logger.error(f"Error generating observation: {e}")
            return None
    
    async def _generate_fallback_observation(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate observation using fallback templates"""
        
        # Analyze sensor data for context
        context = self._analyze_sensor_context(sensor_data)
        
        # Select appropriate template
        template = random.choice(self.fallback_observations)
        
        # Add context-specific modifications
        if context.get('recent_activity'):
            template = f"The recent activity suggests {template.lower()}"
        elif context.get('silence'):
            template = f"Despite the apparent silence, {template.lower()}"
        elif context.get('multiple_nodes'):
            template = f"Across multiple sensors, {template.lower()}"
        
        return {
            "text": template,
            "confidence": 0.7,  # Lower confidence for fallback
            "source": "fallback_generator",
            "model": "template",
            "provider": "fallback",
            "timestamp": asyncio.get_event_loop().time(),
            "context": context
        }
    
    def _analyze_sensor_context(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sensor data to provide context for observation generation"""
        context = {
            "recent_activity": False,
            "silence": True,
            "multiple_nodes": False,
            "node_count": 0,
            "domain_count": 0,
            "signal_count": 0
        }
        
        if not sensor_data:
            return context
        
        current_time = asyncio.get_event_loop().time() * 1000
        recent_threshold = 30000  # 30 seconds
        
        context["node_count"] = len(sensor_data)
        context["multiple_nodes"] = context["node_count"] > 1
        
        for node, domains in sensor_data.items():
            context["domain_count"] += len(domains)
            
            for domain, signals in domains.items():
                context["signal_count"] += len(signals)
                
                for signal, data in signals.items():
                    if isinstance(data, dict) and 'ts_ms' in data:
                        age_ms = current_time - data['ts_ms']
                        if age_ms < recent_threshold:
                            context["recent_activity"] = True
                            context["silence"] = False
        
        return context
    
    def _get_observation_prompts(self) -> List[str]:
        """Get different types of observation prompts"""
        return [
            "Generate a brief, unsettling observation about what might be happening based on this sensor data. Make it mysterious and foreboding.",
            "What does this sensor data suggest is happening? Write a creepy, observational comment.",
            "Based on these sensor readings, what concerning pattern do you notice? Be ominous and vague.",
            "What unsettling conclusion can be drawn from this sensor activity? Write it as an unreliable narrator would.",
            "What does this data pattern suggest that shouldn't be happening? Make it mysterious and disturbing."
        ]
    
    async def generate_multiple_observations(self, sensor_data: Dict[str, Any], count: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple observations for variety"""
        observations = []
        
        for _ in range(count):
            observation = await self.generate_observation(sensor_data)
            if observation:
                observations.append(observation)
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
        
        return observations
    
    def get_observation_stats(self) -> Dict[str, Any]:
        """Get statistics about observation generation"""
        return {
            "fallback_observations_count": len(self.fallback_observations),
            "llm_available": self.llm_client is not None and self.llm_client.is_connected(),
            "house_id": self.house_id
        }
