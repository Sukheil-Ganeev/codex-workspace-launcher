# Worktree Tooling Research

Checked on 2026-06-22.

## Recommended Default

Use Codex native worktree/thread tools first. They know about Codex-managed worktrees and avoid phantom state.

## Useful Sources

- OpenAI Codex app worktrees: official source for Codex-managed worktrees.
- OpenAI Codex local environments: official source for setup scripts and worktree setup behavior.
- `obra/superpowers` `using-git-worktrees`: best reusable skill pattern.
- Git official `git worktree` docs: primary Git behavior reference.
- GitHub issue `anthropics/claude-code#34645`: documents `.git/config.lock` contention when many worktrees start at once.
- `broskees/worktree-mcp`: MCP lifecycle idea, not enabled by default.
- `ben-rogerson/git-worktree-toolbox`: MCP plus CLI candidate, not enabled by default.
- `cyanheads/git-mcp-server`: broad Git MCP candidate, powerful and therefore not enabled by default.
- `max-sixty/worktrunk`: popular CLI candidate for AI-agent worktrees, not enabled by default.

## Project Decision

Do not install active external git/worktree MCP servers into the project by default.

Reason: they can create branches, move worktrees, inspect changes, and sometimes commit/push. For this project, the safe default is a local skill plus preflight validator. External MCP/CLI can be enabled later only if native Codex worktrees remain unreliable after the guarded launch.
