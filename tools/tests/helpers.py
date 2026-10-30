import os
import sys
import tempfile

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

GOOD_SKILL = """---
name: demo
description: A demo skill.
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash(python3 .claude/scripts/demo.py *) Edit(**/Ticket Digests/**) mcp__claude_ai_Linear__list_issues
---
Read first: `.claude/project-map.md`.
"""
GOOD_AGENT = """---
name: helper
description: A read-only helper.
tools: Read, Grep, Glob, mcp__claude_ai_Linear__list_issues
---
Read `.claude/project-map.md`.
"""


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def make_root(extra=None):
    """A small valid package in a temp folder. Returns the folder path."""
    root = tempfile.mkdtemp()
    write(root, ".claude/skills/demo/SKILL.md", GOOD_SKILL)
    write(root, ".claude/agents/helper.md", GOOD_AGENT)
    write(root, ".claude/project-map.md", "# Map\n")
    write(root, ".claude/scripts/demo.py", "print('hi')\n")
    for name in ("standard.md", "epic.md", "design.md"):
        write(root, "Templates/Tickets/" + name, "# t\n")
    write(root, ".claude/reference/ticket-rules.md", "# rules\n")
    write(root, ".claude/reference/vault-update-rules.md", "# rules\n")
    write(root, ".claude/agents/project-manager.md", GOOD_AGENT.replace("name: helper", "name: project-manager"))
    write(root, ".claude/scripts/check_ticket.py", "print('ok')\n")
    for rel, text in (extra or {}).items():
        write(root, rel, text)
    return root
