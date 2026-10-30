import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import digest_window as dw

NOW = datetime(2026, 10, 26, 8, 30)  # a Monday


class DigestWindowTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.state = os.path.join(self.dir, "state", "digest.json")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_first_run_covers_the_last_24_hours(self):
        start, end = dw.window(self.state, NOW)
        self.assertEqual(start, NOW - timedelta(hours=24))
        self.assertEqual(end, NOW)

    def test_window_starts_at_the_last_recorded_run(self):
        dw.record(self.state, datetime(2026, 10, 23, 8, 30))  # Friday
        start, _ = dw.window(self.state, NOW)
        self.assertEqual(start, datetime(2026, 10, 23, 8, 30))  # Monday covers the weekend

    def test_window_is_capped_at_seven_days(self):
        dw.record(self.state, datetime(2026, 9, 1, 8, 0))
        start, _ = dw.window(self.state, NOW)
        self.assertEqual(start, NOW - timedelta(days=7))

    def test_checking_the_window_does_not_write_state(self):
        dw.window(self.state, NOW)
        self.assertFalse(os.path.exists(self.state))

    def test_record_writes_iso_time(self):
        dw.record(self.state, NOW)
        self.assertEqual(json.load(open(self.state))["last_run"], "2026-10-26T08:30:00")

    def test_future_last_run_falls_back_to_24_hours(self):
        dw.record(self.state, NOW + timedelta(days=2))
        start, _ = dw.window(self.state, NOW)
        self.assertEqual(start, NOW - timedelta(hours=24))

    def test_corrupt_state_falls_back_to_24_hours(self):
        os.makedirs(os.path.dirname(self.state))
        open(self.state, "w").write("not json")
        start, _ = dw.window(self.state, NOW)
        self.assertEqual(start, NOW - timedelta(hours=24))


if __name__ == "__main__":
    unittest.main()
