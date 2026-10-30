# Letting Claude read and write your Obsidian vault (Obsidian MCP)

## Do you need this?

**For the skills in this package: no.** Claude Code, started from your vault folder, already reads and writes your notes as ordinary files. Everything in [OBSIDIAN-SETUP.md](OBSIDIAN-SETUP.md) works without this.

**You want this if** you also use Claude Desktop (or another chat app) and want it to list, search, read and create notes in your vault *through Obsidian itself*. It connects Claude to the Obsidian **Local REST API** plugin, which has a built-in MCP server.

This guide comes from a working setup on macOS and Windows with Claude Desktop. The commands were not re-run for this document. The plugin and `mcp-remote` details were checked against their own documentation on 30 Oct 2026 (sources at the end). Anything not confirmed there is marked **unverified**.

## What you will have at the end

Claude Desktop shows an "obsidian" connection, and you can ask it things like "List my Obsidian vault files" or "Search my vault for Django".

## Step 0: Homebrew (macOS only)

Skip this on Windows. Homebrew is needed to install Node.js on a Mac. If `brew --version` already works, skip to Step 1. Otherwise follow the install instructions at https://brew.sh. The installer prints two lines to add Homebrew to your shell; copy exactly the lines it gives you. On an Apple Silicon Mac they look like:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

On an Intel Mac, Homebrew installs to `/usr/local` instead of `/opt/homebrew`, so use `/usr/local/bin/npx` wherever this guide says `/opt/homebrew/bin/npx`.

```bash
brew --version
```

## Step 1: install Node.js

Claude Desktop connects to the plugin through a small helper (`mcp-remote`) that needs Node.js.

**macOS:**

```bash
brew install node
```

**Windows:** install from https://nodejs.org/en/download, or in PowerShell run `winget install OpenJS.NodeJS`.

Check each of these separately:

```bash
node -v
npm -v
npx -v
```

Find where `npx` is. You will need the path in Step 6:

```bash
which npx          # macOS
where npx          # Windows (PowerShell), typically C:\Program Files\nodejs\npx.cmd
```

## Step 2: install the Obsidian Local REST API plugin

In Obsidian: **Settings, Community plugins, Browse**, search for **Local REST API**, then **Install** and **Enable**.

## Step 3: find the key and the address

The plugin includes a built-in MCP server at `/mcp/`. In Obsidian open **Settings, Local REST API** and copy:

- the **API key**
- the address: `https://127.0.0.1:27124/mcp/`

An earlier version of this guide said to switch on an "Enable MCP Server" option under Advanced settings. The plugin's own README does not name such a toggle, so **unverified**: if you see one, turn it on; if you do not, the server may already be running.

The plugin's secure port is 27124. It also has a plain-HTTP port (27123) that is off until you enable it. Leave HTTP off unless you have a reason.

**Binding.** You connect to `127.0.0.1`, your own computer. The README does not say the server listens only there, and it mentions a configurable binding host. Check the plugin's settings and keep the binding host at `127.0.0.1`, so nothing else on your network can reach it.

## Step 4: let your computer trust the plugin's certificate

The plugin uses its own certificate. The plugin's README says to download its **CA certificate** and trust it in your system:

```
https://127.0.0.1:27124/obsidian-local-rest-api.crt
```

(Obsidian must be running for that address to work.) The plugin settings also have an **Install certificate** option.

- **macOS:** Keychain Access, Certificates, "Obsidian Local REST API", Trust, **Always Trust**. *(Unverified menu path.)*
- **Windows:** add it under **Trusted Root Certification Authorities**.

**Note:** Node (which `mcp-remote` runs on) does not use your system's trusted certificates by default. That is why the examples below also include a switch to skip the check, or you can point Node at the certificate (see "Keep it safe").

## Step 5: find Claude Desktop's config file

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

## Step 6: add the connection

Replace `YOUR_API_KEY` with the key you copied.

**Windows.** Claude Desktop on Windows has a documented bug where spaces inside `args` are not escaped when it starts `npx`. The header `Authorization: Bearer ...` contains a space, so put the value in `env` and leave no space in `args`:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx.cmd",
      "args": [
        "mcp-remote@latest",
        "https://127.0.0.1:27124/mcp/",
        "--header",
        "Authorization:${AUTH_HEADER}"
      ],
      "env": {
        "AUTH_HEADER": "Bearer YOUR_API_KEY",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  }
}
```

If `npx.cmd` is not found, replace `"command": "npx.cmd"` with the full path from `where npx`, written with doubled backslashes: `"C:\\Program Files\\nodejs\\npx.cmd"`.

**macOS.** Replace the `npx` path if yours differs (from `which npx`):

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "/usr/bin/env",
      "args": [
        "NODE_TLS_REJECT_UNAUTHORIZED=0",
        "/opt/homebrew/bin/npx",
        "mcp-remote@latest",
        "https://127.0.0.1:27124/mcp/",
        "--header",
        "Authorization: Bearer YOUR_API_KEY"
      ]
    }
  }
}
```

