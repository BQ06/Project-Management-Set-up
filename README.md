# Project-Management-Set-up

Repo housing all skills and agents used for Product Ownership/Management purposes.

## Project-management agent and skills for Claude Code

A read-only project-manager agent and eight skills that turn your project notes, Linear tickets, Granola calls and Slack into accurate, reviewed tickets, plans and digests. Everything that writes (a ticket, a note, a published page) shows you the full result first and waits for a clear yes. Tickets in Done or QA are never touched.

This repo holds the agents and skills only. It does not hold any project notes, credentials or client data: those stay in your own vault.

## What is in it

| | |
|---|---|
| Agent | `project-manager`: read-only status, gap and conflict checks |
| Skills | `/new-ticket`, `/update-ticket`, `/tickets-from-updates`, `/morning-digest`, `/intake`, `/scope-project`, `/roadmap`, `/wireframe-prompt` |
| Rules | `ticket-rules.md` (every ticket rule and standing ruling), `vault-update-rules.md` |
| Templates | standard, epic and design ticket templates, enforced by the ticket checker |
| Config | `pm-config.json` (your Linear team keys), `project-map.md` (your projects), `settings.local.json` (permissions) |
| Scripts | the ticket checker, the changed-notes finder and the digest window, with 76 tests |
| Starter notes | `starter/ExampleProject/`: an Overview, Scope Boundaries and Open Questions note to copy for a first project |
| Tools | installer, setup checker (`doctor`), skills linter, secret scanner, vault exporter, MCP name rewriter, with 60 tests |

Read these in order:

1. [docs/OBSIDIAN-SETUP.md](docs/OBSIDIAN-SETUP.md): start here if you have no vault yet. Set up Obsidian, install this, and write notes the skills can use.
2. [docs/HOW-TO.md](docs/HOW-TO.md): how to use the agent and each skill, day to day.
3. [docs/MCP-SETUP.md](docs/MCP-SETUP.md): connect Linear, Granola, Slack and Google Drive.
4. [docs/ADAPTING.md](docs/ADAPTING.md): change the team keys, workflow statuses, house rules and templates to fit your own team.
5. [docs/OBSIDIAN-MCP.md](docs/OBSIDIAN-MCP.md): optional. Let Claude Desktop read and write your vault through Obsidian. The skills do not need it.

## Where everything is

The agent and skills sit in a folder whose name starts with a dot, `.claude`. Finder hides such folders (press Cmd+Shift+. to show them), and GitHub shows them normally. Claude Code only looks for agents and skills in that exact place, so the folder cannot be renamed or moved.

| What | Where |
|---|---|
| The agent | [`.claude/agents/project-manager.md`](.claude/agents/project-manager.md) |
| The skills (one folder each, with a `SKILL.md`) | [`.claude/skills/`](.claude/skills/) |
| Ticket rules and house rules | [`.claude/reference/`](.claude/reference/) |
| Scripts and their tests | [`.claude/scripts/`](.claude/scripts/) |
| Ticket templates | [`Templates/Tickets/`](Templates/Tickets/) |
| Examples to copy (project map, settings, config, `CLAUDE.md`) | [`.claude/`](.claude/) and the repo root, files named `*.example.*` |
| Starter notes for a first project | [`starter/ExampleProject/`](starter/ExampleProject/) |
| Installer, setup checker, linter, scanner, exporter | [`tools/`](tools/) |

## Prerequisites

- Claude Code, started from your vault folder.
- Python 3.9 or newer (standard library only; nothing to install).
- Connectors in Claude Code (check with `/mcp`): **Linear** (required for the ticket skills), **Granola**, **Slack** and **Google Drive** (used for context; the skills say when a source is missing). The skills expect claude.ai connectors. Setup, and what to do if you add servers another way, is in [docs/MCP-SETUP.md](docs/MCP-SETUP.md).
- A vault: a folder of project notes, with one subfolder per project.
- `/roadmap` and `/wireframe-prompt` also use Claude's Artifact tool and its `artifact-design` and `browser-automation` skills.

## Quick start

```bash
git clone <this repo> pm-agents-skills
python3 pm-agents-skills/tools/install.py /path/to/your/vault --with-starter
```

The installer copies the agent, skills, rules, scripts and templates into your vault. `--with-starter` also creates an `ExampleProject` folder of three starter notes. It never overwrites a file you already have, and it creates four files from the examples only if they are missing: `.claude/project-map.md`, `.claude/pm-config.json`, `.claude/settings.local.json` and `CLAUDE.md`.

Then:

1. Edit `.claude/project-map.md`: replace `ExampleProject` with your own projects (vault folder, Linear project, start notes, aliases). Set your Linear team keys in `.claude/pm-config.json` if they are not `DEV` and `DES`. See [docs/ADAPTING.md](docs/ADAPTING.md).
2. Run `python3 pm-agents-skills/tools/doctor.py --root /path/to/your/vault` and fix anything that fails.
3. Start Claude Code in the vault, run `/skills` to confirm the commands load, then try `/new-ticket <short description> dry-run`.

## Safety

- **Nothing writes without a clear yes.** Skills show the full draft, check it, and wait.
- **Writes are not pre-approved.** The skills' permission lists contain read tools only, so creating or editing a ticket always prompts. The linter fails the build if a skill pre-approves a write.
- **Done and QA tickets are read-only,** and their IDs are never written into other tickets, because in Linear a written ID creates a link that touches the finished ticket.
- **Credentials never go in the project map, notes or digests.** The secret scanner and the setup checker both look for them.
- **The agent is read-only:** no edit, write or shell tools.

## Keeping this repo and your vault in step

Your vault's `.claude` is the working copy. After you improve a skill there, rebuild this repo's copy:

```bash
python3 tools/export_from_vault.py /path/to/your/vault
python3 tools/scan_secrets.py
```

The exporter copies only the agent, skills, rules, scripts and templates. It refuses to copy anything if the scanner finds a credential, a personal path, an email address, a real Slack channel ID or a real artifact link in those files. It never copies `project-map.md`, settings, plans, state or any note.

## Development

```bash
python3 -m unittest discover -s .claude/scripts -p "test_*.py"   # ticket checker, note changes, digest window
python3 -m unittest discover -s tools/tests                      # linter, scanner, exporter, installer, doctor
python3 tools/lint_skills.py                                     # agents and skills
python3 tools/scan_secrets.py                                    # nothing sensitive
```

GitHub Actions runs all four on every push and pull request, on Python 3.9 and 3.12.

## Credits

The `/intake` skill's interview style (one question at a time, play the understanding back, build nothing before approval) is inspired by the brainstorming skill in [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent (obra), MIT licence. Superpowers is not included here. It is a separate, optional install that works well alongside these skills.

## Version

See [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md).
