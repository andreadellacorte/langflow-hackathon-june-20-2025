import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_mistral_connection():
    """Test Mistral API connection and response"""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Simple response
    data = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": "You are eMCeeP, an event management AI assistant."},
            {"role": "user", "content": "What's the WiFi password for the event?"}
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print("✅ Mistral API test successful")
        print(f"Response: {result['choices'][0]['message']['content']}")
        return True
    except Exception as e:
        print(f"❌ Mistral API test failed: {e}")
        return False

def test_event_command():
    """Test event management command processing"""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are eMCeeP, an AI event management assistant. 
Your job is to help event organizers make changes to events efficiently.

When processing commands:
1. Identify what needs to change (time, location, speaker, etc.)
2. Extract specific parameters (old value, new value)
3. Consider impact on other schedule items
4. Generate appropriate notifications for attendees

Always confirm changes clearly and ask if you should proceed with notifications."""
    
    test_command = "Move the keynote from 10:00 AM to 10:30 AM and notify all attendees"
    
    data = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_command}
        ],
        "max_tokens": 200
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print("✅ Event command test successful")
        print(f"Command: {test_command}")
        print(f"Response: {result['choices'][0]['message']['content']}")
        return True
    except Exception as e:
        print(f"❌ Event command test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Testing eMCeeP Mistral Integration...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ MISTRAL_API_KEY not found in environment variables")
        print("Please set your API key in .env file")
        exit(1)
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Run tests
    test1_success = test_mistral_connection()
    print()
    test2_success = test_event_command()
    
    print("\n" + "=" * 50)
    if test1_success and test2_success:
        print("🎉 All tests passed! eMCeeP is ready for integration.")
    else:
        print("⚠️  Some tests failed. Check your API configuration.") 