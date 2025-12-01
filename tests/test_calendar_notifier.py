import unittest
from datetime import datetime, date
from datetime import time as dt_time
from unittest.mock import MagicMock, Mock, patch

import calendar_notifier


class TestCalendarNotifier(unittest.TestCase):

    def test_today_bounds_iso(self) -> None:
        start, end = calendar_notifier.today_bounds_iso()

        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)

        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

        self.assertEqual(start_dt.time(), dt_time.min)
        self.assertLessEqual(start_dt, end_dt)

    def test_friendly_time_all_day_event(self) -> None:
        # ARRANGE
        event = {"start": {"date": "2024-01-15"}, "end": {"date": "2024-01-16"}}

        # ACT
        result = calendar_notifier.friendly_time(event)

        # ASSERT
        self.assertEqual(result, "All day")

    def test_friendly_time_timed_event(self) -> None:
        # ARRANGE
        event = {"start": {"dateTime": "2024-01-15T09:30:00-08:00"}, "end": {"dateTime": "2024-01-15T10:15:00-08:00"}}

        # ACT
        result = calendar_notifier.friendly_time(event)

        # ASSERT
        self.assertEqual(result, "09:30–10:15")

    def test_friendly_time_no_end_time(self) -> None:
        # ARRANGE
        event = {"start": {"dateTime": "2024-01-15T09:30:00-08:00"}, "end": {}}

        # ACT
        result = calendar_notifier.friendly_time(event)

        # ASSERT
        self.assertEqual(result, "2024-01-15 09:30")

    def test_friendly_time_invalid_datetime(self) -> None:
        # ARRANGE
        event = {"start": {"dateTime": "invalid-datetime"}, "end": {"dateTime": "invalid-datetime"}}

        # ACT
        result = calendar_notifier.friendly_time(event)

        # ASSERT
        self.assertEqual(result, "invalid-datetime")

    @patch("calendar_notifier.build")
    def test_fetch_events_for_today(self, mock_build: MagicMock) -> None:
        # ARRANGE
        mock_service = Mock()
        mock_events = Mock()
        mock_list = Mock()

        mock_service.events.return_value = mock_events
        mock_events.list.return_value = mock_list
        mock_list.execute.return_value = {"items": [{"id": "test_event"}]}

        # ACT
        result = calendar_notifier.fetch_events_for_today(mock_service)

        # ASSERT
        self.assertEqual(result, [{"id": "test_event"}])
        mock_events.list.assert_called_once()

    @patch("calendar_notifier.build")
    def test_fetch_tasks_for_today(self, mock_build: MagicMock) -> None:
        # ARRANGE
        mock_service = Mock()
        mock_tasks = Mock()
        mock_list = Mock()

        mock_service.tasks.return_value = mock_tasks
        mock_tasks.list.return_value = mock_list
        mock_list.execute.return_value = {"items": [{"id": "test_task"}]}

        # ACT
        result = calendar_notifier.fetch_tasks_for_today(mock_service)

        # ASSERT
        self.assertEqual(result, [{"id": "test_task"}])
        mock_tasks.list.assert_called_once()

    @patch("subprocess.run")
    def test_show_notification(self, mock_run: MagicMock) -> None:
        # ACT
        calendar_notifier.show_notification("Test Title", "Test Message")

        # ASSERT
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[1], "Test Title")
        self.assertEqual(args[2], "Test Message")

    @patch("calendar_notifier.InstalledAppFlow")
    def test_load_credentials(self, mock_flow_class: MagicMock) -> None:
        # ARRANGE
        mock_flow = Mock()
        mock_creds = Mock()
        mock_flow_class.from_client_secrets_file.return_value = mock_flow
        mock_flow.run_local_server.return_value = mock_creds

        # ACT
        result = calendar_notifier.load_credentials()

        # ASSERT
        self.assertEqual(result, mock_creds)
        mock_flow_class.from_client_secrets_file.assert_called_once_with(
            calendar_notifier.CLIENT_SECRETS_FILE, calendar_notifier.SCOPES
        )
        mock_flow.run_local_server.assert_called_once_with(port=0)

    @patch("calendar_notifier.show_notification")
    @patch("calendar_notifier.fetch_tasks_for_today")
    @patch("calendar_notifier.fetch_events_for_today")
    @patch("calendar_notifier.build")
    @patch("calendar_notifier.load_credentials")
    @patch("calendar_notifier.time.sleep")
    def test_sends_notifications_only_once(
            self,
            mock_sleep,
            mock_load_creds,
            mock_build,
            mock_fetch_events,
            mock_fetch_tasks,
            mock_notify
    ):
        """Events/tasks are notified once, then skipped."""
        # --- Fake services returned by build() ---
        mock_build.return_value = MagicMock()

        # --- Fake data ---
        mock_fetch_events.return_value = [
            {"id": "ev1", "summary": "Meeting"},
            {"id": "ev2", "summary": "Lunch"},
        ]
        mock_fetch_tasks.return_value = [
            {"id": "t1", "title": "Buy milk"}
        ]

        # Make sleep raise StopIteration so main_loop runs exactly 1 cycle
        mock_sleep.side_effect = StopIteration

        # Run one loop
        with self.assertRaises(StopIteration):
            calendar_notifier.main_loop()

        # --- Assertions ---
        # Notifications sent for each unique ID
        self.assertEqual(mock_notify.call_count, 3)

        titles = [call.args[0] for call in mock_notify.call_args_list]
        self.assertIn("Meeting", titles)
        self.assertIn("Lunch", titles)
        self.assertIn("Buy milk", titles)