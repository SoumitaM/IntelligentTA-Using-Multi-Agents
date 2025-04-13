# # test_whatsapp.py

# import os
# from dotenv import load_dotenv
# from twilio.rest import Client

# # Load from .env
# load_dotenv()

# # Twilio credentials
# account_sid = os.getenv("TWILIO_ACCOUNT_SID")
# auth_token = os.getenv("TWILIO_AUTH_TOKEN")
# from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# # Replace with your actual number
# to_number = "whatsapp:+916289798474"

# message_body = "👋 Hello from TalentAI! This is a test message via WhatsApp."
# print(f"Status: {message_body.status}")


# client = Client(account_sid, auth_token)

# try:
#     message = client.messages.create(
#         body=message_body,
#         from_=from_number,
#         to=to_number
#     )
#     print(f"✅ Message sent! SID: {message.sid}")
# except Exception as e:
#     print(f"❌ Failed to send message: {e}")


# test_whatsapp.py

# test_whatsapp.py

import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load Twilio credentials from .env
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = "whatsapp:+14155238886"  # Twilio sandbox sender
to_number = "whatsapp:+916289798474"  # 👈 Your paired number

client = Client(account_sid, auth_token)

try:
    # ✅ Send a pre-approved template message: hello_world
    message = client.messages.create(
        from_=from_number,
        to=to_number,
        body="Hello Soumita, this is a message from TalentAI!"
    )
    print(f"✅ Message sent! SID: {message.sid}")
except Exception as e:
    print(f"❌ Failed to send message: {e}")
