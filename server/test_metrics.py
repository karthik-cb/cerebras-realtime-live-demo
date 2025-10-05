#!/usr/bin/env python3
"""
Test script to manually create metrics for the most recent conversation.
"""

import asyncio
import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.database import DatabaseSessionFactory
from common.models import Message
from sqlalchemy import select
from bots.log_based_metrics import LogBasedMetricsExtractor


async def main():
    """Create sample metrics for the most recent conversation."""
    print("🧪 Testing metrics creation...")
    
    # Initialize database
    db_factory = DatabaseSessionFactory()
    await db_factory.initialize_schema()
    
    async with db_factory() as db:
        # Get the most recent conversation
        from common.models import Conversation
        result = await db.execute(
            select(Conversation)
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            print("❌ No conversations found")
            return
        
        print(f"📊 Testing with conversation: {conversation.conversation_id}")
        
        # Get the latest message
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.conversation_id)
            .order_by(Message.message_number.desc())
            .limit(1)
        )
        latest_message = result.scalar_one_or_none()
        
        if not latest_message:
            print("❌ No messages found")
            return
        
        print(f"📊 Attaching metrics to message: {latest_message.message_number}")
        
        # Create metrics using the log-based extractor
        extractor = LogBasedMetricsExtractor(conversation.conversation_id)
        created = await extractor.extract_metrics_from_logs(db, str(latest_message.message_id))
        
        print(f"✅ Created {len(created)} metrics")
        
        # Verify the metrics were created
        from common.models import InteractionMetrics
        result = await db.execute(
            select(InteractionMetrics)
            .where(InteractionMetrics.message_id == latest_message.message_id)
        )
        metrics = result.scalars().all()
        
        print(f"📊 Verification: Found {len(metrics)} metrics in database")
        for metric in metrics:
            print(f"   - {metric.service_type}: {metric.service_name} (TTFB: {metric.ttfb}, Processing: {metric.processing_time})")


if __name__ == "__main__":
    asyncio.run(main())
