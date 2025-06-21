#!/usr/bin/env python3
"""
Test script for eMCeeP Twilio Webhook Server
Tests the webhook endpoints and Langflow connectivity
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', f"http://localhost:{os.getenv('WEBHOOK_PORT', '5000')}")

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Langflow URL: {data.get('langflow_url')}")
            print(f"   Flow ID: {data.get('langflow_flow_id')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_langflow_connectivity():
    """Test Langflow connectivity"""
    print("\n🔍 Testing Langflow connectivity...")
    try:
        response = requests.get(f"{WEBHOOK_BASE_URL}/test-langflow")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Langflow connectivity test passed")
            print(f"   Response: {data.get('langflow_response')}")
            return True
        else:
            print(f"❌ Langflow test failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error')}")
                except:
                    print(f"   Response: {response.text}")
            else:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Langflow test error: {e}")
        return False

def test_sms_webhook():
    """Test SMS webhook with sample data"""
    print("\n🔍 Testing SMS webhook...")
    try:
        # Simulate Twilio SMS webhook data
        webhook_data = {
            'From': '+1234567890',
            'Body': 'Hello, what time does the keynote start?',
            'MessageSid': 'test_message_123',
            'AccountSid': 'test_account'
        }
        
        response = requests.post(
            f"{WEBHOOK_BASE_URL}/sms",
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            print(f"✅ SMS webhook test passed")
            print(f"   Response: {response.text}")
            return True
        else:
            print(f"❌ SMS webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ SMS webhook test error: {e}")
        return False

def test_voice_webhook():
    """Test voice webhook with sample data"""
    print("\n🔍 Testing voice webhook...")
    try:
        # Simulate Twilio voice webhook data
        webhook_data = {
            'From': '+1234567890',
            'CallSid': 'test_call_123',
            'AccountSid': 'test_account'
        }
        
        response = requests.post(
            f"{WEBHOOK_BASE_URL}/voice",
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            print(f"✅ Voice webhook test passed")
            print(f"   TwiML Response generated successfully")
            return True
        else:
            print(f"❌ Voice webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Voice webhook test error: {e}")
        return False

def test_langflow_direct():
    """Test Langflow directly (bypassing webhook server)"""
    print("\n🔍 Testing Langflow directly...")
    
    langflow_url = os.getenv('LANGFLOW_URL', 'http://localhost:7860')
    langflow_flow_id = os.getenv('LANGFLOW_FLOW_ID', 'your-flow-id')
    
    if not langflow_flow_id or langflow_flow_id == 'your-flow-id':
        print("⚠️  LANGFLOW_FLOW_ID not set, skipping direct test")
        return True
    
    try:
        # Test the exact format from the example
        url = f"{langflow_url}/api/v1/run/{langflow_flow_id}"
        payload = {
            "input_value": "Hello, this is a test message from the webhook test script",
            "output_type": "chat",
            "input_type": "chat"
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Direct Langflow test passed")
        print(f"   Raw response: {result}")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Langflow at {langflow_url}")
        print("   Make sure Langflow is running: langflow run --host 0.0.0.0 --port 7860")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Direct Langflow test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Direct Langflow test error: {e}")
        return False

def show_webhook_urls():
    """Show the webhook URLs for Twilio configuration"""
    print("\n📋 Webhook URLs for Twilio Configuration:")
    print("="*50)
    base_url = os.getenv('WEBHOOK_PUBLIC_URL', 'https://your-domain.ngrok.io')
    print(f"SMS Webhook URL: {base_url}/sms")
    print(f"Voice Webhook URL: {base_url}/voice")
    print()
    print("💡 Tips:")
    print("1. Use ngrok for local testing: ngrok http 5000")
    print("2. Update WEBHOOK_PUBLIC_URL in .env with your ngrok URL")
    print("3. Configure these URLs in your Twilio phone number settings")

def main():
    """Run all tests"""
    print("🎤 eMCeeP Webhook Server Tests")
    print("="*50)
    
    # Check if server is running
    try:
        requests.get(f"{WEBHOOK_BASE_URL}/health", timeout=5)
    except requests.exceptions.RequestException:
        print(f"❌ Webhook server not running at {WEBHOOK_BASE_URL}")
        print("Please start the server first: python scripts/twilio_webhook_server.py")
        return False
    
    # Run tests
    tests = [
        test_health_endpoint,
        test_langflow_direct,
        test_langflow_connectivity,
        test_sms_webhook,
        test_voice_webhook
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Webhook server is ready.")
    else:
        print("⚠️  Some tests failed. Check your configuration.")
    
    show_webhook_urls()
    
    return passed == len(tests)

if __name__ == "__main__":
    main() 