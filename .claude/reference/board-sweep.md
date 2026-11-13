# Board sweep

The checks the project-manager agent and `/board-refresh` run on a project's board. Read-only: they report and propose, a person makes the change. The Golden rule and Ownership rule in `ticket-rules.md` and `CLAUDE.md` apply to everything here.

## The Todo rule (dev team, 6 Nov 2026)
A ticket is Todo only when we are 100% sure of both:
1. A developer can finish it with no blockers.
2. It is definitely needed and its requirements are final.

If it is not needed soon, its priority is Low. Anything waiting on a client or partner decision stays in Backlog, even if it could be built with placeholder data. The epic's readiness summary still lists it as "buildable once X is confirmed".

## What counts as a blocker
- A blocker is an open ticket that must finish first for the work to make sense, and it is a Linear "blocked by" link. A blocker written only in the description is not enough.
- A decision from a client or partner, or a feasibility answer from an external engineer, is "Waiting on", not a blocker. It keeps the ticket in Backlog.
- Placeholder test: if the ticket can be built and shown with placeholder data, it is not blocked by the missing data or API. Default split: (1) the screen with placeholder data, (2) the back-end job, (3) a connect ticket blocked by both. Only the connect ticket is blocked.
- A blocker that is Done or QA is no longer a blocker. Drop it from the text; leave an existing link alone (removing it touches the Done or QA ticket). Never write a Done or QA ID in ticket text.
- An open developer ticket may be named and linked as a blocker.

## How to read the board
1. List every ticket in the project with status, parent, creator, assignee and priority. Follow the cursor while `hasNextPage` is true.
2. Read each ticket with `get_issue` and its relations included, and note status, creator, assignee, labels and priority. You may follow a blocker outside the tickets you were asked about, read-only, to learn its status. Statuses and links come from live Linear, never from earlier summaries or from another agent's report.
3. Read descriptions in full; the checks compare the text with the links.
4. Reading Done and QA tickets is allowed. Recommending a change to one is not: say "flag only".

## Checks
### A. Stale blocker, or text and links disagree
Text names a blocker the links do not show (or the reverse), or a named blocker is Done, QA, Canceled or finished work described elsewhere.

### B. Not actually blocked
The ticket is blocked only by missing data, an API or a back end, and could be built and shown with placeholder data. Propose removing the link and adding "build against placeholder data", or the three-ticket split when the ticket mixes two jobs. Run B before G: first decide whether the blocker is real. A text-only blocker that is not real is removed from the text (not linked); a real one gets a Linear link (check G).

### C. Status does not match the Todo rule
- Todo with an open blocker, an open client decision, or unfinished requirements: propose Backlog (own tickets) or flag (others').
- In Progress with an open blocker or open decision: never moved by us; flag it to the developer.
- Backlog with every blocker cleared, an owner and final requirements: propose Todo.
- Blocked status with no link or no named external owner.
- Unanswered partner or external-engineer items under Waiting on or External: if the answer could change what this ticket builds, the ticket is Backlog. An item that only matters at go-live, or for a different ticket, does not belong under Waiting on; record it in the epic's readiness summary under "needed before go-live".

### D. Circular dependency
Follow "blocked by" links; report any ticket that is reachable from itself, with the chain.

### E. Dead-end blocker
The blocking ticket is in Backlog and unassigned, or is itself blocked, or blocks many tickets while having no owner.

### F. "None" while a decision is pending
"Open questions" says None (or the epic's readiness says nothing is waiting) while a client or partner decision is still open anywhere in the ticket, its comments or the latest calls.

### G. Blockers not linked
A blocker is written in the description with no Linear link, or a link has no matching text, or the text names a ticket that only has a "related" link.

### H. Priority
Work that is not needed soon is not marked Low. Work that is urgent is marked Low. A Todo with "No priority" is a minor note ("set a priority"), not a breach.

### I. Wording
Old-template headings (Expected behaviour, Potential impacts, Acceptance criteria, Dependencies with Blocks / External), jargon, over-long text. Use `python3 .claude/scripts/check_ticket.py` for tickets you have a draft of; for live tickets judge the description by eye against the current template headings (Business context, Requirements, Design, Dependencies, Open questions) and the jargon and length rules.

### J. Set-up gaps
A ticket with no priority, a Todo with no assignee, a design ticket without the `Design` label, a child ticket with no parent where the notes show an epic owns it, or a priority, label or assignee that differs from what the PM approved. These are minor notes ("set a priority"), not breaches: the set-up fields are optional for the PM (Set-up questions in `ticket-rules.md`). Flag only on other people's tickets.

## Report
One table per project, most serious first:

| Ticket | Creator | Status | Check | What is wrong | Proposed fix |
|---|---|---|---|---|---|

- Own tickets (created by the PM): propose the exact change (link to remove, line to edit, status or priority).
- Other people's tickets: "flag only" and who to tell.
- Done and QA tickets: never in the Proposed fix column.
- Every row carries a Linear link: `https://linear.app/<workspace>/issue/<ID>`.
- End with Read, Not read, Could not check lines.
- Mark anything not verified live as "not verified".

## Readiness summary (epics)
For an epic, also give a readiness summary from the same reading, headed "As of <date>": build order; can build now; can build with placeholder data; waiting on the client (and who is chasing); blocked by unbuilt work; buildable once a client confirmation arrives; needed before go-live. Link the dev tasks; do not copy their wording. For an epic created by the PM, offer it as an `/update-ticket` change. For an epic created by a developer, it appears in the digest only.
