"""
Metrics Extractor - Uses Cerebras LLM to extract metrics from conversation logs.
"""

import json
import re
import time
from typing import Dict, List, Any, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import InteractionMetrics, Message
import httpx


class MetricsExtractor:
    """Extracts metrics from conversation logs using Cerebras LLM."""
    
    def __init__(self, db_session: AsyncSession, conversation_id: str):
        self.db_session = db_session
        self.conversation_id = conversation_id
        
        # Get API key from environment
        from common.config import SERVICE_API_KEYS
        self.api_key = SERVICE_API_KEYS.get("cerebras")
        if not self.api_key:
            raise Exception("CEREBRAS_API_KEY not found in environment variables")
        
        self.model = "gpt-oss-120b"
        self.base_url = "https://api.cerebras.ai/v1"
    
    async def extract_metrics_from_logs(self, log_content: str) -> List[Dict[str, Any]]:
        """Extract metrics from conversation logs using Cerebras LLM."""
        try:
            if not log_content.strip():
                logger.warning("📊 No log content to extract metrics from")
                return []
            
            # Create a prompt for the LLM to extract metrics
            prompt = self._create_extraction_prompt(log_content)
            
            # Use Cerebras LLM to extract metrics
            response = await self._call_cerebras_api(prompt)
            
            # Parse the LLM response
            metrics = self._parse_llm_response(response)
            
            logger.info(f"📊 Extracted {len(metrics)} metrics from conversation logs")
            if metrics:
                logger.info(f"📊 Sample extracted metric: {metrics[0]}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to extract metrics from logs: {e}")
            return []
    
    def _create_extraction_prompt(self, log_content: str) -> str:
        """Create a prompt for the LLM to extract metrics."""
        return f"""
You are a metrics extraction expert. Analyze the following conversation logs and extract ONLY performance metrics from Pipecat services.

**IGNORE all other logs** - only extract metrics from these specific patterns:

**TTS Metrics (DeepgramTTSService):**
- Usage Characters: "DeepgramTTSService#0 usage characters: 94"
- TTFB: "DeepgramTTSService#0 TTFB: 0.1980431079864502"
- Processing Time: "DeepgramTTSService#0 processing time: 0.2672660350799560"

**STT Metrics (DeepgramSTTService):**
- TTFB: "DeepgramSTTService#0 TTFB: 0.0002961158752441406"
- Processing Time: "DeepgramSTTService#0 processing time: 0.0004220008850097656"

**LLM Metrics (CerebrasLLMService):**
- TTFB: "CerebrasLLMService#0 TTFB: 0.15604376792907715"
- Tokens: "CerebrasLLMService#0 prompt tokens: 1529, completion tokens: 102"
- Processing Time: "CerebrasLLMService#0 processing time: 0.4494750499725342"

**Look for these exact log patterns:**
- Lines containing "pipecat.processors.metrics.frame_processor_metrics"
- Lines containing "TTFB:", "processing time:", "usage characters:", "prompt tokens:", "completion tokens:"
- Lines with service names ending in "Service#0"

**IGNORE:**
- MCP service registration logs
- Pipeline creation logs
- Tool registration logs
- Any other non-metrics logs

Log Content:
{log_content}

Extract all metrics and return them as a JSON array with this structure:
[
  {{
    "service_type": "stt|llm|tts|mcp",
    "service_name": "ServiceName#0",
    "ttfb": "0.123",
    "total_latency": "0.456",
    "processing_time": "0.456",
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "characters_processed": 123,
    "interaction_id": "unique_id"
  }}
]

If no metrics are found, return an empty array: []

Only return the JSON array, no other text.
"""
    
    async def _call_cerebras_api(self, prompt: str) -> str:
        """Call the Cerebras API to extract metrics."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a metrics extraction assistant. Extract performance metrics from logs and return them as JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 2000
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"❌ Failed to call Cerebras API: {e}")
            return ""
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response and extract metrics."""
        try:
            logger.info(f"📊 LLM Response: {response[:200]}...")  # Log first 200 chars
            
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Parse JSON
            metrics = json.loads(response)
            logger.info(f"📊 Parsed {len(metrics)} metrics from LLM response")
            
            # Validate and clean the metrics
            cleaned_metrics = []
            for metric in metrics:
                if self._validate_metric(metric):
                    cleaned_metrics.append(self._clean_metric(metric))
                else:
                    logger.warning(f"📊 Invalid metric skipped: {metric}")
            
            logger.info(f"📊 Cleaned {len(cleaned_metrics)} valid metrics")
            return cleaned_metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to parse LLM response: {e}")
            logger.error(f"LLM Response: {response}")
            return []
    
    def _validate_metric(self, metric: Dict[str, Any]) -> bool:
        """Validate that a metric has required fields."""
        required_fields = ["service_type", "service_name"]
        return all(field in metric for field in required_fields)
    
    def _clean_metric(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize a metric."""
        # Ensure numeric fields are properly formatted
        numeric_fields = ["ttfb", "total_latency", "processing_time", "prompt_tokens", "completion_tokens", "characters_processed"]
        for field in numeric_fields:
            if field in metric and metric[field] is not None:
                try:
                    metric[field] = float(metric[field]) if field in ["ttfb", "total_latency", "processing_time"] else int(metric[field])
                except (ValueError, TypeError):
                    metric[field] = 0
        
        # Ensure string fields are strings
        string_fields = ["service_type", "service_name", "interaction_id"]
        for field in string_fields:
            if field in metric and metric[field] is not None:
                metric[field] = str(metric[field])
        
        return metric
    
    async def store_metrics(self, metrics: List[Dict[str, Any]], message_id: str):
        """Store extracted metrics in the database."""
        try:
            for i, metric in enumerate(metrics):
                # Create a unique interaction ID
                interaction_id = f"{message_id}_extracted_{i}_{int(time.time() * 1000)}"
                
                # Debug logging
                logger.info(f"📊 Storing metric {i+1}/{len(metrics)}: {metric}")
                
                await InteractionMetrics.create_metrics(
                    db_session=self.db_session,
                    message_id=message_id,
                    service_type=metric.get("service_type", "unknown"),
                    service_name=metric.get("service_name", "UnknownService"),
                    interaction_id=interaction_id,
                    ttfb=str(metric.get("ttfb", 0)),
                    total_latency=str(metric.get("total_latency", 0)),
                    processing_time=str(metric.get("processing_time", 0)),
                    prompt_tokens=metric.get("prompt_tokens"),
                    completion_tokens=metric.get("completion_tokens"),
                    characters_processed=metric.get("characters_processed"),
                    service_metadata={"extracted_from_logs": True, "conversation_id": self.conversation_id}
                )
            
            # Commit the transaction
            await self.db_session.commit()
            logger.info(f"📊 Stored {len(metrics)} extracted metrics for message {message_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store extracted metrics: {e}")
            await self.db_session.rollback()
            raise e


async def extract_and_store_metrics(conversation_id: str, log_content: str, message_id: str, db_session: AsyncSession):
    """Extract metrics from logs and store them in the database."""
    try:
        extractor = MetricsExtractor(db_session, conversation_id)
        metrics = await extractor.extract_metrics_from_logs(log_content)
        
        if metrics:
            await extractor.store_metrics(metrics, message_id)
            logger.info(f"📊 Successfully extracted and stored {len(metrics)} metrics for conversation {conversation_id}")
        else:
            logger.warning(f"📊 No metrics extracted for conversation {conversation_id}")
            
    except Exception as e:
        logger.error(f"❌ Failed to extract and store metrics: {e}")
