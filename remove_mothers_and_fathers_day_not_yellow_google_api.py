from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import datetime

# If modifying these scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def delete_non_yellow_parents_days(service, calendar_id='primary'):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print("Searching for old Mother's and Father's Day events...")

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=2500,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    for event in events:
        title = event.get('summary', '')
        if title in ["Mother's Day", "Father's Day"]:
            color = event.get('colorId', None)
            if color != '5':  # Only delete non-yellow ones
                print(f"Deleting: {title} on {event['start'].get('date') or event['start'].get('dateTime')}")
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()

    print("✅ Cleanup complete.")

if __name__ == '__main__':
    service = authenticate_google_calendar()
    delete_non_yellow_parents_days(service)
