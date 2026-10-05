---
name: project-autopilot
description: Coordinate long-running, evidence-backed project improvement across data, code, search, agents and quality. Use when the owner requests continuous work or a project brain/autopilot; do not route an ordinary one-file edit here.
---

# Project Autopilot

Run one durable project objective through repeated **observe → choose → execute → verify → update** cycles. The project and the owner's current request define completion. A scan or a worker's `success` is never project acceptance.

For a project with an installed controller, run its read-only scanner and inspect the resulting facts, open work, live process handles and independent review. The Marsel project adapter is in [references/marsel.md](references/marsel.md). If a project lacks a controller, create a bounded one from its actual artifacts before automating dispatch. Keep a single coordinator and one writer per mutable output.

1. **Observe:** pin the current files, source versions, process handles, resource limits and existing work. Check whether a worker is actually live before restart. Treat unknown/partial states as unknown, not complete or dead.
2. **Prioritize:** compare current evidence with the full owner objective. Add missing work to a durable, deduplicated backlog. Prefer useful dependent work; do independent tasks in parallel. Do not narrow the objective to a passing pilot.
3. **Plan models and access:** use the owner's already approved model/reasoning set. For Marsel, the owner requested Luna high or higher for subagents and Fast Mode where the host exposes it. Do not claim a toggle is active when it is unavailable. Keep Marsel data separate from other family projects, and protect `data/` as read-only.
4. **Execute:** issue clear ownership of files, source scope, expected output and acceptance tests. Use versioned/isolated outputs. Existing Muse/Command Code/codex-report-delivery adapters can provide durable external work and reports; native subagents are allowed when the owner explicitly requested them. Never create a second writer or blind retry an ambiguous run.
5. **Verify:** independently check output hashes, meaningful test cases, source links, semantic limits, resource use and negative cases. Failed checks return to the author with a concrete defect. For UI or CLI deliverables, apply the owner's recording rules. Do not promote a hypothesis, unknown contact or historical price into confirmed seller knowledge by schema alone.
6. **Update:** record decisions, defects, accepted artifacts, provenance, quality limits and next work. Refresh search/graph indexes after source changes. Run the scan again while useful authorized work remains; a timer or report notification should be quiet if state has not changed.

**Execution backends are optional adapters, not assumed installations.** Evaluate OpenHands, OpenViking, Cognee, GraphRAG and LlamaIndex on a bounded source set before importing private archives or adding their own model providers. Read [references/backend-evaluation.md](references/backend-evaluation.md) for gates. The user chose the current Codex model for semantic reading; numeric embedding vectors are not available from this chat interface, so never label its reasoning output an embedding index.

A task can be marked accepted only against its exact objective and scope, with immutable evidence and independent review. A complete project claim requires a requirement-by-requirement audit against the original full goal. Preserve the owner's existing approval; ask again only for a genuinely new irreversible, paid or production action outside that scope.

## Existing cross-host guidance

The ufc333 installation already contained a broader, independently authored [Project Autopilot skill](references/ufc333-existing-skill.md). Its existing guidance is preserved as a reference, including [provider boundaries](references/provider-boundaries.md) and [search contracts](references/search-contracts.md). Read those before integrating an external backend or claiming a new search mode. The owner's explicit instruction for this task to use Luna subagents controls this run even where the reference describes a different execution mode. Keep local project behavior in [Marsel adapter](references/marsel.md).
