"""
Conversation metrics generation utilities.
Handles automatic generation of conversation-level metrics summaries.
"""

import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from common.database import default_session_factory
from common.models import Message, InteractionMetrics
from sqlalchemy import select
from loguru import logger


async def generate_conversation_metrics_summary(
    conversation_id: str, 
    db_session: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Generate a conversation-level metrics summary for the given conversation.
    
    Args:
        conversation_id: The ID of the conversation to generate metrics for
        db_session: Optional database session (if None, creates a new one)
    
    Returns:
        Dictionary containing the metrics summary
    """
    async def _generate_with_session(session: AsyncSession) -> Dict[str, Any]:
        # Get all messages for the conversation
        result = await session.execute(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.message_number)
        )
        messages = result.scalars().all()
        
        # Initialize metrics summary
        conversation_metrics = {
            "total_messages": len(messages),
            "total_latency": 0.0,
            "total_tokens": 0,
            "service_breakdown": {
                "stt": {"count": 0, "total_latency": 0.0, "avg_latency": 0.0},
                "llm": {"count": 0, "total_latency": 0.0, "avg_latency": 0.0, "total_tokens": 0},
                "tts": {"count": 0, "total_latency": 0.0, "avg_latency": 0.0, "total_characters": 0}
            }
        }
        
        # Get all metrics for this conversation
        message_ids = [str(msg.message_id) for msg in messages]
        if message_ids:
            result = await session.execute(
                select(InteractionMetrics).where(InteractionMetrics.message_id.in_(message_ids))
            )
            metrics = result.scalars().all()
            
            # Aggregate metrics from all messages
            for metric in metrics:
                service_type = metric.service_type
                if service_type in conversation_metrics["service_breakdown"]:
                    # Update service breakdown
                    service_data = conversation_metrics["service_breakdown"][service_type]
                    service_data["count"] += 1
                    
                    # Prefer total_latency, fall back to processing_time
                    latency = None
                    if metric.total_latency:
                        latency = float(metric.total_latency)
                    elif metric.processing_time:
                        latency = float(metric.processing_time)
                    if latency is not None:
                        service_data["total_latency"] += latency
                        conversation_metrics["total_latency"] += latency
                    
                    if metric.prompt_tokens:
                        conversation_metrics["total_tokens"] += metric.prompt_tokens
                        service_data["total_tokens"] += metric.prompt_tokens
                    
                    if metric.completion_tokens:
                        conversation_metrics["total_tokens"] += metric.completion_tokens
                        service_data["total_tokens"] += metric.completion_tokens
                    
                    if metric.characters_processed:
                        service_data["total_characters"] += metric.characters_processed
        
        # Calculate averages
        for service_type, data in conversation_metrics["service_breakdown"].items():
            if data["count"] > 0:
                data["avg_latency"] = data["total_latency"] / data["count"]
        
        logger.info(f"📊 Generated conversation metrics for {conversation_id}: {conversation_metrics['total_messages']} messages, {conversation_metrics['total_latency']:.2f}s total latency")
        return conversation_metrics
    
    if db_session:
        return await _generate_with_session(db_session)
    else:
        async with default_session_factory() as session:
            return await _generate_with_session(session)


async def store_conversation_metrics_summary(
    conversation_id: str,
    metrics_summary: Dict[str, Any],
    db_session: Optional[AsyncSession] = None
) -> None:
    """
    Store the conversation metrics summary in the database.
    This could be stored in a separate table or as metadata on the conversation.
    
    For now, we'll store it as a special message in the conversation.
    """
    async def _store_with_session(session: AsyncSession) -> None:
        # Create a special system message to store the metrics summary
        from common.models import Message
        import json
        import uuid
        from datetime import datetime
        
        # Check if metrics summary already exists
        existing_result = await session.execute(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.content.op("->>")("role") == "metrics_summary"
            )
        )
        existing_message = existing_result.scalar_one_or_none()
        
        if existing_message:
            # Update existing metrics summary
            existing_message.content = {
                "role": "metrics_summary",
                "content": json.dumps(metrics_summary)
            }
            existing_message.updated_at = datetime.utcnow()
            logger.info(f"📊 Updated existing metrics summary for conversation {conversation_id}")
        else:
            # Create new metrics summary message
            metrics_message = Message(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                message_number=999999,  # High number to ensure it's at the end
                content={
                    "role": "metrics_summary",
                    "content": json.dumps(metrics_summary)
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(metrics_message)
            logger.info(f"📊 Stored new metrics summary for conversation {conversation_id}")
        
        await session.commit()
    
    if db_session:
        await _store_with_session(db_session)
    else:
        async with default_session_factory() as session:
            await _store_with_session(session)


async def generate_and_store_conversation_metrics(
    conversation_id: str,
    db_session: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Generate and store conversation metrics summary using log extraction.
    
    Args:
        conversation_id: The ID of the conversation
        db_session: Optional database session
    
    Returns:
        The generated metrics summary
    """
    logger.info(f"📊 Generating conversation metrics for {conversation_id}")
    
    # Try to extract metrics using OpenTelemetry/Pipecat built-in metrics
    await _extract_metrics_from_opentelemetry(conversation_id, db_session)
    
    # Generate metrics
    metrics_summary = await generate_conversation_metrics_summary(conversation_id, db_session)
    
    # Store metrics
    await store_conversation_metrics_summary(conversation_id, metrics_summary, db_session)
    
    return metrics_summary


async def extract_metrics_for_conversation(conversation_id: str, db_session: Optional[AsyncSession] = None):
    """
    Extract metrics for a conversation using the log-based approach.
    
    This is the primary metrics collection method for the demo. It creates realistic
    sample metrics distributed across conversation turns to simulate OpenTelemetry data.
    
    Args:
        conversation_id: The conversation ID to extract metrics for
        db_session: Optional database session
    """
    try:
        import os
        from bots.log_based_metrics import LogBasedMetricsExtractor

        # Only run when tracing is enabled
        if os.getenv("ENABLE_TRACING", "0") in ("0", "false", "False", ""):
            return

        async def _run_with_session(session: AsyncSession):
            # Create extractor and let it distribute metrics across all messages
            extractor = LogBasedMetricsExtractor(conversation_id)
            # Pass a dummy message_id since the extractor will find all messages itself
            created = await extractor.extract_metrics_from_logs(session, "dummy")
            if created:
                logger.info(f"📊 Persisted {len(created)} distributed log-based metrics for conversation {conversation_id}")

        if db_session:
            await _run_with_session(db_session)
        else:
            async with default_session_factory() as session:
                await _run_with_session(session)
        return

    except Exception as e:
        logger.error(f"❌ Failed to collect log-based metrics: {e}")


# DEPRECATED: Use extract_metrics_for_conversation instead
async def _extract_metrics_from_opentelemetry(conversation_id: str, db_session: Optional[AsyncSession] = None):
    """
    DEPRECATED: Use extract_metrics_for_conversation instead.
    
    This function is kept for backward compatibility but is deprecated.
    """
    logger.warning("⚠️ _extract_metrics_from_opentelemetry is deprecated. Use extract_metrics_for_conversation instead.")
    return await extract_metrics_for_conversation(conversation_id, db_session)
