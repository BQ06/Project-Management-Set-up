# Changelog

## 0.1.2 - 30 Oct 2026

- `docs/OBSIDIAN-MCP.md`: connecting Claude Desktop to an Obsidian vault with the Local REST API plugin, for macOS and Windows, with a safety section. Optional: the skills do not need it.

## 0.1.1 - 30 Oct 2026

- `docs/OBSIDIAN-SETUP.md`: setting up an Obsidian vault, installing the package and writing notes the skills can use.
- `starter/ExampleProject/`: three starter notes, created by `install.py --with-starter`.
- README: a "Where everything is" table, including why the skills are in the hidden `.claude` folder.

## 0.1.0 - 30 Oct 2026

First packaged release.

- The `project-manager` agent and eight skills: `/new-ticket`, `/update-ticket`, `/tickets-from-updates`, `/morning-digest`, `/intake`, `/scope-project`, `/roadmap`, `/wireframe-prompt`.
- Hardened rules: Done and QA ticket IDs are never written into ticket text; standing rulings (client confirmation, live content, no testing tickets, no change comments on Backlog rewrites, cleanup scope, show the full text, sweep first); evidence and paging rules; every agent report ends with Read, Not read and Could not check.
- The ticket checker now lists every ticket ID in a draft so each can be checked for Done or QA status.
- Tooling: installer, setup checker, skills linter, secret scanner, vault exporter and MCP name rewriter, with tests and a GitHub Actions workflow.
- `pm-config.json`: the ticket checker's team keys and design title tag are configurable. Defaults are unchanged.
- The exporter can rewrite team-specific wording to generic wording using a private map, and refuses to copy if a private term survives.
- Documentation: README, a how-to guide, connector setup and a guide to adapting the package.
