"""
Service configurations for TTS-LLM-STT pipeline components.
Provides centralized configuration for Deepgram STT, Cerebras LLM, and Deepgram TTS.
"""

import os
from typing import Optional

from pipecat.services.cerebras import CerebrasLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService, LiveOptions
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.transcriptions.language import Language

from common.config import SERVICE_API_KEYS


class ServiceConfig:
    """Configuration class for TTS-LLM-STT services."""
    
    # Default models
    DEFAULT_STT_MODEL = "nova-2-general"
    DEFAULT_LLM_MODEL = "gpt-oss-120b"
    DEFAULT_TTS_VOICE = "aura-luna-en"
    
    # Available models
    AVAILABLE_STT_MODELS = [
        "nova-3-general",
        "nova-2-general", 
        "nova-2-phonecall",
        "nova-2-meeting",
        "nova-2-finance",
        "nova-2-voicemail",
        "nova-2-conversationalai",
        "nova-2-medical",
        "nova-2-drive",
        "nova-2-automotive",
        "nova-2-smartgrid",
        "nova-2-education",
        "nova-2-custom",
        "nova-2-multilingual",
        "nova-2-phonecall-multilingual",
        "nova-2-meeting-multilingual",
        "nova-2-conversationalai-multilingual",
        "nova-2-voicemail-multilingual",
        "nova-2-finance-multilingual",
        "nova-2-medical-multilingual",
        "nova-2-drive-multilingual",
        "nova-2-automotive-multilingual",
        "nova-2-smartgrid-multilingual",
        "nova-2-education-multilingual",
        "nova-2-custom-multilingual"
    ]
    
    AVAILABLE_LLM_MODELS = [
        "gpt-oss-120b",
        "llama-3.3-70b",
        "llama3.1-8b",
        "llama-4-scout-17b-16e-instruct",
        "qwen-3-235b-a22b-instruct-2507",
        "qwen-3-235b-a22b-thinking-2507",
        "qwen-3-32b",
        "qwen-3-coder-480b"
    ]
    
    AVAILABLE_TTS_VOICES = [
        "aura-2-helena-en",
        "aura-2-andromeda-en", 
        "aura-helios-en",
        "aura-luna-en",
        "aura-stella-en",
        "aura-zeus-en"
    ]


def create_deepgram_stt_service(
    model: str = ServiceConfig.DEFAULT_STT_MODEL,
    language: str = "en",
    smart_format: bool = True,
    sample_rate: int = 16000
) -> DeepgramSTTService:
    """Create a Deepgram STT service with the specified configuration."""
    api_key = SERVICE_API_KEYS.get("deepgram")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
    
    if model not in ServiceConfig.AVAILABLE_STT_MODELS:
        raise ValueError(f"Unsupported STT model: {model}. Available models: {ServiceConfig.AVAILABLE_STT_MODELS}")
    
    return DeepgramSTTService(
        api_key=api_key,
        live_options=LiveOptions(
            model=model,
            language="en", #language,
            smart_format=smart_format,
            sample_rate=sample_rate
        )
    )


def create_cerebras_llm_service(
    model: str = ServiceConfig.DEFAULT_LLM_MODEL,
    base_url: str = "https://api.cerebras.ai/v1",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> CerebrasLLMService:
    """Create a Cerebras LLM service with the specified configuration."""
    api_key = SERVICE_API_KEYS.get("cerebras")
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY not found in environment variables")
    
    if model not in ServiceConfig.AVAILABLE_LLM_MODELS:
        raise ValueError(f"Unsupported LLM model: {model}. Available models: {ServiceConfig.AVAILABLE_LLM_MODELS}")
    
    return CerebrasLLMService(
        api_key=api_key,
        model=model,
        # base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens
    )


def create_deepgram_tts_service(
    voice: str = ServiceConfig.DEFAULT_TTS_VOICE,
    sample_rate: int = 24000,
    encoding: str = "linear16"
) -> DeepgramTTSService:
    """Create a Deepgram TTS service with the specified configuration."""
    api_key = SERVICE_API_KEYS.get("deepgram")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
    
    if voice not in ServiceConfig.AVAILABLE_TTS_VOICES:
        raise ValueError(f"Unsupported TTS voice: {voice}. Available voices: {ServiceConfig.AVAILABLE_TTS_VOICES}")
    
    return DeepgramTTSService(
        api_key=api_key,
        voice=voice,
        sample_rate=sample_rate,
        encoding=encoding
    )
