---
name: adapter-parallel-chat-factory-safe
description: "Use in ticket-project when splitting adapter, parser, source-readiness, proof/spec, or import-readiness work across multiple Codex chats, subagents, branches, or worktrees. Required for 10-chat adapter shell factory work, per-domain adapter batches, outcome collection, coordinator integration, and any parallel parser work where workers must avoid live/raw/master/git conflicts."
---

# Adapter Parallel Chat Factory Safe

## Purpose

Use this skill when adapter work is too large for one chat and must be split across several isolated chats.

Business goal: close the adapter/parser family faster while keeping the owner out of micro-management and keeping risky actions blocked.

## Worker Contract

Each worker must have:

- one assigned domain list;
- one clear business goal;
- one set of allowed files;
- one outcome JSON/CSV namespace;
- no permission to write `master`, confirmed layers, shared imports, shared core code, or git;
- no permission to run live/browser/raw/API/Firecrawl unless a separate yellow window is approved.
- no permission to run `tools\hooks\run_project_hook.ps1` in any mode; shared project hooks belong to the coordinator, not the worker.

For the 2026-06-22 adapter-shell wave, use:

```text
docs/prompts/adapter_shell_chats_20260622/STARTING_PROMPTS.md
docs/prompts/adapter_shell_chats_20260622/chat_01.md ... chat_10.md
```

## Status Vocabulary

Workers must finish every assigned domain with one of these statuses:

- `adapter_works`
- `adapter_preview_ready_from_saved_source`
- `spec_ready`
- `yellow_window_needed`
- `no_public_vector`
- `out_of_scope`
- `error_with_evidence`

Do not accept vague statuses like `maybe`, `needs review`, or `could not do`.

## Worker Verification Boundary

A worker runs only the exact validator named in its prompt. If the coordinator validator has not been created yet, the worker must leave `validation_status=PENDING_COORDINATOR_VALIDATION`. It must not search for a substitute validator and must not run project-wide hooks, documentation refreshes or handoff checks.

## Coordinator Contract

The coordinator does not trust chat summaries alone.

After workers finish:

1. collect outcome files;
2. check every assigned domain has exactly one final status;
3. reject duplicated ownership between chats;
4. rebuild the mass adapter factory;
5. run import dry-run only, not `master`;
6. update owner-facing status and bridge;
7. run language checks and project handoff.

## What To Tell The Owner

Owner-facing messages should stay at business level:

- how many domains moved from shell to useful result;
- how many are ready for import decision;
- how many need yellow windows;
- whether parser family is closer to completion;
- which owner decisions remain real.

Do not fill the owner chat with per-file technical noise unless asked.

## References

Load `references/worker-output-contract.md` when preparing worker prompts or integrating finished worker outputs.
