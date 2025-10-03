# Latency Metrics Implementation

This document describes the comprehensive latency metrics capture and display system implemented for the Cerebras Realtime Live Demo.

## Overview

The system captures and stores latency metrics for different services in the conversation flow, following best practices from [Deepgram's latency measurement guide](https://developers.deepgram.com/docs/measuring-streaming-latency) and [Pipecat's metrics documentation](https://docs.pipecat.ai/guides/fundamentals/metrics).

## Architecture

### Database Schema

#### InteractionMetrics Table
```sql
CREATE TABLE interaction_metrics (
    metrics_id VARCHAR PRIMARY KEY,
    message_id VARCHAR NOT NULL,
    service_type VARCHAR(50) NOT NULL,  -- 'stt', 'llm', 'tts', 'mcp'
    service_name VARCHAR(100) NOT NULL, -- e.g., 'DeepgramSTTService', 'CerebrasLLMService'
    interaction_id VARCHAR(100),        -- Unique identifier for this interaction
    ttfb VARCHAR(20),                   -- Time to first byte (in seconds)
    processing_time VARCHAR(20),        -- Processing time (in seconds)
    total_latency VARCHAR(20),          -- Total latency (in seconds)
    prompt_tokens INTEGER,              -- LLM prompt tokens
    completion_tokens INTEGER,          -- LLM completion tokens
    characters_processed INTEGER,       -- TTS characters processed
    metadata JSON,                      -- Additional service-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE
);
```

### Backend Components

#### 1. Metrics Capture (`server/bots/metrics_capture.py`)
- **MetricsCollector**: Handles storing metrics to the database
- **ServiceMetricsTracker**: Tracks timing for individual service interactions
- Factory functions for easy instantiation

#### 2. Database Models (`server/common/models.py`)
- **InteractionMetrics**: SQLAlchemy model for the metrics table
- **InteractionMetricsModel**: Pydantic model for API responses
- **InteractionMetricsCreateModel**: Pydantic model for API requests
- Updated **MessageModel** to include metrics relationship

#### 3. Bot Pipeline Integration
- **WebRTC Bot** (`server/bots/webrtc/bot_pipeline.py`): Integrated metrics capture for STT, LLM, and TTS services
- **HTTP Bot** (`server/bots/http/bot.py`): Prepared for metrics integration

#### 4. API Endpoints (`server/webapp/api/conversations.py`)
- Updated conversation messages endpoint to include metrics
- New endpoint: `GET /conversations/{conversation_id}/messages/{message_id}/metrics`

### Frontend Components

#### 1. Metrics Display (`client/src/components/MetricsDisplay.tsx`)
- Collapsible metrics display with service grouping
- Summary statistics (total latency, total tokens)
- Detailed breakdown by service type (STT, LLM, TTS, MCP)
- Color-coded service indicators
- Metadata display for debugging

#### 2. Updated Message Interface (`client/src/lib/messages.ts`)
- Added `InteractionMetrics` interface
- Updated `Message` interface to include optional `metrics` array

#### 3. Chat Message Integration (`client/src/components/ChatMessage.tsx`)
- Integrated metrics display into message rendering
- Shows metrics when available

## Metrics Captured

### Service Types
- **STT (Speech-to-Text)**: Deepgram STT service metrics
- **LLM (Large Language Model)**: Cerebras LLM service metrics  
- **TTS (Text-to-Speech)**: Deepgram TTS service metrics
- **MCP (Model Context Protocol)**: MCP service metrics

### Latency Metrics
- **TTFB (Time to First Byte)**: Time until first response from service
- **Processing Time**: Time taken by service to process request
- **Total Latency**: End-to-end latency for the interaction

### Usage Metrics
- **Prompt Tokens**: Number of input tokens for LLM
- **Completion Tokens**: Number of output tokens from LLM
- **Characters Processed**: Number of characters processed by TTS

### Metadata
- Service-specific debugging information
- Error details when available
- Response lengths and other contextual data

## Usage

### Running the Migration
```bash
cd server
python migrations/add_metrics_table.py
```

### API Usage

#### Get Conversation with Metrics
```bash
GET /conversations/{conversation_id}/messages
```
Returns messages with included metrics data.

#### Get Specific Message Metrics
```bash
GET /conversations/{conversation_id}/messages/{message_id}/metrics
```
Returns detailed metrics for a specific message.

### Frontend Display
Metrics are automatically displayed in the conversation thread when available. Users can:
- Click "Performance Metrics" to expand/collapse the display
- View summary statistics
- Drill down into specific service metrics
- Examine metadata for debugging

## Implementation Details

### Timing Strategy
The system uses a combination of:
1. **Event-based timing**: Capturing metrics when service events occur
2. **Service tracking**: Tracking start/end times for interactions
3. **Async storage**: Non-blocking metrics storage to avoid affecting performance

### Error Handling
- Graceful degradation when metrics capture fails
- Error information stored in metadata
- No impact on core conversation functionality

### Performance Considerations
- Metrics storage is asynchronous
- Minimal overhead on conversation flow
- Efficient database queries with proper indexing

## Future Enhancements

1. **Real-time Metrics Dashboard**: Live metrics visualization
2. **Performance Analytics**: Historical performance analysis
3. **Alerting**: Performance threshold monitoring
4. **Service Comparison**: Compare different service providers
5. **Cost Tracking**: Token usage cost analysis

## Troubleshooting

### Common Issues
1. **Missing Metrics**: Check if metrics collection is enabled in bot pipeline
2. **Database Errors**: Ensure migration has been run
3. **Frontend Display**: Verify TypeScript compilation

### Debug Information
- Check server logs for metrics capture errors
- Examine metadata in the frontend display
- Use the API endpoints to inspect raw metrics data

## References
- [Deepgram Latency Measurement](https://developers.deepgram.com/docs/measuring-streaming-latency)
- [Pipecat Metrics Guide](https://docs.pipecat.ai/guides/fundamentals/metrics)
- [Real-time Performance Monitoring Best Practices](https://developers.deepgram.com/docs/measuring-streaming-latency)
