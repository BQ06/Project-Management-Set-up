#!/usr/bin/env python3
"""Install the agents and skills into a vault (an Obsidian folder that holds your project notes).

Usage: install.py VAULT_PATH [--force]
Copies the managed files into the vault. An existing file is left alone unless --force is given.
project-map.md, settings.local.json and CLAUDE.md are created from the examples only if missing,
and are never overwritten, even with --force: they hold your own project data.
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def install(vault, force=False, repo=REPO):
    """Return (copied, skipped, created)."""
    if not os.path.isdir(vault):
        raise SystemExit("vault folder not found: %s" % vault)
    copied, skipped, created = [], [], []
    for rel, full in sorted(common.collect(repo).items()):
        dest = os.path.join(vault, rel)
        if os.path.exists(dest) and not force:
            skipped.append(rel)
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(full, dest)
        copied.append(rel)
    for target, example in common.EXAMPLES.items():
        dest = os.path.join(vault, target)
        src = os.path.join(repo, example)
        if os.path.exists(dest) or not os.path.exists(src):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(src, dest)
        created.append(target)
    return copied, skipped, created


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--force", action="store_true", help="overwrite existing agent, skill, rule, script and template files")
    args = ap.parse_args()
    copied, skipped, created = install(os.path.abspath(args.vault), args.force)
    print("Copied %d files, left %d existing files alone." % (len(copied), len(skipped)))
    for rel in created:
        print("Created %s from the example. Edit it for your projects." % rel)
    print("Next: python3 tools/doctor.py --root %s" % args.vault)


if __name__ == "__main__":
    main()
