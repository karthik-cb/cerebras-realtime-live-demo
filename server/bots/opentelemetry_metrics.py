"""
DEPRECATED: OpenTelemetry Metrics Integration for Pipecat

This module is deprecated in favor of the simpler log-based metrics approach
in bots/log_based_metrics.py. The log-based approach is more reliable and
easier to maintain.

Use bots/log_based_metrics.py for new metrics collection needs.

Original purpose: Uses Pipecat's built-in OpenTelemetry support for comprehensive metrics collection.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from common.models import InteractionMetrics, Message
from common.database import default_session_factory


# =====================
# In-memory span store
# =====================

from typing import cast

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace.export import SpanExporter, SimpleSpanProcessor
    from opentelemetry.sdk.trace.export import SpanExportResult
except Exception:  # pragma: no cover - optional dependency
    trace = None  # type: ignore
    SpanExporter = object  # type: ignore
    SimpleSpanProcessor = object  # type: ignore
    SpanExportResult = object  # type: ignore


class _InMemorySpanStore:
    """Thread-safe in-memory store for exported span dicts."""
    def __init__(self):
        self._spans: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def add(self, span_dict: Dict[str, Any]):
        async with self._lock:
            self._spans.append(span_dict)

    async def pop_for_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        async with self._lock:
            matched: List[Dict[str, Any]] = []
            remaining: List[Dict[str, Any]] = []
            for d in self._spans:
                if d.get("conversation_id") == conversation_id:
                    matched.append(d)
                else:
                    remaining.append(d)
            self._spans = remaining
            return matched


_span_store = _InMemorySpanStore()
_last_conversation_id: Optional[str] = None


def _ns_to_seconds(value_ns: Optional[int]) -> Optional[float]:
    if value_ns is None:
        return None
    try:
        return float(value_ns) / 1_000_000_000.0
    except Exception:
        return None


def _service_type_from_span(name: str, attributes: Dict[str, Any]) -> str:
    lname = name.lower()
    system = str(attributes.get("gen_ai.system", "")).lower()
    # Strong name hints
    if "stt" in lname:
        return "stt"
    if "tts" in lname:
        return "tts"
    if "llm" in lname:
        return "llm"
    # Attribute-based hints
    if attributes.get("transcript") is not None or attributes.get("is_final") is not None:
        return "stt"
    if attributes.get("metrics.character_count") is not None or attributes.get("text") is not None:
        return "tts"
    if (
        system in ("openai", "gcp.gemini", "cerebras", "anthropic")
        or attributes.get("gen_ai.usage.input_tokens") is not None
        or attributes.get("gen_ai.usage.output_tokens") is not None
        or attributes.get("input") is not None
        or attributes.get("output") is not None
    ):
        return "llm"
    return "unknown"


def _service_name_from_span(name: str, attributes: Dict[str, Any]) -> str:
    system = attributes.get("gen_ai.system")
    model = attributes.get("gen_ai.request.model")
    if system and model:
        return f"{system}:{model}"
    if system:
        return str(system)
    return name


class _DBSpanExporter(SpanExporter):
    """Exporter that transforms spans and stores them in memory for later DB ingestion."""

    def export(self, spans):  # type: ignore[override]
        # spans is an iterable of ReadableSpan/SpanData
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async def _process():
            for s in spans:
                try:
                    # SpanData has attributes dict-like
                    attributes = getattr(s, "attributes", {}) or {}
                    span_name = getattr(s, "name", "")
                    start_time = getattr(s, "start_time", None)
                    end_time = getattr(s, "end_time", None)
                    duration_s = None
                    if start_time is not None and end_time is not None:
                        duration_s = _ns_to_seconds(end_time - start_time)
                    else:
                        # An approximate fallback for the duration
                        duration_s = attributes.get("metrics.ttfb")
                    # Conversation id handling
                    conv_id = attributes.get("conversation.id") or attributes.get("conversation_id")
                    global _last_conversation_id
                    if span_name == "conversation" and attributes.get("conversation.id"):
                        _last_conversation_id = str(attributes.get("conversation.id"))
                    if conv_id is None and _last_conversation_id is not None:
                        conv_id = _last_conversation_id

                    span_dict = {
                        "name": span_name,
                        "attributes": dict(attributes),
                        "conversation_id": conv_id,
                        "service_type": _service_type_from_span(span_name, attributes),
                        "service_name": _service_name_from_span(span_name, attributes),
                        "metrics": {
                            "ttfb": attributes.get("metrics.ttfb"),
                            "processing_time": duration_s,
                            "prompt_tokens": attributes.get("gen_ai.usage.input_tokens"),
                            "completion_tokens": attributes.get("gen_ai.usage.output_tokens"),
                            "characters_processed": attributes.get("metrics.character_count"),
                        },
                    }
                    if os.getenv("OTEL_EXPORT_DEBUG"):
                        try:
                            logger.debug(f"📊 Exported span -> {span_dict['name']} type={span_dict['service_type']} conv={span_dict['conversation_id']}")
                        except Exception:
                            pass
                    await _span_store.add(span_dict)
                    logger.info(f"📊 Added span to store: {span_dict['name']} ({span_dict['service_type']}) for conversation {span_dict['conversation_id']}")
                except Exception:
                    # Best-effort
                    pass

        try:
            if loop.is_running():
                asyncio.create_task(_process())
            else:
                loop.run_until_complete(_process())
        except Exception:
            pass
        return SpanExportResult.SUCCESS  # type: ignore

    def shutdown(self):  # type: ignore[override]
        return

class OpenTelemetryMetricsCollector:
    """
    DEPRECATED: Collects metrics from OpenTelemetry traces and stores them in the database.
    
    This class is deprecated. Use LogBasedMetricsExtractor from bots/log_based_metrics.py instead.
    """
    
    def __init__(self, conversation_id: str):
        logger.warning("⚠️ OpenTelemetryMetricsCollector is deprecated. Use LogBasedMetricsExtractor instead.")
        self.conversation_id = conversation_id
        self.metrics_buffer: List[Dict[str, Any]] = []
        
    async def collect_metrics_from_traces(self, db_session: AsyncSession, message_id: str):
        """Collect metrics from OpenTelemetry traces and store them."""
        try:
            # Feature flag: allow disabling during rollout
            enable_tracing = os.getenv("ENABLE_TRACING", "0") not in ("0", "false", "False", "")
            if not enable_tracing:
                return []

            # Drain spans for this conversation from in-memory store.
            # Spans may arrive slightly after the call; retry briefly.
            exported: List[Dict[str, Any]] = []
            for _ in range(10):  # up to ~2s total
                exported = await _span_store.pop_for_conversation(self.conversation_id)
                if exported:
                    break
                await asyncio.sleep(0.2)
            if not exported:
                return []

            created: List[Dict[str, Any]] = []
            for item in exported:
                try:
                    svc_type = item.get("service_type") or "unknown"
                    svc_name = item.get("service_name") or "unknown"
                    m = item.get("metrics", {}) or {}
                    ttfb = m.get("ttfb")
                    processing_time = m.get("processing_time")
                    prompt_tokens = m.get("prompt_tokens")
                    completion_tokens = m.get("completion_tokens")
                    characters_processed = m.get("characters_processed")

                    record = await InteractionMetrics.create_metrics(
                        db_session=db_session,
                        message_id=message_id,
                        service_type=str(svc_type),
                        service_name=str(svc_name),
                        interaction_id=f"otel_{self.conversation_id}",
                        ttfb=str(ttfb) if ttfb is not None else None,
                        processing_time=str(round(processing_time, 6)) if processing_time is not None else None,
                        prompt_tokens=int(prompt_tokens) if prompt_tokens is not None else None,
                        completion_tokens=int(completion_tokens) if completion_tokens is not None else None,
                        characters_processed=int(characters_processed) if characters_processed is not None else None,
                        service_metadata={"source": "otel", "span_name": item.get("name")},
                    )
                    created.append(record.dict() if hasattr(record, "dict") else {"service_name": svc_name})
                except Exception as e:
                    logger.warning(f"📊 Failed to persist OTEL metric span: {e}")

            return created
            
        except Exception as e:
            logger.error(f"❌ Failed to collect OpenTelemetry metrics: {e}")
            return []


def setup_conversation_tracing(conversation_id: str):
    """
    DEPRECATED: Set up OpenTelemetry tracing for a conversation, gated by feature flags.
    
    This function is deprecated. The log-based metrics approach in bots/log_based_metrics.py
    is now the preferred method for metrics collection.
    """
    logger.warning("⚠️ setup_conversation_tracing is deprecated. Use log-based metrics approach instead.")
    try:
        # Feature flag
        enable_tracing = os.getenv("ENABLE_TRACING", "0") not in ("0", "false", "False", "")
        if not enable_tracing:
            logger.info("📊 Tracing disabled by ENABLE_TRACING flag")
            return

        # Attempt imports
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from pipecat.utils.tracing.setup import setup_tracing
        except ImportError:
            logger.warning("📊 OpenTelemetry not available - disable ENABLE_TRACING or install tracing extras")
            return

        # Service name and exporter
        service_name = os.getenv("OTEL_SERVICE_NAME", "cerebras-voice-demo")
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
        console_export = os.getenv("OTEL_CONSOLE_EXPORT", "1") not in ("0", "false", "False")

        exporter = None
        if otlp_endpoint:
            try:
                exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                logger.info(f"📊 Using OTLP exporter: {otlp_endpoint}")
            except Exception as e:
                logger.warning(f"📊 Failed to create OTLP exporter ({otlp_endpoint}), falling back to console: {e}")
                exporter = None

        # Create a composite exporter that includes both the main exporter and our DB exporter
        db_exporter = _DBSpanExporter()
        
        if exporter:
            # If we have a main exporter, we need to use both
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            
            # Create a custom exporter that forwards to both
            class CompositeExporter(SpanExporter):
                def export(self, spans):
                    # Export to main exporter
                    try:
                        exporter.export(spans)
                    except Exception as e:
                        logger.warning(f"📊 Main exporter failed: {e}")
                    
                    # Export to DB exporter
                    try:
                        db_exporter.export(spans)
                    except Exception as e:
                        logger.warning(f"📊 DB exporter failed: {e}")
                    
                    return SpanExportResult.SUCCESS
                
                def shutdown(self):
                    try:
                        exporter.shutdown()
                    except Exception:
                        pass
                    try:
                        db_exporter.shutdown()
                    except Exception:
                        pass
            
            composite_exporter = CompositeExporter()
            setup_tracing(
                service_name=service_name,
                exporter=composite_exporter,
                console_export=console_export,
            )
        else:
            # No main exporter, just use our DB exporter
            setup_tracing(
                service_name=service_name,
                exporter=db_exporter,
                console_export=console_export,
            )

        # Provide a best-effort default conversation id for spans that lack it
        global _last_conversation_id
        _last_conversation_id = conversation_id
        logger.info("📊 OpenTelemetry setup complete with DB span capture")

        logger.info(f"📊 OpenTelemetry tracing configured for conversation {conversation_id} (service={service_name})")

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
    """
    DEPRECATED: Collects metrics using Pipecat's built-in metrics system.
    
    This class is deprecated. Use LogBasedMetricsExtractor from bots/log_based_metrics.py instead.
    """
    
    def __init__(self, conversation_id: str):
        logger.warning("⚠️ PipecatMetricsCollector is deprecated. Use LogBasedMetricsExtractor instead.")
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
