---
name: roadmap
description: Build or refresh a project's visual roadmap artifact (phase cards, gates, risks, status) from its Scope and Phasing note and, mid-build, live Linear. Dateless unless the client set dates. Manual use only.
disable-model-invocation: true
argument-hint: "<project> [refresh] [dry-run]"
allowed-tools: Read Grep Glob mcp__claude_ai_Linear__list_issues mcp__claude_ai_Linear__get_issue mcp__claude_ai_Linear__list_projects mcp__claude_ai_Linear__list_issue_labels mcp__claude_ai_Slack__slack_search_channels mcp__claude_ai_Slack__slack_read_channel mcp__claude_ai_Slack__slack_read_thread mcp__claude_ai_Slack__slack_search_public mcp__claude_ai_Google_Drive__search_files mcp__claude_ai_Google_Drive__read_file_content
---

# /roadmap

Arguments: `$ARGUMENTS` = a project name, optionally `refresh` (rebuild the page and republish it to the project's existing roadmap URL), optionally `dry-run`.

Read first: `.claude/project-map.md`, `.claude/reference/ticket-rules.md` (including the Standing rulings), `.claude/reference/vault-update-rules.md`. The roadmap shows the plan; it does not set it. Planning is `/scope-project`. Reading Linear and the existing artifact is fine in dry-run; publishing is not.

## Steps
1. **Find the plan.** Read `<Project>/Scope and Phasing.md`. If it is missing, stop and suggest `/scope-project`. Note its `status` (`proposed` or `committed`), `led-by`, `method` and its change history.
2. **Load the design skill.** Load `artifact-design` with the Skill tool before writing any HTML. Load `dataviz` only if the page will draw charts; simple CSS progress bars do not count.
3. **Gather the data.** Do the freshness sweep in `project-map.md` first, and say in the outline what it found and as of when.
   - New project (no tickets yet): the scope note alone.
   - Mid-build: `list_issues` for the Linear project (title, status, statusType, parentId, labels, limit 250, paging until done). Keep open tickets and Done tickets that carry a phase label. Group them by phase label.
   - Counts per phase: **Done** = completed; **In progress** = started, including QA but not Blocked; **Blocked** = status named Blocked; **Waiting** = backlog or unstarted. Canceled and Duplicate tickets are left out. Tickets that are parents of others are shown as "Epic" lines.
   - Open tickets with no phase label go in a final "Not yet phased" list. A phase with no tickets says "No tickets yet". Where the scope note records label drift, show the ticket in the phase its label says and add a small "label differs from plan" tag.
   - Mark proposed phases as proposed.
4. **Design the page** (one self-contained HTML file, light and dark, readable on a phone, system fonts, no external embeds):
   - Title: `<Project> Build Roadmap`, kept the same on refresh.
   - Header: one sentence on what the plan is for, then stamps that follow the note's `status`: "Committed" or "Proposed". For a client-led plan add "Proposal vN" (N = the number of change-history entries) with the date of the latest entry. Also "As of <date>" and "No dates agreed" unless the scope note carries dates from a client-facing roadmap or the user, in which case show them with the source and "indicative".
   - Phase cards: name, why it sits here and what it depends on (in plain words; never show rule letters like "(b)" or "(d)"), the gate if any, the counts, and the tickets as ID, title and status.
   - Decisions that gate a phase (show "Owner not stated" where the note says so), risks, open questions, future scope (nice to have), planned later, if the note has them.
   - Client-led only: a change history, newest first, with date and reason.
   - Dateless by default. Show dates, as a simple timeline, only where the scope note carries them from a client-facing roadmap or the user; label them indicative and cite the source.
   - Link to the project's design references (from `Design links` in the project map) next to the phases they belong to.
   - Show only what is in the scope note or Linear. No credentials or secrets, no internal chatter, no advice about rotating keys.
5. **Refresh.** Take the URL from `Roadmap URL` in the project map and read the existing artifact first. Use it as a layout reference only: rebuild from the current note and Linear, drop anything that breaks these rules (dates the client did not set, secrets text, outdated phases), and list in chat what you dropped. If the URL is "none yet", ask whether to publish a new page.
6. **Build and check locally.** Write the HTML to the session scratchpad directory. With the `browser-automation` skill open it at desktop width and at phone width (about 390px) and in dark mode, and check for console errors, failed requests, horizontal overflow and a clean render; look at a screenshot. Fix what it finds.
7. **Show and wait.** Show an outline of the page, the counts, what was dropped on a refresh, and what the check found. If `dry-run`, stop here: nothing is published.
8. **Publish on a clear yes.** Use the Artifact tool as a private page (it prompts). Do not share it. For a refresh publish to the same URL; otherwise pass a short `description` and an `icon`.
9. **Record the URL.** Show the proposed `Roadmap URL` edit to the project map and write it only after a yes.

Never publish without step 8. Do not change tickets, labels or notes. End the chat summary with three short lines: **Read** (what you read and as of when), **Not read** (what you skipped and why) and **Could not check** (anything unavailable, including a search that covered only the first page).
