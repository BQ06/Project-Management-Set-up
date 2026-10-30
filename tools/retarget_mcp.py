#!/usr/bin/env python3
"""Rewrite the MCP tool names in the skills, agent and rules to match how YOU connected a service.

The package names tools the way claude.ai connectors do, for example
mcp__claude_ai_Linear__list_issues. If you add a server another way (for example
`claude mcp add --transport http linear https://mcp.linear.app/mcp`), its tools are named
mcp__linear__list_issues and the skills would stop matching. This rewrites the prefix.

Usage:
  retarget_mcp.py VAULT --map Linear=linear --map Granola=granola          show what would change
  retarget_mcp.py VAULT --map Linear=linear --map Granola=granola --write  apply it

The names on the left are Linear, Granola, Slack and Google_Drive. The names on the right are the
server names `/mcp` shows in your Claude Code. Only the prefix is rewritten: check that the tool
names after it (for example slack_read_channel) are the ones your server really offers.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

KNOWN = ("Linear", "Granola", "Slack", "Google_Drive")
SERVER = re.compile(r"^[A-Za-z0-9_-]+$")
TARGETS = (".claude/skills", ".claude/agents", ".claude/reference", ".claude/settings.local.json", ".claude/settings.example.json")


def parse_map(pairs):
    mapping = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit("bad --map '%s': use Name=server" % pair)
        name, server = pair.split("=", 1)
        if name not in KNOWN:
            raise SystemExit("unknown service '%s': use one of %s" % (name, ", ".join(KNOWN)))
        if not SERVER.match(server):
            raise SystemExit("bad server name '%s': letters, digits, - and _ only" % server)
        mapping[name] = server
    return mapping


def files(vault):
    for rel in TARGETS:
        base = os.path.join(vault, rel)
        if os.path.isfile(base):
            yield base
        elif os.path.isdir(base):
            for folder, _dirs, names in os.walk(base):
                for n in names:
                    if n.endswith((".md", ".json")):
                        yield os.path.join(folder, n)


def retarget_text(text, mapping):
    count = 0
    for name, server in mapping.items():
        old = "mcp__claude_ai_%s__" % name
        count += text.count(old)
        text = text.replace(old, "mcp__%s__" % server)
    return text, count


def run(vault, mapping, write=False):
    """Return {path: replacements}. Writes only when write is True."""
    changed = {}
    for path in files(vault):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new, count = retarget_text(text, mapping)
        if count:
            changed[path] = count
            if write:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--map", action="append", default=[], help="Name=server, for example Linear=linear")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if not args.map:
        raise SystemExit("give at least one --map Name=server")
    changed = run(os.path.abspath(args.vault), parse_map(args.map), args.write)
    for path, count in sorted(changed.items()):
        print("%s: %d names" % (os.path.relpath(path, args.vault), count))
    total = sum(changed.values())
    if args.write:
        print("Rewrote %d tool names in %d files. Run tools/doctor.py to check." % (total, len(changed)))
    else:
        print("%d tool names in %d files would change. Add --write to apply." % (total, len(changed)))


if __name__ == "__main__":
    main()
