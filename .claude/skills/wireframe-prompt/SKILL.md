---
name: wireframe-prompt
description: Write an extensive wireframing prompt for one area of a project from the vault notes, scope note and project memory, show it for approval, then build the first prototype wireframes as a private Claude artifact. Manual use only.
disable-model-invocation: true
argument-hint: "<project> <area, e.g. client portal> [dry-run]"
allowed-tools: Read Grep Glob mcp__claude_ai_Linear__list_issues mcp__claude_ai_Linear__get_issue mcp__claude_ai_Linear__list_projects mcp__claude_ai_Slack__slack_search_channels mcp__claude_ai_Slack__slack_read_channel mcp__claude_ai_Slack__slack_read_thread mcp__claude_ai_Slack__slack_search_public mcp__claude_ai_Google_Drive__search_files mcp__claude_ai_Google_Drive__read_file_content mcp__claude_ai_Granola__list_meetings mcp__claude_ai_Granola__get_meetings mcp__claude_ai_Granola__query_granola_meetings
---

# /wireframe-prompt

Arguments: `$ARGUMENTS` = a project, the area to wireframe, optionally `dry-run`.

Read first: `.claude/project-map.md`, `.claude/reference/ticket-rules.md` (including the Standing rulings), `.claude/reference/vault-update-rules.md`. Find any earlier wireframe prompts with Glob `**/*Wireframe*Prompt*.md`. Take their tone and level of detail as the model; the structure in step 4 below is the one to follow. Scratch writes (a draft in the session scratchpad) are fine in every mode.

## Steps
1. **Scope the request.** Identify the project and the area. If the area is unclear, ask one question.
2. **Freshness sweep, then find and read the context.** Do the sweep in `project-map.md` and open with what you read. Then read what the area needs:
   - The plan: `<Project>/Scope and Phasing.md` and the roadmap (the roadmap URL in the project map, if there is one). If either is missing, say so, use the project's start notes and the nearest scope documents instead, and mark the area's scope status as proposed.
   - The notes on the area: use Glob and Grep on the project folder with the area's keywords and synonyms, plus the notes the start notes link to. Order by age using the note's `date` frontmatter, else the date in its filename, else its file modified time; say when you fell back.
   - A note is **superseded** if it says so, or if a later dated note on the same topic replaces it. Skip superseded content, and say what you skipped and why.
   - The project's saved memory: the `memory` folder under `~/.claude/projects/<this working directory with / replaced by ->/memory/`. If it is empty, say so.
   - Design links: the project's `Design links` in the project map, and links in the notes and Slack. Reference the existing prototypes in the prompt by link, saying what each shows, so the designer builds on them.
   - Linear: list the project's tickets (including Done and Canceled) and read those in the area, paging until the list is complete. A Canceled or Done epic matters even if the notes call it live.
   Credential notes are never inputs. If a source note holds a credential, a real email or other personal data, do not carry it over; use an invented placeholder.
3. **Ask the PM before you put a decision in the prompt.** A product decision the PM can make is asked in chat and written in as the answer. Only decisions that depend on the client, or on dev, go under "Open decisions" in the prompt, with the options. Ask the designer for a clearly labelled placeholder or both versions.
4. **Write the prompt** in this structure, in plain language. Backend limits are expressed only as what the user sees (for example "we may only be able to show the valuation from this visit"); leave out anything that cannot be said that way. No technical implementation detail, no credentials. "Extensive" means every screen and state is covered, with no fixed length.
   - **Opening:** what the product is, who the users are, and where this area sits in the journey.
   - **Labels used:** *Confirmed* means agreed by the client or confirmed as real by a dated team note; *Proposed* is anything else, including customer-facing wording that has not been agreed; *Exploratory* may not go ahead. Ask for a visible tag on each screen.
   - **Scope status** of the area, from the plan.
   - **Entry and access:** how a user gets here and what they must do first.
   - **Sections or screens,** in journey order. For each: purpose, who sees it, the content, key actions, the states (empty, loading, error, success) and the user-visible logic (statuses, eligibility, what happens next).
   - **Design requirements:** mobile-first, empty states as important as filled ones, brand and wording rules from the notes, accessibility basics (contrast, tap targets, labels, errors in words, not colour alone), invented placeholder data only. If the notes name only a palette and give no hex values or fonts, say so and ask the designer to propose them; never invent brand detail.
   - **Open decisions:** numbered. Ticket IDs may appear here and nowhere else in the prompt.
   - **Deliverable:** the list of screens, with the states each must show, as one clickable low-fidelity prototype. The placeholder copy lives in the wireframe, not in the prompt.
5. **Show the prompt** in full, then four short lists: what you read, what you skipped (and why), conflicts flagged, and what Linear shows about the area (including items that are not conflicts). Then say what the next step is. If `dry-run`, stop here: nothing is saved or built.
6. **Wait for a clear yes.** Requested changes are made and shown again.
7. **Save the prompt** after the yes, as a new note `<Project>/Wireframe Prompt - <area>.md` following `vault-update-rules.md` (frontmatter with the project tag and `date`; `Parent: [[Overview]]`; the prompt in a fenced block; a Related list that links any earlier prompt for the area). Show a short summary of the new note first. Never overwrite an earlier prompt. If the new one replaces it, propose marking the earlier one "superseded" as a separate diff shown first.
8. **Build the wireframes.** Load `artifact-design` with the Skill tool. Build one self-contained HTML wireframe prototype that follows the approved prompt exactly: low fidelity, every listed screen and state, a clickable flow, and the Confirmed, Proposed and Exploratory tags. Check it locally with the `browser-automation` skill (render, console errors, a screenshot) and fix what it finds.
9. **Publish privately** with the Artifact tool (it prompts), with an icon and a short description. Report the URL. Never share the page. Offer revisions; each is shown, then rebuilt and republished to the same URL.

Never build before step 6. Do not change tickets or other notes. End the chat summary with three short lines: **Read** (what you read and as of when), **Not read** (what you skipped and why) and **Could not check** (anything unavailable, including a search that covered only the first page).
