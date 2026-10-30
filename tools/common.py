"""Shared helpers: which files make up the agents-and-skills package."""
import os

# The package: everything the agents and skills need to run, and nothing from the vault.
# (folder, file test) pairs, relative to a vault root or to this repo's root.
MANAGED = [
    (".claude/agents", lambda rel: rel.endswith(".md") and rel.count("/") == 2),
    (".claude/skills", lambda rel: rel.endswith("/SKILL.md") and rel.count("/") == 3),
    (".claude/reference", lambda rel: rel.endswith(".md") and rel.count("/") == 2),
    (".claude/scripts", lambda rel: rel.endswith(".py") and rel.count("/") == 2),
    ("Templates/Tickets", lambda rel: rel.endswith(".md") and rel.count("/") == 2),
]
# Project data that lives only in a vault. The repo ships examples of these instead.
EXAMPLES = {
    ".claude/project-map.md": ".claude/project-map.example.md",
    ".claude/settings.local.json": ".claude/settings.example.json",
    ".claude/pm-config.json": ".claude/pm-config.example.json",
    "CLAUDE.md": "CLAUDE.example.md",
}


def collect(root):
    """Return {relative path: absolute path} for the managed files under root."""
    found = {}
    for folder, wanted in MANAGED:
        base = os.path.join(root, folder)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                if wanted(rel):
                    found[rel] = full
    return found
