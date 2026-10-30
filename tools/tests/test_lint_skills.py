import os
import unittest

import helpers
import lint_skills


def errors(root):
    return [m for lvl, m in lint_skills.lint(root) if lvl == "ERROR"]


class LintTests(unittest.TestCase):
    def test_good_package_passes(self):
        self.assertEqual(errors(helpers.make_root()), [])

    def test_tokens_keep_spaces_inside_brackets(self):
        toks = lint_skills.tokens("Read Edit(**/Ticket Digests/**) Bash(python3 a.py *)")
        self.assertEqual(toks, ["Read", "Edit(**/Ticket Digests/**)", "Bash(python3 a.py *)"])

    def test_write_path_rule_is_an_error(self):
        bad = helpers.GOOD_SKILL.replace("Read Grep", "Write(**/x/**) Read Grep")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("never matches" in m for m in errors(root)))

    def test_mcp_write_tool_is_an_error(self):
        bad = helpers.GOOD_SKILL.replace("mcp__claude_ai_Linear__list_issues", "mcp__claude_ai_Linear__save_issue")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("must not be pre-approved" in m for m in errors(root)))

    def test_unknown_tool_is_an_error(self):
        bad = helpers.GOOD_SKILL.replace("Read Grep", "Reed Grep")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("unknown tool" in m for m in errors(root)))

    def test_name_must_match_folder(self):
        bad = helpers.GOOD_SKILL.replace("name: demo", "name: other")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("does not match its folder" in m for m in errors(root)))

    def test_missing_referenced_file_is_an_error(self):
        bad = helpers.GOOD_SKILL + "Run `.claude/scripts/missing.py`.\n"
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("missing.py" in m for m in errors(root)))

    def test_generated_state_file_is_not_flagged(self):
        ok = helpers.GOOD_SKILL + "State lives in `.claude/state/digest.json`.\n"
        root = helpers.make_root({".claude/skills/demo/SKILL.md": ok})
        self.assertEqual(errors(root), [])

    def test_example_file_counts_for_a_vault_owned_file(self):
        root = helpers.make_root()
        os.remove(os.path.join(root, ".claude/project-map.md"))
        helpers.write(root, ".claude/project-map.example.md", "# example\n")
        ok = helpers.GOOD_SKILL + "Edit `.claude/project-map.md`.\n"
        helpers.write(root, ".claude/skills/demo/SKILL.md", ok)
        self.assertEqual(errors(root), [])

    def test_reading_ticket_rules_requires_naming_the_standing_rulings(self):
        bad = helpers.GOOD_SKILL + "Read `.claude/reference/ticket-rules.md`.\n"
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("Standing rulings" in m for m in errors(root)))
        good = bad + "Include the Standing rulings.\n"
        root = helpers.make_root({".claude/skills/demo/SKILL.md": good})
        self.assertEqual(errors(root), [])

    def test_skill_that_writes_to_linear_must_wait_for_a_yes(self):
        bad = helpers.GOOD_SKILL + "Then call save_issue.\n"
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("clear yes" in m for m in errors(root)))
        good = bad + "Wait for a clear yes first.\n"
        root = helpers.make_root({".claude/skills/demo/SKILL.md": good})
        self.assertEqual(errors(root), [])

    def test_skill_must_read_the_project_map(self):
        bad = helpers.GOOD_SKILL.replace(".claude/project-map.md", "the map")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any("project-map" in m for m in errors(root)))

    def test_agent_must_be_read_only(self):
        bad = helpers.GOOD_AGENT.replace("Read, Grep", "Edit, Read, Grep")
        root = helpers.make_root({".claude/agents/helper.md": bad})
        self.assertTrue(any("read-only agent" in m for m in errors(root)))

    def test_agent_needs_a_tools_list(self):
        bad = helpers.GOOD_AGENT.replace("tools: Read, Grep, Glob, mcp__claude_ai_Linear__list_issues\n", "")
        root = helpers.make_root({".claude/agents/helper.md": bad})
        self.assertTrue(any("no tools list" in m for m in errors(root)))

    def test_not_manual_only_is_a_warning_not_an_error(self):
        warn = helpers.GOOD_SKILL.replace("disable-model-invocation: true\n", "")
        root = helpers.make_root({".claude/skills/demo/SKILL.md": warn})
        found = lint_skills.lint(root)
        self.assertTrue(any(l == "WARN" for l, _ in found))
        self.assertEqual(errors(root), [])


if __name__ == "__main__":
    unittest.main()
