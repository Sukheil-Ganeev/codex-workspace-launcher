# Phase 4: SYNC -- Detailed Reference

**Goal:** After code refactoring (Phases 1-3), documentation is guaranteed to reflect the new structure. No stale paths, no duplicates, no dead files.

**Methodology sources:** doc-ops (audit/clean/score), docs-optimizer (anti-patterns, tier table, DUP codes)

---

## Principles

1. **CLAUDE.md = navigation hub, not encyclopedia** -- links instead of content
2. **Freshness > Completeness** -- 50 up-to-date lines > 500 stale ones
3. **Archive != Delete** -- move to `docs/archive/`, don't delete; journals (CHANGELOG, ISSUES) always grow
4. **Cache-optimized** -- static at top of CLAUDE.md, dynamic at bottom
5. **SSOT** -- each fact lives in ONE file, others link to it

---

## Step-by-Step Workflow

### Step 1. Re-scan all .md files

After Phase 3, paths may have changed. Full re-scan:

```
1. Find all .md files: root, docs/, .claude/, subprojects
2. For each file: lines, ~tokens (lines * 4), last modification date (git log)
3. Build parent CLAUDE.md chain (up the tree to ~/.claude/)
4. Determine project stage: INIT / ACTIVE / STABLE / MAINTENANCE
```

### Step 2. Check 20 Anti-Patterns

Run all documents through 20 anti-patterns:

| Priority | ID | What to look for |
|----------|-----|-----------------|
| Critical | AP-01 | CLAUDE.md > 4K tokens (context stuffing) |
| Critical | AP-07 | No experience/ or lessons learned |
| Critical | AP-12 | No project stage (INIT/ACTIVE/STABLE) |
| Critical | AP-16 | One fact in 3+ files (cross-file duplication) |
| High | AP-02 | Instructions for deleted files (stale docs) |
| High | AP-03 | MD files with no inbound links (orphan docs) |
| High | AP-04 | Dynamic content at top of CLAUDE.md (cache-hostile order) |
| High | AP-09 | Documentation describes non-existent code (code-doc drift) |
| High | AP-10 | Monolithic status section |
| High | AP-11 | Duplicate commands across files |
| High | AP-13 | Flat doc hierarchy (no tiering) |
| High | AP-17 | Missing quick start |
| High | AP-18 | No error handling docs |
| High | AP-19 | Outdated dependency versions in docs |
| High | AP-20 | Missing architecture diagram or link |
| Medium | AP-05 | Instruction overload (>30 rules) |
| Medium | AP-06 | Missing rules file link |
| Low | AP-08 | Too much emphasis formatting |
| Low | AP-14 | Missing table of contents for >200 line docs |
| Low | AP-15 | Inconsistent heading levels |

**Special attention after refactoring:** AP-02 (stale docs) and AP-09 (code-doc drift) -- file and function paths changed in Phases 1-3.

### Step 3. Find Duplication -> DUP-XX Codes

Each duplication must be coded:

```
DUP-XX | [file A] <-> [file B] | [what's duplicated] | Severity: HIGH/MEDIUM/LOW
```

Examples:
```
DUP-01 | CLAUDE.md <-> docs/DEPLOY.md | Deploy params (IP, zone) | Severity: HIGH
DUP-02 | CLAUDE.md <-> MEMORY.md | Tech stack listing | Severity: MEDIUM
DUP-03 | README.md <-> CLAUDE.md | Quick Start commands | Severity: HIGH
```

**Rule:** identical string (>10 words) in 2+ files = SSOT violation.

### Step 4. Create Tier Table

Classify ALL significant .md files:

| Tier | Description | Tokens | Action |
|------|------------|--------|--------|
| **Essential** | Loaded every session | ~800 | Keep in CLAUDE.md, compress |
| **On-demand** | On request when working with topic | ~500 each | Move to docs/, add link |
| **Archive** | Outdated, orphan docs | 0 | To docs/archive/ + .claudeignore |

**Rule AP-03:** orphan docs (no inbound links) ALWAYS -> Archive.

Example tier table:
```
| Tier       | File                    | Reason                            |
|------------|-------------------------|-----------------------------------|
| Essential  | CLAUDE.md               | Navigation hub                    |
| Essential  | ISSUES.md               | Active issues list                |
| On-demand  | docs/ARCHITECTURE.md    | Read when changing architecture   |
| On-demand  | docs/DEPLOY.md          | Read when deploying               |
| Archive    | docs/old_plan.md        | Superseded by new plan            |
| Archive    | docs/setup_v1.md        | Orphan: no inbound links          |
```

### Step 5. Optimize CLAUDE.md

