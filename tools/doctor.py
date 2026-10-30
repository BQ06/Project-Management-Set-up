#!/usr/bin/env python3
"""Check that a vault is set up so the agents and skills can run.

Usage: doctor.py [--root VAULT_PATH]
Prints PASS, WARN or FAIL per check. Exits 1 if any check FAILs.
It cannot see your connectors (Linear, Granola, Slack, Drive); it reminds you to check them.
"""
import argparse
import json
import os
import py_compile
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_skills  # noqa: E402
import scan_secrets  # noqa: E402

MIN_PYTHON = (3, 9)
TEMPLATES = ("standard.md", "epic.md", "design.md")
REQUIRED = [
    ".claude/agents/project-manager.md",
    ".claude/reference/ticket-rules.md",
    ".claude/reference/vault-update-rules.md",
    ".claude/scripts/check_ticket.py",
]


def parse_projects(text):
    """Return {name: {"folder": str, "linear": str, "start": [str]}} from a project map."""
    projects, current, in_projects = {}, None, False
    for line in text.splitlines():
        if line.startswith("## "):
            in_projects = line.strip() == "## Projects"
            current = None
            continue
        if in_projects and line.startswith("### "):
            current = line[4:].strip()
            projects[current] = {"folder": None, "linear": None, "start": []}
            continue
        if current is None:
            continue
        m = re.match(r"^- Vault folder:\s*`([^`]+)`", line)
        if m:
            projects[current]["folder"] = m.group(1)
        m = re.match(r"^- Linear project:\s*`([^`]+)`", line)
        if m:
            projects[current]["linear"] = m.group(1)
        m = re.match(r"^- Start notes:\s*(.+)$", line)
        if m:
            projects[current]["start"] = re.findall(r"`([^`]+)`", m.group(1))
    return projects


def run(root):
    results = []

    def add(level, msg):
        results.append((level, msg))

    if sys.version_info >= MIN_PYTHON:
        add("PASS", "Python %d.%d" % sys.version_info[:2])
    else:
        add("FAIL", "Python %d.%d or newer is needed" % MIN_PYTHON)

    for rel in REQUIRED:
        add("PASS" if os.path.isfile(os.path.join(root, rel)) else "FAIL", "found %s" % rel)
    for name in TEMPLATES:
        rel = "Templates/Tickets/" + name
        add("PASS" if os.path.isfile(os.path.join(root, rel)) else "FAIL", "found %s" % rel)

    scripts = os.path.join(root, ".claude", "scripts")
    if os.path.isdir(scripts):
        for name in sorted(os.listdir(scripts)):
            if name.endswith(".py"):
                try:
                    py_compile.compile(os.path.join(scripts, name), cfile=os.path.join(tempfile.gettempdir(), "doctor.pyc"), doraise=True)
                except py_compile.PyCompileError as exc:
                    add("FAIL", "script %s does not compile: %s" % (name, exc.msg.strip().splitlines()[-1]))
        add("PASS", "scripts compile")

    problems = lint_skills.lint(root)
    errors = [m for lvl, m in problems if lvl == "ERROR"]
    for m in errors:
        add("FAIL", m)
    if not errors:
        add("PASS", "agents and skills pass the linter")

    map_path = os.path.join(root, ".claude", "project-map.md")
    if not os.path.isfile(map_path):
        add("FAIL", "no .claude/project-map.md (copy .claude/project-map.example.md and edit it)")
    else:
        with open(map_path, encoding="utf-8") as fh:
            text = fh.read()
        projects = parse_projects(text)
        if not projects:
            add("FAIL", "project-map.md lists no projects under '## Projects'")
        for name, p in projects.items():
            folder = p["folder"]
            if not folder:
                add("FAIL", "%s: no 'Vault folder' line" % name)
                continue
            fpath = os.path.join(root, folder)
            if not os.path.isdir(fpath):
                add("FAIL", "%s: vault folder '%s' does not exist" % (name, folder))
                continue
            add("PASS", "%s: vault folder '%s' exists" % (name, folder))
            if not p["linear"]:
                add("WARN", "%s: no 'Linear project' line (ticket skills need it)" % name)
            for note in p["start"]:
                if not (os.path.exists(os.path.join(fpath, note)) or os.path.exists(os.path.join(root, note))):
                    add("WARN", "%s: start note '%s' not found" % (name, note))
        creds = scan_secrets.scan_file(map_path, "project-map.md", only=scan_secrets.CREDENTIAL_LABELS)
        for _rel, line, what in creds:
            add("FAIL", "project-map.md line %d looks like a credential: %s. Credentials never go in the map." % (line, what))
        if not creds:
            add("PASS", "project-map.md holds no credential-looking values")

    settings = os.path.join(root, ".claude", "settings.local.json")
    if os.path.isfile(settings):
        try:
            with open(settings, encoding="utf-8") as fh:
                data = json.load(fh)
            add("PASS", "settings.local.json is valid JSON")
            for rule in data.get("permissions", {}).get("allow", []):
                if rule.startswith("Write("):
                    add("WARN", "settings.local.json: '%s' never matches. Use Edit(path)" % rule)
                if re.match(r"^mcp__.*__(save|create|delete|update|send)_", rule):
                    add("WARN", "settings.local.json: '%s' would let a write run without a prompt" % rule)
        except ValueError as exc:
            add("FAIL", "settings.local.json is not valid JSON: %s" % exc)
    else:
        add("WARN", "no .claude/settings.local.json: every read will ask permission (see settings.example.json)")

    cfg = os.path.join(root, ".claude", "pm-config.json")
    if os.path.isfile(cfg):
        try:
            with open(cfg, encoding="utf-8") as fh:
                data = json.load(fh)
            unknown = sorted(set(data) - {"build_team", "design_team", "design_tag"})
            if unknown:
                add("WARN", "pm-config.json has unknown keys: %s" % ", ".join(unknown))
            else:
                add("PASS", "pm-config.json is valid (build team %s, design team %s)" % (data.get("build_team", "DEV"), data.get("design_team", "DES")))
        except ValueError as exc:
            add("FAIL", "pm-config.json is not valid JSON: %s" % exc)
    add("WARN", "check by hand: Linear, Granola, Slack and Google Drive connectors are connected in Claude Code (/mcp)")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    args = ap.parse_args()
    results = run(os.path.abspath(args.root))
    for level, msg in results:
        print("%s: %s" % (level, msg))
    failed = [r for r in results if r[0] == "FAIL"]
    print("%d checks, %d failed" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
