#!/usr/bin/env python3
"""
Minimal script to query metrics database directly.
Usage: python check_metrics.py
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.database import DatabaseSessionFactory
from common.models import Conversation, Message, InteractionMetrics
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_most_recent_conversation(db: AsyncSession) -> Optional[Conversation]:
    """Get the most recent conversation."""
    result = await db.execute(
        select(Conversation)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_conversation_messages(db: AsyncSession, conversation_id: str):
    """Get all messages for a conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.message_number)
    )
    return result.scalars().all()


async def get_conversation_metrics(db: AsyncSession, conversation_id: str):
    """Get all metrics for a conversation."""
    result = await db.execute(
        select(InteractionMetrics, Message)
        .join(Message, InteractionMetrics.message_id == Message.message_id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.message_number, InteractionMetrics.created_at)
    )
    return result.all()


async def get_metrics_summary(db: AsyncSession, conversation_id: str):
    """Get metrics summary for a conversation."""
    result = await db.execute(
        select(
            func.count(InteractionMetrics.metrics_id).label('total_metrics'),
            func.count(func.distinct(Message.message_id)).label('total_messages'),
            func.count(func.distinct(InteractionMetrics.service_type)).label('service_types')
        )
        .select_from(Message)
        .outerjoin(InteractionMetrics, Message.message_id == InteractionMetrics.message_id)
        .where(Message.conversation_id == conversation_id)
    )
    return result.first()


async def main():
    """Main function to run the metrics check."""
    print("🔍 Checking metrics database...")
    
    # Initialize database
    db_factory = DatabaseSessionFactory()
    await db_factory.initialize_schema()
    
    async with db_factory() as db:
        # 1. Get most recent conversation
        print("\n1. Most recent conversation:")
        conversation = await get_most_recent_conversation(db)
        if not conversation:
            print("❌ No conversations found")
            return
        
        print(f"   ID: {conversation.conversation_id}")
        print(f"   Title: {conversation.title}")
        print(f"   Created: {conversation.created_at}")
        
        # 2. Get messages for this conversation
        print(f"\n2. Messages in conversation {conversation.conversation_id}:")
        messages = await get_conversation_messages(db, conversation.conversation_id)
        print(f"   Total messages: {len(messages)}")
        
        for msg in messages:
            role = msg.content.get('role', 'unknown') if isinstance(msg.content, dict) else 'unknown'
            print(f"   - Message {msg.message_number}: {role} (ID: {msg.message_id})")
        
        # 3. Get metrics summary
        print(f"\n3. Metrics summary:")
        summary = await get_metrics_summary(db, conversation.conversation_id)
        print(f"   Total metrics: {summary.total_metrics}")
        print(f"   Total messages: {summary.total_messages}")
        print(f"   Service types: {summary.service_types}")
        
        # 4. Get detailed metrics
        print(f"\n4. Detailed metrics:")
        metrics_data = await get_conversation_metrics(db, conversation.conversation_id)
        
        if not metrics_data:
            print("   ❌ No metrics found for this conversation")
            return
        
        for metrics, message in metrics_data:
            role = message.content.get('role', 'unknown') if isinstance(message.content, dict) else 'unknown'
            print(f"   Message {message.message_number} ({role}):")
            print(f"     Service: {metrics.service_type} - {metrics.service_name}")
            print(f"     TTFB: {metrics.ttfb}")
            print(f"     Processing Time: {metrics.processing_time}")
            print(f"     Total Latency: {metrics.total_latency}")
            if metrics.prompt_tokens or metrics.completion_tokens:
                print(f"     Tokens: {metrics.prompt_tokens}/{metrics.completion_tokens}")
            if metrics.characters_processed:
                print(f"     Characters: {metrics.characters_processed}")
            print(f"     Created: {metrics.created_at}")
            print()
        
        # 5. Check for messages without metrics
        print("5. Messages without metrics:")
        messages_with_metrics = {msg.message_id for _, msg in metrics_data}
        messages_without_metrics = [msg for msg in messages if msg.message_id not in messages_with_metrics]
        
        if messages_without_metrics:
            for msg in messages_without_metrics:
                role = msg.content.get('role', 'unknown') if isinstance(msg.content, dict) else 'unknown'
                print(f"   - Message {msg.message_number} ({role}): {msg.message_id}")
        else:
            print("   ✅ All messages have metrics")


if __name__ == "__main__":
    asyncio.run(main())
