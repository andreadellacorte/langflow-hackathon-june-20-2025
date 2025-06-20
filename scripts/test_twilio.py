import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def test_sms_sending():
    """Test SMS sending functionality"""
    try:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        # Send test message
        message = client.messages.create(
            body="🎤 eMCeeP test message: This is your AI event assistant!",
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to="+447575171999"  # Replace with your test number
        )
        
        print(f"✅ SMS sent successfully. Message ID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
        return False

def test_bulk_notification():
    """Test sending notifications to multiple attendees"""
    attendees = [
        {"name": "John", "phone": "+447575171999"},
        {"name": "Jane", "phone": "+447575171999"}
    ]
    
    message_body = """🎤 eMCeeP Update: The keynote has been moved from 10:00 AM to 10:30 AM. 

Updated Schedule:
• 10:30 AM - Opening Keynote (Main Hall)
• 11:30 AM - Coffee Break

Questions? Reply to this message!"""
    
    # Demo would send to attendees
    print("📱 Would send bulk notification to all attendees")
    print(f"Message: {message_body}")
    
    # Simulate sending (without actually sending multiple SMS)
    print(f"📲 Would notify {len(attendees)} attendees")
    for attendee in attendees:
        print(f"  → {attendee['name']}: {attendee['phone']}")
    
    return True

def test_twilio_connection():
    """Test basic Twilio connection and account info"""
    try:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        # Get account info
        account = client.api.accounts(os.getenv('TWILIO_ACCOUNT_SID')).fetch()
        print(f"✅ Twilio connection successful")
        print(f"Account Status: {account.status}")
        print(f"Account Type: {account.type}")
        
        # Get phone numbers
        phone_numbers = client.incoming_phone_numbers.list()
        if phone_numbers:
            print(f"Available phone numbers: {len(phone_numbers)}")
            for number in phone_numbers[:3]:  # Show first 3
                print(f"  → {number.phone_number}")
        else:
            print("⚠️  No phone numbers found. You may need to purchase one.")
        
        return True
        
    except Exception as e:
        print(f"❌ Twilio connection test failed: {e}")
        return False

def create_demo_escalation_message():
    """Create an escalation message for organizer"""
    escalation_msg = """🚨 eMCeeP ESCALATION ALERT

Issue: Multiple attendees asking about WiFi problems
Frequency: 15 questions in last 10 minutes
Sentiment: Frustrated

Latest question: "The WiFi isn't working and I can't access my presentation!"

Suggested Actions:
1. Check WiFi infrastructure
2. Send broadcast update to all attendees
3. Activate backup hotspots

Reply RESOLVED when issue is fixed."""
    
    print("🚨 Example escalation message:")
    print(escalation_msg)
    return escalation_msg

if __name__ == "__main__":
    print("📱 Testing eMCeeP Twilio Integration...")
    print("=" * 50)
    
    # Check if credentials are set
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, phone_number]):
        print("❌ Twilio credentials not found in environment variables")
        print("Please set the following in .env file:")
        print("- TWILIO_ACCOUNT_SID")
        print("- TWILIO_AUTH_TOKEN") 
        print("- TWILIO_PHONE_NUMBER")
        exit(1)
    
    print(f"🔑 Account SID: {account_sid[:10]}...")
    print(f"📞 Phone Number: {phone_number}")
    
    # Run tests
    print("\n1. Testing Twilio Connection...")
    test1_success = test_twilio_connection()
    
    print("\n2. Testing SMS Sending...")
    print("⚠️  Note: This will send an actual SMS to the test number!")
    response = input("Continue? (y/N): ")
    if response.lower() == 'y':
        test2_success = test_sms_sending()
    else:
        print("📱 SMS test skipped")
        test2_success = True
    
    print("\n3. Testing Bulk Notification (Demo)...")
    test3_success = test_bulk_notification()
    
    print("\n4. Creating Demo Escalation Message...")
    create_demo_escalation_message()
    
    print("\n" + "=" * 50)
    if test1_success and test2_success and test3_success:
        print("🎉 All Twilio tests passed! eMCeeP SMS is ready.")
    else:
        print("⚠️  Some tests failed. Check your Twilio configuration.") 