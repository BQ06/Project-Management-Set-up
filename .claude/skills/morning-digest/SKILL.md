---
name: morning-digest
description: Alias for /board-refresh, the daily and on-demand board review. Kept so the old command still works.
argument-hint: "[project | all] [walk | no-walk] [dry-run]"
allowed-tools: Read Skill
---

# /morning-digest

Read `.claude/project-map.md` first. This command is now `/board-refresh`. Run the `board-refresh` skill with the same arguments (`$ARGUMENTS`) and follow it exactly. The review covers the board check, the product walk and the meetings, and writes `<Project>/Ticket Digests/YYYY-MM-DD.md`. Proposals only.
