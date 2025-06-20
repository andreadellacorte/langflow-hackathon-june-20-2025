#!/usr/bin/env python3
"""
OpenAI API test for eMCeeP project
"""

import os
import openai
from dotenv import load_dotenv

load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection and response"""
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple eMCeeP query
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are eMCeeP, an event management AI assistant."},
                {"role": "user", "content": "What's the WiFi password for the event?"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        print("✅ OpenAI API test successful")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_event_command():
    """Test event management command processing with OpenAI"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        system_prompt = """You are eMCeeP, an AI event management assistant. 
Your job is to help event organizers make changes to events efficiently.

When processing commands:
1. Identify what needs to change (time, location, speaker, etc.)
2. Extract specific parameters (old value, new value)
3. Consider impact on other schedule items
4. Generate appropriate notifications for attendees

Always confirm changes clearly and ask if you should proceed with notifications."""
        
        test_command = "Move the keynote from 10:00 AM to 10:30 AM and notify all attendees"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_command}
            ],
            max_tokens=200,
            temperature=0.5
        )
        
        print("✅ Event command test successful")
        print(f"Command: {test_command}")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Event command test failed: {e}")
        return False

def test_json_parsing():
    """Test OpenAI's ability to return structured JSON for command parsing"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        system_prompt = """You are a command parser for eMCeeP event management system.
Parse voice commands and return ONLY valid JSON with this structure:
{
  "action": "reschedule|relocate|notify|cancel",
  "target": "session name or id",
  "new_value": "new time or location",
  "confidence": "high|medium|low"
}"""
        
        test_command = "Reschedule the opening keynote to 11 AM"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_command}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        import json
        response_content = response.choices[0].message.content
        if response_content:
            parsed_response = json.loads(response_content)
        else:
            raise ValueError("Empty response from OpenAI")
        
        print("✅ JSON parsing test successful")
        print(f"Command: {test_command}")
        print(f"Parsed JSON: {json.dumps(parsed_response, indent=2)}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed - invalid JSON: {e}")
        print(f"Raw response: {response.choices[0].message.content}")
        return False
    except Exception as e:
        print(f"❌ JSON parsing test failed: {e}")
        return False

def test_faq_enhancement():
    """Test OpenAI's ability to enhance FAQ responses contextually"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Simulate event data context
        event_context = """
        Event: Tech Conference 2025
        Date: June 21, 2025
        Venue: Downtown Convention Center
        WiFi: EventWiFi / Connect2025
        Parking: Free in garage levels 2-4
        """
        
        system_prompt = f"""You are eMCeeP, helping attendees at this event:
        {event_context}
        
        Answer questions helpfully and conversationally, using the event details when relevant."""
        
        test_question = "I can't find parking anywhere, help!"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_question}
            ],
            max_tokens=150,
            temperature=0.6
        )
        
        print("✅ FAQ enhancement test successful")
        print(f"Question: {test_question}")
        print(f"Enhanced response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ FAQ enhancement test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing eMCeeP OpenAI Integration...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your API key in .env file")
        exit(1)
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Run all tests
    tests = [
        ("Basic Connection", test_openai_connection),
        ("Event Commands", test_event_command),
        ("JSON Parsing", test_json_parsing),
        ("FAQ Enhancement", test_faq_enhancement)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        success = test_func()
        results.append(success)
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! eMCeeP is ready for OpenAI integration.")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Check your API configuration.")
        
    print("\n💡 Next steps:")
    print("   1. Update Langflow flows to use OpenAI components")
    print("   2. Test with real event scenarios")
    print("   3. Configure voice command processing") 