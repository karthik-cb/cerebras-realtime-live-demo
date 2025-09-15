"""
Model Configuration

This module defines available models for STT, LLM, and TTS services,
as well as MCP server configurations that can be selected by users.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ModelOption:
    """Configuration for a model option"""
    id: str
    name: str
    description: str
    provider: str
    enabled: bool = True

# Deepgram STT Models (based on services.py)
DEEPGRAM_STT_MODELS = [
    ModelOption(
        id="nova-3-general",
        name="Nova-3 General",
        description="Latest general-purpose model with improved accuracy",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-general",
        name="Nova-2 General",
        description="General-purpose model with good accuracy",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-phonecall",
        name="Nova-2 Phone Call",
        description="Optimized for phone call audio quality",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-meeting",
        name="Nova-2 Meeting",
        description="Optimized for meeting and conference audio",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-finance",
        name="Nova-2 Finance",
        description="Optimized for financial and business terminology",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-voicemail",
        name="Nova-2 Voicemail",
        description="Optimized for voicemail transcription",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-conversationalai",
        name="Nova-2 Conversational AI",
        description="Optimized for conversational AI applications",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-medical",
        name="Nova-2 Medical",
        description="Optimized for medical terminology and conversations",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-drivethru",
        name="Nova-2 Drive Thru",
        description="Optimized for drive-through audio quality",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="nova-2-automotive",
        name="Nova-2 Automotive",
        description="Optimized for automotive applications",
        provider="Deepgram",
        enabled=True
    ),
]

# Cerebras LLM Models (based on services.py)
CEREBRAS_LLM_MODELS = [
    ModelOption(
        id="gpt-oss-120b",
        name="GPT-OSS 120B",
        description="120 billion parameter open-source GPT model",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="llama-3.3-70b",
        name="Llama 3.3 70B",
        description="70 billion parameter Llama 3.3 model",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="llama3.1-8b",
        name="Llama 3.1 8B",
        description="8 billion parameter Llama 3.1 model",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="llama-4-scout-17b-16e-instruct",
        name="Llama 4 Scout 17B",
        description="17 billion parameter Llama 4 Scout model with instruction tuning",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="qwen-3-235b-a22b-instruct-2507",
        name="Qwen 3 235B Instruct",
        description="235 billion parameter Qwen 3 model with instruction tuning",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="qwen-3-235b-a22b-thinking-2507",
        name="Qwen 3 235B Thinking",
        description="235 billion parameter Qwen 3 model with thinking capabilities",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="qwen-3-32b",
        name="Qwen 3 32B",
        description="32 billion parameter Qwen 3 model",
        provider="Cerebras",
        enabled=True
    ),
    ModelOption(
        id="qwen-3-coder-480b",
        name="Qwen 3 Coder 480B",
        description="480 billion parameter Qwen 3 Coder model for code generation",
        provider="Cerebras",
        enabled=True
    ),
]

# Deepgram TTS Models (based on services.py)
DEEPGRAM_TTS_MODELS = [
    ModelOption(
        id="aura-2-helena-en",
        name="Aura 2 Helena (English)",
        description="Female voice, warm and conversational",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="aura-2-andromeda-en",
        name="Aura 2 Andromeda (English)",
        description="Female voice, professional and clear",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="aura-helios-en",
        name="Aura Helios (English)",
        description="Male voice, bright and optimistic",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="aura-luna-en",
        name="Aura Luna (English)",
        description="Female voice, warm and conversational",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="aura-stella-en",
        name="Aura Stella (English)",
        description="Female voice, professional and clear",
        provider="Deepgram",
        enabled=True
    ),
    ModelOption(
        id="aura-zeus-en",
        name="Aura Zeus (English)",
        description="Male voice, deep and commanding",
        provider="Deepgram",
        enabled=True
    ),
]

# MCP Server Options
MCP_SERVER_OPTIONS = [
    ModelOption(
        id="filesystem",
        name="Filesystem",
        description="File operations (read, write, list files)",
        provider="MCP",
        enabled=True
    ),
    ModelOption(
        id="paypal_sandbox",
        name="PayPal Sandbox",
        description="PayPal business tools (invoices, payments, subscriptions) - Sandbox environment",
        provider="PayPal",
        enabled=True
    ),
    ModelOption(
        id="paypal_production",
        name="PayPal Production",
        description="PayPal business tools (invoices, payments, subscriptions) - Production environment",
        provider="PayPal",
        enabled=False
    ),
    ModelOption(
        id="database",
        name="Database",
        description="Database operations (query, insert, update)",
        provider="MCP",
        enabled=False
    ),
    ModelOption(
        id="weather",
        name="Weather",
        description="Real-time weather data from OpenWeatherMap",
        provider="MCP",
        enabled=False
    ),
    ModelOption(
        id="calendar",
        name="Calendar",
        description="Google Calendar integration (events, scheduling)",
        provider="MCP",
        enabled=False
    ),
    ModelOption(
        id="email",
        name="Email",
        description="Email operations (send, read, manage)",
        provider="MCP",
        enabled=False
    ),
    ModelOption(
        id="github",
        name="GitHub",
        description="GitHub operations (repos, issues, pull requests)",
        provider="MCP",
        enabled=False
    ),
    ModelOption(
        id="slack",
        name="Slack",
        description="Slack integration (messages, channels, users)",
        provider="MCP",
        enabled=False
    ),
    ModelOption(
        id="jira",
        name="Jira",
        description="Jira project management integration",
        provider="MCP",
        enabled=False
    ),
]

def get_available_models() -> Dict[str, List[ModelOption]]:
    """Get all available models organized by service type"""
    return {
        "stt": [model for model in DEEPGRAM_STT_MODELS if model.enabled],
        "llm": [model for model in CEREBRAS_LLM_MODELS if model.enabled],
        "tts": [model for model in DEEPGRAM_TTS_MODELS if model.enabled],
        "mcp": [model for model in MCP_SERVER_OPTIONS if model.enabled],
    }

def get_default_models() -> Dict[str, str]:
    """Get default model selections (based on services.py)"""
    return {
        "stt": "nova-2-general",
        "llm": "gpt-oss-120b", 
        "tts": "aura-luna-en",
        "mcp": "filesystem",
    }

def get_model_by_id(service: str, model_id: str) -> Optional[ModelOption]:
    """Get a specific model by service and ID"""
    models = get_available_models().get(service, [])
    return next((model for model in models if model.id == model_id), None)
