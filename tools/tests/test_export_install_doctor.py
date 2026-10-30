import os
import tempfile
import unittest

import helpers  # noqa: F401  (sets up the import path first)
import common
import doctor
import export_from_vault
import install

MAP = """# Project map

## Projects

### Demo
- Vault folder: `Demo`
- Linear project: `demo`
- Start notes: `Overview.md`
"""


class ExportTests(unittest.TestCase):
    def test_copies_only_managed_files(self):
        vault = helpers.make_root({
            ".claude/project-map.md": MAP,
            ".claude/settings.local.json": "{}",
            ".claude/plans/ledger.md": "log",
            "ExampleProject/Note.md": "a vault note",
        })
        repo = tempfile.mkdtemp()
        copied, removed, findings, _u = export_from_vault.export(vault, repo)
        self.assertEqual(findings, [])
        self.assertIn(".claude/skills/demo/SKILL.md", copied)
        for rel in (".claude/project-map.md", ".claude/settings.local.json", ".claude/plans/ledger.md", "ExampleProject/Note.md"):
            self.assertFalse(os.path.exists(os.path.join(repo, rel)), rel)

    def test_blocks_when_a_source_file_has_a_secret(self):
        vault = helpers.make_root({".claude/reference/ticket-rules.md": "key: Bearer " + "c" * 24})
        repo = tempfile.mkdtemp()
        copied, _removed, findings, _u = export_from_vault.export(vault, repo)
        self.assertEqual(copied, [])
        self.assertTrue(findings)
        self.assertEqual(common.collect(repo), {})

    def test_removes_files_deleted_from_the_vault(self):
        vault = helpers.make_root()
        repo = tempfile.mkdtemp()
        helpers.write(repo, ".claude/skills/old/SKILL.md", helpers.GOOD_SKILL.replace("demo", "old"))
        _copied, removed, _f, _u = export_from_vault.export(vault, repo)
        self.assertIn(".claude/skills/old/SKILL.md", removed)


class ExportMapTests(unittest.TestCase):
    def vault_with_map(self, rules, mapping):
        import json
        return helpers.make_root({
            ".claude/reference/ticket-rules.md": rules,
            ".claude/export-map.json": json.dumps(mapping),
        })

    def test_map_rewrites_text_and_the_map_itself_is_not_exported(self):
        vault = self.vault_with_map("Ask Jane about Acme Corp.\n", {"replace": [["Jane", "the PM"], ["Acme Corp", "the client"]], "deny": ["Jane", "Acme"]})
        repo = tempfile.mkdtemp()
        copied, _r, findings, unused = export_from_vault.export(vault, repo)
        self.assertEqual(findings, [])
        self.assertEqual(unused, [])
        with open(os.path.join(repo, ".claude/reference/ticket-rules.md")) as fh:
            self.assertEqual(fh.read(), "Ask the PM about the client.\n")
        self.assertFalse(os.path.exists(os.path.join(repo, ".claude/export-map.json")))

    def test_a_private_term_that_survives_blocks_the_export(self):
        vault = self.vault_with_map("Ask Jane about Acme Corp.\n", {"replace": [["Jane", "the PM"]], "deny": ["Jane", "Acme"]})
        repo = tempfile.mkdtemp()
        copied, _r, findings, _u = export_from_vault.export(vault, repo)
        self.assertEqual(copied, [])
        self.assertTrue(any("'Acme'" in f[2] for f in findings))
        self.assertEqual(common.collect(repo), {})

    def test_deny_is_case_insensitive(self):
        vault = self.vault_with_map("see ACME here\n", {"replace": [], "deny": ["acme"]})
        _c, _r, findings, _u = export_from_vault.export(vault, tempfile.mkdtemp())
        self.assertTrue(findings)

    def test_unused_replacement_is_reported(self):
        vault = self.vault_with_map("nothing special\n", {"replace": [["gone text", "x"]], "deny": []})
        _c, _r, findings, unused = export_from_vault.export(vault, tempfile.mkdtemp())
        self.assertEqual(findings, [])
        self.assertEqual(unused, ["gone text"])

    def test_secret_that_appears_only_after_a_rewrite_is_still_caught(self):
        vault = self.vault_with_map("token PLACEHOLDER\n", {"replace": [["PLACEHOLDER", "Bearer " + "d" * 24]], "deny": []})
        copied, _r, findings, _u = export_from_vault.export(vault, tempfile.mkdtemp())
        self.assertEqual(copied, [])
        self.assertTrue(findings)


