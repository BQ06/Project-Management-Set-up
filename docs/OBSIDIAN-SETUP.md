# Setting up your Obsidian vault and using it with the agent and skills

This guide is for someone starting from nothing. By the end you will have a vault of project notes, the agent and skills installed in it, and a daily routine.

## What the vault is, and why Obsidian

Your **vault** is a folder of plain Markdown notes, one subfolder per project. It holds what you know about each project: what it is, what was decided, what is still open.

**Obsidian** is a free app that opens that folder as a notebook: you read and edit notes, and link them to each other with `[[Note Name]]`. Obsidian does not store anything of its own. The notes are ordinary files, so **Claude Code reads and writes exactly the same files**. You can use Obsidian to read, search and edit, and Claude Code (run from the vault folder) to draft, check and update. Both see the same notes.

This keeps the notes the source of truth. Linear holds the tickets, but the reasons behind them live here.

## Step 1: create the vault

1. Install Obsidian from https://obsidian.md and open it.
2. Create a new vault, or choose **Open folder as vault** and pick a folder you already have. Call it something like `Projects`.
3. Obsidian does not show folders that start with a dot, so the `.claude` folder the next step creates stays out of the way. You can see it in your file manager or editor.

## Step 2: install the agent and skills into it

From the repo folder, in a terminal:

```bash
python3 tools/install.py /path/to/your/vault --with-starter
python3 tools/doctor.py --root /path/to/your/vault
```

This copies the agent, skills, rules, scripts and templates into the vault's `.claude` and `Templates` folders, and creates a starter project called `ExampleProject` with three notes. It never overwrites anything you already have. `doctor` tells you what still needs doing.

## Step 3: the layout

```
Projects/                      your vault
  .claude/                     agent, skills, rules, scripts (hidden in Obsidian)
  Templates/Tickets/           the three ticket templates
  CLAUDE.md                    instructions Claude reads when you start it here
  ExampleProject/              one folder per project
    Overview.md                start note: what the project is
    Scope Boundaries.md        start note: what is in and what is later
    Open Questions.md          what is not answered yet, and who answers it
    Ticket Digests/            written by /morning-digest, one note per day
```

Add a folder for each real project. Keep one rule: **a project's folder name must match the "Vault folder" in `.claude/project-map.md`**. That file is how every skill finds your project, so edit it whenever you add or rename one.

## Step 4: tell the skills about your project

Open `.claude/project-map.md` (in your editor, or any text app) and replace the `ExampleProject` entry with your own: the vault folder, the exact Linear project name, the start notes, the names the project goes by in meetings, and your Slack channels. [HOW-TO.md](HOW-TO.md) explains each line. Then run `doctor` again. If you use different Linear team keys, set them in `.claude/pm-config.json` (see [ADAPTING.md](ADAPTING.md)).

## How to write notes the skills can use

The skills read your notes, so a few habits make them far more accurate.

- **Start every project with an Overview and a Scope Boundaries note.** Name them in the project map as start notes. Skills read these first.
- **Date things.** Put the newest status at the top of the Overview with its date and where it came from ("call, 30 Oct" or "Linear"). The skills prefer the newest dated source, and say which notes are stale.
- **Mark what is decided and what is only proposed.** A decision is decided if a dated note says so plainly. Otherwise write "proposed".
- **Use frontmatter** at the top of a note:

  ```
  ---
  tags: [yourproject, meeting]
  date: 2026-10-30
  status: draft
  source: call notes
  ---
  ```
- **Link notes.** Start with `Parent: [[Overview]]` and end with a "Related notes" list of `[[links]]`.
- **Name files the same way each time:** `Meeting Notes 2026-10-30 Weekly Catchup.md`, `Epic - Checkout.md`, `Draft Tickets - Checkout (30 Oct).md`.
- **Use plain hyphens and colons**, not long dashes.
- **Say where a meeting note came from.** If only a summary was available and not the full transcript, write that.
- **Never put credentials in an ordinary note.** If a project needs them, keep them in one note whose name contains "credential" (for example `Staging Credentials.md`), list it in the project map's credential section, and put them in a ticket's Credentials section only when a ticket needs them. The skills skip those notes.

## A daily routine

1. **Morning:** read what changed. Run `/morning-digest all` (or open the day's note in `Ticket Digests/`), then act on the proposals with `/update-ticket` or `/new-ticket`.
2. **During the day:** keep notes in Obsidian as things happen: a short dated line under "Current status" is enough.
3. **After a call:** add or paste the call notes into a dated note, then ask the agent what is now out of date, and fix the tickets it names.
4. **Starting something new:** run `/intake <project> <topic>` to capture it properly, then `/scope-project` and `/new-ticket`.
5. **Once a week:** ask the agent for a status check and a gap and conflict check on each project.

Run Claude Code from the vault folder (`cd` into it first), so it can see `.claude`, `CLAUDE.md` and your notes. Skills load when a session starts, so run `/skills` to confirm they are there.

## Working in both at once

Obsidian and Claude Code can be open on the same vault at the same time. A note Claude Code writes usually appears in Obsidian straight away. Review it there. Every skill that writes a note shows you the change first and waits for your yes, so nothing lands in the vault that you have not approved.

If you edit a note while a skill is running, finish before you ask it to write, so it does not draft against an old version.

## Optional: let Claude Desktop reach the vault through Obsidian

The skills do not need this. If you also want Claude Desktop to search and create notes in the vault, see [OBSIDIAN-MCP.md](OBSIDIAN-MCP.md).

## Keeping it safe

- **Back up the vault.** It is plain files, so Time Machine, a cloud folder or a private Git repo all work.
- **If you put the vault in Git, keep it private and ignore your credential notes.** The vault holds client information. The repo this package comes from does not contain any vault notes, and you should keep it that way: do not copy your notes into it.
- Do not edit `.claude/state/`. It records when the last digest ran.

## First-day checklist

- [ ] Obsidian installed, vault opened.
- [ ] `install.py --with-starter` run; `doctor.py` shows no failures.
- [ ] Linear, Granola, Slack and Google Drive connected ([MCP-SETUP.md](MCP-SETUP.md)).
- [ ] Your real project added to `.claude/project-map.md` and its folder created, with an Overview and a Scope Boundaries note.
- [ ] Claude Code started in the vault; `/skills` shows the commands.
- [ ] `/new-ticket <a small real change> dry-run` tried, and the draft read.
- [ ] `/morning-digest all dry-run` tried.
