import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_check as sc

LONDON = ZoneInfo("Europe/London")
MAP = """### ExampleProject
- Vault folder: `ExampleProject`

### ExampleProject Two
- Vault folder: `ExampleProject Two`
"""


class SessionCheckTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, ".claude"))
        with open(os.path.join(self.root, ".claude", "project-map.md"), "w") as fh:
            fh.write(MAP)

    def tearDown(self):
        shutil.rmtree(self.root)

    def digest(self, project, date):
        folder = os.path.join(self.root, project, "Ticket Digests")
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, date + ".md"), "w").close()

    def test_before_nine_nothing_is_due(self):
        now = datetime(2026, 11, 6, 8, 59, tzinfo=LONDON)
        self.assertEqual(sc.missing_projects(self.root, now), [])

    def test_after_nine_lists_projects_without_todays_digest(self):
        now = datetime(2026, 11, 6, 9, 5, tzinfo=LONDON)
        self.assertEqual(sc.missing_projects(self.root, now), ["ExampleProject", "ExampleProject Two"])

    def test_a_project_with_todays_digest_is_not_listed(self):
        self.digest("ExampleProject", "2026-11-06")
        now = datetime(2026, 11, 6, 10, 0, tzinfo=LONDON)
        self.assertEqual(sc.missing_projects(self.root, now), ["ExampleProject Two"])

    def test_yesterdays_digest_does_not_count(self):
        self.digest("ExampleProject", "2026-11-05")
        now = datetime(2026, 11, 6, 10, 0, tzinfo=LONDON)
        self.assertIn("ExampleProject", sc.missing_projects(self.root, now))

    def test_message_names_the_command_and_projects(self):
        msg = sc.message(["ExampleProject"])
        self.assertIn("/board-refresh", msg)
        self.assertIn("ExampleProject", msg)

    def test_no_message_when_nothing_is_due(self):
        self.assertEqual(sc.message([]), "")

    def test_before_nine_asks_for_the_nine_am_schedule(self):
        now = datetime(2026, 11, 6, 8, 0, tzinfo=LONDON)
        text = sc.report(self.root, now)
        self.assertIn("9 am", text)
        self.assertIn("schedule", text.lower())

    def test_before_nine_stays_quiet_when_today_is_done(self):
        for p in ("ExampleProject", "ExampleProject Two"):
            self.digest(p, "2026-11-06")
        now = datetime(2026, 11, 6, 8, 0, tzinfo=LONDON)
        self.assertEqual(sc.report(self.root, now), "")

    def test_after_nine_report_says_run_now(self):
        now = datetime(2026, 11, 6, 9, 30, tzinfo=LONDON)
        self.assertIn("/board-refresh", sc.report(self.root, now))


if __name__ == "__main__":
    unittest.main()
