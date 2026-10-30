#!/usr/bin/env python3
"""Lint the agents and skills under .claude/ so a broken one is caught before it ships.

Usage: lint_skills.py [--root PATH]
Checks every .claude/skills/*/SKILL.md and .claude/agents/*.md. Prints one line per problem
(ERROR or WARN). Exits 1 if there is any ERROR, 0 otherwise.
"""
import argparse
import os
import re
import sys

BUILTIN_TOOLS = {
    "Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit", "Bash",
    "WebFetch", "WebSearch", "Agent", "Task", "Skill", "TodoWrite",
}
# Verbs that change something outside the session. A skill may not pre-approve these:
# the permission prompt is the second gate before any write.
WRITE_VERBS = {
    "save", "create", "delete", "update", "send", "share", "trash", "add", "apply",
    "label", "unlabel", "mark", "merge", "submit", "retire", "restore", "reply",
    "forward", "remove", "publish",
}
EDIT_TOOLS_FOR_AGENTS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "Bash"}
PATH_REF = re.compile(r"(\.claude/[A-Za-z0-9_./-]+|Templates/[A-Za-z0-9_./-]+)")
GENERATED = (".claude/state",)
# Files a vault owns. A repo ships an example instead, so the example counts as present.
OPTIONAL = {
    ".claude/project-map.md": ".claude/project-map.example.md",
    ".claude/settings.local.json": ".claude/settings.example.json",
}


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def tokens(value):
    """Split an allowed-tools or tools value on spaces or commas, but not inside brackets."""
    out, cur, depth = [], "", 0
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch in " ,\t" and depth == 0:
            if cur:
                out.append(cur)
                cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def check_tool(tok, owner):
    """Return a list of (level, message) for one tool entry."""
    found = []
    name = tok.split("(", 1)[0]
    has_path = "(" in tok
    if name.startswith("mcp__"):
        parts = name.rsplit("__", 1)
        if len(parts) != 2 or not parts[0].startswith("mcp__") or "__" not in name[5:]:
            found.append(("ERROR", "%s: '%s' is not a valid mcp__server__tool name" % (owner, tok)))
        else:
            verb = parts[1].split("_")[0]
            if verb in WRITE_VERBS:
                found.append(("ERROR", "%s: '%s' changes something outside the session and must not be pre-approved" % (owner, tok)))
        return found
    if name not in BUILTIN_TOOLS:
        found.append(("ERROR", "%s: unknown tool '%s'" % (owner, name)))
        return found
    if name in ("Write", "NotebookEdit", "Glob") and has_path:
        found.append(("ERROR", "%s: '%s' never matches. Use Edit(path) for file writes" % (owner, tok)))
    return found


def check_references(text, root, owner):
    found = []
    for m in PATH_REF.finditer(text):
        ref = m.group(1).rstrip(".,;:)`'\"")
        if any(ch in ref for ch in "*<>"):
            continue
        if ref.endswith("/") or ref.startswith(GENERATED):
            continue
        if not os.path.exists(os.path.join(root, ref)) and not os.path.exists(os.path.join(root, OPTIONAL.get(ref, "-"))):
            found.append(("ERROR", "%s: refers to '%s', which does not exist" % (owner, ref)))
    return sorted(set(found))


def lint_skill(path, root):
    owner = os.path.relpath(path, root)
    found = []
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm = frontmatter(text)
    if fm is None:
        return [("ERROR", "%s: no frontmatter" % owner)]
    folder = os.path.basename(os.path.dirname(path))
    if fm.get("name") != folder:
        found.append(("ERROR", "%s: name '%s' does not match its folder '%s'" % (owner, fm.get("name"), folder)))
    if not fm.get("description"):
        found.append(("ERROR", "%s: no description" % owner))
    if fm.get("disable-model-invocation") != "true":
        found.append(("WARN", "%s: not manual-only (disable-model-invocation: true)" % owner))
    if "allowed-tools" not in fm:
        found.append(("ERROR", "%s: no allowed-tools" % owner))
    else:
        for tok in tokens(fm["allowed-tools"]):
            found += check_tool(tok, owner)
    body = text.split("\n---\n", 1)[-1]
    if ".claude/project-map.md" not in body:
        found.append(("ERROR", "%s: does not read .claude/project-map.md" % owner))
    if "ticket-rules.md" in body and "Standing rulings" not in body:
        found.append(("ERROR", "%s: reads ticket-rules.md without naming the Standing rulings" % owner))
    if re.search(r"save_issue|save_comment", body) and "clear yes" not in body:
        found.append(("ERROR", "%s: can write to Linear but never says to wait for a clear yes" % owner))
    found += [(lvl, msg) for lvl, msg in check_references(body, root, owner)]
    return found


def lint_agent(path, root):
    owner = os.path.relpath(path, root)
    found = []
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm = frontmatter(text)
    if fm is None:
        return [("ERROR", "%s: no frontmatter" % owner)]
    stem = os.path.splitext(os.path.basename(path))[0]
    if fm.get("name") != stem:
        found.append(("ERROR", "%s: name '%s' does not match its file '%s'" % (owner, fm.get("name"), stem)))
    if not fm.get("description"):
        found.append(("ERROR", "%s: no description" % owner))
    if "tools" not in fm:
        found.append(("ERROR", "%s: no tools list (an agent without one gets every tool)" % owner))
    else:
        for tok in tokens(fm["tools"]):
            found += check_tool(tok, owner)
            if tok.split("(", 1)[0] in EDIT_TOOLS_FOR_AGENTS:
                found.append(("ERROR", "%s: a read-only agent must not have '%s'" % (owner, tok)))
    body = text.split("\n---\n", 1)[-1]
    found += check_references(body, root, owner)
    return found


def lint(root):
    found = []
    skills = os.path.join(root, ".claude", "skills")
    agents = os.path.join(root, ".claude", "agents")
    if os.path.isdir(skills):
        for name in sorted(os.listdir(skills)):
            p = os.path.join(skills, name, "SKILL.md")
            if os.path.isfile(p):
                found += lint_skill(p, root)
    else:
        found.append(("ERROR", ".claude/skills not found under %s" % root))
    if os.path.isdir(agents):
        for name in sorted(os.listdir(agents)):
            if name.endswith(".md"):
                found += lint_agent(os.path.join(agents, name), root)
    else:
        found.append(("ERROR", ".claude/agents not found under %s" % root))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
    args = ap.parse_args()
    problems = lint(args.root)
    for level, msg in problems:
        print("%s: %s" % (level, msg))
    errors = [p for p in problems if p[0] == "ERROR"]
    if not problems:
        print("OK: skills and agents pass all checks")
    elif not errors:
        print("OK: no errors (%d warnings)" % len(problems))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