class InstallTests(unittest.TestCase):
    def make_repo(self):
        repo = helpers.make_root({
            ".claude/project-map.example.md": MAP,
            ".claude/settings.example.json": '{"permissions": {"allow": []}}',
            "CLAUDE.example.md": "# example",
            ".claude/pm-config.example.json": '{"build_team": "DEV"}',
        })
        return repo

    def test_installs_and_creates_examples(self):
        repo, vault = self.make_repo(), tempfile.mkdtemp()
        copied, skipped, created = install.install(vault, repo=repo)
        self.assertIn(".claude/skills/demo/SKILL.md", copied)
        self.assertEqual(sorted(created), [".claude/pm-config.json", ".claude/project-map.md", ".claude/settings.local.json", "CLAUDE.md"])
        self.assertEqual(skipped, [])

    def test_never_overwrites_existing_files(self):
        repo, vault = self.make_repo(), tempfile.mkdtemp()
        helpers.write(vault, ".claude/skills/demo/SKILL.md", "mine")
        helpers.write(vault, ".claude/project-map.md", "my real map")
        _c, skipped, created = install.install(vault, repo=repo)
        self.assertIn(".claude/skills/demo/SKILL.md", skipped)
        self.assertNotIn(".claude/project-map.md", created)
        with open(os.path.join(vault, ".claude/skills/demo/SKILL.md")) as fh:
            self.assertEqual(fh.read(), "mine")

    def test_force_overwrites_package_files_but_never_project_data(self):
        repo, vault = self.make_repo(), tempfile.mkdtemp()
        helpers.write(vault, ".claude/skills/demo/SKILL.md", "mine")
        helpers.write(vault, ".claude/project-map.md", "my real map")
        install.install(vault, force=True, repo=repo)
        with open(os.path.join(vault, ".claude/skills/demo/SKILL.md")) as fh:
            self.assertEqual(fh.read(), helpers.GOOD_SKILL)
        with open(os.path.join(vault, ".claude/project-map.md")) as fh:
            self.assertEqual(fh.read(), "my real map")


class DoctorTests(unittest.TestCase):
    def levels(self, root):
        return [(lvl, m) for lvl, m in doctor.run(root)]

    def test_good_vault_has_no_failures(self):
        root = helpers.make_root({".claude/project-map.md": MAP, "Demo/Overview.md": "x"})
        self.assertEqual([m for lvl, m in self.levels(root) if lvl == "FAIL"], [])

    def test_missing_vault_folder_fails(self):
        root = helpers.make_root({".claude/project-map.md": MAP})
        self.assertTrue(any(l == "FAIL" and "does not exist" in m for l, m in self.levels(root)))

    def test_missing_start_note_warns(self):
        root = helpers.make_root({".claude/project-map.md": MAP, "Demo/Other.md": "x"})
        self.assertTrue(any(l == "WARN" and "Overview.md" in m for l, m in self.levels(root)))

    def test_credential_in_project_map_fails(self):
        root = helpers.make_root({".claude/project-map.md": MAP + "\napi key: " + "k" * 20 + "\n", "Demo/Overview.md": "x"})
        self.assertTrue(any(l == "FAIL" and "credential" in m for l, m in self.levels(root)))

    def test_no_project_map_fails(self):
        root = helpers.make_root()
        os.remove(os.path.join(root, ".claude/project-map.md"))
        self.assertTrue(any(l == "FAIL" and "project-map" in m for l, m in self.levels(root)))

    def test_bad_settings_json_fails_and_write_rule_warns(self):
        root = helpers.make_root({".claude/project-map.md": MAP, "Demo/Overview.md": "x", ".claude/settings.local.json": "{bad"})
        self.assertTrue(any(l == "FAIL" and "valid JSON" in m for l, m in self.levels(root)))
        root = helpers.make_root({".claude/project-map.md": MAP, "Demo/Overview.md": "x",
                                  ".claude/settings.local.json": '{"permissions": {"allow": ["Write(**/x/**)"]}}'})
        self.assertTrue(any(l == "WARN" and "never matches" in m for l, m in self.levels(root)))

    def test_linter_errors_become_failures(self):
        bad = helpers.GOOD_SKILL.replace("name: demo", "name: wrong")
        root = helpers.make_root({".claude/project-map.md": MAP, "Demo/Overview.md": "x", ".claude/skills/demo/SKILL.md": bad})
        self.assertTrue(any(l == "FAIL" and "does not match" in m for l, m in self.levels(root)))

    def test_pm_config_is_checked(self):
        base = {".claude/project-map.md": MAP, "Demo/Overview.md": "x"}
        root = helpers.make_root(dict(base, **{".claude/pm-config.json": '{"build_team": "ENG", "design_team": "UX"}'}))
        self.assertTrue(any(l == "PASS" and "build team ENG" in m for l, m in self.levels(root)))
        root = helpers.make_root(dict(base, **{".claude/pm-config.json": "{nope"}))
        self.assertTrue(any(l == "FAIL" and "pm-config.json" in m for l, m in self.levels(root)))
        root = helpers.make_root(dict(base, **{".claude/pm-config.json": '{"team": "X"}'}))
        self.assertTrue(any(l == "WARN" and "unknown keys" in m for l, m in self.levels(root)))

    def test_parse_projects(self):
        got = doctor.parse_projects(MAP)
        self.assertEqual(got["Demo"], {"folder": "Demo", "linear": "demo", "start": ["Overview.md"]})


if __name__ == "__main__":
    unittest.main()
