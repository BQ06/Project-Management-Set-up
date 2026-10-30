import os
import tempfile
import unittest

import helpers
import scan_secrets


def scan_text(text, name="note.md"):
    root = tempfile.mkdtemp()
    helpers.write(root, name, text)
    return scan_secrets.scan(root)


def kinds(found):
    return " | ".join(f[2] for f in found)


class ScanTests(unittest.TestCase):
    def test_clean_text_passes(self):
        self.assertEqual(scan_text("Nothing sensitive here. Contact support@example.com.\n"), [])

    def test_detects_stripe_key(self):
        text = "key is " + "sk_" + "test_" + "abcdefghijklmnop"
        self.assertIn("Stripe key", kinds(scan_text(text)))

    def test_detects_bearer_token(self):
        text = "Authorization: Bearer " + "a" * 24
        self.assertIn("bearer token", kinds(scan_text(text)))

    def test_short_fake_token_is_allowed(self):
        self.assertEqual(scan_text("Authorization: Bearer fake-token-123\n"), [])

    def test_detects_personal_path(self):
        self.assertIn("personal absolute path", kinds(scan_text("see /Users/someone/Documents/x")))

    def test_detects_real_email(self):
        self.assertIn("email address", kinds(scan_text("mail person@company.co.uk")))

    def test_detects_slack_channel_id(self):
        self.assertIn("Slack channel ID", kinds(scan_text("channel C0BP29BJCE5 here")))

    def test_detects_real_artifact_link(self):
        self.assertIn("real artifact link", kinds(scan_text("https://claude.ai/artifact/AgFb9nf2L6iw3YR4mmiH3c")))

    def test_placeholder_artifact_link_is_fine(self):
        self.assertEqual(scan_text("https://claude.ai/artifact/<artifact-id>\n"), [])

    def test_detects_credential_assignment(self):
        self.assertIn("credential assignment", kinds(scan_text("password: hunter2hunter2hunter2")))

    def test_ordinary_use_of_the_word_secret_is_fine(self):
        self.assertEqual(scan_text("Send the secret key in the headers of every call.\n"), [])

    def test_credential_file_names_are_flagged(self):
        found = scan_text("x", name="Partner Staging Credentials.md")
        self.assertIn("file name looks like a credential file", kinds(found))

    def test_zip_and_ds_store_are_flagged(self):
        self.assertIn("file type", kinds(scan_text("x", name="vault.zip")))
        self.assertIn(".DS_Store", kinds(scan_text("x", name=".DS_Store")))

    def test_ignore_marker_skips_a_line(self):
        self.assertEqual(scan_text("password: hunter2hunter2hunter2 scan:ignore\n"), [])

    def test_output_never_contains_the_secret(self):
        secret = "sk_" + "live_" + "ZZZZsecretvalue1234"
        found = scan_text(secret)
        self.assertNotIn("secretvalue", kinds(found))

    def test_private_terms_are_found_when_a_deny_list_is_given(self):
        root = tempfile.mkdtemp()
        helpers.write(root, "a.md", "Nothing here.\nAsk Acme about it.\n")
        found = scan_secrets.scan_for_terms(root, ["acme", "Other"])
        self.assertEqual([(f[0], f[1]) for f in found], [("a.md", 2)])
        self.assertEqual(scan_secrets.scan_for_terms(root, ["Other"]), [])

    def test_deny_terms_reads_the_map(self):
        import json
        root = tempfile.mkdtemp()
        path = helpers.write(root, "map.json", json.dumps({"replace": [], "deny": ["A", "B"]}))
        self.assertEqual(scan_secrets.deny_terms(path), ["A", "B"])

    def test_only_filter_limits_findings(self):
        found = scan_secrets.scan_file(
            helpers.write(tempfile.mkdtemp(), "m.md", "see /Users/me/x and Bearer " + "b" * 24), "m.md",
            only=scan_secrets.CREDENTIAL_LABELS)
        self.assertEqual([f[2].split(" (")[0] for f in found], ["bearer token"])


if __name__ == "__main__":
    unittest.main()
