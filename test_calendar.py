import datetime
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os

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

def schedule_dummy_event():
    service = get_calendar_service()

    start_time = datetime.datetime(2025, 4, 24, 15, 0, 0, tzinfo=pytz.timezone("Asia/Kolkata"))
    end_time = start_time + datetime.timedelta(minutes=30)

    event = {
        'summary': '🎯 TEST INTERVIEW with Aman Gupta',
        'location': 'Online',
        'description': 'Demo interview scheduled by TalentAI Scheduler!',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [
            {'email': 'your-email@gmail.com'}  # 👈 Replace this with your actual email
        ],
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'✅ Event created: {event.get("htmlLink")}')

# 🔁 Run it
schedule_dummy_event()
