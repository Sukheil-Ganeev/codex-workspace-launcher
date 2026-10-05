---
name: spec-driven-dev
description: "Skill spec-driven-dev"
license: Apache-2.0
compatibility: "Any AI coding agent. No dependencies."
metadata:
---
# Spec-Driven Development

## Overview

Most AI coding failures happen because the agent starts coding before understanding the problem. Spec-driven development reverses the flow:

```
User Request → Extract Requirements → Write Spec → Validate Spec → Implement → Verify Against Spec
                                           ↑                |
                                           └── Revise ──────┘
```

30 minutes of planning saves 3 hours of wrong implementation. The spec becomes the contract, the test oracle, and the team communication artifact.

## When to Use

- Starting a new feature and want to think before coding
- Building something complex where wrong assumptions are expensive
- Working in a team where others need to review the design before implementation
- The agent keeps building the wrong thing because requirements are ambiguous
- Creating RFCs or Architecture Decision Records (ADRs) for the team
- A vague request like "make it better" needs to be turned into real tasks

## When NOT to Use

- Trivial one-liner fixes (typo, rename, single value change)
- Hotfixes where speed matters more than design
- Throwaway scripts or one-off migrations with no future use
- When the spec already exists and has been approved — just implement

---

## Modes

### mode: spec — Write Specification First

Use for new features, integrations, or any work where the "what" is unclear.

**Step 1: Extract Requirements**

Turn vague language into structured, testable requirements using MoSCoW priority:

| Priority | Meaning |
|----------|---------|
| Must | Non-negotiable. Feature fails without this. |
| Should | High value, ship if possible, not a blocker. |
| Could | Nice to have, only if time allows. |
| Won't | Explicitly out of scope for this iteration. |

Rule: "Fast", "Secure", "Scalable" are NOT requirements. Measurable criteria are:
- "Fast" → "API responds in <300ms at p95 under 1000 concurrent users"
- "Secure" → "All endpoints require JWT auth; tokens expire in 15 min"
- "Scalable" → "Handles 10x current load without architecture change"

**Step 2: Technical Spec Template**

```markdown
# Technical Spec: [Feature Name]

**Status:** Draft | In Review | Approved | Implemented
**Author:** [name]
**Date:** [YYYY-MM-DD]
**Approvers:** [names]

---

## 1. Overview
One paragraph: what we're building and why, in plain language.

## 2. Goals & Non-Goals

### Goals
- [Specific, measurable outcome]
- [Specific, measurable outcome]

### Non-Goals (explicitly excluded)
- [Thing we are NOT building]
- [Scope we are deferring to later]

## 3. Background & Context
Why now? What is the current state? What problem does this solve?

## 4. Technical Design

### 4.1 Architecture
High-level diagram or description: components, data flow, integrations.

### 4.2 Data Model
Database tables, API types, key data structures with field names and types.

### 4.3 API / Interface Design
Endpoints or function signatures, request/response types, error handling.

### 4.4 Key Algorithms & Logic
Non-obvious decisions: state machines, ranking logic, caching strategy.

## 5. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Option A (chosen) | ... | ... | Chosen because... |
| Option B | ... | ... | Rejected because... |

## 6. Implementation Plan

### Phase 1: [Name] — estimated Xh
- [ ] Task 1 (files: ...)
- [ ] Task 2 (files: ...)

### Phase 2: [Name] — estimated Xh
- [ ] Task 3 (files: ...)

## 7. Testing Strategy
- Unit tests: [what logic to cover]
- Integration tests: [what flows to cover]
- E2E tests: [what user paths to cover]
- Performance benchmarks: [what to measure]

## 8. Rollout Plan
- Feature flag: [flag name]
- Rollout stages: internal → 5% → 25% → 100%
- Rollback trigger: [metric] drops below [threshold]
- Migration notes: [any DB migration or data backfill needed]

## 9. Security & Privacy Considerations
- Auth requirements
- Data sensitivity
- Rate limiting needs

## 10. Open Questions
- [ ] [Question that blocks design decision]
- [ ] [Question that changes scope]

## 11. References
- [Related RFC, ADR, or design doc]
- [External documentation or API reference]
```

