---
name: cursor-team-kit-what-did-i-get-done
description: Cursor Team Kit port: Summarize authored commits over a user-specified time period into a concise update
---

## Cross-agent port safety

This skill was ported from Cursor Team Kit for use outside Cursor.

Host-agent rules always win: Codex, Claude Code, Gemini CLI, project AGENTS.md/CLAUDE.md/GEMINI.md, sandbox, approval and security policies take priority over this port.

Before running any command that changes files, creates commits/branches/PRs, pushes, installs dependencies, opens browsers, contacts GitHub/CI, or starts long-running services, verify the user's intent and follow the host agent approval model.

Do not run destructive commands, bypass hooks, export secrets, copy browser sessions, send messages, comment, post, join groups, or use stealth/proxy/headless escalation unless the user explicitly asked and the project rules allow it.

Cursor-only concepts such as `Task`, Cursor subagents, Canvas, in-app browser, or Cursor plugin APIs are conceptual in this port. Map them to the current agent's available tools, or stop and explain the limitation.

# What did I get done

## Trigger

Need a short, high-signal summary of work completed in a specific time range (for example: yesterday, last 3 days, or last week).

## Workflow

1. Resolve the requested time window into concrete dates.
2. Read commits authored by the current git user email within that range.
3. Exclude merge commits and uncommitted changes.
4. Synthesize the most important shipped changes into a concise status update.
5. Include the actual date range used in the final summary.

## Guardrails

- Be extremely concise and information-dense.
- Prioritize substantial behavior or architecture changes.
- Omit cosmetic-only changes (formatting, imports, minor renames).
- Do not infer intent or motivation. Describe changes functionally.

## Output

- One short summary suitable for a status update
- Real date range
- Optional 2-5 bullets for major changes only
