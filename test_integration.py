#!/usr/bin/env python3
"""
Test script to verify TTS-LLM-STT pipeline integration.
This script tests the service configurations and basic functionality.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

from bots.services import (
    create_deepgram_stt_service,
    create_cerebras_llm_service, 
    create_deepgram_tts_service,
    ServiceConfig
)


async def test_services():
    """Test that all services can be instantiated with default configurations."""
    
    print("🧪 Testing TTS-LLM-STT Pipeline Integration")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Checking Environment Variables:")
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    
    print(f"  DEEPGRAM_API_KEY: {'✅ Set' if deepgram_key else '❌ Missing'}")
    print(f"  CEREBRAS_API_KEY: {'✅ Set' if cerebras_key else '❌ Missing'}")
    
    if not deepgram_key or not cerebras_key:
        print("\n❌ Missing required API keys. Please set them in your .env file.")
        return False
    
    # Test Deepgram STT Service
    print("\n🎤 Testing Deepgram STT Service:")
    try:
        stt = create_deepgram_stt_service()
        print(f"  ✅ STT Service created successfully")
        print(f"  📊 Model: {ServiceConfig.DEFAULT_STT_MODEL}")
        print(f"  📊 Available models: {len(ServiceConfig.AVAILABLE_STT_MODELS)}")
    except Exception as e:
        print(f"  ❌ STT Service creation failed: {e}")
        return False
    
    # Test Cerebras LLM Service
    print("\n🧠 Testing Cerebras LLM Service:")
    try:
        llm = create_cerebras_llm_service()
        print(f"  ✅ LLM Service created successfully")
        print(f"  📊 Model: {ServiceConfig.DEFAULT_LLM_MODEL}")
        print(f"  📊 Available models: {len(ServiceConfig.AVAILABLE_LLM_MODELS)}")
    except Exception as e:
        print(f"  ❌ LLM Service creation failed: {e}")
        return False
    
    # Test Deepgram TTS Service
    print("\n🔊 Testing Deepgram TTS Service:")
    try:
        tts = create_deepgram_tts_service()
        print(f"  ✅ TTS Service created successfully")
        print(f"  📊 Voice: {ServiceConfig.DEFAULT_TTS_VOICE}")
        print(f"  📊 Available voices: {len(ServiceConfig.AVAILABLE_TTS_VOICES)}")
    except Exception as e:
        print(f"  ❌ TTS Service creation failed: {e}")
        return False
    
    # Test model validation
    print("\n🔍 Testing Model Validation:")
    
    # Test invalid STT model
    try:
        create_deepgram_stt_service(model="invalid-model")
        print("  ❌ Should have failed with invalid STT model")
        return False
    except ValueError:
        print("  ✅ Invalid STT model correctly rejected")
    
    # Test invalid LLM model
    try:
        create_cerebras_llm_service(model="invalid-model")
        print("  ❌ Should have failed with invalid LLM model")
        return False
    except ValueError:
        print("  ✅ Invalid LLM model correctly rejected")
    
    # Test invalid TTS voice
    try:
        create_deepgram_tts_service(voice="invalid-voice")
        print("  ❌ Should have failed with invalid TTS voice")
        return False
    except ValueError:
        print("  ✅ Invalid TTS voice correctly rejected")
    
    print("\n🎉 All tests passed! TTS-LLM-STT pipeline is ready.")
    print("\n📝 Next steps:")
    print("  1. Run 'python sesame.py init' to initialize the database")
    print("  2. Run 'python sesame.py run' to start the server")
    print("  3. Run 'npm run dev' in the client directory to start the frontend")
    print("  4. Open your browser and test the voice chat functionality")
    
    return True


def main():
    """Main test function."""
    print("🚀 TTS-LLM-STT Pipeline Integration Test")
    print("This script tests the service configurations and validates the setup.")
    print()
    
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent / "server" / ".env"
    if env_file.exists():
        print(f"📁 Loading environment variables from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Run the async test
    try:
        success = asyncio.run(test_services())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
