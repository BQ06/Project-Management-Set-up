# Vault update rules

The vault is the living knowledge base. Keep it current with new project-level context: decisions, scope changes, superseded plans, open questions. Always show the change first, then write only after a clear yes.

## Show before writing
- Small edits: show a diff.
- Larger changes or new notes: show a short summary of what will change and where.
- Write only after the user confirms. With `dry-run`, never write.

## Follow what is already there
- Use Obsidian wikilinks (`[[Note Name]]`). Most notes start with `Parent: [[Overview]]` and end with a related-notes list.
- New notes open with frontmatter: `tags` (including the project tag), `date`, and where relevant `status`, `attendees`, `source`.
- Filenames follow the project's pattern, e.g. `Meeting Notes YYYY-MM-DD <Topic>.md`, `Epic - <Name>.md`.
- Use plain hyphens and colons, not em dashes.
- Record the source of meeting notes and say plainly when only a summary was available.

## Keeping notes honest
- Before stating something is current, check the newest dated notes.
- When a decision overrides an older note, mark the older note "superseded" and link the newer one. Do not delete or silently rewrite history.
- If notes contradict each other, point it out. Do not quietly pick a version.
- Do not copy anything from the credential notes listed in `.claude/project-map.md` into other vault notes or digests. Credentials go only in a ticket's optional Credentials section.
- Only write project-level context. Do not paste logs or raw technical output.

## Where Claude may create files
- Digests: `<project folder>/Ticket Digests/YYYY-MM-DD.md`. Proposals only.
- Everything else: only what the user has approved in that message.
