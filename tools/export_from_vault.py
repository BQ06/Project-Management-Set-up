#!/usr/bin/env python3
"""Rebuild this repo's copy of the agents and skills from a vault's .claude folder.

Usage: export_from_vault.py VAULT_PATH [--repo PATH] [--map PATH]

Copies only the managed files (agents, skills, reference rules, scripts, ticket templates).
It never copies project-map.md, settings.local.json, plans, state or any vault note.

The package is shared, so it must not carry names from one team's own projects. An optional
private map in the vault (default VAULT/.claude/export-map.json, never exported) rewrites
those specifics to generic wording:

    {"replace": [["old text", "new text"], ...], "deny": ["Name", "Another"]}

Each replacement is a literal, case-sensitive text swap applied in order. Every term in "deny"
(case-insensitive) must be gone after the swaps, or nothing is copied. The transformed text is
then scanned for credentials, personal paths, email addresses and real IDs. If anything is
found, nothing is copied. Files in the repo that no longer exist in the vault are removed.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import scan_secrets  # noqa: E402


def load_map(path):
    if not path or not os.path.isfile(path):
        return {"replace": [], "deny": []}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {"replace": [tuple(x) for x in data.get("replace", [])], "deny": list(data.get("deny", []))}


def transform(texts, mapping):
    """Return (new_texts, unused_replacements). texts is {rel: text}."""
    out = dict(texts)
    unused = []
    for old, new in mapping["replace"]:
        hit = False
        for rel, text in out.items():
            if old in text:
                out[rel] = text.replace(old, new)
                hit = True
        if not hit:
            unused.append(old)
    return out, unused


def deny_findings(texts, deny):
    found = []
    for term in deny:
        pattern = re.compile(re.escape(term), re.I)
        for rel, text in sorted(texts.items()):
            for number, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    found.append((rel, number, "private term '%s' is still present" % term))
    return found


def export(vault, repo, map_path=None):
    """Return (copied, removed, findings, unused). Nothing is copied if findings is not empty."""
    if not os.path.isdir(os.path.join(vault, ".claude")):
        raise SystemExit("not a vault: %s has no .claude folder" % vault)
    if map_path is None:
        map_path = os.path.join(vault, ".claude", "export-map.json")
    mapping = load_map(map_path)
    source = common.collect(vault)
    texts = {}
    findings = []
    for rel, full in sorted(source.items()):
        try:
            with open(full, encoding="utf-8") as fh:
                texts[rel] = fh.read()
        except UnicodeDecodeError:
            findings.append((rel, 0, "not a UTF-8 text file"))
    texts, unused = transform(texts, mapping)
    findings += deny_findings(texts, mapping["deny"])
    for rel, text in sorted(texts.items()):
        findings += scan_secrets.scan_text(rel, text)
    if findings:
        return [], [], findings, unused
    copied = []
    for rel, text in sorted(texts.items()):
        dest = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        copied.append(rel)
    removed = []
    for rel, full in sorted(common.collect(repo).items()):
        if rel not in source:
            os.remove(full)
            removed.append(rel)
    return copied, removed, [], unused


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    ap.add_argument("--map", default=None, help="path to a private export map (default: VAULT/.claude/export-map.json)")
    args = ap.parse_args()
    vault = os.path.abspath(args.vault)
    map_path = args.map or os.path.join(vault, ".claude", "export-map.json")
    if not os.path.isfile(map_path):
        print("NOTE: no export map at %s, so files are copied exactly as they are." % map_path)
    copied, removed, findings, unused = export(vault, os.path.abspath(args.repo), args.map)
    for old in unused:
        print("WARN: replacement matched nothing (map is out of date): %r" % old[:60])
    if findings:
        for rel, line, what in findings:
            print("BLOCKED %s%s: %s" % (rel, (":%d" % line) if line else "", what))
        print("Nothing was copied. Fix the source files or the export map and run again.")
        sys.exit(1)
    print("Copied %d files, removed %d stale files." % (len(copied), len(removed)))
    for rel in removed:
        print("  removed %s" % rel)


if __name__ == "__main__":
    main()