This form worked on a Mac. The Windows form above also works on a Mac if you prefer one layout for both.

If the file already has other servers, add `"obsidian": { ... }` inside the existing `mcpServers` block. Do not create a second `mcpServers`.

On Windows you can fetch the helper first so the first start does not stall:

```powershell
npx -y mcp-remote@latest --version
```

## Step 7: restart Claude

Quit Claude Desktop fully and reopen it.

- **macOS:** `pkill Claude`, then reopen.
- **Windows:** `taskkill /IM Claude.exe /F`, then reopen.

## Step 8: check it connected

Open the logs:

- **macOS:** `open ~/Library/Logs/Claude`
- **Windows:** `%APPDATA%\Claude\logs`

A good connection shows `obsidian-local-rest-api` as the server name, with the tools and resources listed.

## Step 9: try it

Ask Claude:

- "List my Obsidian vault files"
- "Create a note called Test.md"
- "Search my vault for 'Django'"
- "What Obsidian tools are available?"

Delete `Test.md` afterwards.

## Using it from Claude Code (optional, unverified)

Claude Code does not need this for the skills. If you want it anyway, Claude Code can add remote servers itself, with no helper. Its documented syntax for an HTTP server with a header is:

```bash
claude mcp add --transport http obsidian https://127.0.0.1:27124/mcp/ --header "Authorization: Bearer YOUR_API_KEY"
```

**Unverified:** Claude Code's documentation does not cover servers with their own certificate. If this fails with a certificate error, Claude Code is not trusting the plugin's certificate. Giving it the downloaded `.crt` through the `NODE_EXTRA_CA_CERTS` environment variable before you start Claude Code is the likely fix, but it has not been tested here.

The helper route also works. In Claude Code's syntax, options come before the server name and the server command comes after `--`:

```bash
claude mcp add --env NODE_TLS_REJECT_UNAUTHORIZED=0 --transport stdio obsidian -- npx mcp-remote@latest https://127.0.0.1:27124/mcp/ --header "Authorization: Bearer YOUR_API_KEY"
```

The tools would be named `mcp__obsidian__...`. None of this package's skills use them.

## Keep it safe

- **The API key is a password to your vault.** Anyone with it, on your machine, can read and change every note. Never paste it into a note, a ticket, a chat or a repo. If it leaks, regenerate it in the plugin settings and update the config. The plugin refuses further attempts after about ten wrong keys in a minute.
- **The config file holds the key.** Never commit `claude_desktop_config.json`, and keep it out of any repo. On the command line the key can also show up in your computer's process list. `mcp-remote` has a `--header-file` option that keeps it out of there (see its README).
- **The plugin protects Obsidian's own settings folder by default** (`.obsidian`). Leave "Allow access to the configuration directory" **off**: turning it on gives every holder of the key that access.
- **Certificate checking is switched off in the examples** (`NODE_TLS_REJECT_UNAUTHORIZED=0`). The plugin's own README lists skipping verification for `127.0.0.1` as an option, and this connection stays on your computer, but the safer route is to trust the certificate. `mcp-remote`'s README documents `NODE_EXTRA_CA_CERTS` for custom certificates. Download the plugin's `.crt` file (Step 4), then in the config's `env` block set `NODE_EXTRA_CA_CERTS` to its full path and remove the `NODE_TLS_REJECT_UNAUTHORIZED` line. **Unverified** for this plugin: test it, and put the skip-verification line back if it fails.
- **`mcp-remote@latest` downloads the newest version every time Claude starts.** Once it works, consider replacing `@latest` with the exact version you tested, so a bad update cannot reach your key. Find it with `npm view mcp-remote version`.
- **Claude can create and edit notes through this connection without the show-first approvals the skills use.** Ask it to show you what it would change before it writes. If your vault holds credential notes, remember this connection can read them. Keep those in a separate vault if that worries you.

## If it does not work

| Symptom | Check |
|---|---|
| Nothing named "obsidian" in Claude | Fully quit and reopen Claude. Check the config is valid JSON and sits inside one `mcpServers` block. |
| "command not found" | Re-run `which npx` or `where npx` and use that full path in the config. |
| Works on Mac, fails on Windows with a header or "unauthorized" error | Use the Windows form in Step 6, with the header value in `env`. |
| Certificate or connection errors | Is Obsidian open, with the plugin enabled? Try `curl -k https://127.0.0.1:27124/mcp/`. The connection should succeed. |
| Claude connects but cannot see notes | Confirm you opened the right vault in Obsidian, since the plugin serves the vault that is open. |
| The key stopped working | Regenerate it in the plugin settings and update the config. |

## Sources

- Obsidian Local REST API plugin (built-in MCP server, ports, certificate, security notes): https://github.com/coddingtonbear/obsidian-local-rest-api
- `mcp-remote` (config format, headers, the Windows spaces bug, `--header-file`, custom certificates): https://github.com/geelen/mcp-remote
- Claude Code, adding MCP servers (`claude mcp add` syntax): https://code.claude.com/docs/en/mcp.md
