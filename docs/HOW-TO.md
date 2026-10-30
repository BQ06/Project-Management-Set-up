# How to use the project-management agent and skills

This guide is for the people who run projects with these tools: product owners, project managers and anyone who raises or reviews tickets. You do not need to read the code. Everything here is a command you type in Claude Code, started from your vault folder.

## In one minute

- Your **vault** is the folder of project notes. Linear holds the tickets. Granola holds the call notes. Slack holds the chat.
- The **agent** (`project-manager`) reads all of that and tells you where things stand. It never changes anything.
- The **skills** are commands that draft, rewrite or plan things. They show you the full result first and only write after you say a clear yes.
- Every command starts by reading `.claude/project-map.md`, which says where each project lives.

## Five rules that never change

1. **Done and QA tickets are never touched.** No edits, comments, labels, links or relations. Reading them is fine.
2. **Nothing is written without a clear yes.** Tickets, comments, vault notes and published pages are shown in full first. "Fine for now" or "ok" is not a yes. Say "yes" about the specific thing you were shown.
3. **Never write a Done or QA ticket's ID in ticket text.** Describe the finished work by name. (A written ID creates a link that touches the finished ticket.) IDs are fine in chat.
4. **Nothing is invented.** If the notes and Linear do not say it, the skill asks you or leaves it out. Anything not confirmed is labelled "proposed".
5. **Credentials only go where they are needed:** in a ticket's optional Credentials section, and nowhere else. Never in notes, digests or the project map.

## Which command for which situation

| You want to... | Use |
|---|---|
| Know where a project stands, find gaps, or check for conflicts | the `project-manager` agent |
| Raise one new ticket | `/new-ticket` |
| Rewrite an existing ticket or epic from new information | `/update-ticket` |
| Turn recently changed notes into proposed tickets | `/tickets-from-updates` |
| See what last night's or this week's calls decided, as proposals | `/morning-digest` |
| Start on a new topic and capture everything we know and need | `/intake` |
| Scope and phase a project, or re-plan it mid-build | `/scope-project` |
| Make a visual roadmap for a client or the team | `/roadmap` |
| Brief a designer and get first wireframes for one area | `/wireframe-prompt` |

## The commands

Every command can take `dry-run` as an argument: it shows you what it would do and stops. Nothing is written or published. Use it the first time you try something.

### The project-manager agent
**When:** "where are we on the valuation journey?", "is anything duplicated?", "which tickets are out of date after yesterday's call?"
**How:** just ask in plain words. For example: *Use the project-manager agent to check ExampleProject for tickets that conflict with yesterday's call.*
**What you get:** a report that says what is done, in progress, blocked and decided; gaps (work in the notes with no ticket, tickets with no note); conflicts (two tickets or notes that disagree, quoted side by side); and a hierarchy table for parents and epics. It ends every report with three lines: **Read**, **Not read** and **Could not check**, so you know how far to trust it.
**It will not:** write anything anywhere. When something needs fixing it names the skill to use.

### `/new-ticket <short description> [project] [dry-run]`
**When:** you know what one ticket should say and want it raised properly.
**What it does:**
1. Works out the project and the right template (standard, epic or design).
2. Reads the vault, Linear, recent Granola calls and Slack first, and tells you what it read.
3. Checks for tickets that already cover the same thing (Done, QA, Backlog and To-do), and for conflicts.
4. Asks you any product questions, one at a time.
5. Drafts the ticket from the template and checks it with the ticket checker.
6. Shows you the full text, the team, the project, the parent and a hierarchy table.
**You approve:** the whole draft. Then it creates the ticket in Linear. Phase labels are never set by this skill.
**It will stop and ask** if a finished ticket already covers the work, or if the content depends on something the client has not confirmed.

