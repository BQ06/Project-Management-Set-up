---
name: new-ticket
description: Draft and create one Linear ticket from a short description, using the vault templates and the project notes. Manual use only.
disable-model-invocation: true
argument-hint: "<short description> [project] [dry-run]"
allowed-tools: Read Grep Glob Bash(python3 .claude/scripts/check_ticket.py *) mcp__claude_ai_Linear__list_issues mcp__claude_ai_Linear__get_issue mcp__claude_ai_Linear__list_projects mcp__claude_ai_Linear__list_teams mcp__claude_ai_Linear__list_issue_labels mcp__claude_ai_Linear__list_comments mcp__claude_ai_Slack__slack_search_channels mcp__claude_ai_Slack__slack_read_channel mcp__claude_ai_Slack__slack_read_thread mcp__claude_ai_Slack__slack_search_public mcp__claude_ai_Google_Drive__search_files mcp__claude_ai_Google_Drive__read_file_content mcp__claude_ai_Granola__list_meetings mcp__claude_ai_Granola__get_meetings mcp__claude_ai_Granola__query_granola_meetings
---

# /new-ticket

Creates ONE ticket. Arguments: `$ARGUMENTS` = a short description, optionally a project name, optionally `dry-run`.

Read these first: `.claude/project-map.md`, `.claude/reference/ticket-rules.md` (including the Standing rulings). Follow them exactly. Credential notes in the project map are read only when the ticket needs credentials.

## Golden rule
Never touch a ticket in Done or QA (see `ticket-rules.md`). Do not set a Done or QA ticket as the parent, and do not add a relation to one. If the conflict check finds that a Done or QA ticket already covers the outcome, say so and stop; nothing is created or linked.

Only the PM's own tickets are edited (Ownership rule in `ticket-rules.md`). Read `createdBy` on any existing ticket the conflict check turns up. A ticket created by someone else is read-only: do not edit, comment on, relate or reparent it. Report the overlap to the PM, who decides whether the new ticket is still needed.

## Steps
1. **Project.** Work it out from the argument or the description. If it is genuinely unclear, ask one question. If Linear is not connected, stop and say so.
2. **Template.** Choose Standard, Epic or Design (UX design work for the Design Team, title `[DESIGN] - <what>`) using the rules in `ticket-rules.md`. Say which and why in one line. If unsure, ask one question. For an epic, also propose its child standard tickets (titles only) and say they would be sub-issues. Create the epic only; children are drafted one at a time afterwards.
3. **Read the template** from `Templates/Tickets/` (not from memory).
4. **Freshness sweep, then gather facts.** Do the sweep in `project-map.md` (fresh Linear, the latest Granola calls, Slack, newest notes) and also read the project's wireframe or design artifact and, for projects the map links as siblings, the sibling project's folder. Say what you read. If the ticket depends on something the client has not confirmed, hold it and say so (Standing rulings). Do not raise separate testing or audit tickets. If a vault note is stale against a newer source, say so. **Gather facts** from the project's start notes and the notes the description points to. Read only what you need. Do not ask for anything the notes already state. If the notes do not say it, it does not go in the ticket: use "N/A" where the line truly does not apply, or a genuine question under Open questions.
5. **Conflict check** exactly as in `ticket-rules.md`. **The conflict check always cross-references three groups in the same area: Done tickets, QA tickets and Backlog/To-do tickets.** Read each one's description in full (not titles), name the covering ticket, and classify the open ticket as built (propose closing it as Canceled, with a comment on the open ticket only), partly built (rewrite it down to what is missing), conflicting (state the conflict, never pick a side) or still needed. Done and QA tickets are read-only. See `ticket-rules.md`, Conflict check step 0. If a ticket already covers the outcome, show it and ask: update it (use `/update-ticket`) or skip. Never create a duplicate. If specs conflict, put the conflict in Open questions and draft the Linear comment for dev.
   Also decide the parent: if the notes or the conflict check show it belongs under an existing epic, propose that parent and ask the user to confirm. Run the Hierarchy check in `ticket-rules.md` on the proposed parent, its epic and its children.
   Before drafting, list the questions the PM can answer and ask them one at a time (see "Open questions" in `ticket-rules.md`). Only dev-dependent questions may stay in the ticket.
6. **Draft** in the template's exact structure, product-focused: the user and client journey and the logic, no technical detail. Size the ticket to the change and keep Expected behaviour short and plain (see "Quality bar" in `ticket-rules.md`): a small change gets a short ticket, and a larger change may carry a slightly longer context where it helps dev. Add the optional Credentials section only if the ticket needs it (see `ticket-rules.md`) and say in the summary that it does.
7. **Check.** Save the draft to a scratch file in the session scratchpad and run the check script as written in `ticket-rules.md`. Fix every FAIL and rerun until it prints OK. The script also lists every ticket ID in the draft: run `get_issue` on each and replace any Done or QA ID with a plain description of the finished work.
8. **Show** the full text of the draft, not a summary, the check result, the team (DEV or DES), the project, the parent if any, the Hierarchy table, and any drafted comment. For a design ticket also show the labels (`Design` plus the paired dev ticket's phase label) and the assignee (the design team lead named in the project map), and send them with the create. If `dry-run` was given, stop here and say nothing was created.
9. **Wait for a clear yes.** Anything else is not approval.
10. **Create.** Re-run the check on the exact text, then call `mcp__claude_ai_Linear__save_issue` (this prompts; that is intended). Send the `## <title>` line's text as `title` and leave that line out of `description`, so the title is not printed twice in the ticket (see `ticket-rules.md`). Report the ID and URL. Post a drafted comment only if the user approved it.

Never create, edit or comment on a ticket without step 9. Do not set phase labels.
