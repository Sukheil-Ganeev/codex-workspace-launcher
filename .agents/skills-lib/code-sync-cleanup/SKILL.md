---
name: code-sync-cleanup
description: "Finds and fixes divergences between code and documentation, cross-file inconsistencies, and duplicate logic. Use when docs feel stale, code contradicts docs, or duplicate logic exists across files."
---
# Code Sync & Cleanup

## Overview

Code Sync & Cleanup finds and resolves four categories of technical debt that accumulate silently as codebases evolve:

1. **Drift** — documentation that no longer matches the code
2. **Shadow** — code that exists but is completely undocumented
3. **Duplication** — identical or near-identical logic scattered across files
4. **Inconsistency** — related files that contradict each other (naming, behavior, contracts)

The skill operates in four focused modes. Each mode produces a structured report with severity codes and concrete actions — never vague observations.

---

## When to Use

| Situation | Mode |
|-----------|------|
| Docs reference old function names, removed tables, wrong params | `drift` |
| New features were shipped but nothing was written | `drift` |
| Suspicion that two modules do the same thing | `cross-file` |
| Multiple handlers have copy-pasted validation logic | `cross-file` |
| CHANGELOG/CLAUDE.md contradicts actual source files | `sync` |
| Pre-PR quality pass across a feature branch | `review` |
| Full codebase health check | `drift` + `cross-file` combined |

---

## Modes

### drift — Find Code/Docs Divergence

Detect every place where documentation describes something the code no longer does (or never did).

**What to scan:**
- Function/method signatures vs. docstrings and inline comments
- Database table/column names in docs vs. actual schema migrations
- API endpoint paths in docs vs. route definitions
- Environment variable names in README/.env.example vs. config files
- Version numbers and changelog entries vs. git history or package.json
- Architecture diagrams or description prose vs. actual directory structure
- Removed features still described as "available"

**Step-by-step:**
1. List all documentation files (*.md, docstrings, comments, CLAUDE.md, README)
2. Extract every claim: function names, table names, endpoints, env vars, module paths
3. For each claim — verify against the actual source file it references
4. Classify each finding:
   - `STALE` — doc describes something that was changed/removed
   - `GHOST` — doc references a symbol that no longer exists anywhere
   - `SHADOW` — code exists with no corresponding documentation at all
   - `MISMATCH` — doc describes correct intent but wrong detail (wrong param name, wrong default)
5. Output drift report (see Output Format)

**Severity assignment:**

| Severity | Meaning |
|----------|---------|
| CRITICAL | Leads someone to use wrong API, wrong table, wrong auth flow |
| HIGH | Significant confusion; will waste developer time |
| MEDIUM | Misleading but survivable with source inspection |
| LOW | Cosmetic — old name, stale example value |

**Example output line:**
```
DRIFT-03 | docs/API.md:47 | References endpoint /api/v1/blocks | Actual: /api/v2/blocks since migration v18 | Severity: HIGH
```

---

### sync — Update Docs to Match Code

Takes the output of `drift` and produces concrete documentation patches.

**Rules:**
- Never invent intent — only document what the code demonstrably does
- Prefer removing stale content over rewriting speculatively
- When a function changed behavior, describe the new behavior with one concrete example
- For database schema: read the latest migration file, not the oldest
- Mark anything uncertain as `[VERIFY]` — do not silently guess

**Step-by-step:**
1. Run or import a `drift` report
2. For each STALE/GHOST finding — propose a minimal diff to the doc file
3. For each SHADOW finding — generate a short description block to insert
4. For MISMATCH — generate a targeted in-place correction
5. Group all changes by target file, show before/after diff
6. Require confirmation before writing — show total file count and line delta

**Minimum doc block for a SHADOW function:**
```
#### function_name(param1, param2)
What it does: [one sentence]
Returns: [type and meaning]
Side effects: [DB write / external call / none]
Example: [concrete call + return value]
```

---

### cross-file — Find Cross-File Issues

Finds duplicated logic, conflicting contracts, and inconsistent naming across related files.

**What to look for:**

**Duplication patterns:**
- Same validation logic copy-pasted into multiple handlers
- Identical SQL query fragments in more than one service
- Repeated error-formatting code (should be a shared helper)
- Multiple files defining the same constant with the same or different value
- Test fixtures duplicated between test files instead of being shared

**Inconsistency patterns:**
- Function A calls `get_user(user_id)`, function B calls `fetch_user(uid)` — same underlying operation, different naming
- Module A imports `from config import DATABASE_URL`, module B hardcodes the default
- Handler X returns `{"status": "ok"}`, handler Y returns `{"success": True}` — no canonical shape
- One file uses `$1/$2` asyncpg placeholders, another uses `?` SQLite-style
- Two formatters doing the same escaping independently

**Dependency graph checks (for monorepos or multi-package projects):**
- Circular imports
- Packages importing from each other's private internals
- Version mismatches for the same dependency across packages

**Step-by-step:**
1. Map the file set: group by layer (handlers / services / data / tests / config)
2. For each layer — scan for duplicated blocks (>5 identical or near-identical lines)
3. For cross-layer calls — verify the contract at each call site matches the definition
4. Check naming consistency: same operation should use the same verb and noun everywhere
5. Output cross-file report (see Output Format)

**Duplication codes:**
```
DUP-XX | [file A]:[line] ↔ [file B]:[line] | [what is duplicated] | Severity: HIGH/MEDIUM/LOW
```

**Inconsistency codes:**
```
INC-XX | [file A] vs [file B] | [what conflicts] | Impact: [who breaks if left unfixed]
```