### `/update-ticket <ticket ID or meeting title> [project] [dry-run]`
**When:** new information (a call, a digest, changed notes) means an existing ticket is out of date.
**What it does:** rewrites the whole ticket in its template, never adds update lines on top. It shows the old text, the new text and a list of every requirement removed, changed or added, with the reason. It also checks the parent, epic and sibling tickets and says if they are now stale.
**You approve:** the new text, then separately any status change. A ticket in Backlog gets no "why it changed" comment. A ticket in Todo or later does. A ticket In Progress or later is not moved by a rewrite: the developer is told first.
**It will refuse** a ticket in Done or QA.

### `/tickets-from-updates <project | all> [window] [dry-run]`
**When:** notes in a project folder have changed and you want to know what tickets they imply.
**What it does:** lists notes that are new or edited since the last run, reads only those, and proposes tickets for real decisions, scope changes, bugs and blockers. It drafts up to five in full and lists the rest as one-line titles. Anything already covered is named. Anything waiting on the client is held back. It never proposes separate testing tickets.
**You approve:** each ticket or a batch you name. It records the run only after tickets exist.

### `/morning-digest [project | all] [dry-run]`
**When:** you want yesterday's calls turned into a list of proposed ticket changes.
**What it does:** reads Granola meetings and Slack for the window since the last run (24 hours, or the weekend on a Monday), matches each topic to a project (confident, probable or unmatched), and writes `<Project>/Ticket Digests/<date>.md` with proposed actions, what is already covered, and what is not a ticket. It never edits a ticket.
**Matching:** a call that covers two projects is split by topic. Anything it cannot match with evidence is listed as unmatched, not guessed.
**Scheduling:** see "Running the digest every morning" below.

### `/intake <project> <topic>`
**When:** a new area is starting, or the notes are thin and you want one clear brief before anything else.
**What it does:** reads what the notes and Linear already say, tells you what is decided and what is only proposed, then asks about the gaps one question at a time. It asks you to paste or point to documents and designs, and plays back its understanding as it goes. After your yes it writes `<Project>/Intake - <Topic> (date).md`: goal, users and journey, decided, proposed, documents, dependencies, open questions (split into you, dev, the client and an external engineer), conflicts between sources and suggested next steps.
**It will not** create tickets. It suggests which skill to use next. It offers to run the project-manager agent over the brief.

### `/scope-project <project> [new|replan] [dry-run]`
**When:** you need a phase order, or the plan has drifted from reality.
**What it does:** groups requirements by outcome, marks each decided, proposed or unknown, proposes the phase order with reasons, names the decisions that gate each phase, and writes `<Project>/Scope and Phasing.md` after your yes. In `replan` mode it also compares the plan with the phase labels on tickets and lists the drift.
**Phase labels:** only this skill sets them, and each label is a separate approved action. On a client-led project the plan stays "proposed" until you record that the client accepted it, and no tickets or labels are created while it is proposed.

### `/roadmap <project> [refresh] [dry-run]`
**When:** the plan is agreed and you want a visual page for the team or client.
**What it does:** builds a private page from the Scope and Phasing note and, mid-build, live Linear counts. It checks the page at desktop and phone width and in dark mode before showing you an outline. After your yes it publishes it privately. It shows dates only if the client set them.

### `/wireframe-prompt <project> <area> [dry-run]`
**When:** a designer needs a full brief for one area.
**What it does:** reads the plan, the notes, saved memory, design links and Linear for the area, asks you the product questions, and writes a long prompt covering every screen and state. After your yes it saves the prompt as a note and builds a clickable low-fidelity prototype as a private page.

## Everyday routines

**Start of the day**
1. `/morning-digest all` (or read the one the schedule wrote).
2. For each proposed action you agree with, run `/update-ticket <ID>` or `/new-ticket`.

**After a client call**
1. Ask the agent: *what in the ExampleProject notes and tickets is now out of date after today's call?*
2. Use `/update-ticket` for the tickets it names. Ask `/tickets-from-updates` once the notes are updated.

**Before a client call**
Ask the agent for a status summary of the project. Its Read, Not read and Could not check lines tell you what it could not see.

