#!/usr/bin/env python3
"""
eMCeeP Twilio Webhook Server
Acts as a bridge between Twilio and Langflow for SMS and voice interactions
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/twilio_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
LANGFLOW_URL = os.getenv('LANGFLOW_URL', 'http://localhost:7860')
LANGFLOW_FLOW_ID = os.getenv('LANGFLOW_FLOW_ID', 'your-flow-id')

class eMCeePWebhookHandler:
    """Handler for Twilio webhook requests"""
    
    def __init__(self):
        self.conversation_sessions = {}  # Track ongoing conversations
    
    def query_langflow(self, message: str, phone_number: str, message_type: str = 'sms') -> str:
        """Send message to Langflow and get AI response"""
        try:
            # Prepare the input message with context
            context_message = f"[Phone: {phone_number}] [Type: {message_type}] {message}"
            
            # Prepare payload for Langflow (matching the provided example)
            payload = {
                "input_value": context_message,
                "input_type": "chat",
                "output_type": "chat"
            }
            
            # Make request to Langflow API
            langflow_endpoint = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
            
            response = requests.post(
                langflow_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Parse the response
            result = response.json()
            logger.debug(f"Langflow response: {result}")
            
            # Extract the response text - try multiple possible paths
            response_text = None
            
            # Try to extract from different possible response structures
            if "outputs" in result and result["outputs"]:
                # Try first output structure
                first_output = result["outputs"][0]
                if "outputs" in first_output and first_output["outputs"]:
                    output_data = first_output["outputs"][0]
                    if "results" in output_data:
                        results = output_data["results"]
                        if "message" in results and "text" in results["message"]:
                            response_text = results["message"]["text"]
                        elif "text" in results:
                            response_text = results["text"]
                        elif isinstance(results, str):
                            response_text = results
            
            # Fallback: try to find any text in the response
            if not response_text and isinstance(result, dict):
                # Try to find any text field recursively
                def find_text(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key in ['text', 'message', 'response', 'output'] and isinstance(value, str):
                                return value
                            elif isinstance(value, (dict, list)):
                                found = find_text(value)
                                if found:
                                    return found
                    elif isinstance(obj, list):
                        for item in obj:
                            found = find_text(item)
                            if found:
                                return found
                    return None
                
                response_text = find_text(result)
            
            # Return response or fallback
            if response_text:
                return response_text.strip()
            else:
                logger.warning(f"Could not extract text from Langflow response: {result}")
                return "I received your message but couldn't generate a proper response. Please try again."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error to Langflow: {e}")
            return self.get_fallback_response()
        except ValueError as e:
            logger.error(f"Error parsing Langflow response: {e}")
            return self.get_fallback_response()
        except Exception as e:
            logger.error(f"Unexpected error querying Langflow: {e}")
            return self.get_fallback_response()
    
    def get_fallback_response(self) -> str:
        """Provide fallback response when Langflow is unavailable"""
        return ("Hi! I'm eMCeeP, your AI event assistant. I'm experiencing some technical difficulties "
                "right now. Please try again in a moment, or find a staff member for immediate assistance.")
    
    def handle_sms(self, from_number: str, body: str) -> str:
        """Process incoming SMS and get response from Langflow"""
        logger.info(f"SMS from {from_number}: {body}")
        
        # Get AI response through Langflow
        response = self.query_langflow(body, from_number, 'sms')
        
        logger.info(f"SMS response to {from_number}: {response}")
        return response
    
    def handle_voice_start(self, caller: str) -> VoiceResponse:
        """Handle initial voice call"""
        logger.info(f"Voice call from {caller}")
        
        response = VoiceResponse()
        
        # Welcome message and prompt for speech
        gather = Gather(
            input='speech',
            action='/voice/process',
            method='POST',
            speech_timeout='3',
            language='en-US',
            enhanced=True
        )
        
        gather.say(
            "Hello! You've reached eMCeeP, your AI event assistant. "
            "I can help you with event information. Please tell me how I can help you.",
            voice='alice'
        )
        
        response.append(gather)
        
        # Fallback if no speech detected
        response.say("I didn't hear anything. Please call back if you need assistance. Goodbye!")
        
        return response
    
    def handle_voice_process(self, speech_result: str, caller: str) -> VoiceResponse:
        """Process transcribed speech and provide voice response"""
        response = VoiceResponse()
        
        if not speech_result:
            response.say("I didn't understand that. Please try again or call back later.")
            return response
        
        logger.info(f"Voice transcription from {caller}: {speech_result}")
        
        # Get AI response through Langflow
        ai_response = self.query_langflow(speech_result, caller, 'voice')
        
        logger.info(f"Voice response to {caller}: {ai_response}")
        
        # Speak the response
        response.say(ai_response, voice='alice')
        
        # Ask if they need more help
        gather = Gather(
            input='speech',
            action='/voice/process',
            method='POST',
            speech_timeout='3',
            language='en-US',
            enhanced=True
        )
        
        gather.say("Is there anything else I can help you with?", voice='alice')
        response.append(gather)
        
        # Fallback
        response.say("Thank you for calling eMCeeP. Have a great day!")
        
        return response

# Initialize handler
handler = eMCeePWebhookHandler()

# Flask routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "langflow_url": LANGFLOW_URL,
        "langflow_flow_id": LANGFLOW_FLOW_ID
    })

@app.route('/sms', methods=['POST'])
def handle_sms():
    """Handle incoming SMS webhook from Twilio"""
    try:
        from_number = request.form.get('From')
        body = request.form.get('Body', '').strip()
        
        if not from_number or not body:
            logger.warning("SMS webhook missing required fields")
            return "Error: Missing required fields", 400
        
        # Get response from Langflow
        response_text = handler.handle_sms(from_number, body)
        
        # Create TwiML response
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)
        
        return str(twiml_response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error handling SMS: {e}")
        # Return a simple error response
        twiml_response = MessagingResponse()
        twiml_response.message("Sorry, I'm having technical difficulties. Please try again later.")
        return str(twiml_response), 500, {'Content-Type': 'text/xml'}

@app.route('/voice', methods=['POST'])
def handle_voice():
    """Handle incoming voice call webhook from Twilio"""
    try:
        caller = request.form.get('From', 'Unknown')
        twiml_response = handler.handle_voice_start(caller)
        
        return str(twiml_response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error handling voice call: {e}")
        response = VoiceResponse()
        response.say("Sorry, I'm experiencing technical difficulties. Please try calling back later.")
        return str(response), 500, {'Content-Type': 'text/xml'}

@app.route('/voice/process', methods=['POST'])
def handle_voice_process():
    """Handle voice processing (speech recognition results) from Twilio"""
    try:
        speech_result = request.form.get('SpeechResult', '')
        caller = request.form.get('From', 'Unknown')
        
        twiml_response = handler.handle_voice_process(speech_result, caller)
        return str(twiml_response), 200, {'Content-Type': 'text/xml'}
        
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        response = VoiceResponse()
        response.say("Sorry, I encountered an error. Please try again or call back later.")
        return str(response), 500, {'Content-Type': 'text/xml'}

@app.route('/test-langflow', methods=['GET'])
def test_langflow():
    """Test endpoint to verify Langflow connectivity"""
    try:
        test_response = handler.query_langflow("Hello, this is a test message", "+1234567890", "test")
        return jsonify({
            "status": "success",
            "langflow_response": test_response,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Langflow test failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    # Check required environment variables
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        exit(1)
    
    if not LANGFLOW_FLOW_ID or LANGFLOW_FLOW_ID == 'your-flow-id':
        print("⚠️  LANGFLOW_FLOW_ID not set. Please set it in your .env file after creating your flow.")
    
    print("🎤 eMCeeP Twilio Webhook Server starting...")
    print(f"📱 Twilio Phone: {os.getenv('TWILIO_PHONE_NUMBER')}")
    print(f"🔗 Langflow URL: {LANGFLOW_URL}")
    print(f"🔀 Flow ID: {LANGFLOW_FLOW_ID}")
    print("💬 Ready to bridge Twilio ↔ Langflow!")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('WEBHOOK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    ) 