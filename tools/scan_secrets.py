#!/usr/bin/env python3
"""Scan a folder for things that must never reach GitHub: credentials, personal paths,
email addresses, real Slack channel IDs, real artifact links and credential-looking files.

Usage: scan_secrets.py [--root PATH]
Prints file:line and the kind of finding, with the matched text masked. Never prints a value.
Exits 1 if anything is found. A line containing 'scan:ignore' is skipped.
"""
import argparse
import json
import os
import re
import sys

PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Stripe key", re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{10,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("credential assignment", re.compile(
        r"(?i)\b(?:password|passwd|secret|api[_ -]?key|access[_ -]?token|client[_ -]?secret)\b[\"'\s*:=]+[A-Za-z0-9/+_.!@#$%^&-]{12,}")),
    ("personal absolute path", re.compile(r"/Users/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\")),
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.(?:com|org)\b|users\.noreply\.github\.com\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("Slack channel ID", re.compile(r"\bC0[A-Z0-9]{8,10}\b")),
    ("real artifact link", re.compile(r"claude\.ai/(?:code/)?artifact/[A-Za-z0-9]{12,}")),
]
BAD_NAME = re.compile(r"credential|password|secret|token|api.?key|login", re.I)
BAD_EXT = {".zip", ".env", ".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_FILES = {"scan_secrets.py", "test_scan_secrets.py"}
CREDENTIAL_LABELS = {"private key", "AWS access key", "Stripe key", "Slack token", "GitHub token", "bearer token", "JWT", "credential assignment"}


def mask(text):
    return text[:4] + "****" if len(text) > 4 else "****"


def scan_file(path, rel, only=None):
    found = []
    base = os.path.basename(path)
    ext = os.path.splitext(base)[1].lower()
    if base == ".DS_Store":
        return [(rel, 0, "macOS .DS_Store file")]
    if ext in BAD_EXT or base == ".env":
        found.append((rel, 0, "file type that should not be committed (%s)" % (ext or base)))
    if BAD_NAME.search(base) and base not in SKIP_FILES:
        found.append((rel, 0, "file name looks like a credential file"))
    if base in SKIP_FILES:
        return found
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (UnicodeDecodeError, OSError):
        return found
    return found + scan_text(rel, text, only)


def scan_text(rel, text, only=None):
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        if "scan:ignore" in line:
            continue
        for label, pattern in PATTERNS:
            if only is not None and label not in only:
                continue
            m = pattern.search(line)
            if m:
                found.append((rel, number, "%s (%s)" % (label, mask(m.group(0)))))
    return found


def deny_terms(map_path):
    """Private terms from an export map (kept outside the repo). Returns a list."""
    with open(map_path, encoding="utf-8") as fh:
        return list(json.load(fh).get("deny", []))


def scan_for_terms(root, terms):
    found = []
    pats = [(t, re.compile(re.escape(t), re.I)) for t in terms]
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(folder, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            rel = os.path.relpath(path, root)
            for number, line in enumerate(text.splitlines(), 1):
                for term, pat in pats:
                    if pat.search(line):
                        found.append((rel, number, "private term '%s'" % term))
    return sorted(found)


def scan(root):
    found = []
    for folder, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(folder, name)
            found += scan_file(path, os.path.relpath(path, root))
    return sorted(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    ap.add_argument("--deny-map", default=None, help="an export map (JSON with a 'deny' list) kept outside the repo")
    args = ap.parse_args()
    problems = scan(args.root)
    if args.deny_map:
        problems += scan_for_terms(args.root, deny_terms(args.deny_map))
    for rel, line, what in problems:
        print("%s%s: %s" % (rel, (":%d" % line) if line else "", what))
    if not problems:
        print("OK: nothing sensitive found")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
