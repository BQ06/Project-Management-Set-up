import os
import unittest

import helpers
import lint_skills
import retarget_mcp


class RetargetTests(unittest.TestCase):
    def test_parse_map_accepts_known_services(self):
        self.assertEqual(retarget_mcp.parse_map(["Linear=linear", "Google_Drive=gdrive"]), {"Linear": "linear", "Google_Drive": "gdrive"})

    def test_parse_map_rejects_unknown_service_and_bad_names(self):
        with self.assertRaises(SystemExit):
            retarget_mcp.parse_map(["Jira=jira"])
        with self.assertRaises(SystemExit):
            retarget_mcp.parse_map(["Linear=lin ear"])
        with self.assertRaises(SystemExit):
            retarget_mcp.parse_map(["Linear"])

    def test_text_is_rewritten_and_counted(self):
        text = "mcp__claude_ai_Linear__list_issues mcp__claude_ai_Linear__get_issue mcp__claude_ai_Slack__slack_read_channel"
        new, count = retarget_mcp.retarget_text(text, {"Linear": "linear"})
        self.assertEqual(count, 2)
        self.assertEqual(new, "mcp__linear__list_issues mcp__linear__get_issue mcp__claude_ai_Slack__slack_read_channel")

    def test_dry_run_changes_nothing_and_write_applies_it(self):
        root = helpers.make_root()
        path = os.path.join(root, ".claude/skills/demo/SKILL.md")
        before = open(path).read()
        changed = retarget_mcp.run(root, {"Linear": "linear"}, write=False)
        self.assertTrue(changed)
        self.assertEqual(open(path).read(), before)
        retarget_mcp.run(root, {"Linear": "linear"}, write=True)
        after = open(path).read()
        self.assertIn("mcp__linear__list_issues", after)
        self.assertNotIn("claude_ai_Linear", after)

    def test_retargeted_package_still_passes_the_linter(self):
        root = helpers.make_root()
        retarget_mcp.run(root, {"Linear": "linear"}, write=True)
        self.assertEqual([m for lvl, m in lint_skills.lint(root) if lvl == "ERROR"], [])

    def test_retargeted_write_tools_are_still_blocked_by_the_linter(self):
        bad = helpers.GOOD_SKILL.replace("mcp__claude_ai_Linear__list_issues", "mcp__claude_ai_Linear__save_issue")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        retarget_mcp.run(root, {"Linear": "linear"}, write=True)
        self.assertTrue(any("must not be pre-approved" in m for lvl, m in lint_skills.lint(root) if lvl == "ERROR"))


if __name__ == "__main__":
    unittest.main()
