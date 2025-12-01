#!/usr/bin/env python3
"""
Google Calendar -> Windows Toast notifier.
- OAuth2 flow (client_secrets.json)
- Notifies each event for today (including all-day events)
- Persists notified event ids per-day to avoid duplicates during the same day
- Runs in a loop every 60 seconds
"""
import os
import subprocess
import time
from datetime import datetime
from datetime import time as dt_time
from pathlib import Path
from typing import Any

import googleapiclient.discovery
from dateutil import parser
from dateutil.tz import tzlocal
from google.auth.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# -------------------------------------------------------------------------
# Config
# -------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/tasks.readonly"]
CLIENT_SECRETS_FILE = "client_secrets.json"  # from Google Cloud Console
POLL_INTERVAL_SECONDS = 60  # how often to check (every minute)


# -------------------------------------------------------------------------


def load_credentials() -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds: Credentials = flow.run_local_server(port=0)
    return creds


def today_bounds_iso() -> tuple[str, str]:
    """Return RFC3339 timestamps (with local timezone) for start and end of current day."""
    local_tz = tzlocal()
    now = datetime.now(local_tz)
    start = datetime.combine(now.date(), dt_time.min).astimezone(local_tz)
    end = now.astimezone(local_tz)
    # RFC3339 format
    return start.isoformat(), end.isoformat()


def friendly_time(event: dict[str, Any]) -> str:
    """
    Return human friendly time for event:
    - All-day events: 'All day'
    - Events with dateTime: formatted local start - end
    """
    start = event.get("start", {})
    end = event.get("end", {})

    if "date" in start:
        # all-day event
        return "All day"
    else:
        # dateTime present, parse and format local times
        try:
            start_time = parser.isoparse(start.get("dateTime"))
            end_time = parser.isoparse(end.get("dateTime")) if end.get("dateTime") else None
            # Format time e.g. "09:30–10:15"
            if end_time:
                return f"{start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"
            else:
                return start_time.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return start.get("dateTime") or start.get("date")  # type: ignore


def fetch_events_for_today(calendar_service: googleapiclient.discovery.Resource) -> list[dict[str, Any]]:
    time_min, time_max = today_bounds_iso()
    events_result = (
        calendar_service.events()
        .list(calendarId="primary", timeMin=time_min, timeMax=time_max, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events: list[dict[str, Any]] = events_result.get("items", [])
    return events


def fetch_tasks_for_today(tasks_service: googleapiclient.discovery.Resource) -> list[dict[str, Any]]:
    time_min, time_max = today_bounds_iso()
    tasks_result = tasks_service.tasks().list(tasklist="@default", dueMin=time_min).execute()
    tasks: list[dict[str, Any]] = tasks_result.get("items", [])

    return tasks


def show_notification(title: str, message: str) -> None:
    exe_path = Path(__file__).parent / "bin" / "Notifier.exe"
    subprocess.run(
        [str(exe_path), title, message], check=False, creationflags=subprocess.CREATE_NO_WINDOW  # hide console window
    )


def main_loop() -> None:
    creds = load_credentials()
    calendar_service = build("calendar", "v3", credentials=creds)
    tasks_service = build("tasks", "v1", credentials=creds)

    notified_event_ids: set[str] = set()
    notified_task_ids: set[str] = set()
    local_tz = tzlocal()
    today_str = datetime.now(local_tz).date().isoformat()

    while True:
        try:
            events = fetch_events_for_today(calendar_service)
            tasks = fetch_tasks_for_today(tasks_service)
        except Exception:
            show_notification("Failed to fetch google events and tasks!", "Restart the application to try again")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        # Notify all events for today, but only once per event per day
        for event in events:
            event_id = event.get("id")
            if not event_id:
                continue

            if event_id in notified_event_ids:
                continue

            event_title = event.get("summary") or "(No title)"
            show_notification(event_title, friendly_time(event))
            notified_event_ids.add(event_id)

        for task in tasks:
            title = task.get("title", "Untitled Task")
            task_id = task.get("id")
            if not task_id:
                continue

            if task_id in notified_task_ids:
                continue
            notified_task_ids.add(task_id)
            show_notification(title, f"Task: {title} Due today")

        # If the date changed (past midnight), reset set and update today_str
        current_date = datetime.now(local_tz).date().isoformat()
        if current_date != today_str:
            today_str = current_date
            notified_event_ids.clear()
            notified_task_ids.clear()

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    # Basic guard for Windows environment
    if os.name != "nt":
        print("This script uses Windows toast notifications; run on Windows.")
    main_loop()