**Refactor recommendation format:**
```
DUP-02 → REFACTOR: Extract to bot/services/user_helpers.py::validate_phone()
         Move: bot/handlers/booking.py:134, bot/handlers/profile.py:89
         Effort: ~20 min
```

---

### review — Quality & Consistency Check

A structured pre-PR or pre-deploy pass combining drift detection, cross-file checks, and a focused code quality scan.

**Review dimensions (in priority order):**

1. **Correctness** — logic errors, wrong conditionals, off-by-one, null/None not handled
2. **Security** — injection paths, missing auth checks, hardcoded secrets, unsafe deserialization
3. **Async safety** — missing await, shared mutable state across coroutines, unhandled exceptions in tasks
4. **Performance** — N+1 queries, missing indexes referenced in code, synchronous blocking calls in async context
5. **Error handling** — bare `except:`, swallowed exceptions, missing fallback for external API failures
6. **Naming & contracts** — function does what its name says, return type matches annotation
7. **Test coverage** — happy path only? edge cases missing? mocks hiding real behavior?

**Process:**
1. State the purpose of the code being reviewed in one sentence before proceeding — if unclear, ask
2. Check each dimension against the files provided
3. Classify each finding: CRITICAL / HIGH / MEDIUM / LOW
4. For each CRITICAL or HIGH finding — provide a concrete fix, not just a description of the problem
5. Explicitly call out what was checked and what was not (scope boundary)
6. End with a verdict: APPROVE / REQUEST CHANGES / COMMENT ONLY

**Do not flag:**
- Pure style preferences when a linter/formatter handles it
- Naming choices that are internally consistent even if unconventional
- Patterns that are project-standard (verify against CLAUDE.md before flagging)

**Verdict criteria:**

| Verdict | Condition |
|---------|-----------|
| APPROVE | No CRITICAL/HIGH; MEDIUM findings noted but non-blocking |
| REQUEST CHANGES | Any CRITICAL finding, or 3+ HIGH findings |
| COMMENT ONLY | 1-2 HIGH findings with clear low-effort fixes; author's call |

---

## Output Format

### Drift Report
```
## Drift Report — [project/path] — [date]

Total findings: N  (CRITICAL: X | HIGH: Y | MEDIUM: Z | LOW: W)

### CRITICAL
DRIFT-01 | [doc file]:[line] | [claim] | [reality] | Action: [delete/update/add]

### HIGH
DRIFT-02 | ...

### Sync plan
Files to change: N
Net line delta: +X / -Y
[Confirm before applying]
```

### Cross-File Report
```
## Cross-File Report — [path] — [date]

Duplications: N  |  Inconsistencies: M

### Duplications
DUP-01 | [file A]:[line] ↔ [file B]:[line] | [description] | Severity: HIGH
  → Refactor: [specific action]

### Inconsistencies
INC-01 | [file A] vs [file B] | [conflict] | Impact: [description]
  → Fix: [specific action]
```

### Review Report
```
## Review — [scope] — [date]
Intent: [one sentence]
Files reviewed: [list]
Files NOT reviewed: [list]

### CRITICAL
[finding with fix]

### HIGH
[finding with fix]

### MEDIUM / LOW
[findings, brief]

### Positive
[what is done well — required, not optional]

Verdict: APPROVE / REQUEST CHANGES / COMMENT ONLY
```

---

## Quick Reference

```
drift     → find what docs say that code no longer does
sync      → fix the docs based on drift findings
cross-file → find duplicated logic and conflicting contracts
review    → full pre-PR quality pass
```

**Severity shortcuts:**
- CRITICAL = wrong behavior if followed, security hole, data loss risk
- HIGH = significant confusion or wasted time
- MEDIUM = misleading but survivable
- LOW = cosmetic

**Code prefixes:**
- `DRIFT-XX` — documentation divergence
- `DUP-XX` — duplicated logic
- `INC-XX` — inconsistency between files
- `REVIEW-XX` — code quality finding

---

## Common Mistakes

**In drift mode:**
- Reading only the latest doc and assuming earlier sections are current — scan all sections
- Flagging intentional aliases as GHOST — check git log before declaring something removed
- Marking a feature SHADOW just because it has no .md file — inline docstrings count

**In sync mode:**
- Rewriting a doc to match what you *think* the code should do — only document what it *does*
- Silently deleting an entire section because one claim was stale — fix the claim, not the section
- Forgetting to update cross-references when you rename something

**In cross-file mode:**
- Flagging intentional platform-specific variants as duplication — check if the difference is meaningful
- Missing duplication because variable names differ — look at structure, not just text
- Proposing a shared helper that would require circular imports to use

**In review mode:**
- Starting the review without understanding intent — always state the purpose first
- Flagging project conventions as bugs — read CLAUDE.md before reviewing
- Listing 20 LOW findings and 0 positives — that is not a review, it is a complaint
- Giving REQUEST CHANGES for only MEDIUM findings — calibrate to severity table

---

## Sources

This skill synthesizes:
- **jeffallan/claude-skills code-reviewer** (v1.1.0, MIT) — review dimensions, severity framework, verdict criteria, positive-feedback requirement
- **TerminalSkills/skills code-reviewer** (v1.0.0, Apache-2.0) — six-dimension checklist, concrete fix requirement, scope boundary declaration
- **TerminalSkills/skills monorepo-manager** (Apache-2.0) — dependency graph analysis, version consistency checks, circular import detection
- **Original authorship** — drift/sync/cross-file mode design, DRIFT-XX/DUP-XX/INC-XX coding system, output format templates, Common Mistakes section
