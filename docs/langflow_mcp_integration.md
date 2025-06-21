# eMCeeP MCP Server Integration with Langflow

This guide explains how to use the eMCeeP Event Management MCP Server with Langflow for Flow 1 (Voice Command Processing).

## Overview

The MCP (Model Context Protocol) server provides a standardized way for Langflow to access event management capabilities:

- **Resources**: Event data (schedule, attendees, FAQ, changelog)  
- **Tools**: Intent classification, event updates, voice command processing
- **Live Updates**: Real-time access to event data with automatic persistence

## Setup

### 1. Install MCP Dependencies

```bash
pip install mcp>=1.0.0
```

### 2. Start the MCP Server

```bash
cd scripts
python event_mcp_server.py
```

The server will start and wait for connections via stdin/stdout.

### 3. Configure Langflow MCP Connection

In Langflow, add an MCP Client component and configure it to connect to the eMCeeP server:

```json
{
  "server_name": "emceep-event-manager",
  "command": ["python", "scripts/event_mcp_server.py"],
  "working_directory": ".."
}
```

## Flow 1: Voice Command Processing

### Langflow Components Setup

#### 1. Text Input Component
- **Name**: "Voice Command Input"
- **Purpose**: Capture voice commands (simulating voice-to-text)
- **Example inputs**:
  - "Move the keynote from 10:00 to 10:30"
  - "Change lunch location to the garden terrace"
  - "Cancel the afternoon workshop"

#### 2. MCP Tool Call Component 
- **Tool**: `process_voice_command`
- **Input**: Voice command text from step 1
- **Parameters**:
  ```json
  {
    "command": "{voice_command_text}",
    "auto_execute": true
  }
  ```

#### 3. Response Processing Component
- **Purpose**: Parse MCP response and format for output
- **Extracts**:
  - Intent classification result
  - Execution status  
  - Success/error messages
  - Suggested follow-up actions

#### 4. Notification Component (Optional)
- **Tool**: `update_event_time` or `update_event_location` 
- **Purpose**: Send SMS notifications for successful changes
- **Trigger**: Only when execution was successful

### Example Flow Configuration

```json
{
  "flow_name": "eMCeeP Voice Command Flow",
  "components": [
    {
      "id": "voice_input",
      "type": "TextInput",
      "config": {
        "display_name": "Voice Command",
        "placeholder": "e.g., Move keynote from 10:00 to 10:30"
      }
    },
    {
      "id": "mcp_client", 
      "type": "MCPClient",
      "config": {
        "server_config": {
          "command": ["python", "scripts/event_mcp_server.py"]
        }
      }
    },
    {
      "id": "voice_processor",
      "type": "MCPToolCall",
      "config": {
        "tool_name": "process_voice_command",
        "parameters": {
          "command": "{{voice_input.text}}",
          "auto_execute": true
        }
      }
    },
    {
      "id": "response_formatter",
      "type": "PythonFunction",
      "config": {
        "code": "def format_response(mcp_result):\n    result = json.loads(mcp_result)\n    return {\n        'status': result.get('status'),\n        'message': result.get('classification', {}).get('suggested_action'),\n        'executed': result.get('execution_result', {}).get('executed', False)\n    }"
      }
    }
  ],
  "connections": [
    {"from": "voice_input", "to": "voice_processor"},
    {"from": "voice_processor", "to": "response_formatter"}
  ]
}
```

## Available MCP Tools

### 1. `classify_voice_command`
Classify intent from voice input without executing.

**Input**:
```json
{
  "text": "Move the keynote from 10:00 to 10:30"
}
```

**Output**:
```json
{
  "intent": "time_change",
  "confidence": 0.8,
  "parameters": {
    "event_name": "keynote", 
    "old_time": "10:00",
    "new_time": "10:30"
  },
  "suggested_action": "Update keynote time from 10:00 to 10:30 and notify attendees"
}
```

### 2. `process_voice_command`
Full pipeline: classify intent + execute if high confidence.

**Input**:
```json
{
  "command": "Move the keynote from 10:00 to 10:30",
  "auto_execute": true
}
```

**Output**:
```json
{
  "original_command": "Move the keynote from 10:00 to 10:30",
  "classification": { /* classification result */ },
  "execution_result": {
    "executed": true,
    "action": "time_change",
    "details": "Updated keynote to 10:30"
  },
  "status": "completed"
}
```

### 3. `update_event_time`
Manually update event time.

**Input**:
```json
{
  "event_identifier": "keynote",
  "new_time": "10:30",
  "new_end_time": "11:30"
}
```

### 4. `update_event_location`
Manually update event location.

**Input**:
```json
{
  "event_identifier": "panel",
  "new_location": "Conference Room B"
}
```

### 5. `get_event_info`
Answer questions using event data.

**Input**:
```json
{
  "question": "What's the WiFi password?"
}
```

**Output**:
```json
{
  "question": "what's the wifi password?",
  "answer": "WiFi network: EventWiFi, Password: Connect2025",
  "found_answer": true
}
```

### 6. `get_changelog`
Get recent event changes.

**Input**:
```json
{
  "limit": 5
}
```

## Available MCP Resources

### 1. `event://schedule`
Current event schedule

### 2. `event://attendees`  
Registered attendees list

### 3. `event://faq`
FAQ database

### 4. `event://changelog`
History of changes

### 5. `event://full`
Complete event data

## Error Handling

The MCP server provides robust error handling:

```json
{
  "success": false,
  "error": "Could not find event: invalid_event",
  "details": "Event identifier 'invalid_event' not found in schedule"
}
```

Common error scenarios:
- Event not found
- Invalid time format
- File access issues
- JSON parsing errors

## Testing the Integration

### Test Commands

1. **Time Change**:
   ```
   "Move the keynote from 10:00 to 10:30"
   "Reschedule lunch to 1:00 PM"
   "Delay the panel by 15 minutes"
   ```

2. **Location Change**:
   ```
   "Move the workshop to Room B"
   "Change panel location to Main Hall"
   ```

3. **Information Queries**:
   ```
   "What's the WiFi password?"
   "Where is parking available?"
   "What time is lunch?"
   ```

### Expected Responses

For successful time change:
```json
{
  "status": "completed",
  "message": "Update keynote time from 10:00 to 10:30 and notify attendees",
  "executed": true
}
```

For information query:
```json
{
  "question": "what's the wifi password?",
  "answer": "WiFi network: EventWiFi, Password: Connect2025",
  "found_answer": true
}
```

## Benefits of MCP Integration

1. **Standardized Interface**: Clean, documented tool interface
2. **Type Safety**: JSON schema validation for inputs/outputs  
3. **Resource Access**: Direct access to event data via URIs
4. **Real-time Updates**: Live connection to event database
5. **Error Handling**: Structured error responses
6. **Extensibility**: Easy to add new tools and resources

## Next Steps

1. Test the MCP server independently
2. Configure Langflow MCP client
3. Build Flow 1 using MCP tools
4. Add notification capabilities
5. Extend with Flows 2 and 3

The MCP integration provides a much cleaner architecture than direct API calls and makes the event management capabilities available to any MCP-compatible system. 