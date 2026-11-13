# CLAUDE.md

This folder is the source of truth: an Obsidian vault of project knowledge, plus the project-management setup in `.claude/`. It is not a codebase.

Copy this file to `CLAUDE.md` in your vault root and edit the project list.

## Projects
- List your projects here. Which Linear project, labels and start notes each uses: @.claude/project-map.md
- Each project folder may have its own `CLAUDE.md`. Read it for that project's conventions.

## Templates
- `Templates/Tickets/standard.md`, `Templates/Tickets/epic.md` and `Templates/Tickets/design.md` (UX design tickets for the Design Team) are canonical. They win over any older template pointer in a project folder.

## Rules
- **Golden rule: tickets in Done or QA are never touched.** No skill or agent may edit, comment on, relabel, re-prioritise, re-status, reparent, link or relate (duplicate, blocks, related-to, parent or sub-issue) a Linear ticket whose status is Done or QA. Reading them is fine. Check the status with `get_issue` before every write and stop if it is Done or QA. Setting a link or relation between an open ticket and a Done or QA one counts as touching it. Never write a Done or QA ticket's ID in the text of any ticket description or comment either: in this workspace a written ID creates a related link and bumps the finished ticket. Describe the finished work by name instead. IDs may be named in chat reports to the PM. To retire an open ticket that is covered by finished work, close it as Canceled with a comment on the open ticket that describes the covering work by name, and never set a duplicate link to the finished one.
- Tickets and epics follow the rules in @.claude/reference/ticket-rules.md.
- Vault updates follow @.claude/reference/vault-update-rules.md.
- Never create, edit or comment on a Linear ticket without showing the final draft and getting a clear yes.
- Vault changes are shown first (diff or summary) and written only after a clear yes.
- Tickets describe the user and client journey and the logic. Leave technical detail to dev.
- Credentials and keys may go in a ticket, only in the template's optional Credentials section and only when the ticket needs them. Never copy them into other notes, digests or prompts.
- Only the scoping and roadmap skills set phase labels, except that a design ticket copies the phase label of the dev ticket it pairs with.
- Do not guess. If the notes and Linear do not say it, ask or leave it out.

## Commands
- `/new-ticket`: draft and create one ticket from a short description.
- `/update-ticket`: rewrite an existing ticket or epic from new information, with a before/after diff.
- `/tickets-from-updates`: turn changed notes in a project into proposed tickets.
- Agent `project-manager`: read-only status, gap and conflict checks.
- `/scope-project`: scope and phase a project (new or re-plan) and write `<Project>/Scope and Phasing.md` after approval. Only this skill sets phase labels.
- `/roadmap`: build or refresh the project's visual roadmap artifact (private).
- `/wireframe-prompt`: write a wireframing prompt for one area, then build the wireframes after approval.
- `/board-refresh`: the daily and on-demand board review. It checks blockers, status and wording against live Linear, walks the app as a user, reads the latest calls and writes `<Project>/Ticket Digests/`. Proposals only. `/morning-digest` is its old name and still works.
- `/intake`: interview the PM about a project or topic, collect documents and context, and write `<Project>/Intake - <Topic> (date).md` after approval. It never touches tickets.
