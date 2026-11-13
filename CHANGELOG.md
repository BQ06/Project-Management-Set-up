# Changelog

## 0.2.0 - 13 Nov 2026

- New `/board-refresh` skill: the daily and on-demand board review. It checks blockers, status and wording against live Linear, walks the app as a user, reads the latest calls and writes a dated digest. Proposals only. `/morning-digest` is now an alias for it.
- New `board-sweep.md`: the Todo rule (a ticket is Todo only when a developer can finish it with no blockers and it is definitely needed with final requirements) and board checks A to J. The `project-manager` agent and `/board-refresh` both use it.
- New session check script (`session_check.py`), with tests: it lists the projects whose board review is due.
- Set-up questions in `ticket-rules.md`: `/new-ticket`, `/update-ticket` and `/tickets-from-updates` ask for title, status, priority, labels, assignee and parent before drafting. The questions are optional and a blank answer is never guessed. If the PM asks for Todo against the Todo rule, the skill warns once, then follows the PM. After every save the skills read the ticket back and report what the tracker returned.
- Design tickets default to the Linear "Design Template Example"; the long-form design template stays available on request.
- The agent and skills say when Granola only covers the last 30 days, and state plainly when a later source corrects an earlier answer.
- Tooling: the exporter now copies the legacy templates the ticket checker needs, and the linter knows the `AskUserQuestion` tool. `/board-refresh` and `/morning-digest` now pass the linter.
- Tests: 120 script tests and 60 tooling tests.

## 0.1.3 - 3 Nov 2026

- New ownership rule in `ticket-rules.md`: only tickets created by the PM may be edited, commented on, re-statused, linked or cancelled. Every skill and the `project-manager` agent read `createdBy` first, leave other people's tickets alone, and report conflicts to the PM, whose own ticket gives way.
- `/new-ticket`, `/update-ticket`, `/tickets-from-updates` and `/scope-project` carry the rule. The agent shows each ticket's creator in its tables and marks other people's tickets "flag only".

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
