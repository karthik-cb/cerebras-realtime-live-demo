# TTS-LLM-STT Pipeline Implementation

This document describes the turbocharged TTS-LLM-STT pipeline implementation that replaces the original Gemini Multimodal Live API with a more flexible and performant architecture using Deepgram and Cerebras services.

## Overview

The new pipeline consists of three main components:

1. **Deepgram STT (Speech-to-Text)** - Converts user audio to text
2. **Cerebras LLM (Large Language Model)** - Processes text and generates responses  
3. **Deepgram TTS (Text-to-Speech)** - Converts AI responses to audio

## Architecture

### WebRTC Pipeline (Real-time Voice Chat)

```
Audio Input → Deepgram STT → RTVI → User Aggregator → Cerebras LLM → Deepgram TTS → Audio Output
```

### HTTP Pipeline (Text Chat)

```
Text Input → RTVI → User Aggregator → Cerebras LLM → Text Output
```

## Services Configuration

### Deepgram STT Service

- **Default Model**: `nova-2-general`
- **Sample Rate**: 16000 Hz
- **Language**: English (EN)
- **Features**: Smart formatting, real-time transcription

**Available Models**:
- `nova-3-general` - Latest general purpose
- `nova-2-general` - General purpose, meetings
- `nova-2-phonecall` - Phone calls, low quality audio
- `nova-2-meeting` - Meeting-specific optimization
- `nova-2-finance` - Financial domain
- `nova-2-voicemail` - Voicemail transcription
- `nova-2-conversationalai` - Conversational AI
- `nova-2-medical` - Medical domain
- `nova-2-drive` - Automotive
- `nova-2-automotive` - Automotive
- `nova-2-smartgrid` - Smart grid
- `nova-2-education` - Education
- `nova-2-custom` - Custom models
- `nova-2-multilingual` - Multilingual support

### Cerebras LLM Service

- **Default Model**: `gpt-oss-120b`
- **Base URL**: `https://api.cerebras.ai/v1`
- **Temperature**: 0.7
- **Max Tokens**: 1000

**Available Models**:
- `gpt-oss-120b` - 120B parameter model
- `llama-3.1-405b-instruct` - 405B parameter Llama model
- `llama-3.1-70b-instruct` - 70B parameter Llama model
- `llama-3.1-8b-instruct` - 8B parameter Llama model
- `llama-3.1-1b-instruct` - 1B parameter Llama model
- Various quantization variants (AWQ, W8A16, W4A16, etc.)

### Deepgram TTS Service

- **Default Voice**: `aura-luna-en`
- **Sample Rate**: 24000 Hz
- **Encoding**: linear16

**Available Voices**:
- `aura-2-helena-en` - Natural female voice
- `aura-2-andromeda-en` - Expressive female voice
- `aura-helios-en` - Warm male voice
- `aura-luna-en` - Conversational female voice
- `aura-stella-en` - Professional female voice
- `aura-zeus-en` - Authoritative male voice

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the `server` directory with the following variables:

```bash
# Required API Keys
DEEPGRAM_API_KEY="your_deepgram_api_key_here"
CEREBRAS_API_KEY="your_cerebras_api_key_here"

# Optional (for backward compatibility)
GEMINI_API_KEY=""
DAILY_API_KEY="your_daily_api_key_here"

# Database
DATABASE_URL="sqlite+aiosqlite:///./sesame.db"

# Webapp Configuration
WEBAPP_PORT="7860"
WEBAPP_LOG_LEVEL=DEBUG

# Bot Configuration
BOT_LOG_LEVEL=DEBUG
BOT_MAX_VOICE_SESSION_TIME=900
```

### 2. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python sesame.py init
```

### 4. Run Server

```bash
python sesame.py run
```

### 5. Run Client

```bash
cd client
npm install
npm run dev
```

## API Key Setup

### Deepgram API Key

1. Sign up at [Deepgram Console](https://console.deepgram.com/)
2. Create a new API key
3. Add it to your `.env` file as `DEEPGRAM_API_KEY`

### Cerebras API Key

1. Sign up at [Cerebras Cloud](https://cloud.cerebras.ai/)
2. Generate an API key from your dashboard
3. Add it to your `.env` file as `CEREBRAS_API_KEY`

## Usage Examples

### WebRTC Voice Chat

The WebRTC mode provides real-time voice interaction:

1. Start the server and client
2. Click "Switch to Voice Mode" in the chat interface
3. Allow microphone permissions
4. Speak naturally - the system will:
   - Convert your speech to text using Deepgram STT
   - Process the text with Cerebras LLM
   - Convert the response to speech using Deepgram TTS

### HTTP Text Chat

The HTTP mode provides text-based interaction:

1. Type your message in the chat interface
2. Press Enter or click Send
3. The system will process your text with Cerebras LLM
4. Display the response in the chat

## Customization

### Changing Models

You can customize the models by modifying the service configurations in `server/bots/services.py`:

```python
# Change STT model
stt = create_deepgram_stt_service(model="nova-3-general")

# Change LLM model  
llm = create_cerebras_llm_service(model="llama-3.1-70b-instruct")

# Change TTS voice
tts = create_deepgram_tts_service(voice="aura-zeus-en")
```

### Pipeline Configuration

The pipeline processors are defined in `server/bots/webrtc/bot_pipeline.py`:

```python
processors = [
    transport.input(),
    stt,  # Deepgram STT
    rtvi,
    user_aggregator,
    llm,  # Cerebras LLM
    tts,  # Deepgram TTS
    rtvi_speaking,
    rtvi_user_transcription,
    rtvi_bot_llm,
    rtvi_bot_transcription,
    transport.output(),
    rtvi_bot_tts,
    assistant_aggregator,
    storage.create_processor(exit_on_endframe=True),
]
```

## Performance Benefits

### Compared to Gemini Multimodal Live:

1. **Lower Latency**: Separate STT and TTS services allow for optimized streaming
2. **Better Quality**: Deepgram's specialized STT/TTS models vs. general multimodal
3. **More Control**: Independent configuration of each pipeline component
4. **Cost Efficiency**: Pay only for what you use with granular billing
5. **Flexibility**: Easy to swap models or add new services

### Latency Optimizations:

- **STT Streaming**: Real-time transcription with interim results
- **LLM Streaming**: Token-by-token response generation
- **TTS Streaming**: Chunked audio generation for immediate playback
- **VAD Integration**: Voice Activity Detection for efficient processing

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env`
2. **Model Not Found**: Check that the model name is in the available models list
3. **Audio Issues**: Verify microphone permissions and audio device selection
4. **Connection Errors**: Check network connectivity and API endpoint availability

### Debug Mode

Enable debug logging by setting:

```bash
BOT_LOG_LEVEL=DEBUG
WEBAPP_LOG_LEVEL=DEBUG
```

### Monitoring

The pipeline includes comprehensive metrics:

- **STT Metrics**: Time to first byte, processing duration
- **LLM Metrics**: Token usage, response time
- **TTS Metrics**: Synthesis time, character usage

## Migration from Gemini

The codebase maintains backward compatibility. To switch back to Gemini:

1. Set `GEMINI_API_KEY` in your `.env` file
2. Modify the service imports in the pipeline files
3. Replace the service instantiations with Gemini equivalents

## Support

For issues related to:

- **Deepgram**: Check [Deepgram Documentation](https://docs.deepgram.com/)
- **Cerebras**: Check [Cerebras Documentation](https://docs.cerebras.ai/)
- **Pipecat**: Check [Pipecat Documentation](https://docs.pipecat.ai/)

## License

This implementation maintains the same BSD-2-Clause license as the original project.
