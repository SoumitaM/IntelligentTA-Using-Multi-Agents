# src/talent_ai/tools/send_whatsapp_tool.py

import os
from twilio.rest import Client
from crewai_tools import tool

@tool("send_whatsapp_message")
def send_whatsapp_message_tool(to: str, message: str) -> str:
    """
    Sends a WhatsApp message using Twilio.
    
    Args:
        to (str): WhatsApp recipient number in format 'whatsapp:+<countrycode><number>'.
        message (str): The message to be sent.

    Returns:
        str: Delivery status or error message.
    """
    # SET THESE ENV VARS IN YOUR .env FILE OR IN main.py
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Default Twilio sandbox number

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to  # Example: 'whatsapp:+919999999999'
        )
        return f"Message sent to {to}. Status: {msg.status}, SID: {msg.sid}"
    except Exception as e:
        return f"Error sending message to {to}: {str(e)}"
