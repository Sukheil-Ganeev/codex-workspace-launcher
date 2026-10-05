---
name: project-autopilot
description: "Maintain a project's evidence-backed execution loop, knowledge indexes and searchable development state when asked for a project autopilot or continuous engineering. Reuse the project's actual goal, task ledger and working runtime."
---

# Project Autopilot

Support an existing project through a repeatable observe → prioritize → execute
→ verify → review → update-knowledge loop. Preserve the full requested outcome
and account for each explicit capability. A saved plan, index, generated summary
or fixture test is not runtime or semantic acceptance.

## Entry and execution choice

Identify the canonical root, original objective, current main task ledger,
applicable owner decisions, source boundaries, code/data versions and active
writers. Recover accepted results before repeating them. Keep one authoritative
plan; use a requirement coverage ledger when the owner requests all named items.

Honor the current execution choice. `codex-primary-only` means the primary
Codex performs the work and uses deterministic helpers. It does not silently
start Muse, OpenHands agents, nested agents or a new model provider. Preserve
an independent-review queue if a required reviewer is unavailable. When worker
execution is authorized, specify model/effort, resource bounds, file ownership,
versions and acceptance before dispatch; never infer a paid or external scope.

## Work cycle

1. Observe meaningful changes in source/code/task evidence; avoid unchanged
   audits. Inspect the riskiest prerequisite before developing dependent work.
2. Select a useful available task with observable acceptance. Record its input
   fingerprints, scope, gates, resource budget, retry policy and rollback path.
3. Execute in an isolated branch or resource boundary. Keep one writer per
   artifact. Long work needs counters, a live handle, checkpoints and a bounded
   resume; timeout alone is not a failure or permission to duplicate a run.
4. Verify actual behavior, negative cases, source coverage and component
   connections. Record failed attempts unchanged and repairs as new versions.
5. Distinguish self-tested, independent review, operating and accepted states.
   Do not promote a result because a process printed PASS.
6. Update the existing task ledger and affected docs/indexes by content version.
   Continue the next available dependency without micro-confirmations. Stop
   only at completion, a real gate, an owner stop or an execution limitation.

## Knowledge and search routing

For indexing/retrieval work, read [search-contracts.md](references/search-contracts.md).
Treat exact, structural, lexical, vector and graph evidence as complementary.
Return source IDs/paths, spans, time and version; preserve actor/source identity
uncertainty. Use a routing decision appropriate to the question rather than
calling every retriever for every query.

For third-party integration, read [provider-boundaries.md](references/provider-boundaries.md).
OpenHands, OpenViking, Cognee, GraphRAG, LlamaIndex and SCIP are distinct named
requirements when explicitly requested. Account for each. Verify the real
component, upstream revision, license, dependencies and a representative local
example; a custom lookalike or import test does not prove the requested product.
Keep working routes through separate adapters and record unavailable prerequisites.

Project memory stores evidence-backed decisions, source references, task state,
successful/failed strategies and their versions. Raw conversations, credentials
and global native-memory writes require their applicable explicit authority.
Source changes invalidate dependent summaries and indexes; incremental handling
must account for updates, removals, duplicates and rejected/quarantined input.

## Acceptance and continuity

Use separate coverage for the requested corpus, search capabilities, engineering
cycle and operating integration. Every item has evidence or an explicit remaining
condition. A small pilot does not replace full scope. Retain practical budgets,
max retries, stuck detection, protected branches, rollback checkpoints and source
provenance. A CI provider being unavailable does not turn an unrun check into PASS.

Use the product's goal/automation mechanism for recurring work when authorized.
Do not create a second infinite loop or silently install a persistent service.
Stay quiet on unchanged/non-actionable scheduled checks unless periodic updates
were requested. Report progress in the owner's language, then the actual next
action and responsible party. Do not promise background continuation without
an observed execution mechanism.
