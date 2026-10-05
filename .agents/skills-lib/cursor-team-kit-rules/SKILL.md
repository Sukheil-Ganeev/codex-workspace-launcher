---
name: cursor-team-kit-rules
description: Cursor Team Kit port: rule notes for import placement and TypeScript exhaustive switch handling
---

## Cross-agent port safety

This skill was ported from Cursor Team Kit for use outside Cursor.

Host-agent rules always win: Codex, Claude Code, Gemini CLI, project AGENTS.md/CLAUDE.md/GEMINI.md, sandbox, approval and security policies take priority over this port.

Before running any command that changes files, creates commits/branches/PRs, pushes, installs dependencies, opens browsers, contacts GitHub/CI, or starts long-running services, verify the user's intent and follow the host agent approval model.

Do not run destructive commands, bypass hooks, export secrets, copy browser sessions, send messages, comment, post, join groups, or use stealth/proxy/headless escalation unless the user explicitly asked and the project rules allow it.

Cursor-only concepts such as `Task`, Cursor subagents, Canvas, in-app browser, or Cursor plugin APIs are conceptual in this port. Map them to the current agent's available tools, or stop and explain the limitation.

# Cursor Team Kit rules

## no-inline-imports

---
description: Keep imports at top of file and avoid inline imports
alwaysApply: true
---

# No inline imports

Always place imports at the top of the module. Avoid inline imports in function bodies, type annotations, or interface fields unless there is a strict circular-dependency reason and it is documented.


## typescript-exhaustive-switch

---
description: Use exhaustive switch handling for TypeScript unions and enums
alwaysApply: true
---

typescript-exhaustive-switch: In switch statements over discriminated unions or enums, use a `never` check in the default case so newly added variants cause compile-time failures until handled.