---

### mode: adr — Architecture Decision Record

Use when making a significant technical choice that the team needs to understand and agree on. ADRs are lightweight, permanent records — once written and accepted, they should not be deleted (only superseded).

**When to write an ADR:**
- Choosing between two technologies, frameworks, or approaches
- Deciding on a data model pattern
- Choosing an authentication strategy
- Any decision where "why did we do it this way?" will come up in 6 months

**ADR Template:**

```markdown
# ADR-[NNN]: [Short title of decision]

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-[NNN]
**Date:** [YYYY-MM-DD]
**Deciders:** [people who made or approved this decision]

---

## Context

What is the situation that requires a decision? What forces are at play?
What constraints (technical, time, cost) are relevant?

(Write this section as if the reader has no context — future you in 6 months.)

## Decision

What we decided to do, stated clearly and without justification yet.

> We will use [X] for [purpose].

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative / Trade-offs
- [Downside or cost accepted]
- [Limitation we live with]

### Neutral
- [Side effects that are neither good nor bad]

## Alternatives Considered

### Option A: [name]
- Description: ...
- Pros: ...
- Cons: ...
- Rejected because: ...

### Option B: [name]
- Description: ...
- Pros: ...
- Cons: ...
- Rejected because: ...

## References
- [Link to related doc, PR, issue, or external resource]
```

**ADR Example — Choosing PostgreSQL over MongoDB:**

```markdown
# ADR-001: Use PostgreSQL as primary database

**Status:** Accepted
**Date:** 2026-03-12
**Deciders:** Sukheil, backend team

## Context
We need a primary database for the catalog bot. The data includes bookings,
users, loyalty points, and a product catalog. The team has more SQL experience
than NoSQL. Relational integrity matters (bookings reference blocks and users).

## Decision
We will use PostgreSQL via asyncpg for all persistent data.

## Consequences
### Positive
- Strong relational integrity with FK constraints
- Team already knows SQL
- Mature ecosystem (migrations, backups, monitoring)
- asyncpg gives high async performance

### Negative / Trade-offs
- Schema changes require migrations (more friction than schemaless)
- Slightly more setup than SQLite for local dev

## Alternatives Considered

### MongoDB
- Pros: flexible schema, easy horizontal scaling
- Cons: team unfamiliar, no joins, eventual consistency issues for bookings
- Rejected: team SQL fluency + relational data structure outweigh flexibility benefit

### SQLite
- Pros: zero setup, file-based
- Cons: no concurrent writes, not suitable for production with multiple services
- Rejected: production multi-service architecture requires a real DB server
```

---

### mode: rfc — Request for Comments

Use for large changes that affect multiple teams, break backwards compatibility, or require organizational buy-in before work starts. RFCs are living documents during the comment period.

**RFC Template:**

```markdown
# RFC-[NNN]: [Descriptive title]

**Status:** Draft | Open for Comments | Final Comment Period | Accepted | Rejected | Withdrawn
**Author:** [name]
**Created:** [YYYY-MM-DD]
**Comment deadline:** [YYYY-MM-DD]
**Tracking issue:** [link]

---

## Summary
Two-sentence TL;DR. What are we changing and why?

## Motivation
What problem does this solve? Why is the status quo unacceptable?
Include metrics if available (e.g., "currently 40% of support tickets are X").

## Detailed Design
The full technical proposal. Be specific enough that someone could implement
this RFC without asking follow-up questions.

Include:
- Interface changes (API, DB schema, config)
- Behavioural changes (what changes for users, callers, downstream systems)
- Migration path from current to proposed state

## Drawbacks
Why should we NOT do this? What are the costs?
Be honest — a good RFC acknowledges real downsides.

## Alternatives
What other approaches were considered? Why were they rejected?

## Unresolved Questions
- [Question 1 — must be answered before accepting]
- [Question 2 — can be resolved during implementation]

## Future Possibilities
What could this enable later? What is deliberately out of scope now?
```

---

### mode: validate — Validate Idea Before Building

Use when someone brings a vague idea. Answer these 5 questions before writing a single line of code:

