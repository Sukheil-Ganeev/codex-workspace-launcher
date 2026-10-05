---
name: codex-worktree-orchestration-safe
description: "Use in ticket-project before creating, forking, handing off, inspecting, merging, or cleaning Codex worktree threads, git worktrees, branches, or parallel agent branches. Required for 10-chat adapter factory launches, background Codex threads, worktree isolation, branch fan-out, merge-back planning, config.lock/index.lock errors, and any workflow where multiple agents may touch the same repository."
---

# Codex Worktree Orchestration Safe

## Purpose

Use this skill before launching Codex worktree chats or branch-based parallel work.

Business goal: increase adapter throughput without corrupting the shared workspace, losing untracked prompt files, or making agents overwrite each other.

## Non-Negotiables

- Prefer Codex native worktree/thread tools over manual `git worktree add`.
- Never create many worktrees at the same second; serialize creation and verify each result.
- Start with one test worktree/thread before launching a wave.
- Do not use `startingState: branch` unless the branch already exists and contains the prompt files the worker must read.
- If prompt files are untracked in the main checkout, either use a `working-tree` start or paste the full prompt into the worker.
- Do not run `git add .`, commit, merge, push, delete branches, or remove worktrees without an explicit owner decision.
- If `.git/config.lock` or `.git/index.lock` exists, stop and diagnose; do not remove locks blindly.
- Every worker must write only to its assigned outcome files or branch/worktree.
- After workers finish, coordinate integration from a clean coordinator pass, not from worker chats.

## Preflight

Before a launch, run:

```bash
python3 .agents/skills/codex-worktree-orchestration-safe/scripts/worktree_preflight.py --adapter-shell
```

Use the result:

- `PASS`: one test thread may be started.
- `WARN`: read the warning and fix before a multi-chat wave.
- `FAIL`: do not launch worktree chats.

## Launch Order

1. Read `docs/handoffs/LATEST_CROSS_AGENT_CONTEXT.md`.
2. Run the preflight script.
3. Confirm the relevant prompt files exist.
4. Launch one test worktree/thread.
5. Verify that the thread exists, the worktree exists, and it can read its prompt.
6. Launch the rest sequentially, with a short wait/check between starts.
7. Record pending thread/worktree IDs in a coordination note.
8. When workers finish, collect only their outcome artifacts.
9. Run the project validators and full handoff.

## Failure Handling

If a thread reports initialization failure:

- check `git worktree list --porcelain`;
- check `git branch --list 'codex/adapter-shell-chat-*'`;
- check `.git/config.lock` and `.git/index.lock`;
- check whether the start used `branch` while the branch did not exist;
- check whether the worker needed untracked prompt files that were not present in its checkout;
- do not launch more workers until the cause is recorded.

## Tooling Policy

External MCP/CLI tools for worktrees are allowed only as reviewed candidates until the owner chooses to enable them.

Current default for ticket-project:

- use native Codex app worktree tools first;
- use manual `git worktree` only as fallback;
- keep GitHub/MCP/CLI worktree managers documented, but not active by default.

## References

Load these only when needed:

- `references/worktree-tooling-research.md` for evaluated GitHub/MCP/CLI tools.
- `references/launch-checklist.md` for the 10-chat adapter launch checklist.
