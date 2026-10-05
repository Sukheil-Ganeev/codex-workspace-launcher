---
name: browser-use-cli
description: "Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, or extract information from web pages."
allowed-tools: Bash(browser-use:*)
---
# Browser Automation with browser-use CLI

The `browser-use` command provides fast, persistent browser automation. A background daemon keeps the browser open across commands, giving ~50ms latency per call.

## Prerequisites

```bash
browser-use doctor    # Verify installation
```

For setup details, see https://github.com/browser-use/browser-use/blob/main/browser_use/skill_cli/README.md

## Core Workflow

1. **Navigate**: `browser-use open <url>` — starts browser if needed
2. **Inspect**: `browser-use state` — returns clickable elements with indices
3. **Interact**: use indices from state (`browser-use click 5`, `browser-use input 3 "text"`)
4. **Verify**: `browser-use state` or `browser-use screenshot` to confirm
5. **Repeat**: browser stays open between commands
6. **Cleanup**: `browser-use close` when done

## Browser Modes

```bash
browser-use open <url>                         # Default: headless Chromium
browser-use --headed open <url>                # Visible window
browser-use --profile "Default" open <url>      # Real Chrome with Default profile (existing logins/cookies)
browser-use --profile "Profile 1" open <url>   # Real Chrome with named profile
browser-use --connect open <url>               # Auto-discover running Chrome via CDP
browser-use --cdp-url ws://localhost:9222/... open <url>  # Connect via CDP URL
```

`--connect`, `--cdp-url`, and `--profile` are mutually exclusive.

## Commands

```bash
# Navigation
browser-use open <url>                    # Navigate to URL
browser-use back                          # Go back in history
browser-use scroll down                   # Scroll down (--amount N for pixels)
browser-use scroll up                     # Scroll up
browser-use switch <tab>                  # Switch to tab by index
browser-use close-tab [tab]              # Close tab (current if no index)

# Page State — always run state first to get element indices
browser-use state                         # URL, title, clickable elements with indices
browser-use screenshot [path.png]         # Screenshot (base64 if no path, --full for full page)

# Interactions — use indices from state
browser-use click <index>                 # Click element by index
browser-use click <x> <y>                 # Click at pixel coordinates
browser-use type "text"                   # Type into focused element
browser-use input <index> "text"          # Click element, then type
browser-use keys "Enter"                  # Send keyboard keys (also "Control+a", etc.)
browser-use select <index> "option"       # Select dropdown option
browser-use upload <index> <path>         # Upload file to file input
browser-use hover <index>                 # Hover over element
browser-use dblclick <index>              # Double-click element
browser-use rightclick <index>            # Right-click element

# Data Extraction
browser-use eval "js code"                # Execute JavaScript, return result
browser-use get title                     # Page title
browser-use get html [--selector "h1"]    # Page HTML (or scoped to selector)
browser-use get text <index>              # Element text content
browser-use get value <index>             # Input/textarea value
browser-use get attributes <index>        # Element attributes
browser-use get bbox <index>              # Bounding box (x, y, width, height)

# Wait
browser-use wait selector "css"           # Wait for element (--state visible|hidden|attached|detached, --timeout ms)
browser-use wait text "text"              # Wait for text to appear

# Cookies
browser-use cookies get [--url <url>]     # Get cookies (optionally filtered)
browser-use cookies set <name> <value>    # Set cookie (--domain, --secure, --http-only, --same-site, --expires)
browser-use cookies clear [--url <url>]   # Clear cookies
browser-use cookies export <file>         # Export to JSON
browser-use cookies import <file>         # Import from JSON

# Python — persistent session with browser access
browser-use python "code"                 # Execute Python (variables persist across calls)
browser-use python --file script.py       # Run file
browser-use python --vars                 # Show defined variables
browser-use python --reset                # Clear namespace

# Session
browser-use close                         # Close browser and stop daemon
browser-use sessions                      # List active sessions
browser-use close --all                   # Close all sessions
```

