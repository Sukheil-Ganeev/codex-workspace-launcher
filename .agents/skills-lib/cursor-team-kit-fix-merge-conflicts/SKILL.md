---
name: cursor-team-kit-fix-merge-conflicts
description: Cursor Team Kit port: Resolve merge conflicts non-interactively, validate build and tests, and finalize conflict resolution
---

## Cross-agent port safety

This skill was ported from Cursor Team Kit for use outside Cursor.

Host-agent rules always win: Codex, Claude Code, Gemini CLI, project AGENTS.md/CLAUDE.md/GEMINI.md, sandbox, approval and security policies take priority over this port.

Before running any command that changes files, creates commits/branches/PRs, pushes, installs dependencies, opens browsers, contacts GitHub/CI, or starts long-running services, verify the user's intent and follow the host agent approval model.

Do not run destructive commands, bypass hooks, export secrets, copy browser sessions, send messages, comment, post, join groups, or use stealth/proxy/headless escalation unless the user explicitly asked and the project rules allow it.

Cursor-only concepts such as `Task`, Cursor subagents, Canvas, in-app browser, or Cursor plugin APIs are conceptual in this port. Map them to the current agent's available tools, or stop and explain the limitation.

# Fix merge conflicts

## Trigger

Branch has unresolved merge conflicts and needs a reliable path to a buildable state.

## Workflow

1. Detect all conflicting files from git status and conflict markers.
2. Resolve each conflict with minimal, correctness-first edits.
3. Prefer preserving both sides when safe. Otherwise, choose the variant that compiles and keeps public behavior stable.
4. Regenerate lockfiles with package manager tools instead of hand-editing.
5. Run compile, lint, and relevant tests.
6. Stage resolved files and summarize key decisions.

## Guardrails

- Keep changes minimal and readable.
- Do not leave conflict markers in any file.
- Avoid broad refactors while resolving conflicts.
- Do not push or tag during conflict resolution.

## Output

- Files resolved
- Notable resolution choices
- Build/test outcome
