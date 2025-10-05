"""
DEPRECATED: Metrics capture utility for tracking latency and usage metrics in real-time conversations.

This module is deprecated in favor of the simpler log-based metrics approach
in bots/log_based_metrics.py. The log-based approach is more reliable and
easier to maintain.

Use bots/log_based_metrics.py for new metrics collection needs.

Original purpose: Based on Deepgram and Pipecat metrics documentation.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, Optional, List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import InteractionMetrics


class MetricsCollector:
    """
    DEPRECATED: Collects and stores interaction metrics for different services.
    
    This class is deprecated. Use LogBasedMetricsExtractor from bots/log_based_metrics.py instead.
    """
    
    def __init__(self, db_session: AsyncSession, message_id: str):
        logger.warning("⚠️ MetricsCollector is deprecated. Use LogBasedMetricsExtractor instead.")
        self.db_session = db_session
        self.message_id = message_id
        self.interaction_id = str(uuid.uuid4())
        self.metrics_buffer: List[Dict[str, Any]] = []
        
    async def capture_ttfb_metrics(
        self,
        service_type: str,
        service_name: str,
        ttfb: float,
        processing_time: Optional[float] = None,
        service_metadata: Optional[Dict[str, Any]] = None
    ):
        """Capture Time to First Byte metrics for a service."""
        try:
            logger.info(f"📊 Attempting to capture TTFB metrics for {service_name}: {ttfb}s")
            await InteractionMetrics.create_metrics(
                db_session=self.db_session,
                message_id=self.message_id,
                service_type=service_type,
                service_name=service_name,
                interaction_id=self.interaction_id,
                ttfb=str(round(ttfb, 6)),
                processing_time=str(round(processing_time, 6)) if processing_time else None,
                service_metadata=service_metadata
            )
            logger.info(f"📊 Successfully captured TTFB metrics for {service_name}: {ttfb}s")
        except Exception as e:
            logger.error(f"❌ Failed to capture TTFB metrics: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    async def capture_usage_metrics(
        self,
        service_type: str,
        service_name: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        characters_processed: Optional[int] = None,
        service_metadata: Optional[Dict[str, Any]] = None
    ):
        """Capture usage metrics (tokens, characters) for a service."""
        try:
            await InteractionMetrics.create_metrics(
                db_session=self.db_session,
                message_id=self.message_id,
                service_type=service_type,
                service_name=service_name,
                interaction_id=self.interaction_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                characters_processed=characters_processed,
                service_metadata=service_metadata
            )
            logger.debug(f"📊 Captured usage metrics for {service_name}: {prompt_tokens or 0} prompt, {completion_tokens or 0} completion tokens")
        except Exception as e:
            logger.error(f"❌ Failed to capture usage metrics: {e}")
    
    async def capture_latency_metrics(
        self,
        service_type: str,
        service_name: str,
        total_latency: float,
        ttfb: Optional[float] = None,
        processing_time: Optional[float] = None,
        service_metadata: Optional[Dict[str, Any]] = None
    ):
        """Capture comprehensive latency metrics for a service."""
        try:
            await InteractionMetrics.create_metrics(
                db_session=self.db_session,
                message_id=self.message_id,
                service_type=service_type,
                service_name=service_name,
                interaction_id=self.interaction_id,
                ttfb=str(round(ttfb, 6)) if ttfb else None,
                processing_time=str(round(processing_time, 6)) if processing_time else None,
                total_latency=str(round(total_latency, 6)),
                service_metadata=service_metadata
            )
            logger.debug(f"📊 Captured latency metrics for {service_name}: {total_latency}s total")
        except Exception as e:
            logger.error(f"❌ Failed to capture latency metrics: {e}")


class ServiceMetricsTracker:
    """Tracks metrics for individual services during conversation flow."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.start_times: Dict[str, float] = {}
        self.interaction_counters: Dict[str, int] = {}
    
    def start_interaction(self, service_name: str) -> str:
        """Start tracking an interaction and return interaction ID."""
        interaction_key = f"{service_name}_{int(time.time() * 1000)}"
        self.start_times[interaction_key] = time.time()
        logger.info(f"📊 Started tracking interaction: {interaction_key}")
        return interaction_key
    
    def end_interaction(self, interaction_key: str, service_type: str, service_name: str, 
                       service_metadata: Optional[Dict[str, Any]] = None):
        """End tracking and capture metrics."""
        if interaction_key not in self.start_times:
            logger.warning(f"❌ No start time found for interaction {interaction_key}")
            return
        
        duration = time.time() - self.start_times[interaction_key]
        del self.start_times[interaction_key]
        
        logger.info(f"📊 Ending interaction {interaction_key}: {duration:.3f}s latency")
        
        # Capture the metrics asynchronously
        asyncio.create_task(
            self.metrics_collector.capture_latency_metrics(
                service_type=service_type,
                service_name=service_name,
                total_latency=duration,
                service_metadata=service_metadata
            )
        )


def create_metrics_collector(db_session: AsyncSession, message_id: str) -> MetricsCollector:
    """Factory function to create a metrics collector."""
    return MetricsCollector(db_session, message_id)


def create_service_tracker(metrics_collector: MetricsCollector) -> ServiceMetricsTracker:
    """Factory function to create a service metrics tracker."""
    return ServiceMetricsTracker(metrics_collector)