Target structure (cache-optimized: static at top, dynamic at bottom):

| # | Section | Type | Content |
|---|---------|------|---------|
| 1 | Project Name + stack/git/deploy | STATIC | Project header |
| 2 | Quick Start (5 steps) | STATIC | Quick start |
| 3 | Commands | STATIC | Command table |
| 4 | Project Structure | SEMI-STATIC | Tree, max 40 lines |
| 5 | Principles and Rules | SEMI-STATIC | Links to docs/ |
| 6 | Docs Navigation | SEMI-STATIC | File -> when to read |
| 7 | Current Status | DYNAMIC | Table: phase, progress |
| 8 | Open Issues | DYNAMIC | Link to ISSUES.md |
| 9 | What's Next | DYNAMIC | Priority list |

**Actions:**
- Remove duplicates (by DUP-XX codes from Step 3)
- Update all file paths after Phase 3 moves
- Compress to target: **200-250 lines, ~1K-1.2K tokens**
- Move on-demand content to docs/ with links

### Step 6. Update Service Files

| File | What to update |
|------|---------------|
| INDEX.md | Paths, statuses after refactoring |
| CHANGELOG.md | Phase 4 SYNC entry (Keep a Changelog format) |
| ISSUES.md | Close resolved issues, update stale statuses |
| .claudeignore | Add Archive-tier files |

### Step 7. Drift Check: Code <-> Documentation

**Critical step after refactoring.** Verify:

1. **Paths in documentation** -> files actually exist (`glob`/`grep` verification)
2. **Described functions/classes** -> exist in code
3. **Versions in text** -> match current project version
4. **Freshness issues** coded as AP-F0X:

```
AP-F01 | [file] | Not updated in N days | Severity: HIGH/MEDIUM/LOW
AP-F02 | [file] | Version in text diverges from current | Severity: HIGH
AP-F03 | [file] | URL/path does not exist | Severity: MEDIUM
AP-F04 | [file] | Describes deleted module/function | Severity: HIGH
```

### Step 8. Calculate Health Score

Formula:
```
Score = (Completeness * 0.3) + (Efficiency * 0.3) + (Freshness * 0.2) + (Structure * 0.2)
```

| Component | What it evaluates |
|-----------|------------------|
| Completeness | All critical sections present |
| Efficiency | CLAUDE.md tokens / useful information ratio |
| Freshness | % of files updated in last 30 days |
| Structure | Cache ordering + tiering + no duplication |

**Thresholds:**

| Score | Condition |
|-------|-----------|
| 5/5 | CLAUDE.md <250 lines AND <2.5K tokens, 0 duplicates, 0 stale |
| 4/5 | CLAUDE.md <300 lines, 1-3 duplicates, <20% stale |
| 3/5 | CLAUDE.md <400 lines, 3-5 duplicates, <30% stale |
| 2/5 | CLAUDE.md >400 lines OR >4K tokens, >5 duplicates |
| 1/5 | Significant drift, >50% stale, >500 lines |

**If score < 3/5** -> repeat Steps 5-7 until at least 3/5.

### Step 9. Show Before/After Metrics

Mandatory final output:

```
PHASE 4 SYNC RESULTS:

                      Before    After     Delta
CLAUDE.md lines:      480       230       -52%
CLAUDE.md ~tokens:    3,840     920       -76%
Cross-file dupes:     7         0         -100%
Stale files:          4/12      0/12      -100%
Orphan docs:          3         0         -100%
Health Score:         2/5       4/5       +2

Archive moved:        3 files -> docs/archive/
SSOT violations:      5 -> 0
Anti-patterns:        8 -> 1 (AP-05 minor)
```

---

## What NOT to Do in Phase 4

- **Delete** CHANGELOG.md, WHY-LOG.md, ISSUES.md -- journals always grow
- **Delete** dormant docs -- ask the owner, mark `// DORMANT`
- **Apply** changes without showing diff and getting owner confirmation
- **Compress** archive journals -- only move old entries to docs/archive/
- **Ignore** parent CLAUDE.md chain when counting tokens

---

## Phase 4 Completion Checklist

```
[ ] All .md files re-scanned after Phase 3
[ ] 20 anti-patterns checked, critical/high fixed
[ ] Duplication coded (DUP-XX) and resolved
[ ] Tier table created (Essential/On-demand/Archive)
[ ] CLAUDE.md optimized (<250 lines, cache-ordered)
[ ] INDEX.md, CHANGELOG.md, ISSUES.md updated
[ ] Drift check passed: all paths and versions current
[ ] Health Score >= 3/5
[ ] Before/after metrics shown to owner
```
