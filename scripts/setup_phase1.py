#!/usr/bin/env python3
"""
eMCeeP Phase 1 Setup Script
Automates the initial setup process for the demo environment
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_virtual_environment():
    """Check if virtual environment is activated"""
    print("📦 Checking virtual environment...")
    if sys.prefix == sys.base_prefix:
        print("⚠️  Virtual environment not detected")
        print("Please run: source .venv/bin/activate")
        return False
    print("✅ Virtual environment is active")
    return True

def install_requirements():
    """Install required packages"""
    print("📥 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("🔧 Checking environment configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found")
        print("Creating .env from template...")
        
        # Copy template
        template_path = Path(".env.template")
        if template_path.exists():
            shutil.copy(template_path, env_path)
            print("✅ .env file created from template")
            print("❗ Please edit .env and add your API keys")
            return False
        else:
            print("❌ .env.template not found")
            return False
    
    # Check for required variables
    required_vars = [
        "MISTRAL_API_KEY",
        "TWILIO_ACCOUNT_SID", 
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    
    missing_vars = []
    with open(env_path) as f:
        env_content = f.read()
        for var in required_vars:
            if f"{var}=your_" in env_content or f"{var}=" not in env_content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing API keys in .env: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def validate_event_data():
    """Validate event.json file"""
    print("📊 Validating event data...")
    
    event_path = Path("data/event.json")
    if not event_path.exists():
        print("❌ data/event.json not found")
        return False
    
    try:
        with open(event_path) as f:
            event_data = json.load(f)
        
        # Basic validation
        required_fields = ["event_id", "name", "schedule", "attendees", "faq"]
        for field in required_fields:
            if field not in event_data:
                print(f"❌ Missing required field in event.json: {field}")
                return False
        
        print(f"✅ Event data valid ({len(event_data['schedule'])} events, {len(event_data['attendees'])} attendees)")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in event.json: {e}")
        return False

def test_langflow_installation():
    """Test if langflow is installed and accessible"""
    print("🔬 Testing Langflow installation...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "langflow", "--version"], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"✅ Langflow {version} is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Langflow not found or not working")
        return False

def create_demo_directories():
    """Create necessary directories"""
    print("📁 Creating directory structure...")
    
    directories = ["flows", "data", "scripts", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directory structure created")
    return True

def run_api_tests():
    """Run basic API tests if credentials are available"""
    print("🧪 Running API tests...")
    
    # Test Mistral API
    try:
        result = subprocess.run([sys.executable, "scripts/test_mistral.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Mistral API test passed")
        else:
            print("⚠️  Mistral API test issues (check your API key)")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  Could not run Mistral API test")
    
    # Test Twilio (connection only, no SMS)
    try:
        result = subprocess.run([sys.executable, "scripts/test_twilio.py"], 
                              input="n\n", capture_output=True, text=True, timeout=30)
        if "connection successful" in result.stdout.lower():
            print("✅ Twilio connection test passed")
        else:
            print("⚠️  Twilio connection test issues")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  Could not run Twilio connection test")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Phase 1 Setup Complete!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. 🔑 Edit .env file with your actual API keys")
    print("2. 🧪 Run test scripts:")
    print("   python scripts/test_mistral.py")
    print("   python scripts/test_twilio.py")
    print("3. 🚀 Start Langflow:")
    print("   langflow run --host 0.0.0.0 --port 7860")
    print("4. 🌐 Open browser to: http://localhost:7860")
    print("5. 📖 Follow Phase 1 implementation guide in docs/phase1.md")
    print()
    print("Ready to build your eMCeeP demo! 🎤")

def main():
    """Main setup function"""
    print("🎤 eMCeeP Phase 1 Setup")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Directory Structure", create_demo_directories),
        ("Requirements Installation", install_requirements),
        ("Langflow Installation", test_langflow_installation),
        ("Environment Variables", check_env_file),
        ("Event Data", validate_event_data),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        if not check_func():
            all_passed = False
    
    if all_passed:
        print(f"\n--- API Tests ---")
        run_api_tests()
        print_next_steps()
    else:
        print("\n❌ Setup incomplete. Please fix the issues above and run again.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 