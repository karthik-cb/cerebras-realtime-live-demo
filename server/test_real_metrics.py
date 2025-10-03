#!/usr/bin/env python3
"""
Test script for real conversation metrics extraction.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bots.metrics_extractor import MetricsExtractor
from common.database import default_session_factory
from common.models import Message
from sqlalchemy import select

async def test_real_metrics_extraction():
    """Test metrics extraction with the real conversation log format."""
    try:
        # Read the real conversation log file
        with open("logs/test_real_conversation.log", "r") as f:
            log_content = f.read()
        
        print(f"📊 Real conversation log content:\n{log_content}")
        
        # Get a test conversation and message
        async with default_session_factory() as db_session:
            # Get the latest conversation
            result = await db_session.execute(
                select(Message).order_by(Message.created_at.desc()).limit(1)
            )
            latest_message = result.scalar_one_or_none()
            
            if not latest_message:
                print("❌ No messages found in database")
                return
            
            conversation_id = latest_message.conversation_id
            message_id = latest_message.message_id
            
            print(f"📊 Using conversation: {conversation_id}")
            print(f"📊 Using message: {message_id}")
            
            # Create metrics extractor
            extractor = MetricsExtractor(db_session, conversation_id)
            
            # Extract metrics
            metrics = await extractor.extract_metrics_from_logs(log_content)
            print(f"📊 Extracted {len(metrics)} metrics")
            
            if metrics:
                for i, metric in enumerate(metrics):
                    print(f"📊 Metric {i+1}: {metric}")
                
                # Store metrics
                await extractor.store_metrics(metrics, message_id)
                print(f"📊 Stored metrics successfully")
            else:
                print("❌ No metrics extracted")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_metrics_extraction())
