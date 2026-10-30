# Adapting this to your own team and projects

This package was built around one team's way of working. It is meant to be adapted. This page lists what to change, and what not to.

## Do not change (the safety rules)

- Nothing is written without a clear yes.
- Tickets in Done or QA are never touched.
- Done and QA ticket IDs are never written into ticket text.
- Nothing is called built, existing or decided without a source.
- Credentials never go in the project map, notes or digests.

These are what make the skills safe to trust. The linter and tests protect them.

## Change these to fit your setup

### 1. Your projects: `.claude/project-map.md`
Copy the example and describe your projects. Every skill reads this file first. It holds your vault folders, Linear project names, start notes, Slack channels, meeting keywords and how each project is led. It also holds the routing rules: which Linear team gets build work and which gets design work, and who your design team lead is. Edit those lines to match your teams.

### 2. Your Linear team keys: `.claude/pm-config.json`
The ticket checker assumes build tickets go to a team with the key `DEV` and design tickets to `DES`, and that design titles start with `[DESIGN] - `. If your keys differ, set them:

```json
{ "build_team": "ENG", "design_team": "UX", "design_tag": "[Design] - " }
```

The skills' prose still says "DEV" and "DES" in a few places as examples. They read your project map for the real routing, but a search-and-replace of the two keys in `.claude/skills/` and `.claude/reference/` keeps things tidy.

### 3. Your Linear workflow
The rules assume these statuses: Backlog, Todo, In Progress, QA, Done, Canceled, Blocked. The golden rule protects **Done** and **QA**. If your workflow has no QA status, or calls it "In Review", search for `QA` in `.claude/reference/ticket-rules.md`, `CLAUDE.md` and the skills, and change it to the status that means "finished or being verified". Keep the protected set as large, not smaller.

Labels: the package expects a `Design` label and phase labels named `Phase 1`, `Phase 2` and so on, set only by `/scope-project`. If your labels differ, say so in the project map and in `ticket-rules.md`.

### 4. Your house rules: the "Standing rulings" in `ticket-rules.md`
Those rules came from one product owner's corrections over time. They are a starting set. Keep the ones that suit you and delete or edit the rest. Examples that are preferences, not safety: no separate testing tickets, no change comments on Backlog rewrites, how live-site wording is approved, holding tickets that wait on a client answer. If you delete one, delete it in the skills that mention it too (search for `Standing rulings`).

### 5. Your company name
`ticket-rules.md` says never to write the company's own name in a ticket (say "we"). If you do want it, remove that line.

### 6. Your templates: `Templates/Tickets/`
The three templates are enforced by `check_ticket.py`: it reads their headings and checks every draft against them. To change a template, edit the file in `Templates/Tickets/` and run the tests. A heading you add becomes required.

### 7. Your connectors
See [MCP-SETUP.md](MCP-SETUP.md). If you do not use claude.ai connectors, rewrite the tool names with `tools/retarget_mcp.py`.

## After any change

```bash
python3 tools/lint_skills.py                              # skills and agents still valid
python3 -m unittest discover -s .claude/scripts -p "test_*.py"
python3 tools/doctor.py --root /path/to/your/vault        # your setup is complete
```

If you keep your own copy of this repo, run the same commands in it before you push. `tools/scan_secrets.py` must also pass: it stops credentials, personal file paths, email addresses and real IDs reaching GitHub.

## Keeping your private details out of a shared copy

If you later share your adapted version, put a private `.claude/export-map.json` in your vault (it is never exported) with `replace` pairs that swap your own names for generic wording and a `deny` list of names that must not appear. `tools/export_from_vault.py` applies the swaps and refuses to copy if any denied name survives. `tools/scan_secrets.py --deny-map <that file>` checks a repo against the same list.
