#!/usr/bin/env python3
"""List notes in a project folder that are new or edited since the last recorded run.

Read-only for the vault. State lives in .claude/state/last-processed.json.

  changed_notes.py --project ExampleProject            report changes since the last record
  changed_notes.py --project ExampleProject --since 2026-10-15   report notes modified since a date
  changed_notes.py --project ExampleProject --record   save the current state as the new baseline

A note counts as changed only when its content hash differs, so a note that was merely touched
(Obsidian sync, bulk edits) is skipped. Digest folders and sensitive notes are never reported.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
DEFAULT_MAP = os.path.join(HERE, "..", "project-map.md")
DEFAULT_STATE = os.path.join(HERE, "..", "state", "last-processed.json")
DIGEST_DIRS = ("Ticket Digests", "Product Walks")
SENSITIVE_NAME = re.compile(r"credential|password|login|api key|secret|token", re.I)


class NoBaseline(Exception):
    pass


def sensitive_paths(map_file):
    """Paths listed as backticked bullets under the 'Sensitive notes' heading."""
    paths, inside = [], False
    with open(map_file, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## "):
                inside = line.lower().startswith("## sensitive")
                continue
            m = re.match(r"^- `([^`]+)`", line) if inside else None
            if m:
                paths.append(m.group(1))
    return paths


def excluded(rel, sensitive):
    parts = rel.split("/")
    if any(d in parts[:-1] for d in DIGEST_DIRS) or not rel.endswith(".md"):
        return True
    if os.path.basename(rel) == "CLAUDE.md":
        return True  # folder config, not project context
    if SENSITIVE_NAME.search(os.path.basename(rel)):
        return True
    for s in sensitive:
        if rel == s or (s.endswith("/") and rel.startswith(s)) or rel.startswith(s + "/"):
            return True
    return False


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def scan(root, project, map_file):
    sensitive = sensitive_paths(map_file)
    found = {}
    base = os.path.join(root, project)
    for dirpath, _dirs, files in os.walk(base):
        for name in files:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if excluded(rel, sensitive):
                continue
            found[rel] = {"mtime": os.path.getmtime(full), "sha256": sha(full)}
    return found


def load_state(state_file):
    if not os.path.exists(state_file):
        return {}
    with open(state_file, encoding="utf-8") as fh:
        return json.load(fh)


def changed(root, project, state_file, map_file, since=None):
    current = scan(root, project, map_file)
    if since is not None:
        return [{"path": p, "status": "modified"} for p, v in sorted(current.items()) if v["mtime"] >= since]
    state = load_state(state_file).get(project)
    if state is None:
        raise NoBaseline("no baseline for %s: run with --record to save one, or pass --since DATE" % project)
    old = state["files"]
    out = []
    for p, v in sorted(current.items()):
        if p not in old:
            out.append({"path": p, "status": "new"})
        elif old[p]["sha256"] != v["sha256"]:
            out.append({"path": p, "status": "modified"})
    return out


def record(root, project, state_file, map_file):
    data = load_state(state_file)
    data[project] = {"processed_at": datetime.now().isoformat(timespec="seconds"),
                     "files": scan(root, project, map_file)}
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)


def parse_since(text):
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return time.time() - float(text) * 86400


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="vault folder name, e.g. ExampleProject")
    ap.add_argument("--since", help="ISO date, or a number of days back")
    ap.add_argument("--record", action="store_true", help="save the current state as the baseline")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--map", default=DEFAULT_MAP)
    ap.add_argument("--state", default=DEFAULT_STATE)
    args = ap.parse_args()
    if args.record:
        record(args.root, args.project, args.state, args.map)
        print("recorded baseline for %s" % args.project)
        return
    try:
        since = parse_since(args.since) if args.since else None
        print(json.dumps(changed(args.root, args.project, args.state, args.map, since), indent=1))
    except NoBaseline as exc:
        print("NO BASELINE: %s" % exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
