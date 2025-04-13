# # receive_whatsapp.py

# from flask import Flask, request, jsonify
# from datetime import datetime

# app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def home():
#     return "WhatsApp webhook is running!"

# @app.route('/incoming_whatsapp', methods=['POST'])
# def incoming_whatsapp():
#     try:
#         # Twilio sends form-encoded data
#         incoming_msg = request.form.get('Body')
#         from_number = request.form.get('From')
#         timestamp = datetime.now().isoformat()

#         print(f"[{timestamp}] Message from {from_number}: {incoming_msg}")

#         # : Process the message with CrewAI (e.g., trigger scheduling agent)

#         # Twilio expects a 200 OK response
#         return "Message received", 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5002, debug=True)


# receive_whatsapp.py

# from flask import Flask, request, jsonify
# from datetime import datetime

# app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def home():
#     return "Webhook running!"

# @app.route('/incoming_whatsapp', methods=['POST'])
# def incoming_whatsapp():
#     print("✅ Webhook hit!")

#     incoming_msg = request.form.get('Body')
#     from_number = request.form.get('From')
#     timestamp = datetime.now().isoformat()

#     print(f"[{timestamp}] Message from {from_number}: {incoming_msg}")
#     return "Message received", 200

# if __name__ == '__main__':
#     app.run(port=5002, debug=True)

# import litellm
# litellm._turn_on_debug()

import os
from dotenv import load_dotenv
import litellm
import json

# Load environment variables first
load_dotenv()

# Configure LiteLLM
litellm.drop_params = True  # Prevents sending unnecessary params
os.environ["ANTHROPIC_API_KEY"] = ""  # Prevent default fallback

from flask import Flask, request, jsonify
from datetime import datetime
from run_schedule_task import run_schedule_task

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "✅ WhatsApp webhook is running!"

@app.route('/incoming_whatsapp', methods=['POST'])
def incoming_whatsapp():
    try:
        # Log the incoming request
        print("🔔 Webhook received!")
        
        # Get incoming message from Twilio
        incoming_msg = request.form.get('Body', '').strip()
        from_number = request.form.get('From', '')
        timestamp = datetime.now().isoformat()
        
        print(f"[{timestamp}] Message from {from_number}: {incoming_msg}")
        
        # Create a directory to save messages if it doesn't exist
        msgs_dir = "whatsapp_messages"
        if not os.path.exists(msgs_dir):
            os.makedirs(msgs_dir)
        
        # Save message to a file
        msg_file = os.path.join(msgs_dir, f"msg_{timestamp.replace(':', '-')}.json")
        
        # In a production app, you'd look up the phone number to find the candidate
        # For this demo, we'll default to Priya Patel
        candidate_name = "Priya Patel"
        
        # Save message data
        message_data = {
            "candidate_name": candidate_name,
            "phone_number": from_number,
            "message_body": incoming_msg,
            "timestamp": timestamp
        }
        
        with open(msg_file, 'w') as f:
            json.dump(message_data, f)
        
        # Also create a simple flag file that Streamlit can easily check
        with open('new_confirmation.txt', 'w') as f:
            f.write(f"{candidate_name},Saturday,10:00 AM")  # Use default date/time if not specified
        
        return "OK", 200
    
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
