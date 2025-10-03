"""
Simple metrics capture that manually tracks conversation metrics.
This is a fallback approach when Pipecat's built-in metrics aren't working.
"""

import time
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import InteractionMetrics


class SimpleMetricsCapture:
    """Simple metrics capture that manually tracks conversation metrics."""
    
    def __init__(self, db_session: AsyncSession, message_id: str):
        self.db_session = db_session
        self.message_id = message_id
        self.interaction_id = f"simple_{int(time.time() * 1000)}"
        self.start_times: Dict[str, float] = {}
        
    async def start_interaction(self, service_type: str, service_name: str) -> str:
        """Start tracking an interaction."""
        interaction_key = f"{service_type}_{int(time.time() * 1000)}"
        self.start_times[interaction_key] = time.time()
        logger.info(f"📊 Started {service_type} interaction: {interaction_key}")
        return interaction_key
    
    async def end_interaction(self, interaction_key: str, service_type: str, service_name: str, 
                            metadata: Optional[Dict[str, Any]] = None):
        """End tracking and store metrics."""
        if interaction_key not in self.start_times:
            logger.warning(f"❌ No start time found for interaction {interaction_key}")
            return
        
        duration = time.time() - self.start_times[interaction_key]
        del self.start_times[interaction_key]
        
        logger.info(f"📊 Ending {service_type} interaction: {duration:.3f}s")
        
        # Store the metrics
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=service_name,
            interaction_id=self.interaction_id,
            total_latency=str(round(duration, 6)),
            service_metadata=metadata or {}
        )
    
    async def capture_ttfb_metrics(self, service_type: str, service_name: str, 
                                 ttfb: float, metadata: Optional[Dict[str, Any]] = None):
        """Capture TTFB metrics."""
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=service_name,
            interaction_id=self.interaction_id,
            ttfb=str(round(ttfb, 6)),
            service_metadata=metadata or {}
        )
        logger.info(f"📊 Captured TTFB: {service_type} = {ttfb}s")
    
    async def capture_usage_metrics(self, service_type: str, service_name: str,
                                  prompt_tokens: Optional[int] = None,
                                  completion_tokens: Optional[int] = None,
                                  characters_processed: Optional[int] = None,
                                  metadata: Optional[Dict[str, Any]] = None):
        """Capture usage metrics."""
        await InteractionMetrics.create_metrics(
            db_session=self.db_session,
            message_id=self.message_id,
            service_type=service_type,
            service_name=service_name,
            interaction_id=self.interaction_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            characters_processed=characters_processed,
            service_metadata=metadata or {}
        )
        logger.info(f"📊 Captured usage: {service_type} = {prompt_tokens or 0} prompt, {completion_tokens or 0} completion, {characters_processed or 0} chars")


# Global metrics capture instance
_metrics_capture: Optional[SimpleMetricsCapture] = None


def initialize_simple_metrics_capture(db_session: AsyncSession, message_id: str):
    """Initialize the global metrics capture instance."""
    global _metrics_capture
    _metrics_capture = SimpleMetricsCapture(db_session, message_id)


async def start_interaction(service_type: str, service_name: str) -> str:
    """Start tracking an interaction."""
    global _metrics_capture
    if _metrics_capture:
        return await _metrics_capture.start_interaction(service_type, service_name)
    return ""


async def end_interaction(interaction_key: str, service_type: str, service_name: str, 
                        metadata: Optional[Dict[str, Any]] = None):
    """End tracking and store metrics."""
    global _metrics_capture
    if _metrics_capture:
        await _metrics_capture.end_interaction(interaction_key, service_type, service_name, metadata)


async def capture_ttfb_metrics(service_type: str, service_name: str, 
                             ttfb: float, metadata: Optional[Dict[str, Any]] = None):
    """Capture TTFB metrics."""
    global _metrics_capture
    if _metrics_capture:
        await _metrics_capture.capture_ttfb_metrics(service_type, service_name, ttfb, metadata)


async def capture_usage_metrics(service_type: str, service_name: str,
                              prompt_tokens: Optional[int] = None,
                              completion_tokens: Optional[int] = None,
                              characters_processed: Optional[int] = None,
                              metadata: Optional[Dict[str, Any]] = None):
    """Capture usage metrics."""
    global _metrics_capture
    if _metrics_capture:
        await _metrics_capture.capture_usage_metrics(service_type, service_name, prompt_tokens, completion_tokens, characters_processed, metadata)
