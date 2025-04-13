import os
import datetime
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES required to write to Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def schedule_interview(candidate_name, role, start_time, end_time, hr_email):
    """
    Schedules an interview on Google Calendar.

    Args:
        candidate_name (str): Name of the candidate.
        role (str): Job title.
        start_time (str): ISO format datetime string.
        end_time (str): ISO format datetime string.
        hr_email (str): The HR manager's email to invite.

    Returns:
        str: Confirmation message with calendar link (if available).
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
        return f"❌ Failed to schedule interview: {str(e)}" 