"""
Conversation Logger - Stores debug logs per conversation for metrics extraction.
"""

import os
import time
import asyncio
from typing import Optional
from loguru import logger
from pathlib import Path


class ConversationLogger:
    """Logs conversation-specific debug information for metrics extraction."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.log_file_path = None
        self.original_logger = None
        self.log_file = None
        
    def start_logging(self):
        """Start logging to a conversation-specific file."""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Create conversation-specific log file
            timestamp = int(time.time())
            self.log_file_path = logs_dir / f"conversation_{self.conversation_id}_{timestamp}.log"
            
            # Add handler to loguru for this conversation (capture ALL logs)
            self.handler_id = logger.add(
                str(self.log_file_path),
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
                # No filter - capture all logs and let the LLM filter them
                rotation="10 MB",
                retention="1 day"
            )
            
            logger.info(f"📊 Started conversation logging to {self.log_file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start conversation logging: {e}")
    
    def stop_logging(self):
        """Stop logging and remove the handler."""
        try:
            if hasattr(self, 'handler_id'):
                logger.remove(self.handler_id)
                logger.info(f"📊 Stopped conversation logging for {self.conversation_id}")
        except Exception as e:
            logger.error(f"❌ Failed to stop conversation logging: {e}")
    
    def get_log_content(self) -> str:
        """Get the content of the conversation log file."""
        try:
            if self.log_file_path and self.log_file_path.exists():
                with open(self.log_file_path, "r") as f:
                    return f.read()
            return ""
        except Exception as e:
            logger.error(f"❌ Failed to read conversation log: {e}")
            return ""
    
    def __del__(self):
        """Cleanup when the logger is destroyed."""
        self.stop_logging()
