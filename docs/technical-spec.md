# eMCeeP - Technical Specification (6-Hour Sprint)

**Project**: eMCeeP - AI Event Management Assistant  
**Hackathon Duration**: 6 hours remaining  
**Realistic Scope**: Core demo with 3 working scenarios  

## 🎯 Architecture Overview (Simplified)

```
Langflow Web UI → 3 Core Flows → Mistral.AI + Twilio
                       ↓
                 Demo Event JSON
```

## 🔧 Technology Stack (Minimal)

### **Primary Platform: Langflow**
- **Role**: Visual AI workflow builder and demo interface
- **Why**: Rapid development, visual appeal for judges, built-in chat UI
- **Installation**: `pip install langflow`

### **AI Integration: Mistral.AI**
- **Model**: Mistral-7B or Mistral-Medium via API
- **Role**: Command parsing and FAQ responses
- **Integration**: Direct API calls from Langflow components

### **Communication: Twilio SMS**
- **Service**: SMS API only (no voice for time constraints)
- **Role**: Send real SMS notifications to demo phones
- **Integration**: Twilio REST API from Langflow

### **Data Storage: JSON Files**
- **Structure**: Simple event.json with attendees and schedule
- **Why**: No database setup time, easy demo data management
- **Location**: Local file system

## 🚀 Implementation Plan (6 Hours)

### **Phase 1: Foundation Setup (1.5 hours)**
```bash
# Quick setup commands
pip install langflow mistralai twilio
export MISTRAL_API_KEY="your_key"
export TWILIO_ACCOUNT_SID="your_sid"
export TWILIO_AUTH_TOKEN="your_token"
langflow run
```

**Tasks:**
- Install and launch Langflow
- Create Mistral.AI and Twilio accounts
- Set up API credentials
- Create basic demo event JSON file

### **Phase 2: Core Flows (3 hours)**
Build exactly 3 Langflow flows:

#### **Flow 1: Command Processor**
```
Chat Input → Mistral Command Parser → Event Updater → SMS Sender → Response
```

#### **Flow 2: FAQ Bot**
```
Chat Input → Mistral FAQ → Event Data Lookup → Response
```

#### **Flow 3: Demo Controller**
```
Mode Selector → Route to Command Processor OR FAQ Bot
```

### **Phase 3: Demo Polish (1.5 hours)**
- Load realistic demo data
- Test all scenarios end-to-end
- Create backup responses for demo failures
- Prepare presentation talking points

## 📊 Data Structure (Minimal)

### event.json
```json
{
  "name": "Tech Conference 2025",
  "date": "2025-06-21",
  "location": "Downtown Convention Center",
  "schedule": [
    {
      "id": "reg",
      "time": "09:00",
      "title": "Registration",
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
      "id": "break1",
      "time": "11:00", 
      "title": "Coffee Break",
      "location": "Lobby"
    }
  ],
  "attendees": [
    {
      "name": "John Doe",
      "phone": "+1234567890",
      "email": "john@example.com"
    },
    {
      "name": "Jane Smith", 
      "phone": "+1234567891",
      "email": "jane@example.com"
    }
  ],
  "faq": {
    "registration": "Registration starts at 9:00 AM in the main lobby. Please bring your confirmation email.",
    "parking": "Free parking is available in the convention center garage on levels 2-4.",
    "wifi": "WiFi network: EventWiFi, Password: Connect2025",
    "lunch": "Lunch will be provided at 12:30 PM in the exhibition hall.",
    "location": "Downtown Convention Center, 123 Main Street, Conference Room A"
  }
}
```

## 🛠 Langflow Component Details

### **Custom Component: Command Parser**
```python
import json
import re
from langflow import CustomComponent

class CommandParser(CustomComponent):
    def process(self, command: str) -> dict:
        # Use Mistral to parse command
        prompt = f"""
        Parse this event management command: "{command}"
        
        Extract:
        - action (reschedule/relocate/notify/cancel)
        - target (session name or id)
        - new_value (new time/location)
        
        Return JSON format: {{"action": "", "target": "", "new_value": ""}}
        """
        
        response = self.query_mistral(prompt)
        try:
            return json.loads(response)
        except:
            return {"error": "Could not parse command"}
```

### **Custom Component: Event Updater**
```python
import json

class EventUpdater(CustomComponent):
    def process(self, parsed_command: dict, event_file: str = "event.json") -> dict:
        with open(event_file, 'r') as f:
            event = json.load(f)
        
        if parsed_command["action"] == "reschedule":
            # Find and update session time
            for session in event["schedule"]:
                if parsed_command["target"].lower() in session["title"].lower():
                    session["time"] = parsed_command["new_value"]
                    break
        
        # Save updated event
        with open(event_file, 'w') as f:
            json.dump(event, f, indent=2)
            
        return {"status": "updated", "event": event}
```

