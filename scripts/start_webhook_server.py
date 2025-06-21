#!/usr/bin/env python3
"""
eMCeeP Webhook Server Startup Script
Provides easy startup with configuration validation
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check required Twilio variables
    twilio_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_PHONE_NUMBER'
    ]
    
    missing_twilio = [var for var in twilio_vars if not os.getenv(var)]
    if missing_twilio:
        print(f"❌ Missing Twilio variables: {', '.join(missing_twilio)}")
        return False
    
    # Check Langflow configuration
    langflow_url = os.getenv('LANGFLOW_URL', 'http://localhost:7860')
    langflow_flow_id = os.getenv('LANGFLOW_FLOW_ID')
    
    if not langflow_flow_id or langflow_flow_id == 'your-flow-id':
        print("⚠️  LANGFLOW_FLOW_ID not set. You'll need to set this after creating your flow.")
    
    print(f"✅ Twilio configuration found")
    print(f"   Phone: {os.getenv('TWILIO_PHONE_NUMBER')}")
    print(f"✅ Langflow configuration")
    print(f"   URL: {langflow_url}")
    print(f"   Flow ID: {langflow_flow_id or 'Not set'}")
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import flask
        import twilio
        import requests
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def start_development_server():
    """Start the development server"""
    print("\n🚀 Starting eMCeeP Webhook Server...")
    
    port = os.getenv('WEBHOOK_PORT', '5000')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Endpoints:")
    print(f"     Health: http://localhost:{port}/health")
    print(f"     SMS: http://localhost:{port}/sms")
    print(f"     Voice: http://localhost:{port}/voice")
    print(f"     Test: http://localhost:{port}/test-langflow")
    
    # Import and run the webhook server
    webhook_script = Path(__file__).parent / "twilio_webhook_server.py"
    
    try:
        subprocess.run([sys.executable, str(webhook_script)], check=True)
    except KeyboardInterrupt:
        print("\n👋 Webhook server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    
    return True

def start_production_server():
    """Start the production server with Gunicorn"""
    print("\n🚀 Starting production server with Gunicorn...")
    
    port = os.getenv('WEBHOOK_PORT', '5000')
    workers = os.getenv('GUNICORN_WORKERS', '2')
    
    try:
        subprocess.run([
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', workers,
            '--timeout', '30',
            '--access-logfile', 'logs/access.log',
            '--error-logfile', 'logs/error.log',
            'scripts.twilio_webhook_server:app'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Production server stopped")
    except subprocess.CalledProcessError:
        print("❌ Production server failed. Make sure Gunicorn is installed.")
        print("Run: pip install gunicorn")
        return False
    except FileNotFoundError:
        print("❌ Gunicorn not found. Install it with: pip install gunicorn")
        return False
    
    return True

def show_ngrok_setup():
    """Show ngrok setup instructions"""
    print("\n📡 For local development with Twilio webhooks:")
    print("="*50)
    print("1. Install ngrok: https://ngrok.com/download")
    print("2. Start ngrok: ngrok http 5000")
    print("3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)")
    print("4. Configure in your Twilio phone number:")
    print("   - SMS webhook: https://abc123.ngrok.io/sms")
    print("   - Voice webhook: https://abc123.ngrok.io/voice")
    print("5. Update WEBHOOK_PUBLIC_URL in .env with your ngrok URL")

def main():
    """Main startup function"""
    print("🎤 eMCeeP Webhook Server Startup")
    print("="*50)
    
    # Check environment and dependencies
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return False
    
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install required packages.")
        return False
    
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    # Choose server type
    print("\n🔧 Server options:")
    print("1. Development server (Flask built-in)")
    print("2. Production server (Gunicorn)")
    print("3. Show ngrok setup instructions")
    
    choice = input("\nChoose option (1/2/3): ").strip()
    
    if choice == '1':
        return start_development_server()
    elif choice == '2':
        return start_production_server()
    elif choice == '3':
        show_ngrok_setup()
        return True
    else:
        print("Invalid choice. Starting development server...")
        return start_development_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 