"""
DEPRECATED: Pipecat metrics capture utility that intercepts logged metrics and stores them in the database.

This module is deprecated in favor of the simpler log-based metrics approach
in bots/log_based_metrics.py. The log-based approach is more reliable and
easier to maintain.

Use bots/log_based_metrics.py for new metrics collection needs.

Original purpose: Based on Pipecat's built-in metrics logging format.
"""

import re
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import InteractionMetrics


class PipecatMetricsCapture:
    """
    DEPRECATED: Captures metrics from Pipecat's built-in logging and stores them in the database.
    
    This class is deprecated. Use LogBasedMetricsExtractor from bots/log_based_metrics.py instead.
    """
    
    def __init__(self, db_session: AsyncSession, message_id: str):
        logger.warning("⚠️ PipecatMetricsCapture is deprecated. Use LogBasedMetricsExtractor instead.")
        self.db_session = db_session
        self.message_id = message_id
        self.interaction_id = f"pipecat_{int(asyncio.get_event_loop().time() * 1000)}"
        
    async def capture_logged_metrics(self, log_message: str):
        """Parse and capture metrics from Pipecat's logged output."""
        try:
            logger.info(f"📊 Attempting to parse log message: {log_message}")
            
            # Parse TTFB metrics: "ServiceName#0 TTFB: 0.8378312587738037"
            ttfb_match = re.search(r'(\w+)Service#\d+ TTFB: ([\d.]+)', log_message)
            if ttfb_match:
                service_name = ttfb_match.group(1)
                ttfb_value = float(ttfb_match.group(2))
                await self._store_ttfb_metrics(service_name, ttfb_value)
                logger.info(f"📊 Captured TTFB: {service_name} = {ttfb_value}s")
            
            # Parse processing time: "ServiceName#0 processing time: 0.0005071163177490234"
            processing_match = re.search(r'(\w+)Service#\d+ processing time: ([\d.]+)', log_message)
            if processing_match:
                service_name = processing_match.group(1)
                processing_time = float(processing_match.group(2))
                await self._store_processing_metrics(service_name, processing_time)
                logger.info(f"📊 Captured processing time: {service_name} = {processing_time}s")
            
            # Parse LLM usage: "ServiceName#0 prompt tokens: 104, completion tokens: 53"
            llm_usage_match = re.search(r'(\w+)Service#\d+ prompt tokens: (\d+), completion tokens: (\d+)', log_message)
            if llm_usage_match:
                service_name = llm_usage_match.group(1)
                prompt_tokens = int(llm_usage_match.group(2))
                completion_tokens = int(llm_usage_match.group(3))
                await self._store_llm_usage_metrics(service_name, prompt_tokens, completion_tokens)
                logger.info(f"📊 Captured LLM usage: {service_name} = {prompt_tokens} prompt, {completion_tokens} completion")
            
            # Parse TTS usage: "ServiceName#0 usage characters: 65"
            tts_usage_match = re.search(r'(\w+)Service#\d+ usage characters: (\d+)', log_message)
            if tts_usage_match:
                service_name = tts_usage_match.group(1)
                characters = int(tts_usage_match.group(2))
                await self._store_tts_usage_metrics(service_name, characters)
                logger.info(f"📊 Captured TTS usage: {service_name} = {characters} characters")
                
        except Exception as e:
            logger.error(f"❌ Failed to parse metrics from log: {e}")
    
    async def _store_ttfb_metrics(self, service_name: str, ttfb: float):
        """Store TTFB metrics."""
        service_type = self._get_service_type(service_name)
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=f"{service_name}Service",
            interaction_id=self.interaction_id,
            ttfb=str(round(ttfb, 6)),
            service_metadata={"source": "pipecat_logs"}
        )
    
    async def _store_processing_metrics(self, service_name: str, processing_time: float):
        """Store processing time metrics."""
        service_type = self._get_service_type(service_name)
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=f"{service_name}Service",
            interaction_id=self.interaction_id,
            processing_time=str(round(processing_time, 6)),
            service_metadata={"source": "pipecat_logs"}
        )
    
    async def _store_llm_usage_metrics(self, service_name: str, prompt_tokens: int, completion_tokens: int):
        """Store LLM usage metrics."""
        service_type = self._get_service_type(service_name)
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=f"{service_name}Service",
            interaction_id=self.interaction_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            service_metadata={"source": "pipecat_logs"}
        )
    
    async def _store_tts_usage_metrics(self, service_name: str, characters: int):
        """Store TTS usage metrics."""
        service_type = self._get_service_type(service_name)
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=f"{service_name}Service",
            interaction_id=self.interaction_id,
            characters_processed=characters,
            service_metadata={"source": "pipecat_logs"}
        )
    
    def _get_service_type(self, service_name: str) -> str:
        """Map service name to service type."""
        service_mapping = {
            "Deepgram": "stt",
            "Cerebras": "llm", 
            "Anthropic": "llm",
            "OpenAI": "llm",
            "Cartesia": "tts",
            "ElevenLabs": "tts",
            "Azure": "tts"
        }
        return service_mapping.get(service_name, "unknown")


# Global metrics capture instance
_metrics_capture: Optional[PipecatMetricsCapture] = None


def initialize_metrics_capture(db_session: AsyncSession, message_id: str):
    """Initialize the global metrics capture instance."""
    global _metrics_capture
    _metrics_capture = PipecatMetricsCapture(db_session, message_id)


async def capture_pipecat_metrics(log_message: str):
    """Capture metrics from a Pipecat log message."""
    global _metrics_capture
    if _metrics_capture:
        await _metrics_capture.capture_logged_metrics(log_message)
