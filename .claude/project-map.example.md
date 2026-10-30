# Project map

Every skill and the project-manager agent read this file first. To add a project, add one entry under "Projects". Nothing else changes.

Copy this file to `.claude/project-map.md` in your vault and edit it. Never put credentials, keys or passwords in it. The real file stays in your vault and is never committed to this repo.

Vault root is the folder that contains `.claude/`. Linear tool names are in `.claude/reference/ticket-rules.md`.

## Routing that applies to every project
- Build work goes to the Dev Team (identifier DEV). UX design work goes to the Design Team (DES).
- Epics are parent issues. Child tickets are sub-issues of the epic.
- A design ticket is titled `[DESIGN] - <what>`, carries the label `Design` and the phase label of the dev ticket it pairs with, is assigned to <design team lead>, and sits under the dev ticket it pairs with.
- Status when raised: Todo only if a developer can start immediately, unblocked. A ticket with an outstanding question or a client blocker is raised in Backlog. Say which in the draft summary.
- Where a developer's own tickets overlap tickets the PM raised, the developer's tickets are correct and the PM's give way.
- Bundled tickets: flag them and explain why. Dev does the technical split.
- Templates live in `Templates/Tickets/standard.md`, `epic.md` and `design.md`.

## Context sources (all read-only)
Use them in this order, and only as much as the task needs:
1. **The vault notes** for the project.
2. **Linear** for what is built, ticketed and in what state.
3. **Granola meetings** for the latest calls. The vault is often stale: decisions are made on calls and the notes are updated later.
4. **Slack** for context and recent updates: the project's channels listed below. Slack is informal: a message is context, not a decision, unless it states one plainly. A channel shared by two projects only gives a probable match for a message that names neither.
5. **Client-facing documents in Google Drive**, listed per project below.
6. **Claude artifacts** the PM published (wireframes, roadmaps), found with the Artifact tool.
Where sources disagree, say so; never quietly pick one.

### Freshness sweep (before proposing a plan, drafting a ticket, rewriting a ticket or writing a prompt)
Do this first, and say at the top of your answer what you read and as of when:
1. **Linear, fresh.** List the project's tickets with `updatedAt`. Read in full every ticket updated in the last 14 days and every ticket the work touches.
2. **Granola, latest calls.** `list_meetings` for the last 30 days. Read every meeting whose title or content concerns the project (use the aliases below), newest first.
3. **Slack,** the project's channels, newest first, for the last few weeks.
4. **Vault notes,** newest first, and the client-facing documents.
5. **Stale check.** List where a vault note disagrees with a newer source. Treat the newer source as the better evidence and say which note is stale.
A decision made on a call is `decided` only if the notes of that call say it plainly; otherwise it is `proposed`.

## Design links (UI and UX references)
Each project entry has a `Design links` list the PM provides. Skills use them as the reference dev builds against, and never invent a link. When a ticket or prompt needs a design reference and none is listed, ask the PM.

## External engineers and parties (the PM chases these; their answers are dependencies, not Open questions)
- **ExampleProject:** <name> (<company>), the client's back-end engineer. Reached through <client contact>.

## Credential notes (read only when a ticket needs credentials; never copy into digests, prompts or other notes)
- `ExampleProject/Staging Credentials.md`
- Any other note whose name contains: credential, password, login, api key, secret, token.
- Change detection skips these notes, so they never drive ticket proposals.

## Projects

### ExampleProject
- Vault folder: `ExampleProject`
- Linear project: `example project`
- Start notes: `Overview.md`, `Scope Boundaries.md`
- Aliases and keywords (used to match meetings): ExampleProject, Example Project; transcription garbles seen: "Example Prodject"
- Phase labels: `Phase 1` to `Phase 5` (scoping and roadmap skills only)
- Plan notes: `Scope and Phasing.md`
- Led by: team-led, or client-led (a client-led plan stays "proposed" until the client's acceptance is recorded)
- Ordering method: build order, MoSCoW or client priority
- Slack channels: `#example-project` (<channel ID>)
- Roadmap URL: none yet
- Client-facing roadmap (Drive): <title and file ID, or none>
- Design links: none provided yet

## Digest folders (written by the morning job, skipped by change detection)
- `<project folder>/Ticket Digests/`
