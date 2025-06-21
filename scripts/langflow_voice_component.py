from langflow.custom import CustomComponent
from langflow.field_typing import Data, Text
from langflow import CustomComponent
from typing import Optional
import requests
import json
import os
from openai import OpenAI

class VoiceCommandProcessor(CustomComponent):
    """
    Custom Langflow Component for processing voice commands using LLM intent classification
    """
    display_name = "eMCeeP Voice Command Processor"
    description = "Process voice commands for event management using LLM-based intent classification"
    
    def build_config(self):
        return {
            "voice_command": {
                "display_name": "Voice Command Text",
                "field_type": "str",
                "required": True,
                "multiline": True,
                "placeholder": "e.g., 'Move the keynote from 10:00 to 10:30'"
            },
            "api_server_url": {
                "display_name": "Event API Server URL",
                "field_type": "str",
                "value": "http://localhost:8000",
                "required": True
            },
            "use_llm_enhancement": {
                "display_name": "Use LLM Enhancement",
                "field_type": "bool",
                "value": True,
                "required": False
            },
            "openai_api_key": {
                "display_name": "OpenAI API Key",
                "field_type": "str",
                "password": True,
                "required": False
            },
            "auto_execute": {
                "display_name": "Auto Execute High Confidence Commands",
                "field_type": "bool",
                "value": True,
                "required": False
            }
        }
    
    def build(
        self,
        voice_command: str,
        api_server_url: str = "http://localhost:8000",
        use_llm_enhancement: bool = True,
        openai_api_key: Optional[str] = None,
        auto_execute: bool = True
    ) -> Data:
        """
        Process voice command through intent classification and event management
        """
        try:
            # Step 1: Basic intent classification using our local API
            basic_classification = self._classify_intent_basic(voice_command, api_server_url)
            
            # Step 2: Enhanced classification using LLM if enabled
            enhanced_classification = None
            if use_llm_enhancement and openai_api_key:
                enhanced_classification = self._classify_intent_llm(voice_command, openai_api_key)
            
            # Step 3: Combine classifications for final decision
            final_classification = self._combine_classifications(basic_classification, enhanced_classification)
            
            # Step 4: Execute command if auto_execute is enabled and confidence is high
            execution_result = None
            if auto_execute and final_classification.get('confidence', 0) > 0.7:
                execution_result = self._execute_command(final_classification, api_server_url)
            
            # Step 5: Build comprehensive response
            result = {
                "original_command": voice_command,
                "basic_classification": basic_classification,
                "enhanced_classification": enhanced_classification,
                "final_classification": final_classification,
                "execution_result": execution_result,
                "status": "completed" if execution_result and execution_result.get('success') else "classified_only",
                "confidence": final_classification.get('confidence', 0),
                "suggested_actions": self._generate_suggested_actions(final_classification)
            }
            
            return Data(value=result)
            
        except Exception as e:
            error_result = {
                "original_command": voice_command,
                "error": str(e),
                "status": "error",
                "confidence": 0.0
            }
            return Data(value=error_result)
    
    def _classify_intent_basic(self, text: str, api_url: str) -> dict:
        """Use our local API for basic intent classification"""
        try:
            response = requests.post(
                f"{api_url}/classify-intent",
                json={"text": text},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "error": str(e),
                "source": "basic_api"
            }
    
    def _classify_intent_llm(self, text: str, api_key: str) -> dict:
        """Enhanced intent classification using OpenAI LLM"""
        try:
            client = OpenAI(api_key=api_key)
            
            system_prompt = """
            You are eMCeeP, an AI assistant specialized in event management voice command classification.
            
            Your task is to analyze voice commands and classify them into these intents:
            1. time_change - changing event times
            2. location_change - changing event locations  
            3. speaker_change - changing speakers
            4. cancel_event - canceling events
            5. add_event - adding new events
            6. query_info - asking for information
            7. escalation - urgent issues requiring immediate attention
            
            For each command, provide:
            - intent: the classified intent
            - confidence: confidence score 0.0-1.0
            - parameters: extracted key information
            - reasoning: brief explanation of your classification
            
            Respond in JSON format only.
            """
            
            user_prompt = f"""
            Classify this voice command: "{text}"
            
            Consider:
            - What action is being requested?
            - What specific details are provided?
            - How urgent or complex is this request?
            - What parameters can be extracted?
            
            Provide your analysis in JSON format.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            # Parse the JSON response
            llm_response = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["source"] = "llm_enhanced"
                return result
            else:
                return {
                    "intent": "unknown",
                    "confidence": 0.0,
                    "error": "Could not parse LLM response",
                    "source": "llm_enhanced",
                    "raw_response": llm_response
                }
                
        except Exception as e:
            return {
                "intent": "unknown", 
                "confidence": 0.0,
                "error": str(e),
                "source": "llm_enhanced"
            }
    
    def _combine_classifications(self, basic: dict, enhanced: Optional[dict]) -> dict:
        """Combine basic and enhanced classifications for final decision"""
        if not enhanced or enhanced.get('error'):
            # Use basic classification only
            return {
                "intent": basic.get('intent', 'unknown'),
                "confidence": basic.get('confidence', 0.0),
                "parameters": basic.get('parameters', {}),
                "source": "basic_only",
                "reasoning": "Enhanced classification not available"
            }
        
        # Compare both classifications
        basic_confidence = basic.get('confidence', 0.0)
        enhanced_confidence = enhanced.get('confidence', 0.0)
        
        # Use the classification with higher confidence
        if enhanced_confidence > basic_confidence:
            final = enhanced.copy()
            final["source"] = "enhanced_preferred"
            final["basic_agreement"] = basic.get('intent') == enhanced.get('intent')
        else:
            final = basic.copy()
            final["source"] = "basic_preferred"
            final["enhanced_agreement"] = basic.get('intent') == enhanced.get('intent')
        
        # Boost confidence if both agree
        if basic.get('intent') == enhanced.get('intent'):
            final["confidence"] = min(1.0, final["confidence"] * 1.2)
            final["agreement"] = True
        else:
            final["confidence"] = final["confidence"] * 0.8
            final["agreement"] = False
        
        return final
    
    def _execute_command(self, classification: dict, api_url: str) -> dict:
        """Execute the classified command via the API"""
        try:
            response = requests.post(
                f"{api_url}/process-voice-command",
                json={"text": classification.get("original_text", "")},
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute command"
            }
    
    def _generate_suggested_actions(self, classification: dict) -> list:
        """Generate suggested actions based on classification"""
        intent = classification.get('intent', 'unknown')
        confidence = classification.get('confidence', 0.0)
        
        actions = []
        
        if intent == 'time_change':
            if confidence > 0.8:
                actions.append("✅ Execute time change automatically")
                actions.append("📱 Send notifications to affected attendees")
            else:
                actions.append("⚠️ Confirm time change details before executing")
                actions.append("🔍 Verify event identification is correct")
        
        elif intent == 'location_change':
            actions.append("📍 Update event location")
            actions.append("🗺️ Check venue availability")
            actions.append("📱 Notify attendees of location change")
        
        elif intent == 'query_info':
            actions.append("📖 Retrieve information from event database")
            actions.append("💬 Provide instant response")
        
        elif intent == 'escalation':
            actions.append("🚨 Immediate organizer notification required")
            actions.append("📞 Consider phone call for urgent issues")
        
        else:
            actions.append("❓ Request clarification from user")
            actions.append("🤔 Review command for better understanding")
        
        return actions


class EventDataRetriever(CustomComponent):
    """
    Custom Langflow Component for retrieving event data from the local API
    """
    display_name = "eMCeeP Event Data Retriever"
    description = "Retrieve event data from the local event management API"
    
    def build_config(self):
        return {
            "api_server_url": {
                "display_name": "Event API Server URL", 
                "field_type": "str",
                "value": "http://localhost:8000",
                "required": True
            },
            "data_type": {
                "display_name": "Data Type",
                "field_type": "str",
                "options": ["complete", "schedule", "attendees", "faq", "changelog"],
                "value": "complete",
                "required": True
            }
        }
    
    def build(
        self, 
        api_server_url: str = "http://localhost:8000",
        data_type: str = "complete"
    ) -> Data:
        """Retrieve event data from the API"""
        try:
            endpoint_map = {
                "complete": "/event",
                "schedule": "/event/schedule", 
                "attendees": "/event/attendees",
                "faq": "/event/faq",
                "changelog": "/event/changelog"
            }
            
            endpoint = endpoint_map.get(data_type, "/event")
            
            response = requests.get(f"{api_server_url}{endpoint}", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return Data(value={
                "data_type": data_type,
                "data": data,
                "status": "success",
                "timestamp": requests.utils.default_user_agent()
            })
            
        except Exception as e:
            return Data(value={
                "data_type": data_type,
                "error": str(e),
                "status": "error"
            })


class NotificationSender(CustomComponent):
    """
    Custom Langflow Component for sending notifications via Twilio
    """
    display_name = "eMCeeP Notification Sender"
    description = "Send SMS notifications to attendees via Twilio"
    
    def build_config(self):
        return {
            "message": {
                "display_name": "Message Content",
                "field_type": "str",
                "multiline": True,
                "required": True
            },
            "recipient_type": {
                "display_name": "Recipient Type",
                "field_type": "str", 
                "options": ["all_attendees", "organizer", "specific_number"],
                "value": "organizer",
                "required": True
            },
            "phone_number": {
                "display_name": "Specific Phone Number",
                "field_type": "str",
                "required": False
            },
            "twilio_account_sid": {
                "display_name": "Twilio Account SID",
                "field_type": "str",
                "password": True,
                "required": True
            },
            "twilio_auth_token": {
                "display_name": "Twilio Auth Token",
                "field_type": "str", 
                "password": True,
                "required": True
            },
            "twilio_phone_number": {
                "display_name": "Twilio Phone Number",
                "field_type": "str",
                "required": True
            }
        }
    
    def build(
        self,
        message: str,
        recipient_type: str = "organizer",
        phone_number: Optional[str] = None,
        twilio_account_sid: str = "",
        twilio_auth_token: str = "",
        twilio_phone_number: str = ""
    ) -> Data:
        """Send SMS notifications"""
        try:
            from twilio.rest import Client
            
            client = Client(twilio_account_sid, twilio_auth_token)
            
            sent_messages = []
            
            if recipient_type == "specific_number" and phone_number:
                # Send to specific number
                message_obj = client.messages.create(
                    body=f"🎤 eMCeeP: {message}",
                    from_=twilio_phone_number,
                    to=phone_number
                )
                sent_messages.append({
                    "to": phone_number,
                    "sid": message_obj.sid,
                    "status": "sent"
                })
            
            elif recipient_type == "organizer":
                # Send to organizer (could retrieve from event data)
                organizer_phone = "+1555123456"  # Default from event data
                message_obj = client.messages.create(
                    body=f"🎤 eMCeeP Alert: {message}",
                    from_=twilio_phone_number,
                    to=organizer_phone
                )
                sent_messages.append({
                    "to": organizer_phone,
                    "sid": message_obj.sid,
                    "status": "sent"
                })
            
            # TODO: Implement bulk sending for all_attendees
            
            return Data(value={
                "message": message,
                "recipient_type": recipient_type,
                "sent_messages": sent_messages,
                "total_sent": len(sent_messages),
                "status": "success"
            })
            
        except Exception as e:
            return Data(value={
                "message": message,
                "error": str(e),
                "status": "error"
            })