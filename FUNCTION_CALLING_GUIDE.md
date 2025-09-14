# Function Calling with TTS-LLM-STT Pipeline

## Overview

The TTS-LLM-STT pipeline now includes function calling capabilities, demonstrating how the voice assistant can perform real-world tasks by calling external functions. This implementation follows the [Cerebras function calling example](https://docs.pipecat.ai/server/services/llm/cerebras#usage-example) from the Pipecat documentation.

## Features

- **Weather Function**: Get current weather information for any location
- **Voice + Visual Feedback**: Function calls are logged and displayed on screen
- **Real-time Processing**: Functions are called during the voice conversation
- **Dual Mode Support**: Works in both WebRTC voice chat and HTTP text chat

## How It Works

### 1. Function Definition

The weather function is defined using Pipecat's `FunctionSchema`:

```python
weather_function = FunctionSchema(
    name="get_current_weather",
    description="Get current weather information for a specific location",
    properties={
        "location": {
            "type": "string",
            "description": "City and state, e.g. San Francisco, CA"
        },
        "format": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Temperature unit to use"
        }
    },
    required=["location", "format"]
)
```

### 2. Function Handler

The function handler simulates weather data retrieval:

```python
async def fetch_weather(params):
    location = params.arguments["location"]
    format_type = params.arguments["format"]
    
    # Simulate weather data (in a real app, you'd call a weather API)
    weather_data = {
        "location": location,
        "temperature": "75°F" if format_type == "fahrenheit" else "24°C",
        "conditions": "sunny",
        "humidity": "65%",
        "wind": "5 mph"
    }
    
    logger.info(f"🌤️ Weather function called for {location} in {format_type}")
    logger.info(f"🌤️ Weather data: {weather_data}")
    
    await params.result_callback(weather_data)
```

### 3. Event Handlers

Function calls are tracked with comprehensive logging:

```python
@llm.event_handler("on_function_calls_started")
async def on_function_calls_started(service, function_calls):
    logger.info(f"🔧 Function calls started: {[call.name for call in function_calls]}")
    for call in function_calls:
        logger.info(f"🔧 Calling function: {call.name} with args: {call.arguments}")

@llm.event_handler("on_function_call_result")
async def on_function_call_result(service, result):
    logger.info(f"🔧 Function call result: {result}")
```

## Usage Examples

### Voice Chat (WebRTC)

1. **Start the voice chat**: Click "Real-Time Voice AI Agent"
2. **Ask about weather**: Say "What's the weather like in San Francisco?"
3. **Watch the logs**: You'll see function call events in the server logs
4. **Get voice response**: The assistant will speak the weather information

### Text Chat (HTTP)

1. **Use the text interface**: Type weather questions
2. **Function calls are logged**: Check server logs for function execution
3. **Get text response**: Weather information is returned in the chat

## Example Conversations

### Voice Input:
> "What's the weather in New York in fahrenheit?"

### Server Logs:
```
🔧 Function calls started: ['get_current_weather']
🔧 Calling function: get_current_weather with args: {'location': 'New York', 'format': 'fahrenheit'}
🌤️ Weather function called for New York in fahrenheit
🌤️ Weather data: {'location': 'New York', 'temperature': '75°F', 'conditions': 'sunny', 'humidity': '65%', 'wind': '5 mph'}
🔧 Function call result: {'location': 'New York', 'temperature': '75°F', 'conditions': 'sunny', 'humidity': '65%', 'wind': '5 mph'}
```

### Voice Output:
> "Let me check the weather for you. The current weather in New York is sunny with a temperature of 75°F, 65% humidity, and winds at 5 mph."

## Extending Function Calling

### Adding New Functions

1. **Define the function schema**:
```python
new_function = FunctionSchema(
    name="your_function_name",
    description="Description of what the function does",
    properties={
        "param1": {
            "type": "string",
            "description": "Parameter description"
        }
    },
    required=["param1"]
)
```

2. **Add to tools schema**:
```python
tools = ToolsSchema(standard_tools=[weather_function, new_function])
```

3. **Register the handler**:
```python
async def your_function_handler(params):
    # Your function logic here
    result = {"key": "value"}
    await params.result_callback(result)

llm.register_function("your_function_name", your_function_handler)
```

### Real API Integration

To integrate with real APIs, replace the simulated data in the function handler:

```python
async def fetch_weather(params):
    location = params.arguments["location"]
    format_type = params.arguments["format"]
    
    # Call real weather API
    weather_data = await call_weather_api(location, format_type)
    
    await params.result_callback(weather_data)
```

## Files Modified

- `server/bots/webrtc/bot_pipeline.py` - Added function calling to WebRTC pipeline
- `server/bots/http/bot.py` - Added function calling to HTTP pipeline

## Benefits

1. **Real-world Task Execution**: Demonstrates how voice assistants can perform actual tasks
2. **Visual Feedback**: Function calls are logged and visible for debugging
3. **Voice + Visual**: Users get both spoken responses and logged information
4. **Extensible**: Easy to add more functions for different tasks
5. **Production Ready**: Framework supports real API integrations

## Next Steps

- Add more functions (calendar, email, database queries)
- Integrate with real APIs (OpenWeatherMap, Google Calendar, etc.)
- Add function call confirmation in the UI
- Implement function call history and analytics

## References

- [Pipecat Function Calling Guide](https://docs.pipecat.ai/server/services/llm/cerebras#usage-example)
- [Cerebras LLM Service Documentation](https://docs.pipecat.ai/server/services/llm/cerebras)
- [Function Schema Documentation](https://docs.pipecat.ai/server/adapters/schemas/function-schema)
