import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import uuid
import re
import random
import time
import json
import pickle
import threading

# For WhatsApp integration
from twilio.rest import Client

# Add the project root to path to ensure imports work correctly
sys.path.append(".")

# DIRECTLY import Google Calendar dependencies to avoid CrewAI
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES required to write to Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# Add state for tracking current candidates
if "current_candidates" not in st.session_state:
    st.session_state.current_candidates = []

# Add state for tracking scheduled interviews
if "scheduled_interviews" not in st.session_state:
    st.session_state.scheduled_interviews = []

# Add state for tracking conversation state
if "state" not in st.session_state:
    st.session_state.state = "initial"

# Add state for tracking confirmed candidates
if "confirmed_candidates" not in st.session_state:
    st.session_state.confirmed_candidates = []

# Store interview date/time
if "interview_date" not in st.session_state:
    st.session_state.interview_date = None

if "interview_time" not in st.session_state:
    st.session_state.interview_time = None

# Mock Java developer data - this could come from a CSV file in the future
MOCK_JAVA_CANDIDATES = [
    {
        "name": "Rahul Sharma",
        "score": 8.7,
        "experience": "5 years",
        "skills": "Java, Spring Boot, Microservices, AWS, Docker"
    },
    {
        "name": "Priya Patel",
        "score": 9.2,
        "experience": "7 years",
        "skills": "Java, Hibernate, REST API, Docker, MySQL"
    },
    {
        "name": "Amit Kumar",
        "score": 7.8,
        "experience": "3 years",
        "skills": "Java, Angular, Git, Maven, JUnit"
    },
    {
        "name": "Neha Singh",
        "score": 8.5,
        "experience": "4 years",
        "skills": "Java, Spring, MongoDB, Jenkins, Docker"
    },
    {
        "name": "Vikram Reddy",
        "score": 8.9,
        "experience": "6 years",
        "skills": "Java, Microservices, Kubernetes, AWS, Spring Boot"
    }
]

# Direct implementation of Google Calendar service
def get_calendar_service():
    """Get authenticated Google Calendar service"""
    creds = None
    
    # Check if token exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def schedule_interview(candidate_name, role, start_time, end_time, hr_email):
    """
    Schedules an interview on Google Calendar.
    """
    try:
        service = get_calendar_service()
        event = {
            'summary': f"Interview with {candidate_name} for {role}",
            'description': f"Interview scheduled for the {role} role.",
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
            'attendees': [{'email': hr_email}],
        }

        event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        return f"✅ Interview scheduled! Google Calendar link: {event.get('htmlLink')}"

    except Exception as e:
        st.error(f"Calendar Error: {str(e)}")
        return f"❌ Failed to schedule interview: {str(e)}"

def send_whatsapp_message(to_number, message):
    """
    Sends a WhatsApp message using Twilio
    """
    try:
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_number = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        
        # For debugging
        st.sidebar.write(f"Using Twilio credentials: {account_sid[:5]}...{account_sid[-5:]}")
        
        # Check if all credentials are available
        if not all([account_sid, auth_token, from_number]):
            st.warning("Twilio credentials missing. WhatsApp message not sent.")
            return "Twilio credentials missing. WhatsApp message not sent."
        
        # Format the to number if it doesn't have WhatsApp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
            
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        # For debugging
        st.sidebar.success(f"WhatsApp sent! SID: {message.sid[:10]}...")
        return f"WhatsApp message sent! SID: {message.sid}"
        
    except Exception as e:
        st.error(f"WhatsApp Error: {str(e)}")
        return f"Error sending WhatsApp message: {str(e)}"