The Python `browser` object provides: `browser.url`, `browser.title`, `browser.html`, `browser.goto(url)`, `browser.back()`, `browser.click(index)`, `browser.type(text)`, `browser.input(index, text)`, `browser.keys(keys)`, `browser.upload(index, path)`, `browser.screenshot(path)`, `browser.scroll(direction, amount)`, `browser.wait(seconds)`.

Cookie safety policy:

- `cookies get` is acceptable for debugging whether a site sees a session, but
  avoid printing sensitive values into the final user response.
- Ask before `cookies export`, `cookies import`, `cookies clear`, or setting
  auth/session cookies.
- Do not use cookie export/import as the first choice for Google, Gmail, Drive,
  banking, payments, or other high-security accounts. Use controlled profiles
  and manual user login instead.
- If cookies are exported for a low-risk site, store them in a clearly named
  temporary file and delete/rotate them when the task is complete if requested.

## Capability Selection

Use this quick decision guide:

```text
Need to click/form/navigate once        -> state + click/input/keys
Need data from visible page             -> extract, then verify if important
Need reliable machine parsing           -> --json
Need repeated multi-step workflow       -> python --file
Need logged-in Google work for AI       -> start ai1/ai2 controlled profile
Need user's main Google account         -> use main only when explicitly needed
Need local website shown externally     -> tunnel, then stop tunnel
Need remote disposable browser          -> cloud, only after user approval
Need browser automation as a service    -> --mcp, only for intentional MCP setup
```

## Underused Local Capabilities

These CLI capabilities are available locally and should be considered before
building custom browser code.

### Structured Output with `--json`

Use `--json` when a command result needs to be parsed by an agent or script.
Prefer it for status checks, session inventory, and repeatable automation.

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use --json sessions
browser-use --json state
```

Use plain text output when the result is meant for quick human inspection.

### LLM Data Extraction with `extract`

Use `extract` when the task is to pull meaning from the current page rather
than to click through an interface. Good fits: prices, contacts, product data,
terms, lists, table-like content, or short summaries of what is visible.

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use open https://example.com
browser-use extract "Extract product names, prices, and availability as a compact table"
```

Treat `extract` output as a working extraction, not legal/financial truth. For
high-stakes data, verify with `state`, `get html`, screenshots, or source URLs.

### Repeatable Browser Scripts with `python --file`

