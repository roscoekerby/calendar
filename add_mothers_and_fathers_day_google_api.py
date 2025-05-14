import datetime
import calendar
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope for full calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_nth_weekday(year, month, weekday, n):
    count = 0
    for day in range(1, 32):
        try:
            date = datetime.date(year, month, day)
        except ValueError:
            break
        if date.weekday() == weekday:
            count += 1
            if count == n:
                return date
    return None

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def add_parents_days(service, calendar_id='primary', start_year=2025, end_year=2125):
    for year in range(start_year, end_year + 1):
        # Mother's Day: 2nd Sunday of May
        mothers_day = get_nth_weekday(year, 5, calendar.SUNDAY, 2)
        # Father's Day: 3rd Sunday of June
        fathers_day = get_nth_weekday(year, 6, calendar.SUNDAY, 3)

        for event_date, title in [(mothers_day, "Mother's Day"), (fathers_day, "Father's Day")]:
            event = {
                'summary': title,
                'start': {'date': event_date.isoformat()},
                'end': {'date': (event_date + datetime.timedelta(days=1)).isoformat()},
                'colorId': '5',  # Yellow
            }
            service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Added {title} on {event_date}")

if __name__ == '__main__':
    service = authenticate_google_calendar()
    add_parents_days(service)
