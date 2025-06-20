# eMCeeP - Phase 1 Implementation Plan

**Duration**: 1.5 hours  
**Goal**: Set up foundation for core demo functionality  
**Success Criteria**: Langflow running with basic AI integration and demo data loaded  

## 🎯 Phase 1 Overview

This phase establishes the technical foundation needed for the 3 core demo scenarios. Focus on getting basic components working rather than perfection.

## 📋 Setup Tasks

### Environment Setup (20 minutes)
- [x] **Install Python dependencies**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install langflow mistralai twilio requests
  ```
- [ ] **Create project directory structure**
  ```bash
  mkdir emceep-demo
  cd emceep-demo
  mkdir data flows
  ```
- [ ] **Set up environment variables**
  ```bash
  export MISTRAL_API_KEY="your_mistral_api_key"
  export TWILIO_ACCOUNT_SID="your_twilio_sid" 
  export TWILIO_AUTH_TOKEN="your_twilio_token"
  export TWILIO_PHONE_NUMBER="your_twilio_number"
  ```

### Account Setup (15 minutes)
- [ ] **Create Mistral.AI account**
  - Sign up at https://console.mistral.ai/
  - Generate API key
  - Test with simple curl command
- [ ] **Set up Twilio account**
  - Sign up at https://www.twilio.com/
  - Get Account SID and Auth Token
  - Purchase/verify phone number for SMS
  - Test SMS sending with sample message

### Demo Data Creation (25 minutes)
- [ ] **Create event.json file**
  ```json
  {
    "name": "Tech Conference 2025",
    "date": "2025-06-21",
    "location": "Downtown Convention Center",
    "schedule": [
      {
        "id": "registration",
        "time": "09:00",
        "title": "Registration & Check-in",
        "location": "Main Lobby"
      },
      {
        "id": "keynote",
        "time": "10:00", 
        "title": "Opening Keynote",
        "location": "Main Hall",
        "speaker": "Dr. Sarah Chen"
      },
      {
        "id": "coffee_break",
        "time": "11:00",
        "title": "Coffee Break",
        "location": "Lobby"
      },
      {
        "id": "panel",
        "time": "11:30",
        "title": "AI Innovation Panel",
        "location": "Main Hall"
      },
      {
        "id": "lunch",
        "time": "12:30",
        "title": "Networking Lunch",
        "location": "Exhibition Hall"
      }
    ],
    "attendees": [
      {"name": "John Doe", "phone": "+1234567890", "email": "john@example.com"},
      {"name": "Jane Smith", "phone": "+1234567891", "email": "jane@example.com"},
      {"name": "Mike Johnson", "phone": "+1234567892", "email": "mike@example.com"}
    ],
    "faq": {
      "registration": "Registration starts at 9:00 AM in the main lobby. Please bring your confirmation email and ID.",
      "parking": "Free parking is available in the convention center garage on levels 2-4. Enter from Oak Street.",
      "wifi": "WiFi network: EventWiFi, Password: Connect2025",
      "lunch": "Lunch will be provided at 12:30 PM in the exhibition hall. Dietary restrictions accommodated.",
      "location": "Downtown Convention Center, 123 Main Street, Suite 100",
      "dress_code": "Business casual attire recommended",
      "contact": "For questions, contact events@techconf.com or call (555) 123-4567"
    }
  }
  ```

### Langflow Launch (10 minutes)
- [ ] **Start Langflow server**
  ```bash
  langflow run --host 0.0.0.0 --port 7860
  ```
- [ ] **Access Langflow interface**
  - Open browser to http://localhost:7860
  - Verify interface loads correctly
  - Explore available components

### Basic Integration Tests (20 minutes)
- [ ] **Test Mistral.AI connection**
  - Create simple test script:
  ```python
  import requests
  import os
  
  def test_mistral():
      headers = {
          "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
          "Content-Type": "application/json"
      }
      data = {
          "model": "mistral-tiny",
          "messages": [{"role": "user", "content": "Hello, this is a test"}],
          "max_tokens": 50
      }
      response = requests.post(
          "https://api.mistral.ai/v1/chat/completions",
          headers=headers, json=data
      )
      print(response.json())
  
  test_mistral()
  ```
  - Verify API response
  - Note any rate limits or issues

- [ ] **Test Twilio SMS**
  - Create simple test script:
  ```python
  from twilio.rest import Client
  import os
  
  def test_sms():
      client = Client(
          os.getenv('TWILIO_ACCOUNT_SID'),
          os.getenv('TWILIO_AUTH_TOKEN')
      )
      
      message = client.messages.create(
          body="eMCeeP test message",
          from_=os.getenv('TWILIO_PHONE_NUMBER'),
          to="+1234567890"  # Replace with your test number
      )
      print(f"Message sent: {message.sid}")
  
  test_sms()
  ```
  - Send test SMS to your phone
  - Verify message received
  - Check Twilio console for delivery status

## 🔧 Langflow Component Setup

### Create Custom Components (In Langflow UI)
- [ ] **Add basic Chat Input/Output components**
  - Drag Chat Input to canvas
  - Drag Chat Output to canvas
  - Connect them for basic flow

- [ ] **Add LLM component**
  - Add OpenAI/LLM component
  - Configure for Mistral.AI endpoint
  - Test with simple prompt

- [ ] **Save initial flow**
  - Name: "Basic Test Flow"
  - Test that components connect properly
  - Verify chat interface works

## 📊 Validation Checklist

### Technical Validation
- [ ] **Langflow server running stable**
- [ ] **All APIs responding correctly**
- [ ] **Demo data file loads without errors**
- [ ] **Environment variables properly set**
- [ ] **No critical dependency issues**

### Demo Preparation
- [ ] **Demo phone numbers ready for SMS**
- [ ] **Test scenarios identified**
  - Schedule change command
  - FAQ question
  - Location update
- [ ] **Backup plans prepared**
  - Fallback responses if APIs fail
  - Error messages for common issues

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### **Langflow won't start**
```bash
# Try different port
langflow run --port 7861

# Check Python version
python --version  # Should be 3.8+

# Reinstall if needed
pip uninstall langflow
pip install langflow
```

#### **Mistral.AI API errors**
- Check API key format (starts with "sk-")
- Verify account has credits
- Try "mistral-tiny" model if others fail
- Check rate limits

#### **Twilio SMS fails**
- Verify phone number format (+1234567890)
- Check account balance
- Confirm phone number is verified
- Test with Twilio console first

#### **JSON file errors**
- Validate JSON syntax at jsonlint.com
- Check file permissions
- Ensure UTF-8 encoding

## 🎯 Success Criteria for Phase 1

At the end of 1.5 hours, you should have:
- ✅ **Langflow running** with basic interface
- ✅ **Mistral.AI responding** to test prompts
- ✅ **Twilio sending SMS** to test numbers
- ✅ **Demo event data** loaded and accessible
- ✅ **Basic flow created** in Langflow UI

## 🚀 Transition to Phase 2

Once Phase 1 is complete, you're ready to build the 3 core Langflow flows:
1. **Command Processor Flow** - Parse and execute event commands
2. **FAQ Bot Flow** - Answer attendee questions
3. **Demo Controller Flow** - Switch between organizer/attendee modes

**Time remaining for Phase 2**: 4.5 hours  
**Next focus**: Building the actual demo scenarios

---

*Complete all checkboxes before moving to Phase 2. If stuck on any item for more than 10 minutes, move to troubleshooting or ask for help.* 