### **Custom Component: SMS Sender**
```python
from twilio.rest import Client
import os

class SMSSender(CustomComponent):
    def process(self, message: str, event_data: dict) -> dict:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        sent_count = 0
        for attendee in event_data["attendees"]:
            try:
                client.messages.create(
                    body=message,
                    from_='+1234567890',  # Your Twilio number
                    to=attendee["phone"]
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send to {attendee['phone']}: {e}")
        
        return {"sent": sent_count, "total": len(event_data["attendees"])}
```

## 🎭 Demo Scenarios (Scripted)

### **Demo Setup**
- Pre-load event.json with "Tech Conference 2025"
- Use 3-5 real phone numbers for SMS demo
- Have Langflow running with flows visible

### **Scenario 1: Schedule Change (90 seconds)**
```
Input: "eMCeeP, the keynote speaker is running late. Move the opening keynote from 10 AM to 10:30 AM and notify everyone."

Expected Flow:
1. Command Parser extracts: reschedule, keynote, 10:30
2. Event Updater modifies event.json
3. SMS Sender sends: "Update: Opening Keynote moved to 10:30 AM"
4. Response: "Done! Keynote rescheduled to 10:30 AM. Sent SMS to 50 attendees."
```

### **Scenario 2: Attendee FAQ (60 seconds)**
```
Input: "What time is registration?"

Expected Flow:
1. FAQ Bot processes question
2. Mistral matches to registration FAQ
3. Response: "Registration for Tech Conference 2025 starts at 9:00 AM in the main lobby. Please bring your confirmation email."
```

### **Scenario 3: Location Change (90 seconds)**
```  
Input: "eMCeeP, we need to move the coffee break to the exhibition hall and tell everyone."

Expected Flow:
1. Command Parser extracts: relocate, coffee break, exhibition hall
2. Event Updater modifies location
3. SMS Sender sends location update
4. Response: "Coffee break moved to exhibition hall. All attendees notified."
```

## 🔌 API Integration Code

### **Mistral.AI Integration**
```python
import requests
import os

def query_mistral(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }
    
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    return response.json()["choices"][0]["message"]["content"]
```

### **Twilio SMS Integration**
```python
from twilio.rest import Client
import os

def send_sms(to_number: str, message: str) -> bool:
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    
    try:
        client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=to_number
        )
        return True
    except Exception as e:
        print(f"SMS failed: {e}")
        return False
```

## 🚨 Backup Plans

### **If Mistral.AI Fails:**
```python
def fallback_parser(command: str) -> dict:
    if "move" in command.lower() and "keynote" in command.lower():
        return {"action": "reschedule", "target": "keynote", "new_value": "10:30"}
    elif "registration" in command.lower():
        return {"action": "faq", "answer": "Registration starts at 9:00 AM"}
    return {"error": "Command not recognized"}
```

### **If Twilio Fails:**
```python
def simulate_sms(message: str, count: int) -> dict:
    print(f"SMS SIMULATION: Would send '{message}' to {count} attendees")
    return {"sent": count, "simulated": True}
```

### **If Langflow Fails:**
- Simple Flask app with same functionality
- Console-based demo
- Focus on AI parsing capabilities

## 📋 Success Checklist

### **Must Have (Demo Requirements)**
- [ ] Langflow running with 3 visible flows
- [ ] Mistral.AI parsing commands correctly
- [ ] Twilio sending real SMS to demo phones
- [ ] 3 scenarios executing without errors
- [ ] Event data updating in real-time

### **Nice to Have (If Time Permits)**
- [ ] Voice simulation with browser speech API
- [ ] Error handling with user-friendly messages
- [ ] Multiple demo events
- [ ] Advanced command types

## 🏆 Why This Approach Wins

**For Technical Judges:**
- Clean, visual Langflow implementation
- Real API integrations (not mocked)
- Practical AI application
- Working end-to-end system

**For Business Judges:**
- Solves real event management problems
- Immediate practical value
- Scalable concept demonstration
- Professional execution

**For General Audience:**
- "Wow, this actually works!"
- Tangible results (real SMS)
- Easy to understand value
- Impressive AI interaction

---

*This technical specification is optimized for successful 6-hour development and impressive demo delivery while maintaining core product value.* 