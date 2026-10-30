# Connecting Linear, Granola, Slack and Google Drive

The skills and the agent read your tools through MCP connectors. This guide gets them connected and checked. Facts here were checked against the vendors' documentation on 30 Oct 2026. Where something could not be confirmed, it says so: check the linked page before relying on it.

## What each connector is for

| Connector | Used for | Needed? |
|---|---|---|
| **Linear** | Reading tickets, and creating or updating them after you approve | Required for every ticket skill. Without it the skills stop and say so. |
| **Granola** | The latest call notes, for `/morning-digest`, `/update-ticket` and the freshness sweep | Recommended. Without it the skills say the calls were not read. |
| **Slack** | Project channels as context | Optional. |
| **Google Drive** | Client-facing documents such as a roadmap | Optional. |

## Option A: claude.ai connectors (recommended)

The skills name tools exactly the way claude.ai connectors do, for example `mcp__claude_ai_Linear__list_issues`. If you connect through claude.ai, nothing needs editing.

1. Log in to Claude Code with a claude.ai account. Connectors are not available when Claude Code uses an API key, Bedrock, Vertex or Foundry for sign-in. Run `/status` to see which you are using.
2. Add each service at https://claude.ai/customize/connectors. On a Team or Enterprise plan only an admin can add a server.
3. Complete the sign-in for each in the browser. Everyone connects with their own account, so you only see what you could see in that tool anyway.
4. Start Claude Code and run `/mcp`. The claude.ai servers are listed there. Each should show as connected.

The connector's display name decides the tool names. The skills expect the display names **Linear**, **Granola**, **Slack** and **Google Drive**. If yours are named differently, the tools will not match; use Option B's rewrite step below.

Check it worked: in a session started from your vault, run `/new-ticket test dry-run`. If it says a tool is missing or not allowed, a connector is not connected or is named differently.

## Option B: adding servers yourself with `claude mcp add`

A server you add this way is named by you, and its tools are named `mcp__<your server name>__<tool>`. The skills would not match, so rewrite the names to fit.

Commands (each opens a browser sign-in the first time you use it, through `/mcp`):

```bash
claude mcp add --transport http linear https://mcp.linear.app/mcp
claude mcp add --transport http granola https://mcp.granola.ai/mcp
```

- **Slack:** Slack's documented route for Claude Code is its plugin: run `/plugin install slack` inside Claude Code. A Slack workspace admin must approve the MCP integration first.
- **Google Drive:** there is no official remote MCP address in the documentation I could reach, so none is given here. Use the claude.ai connector (Option A), or your own Drive server.

Then rewrite the package's tool names to match the server names you chose. First look, then apply:

```bash
python3 tools/retarget_mcp.py /path/to/your/vault --map Linear=linear --map Granola=granola
python3 tools/retarget_mcp.py /path/to/your/vault --map Linear=linear --map Granola=granola --write
python3 tools/doctor.py --root /path/to/your/vault
```

The names on the left are `Linear`, `Granola`, `Slack` and `Google_Drive`. The names on the right are the server names `/mcp` shows. The rewrite changes the prefix only. For a server that is not the claude.ai connector, the tool names after the prefix may also differ (for example a Slack plugin may offer different tools). Compare the tools `/mcp` lists with the ones in the skills' `allowed-tools`, and edit any that differ.

If a local server and a claude.ai connector point at the same address, the local one is used and the connector is hidden.

## Permissions

The first time a tool is used, Claude Code asks. To avoid a prompt for every read, copy the rules in `.claude/settings.example.json` into `.claude/settings.local.json` (the installer does this for you if the file is missing). They allow reading only.

- Do **not** allow anything that creates, edits or deletes (`save_`, `create_`, `update_`, `delete_`, `send_`). The permission prompt is the second approval before any write, after your own yes. The linter in `tools/lint_skills.py` fails if a skill allows one.
- Rules can use a wildcard for a whole server, such as `mcp__linear__*`, but do not use that for Linear: it would also allow the write tools. Whether a wildcard works inside a skill's own `allowed-tools` line is not documented, so the package lists tools one by one.

## Plans and limits worth knowing

- **Granola:** on a free plan you only see the last 30 days of notes, and full transcripts and folders need a paid plan. The skills work from the summaries and say when transcripts were not read. On an Enterprise plan an admin chooses which notes members can reach.
- **Slack:** needs workspace admin approval before it can connect.
- **Linear:** the documentation describes browser sign-in and states no general admin approval step. Your own workspace's rules may still apply.

## If something does not work

| Symptom | Fix |
|---|---|
| `/mcp` shows a server as not connected | Select it and sign in again. Sign-in sessions expire. |
| A skill says a tool is not available | The tool name does not match. Compare `/mcp` with the skill's `allowed-tools` line, or use the rewrite step. |
| Nothing from claude.ai shows up | You may be signed in another way. Run `/status`, and sign in with your claude.ai account. |
| Linear reads fail | The ticket skills stop. Reconnect Linear first. |

## Sources

- Claude Code, using MCP servers and claude.ai connectors: https://code.claude.com/docs/en/mcp.md
- Claude Code, permission rules for MCP tools: https://code.claude.com/docs/en/permissions.md
- Claude connectors directory: https://claude.com/docs/connectors/
- Linear MCP server: https://linear.app/docs/mcp
- Granola MCP: https://docs.granola.ai/help-center/sharing/integrations/mcp
- Slack MCP server: https://docs.slack.dev/ai/slack-mcp-server/connect-to-claude/

The `claude_ai_` prefix in the tool names comes from claude.ai's connector naming. The documentation does not spell this out directly, so treat the exact prefix as observed behaviour, and confirm it in your own `/mcp` list.
