# Metrics Collection Approach

## Primary Method: Log-Based Metrics

**File**: `bots/log_based_metrics.py`

This is the **primary and recommended** approach for metrics collection in the demo. It creates realistic sample metrics distributed across conversation turns to simulate OpenTelemetry data.

### Usage

```python
from bots.log_based_metrics import LogBasedMetricsExtractor

# Create extractor for a conversation
extractor = LogBasedMetricsExtractor(conversation_id)

# Extract and store metrics across all messages
created_metrics = await extractor.extract_metrics_from_logs(db_session, "dummy")
```

### Features

- ✅ **Distributed Metrics**: STT metrics on user messages, LLM/TTS metrics on assistant messages
- ✅ **Realistic Data**: Generates realistic latency and token usage patterns
- ✅ **Easy to Maintain**: Simple, straightforward implementation
- ✅ **Reliable**: No complex OpenTelemetry integration issues
- ✅ **Feature Flag Controlled**: Only runs when `ENABLE_TRACING=1`

## Deprecated Approaches

The following approaches are **deprecated** and should not be used for new development:

### 1. OpenTelemetry Metrics Collector
**File**: `bots/opentelemetry_metrics.py`
- **Status**: DEPRECATED
- **Reason**: Complex integration with OpenTelemetry, unreliable span capture
- **Alternative**: Use `bots/log_based_metrics.py`

### 2. Pipecat Metrics Capture
**File**: `bots/pipecat_metrics_capture.py`
- **Status**: DEPRECATED
- **Reason**: Overly complex, hard to maintain
- **Alternative**: Use `bots/log_based_metrics.py`

### 3. Generic Metrics Collector
**File**: `bots/metrics_capture.py`
- **Status**: DEPRECATED
- **Reason**: Generic approach, not optimized for the demo use case
- **Alternative**: Use `bots/log_based_metrics.py`

## Configuration

Set the following environment variable to enable metrics collection:

```bash
ENABLE_TRACING=1
```

## Integration

The log-based metrics approach is integrated into the conversation flow via:

```python
# In bots/conversation_metrics.py
from bots.log_based_metrics import LogBasedMetricsExtractor

async def extract_metrics_for_conversation(conversation_id: str, db_session: AsyncSession):
    extractor = LogBasedMetricsExtractor(conversation_id)
    return await extractor.extract_metrics_from_logs(db_session, "dummy")
```

## Future Improvements

When real OpenTelemetry integration is needed:

1. Extend `LogBasedMetricsExtractor` to parse actual OpenTelemetry console logs
2. Keep the same distributed metrics approach
3. Maintain the same database schema and API compatibility
