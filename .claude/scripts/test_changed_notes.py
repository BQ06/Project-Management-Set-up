import json
import os
import shutil
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import changed_notes as cn

MAP = """# Project map

## Sensitive notes (never read)
- `Proj/Secrets Note.md`
- `Proj/Keys Folder/`
- Any other note whose name contains: credential, password.

## Projects
"""


class ChangedNotesTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "Proj", "Ticket Digests"))
        os.makedirs(os.path.join(self.root, "Proj", "Keys Folder"))
        os.makedirs(os.path.join(self.root, ".claude", "state"))
        self.map = os.path.join(self.root, "map.md")
        self.state = os.path.join(self.root, ".claude", "state", "last-processed.json")
        with open(self.map, "w") as fh:
            fh.write(MAP)
        self.write("Proj/Overview.md", "overview")
        self.write("Proj/Scope.md", "scope")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        with open(path, "w") as fh:
            fh.write(text)
        return path

    def run_cn(self, **kw):
        return cn.changed(self.root, "Proj", self.state, self.map, **kw)

    def test_no_state_and_no_since_refuses(self):
        with self.assertRaises(cn.NoBaseline):
            self.run_cn()

    def test_baseline_records_then_reports_nothing(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.assertEqual(self.run_cn(), [])

    def test_touched_but_unedited_is_skipped(self):
        cn.record(self.root, "Proj", self.state, self.map)
        later = time.time() + 100
        os.utime(os.path.join(self.root, "Proj", "Overview.md"), (later, later))
        self.assertEqual(self.run_cn(), [])

    def test_edited_note_is_reported_as_modified(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/Scope.md", "scope changed")
        self.assertEqual(self.run_cn(), [{"path": "Proj/Scope.md", "status": "modified"}])

    def test_new_note_is_reported_as_new(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/New.md", "new")
        self.assertEqual(self.run_cn(), [{"path": "Proj/New.md", "status": "new"}])

    def test_digest_folder_is_ignored(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/Ticket Digests/2026-10-23.md", "digest")
        self.assertEqual(self.run_cn(), [])

    def test_product_walks_folder_is_ignored(self):
        os.makedirs(os.path.join(self.root, "Proj", "Product Walks"))
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/Product Walks/2026-11-06.md", "walk")
        self.assertEqual(self.run_cn(), [])

    def test_sensitive_paths_and_names_are_ignored(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/Secrets Note.md", "x")
        self.write("Proj/Keys Folder/a.md", "x")
        self.write("Proj/Staging Credentials.md", "x")
        self.assertEqual(self.run_cn(), [])

    def test_folder_claude_md_is_ignored(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/CLAUDE.md", "config")
        self.assertEqual(self.run_cn(), [])

    def test_non_markdown_is_ignored(self):
        cn.record(self.root, "Proj", self.state, self.map)
        self.write("Proj/image.png", "x")
        self.assertEqual(self.run_cn(), [])

    def test_since_window_uses_modified_time(self):
        old = time.time() - 10 * 86400
        os.utime(os.path.join(self.root, "Proj", "Overview.md"), (old, old))
        got = self.run_cn(since=time.time() - 86400)
        self.assertEqual([c["path"] for c in got], ["Proj/Scope.md"])

    def test_checking_does_not_write_state(self):
        cn.record(self.root, "Proj", self.state, self.map)
        before = open(self.state).read()
        self.write("Proj/Scope.md", "changed")
        self.run_cn()
        self.assertEqual(open(self.state).read(), before)

    def test_record_then_edit_state_is_per_project(self):
        cn.record(self.root, "Proj", self.state, self.map)
        data = json.load(open(self.state))
        self.assertIn("Proj", data)


if __name__ == "__main__":
    unittest.main()