def parse_datetime(interview_date, interview_time):
    """Parse date and time into datetime objects"""
    try:
        now = datetime.now()
        
        # Handle relative dates
        if interview_date.lower() == "tomorrow":
            interview_datetime = now + timedelta(days=1)
        else:
            # Map day names to numbers
            days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
                   "friday": 4, "saturday": 5, "sunday": 6}
            
            day_num = days.get(interview_date.lower())
            if day_num is not None:
                # Calculate days to add
                days_ahead = (day_num - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7  # If today, schedule for next week
                
                interview_datetime = now + timedelta(days=days_ahead)
            else:
                # Try to parse as a date like "April 19"
                try:
                    month_day = interview_date.split()
                    month = month_day[0].lower()
                    day = int(''.join(filter(str.isdigit, month_day[1])))
                    
                    months = {"january": 1, "february": 2, "march": 3, "april": 4, 
                             "may": 5, "june": 6, "july": 7, "august": 8, 
                             "september": 9, "october": 10, "november": 11, "december": 12}
                    month_num = months.get(month)
                    
                    interview_datetime = datetime(now.year, month_num, day)
                    if interview_datetime < now:
                        interview_datetime = datetime(now.year + 1, month_num, day)
                except:
                    return None, f"Could not parse date: {interview_date}"
        
        # Parse time
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', interview_time.lower())
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            ampm = time_match.group(3)
            
            # Convert to 24-hour format
            if ampm.lower() == 'pm' and hour < 12:
                hour += 12
            elif ampm.lower() == 'am' and hour == 12:
                hour = 0
                
            # Set the time
            interview_datetime = interview_datetime.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return interview_datetime, None
        else:
            return None, f"Could not parse time: {interview_time}"
        
    except Exception as e:
        return None, f"Error parsing date/time: {str(e)}"

def schedule_calendar_invite(candidate_name, job_role, interview_date, interview_time):
    """Schedule a calendar invite for an interview"""
    try:
        # Parse datetime
        interview_datetime, error = parse_datetime(interview_date, interview_time)
        if error:
            return f"Could not schedule: {error}"
        
        # Format for Google Calendar
        start_time = interview_datetime.isoformat()
        end_time = (interview_datetime + timedelta(hours=1)).isoformat()
        
        # Set HR email - REPLACE THIS WITH YOUR ACTUAL EMAIL
        hr_email = "soumitamallick03@gmail.com"  # <-- REPLACE THIS
        
        # Schedule the interview
        result = schedule_interview(
            candidate_name=candidate_name,
            role=job_role,
            start_time=start_time,
            end_time=end_time,
            hr_email=hr_email
        )
        
        return result
        
    except Exception as e:
        st.error(f"Error scheduling: {str(e)}")
        return f"Error scheduling interview: {str(e)}"

# Function to add a message to the chat about scheduled interviews
def add_scheduled_interview_message(candidate_name, interview_date, interview_time):
    """Add a message about scheduled interviews to the chat"""
    confirmation = f"📅 Interview with {candidate_name} has been scheduled for {interview_date} at {interview_time}.\n\nCalendar invite has been sent to your email."
    st.session_state.messages.append({"role": "assistant", "content": confirmation})
    
    # We don't call st.rerun() here to avoid issues with WebSockets

def process_whatsapp_confirmation(candidate_name, phone_number, message_body):
    """Process a WhatsApp confirmation and schedule an interview"""
    if "yes" in message_body.lower() or "confirm" in message_body.lower() or "available" in message_body.lower():
        # Find the candidate in scheduled interviews
        candidate = next((c for c in st.session_state.scheduled_interviews if c["name"] == candidate_name), None)
        
        if candidate and candidate_name not in st.session_state.confirmed_candidates:
            # Add to confirmed candidates
            st.session_state.confirmed_candidates.append(candidate_name)
            
            # Get interview details
            job_role = "Java Developer"
            interview_date = st.session_state.interview_date
            interview_time = st.session_state.interview_time
            
            if not interview_date or not interview_time:
                # Default values if none stored
                interview_date = "Saturday"
                interview_time = "10:00 AM"
            
            # Schedule the calendar invite
            calendar_result = schedule_calendar_invite(
                candidate_name=candidate_name,
                job_role=job_role,
                interview_date=interview_date,
                interview_time=interview_time
            )
            
            # Log the result
            st.sidebar.write(f"Calendar result: {calendar_result}")
            
            # Send confirmation to candidate
            confirmation_msg = f"Hello {candidate_name}, this is to confirm that your interview for the Java Developer position has been scheduled for {interview_date} at {interview_time}. We look forward to meeting you!"
            send_whatsapp_message(phone_number, confirmation_msg)
            
            # Add message to chat - this will appear next time the page updates
            add_scheduled_interview_message(candidate_name, interview_date, interview_time)
            
            # Create a file flag to trigger notifications
            with open('new_confirmation.txt', 'w') as f:
                f.write(f"{candidate_name},{interview_date},{interview_time}")
            
            return f"Interview scheduled for {candidate_name}"
        
        return f"Candidate {candidate_name} already confirmed or not found"
    
    return "No confirmation detected in message"

def simulate_whatsapp_response(candidate_name, message):
    """Simulate a WhatsApp response and process it immediately"""
    # Find the candidate
    candidate = next((c for c in st.session_state.scheduled_interviews if c["name"] == candidate_name), None)
    
    if candidate:
        # Use your real phone number here for testing
        phone_number = "+916289798474"  # ⚠️ Replace with your number
        
        # Process the confirmation
        result = process_whatsapp_confirmation(candidate_name, phone_number, message)
        
        # Set a flag for notification
        st.session_state.new_confirmation = True
        
        # Force update of UI
        st.rerun()
        
        return result
    
    return "Candidate not found"

def check_for_new_confirmations():
    """Check for new confirmations from the webhook"""
    try:
        # Check if the notification file exists
        if os.path.exists('new_confirmation.txt'):
            with open('new_confirmation.txt', 'r') as f:
                data = f.read().strip().split(',')
            
            if len(data) >= 3:
                candidate_name, interview_date, interview_time = data
                
                # Update UI to show the confirmation
                st.session_state.new_confirmation = True
                
                # If not already confirmed, add to list
                if candidate_name not in st.session_state.confirmed_candidates:
                    st.session_state.confirmed_candidates.append(candidate_name)
                    add_scheduled_interview_message(candidate_name, interview_date, interview_time)
                
                # Delete the file to avoid processing it twice
                os.remove('new_confirmation.txt')
                
                # Force refresh
                st.rerun()
                
    except Exception as e:
        st.error(f"Error checking for confirmations: {str(e)}")

def main():
    # Check for new confirmations
    check_for_new_confirmations()
    
    st.title("Intelligent Talent Acquisition Assistant")
    st.caption("AI-powered recruitment assistant")
    
    # Sidebar with testing tools
    with st.sidebar:
        st.info("**Twilio WhatsApp Integration**\n\nCandidate confirmations will automatically schedule interviews")
        
        # Show notification if new candidates have confirmed
        if st.session_state.get("new_confirmation", False):
            st.success(f"✅ New confirmation received! Interview scheduled.")
            st.session_state.new_confirmation = False
        
        # Test buttons for simulating WhatsApp responses
        st.subheader("Test WhatsApp Responses")
        if st.session_state.scheduled_interviews:
            for candidate in st.session_state.scheduled_interviews:
                if candidate["name"] not in st.session_state.confirmed_candidates:
                    if st.button(f"Simulate '{candidate['name']}' confirms", key=f"sim_{candidate['name']}"):
                        with st.spinner(f"Processing confirmation from {candidate['name']}..."):
                            result = simulate_whatsapp_response(candidate['name'], "Yes, I am available")
                            st.success(f"✅ {result}")
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input for new message
    prompt = st.chat_input("What kind of candidates are you looking for?")
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the user input
        with st.spinner("Working on your request..."):
            if "java" in prompt.lower() or "developer" in prompt.lower():
                # Use mock data instead of scanning real files
                java_candidates = MOCK_JAVA_CANDIDATES.copy()
                
                # Randomize a bit and take top 4
                random.shuffle(java_candidates)
                st.session_state.current_candidates = java_candidates[:4]
                st.session_state.state = "found_candidates"
                
                response = f"I've found {len(st.session_state.current_candidates)} potential Java Developer candidates from our resume database. Would you like me to schedule interviews with them for next week?"
            
            elif "yes" in prompt.lower() and st.session_state.state == "found_candidates":
                # Show candidates with scores
                response = "Great! Here are the candidates I've found:\n\n"
                for i, candidate in enumerate(st.session_state.current_candidates, 1):
                    response += f"**{i}. {candidate['name']}** (Score: {candidate['score']}/10)\n"
                    response += f"   Experience: {candidate['experience']}\n"
                    response += f"   Skills: {candidate['skills']}\n\n"
                response += "Would you like to schedule interviews with any of these candidates? If so, please specify which ones by number."
                st.session_state.state = "showing_candidates"
            
            elif any(num in prompt.lower() for num in ["1", "2", "3", "4", "all"]) and st.session_state.state == "showing_candidates":
                if "all" in prompt.lower():
                    selected = "all candidates"
                    selected_candidates = st.session_state.current_candidates
                else:
                    # Extract numbers from the input
                    nums = re.findall(r'\d+', prompt)
                    selected_candidates = [st.session_state.current_candidates[int(n)-1] for n in nums if 0 < int(n) <= len(st.session_state.current_candidates)]
                    selected = ", ".join([candidate["name"] for candidate in selected_candidates])
                
                # Store scheduled interviews
                st.session_state.scheduled_interviews = selected_candidates
                
                # Changed the response to explicitly ask for date and time
                response = f"Would you like to schedule an interview with {selected}? If yes, please specify the date and time for the interview (e.g., 'Next Monday at 2:00 PM')."
                st.session_state.state = "asking_for_datetime"
            
            elif st.session_state.state == "asking_for_datetime":
                # Extract date and time information
                date_match = re.search(r'(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december))', prompt.lower())
                time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', prompt.lower())
                
                if date_match and time_match:
                    date_str = date_match.group(1).capitalize()
                    time_str = time_match.group(0)
                    
                    # Store date and time for later use
                    st.session_state.interview_date = date_str
                    st.session_state.interview_time = time_str
                    
                    response = f"I'm scheduling interviews with the selected candidates for {date_str} at {time_str}. Here are the interview slots:\n\n"
                    
                    # Your actual phone number should be used here
                    your_phone_number = "+916289798474"  # ⚠️ Replace with your number
                    
                    for i, candidate in enumerate(st.session_state.scheduled_interviews):
                        response += f"- {candidate['name']}: {date_str} at {time_str}\n"
                        
                        # Create actual WhatsApp message
                        whatsapp_msg = f"Hey {candidate['name']}, your resume got shortlisted for the interview. Are you available on {date_str} at {time_str} for the interview?"
                        
                        # Send actual WhatsApp message - using your real phone number for testing
                        send_result = send_whatsapp_message(your_phone_number, whatsapp_msg)
                        st.sidebar.write(f"Message to {candidate['name']}: {send_result[:30]}...")
                    
                    response += "\nI've sent WhatsApp messages to confirm their availability. When they confirm via WhatsApp, I'll automatically schedule the calendar invites."
                    st.session_state.state = "interviews_scheduled"
                else:
                    response = "I need both a date and time to schedule the interviews. Please specify when you'd like to schedule them (e.g., 'Next Monday at 2:00 PM')."
                    st.session_state.state = "asking_for_datetime"
            
            elif ("yes" in prompt.lower() or "please" in prompt.lower()) and st.session_state.state == "interviews_scheduled":
                # After scheduling, respond to "yes please" with a request for confirmation
                response = "Should I confirm availability for the interview? If yes, please specify date and time."
                st.session_state.state = "confirming_availability"
            
            elif st.session_state.state == "confirming_availability" and any(word in prompt.lower() for word in ["yes", "confirm", "check"]):
                date_match = re.search(r'(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)', prompt.lower())
                time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', prompt.lower())
                
                if date_match or time_match:
                    date_str = date_match.group(1).capitalize() if date_match else "tomorrow"
                    time_str = time_match.group(0) if time_match else "10:00 AM"
                    
                    # Your actual phone number should be used here
                    your_phone_number = "+916289798474"  # ⚠️ Replace with your number
                    
                    # Send actual WhatsApp confirmations
                    response = f"I've sent confirmation messages for {date_str} at {time_str}. The following WhatsApp messages have been sent:\n\n"
                    
                    for candidate in st.session_state.scheduled_interviews:
                        if candidate["name"] not in st.session_state.confirmed_candidates:
                            whatsapp_msg = f"Hello {candidate['name']}, this is to confirm your interview is scheduled for {date_str} at {time_str}. Please reply 'confirm' if you are available."
                            
                            # Send actual WhatsApp message
                            send_whatsapp_message(your_phone_number, whatsapp_msg)
                            
                            response += f"- Confirmation sent to {candidate['name']}\n"
                    
                    response += "\nWhen the candidates reply with their confirmation via WhatsApp, I'll schedule the calendar invites automatically."
                else:
                    response = "I can help confirm availability. Please specify which date and time you'd prefer for the interview."
            
            elif "schedule" in prompt.lower():
                response = "Which candidates would you like to schedule interviews with? Please specify by name or number."
            
            else:
                response = "I understand you're looking for candidates. Please specify the job role and any specific skills you're looking for. For example, 'I need Java developers with Spring Boot experience.'"
        
        # Display assistant response with a simulated thinking delay
        with st.chat_message("assistant"):
            # Create a placeholder for the typing indicator
            typing_placeholder = st.empty()
            typing_placeholder.markdown("_Thinking..._")
            
            # Add a delay of 1.5 seconds to simulate thinking
            time.sleep(1.5)
            
            # Clear the typing indicator and show the actual response
            typing_placeholder.empty()
            st.markdown(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Create a simple file-based webhook receiver
def setup_file_watcher():
    """Set up a file watcher to check for WhatsApp messages"""
    import os
    import time
    import json
    
    watch_dir = "whatsapp_messages"
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
    
    while True:
        for filename in os.listdir(watch_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(watch_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Process the message
                    process_whatsapp_confirmation(
                        data.get('candidate_name', 'Unknown'),
                        data.get('phone_number', ''),
                        data.get('message_body', '')
                    )
                    
                    # Move or delete the file
                    os.remove(file_path)
                    
                except Exception as e:
                    print(f"Error processing webhook file: {str(e)}")
                    
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    # Start file watcher in a separate thread
    # watcher_thread = threading.Thread(target=setup_file_watcher, daemon=True)
    # watcher_thread.start()
    
    # Run the Streamlit app
    main() 