For multi-step workflows, prefer a small Python file over long chains of CLI
commands. This is useful when a task needs loops, retries, structured output,
or repeated checks.

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use python --file .\scripts\browser_task.py
```

Keep these scripts short, task-specific, and easy to delete or adapt. Avoid
putting passwords, 2FA codes, or permanent secrets in scripts.

### MCP Server Mode

The CLI can run as an MCP server:

```powershell
browser-use --mcp
```

Use this only when intentionally wiring Browser Use into an MCP-capable agent
runtime. Do not start it casually during normal one-off browser tasks.

Local Codex MCP setup on this Windows machine:

```text
browser-use-ai1 -> C:\Users\londo\.browser-use\mcp-ai1-config.json -> C:\Users\londo\.browser-use\chrome-google-ai1-profile
browser-use-ai2 -> C:\Users\londo\.browser-use\mcp-ai2-config.json -> C:\Users\londo\.browser-use\chrome-google-ai2-profile
```

These MCP servers are registered in `C:\Users\londo\.codex\config.toml`.
They expose tools such as:

```text
browser_navigate
browser_click
browser_type
browser_get_state
browser_extract_content
browser_get_html
browser_screenshot
browser_scroll
browser_go_back
browser_list_tabs
browser_switch_tab
browser_close_tab
retry_with_browser_use_agent
browser_list_sessions
browser_close_session
browser_close_all
```

Lifecycle rule: do not use the same Chrome profile through both MCP and the
CDP helper at the same time. If MCP uses `ai1`, do not also run
`start-google-controlled.ps1 ai1` until the MCP browser session is closed.
After MCP work, close sessions with `browser_close_session` or
`browser_close_all`.

The local MCP config intentionally does not attach to the user's `main` browser
profile by default.

### Templates with `init`

`browser-use init` can generate Python starter templates:

```powershell
browser-use init --list
browser-use init --template default --output browser_task.py
browser-use init --template advanced --output browser_task_advanced.py
```

This may need network access to fetch templates. If it fails offline, continue
with a small hand-written script instead of blocking the task.

### Install and Setup Commands

`browser-use install` and `browser-use setup` can install or configure browser
dependencies. They may touch the network and local browser/runtime state.
Ask before running them unless the user explicitly requested setup or repair.

## Cloud API

```bash
browser-use cloud connect                 # Provision cloud browser and connect
browser-use cloud connect --timeout 120 --proxy-country US  # With options
browser-use cloud login <api-key>         # Save API key (or set BROWSER_USE_API_KEY)
browser-use cloud logout                  # Remove API key
browser-use cloud v2 GET /browsers        # REST passthrough (v2 or v3)
browser-use cloud v2 POST /tasks '{"task":"...","url":"..."}'
browser-use cloud v2 poll <task-id>       # Poll task until done
browser-use cloud v2 --help               # Show API endpoints
browser-use cloud v3 GET /browsers        # Newer API version, if available
browser-use cloud v3 POST /tasks '{"task":"Search for AI news","url":"https://google.com"}'
browser-use cloud v3 poll <task-id>
browser-use cloud v3 --help
```

`cloud connect` provisions a cloud browser, connects via CDP, and prints a live URL. `browser-use close` disconnects AND stops the cloud browser.

Cloud usage policy:

- Do not use cloud browsers by default for the user's logged-in personal
  accounts.
- Ask before `cloud login`, `cloud connect`, or creating cloud tasks because it
  can involve API keys, billing, and remote browser state.
- Prefer local controlled profiles (`ai1`, `ai2`) for Gmail, Drive, Google
  account work, ChatGPT, X, and similar personal sessions.
- Use `cloud v3` only when the task explicitly benefits from a disposable remote
  browser or the user asks for Browser-Use Cloud.

## Tunnels

```bash
browser-use tunnel <port>                 # Start Cloudflare tunnel (idempotent)
browser-use tunnel list                   # Show active tunnels
browser-use tunnel stop <port>            # Stop tunnel
browser-use tunnel stop --all             # Stop all tunnels
```

Tunnel usage policy:

- Use tunnels for local web app previews, webhook tests, and remote inspection.
- Do not expose account pages, admin panels, or private local services unless
  the user explicitly asks.
- Always stop tunnels after the task:

```powershell
browser-use tunnel list
browser-use tunnel stop <port>
browser-use tunnel stop --all
```

## Profile Management

```bash
browser-use profile list                  # List detected browsers and profiles
browser-use profile sync --all            # Sync profiles to cloud
browser-use profile update                # Download/update profile-use binary
```

Profile management policy:

- `profile list` is safe and useful for discovery.
- `profile sync --all` can upload/sync browser profile data; ask before using it.
- `profile update` can download/update the profile-use helper; ask before using
  it unless the user requested setup.
- On this Windows machine, local Brave auth should use the CDP workflow below,
  not `browser-use --profile`.

## Command Chaining

Commands can be chained with `&&`. The browser persists via the daemon, so chaining is safe and efficient.

```bash
browser-use open https://example.com && browser-use state
browser-use input 5 "user@example.com" && browser-use input 6 "password" && browser-use click 7
```

Chain when you don't need intermediate output. Run separately when you need to parse `state` to discover indices first.

## Common Workflows

### Authenticated Browsing

When a task requires an authenticated site (GitHub, internal tools), use Chrome profiles:

```bash
browser-use profile list                           # Check available profiles
# Ask the user which profile to use, then:
browser-use --profile "Default" open https://github.com  # Already logged in
```

For Google accounts specifically, prefer the dedicated controlled Chrome
profile workflow below. Google/Chrome can refuse or strip cookies when Browser
Use tries to copy or attach to a normal everyday Chrome profile.

### Authenticated Brave on Windows

The current local CLI `--profile` path is Chrome-only, even when
`browser-use profile list` shows Brave profiles. Do not assume
`browser-use --profile "Brave profile name"` will attach to Brave cookies.

For the user's existing Brave login/cookies, use CDP:

1. Ask permission before closing Brave. Warn that unsaved forms can be lost.
2. Close stale Browser Use sessions:

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use close --all
```

