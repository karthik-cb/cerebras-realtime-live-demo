#!/usr/bin/env python3
"""
Setup script for TTS-LLM-STT pipeline.
This script helps users set up the environment and test the integration.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(f"📤 Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"📤 Error: {e.stderr.strip()}")
        return e


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Please use Python 3.10, 3.11, or 3.12")
        return False


def setup_environment():
    """Set up the environment file."""
    print("\n🔧 Setting up environment...")
    
    server_dir = Path(__file__).parent / "server"
    env_file = server_dir / ".env"
    env_example = server_dir / "env.example"
    
    if env_file.exists():
        print(f"📁 Environment file already exists: {env_file}")
        response = input("   Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("   Keeping existing .env file")
            return True
    
    if env_example.exists():
        print(f"📋 Copying {env_example} to {env_file}")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Environment file created")
        print("📝 Please edit the .env file and add your API keys:")
        print("   - DEEPGRAM_API_KEY")
        print("   - CEREBRAS_API_KEY")
        print("   - DAILY_API_KEY (optional, for WebRTC)")
        return True
    else:
        print(f"❌ Environment example file not found: {env_example}")
        return False


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    server_dir = Path(__file__).parent / "server"
    requirements_file = server_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    result = run_command(
        f"pip install -r {requirements_file}",
        cwd=server_dir
    )
    
    if result.returncode == 0:
        print("✅ Python dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install Python dependencies")
        return False


def install_client_dependencies():
    """Install client dependencies."""
    print("\n📦 Installing client dependencies...")
    
    client_dir = Path(__file__).parent / "client"
    package_json = client_dir / "package.json"
    
    if not package_json.exists():
        print(f"❌ Client package.json not found: {package_json}")
        return False
    
    result = run_command("npm install", cwd=client_dir)
    
    if result.returncode == 0:
        print("✅ Client dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install client dependencies")
        return False


def initialize_database():
    """Initialize the database."""
    print("\n🗄️  Initializing database...")
    
    server_dir = Path(__file__).parent / "server"
    sesame_py = server_dir / "sesame.py"
    
    if not sesame_py.exists():
        print(f"❌ Sesame script not found: {sesame_py}")
        return False
    
    result = run_command("python sesame.py init", cwd=server_dir)
    
    if result.returncode == 0:
        print("✅ Database initialized successfully")
        return True
    else:
        print("❌ Failed to initialize database")
        return False


def test_integration():
    """Test the integration."""
    print("\n🧪 Testing integration...")
    
    test_script = Path(__file__).parent / "test_integration.py"
    
    if not test_script.exists():
        print(f"❌ Test script not found: {test_script}")
        return False
    
    result = run_command(f"python {test_script}", check=False)
    
    if result.returncode == 0:
        print("✅ Integration test passed")
        return True
    else:
        print("❌ Integration test failed")
        print("   Please check your API keys and try again")
        return False


def main():
    """Main setup function."""
    print("🚀 TTS-LLM-STT Pipeline Setup")
    print("=" * 40)
    print("This script will help you set up the TTS-LLM-STT pipeline.")
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up environment
    if not setup_environment():
        print("❌ Failed to set up environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    if not install_client_dependencies():
        print("❌ Failed to install client dependencies")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Test integration
    if not test_integration():
        print("❌ Integration test failed")
        print("   Please check your API keys and try again")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("  1. Make sure your API keys are set in server/.env")
    print("  2. Run 'python sesame.py run' in the server directory")
    print("  3. Run 'npm run dev' in the client directory")
    print("  4. Open your browser and test the voice chat functionality")
    print("\n📚 For more information, see TTS_LLM_STT_README.md")


if __name__ == "__main__":
    main()
