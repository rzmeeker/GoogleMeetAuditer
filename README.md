#Purpose

This script is an example usage of how to pull Google Meet activity from the GSuite Admin Audit logs.
Further implementation can be done using the provided functions.

#Installation

Go to console.developers.google.com and make a project with access to the admin API and register an "other"
typed Oauth API key. Or go to https://developers.google.com/admin-sdk/reports/v1/quickstart/python and just click on
"enable reports API" in step one of their quickstart guide if you aren't used to developing stuff with their API.

#Usage
Example usage is in the "if name == main" section at the bottom of report.py

service = get_reports_service() is used to initialize a Resource object that we can use for all our API queries.

get_all_meet_results() is used to download audit data from the API. Requires the service above.

get_meeting_participants() is a parser that takes all that meeting data and returns a dict where keys are meeting codes
and the values are participant emails

did_user_attend_meeting_with() checks if two users were in a meeting within the result of get_meeting_participants. Returns bool

user_attended_meetings_with() returns a List of all users a given user attended meetings with. If you have capitialization right
when entering their email address then it will properly remove them from the list.