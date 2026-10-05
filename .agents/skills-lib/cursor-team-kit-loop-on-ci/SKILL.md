---
name: cursor-team-kit-loop-on-ci
description: Cursor Team Kit port: Monitor PR checks and fix failures until green. Uses gh pr checks as the source of truth for PR-attached checks.
---

## Cross-agent port safety

This skill was ported from Cursor Team Kit for use outside Cursor.

Host-agent rules always win: Codex, Claude Code, Gemini CLI, project AGENTS.md/CLAUDE.md/GEMINI.md, sandbox, approval and security policies take priority over this port.

Before running any command that changes files, creates commits/branches/PRs, pushes, installs dependencies, opens browsers, contacts GitHub/CI, or starts long-running services, verify the user's intent and follow the host agent approval model.

Do not run destructive commands, bypass hooks, export secrets, copy browser sessions, send messages, comment, post, join groups, or use stealth/proxy/headless escalation unless the user explicitly asked and the project rules allow it.

Cursor-only concepts such as `Task`, Cursor subagents, Canvas, in-app browser, or Cursor plugin APIs are conceptual in this port. Map them to the current agent's available tools, or stop and explain the limitation.

# Loop on CI

## Trigger

Need to watch a branch or pull request and iterate on CI failures until all required checks are green.

Use `gh pr checks` as the source of truth. It includes all PR-attached checks, while `gh run list` only covers GitHub Actions.

## Workflow

1. Resolve the PR for the current branch.
2. Inspect current PR checks before waiting.
3. If checks already failed, diagnose those failures first.
4. If checks are pending, watch with `gh pr checks --watch --fail-fast`.
5. After each push, re-check the full PR check set and repeat until green.

## Commands

```bash
# Resolve the active PR
gh pr view --json number,url,headRefName

# Inspect all attached checks
gh pr checks --json name,bucket,state,workflow,link

# Watch pending checks and fail fast
gh pr checks --watch --fail-fast

# GitHub Actions logs, when the failing check links to a GHA run
gh run view <run-id> --log-failed
```

## Guardrails

- Keep each fix scoped to a single failure cause when possible.
- Do not bypass hooks (`--no-verify`) to force progress.
- If the failure is clearly unrelated to the PR and appears fixed on main, merge latest main instead of bloating the PR with unrelated fixes.
- If failures are flaky, retry once and report flake evidence.
- Re-run `gh pr checks --json name,bucket,state,workflow,link` after every push; the check set can change.

## Output

- Current CI status
- Failure summary and fixes applied
- PR URL once checks are green
