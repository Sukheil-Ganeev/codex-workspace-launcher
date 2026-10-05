---
name: cursor-team-kit-weekly-review
description: Cursor Team Kit port: Produce a weekly synthesis of authored commits with highlights by bugfix, tech debt, and net-new work
---

## Cross-agent port safety

This skill was ported from Cursor Team Kit for use outside Cursor.

Host-agent rules always win: Codex, Claude Code, Gemini CLI, project AGENTS.md/CLAUDE.md/GEMINI.md, sandbox, approval and security policies take priority over this port.

Before running any command that changes files, creates commits/branches/PRs, pushes, installs dependencies, opens browsers, contacts GitHub/CI, or starts long-running services, verify the user's intent and follow the host agent approval model.

Do not run destructive commands, bypass hooks, export secrets, copy browser sessions, send messages, comment, post, join groups, or use stealth/proxy/headless escalation unless the user explicitly asked and the project rules allow it.

Cursor-only concepts such as `Task`, Cursor subagents, Canvas, in-app browser, or Cursor plugin APIs are conceptual in this port. Map them to the current agent's available tools, or stop and explain the limitation.

# Weekly review

## Trigger

Need a weekly recap of shipped work for status updates, retros, or planning.

## Workflow

1. Determine the current git user email from repo config.
2. Collect authored commits from the last 7-10 days on the primary branch context.
3. Exclude merge commits.
4. Group meaningful changes into 2-5 concise bullets.
5. Add a short classification paragraph covering:
   - likely bug fixes
   - likely tech debt work
   - likely net-new functionality

## Guardrails

- Keep the recap short and executive-readable.
- Base claims only on commit history and diffs.
- If git email is missing, ask the user to set it before proceeding.

## Output

- 2-5 bullet weekly summary
- Brief classification paragraph (bugfix / tech debt / net-new)
