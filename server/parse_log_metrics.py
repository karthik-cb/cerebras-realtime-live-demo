#!/usr/bin/env python3
"""
Parse OpenTelemetry spans from log file and create metrics records.
Usage: python parse_log_metrics.py <conversation_id>
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.database import DatabaseSessionFactory
from common.models import Message, InteractionMetrics
from sqlalchemy import select


class LogSpanParser:
    """Parse OpenTelemetry spans from log output."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.spans: List[Dict[str, Any]] = []
    
    def parse_log_file(self, log_file_path: str) -> List[Dict[str, Any]]:
        """Parse spans from a log file."""
        spans = []
        
        try:
            with open(log_file_path, 'r') as f:
                for line in f:
                    span = self.parse_span_line(line.strip())
                    if span and span.get('conversation_id') == self.conversation_id:
                        spans.append(span)
        except FileNotFoundError:
            print(f"❌ Log file not found: {log_file_path}")
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
        
        return spans
    
    def parse_span_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single span from a log line."""
        try:
            # Look for JSON objects that represent spans
            if line.startswith('{') and line.endswith('}'):
                span_data = json.loads(line)
                
                # Check if this looks like a span
                if 'name' in span_data and 'attributes' in span_data:
                    return self.extract_span_info(span_data)
        except (json.JSONDecodeError, ValueError):
            pass
        
        return None
    
    def extract_span_info(self, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant information from span data."""
        name = span_data.get('name', '')
        attributes = span_data.get('attributes', {})
        
        # Get timing information
        start_time = span_data.get('start_time')
        end_time = span_data.get('end_time')
        duration_s = None
        
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration_s = (end_dt - start_dt).total_seconds()
            except ValueError:
                pass
        
        # Determine service type
        service_type = self.get_service_type(name, attributes)
        
        return {
            'name': name,
            'service_type': service_type,
            'service_name': self.get_service_name(name, attributes),
            'conversation_id': attributes.get('conversation.id'),
            'ttfb': attributes.get('metrics.ttfb'),
            'processing_time': duration_s,
            'prompt_tokens': attributes.get('gen_ai.usage.input_tokens'),
            'completion_tokens': attributes.get('gen_ai.usage.output_tokens'),
            'characters_processed': attributes.get('metrics.character_count'),
            'start_time': start_time,
            'end_time': end_time,
        }
    
    def get_service_type(self, span_name: str, attributes: Dict[str, Any]) -> str:
        """Determine service type from span name and attributes."""
        name_lower = span_name.lower()
        
        if 'stt' in name_lower or attributes.get('transcript') is not None:
            return 'stt'
        if 'tts' in name_lower or attributes.get('metrics.character_count') is not None:
            return 'tts'
        if 'llm' in name_lower or attributes.get('gen_ai.usage.input_tokens') is not None:
            return 'llm'
        
        return 'unknown'
    
    def get_service_name(self, span_name: str, attributes: Dict[str, Any]) -> str:
        """Get service name from span attributes."""
        system = attributes.get('gen_ai.system')
        model = attributes.get('gen_ai.request.model')
        
        if system and model:
            return f"{system}:{model}"
        if system:
            return str(system)
        
        return span_name


async def create_metrics_from_spans(conversation_id: str, spans: List[Dict[str, Any]]):
    """Create metrics records from parsed spans."""
    if not spans:
        print("❌ No spans found for this conversation")
        return
    
    # Initialize database
    db_factory = DatabaseSessionFactory()
    await db_factory.initialize_schema()
    
    async with db_factory() as db:
        # Get the latest message to attach metrics to
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.message_number.desc())
            .limit(1)
        )
        latest_message = result.scalar_one_or_none()
        
        if not latest_message:
            print(f"❌ No messages found for conversation {conversation_id}")
            return
        
        print(f"📊 Attaching metrics to message {latest_message.message_number} ({latest_message.message_id})")
        
        created_count = 0
        for span in spans:
            try:
                await InteractionMetrics.create_metrics(
                    db_session=db,
                    message_id=str(latest_message.message_id),
                    service_type=span['service_type'],
                    service_name=span['service_name'],
                    interaction_id=f"log_parse_{conversation_id}",
                    ttfb=str(span['ttfb']) if span['ttfb'] is not None else None,
                    processing_time=str(round(span['processing_time'], 6)) if span['processing_time'] is not None else None,
                    total_latency=str(round(span['processing_time'], 6)) if span['processing_time'] is not None else None,
                    prompt_tokens=int(span['prompt_tokens']) if span['prompt_tokens'] is not None else None,
                    completion_tokens=int(span['completion_tokens']) if span['completion_tokens'] is not None else None,
                    characters_processed=int(span['characters_processed']) if span['characters_processed'] is not None else None,
                    service_metadata={"source": "log_parser", "span_name": span['name']},
                )
                created_count += 1
                print(f"✅ Created metric: {span['service_type']} - {span['service_name']}")
            except Exception as e:
                print(f"❌ Failed to create metric for {span['name']}: {e}")
        
        print(f"📊 Created {created_count} metrics for conversation {conversation_id}")


async def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python parse_log_metrics.py <conversation_id>")
        print("Example: python parse_log_metrics.py 0ee147fd-9a02-427a-a9f9-1aa2d06b7a5d")
        return
    
    conversation_id = sys.argv[1]
    
    # Look for log files in common locations
    log_paths = [
        "logs/railway_last_hr.log",
        "logs/test_conversation.log",
        "logs/test_real_conversation.log",
    ]
    
    parser = LogSpanParser(conversation_id)
    spans = []
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            print(f"📄 Parsing log file: {log_path}")
            file_spans = parser.parse_log_file(log_path)
            spans.extend(file_spans)
            print(f"   Found {len(file_spans)} spans for conversation {conversation_id}")
    
    if not spans:
        print(f"❌ No spans found for conversation {conversation_id}")
        print("💡 Make sure to run a voice conversation with ENABLE_TRACING=1 first")
        return
    
    print(f"📊 Found {len(spans)} total spans for conversation {conversation_id}")
    
    # Create metrics from spans
    await create_metrics_from_spans(conversation_id, spans)


if __name__ == "__main__":
    asyncio.run(main())
