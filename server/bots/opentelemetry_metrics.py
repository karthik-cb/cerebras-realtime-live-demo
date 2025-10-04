"""
OpenTelemetry Metrics Integration for Pipecat
Uses Pipecat's built-in OpenTelemetry support for comprehensive metrics collection.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import InteractionMetrics, Message
from common.database import default_session_factory


class OpenTelemetryMetricsCollector:
    """Collects metrics from OpenTelemetry traces and stores them in the database."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.metrics_buffer: List[Dict[str, Any]] = []
        
    async def collect_metrics_from_traces(self, db_session: AsyncSession, message_id: str):
        """Collect metrics from OpenTelemetry traces and store them."""
        try:
            # For now, we'll implement a simple approach that works with Pipecat's built-in metrics
            # In a full implementation, you would:
            # 1. Set up OpenTelemetry exporters (Jaeger, etc.)
            # 2. Configure span processors to capture metrics
            # 3. Extract metrics from trace data
            
            # Since we're using Pipecat's built-in metrics logging, we can still use that
            # but with better structure through OpenTelemetry
            logger.info(f"📊 Collecting OpenTelemetry metrics for conversation {self.conversation_id}")
            
            # For now, return empty list - this will be implemented with actual OpenTelemetry integration
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to collect OpenTelemetry metrics: {e}")
            return []


def setup_conversation_tracing(conversation_id: str):
    """Set up OpenTelemetry tracing for a conversation."""
    try:
        # Check if OpenTelemetry is available
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from pipecat.utils.tracing.setup import setup_tracing
        except ImportError:
            logger.warning("📊 OpenTelemetry not available - falling back to basic metrics")
            return
        
        # Set up OpenTelemetry tracing
        # For development, we can use console export
        setup_tracing(
            service_name="cerebras-voice-demo",
            exporter=None,  # Will use console export for now
            console_export=True,  # Enable console export for debugging
        )
        
        logger.info(f"📊 OpenTelemetry tracing configured for conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup OpenTelemetry tracing: {e}")


async def extract_metrics_from_opentelemetry(
    conversation_id: str, 
    message_id: str, 
    db_session: Optional[AsyncSession] = None
) -> List[Dict[str, Any]]:
    """Extract metrics from OpenTelemetry traces."""
    try:
        collector = OpenTelemetryMetricsCollector(conversation_id)
        
        if db_session:
            return await collector.collect_metrics_from_traces(db_session, message_id)
        else:
            async with default_session_factory() as session:
                return await collector.collect_metrics_from_traces(session, message_id)
                
    except Exception as e:
        logger.error(f"❌ Failed to extract OpenTelemetry metrics: {e}")
        return []


# Alternative approach: Use Pipecat's built-in metrics with better structure
class PipecatMetricsCollector:
    """Collects metrics using Pipecat's built-in metrics system."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        
    async def collect_metrics(self, db_session: AsyncSession, message_id: str):
        """Collect metrics from Pipecat's built-in metrics system."""
        try:
            # For now, return empty metrics to avoid hardcoded data
            # TODO: Implement real OpenTelemetry metrics collection
            logger.warning(f"📊 PipecatMetricsCollector returning empty metrics for conversation {self.conversation_id} - this needs real OpenTelemetry integration")
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to collect Pipecat metrics: {e}")
            return []


async def collect_pipecat_metrics(
    conversation_id: str,
    message_id: str, 
    db_session: Optional[AsyncSession] = None
):
    """Collect metrics using Pipecat's built-in system."""
    try:
        collector = PipecatMetricsCollector(conversation_id)
        
        if db_session:
            return await collector.collect_metrics(db_session, message_id)
        else:
            async with default_session_factory() as session:
                return await collector.collect_metrics(session, message_id)
                
    except Exception as e:
        logger.error(f"❌ Failed to collect Pipecat metrics: {e}")
        return []
