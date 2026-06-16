import time
from twilio.rest import Client

# --- TWILIO CONFIGURATION ---
# You will get these for free by signing up at twilio.com
TWILIO_ACCOUNT_SID = 'YOUR_ACCOUNT_SID_HERE'
TWILIO_AUTH_TOKEN = 'YOUR_AUTH_TOKEN_HERE'
TWILIO_VIRTUAL_NUMBER = '+1234567890'   # The fake number Twilio gives you
SECURITY_GUARD_NUMBER = '+919876543210' # Your actual mobile number

# --- COOLDOWN LOGIC ---
COOLDOWN_PERIOD = 60 # Wait 60 seconds before sending another SMS
last_alert_time = 0

def trigger_sms_alert(camera_id, anomaly_type):
    global last_alert_time
    current_time = time.time()
    
    # Logic Gate: Check if the cooldown period has passed
    if (current_time - last_alert_time) < COOLDOWN_PERIOD:
        return # Silently block the spam
        
    print(f"\n[NETWORK] >> Initiating Emergency Protocol for {camera_id}...")
    
    try:
        # Connect to the Twilio API
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Package and send the payload
        message = client.messages.create(
            body=f"🚨 URGENT: {anomaly_type} detected at {camera_id}! Dispatch security immediately.",
            from_=TWILIO_VIRTUAL_NUMBER,
            to=SECURITY_GUARD_NUMBER
        )
        print(f"[SUCCESS] >> SMS Alert Sent to Guard Room! (Message ID: {message.sid})\n")
        
        # Reset the cooldown timer
        last_alert_time = current_time
        
    except Exception as e:
        print(f"[FAILED] >> Network Error or Missing API Keys: {e}\n")
        # We still update the timer so it doesn't spam errors either
        last_alert_time = current_time