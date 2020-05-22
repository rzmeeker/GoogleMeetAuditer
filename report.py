"""
To use this file you need a credentials.json from google developer console with admin API access in the same dir.
"""


import pickle
from pathlib import Path
from typing import List
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import date, timedelta, datetime
import rfc3339

REPORTS_SCOPES: List[str] = ['https://www.googleapis.com/auth/admin.reports.audit.readonly',
                             'https://www.googleapis.com/auth/admin.reports.usage.readonly']

def get_reports_service() -> Resource:
    """
    Helper method that creates a connection to Google Directory. Should not be invoked directly. Instead use
    self.report_service to avoid rebuilding the connection over and over.

    Returns:
        A Resource object with methods for interacting with the GSuite Admin Reports.
    """
    creds = None
    token_filepath = Path(Path(__file__).parents[0], 'reports_token.pickle')
    creds_filepath = Path(Path(__file__).parents[0], 'credentials.json')
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if Path.exists(token_filepath):
        with open(token_filepath, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_filepath, REPORTS_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_filepath, 'wb') as token:
            pickle.dump(creds, token)

    service = build('admin', 'reports_v1', credentials=creds)
    return service


def get_all_meet_results(service: Resource, startTime: int, endTime: int =None):
    if endTime == None:
        rfcEndTime = get_rfc_datetime_for_x_days_ago(startTime-1)
    else:
        rfcEndTime = get_rfc_datetime_for_x_days_ago(endTime)
    rfcStartTime = get_rfc_datetime_for_x_days_ago(startTime)
    page_token = 'Dummy'
    results = []
    while page_token is not None:
        result = service.activities().list(applicationName='meet',
                                           userKey='all',
                                           startTime=rfcStartTime,
                                           endTime=rfcEndTime).execute()
        if result.get('items'):
            for item in result.get('items', None):
                results.append(item)
        page_token = result.get('nextPageToken', None)
    return results


def get_meeting_participants(results):
    out_dict = {}
    for result in results:
        email = result.get('actor').get('email')
        if email is not None:
            params = result.get('events')[0].get('parameters')
            for param in params:
                if param.get('name') == 'meeting_code':
                    meeting = param.get('value')
                    if meeting in out_dict.keys():
                        if email not in out_dict[meeting]:
                            out_dict[meeting].append(email)
                    else:
                        out_dict[meeting] = [email]
    return out_dict

def get_rfc_datetime_for_x_days_ago(days_ago: int):
    today = date.today()
    target_day = today - timedelta(days=days_ago)
    return rfc3339.rfc3339(target_day)

def did_user_attend_meeting_with(user, other_user, meetings):
    for meeting, participants in meetings.items():
        for participant in participants:
            if user.lower() == participant.lower():
                for participant in participants:
                    if other_user.lower() == participant.lower():
                        return True
    return False


def user_attended_meetings_with(user, meetings):
    out_list = []
    for meeting, participants in meetings.items():
        for participant in participants:
            if participant.lower() == user.lower():
                for participant in participants:
                    out_list.append(participant)
    while user in out_list:
        out_list.remove(user)
    return out_list

if __name__ == "__main__":
    service = get_reports_service()
    days_ago = 0  #changeme if you want a report for X days in the past.

    results = get_all_meet_results(service=service,
                                   startTime=days_ago)
    meetings = get_meeting_participants(results)
    yesterday_results = get_all_meet_results(service=service,
                                             startTime=1,
                                             endTime=0)
    yesterday_meetings = get_meeting_participants(yesterday_results)

    for meeting, participants in meetings.items():
        print(f"Meeting ID: {meeting} had the participants: {participants}")

    print('Did I attend a meeting with bob?')
    print(did_user_attend_meeting_with('username@domain.org', 'bob@domain.org', meetings))
    print("Did I attend a meeting with potato?")
    print(did_user_attend_meeting_with('username@domain.org', 'potato@domain.org',
                                       meetings))
    for i in range(0, 15):
        #prints a report for every day in the last two weeks
        old_results = get_all_meet_results(service=service,
                                           startTime=i,
                                           endTime=i-1)
        old_meetings = get_meeting_participants(old_results)
        print(f'He attended meetings with {i} days ago:')
        print(user_attended_meetings_with('username@domain.org', old_meetings))