3. Close Brave only after permission, then restart Brave with remote debugging:

```powershell
$brave = Get-Process brave -ErrorAction SilentlyContinue
if ($brave) {
    foreach ($p in $brave) { try { $null = $p.CloseMainWindow() } catch {} }
    Start-Sleep -Seconds 5
    $still = Get-Process brave -ErrorAction SilentlyContinue
    if ($still) { $still | Stop-Process -Force }
    Start-Sleep -Seconds 2
}

$exe = "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe"
Start-Process -FilePath $exe -ArgumentList @(
    "--remote-debugging-port=9222",
    "--profile-directory=Default",
    "--restore-last-session",
    "https://chatgpt.com/"
)
```

4. Confirm the CDP port is listening:

```powershell
Get-NetTCPConnection -LocalPort 9222 -ErrorAction SilentlyContinue
```

5. Connect Browser Use to that real Brave session:

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use --cdp-url http://127.0.0.1:9222 open https://chatgpt.com/
browser-use state
```

6. Verify the account from `browser-use state` by profile/sidebar text before
claiming the login worked.

Passwords, 2FA codes, and sensitive login prompts must be handled by the user
directly in the visible browser window, not in chat.

Cleanup rule: after using the user's real Brave profile through CDP, return
Brave to normal mode unless the user explicitly wants to keep it managed. If
Brave remains open with `--remote-debugging-port=9222`, normal manual Brave
window behavior can feel broken because new windows attach to the managed
process.

```powershell
$brave = Get-Process brave -ErrorAction SilentlyContinue
if ($brave) {
    foreach ($p in $brave) { try { $null = $p.CloseMainWindow() } catch {} }
    Start-Sleep -Seconds 5
    $still = Get-Process brave -ErrorAction SilentlyContinue
    if ($still) { $still | Stop-Process -Force }
    Start-Sleep -Seconds 2
}

$exe = "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe"
Start-Process -FilePath $exe
```

Brave's current default download folder on this machine is `D:\Downloads`.
Files downloaded by helper scripts may be elsewhere, e.g.
`D:\Downloads\Instagram_Downloads\...`, and are not necessarily Brave
downloads.

If a clean temporary Brave window is acceptable, use a separate
`--user-data-dir`, but be explicit that existing site cookies/logins will not
be present.

### Google Account in Controlled Chrome on Windows

For Google/Gmail/Drive with Browser Use, do not try to reuse the user's normal
Chrome `Default` profile unless it is already known to work. On Windows, current
Chrome commonly blocks CDP against the normal profile, and copied profile
cookies may not preserve Google login.

Use dedicated persistent Chrome profiles that Browser Use controls. The user
signs into each needed Google account once in the visible Chrome window.

If the local helper exists, use it first. It starts/reuses the controlled Chrome
profile, avoids duplicate Chrome copies on the same port, and verifies Browser
Use.

Available local slots:

```text
main -> port 9225 -> session google-controlled -> C:\Users\londo\.browser-use\chrome-google-profile
ai1  -> port 9226 -> session google-ai1        -> C:\Users\londo\.browser-use\chrome-google-ai1-profile
ai2  -> port 9227 -> session google-ai2        -> C:\Users\londo\.browser-use\chrome-google-ai2-profile
```

Rule of thumb: keep the user's normal/everyday browser separate. Use `ai1` and
`ai2` for AI work whenever possible; use `main` only when the task explicitly
needs the already-signed-in main Google account.

Normal lifecycle:

1. Start `ai1` or `ai2` only when a task needs Google browser automation.
2. Do the browser task through the matching Browser Use session.
3. Stop the AI slot after the task so no extra Chrome windows stay open.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" main
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" ai1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" ai2
```

