#!/usr/bin/env python3
"""
Test script for the eMCeeP MCP Server

This script tests the MCP server functionality including:
- Intent classification
- Event data updates
- Voice command processing
- Resource access

Usage:
    python test_mcp_server.py
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🎤 Testing eMCeeP MCP Server...")
    
    # Test commands to validate
    test_commands = [
        {
            "name": "Time Change Command",
            "tool": "process_voice_command",
            "args": {
                "command": "Move the keynote from 10:00 to 10:30",
                "auto_execute": True
            },
            "expect": {
                "status": "completed",
                "intent": "time_change"
            }
        },
        {
            "name": "Location Change Command", 
            "tool": "process_voice_command",
            "args": {
                "command": "Move the panel to Room B",
                "auto_execute": True
            },
            "expect": {
                "intent": "location_change"
            }
        },
        {
            "name": "Intent Classification Only",
            "tool": "classify_voice_command",
            "args": {
                "text": "Cancel the workshop"
            },
            "expect": {
                "intent": "cancel_event",
                "confidence": ">0.5"
            }
        },
        {
            "name": "Get FAQ Data",
            "tool": "get_faq", 
            "args": {},
            "expect": {
                "faq.wifi": "*Connect2025*"
            }
        },
        {
            "name": "Get Schedule Data",
            "tool": "get_schedule", 
            "args": {},
            "expect": {
                "schedule": "list"
            }
        },
        {
            "name": "Update FAQ Entry",
            "tool": "update_faq", 
            "args": {
                "key": "test_key",
                "value": "test_value"
            },
            "expect": {
                "success": True
            }
        },
        {
            "name": "Add Schedule Item",
            "tool": "add_schedule_item", 
            "args": {
                "title": "Test Workshop",
                "time": "15:00",
                "end_time": "16:00",
                "location": "Room C"
            },
            "expect": {
                "success": True
            }
        },
        {
            "name": "Get Dietary Requirements",
            "tool": "get_dietary_requirements", 
            "args": {},
            "expect": {
                "total_attendees": 3,
                "dietary_summary.vegetarian": 1,
                "dietary_summary.gluten-free": 1
            }
        },
        {
            "name": "Add New Attendee",
            "tool": "add_attendee", 
            "args": {
                "name": "Andrea Della Corte",
                "email": "andrea@example.com",
                "company": "Tech Startup",
                "dietary_restrictions": "vegetarian"
            },
            "expect": {
                "success": True,
                "name": "Andrea Della Corte"
            }
        },
        {
            "name": "Manual Time Update",
            "tool": "update_event_time",
            "args": {
                "event_identifier": "lunch",
                "new_time": "13:00"
            },
            "expect": {
                "success": True
            }
        }
    ]
    
    print(f"📋 Running {len(test_commands)} test cases...\n")
    
    results = []
    
    for i, test in enumerate(test_commands, 1):
        print(f"Test {i}/{len(test_commands)}: {test['name']}")
        
        try:
            # For now, we'll simulate the MCP calls since running an actual MCP server
            # in a test environment requires more complex setup
            result = await simulate_mcp_call(test['tool'], test['args'])
            
            # Validate results
            passed = validate_result(result, test['expect'])
            
            results.append({
                "test": test['name'],
                "passed": passed,
                "result": result
            })
            
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}")
            
            if not passed:
                print(f"   Expected: {test['expect']}")
                print(f"   Got: {result}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                "test": test['name'],
                "passed": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    passed = sum(1 for r in results if r.get('passed', False))
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is ready for Langflow integration.")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        
        # Show failed tests
        failed = [r for r in results if not r.get('passed', False)]
        if failed:
            print("\nFailed tests:")
            for test in failed:
                print(f"  - {test['test']}")
                if 'error' in test:
                    print(f"    Error: {test['error']}")

async def simulate_mcp_call(tool_name: str, args: dict) -> dict:
    """Simulate MCP tool calls for testing purposes"""
    
    # Import the classes from our MCP server
    sys.path.append(str(Path(__file__).parent))
    from event_mcp_server import EventManager, IntentClassifier
    
    # Initialize components with test data path
    event_data_path = Path("data/event.json")
    event_manager = EventManager(event_data_path)
    intent_classifier = IntentClassifier()
    
    if tool_name == "classify_voice_command":
        text = args.get("text", "")
        return intent_classifier.classify_intent(text)
    
    elif tool_name == "process_voice_command":
        command = args.get("command", "")
        auto_execute = args.get("auto_execute", True)
        
        # Classify intent
        classification = intent_classifier.classify_intent(command)
        
        # Execute if high confidence
        execution_result = None
        if auto_execute and classification.get('confidence', 0) > 0.5:
            intent = classification.get('intent')
            params = classification.get('parameters', {})
            
            if intent == 'time_change':
                event_name = params.get('event_name', '')
                new_time = params.get('new_time', '')
                if event_name and new_time:
                    success = event_manager.update_schedule_time(event_name, new_time)
                    if success:
                        event_manager.save_event_data()
                    execution_result = {
                        "executed": success,
                        "action": "time_change"
                    }
            
            elif intent == 'location_change':
                event_name = params.get('event_name', '')
                new_location = params.get('new_location', '')
                if event_name and new_location:
                    success = event_manager.update_schedule_location(event_name, new_location)
                    if success:
                        event_manager.save_event_data()
                    execution_result = {
                        "executed": success,
                        "action": "location_change"
                    }
        
        return {
            "original_command": command,
            "classification": classification,
            "execution_result": execution_result,
            "status": "completed" if execution_result and execution_result.get('executed') else "classified_only"
        }
    
    elif tool_name == "update_event_time":
        event_id = args.get("event_identifier", "")
        new_time = args.get("new_time", "")
        
        success = event_manager.update_schedule_time(event_id, new_time)
        if success:
            event_manager.save_event_data()
        
        return {
            "success": success,
            "event_id": event_id,
            "new_time": new_time
        }
    
    elif tool_name == "update_event_location":
        event_id = args.get("event_identifier", "")
        new_location = args.get("new_location", "")
        
        success = event_manager.update_schedule_location(event_id, new_location)
        if success:
            event_manager.save_event_data()
        
        return {
            "success": success,
            "event_id": event_id,
            "new_location": new_location
        }
    
    elif tool_name == "get_schedule":
        return {
            "schedule": event_manager.event_data.get("schedule", [])
        }
    
    elif tool_name == "get_faq":
        return {
            "faq": event_manager.event_data.get("faq", {})
        }
    
    elif tool_name == "get_organizer":
        return {
            "organizer": event_manager.event_data.get("organizer", {}),
            "event_details": {
                "name": event_manager.event_data.get("name"),
                "date": event_manager.event_data.get("date"),
                "venue": event_manager.event_data.get("venue")
            }
        }
    
    elif tool_name == "get_attendees":
        return {
            "attendees": event_manager.event_data.get("attendees", []),
            "registration_info": event_manager.event_data.get("registration", {})
        }
    
    elif tool_name == "get_everything":
        return {
            "complete_event_data": event_manager.event_data
        }
    
    elif tool_name == "update_faq":
        key = args.get("key", "")
        value = args.get("value", "")
        
        success = event_manager.update_faq(key, value)
        if success:
            event_manager.save_event_data()
        
        return {
            "success": success,
            "message": f"Successfully updated FAQ entry '{key}'" if success else f"Failed to update FAQ entry '{key}'",
            "key": key,
            "value": value
        }
    
    elif tool_name == "add_schedule_item":
        title = args.get("title", "")
        time = args.get("time", "")
        end_time = args.get("end_time", "")
        location = args.get("location", "")
        description = args.get("description")
        speaker = args.get("speaker")
        
        success = event_manager.add_schedule_item(title, time, end_time, location, description, speaker)
        if success:
            event_manager.save_event_data()
        
        return {
            "success": success,
            "message": f"Successfully added '{title}' to schedule" if success else f"Failed to add '{title}' to schedule",
            "title": title,
            "time": time,
            "end_time": end_time,
            "location": location
        }
    
    elif tool_name == "get_dietary_requirements":
        attendees = event_manager.event_data.get("attendees", [])
        
        # Extract dietary information
        dietary_summary = {}
        dietary_details = []
        
        for attendee in attendees:
            dietary = attendee.get("dietary_restrictions", "none")
            dietary_details.append({
                "name": attendee.get("name"),
                "company": attendee.get("company"),
                "dietary_restrictions": dietary
            })
            
            # Count dietary restrictions
            if dietary in dietary_summary:
                dietary_summary[dietary] += 1
            else:
                dietary_summary[dietary] = 1
        
        return {
            "total_attendees": len(attendees),
            "dietary_summary": dietary_summary,
            "detailed_requirements": dietary_details,
            "catering_notes": "Consider offering vegetarian, gluten-free, and regular options based on attendee needs"
        }
    
    elif tool_name == "add_attendee":
        name = args.get("name", "")
        email = args.get("email")
        phone = args.get("phone")
        company = args.get("company")
        dietary_restrictions = args.get("dietary_restrictions", "none")
        
        success = event_manager.add_attendee(name, email, phone, company, dietary_restrictions)
        if success:
            event_manager.save_event_data()
        
        return {
            "success": success,
            "message": f"Successfully added attendee '{name}'" if success else f"Failed to add attendee '{name}'",
            "name": name,
            "dietary_restrictions": dietary_restrictions
        }
    
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def validate_result(result: dict, expected: dict) -> bool:
    """Validate test result against expectations"""
    
    def get_nested_value(data: dict, key: str):
        """Get value from nested dict, supporting dot notation and classification field"""
        # Special case: if looking for 'intent', check classification.intent first
        if key == 'intent' and 'classification' in data:
            classification = data['classification']
            if isinstance(classification, dict) and 'intent' in classification:
                return classification['intent']
        
        # Handle dot notation for nested access
        if '.' in key:
            keys = key.split('.')
            value = data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value
        
        # Simple key access
        return data.get(key)
    
    for key, expected_value in expected.items():
        actual_value = get_nested_value(result, key)
        
        if actual_value is None:
            return False
        
        # Handle special comparison cases
        if isinstance(expected_value, str):
            if expected_value.startswith(">"):
                # Numeric comparison (e.g., ">0.5")
                threshold = float(expected_value[1:])
                if not (isinstance(actual_value, (int, float)) and actual_value > threshold):
                    return False
            elif expected_value.startswith("*") and expected_value.endswith("*"):
                # Contains check (e.g., "*wifi*")
                search_term = expected_value.strip("*").lower()
                if not (isinstance(actual_value, str) and search_term in actual_value.lower()):
                    return False
            elif expected_value == "list":
                # Check if it's a list
                if not isinstance(actual_value, list):
                    return False
            else:
                # Exact match
                if actual_value != expected_value:
                    return False
        else:
            # Direct comparison
            if actual_value != expected_value:
                return False
    
    return True

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if event data file exists
    event_data_path = Path("data/event.json")
    if not event_data_path.exists():
        print(f"❌ Event data file not found: {event_data_path}")
        print("   Please ensure data/event.json exists")
        return False
    
    # Check if MCP package is available
    try:
        import mcp
        print("✅ MCP package available")
    except ImportError:
        print("❌ MCP package not installed")
        print("   Run: pip install mcp>=1.0.0")
        return False
    
    # No longer need OpenAI API key - we return raw event data for LLM processing
    print("✅ Event info will return raw data for LLM processing")
    
    print("✅ All prerequisites met")
    return True

if __name__ == "__main__":
    print("🎤 eMCeeP MCP Server Test Suite")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    asyncio.run(test_mcp_server()) 