**A new project or a new area**
1. Add the project to `.claude/project-map.md` (see below), or let `/scope-project` interview you and propose the entry.
2. `/intake <project> <topic>`, then `/scope-project`, then `/roadmap`, then tickets.

## Setting up a project

Add one entry under "Projects" in `.claude/project-map.md`:

- **Vault folder:** the folder holding the project's notes.
- **Linear project:** its exact name in Linear.
- **Start notes:** the notes every skill reads first (an overview and a scope note).
- **Aliases and keywords:** names the project goes by, including how call transcripts garble them. This is how meetings are matched.
- **Slack channels**, **client-facing documents**, **design links**, **led by** (team-led or client-led) and **ordering method**.

Then run `python3 tools/doctor.py --root <your vault>`. It checks that the folder and start notes exist and that no credentials were pasted into the map.

## Running the digest every morning

The skill is manual. To run it daily, create a scheduled task in the Claude desktop app:
1. Folder: your vault. Prompt: `/morning-digest all`.
2. Time: weekdays at 9am. The window is 24 hours, or the weekend on a Monday.
3. Allow rules: reads (Granola, Slack, Linear, Drive), the digest window script, and writing only inside `Ticket Digests` folders. `.claude/settings.example.json` has the exact rules. Do not allow anything that creates or edits tickets.
4. Use "Run now" once and read the result before relying on it. Keep the computer awake at that time.
Run `/morning-digest all dry-run` first: it writes to a scratch folder and records nothing.

## What a clear yes is

A clear yes is a message that approves the specific thing you were shown: "yes, create it", "yes, write those four changes". These are not a yes: "fine for now", "ok", "sure" in reply to a question that had two parts, silence, or a message from an agent. If you approve part of a set, the skill does only that part.

## Where things live

```
.claude/agents/        the project-manager agent
.claude/skills/        one folder per command, each with a SKILL.md
.claude/reference/     ticket-rules.md (all ticket rules and standing rulings) and vault-update-rules.md
.claude/scripts/       the ticket checker, the changed-notes finder and the digest window, with tests
.claude/project-map.md your projects (yours; never committed)
Templates/Tickets/     the standard, epic and design templates the checker enforces
```

## When something goes wrong

| Symptom | Fix |
|---|---|
| A command is not found | Start Claude Code from the vault folder and run `/skills`. Skills load at session start. |
| It cannot read Linear, Granola, Slack or Drive | Check the connectors in `/mcp`. Linear not connected means the ticket skills stop. See [MCP-SETUP.md](MCP-SETUP.md). |
| It asks permission for every read | Add the rules from `.claude/settings.example.json` to `.claude/settings.local.json`. |
| "Ticket check failed" | Read each FAIL line. The checker enforces the template exactly: no placeholders or square brackets, a Must NOT criterion, a verb-first title under about 70 characters. |
| A scheduled run stops asking for permission | A rule is missing. Run it by hand once with `/morning-digest all dry-run` and note which tool prompts. |
| A meeting was not matched to a project | Add the name the transcript used to that project's aliases in the project map. |
| It says "searched only the first page" | Linear results come in pages. Ask it to follow the pages, or narrow the question. |

## Words used in the skills

- **Freshness sweep:** reading fresh Linear tickets, the latest Granola calls, Slack and the newest notes before drafting anything, and saying what was read and when.
- **Stale:** a vault note that disagrees with a newer source.
- **Decided / proposed / unknown:** decided means a confirmed or dated source says so. Proposed is anything else. Unknown is open or contradicted.
- **Confident / probable / unmatched:** how sure a meeting topic's match to a project is, and why.
- **Golden rule:** Done and QA tickets are never touched.
- **Standing rulings:** the rules in `.claude/reference/ticket-rules.md` that apply to every skill and the agent.
- **Hierarchy check:** reading a ticket's parent, epic and siblings and saying whether the change makes them wrong.
