# Google Calendar → Windows Toast Notifier
A small Windows-only Python service that watches your Google Calendar (and Tasks) and shows native Windows toast notifications for today's events.

## The script:
* Performs an OAuth2 flow to access your calendar and tasks (client_secrets.json required).
* Notifies each event for today (including all-day events).
* Persists notified event and task IDs per day to avoid duplicate notifications within the same day.
* Runs in a loop (default every 60 seconds).

This project uses a hybrid approach: Python for Google Calendar/Tasks API and a small C# native notifier for Windows toast notifications.
Reason: libraries like win10toast create temporary toasts that disappear after a few seconds 
and are not persisted to Windows’ Action Center / Notification Center (they do not appear when you open the clock/calendar area). 
To get native, persistent Windows toast notifications that show in Action Center this project uses the Notifier (C#) helper.

# Requirements
* Windows 10 / Windows 11 (this script uses Windows toast notifications).
* Python 3.13
* UV package manager installed
* Google API credentials: a client_secrets.json file from Google Cloud Console with OAuth credentials for a Desktop application.

# Local project setup
* Create and activate a Python virtual environment
```commandline
python -m venv .venv
.\.venv\Scripts\activate
``` 
* install necessary libraries:
```commandline
 uv sync
```
* Build Notifier (C#): build the C# Notifier project (located in the Notifier folder). See Notifier/README.md for build instructions.
* After building, ensure the resulting Notifier.exe is available to the Python script at: `./bin/Notifier.exe`
* Place the client_secrets.json file next to the Python script
* Run the script:
```commandline
python calendar_notifier.py
```

# Getting client_secrets.json
Refer to [Google docs](https://developers.google.com/identity/protocols/oauth2/native-app) to generate `client_secrets.json`