Stop commands:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" ai1 -Stop
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" ai2 -Stop
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" stop-ai
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" stop-all-managed
```

`stop-ai` closes only `ai1` and `ai2`. `stop-all-managed` also closes `main`,
but only the managed Browser Use Chrome profiles, not the user's normal Chrome
or Brave windows.

To see status for all slots:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" -List
```

To open a login page for a slot:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.browser-use\start-google-controlled.ps1" ai1 -Login
```

or double-click for the default `main` slot:

```text
C:\Users\londo\.browser-use\start-google-controlled.cmd
```

After that, use:

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use --session google-controlled --cdp-url http://127.0.0.1:9225 state
browser-use --session google-ai1 --cdp-url http://127.0.0.1:9226 state
browser-use --session google-ai2 --cdp-url http://127.0.0.1:9227 state
```

Manual setup, only if the helper is missing:

1. Start a separate visible Chrome profile with CDP:

```powershell
$profileDir = "$env:USERPROFILE\.browser-use\chrome-google-profile"
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

$exe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
Start-Process -FilePath $exe -ArgumentList @(
    "--remote-debugging-port=9225",
    "--user-data-dir=$profileDir",
    "--no-first-run",
    "https://accounts.google.com/ServiceLogin"
)
```

2. Connect Browser Use to the same Chrome window:

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use --session google-controlled --cdp-url http://127.0.0.1:9225 open https://accounts.google.com/ServiceLogin
```

3. The user signs in manually in the visible Chrome window. Do not ask them to
paste passwords or 2FA codes into chat.

4. Verify the login before using it:

```powershell
$env:PYTHONIOENCODING = "utf-8"
browser-use --session google-controlled --cdp-url http://127.0.0.1:9225 state
```

A good verification shows either the Google account name/email and Google apps
such as Drive, Gmail, Docs, Sheets, Calendar, etc., or a Google sign-in page for
a fresh AI slot. Example account seen locally in `main`:
`Сухейль Ганеев / ganeevsukheil@gmail.com`.

For future Google tasks, reuse the same slot. This preserves the Google login
for Browser Use without touching the user's normal everyday Chrome profile or
mixing multiple AI sessions into one cookie jar.

### Connecting to Existing Chrome

```bash
browser-use --connect open https://example.com     # Auto-discovers Chrome's CDP endpoint
```

Requires Chrome with remote debugging enabled. Falls back to probing ports 9222/9229.

### Exposing Local Dev Servers

```bash
browser-use tunnel 3000                            # → https://abc.trycloudflare.com
browser-use open https://abc.trycloudflare.com     # Browse the tunnel
```

## Global Options

| Option | Description |
|--------|-------------|
| `--headed` | Show browser window |
| `--profile [NAME]` | Use real Chrome (bare `--profile` uses "Default") |
| `--connect` | Auto-discover running Chrome via CDP |
| `--cdp-url <url>` | Connect via CDP URL (`http://` or `ws://`) |
| `--session NAME` | Target a named session (default: "default") |
| `--json` | Output as JSON |
| `--mcp` | Run as MCP server via stdin/stdout |

## Tips

1. **Always run `state` first** to see available elements and their indices
2. **Use `--headed` for debugging** to see what the browser is doing
3. **Sessions persist** — browser stays open between commands
4. **CLI aliases**: `bu`, `browser`, and `browseruse` all work

## Troubleshooting

- **Browser won't start?** `browser-use close` then `browser-use --headed open <url>`
- **Element not found?** `browser-use scroll down` then `browser-use state`
- **Run diagnostics:** `browser-use doctor`
- **Windows Unicode error in diagnostics/profile output?** Prefix with `$env:PYTHONIOENCODING = "utf-8"` before running `browser-use doctor` or `browser-use profile list`.
- **Brave profile appears in `profile list`, but `--profile` says unknown profile?** This is expected in the current CLI. Use the CDP Brave workflow above.
- **`browser-use profile` opens a cloud/profile sync prompt?** Treat `profile-use` as cloud sync tooling, not the local Brave control path, unless the user explicitly wants cloud profile sync.

## Cleanup

```bash
browser-use close                         # Close browser session
browser-use tunnel stop --all             # Stop tunnels (if any)
```

