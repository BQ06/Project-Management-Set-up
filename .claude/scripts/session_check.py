#!/usr/bin/env python3
"""Session-start check for the daily board review.

Prints a reminder when it is 9 am or later (Europe/London) and a project has no digest dated today.
Used as a Claude Code SessionStart hook; it reads only and writes nothing.
Usage: session_check.py [vault_root]
"""
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
HERE = os.path.dirname(os.path.abspath(__file__))
DUE_HOUR = 9


def project_folders(root):
    path = os.path.join(root, ".claude", "project-map.md")
    with open(path, encoding="utf-8") as fh:
        return re.findall(r"^- Vault folder: `([^`]+)`", fh.read(), re.M)


def missing_projects(root, now):
    if now.astimezone(LONDON).hour < DUE_HOUR:
        return []
    today = now.astimezone(LONDON).strftime("%Y-%m-%d")
    return [p for p in project_folders(root)
            if not os.path.isfile(os.path.join(root, p, "Ticket Digests", today + ".md"))]


def message(projects):
    if not projects:
        return ""
    return ("Daily board review is due: no review has been written today for %s. "
            "Run /board-refresh for those projects only (proposals only), and schedule the 9 am run for this session if it is not scheduled."
            % ", ".join(projects))


def report(root, now):
    """The text to show at session start: run now after 9 am, schedule for 9 am before it."""
    now = now.astimezone(LONDON)
    if now.hour >= DUE_HOUR:
        return message(missing_projects(root, now))
    today = now.strftime("%Y-%m-%d")
    pending = [p for p in project_folders(root)
               if not os.path.isfile(os.path.join(root, p, "Ticket Digests", today + ".md"))]
    if not pending:
        return ""
    return ("It is before 9 am. Schedule a daily 9 am run of /board-refresh all for this session "
            "(skip if today's reviews already exist), unless one is already scheduled. Proposals only.")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "..", ".."))
    text = report(root, datetime.now(LONDON))
    if text:
        print(text)


if __name__ == "__main__":
    main()