```
1. PROBLEM
   What exact problem does this solve?
   Who has this problem, and how often?
   What happens today when they hit this problem?

2. SCOPE
   What is the minimum version that solves the core problem?
   What can we cut without losing the essential value?
   What is explicitly NOT included?

3. DEPENDENCIES
   What does this depend on that doesn't exist yet?
   What other systems does this touch or break?
   Who else needs to approve or be aware?

4. VERIFICATION
   How will we know this works?
   What does "done" look like — the acceptance criteria?
   How will we measure success after launch?

5. RISK
   What is the most likely way this goes wrong?
   What is the impact if it fails in production?
   Do we have a rollback plan?
```

If any answer is "I don't know" — resolve it before designing. Unanswered questions become bugs.

---

### mode: breakdown — Convert Spec to Tasks

Use after a spec is written and approved. Converts spec sections into concrete, orderable implementation tasks.

**Rules for good tasks:**
- Each task takes 15–60 minutes (not "build the auth system")
- Each task has exactly one output you can verify
- Tasks are ordered by dependency (data model before API before UI)
- Each task maps back to a specific spec section

**Breakdown Template:**

```
TASK-001 [spec: §4.2 Data Model]
  Description: Create users table migration
  Files: prisma/schema.prisma, prisma/migrations/
  Output: migration runs cleanly, table exists with correct columns
  Depends on: nothing
  Estimate: 20 min

TASK-002 [spec: §4.3 API Design]
  Description: Implement POST /users endpoint
  Files: src/routes/users.ts, src/types/user.ts
  Output: endpoint accepts valid payload, rejects invalid, returns 201
  Depends on: TASK-001
  Estimate: 30 min

TASK-003 [spec: §7 Testing Strategy]
  Description: Unit tests for user creation logic
  Files: tests/users.test.ts
  Output: all acceptance criteria from spec §4.3 covered by tests
  Depends on: TASK-002
  Estimate: 25 min
```

**Standard implementation order (most features):**
1. DB schema / migrations
2. Core types and interfaces
3. Data access layer / repository
4. Business logic / service layer
5. API / handler layer
6. Tests (unit → integration → E2E)
7. Docs / changelog update

---

## Quick Reference

| Mode | Trigger phrase | Output |
|------|----------------|--------|
| `spec` | "write a spec first", "plan before coding" | Full technical spec markdown |
| `adr` | "architecture decision", "document why we chose X" | ADR markdown file |
| `rfc` | "RFC", "needs team review", "breaking change proposal" | RFC markdown file |
| `validate` | "is this a good idea?", "should we build this?" | 5-question validation checklist |
| `breakdown` | "break this into tasks", "give me the implementation plan" | Ordered task list |

---

## Common Mistakes

1. **Writing code before spec is approved** — the most expensive mistake. Get sign-off first.
2. **Spec without acceptance criteria** — "works correctly" is not testable. Every requirement needs a pass/fail condition.
3. **Treating non-goals as optional** — non-goals prevent scope creep. State them explicitly or they become implicit requirements.
4. **Leaving open questions open** — unresolved questions become bugs or rework. Block until answered.
5. **Never updating the spec** — when implementation diverges, update the spec. Stale specs are worse than no specs.
6. **Over-engineering the document** — time-box spec writing: 30–60 min for a feature, not a day.
7. **Vague alternatives section** — "we considered option B but went with A" is useless. Say *why*.
8. **ADR without consequences** — the most valuable part of an ADR is the trade-offs accepted. Always fill it in.

---

## References

- Original SKILL.md: https://github.com/TerminalSkills/skills/blob/main/skills/spec-driven-dev/SKILL.md (Apache-2.0)
- ADR format inspired by: https://adr.github.io/
- MoSCoW method: https://en.wikipedia.org/wiki/MoSCoW_method
- RFC process inspiration: Rust RFC process (https://github.com/rust-lang/rfcs)

**Source size:** 11,227 bytes (original) + local extensions
**Skill version:** 1.1.0 (based on TerminalSkills v1.0.0 + ADR/RFC/validate/breakdown modes added)
