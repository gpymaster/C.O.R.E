from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import dateutil.parser
import dateutil.tz
from llama_text_no_history import *
import json
import re
import pytz

# ------------------------------
# Step 1: Setup Google Calendar API
# ------------------------------
SCOPES = ['https://www.googleapis.com/auth/calendar']  # <-- change scope to allow write access

creds = None
if os.path.exists('/Users/graysonkeenan/Desktop/C.O.R.E/token.pickle'):
    with open('/Users/graysonkeenan/Desktop/Jarvis/google docs assces/token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('/Users/graysonkeenan/Desktop/Jarvis/google docs assces/google_calender_passkey.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('/Users/graysonkeenan/Desktop/C.O.R.E/token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# ------------------------------
# Step 2: Define time window
# ------------------------------
now = datetime.datetime.now(datetime.timezone.utc)
time_min = (now - datetime.timedelta(hours=1)).isoformat()
time_max = (now + datetime.timedelta(days=3)).isoformat()

# ------------------------------
# Step 3: Get all accessible calendars
# ------------------------------
calendar_list = service.calendarList().list().execute()
calendar_ids = [cal['id'] for cal in calendar_list['items']]

# ------------------------------
# Step 4: Fetch events from all calendars
# Get your primary calendar first (usually the first one)
# ------------------------------
all_events = []
primary_calendar_id = calendar_ids[0] if calendar_ids else None  # Your primary calendar

# Only fetch from your primary calendar for student events
if primary_calendar_id:
    events_result = service.events().list(
        calendarId=primary_calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    for event in events:
        event['calendar_id'] = primary_calendar_id
        all_events.append(event)

# ------------------------------
# Step 5: Helper function to parse dates
# ------------------------------
def parse_event_time(event_time):
    dt = dateutil.parser.isoparse(event_time)
    # Make naive datetimes (all-day events) timezone-aware in UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dateutil.tz.UTC)
    return dt

def get_start_time(event):
    return parse_event_time(event['start'].get('dateTime', event['start'].get('date')))

all_events.sort(key=get_start_time)

# ------------------------------
# Step 6: Print ongoing and upcoming events
# ------------------------------


output_events = []
# Filter for events that contain "Grayson" in the summary (your personal events)
if not all_events:
    pass
else:
    for event in all_events:
        start = parse_event_time(event['start'].get('dateTime', event['start'].get('date')))
        end = parse_event_time(event['end'].get('dateTime', event['end'].get('date')))
        calendar_name = event['calendar_id']
        summary = event.get('summary', '')

        # Only include YOUR events (with "Grayson" in the name)
        if 'grayson' in summary.lower():
            event_info = {
                "calendar_name": calendar_name,
                "summary": summary,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "status": "ONGOING" if start <= now <= end else "UPCOMING" if start > now else "PAST"
            }

            if start <= now <= end:
                output_events.append(event_info)
            elif start > now:
                output_events.append(event_info)

    # # Write ongoing and upcoming events to a JSON file
    # with open("events_output.json", "w") as f:
    #     data = json.dump(output_events, f, indent=2)


# -------------------------------------
# Function: Be able to create events
# -------------------------------------

# def create_event(service, calendar_id, summary, description, start_time, end_time, timezone='UTC'):
#     """
#     Creates a calendar event.

#     Args:
#         service: Authenticated Google Calendar API service
#         calendar_id: Calendar ID (usually 'primary')
#         summary: Event title
#         description: Event description
#         start_time: Event start as datetime object (timezone-aware)
#         end_time: Event end as datetime object (timezone-aware)
#         timezone: Timezone string (default 'UTC')
#     """
#     event = {
#         'summary': summary,
#         'description': description,
#         'start': {
#             'dateTime': start_time.isoformat(),
#             'timeZone': timezone,
#         },
#         'end': {
#             'dateTime': end_time.isoformat(),
#             'timeZone': timezone,
#         }
#     }

#     created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
#     print(f"Event created: {created_event.get('htmlLink')}")

def get_data():
    return json.dumps(output_events, indent=2)


