#!/usr/bin/env python3
"""
ICS to Google Calendar Integration Script

This script allows you to click on ICS files and automatically add events to Google Calendar.
It handles parsing ICS files, authenticating with Google Calendar API, and adding events.

Requirements:
- pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client icalendar python-dateutil tkinter

Setup:
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0 Client ID) for desktop application
5. Download the credentials JSON file and save as 'credentials.json' in script directory
"""

import sys
import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timezone
import pickle
from pathlib import Path

# Google Calendar API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ICS parsing imports
from icalendar import Calendar
from dateutil import tz

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']


class ICSToGoogleCalendar:
    def __init__(self):
        self.service = None
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.pickle'

    def authenticate_google_calendar(self):
        """Authenticate and create Google Calendar service."""
        creds = None

        # Check if token file exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.credentials_file):
                    messagebox.showerror(
                        "Error",
                        f"Credentials file '{self.credentials_file}' not found!\n\n"
                        "Please:\n"
                        "1. Go to Google Cloud Console\n"
                        "2. Enable Google Calendar API\n"
                        "3. Create OAuth 2.0 credentials\n"
                        "4. Download and save as 'credentials.json'"
                    )
                    return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    messagebox.showerror("Authentication Error", f"Failed to authenticate: {e}")
                    return False

            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            messagebox.showerror("Service Error", f"Failed to create Calendar service: {e}")
            return False

    def parse_ics_file(self, ics_file_path):
        """Parse ICS file and extract event information."""
        try:
            with open(ics_file_path, 'rb') as f:
                calendar = Calendar.from_ical(f.read())

            events = []
            for component in calendar.walk():
                if component.name == "VEVENT":
                    event_data = self.extract_event_data(component)
                    if event_data:
                        events.append(event_data)

            return events
        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse ICS file: {e}")
            return None

    def extract_event_data(self, vevent):
        """Extract event data from VEVENT component."""
        try:
            # Basic event information
            summary = str(vevent.get('summary', 'No Title'))
            description = str(vevent.get('description', ''))
            location = str(vevent.get('location', ''))

            # Handle start time
            dtstart = vevent.get('dtstart')
            if dtstart:
                start_dt = dtstart.dt
                if hasattr(start_dt, 'tzinfo') and start_dt.tzinfo:
                    start_time = start_dt.isoformat()
                else:
                    # Assume local timezone if none specified
                    start_time = start_dt.replace(tzinfo=tz.tzlocal()).isoformat()
            else:
                return None

            # Handle end time
            dtend = vevent.get('dtend')
            if dtend:
                end_dt = dtend.dt
                if hasattr(end_dt, 'tzinfo') and end_dt.tzinfo:
                    end_time = end_dt.isoformat()
                else:
                    end_time = end_dt.replace(tzinfo=tz.tzlocal()).isoformat()
            else:
                # If no end time, assume 1 hour duration
                from datetime import timedelta
                if isinstance(start_dt, datetime):
                    end_dt = start_dt + timedelta(hours=1)
                    end_time = end_dt.replace(tzinfo=tz.tzlocal()).isoformat()
                else:
                    end_time = start_time

            # Handle all-day events
            all_day = False
            if hasattr(dtstart.dt, 'date') and not hasattr(dtstart.dt, 'time'):
                all_day = True
                start_time = dtstart.dt.strftime('%Y-%m-%d')
                if dtend:
                    end_time = dtend.dt.strftime('%Y-%m-%d')
                else:
                    end_time = start_time

            return {
                'summary': summary,
                'description': description,
                'location': location,
                'start_time': start_time,
                'end_time': end_time,
                'all_day': all_day
            }
        except Exception as e:
            print(f"Error extracting event data: {e}")
            return None

    def create_google_event(self, event_data):
        """Create event in Google Calendar."""
        try:
            if event_data['all_day']:
                google_event = {
                    'summary': event_data['summary'],
                    'description': event_data['description'],
                    'location': event_data['location'],
                    'start': {'date': event_data['start_time']},
                    'end': {'date': event_data['end_time']},
                }
            else:
                google_event = {
                    'summary': event_data['summary'],
                    'description': event_data['description'],
                    'location': event_data['location'],
                    'start': {'dateTime': event_data['start_time']},
                    'end': {'dateTime': event_data['end_time']},
                }

            # Insert event into primary calendar
            event = self.service.events().insert(
                calendarId='primary',
                body=google_event
            ).execute()

            return event
        except HttpError as e:
            messagebox.showerror("Calendar Error", f"Failed to create event: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            return None

    def show_event_preview(self, events):
        """Show preview of events before adding to calendar."""
        if not events:
            messagebox.showwarning("No Events", "No events found in the ICS file.")
            return

        # Create preview window
        preview_window = tk.Toplevel()
        preview_window.title("Event Preview")
        preview_window.geometry("600x400")
        preview_window.transient()
        preview_window.grab_set()

        # Create main frame
        main_frame = ttk.Frame(preview_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        preview_window.columnconfigure(0, weight=1)
        preview_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text=f"Found {len(events)} event(s):", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Create scrollable text area
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_area = tk.Text(text_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)

        text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Display event details
        for i, event in enumerate(events, 1):
            text_area.insert(tk.END, f"Event {i}:\n")
            text_area.insert(tk.END, f"Title: {event['summary']}\n")
            text_area.insert(tk.END, f"Start: {event['start_time']}\n")
            text_area.insert(tk.END, f"End: {event['end_time']}\n")
            if event['location']:
                text_area.insert(tk.END, f"Location: {event['location']}\n")
            if event['description']:
                text_area.insert(tk.END, f"Description: {event['description']}\n")
            text_area.insert(tk.END, "\n" + "-" * 50 + "\n\n")

        text_area.config(state=tk.DISABLED)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))

        # Result variable
        result = {'add_events': False}

        def add_events():
            result['add_events'] = True
            preview_window.destroy()

        def cancel():
            result['add_events'] = False
            preview_window.destroy()

        # Buttons
        ttk.Button(button_frame, text="Add to Google Calendar", command=add_events).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT)

        # Wait for user response
        preview_window.wait_window()
        return result['add_events']

    def process_ics_file(self, ics_file_path):
        """Main method to process ICS file."""
        print(f"Processing ICS file: {ics_file_path}")

        # Authenticate with Google Calendar
        if not self.authenticate_google_calendar():
            return

        # Parse ICS file
        events = self.parse_ics_file(ics_file_path)
        if not events:
            return

        # Show preview and get user confirmation
        if not self.show_event_preview(events):
            messagebox.showinfo("Cancelled", "Event import cancelled.")
            return

        # Add events to Google Calendar
        success_count = 0
        for event_data in events:
            if self.create_google_event(event_data):
                success_count += 1

        if success_count > 0:
            messagebox.showinfo(
                "Success",
                f"Successfully added {success_count} out of {len(events)} events to Google Calendar!"
            )
        else:
            messagebox.showerror("Error", "Failed to add any events to Google Calendar.")


def main():
    """Main function to handle command line arguments."""
    # Create root window (hidden)
    root = tk.Tk()
    root.withdraw()

    # Check if ICS file was passed as argument
    if len(sys.argv) > 1:
        ics_file_path = sys.argv[1]
    else:
        # If no file provided, open file dialog
        from tkinter import filedialog
        ics_file_path = filedialog.askopenfilename(
            title="Select ICS File",
            filetypes=[("ICS files", "*.ics"), ("All files", "*.*")]
        )

    if not ics_file_path or not os.path.exists(ics_file_path):
        messagebox.showerror("Error", "No valid ICS file selected.")
        return

    # Process the ICS file
    processor = ICSToGoogleCalendar()
    processor.process_ics_file(ics_file_path)


if __name__ == "__main__":
    main()