# eMCeeP - Phase 1 Implementation Plan

**Duration**: 1.5 hours  
**Goal**: Set up foundation for core demo functionality  
**Success Criteria**: Langflow running with basic AI integration and demo data loaded  

## 🎯 Phase 1 Overview

This phase establishes the technical foundation needed for the 3 core demo scenarios:
1. **Voice Command Processing** - "eMCeeP, move the keynote from 2 PM to 3 PM"
2. **Attendee Q&A** - "What's the WiFi password?"
3. **Smart Escalation** - Detecting when organizer attention is needed

Focus on getting basic components working rather than perfection.

## 📋 Setup Tasks

### Environment Setup (20 minutes)
- [x] **Install Python dependencies**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install langflow mistralai twilio requests flask fastapi
  ```
- [x] **Create project directory structure**
  ```bash
  mkdir -p flows data scripts
  ```
- [ ] **Set up environment variables**
  Create `.env` file:
  ```bash
  # AI API Keys
  MISTRAL_API_KEY=your_mistral_api_key
  OPENAI_API_KEY=your_openai_key_optional
  
  # Twilio Configuration
  TWILIO_ACCOUNT_SID=your_twilio_sid
  TWILIO_AUTH_TOKEN=your_twilio_token
  TWILIO_PHONE_NUMBER=your_twilio_number
  
  # Event Data
  EVENT_DATA_PATH=./data/event.json
  
  # Langflow Settings
  LANGFLOW_HOST=0.0.0.0
  LANGFLOW_PORT=7860
  ```

### Account Setup (15 minutes)
- [ ] **Create Mistral.AI account**
  - Sign up at https://console.mistral.ai/
  - Generate API key
  - Choose "mistral-small" model for demo (good balance of cost/performance)
  - Test with simple curl command:
  ```bash
  curl -X POST "https://api.mistral.ai/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $MISTRAL_API_KEY" \
    -d '{
      "model": "mistral-small",
      "messages": [{"role": "user", "content": "Hello"}],
      "max_tokens": 100
    }'
  ```

- [ ] **Set up Twilio account**
  - Sign up at https://www.twilio.com/
  - Get free trial credits ($15 typically)
  - Get Account SID and Auth Token from console
  - Purchase/verify phone number for SMS
  - Test SMS sending:
  ```bash
  curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
    --data-urlencode "From=$TWILIO_PHONE_NUMBER" \
    --data-urlencode "Body=eMCeeP test message" \
    --data-urlencode "To=+1234567890" \
    -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
  ```

### Demo Data Creation (25 minutes)
- [x] **Create comprehensive event.json file**

- [ ] **Create attendee contact database (JSON)**
  ```json
  {
    "contacts": [
      {
        "phone": "+1234567890",
        "name": "John Doe",
        "preference": "sms",
        "timezone": "EST"
      },
      {
        "phone": "+1234567891", 
        "name": "Jane Smith",
        "preference": "sms",
        "timezone": "EST"
      }
    ]
  }
  ```

### Langflow Launch & Initial Setup (15 minutes)
- [x] **Start Langflow server**
  ```bash
  # Make sure virtual environment is activated
  source .venv/bin/activate
  
  # Start with specific configuration
  langflow run --host 0.0.0.0 --port 7860 --env-file .env
  ```
- [ ] **Access Langflow interface**
  - Open browser to http://localhost:7860
  - Create new project: "eMCeeP Demo"
  - Explore component library
  - Test basic drag-and-drop functionality

## 🎯 Core Langflow Flows Design

### Flow 1: Event Manager Voice Commands (Priority 1)
**Purpose**: Process voice commands from event organizer

**Components needed**:
1. **Text Input** (simulating voice-to-text)
2. **Custom Python Function** - Intent classification
3. **Mistral LLM** - Command understanding
4. **Event Data Retrieval** - Load event.json
5. **Schedule Updater** - Modify event data
6. **Notification Sender** - Send updates via Twilio
7. **Response Generator** - Confirm action taken

**Implementation Steps**:
- [x] **Create "Voice Command Flow"**
  - Add Text Input component
  - Configure for commands like: "Move keynote from 10:00 to 10:30"
  - Connect to LLM for intent extraction
  
- [ ] **Add Intent Classification Function**
  ```python
  def classify_intent(command: str) -> dict:
      """Extract intent and parameters from voice command"""
      # Use regex or simple parsing for demo
      patterns = {
          'time_change': r'move (\w+) from (\d{1,2}:\d{2}) to (\d{1,2}:\d{2})',
          'location_change': r'move (\w+) to (.+)',
          'speaker_change': r'replace (\w+) with (\w+)',
          'cancel_event': r'cancel (\w+)'
      }
      
      for intent, pattern in patterns.items():
          match = re.search(pattern, command.lower())
          if match:
              return {
                  'intent': intent,
                  'params': list(match.groups()),
                  'original_command': command
              }
      
      return {'intent': 'unknown', 'params': [], 'original_command': command}
  ```

- [ ] **Configure LLM for Event Management**
  - Model: mistral-small
  - System prompt: 
  ```
  You are eMCeeP, an AI event management assistant. 
  Your job is to help event organizers make changes to events efficiently.
  
  When processing commands:
  1. Identify what needs to change (time, location, speaker, etc.)
  2. Extract specific parameters (old value, new value)
  3. Consider impact on other schedule items
  4. Generate appropriate notifications for attendees
  
  Always confirm changes clearly and ask if you should proceed with notifications.
  ```

### Flow 2: Attendee Q&A System (Priority 2)  
**Purpose**: Answer common attendee questions instantly

**Components needed**:
1. **Text Input** (attendee question)
2. **FAQ Matcher** - Check against known questions
3. **Mistral LLM** - Generate contextual answers
4. **Event Data Lookup** - Access event details
5. **Response Formatter** - Format for SMS/chat
6. **Escalation Trigger** - Detect complex queries

**Implementation Steps**:
- [ ] **Create "FAQ Flow"**
  - Input: Attendee question via SMS/web
  - Process: Match against FAQ database
  - Output: Instant response or escalation
  
- [ ] **Add FAQ Matching Function**
  ```python
  def match_faq(question: str, faq_data: dict) -> dict:
      """Match question against FAQ database"""
      question_lower = question.lower()
      
      # Simple keyword matching for demo
      keyword_map = {
          'wifi': 'wifi',
          'password': 'wifi', 
          'internet': 'wifi',
          'parking': 'parking',
          'location': 'location',
          'address': 'location',
          'lunch': 'lunch',
          'food': 'lunch',
          'schedule': 'schedule',
          'time': 'schedule',
          'registration': 'registration',
          'check': 'registration'
      }
      
      for keyword, faq_key in keyword_map.items():
          if keyword in question_lower:
              return {
                  'matched': True,
                  'answer': faq_data.get(faq_key, 'Information not available'),
                  'confidence': 0.8,
                  'source': 'faq'
              }
      
      return {'matched': False, 'confidence': 0.0, 'source': 'none'}
  ```

### Flow 3: Smart Escalation System (Priority 3)
**Purpose**: Detect when organizer intervention is needed

**Components needed**:
1. **Question Analyzer** - Analyze complexity/urgency
2. **Frequency Counter** - Track repeated questions  
3. **Sentiment Analysis** - Detect frustration
4. **Escalation Decision** - Determine if organizer needed
5. **Alert Sender** - Notify organizer via SMS/call

**Implementation Steps**:
- [ ] **Create "Escalation Flow"**
- [ ] **Add Question Analysis Function**
  ```python
  def should_escalate(question: str, context: dict) -> bool:
      """Determine if question needs organizer attention"""
      
      # Escalation triggers
      escalation_keywords = [
          'emergency', 'urgent', 'problem', 'issue', 'broken',
          'not working', 'angry', 'complaint', 'refund', 'cancel'
      ]
      
      question_lower = question.lower()
      
      # Check for urgent keywords
      if any(keyword in question_lower for keyword in escalation_keywords):
          return True
      
      # Check frequency (if same question asked >5 times)
      if context.get('question_frequency', 0) > 5:
          return True
      
      # Check if answer confidence is low
      if context.get('answer_confidence', 1.0) < 0.5:
          return True
          
      return False
  ```

### Langflow Flow Testing
- [ ] **Test Flow 1: Voice Commands**
  - Input: "Move the keynote from 10:00 to 10:30"
  - Expected: Schedule updated, attendees notified
  - Verify: JSON file updated, SMS sent

- [ ] **Test Flow 2: FAQ Responses**  
  - Input: "What's the WiFi password?"
  - Expected: Instant response with password
  - Verify: Correct answer retrieved from event data

- [ ] **Test Flow 3: Escalation Detection**
  - Input: "The microphone is broken and people are complaining!"
  - Expected: Organizer immediately notified
  - Verify: Escalation alert sent

## 📊 Validation Checklist

### Technical Validation
- [ ] **Langflow server running stable** (no crashes after 10 minutes)
- [ ] **All APIs responding correctly** (< 3 second response time)
- [ ] **Demo data file loads without errors** (valid JSON, all fields present)
- [ ] **Environment variables properly set** (all required keys present)
- [ ] **No critical dependency issues** (all imports working)

### Demo Preparation
- [ ] **Demo phone numbers ready for SMS** (at least 2 test numbers)
- [ ] **Test scenarios prepared and rehearsed**
  - Scenario 1: "eMCeeP, move lunch from 12:30 to 1:00 PM due to speaker delay"
  - Scenario 2: Attendee asks "Where is the parking?"
  - Scenario 3: "There's a fire alarm going off, what do I do?"
- [ ] **Backup plans prepared**
  - Manual responses if AI fails
  - Pre-written SMS templates
  - Error handling for API failures
- [ ] **Demo script written** (what to say, which flows to show)

### Performance Validation
- [ ] **Response time < 5 seconds** for simple queries
- [ ] **SMS delivery < 30 seconds** 
- [ ] **Event data updates persist** (changes saved to file)
- [ ] **Error handling works** (graceful failure messages)

## 🚀 Next Steps After Phase 1

After completing Phase 1, you should have:
- ✅ Working Langflow installation with 3 core flows
- ✅ Event data management system
- ✅ SMS notification capability  
- ✅ AI-powered question answering
- ✅ Basic escalation detection

**Ready for Phase 2**: Voice integration, advanced AI features, and polished demo presentation.

## 🆘 Troubleshooting Guide

### Common Issues:
1. **Langflow won't start**: Check Python version (3.10+), dependencies installed
2. **Mistral API errors**: Verify API key, check rate limits
3. **Twilio SMS fails**: Confirm account verified, phone number active
4. **Event data not loading**: Validate JSON syntax, check file permissions
5. **Flows not connecting**: Ensure component compatibility, check data types

### Quick Fixes:
```bash
# Reset environment
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Check API keys
echo $MISTRAL_API_KEY | head -c 20
curl -I https://api.mistral.ai/v1/models -H "Authorization: Bearer $MISTRAL_API_KEY"

# Restart langflow
pkill -f langflow
langflow run --host 0.0.0.0 --port 7860
```

---

*Complete all checkboxes before moving to Phase 2. If stuck on any item for more than 10 minutes, move to troubleshooting or ask for help.* 