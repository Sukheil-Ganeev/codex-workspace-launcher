# Phase 1: SCAN

> **Goal:** Build a complete structural map of the project and surface every anomaly before touching any code.
> **Output:** SCAN Report with categorized findings and severity levels.

---

## Step 1 — Initialize the Dependency Graph

Create (or update) the `.dsp/` structural graph using `dsp-cli.py`.

```bash
# First time — bootstrap
python dsp-cli.py --root . init

# If .dsp/ already exists — skip init, go straight to Step 2
```

If `dsp-cli.py` is missing:

```bash
curl -O https://raw.githubusercontent.com/k-kolomeitsev/data-structure-protocol/main/skills/data-structure-protocol/scripts/dsp-cli.py
```

## Step 2 — Map All Entities

Traverse the project from root entrypoints via DFS on imports. For each file:

```bash
# Register a module
python dsp-cli.py --root . create-object "src/services/auth.py" "Authentication service — JWT + bcrypt"
# → obj-a1b2c3d4

# Register its exported functions
python dsp-cli.py --root . create-function "src/services/auth.py#verify_token" "Verifies JWT token" --owner obj-a1b2c3d4
# → func-7f3a9c12

# Register exports and imports with WHY
python dsp-cli.py --root . create-shared obj-a1b2c3d4 func-7f3a9c12
python dsp-cli.py --root . add-import obj-a1b2c3d4 obj-deadbeef "Needs DB pool for token blocklist"
```

**Rules:**
- External deps (`node_modules`, `site-packages`) → `create-object --kind external`, never descend inside
- Every import must have a `why` — this is where the graph's value lives
- UIDs are stable: `obj-XXXX` for objects, `func-XXXX` for functions

## Step 3 — Find Orphaned Files

Files that nobody imports and that import nobody — candidates for deletion or missing integration.

```bash
python dsp-cli.py --root . get-orphans
```

**Action:** For each orphan, determine:
- Dead code → mark for removal in Phase 2
- Missing link → add the correct `add-import`
- Standalone utility → document as intentionally isolated

## Step 4 — Detect Circular Dependencies

Cycles make refactoring dangerous — changing one node ripples unpredictably.

```bash
python dsp-cli.py --root . detect-cycles
```

**Action:** Record every cycle. In Phase 2 these become priority refactor targets.

## Step 5 — Run Drift Detection

Scan all documentation against actual code. Check these sources:

| Source | What to verify |
|--------|---------------|
| Docstrings / inline comments | Function signatures, parameter names, return types |
| README, CLAUDE.md | Module paths, endpoint URLs, env var names |
| CHANGELOG | Version numbers vs. `package.json` / `pyproject.toml` |
| API docs | Route definitions vs. actual route files |
| Architecture docs | Directory structure vs. reality |
| `.env.example` | Var names vs. config files that read them |

Classify each finding into one of four categories:

| Category | Meaning | Example |
|----------|---------|---------|
| **STALE** | Doc describes something changed or removed | README says `POST /api/v1/users` but route was migrated to `/api/v2/users` |
| **GHOST** | Doc references a symbol that no longer exists | CLAUDE.md mentions `utils/helpers.py` — file was deleted |
| **SHADOW** | Code exists with zero documentation | New endpoint `/api/v2/export` added but not in any doc |
| **MISMATCH** | Doc has correct intent but wrong detail | Docstring says `timeout=30` but code defaults to `60` |

## Step 6 — Find Duplicates

Scan for identical or near-identical logic across files:

1. **Hash-based** — files with identical content (exact duplicates)
2. **Block-based** — 5+ identical lines appearing in multiple files
3. **Structural** — same logic with different variable names (same AST shape)

Use `cross-file` mode patterns:
```
DUP-01 | src/handlers/booking.py:134 <-> src/handlers/profile.py:89 | validate_phone() copy-pasted | Severity: HIGH
DUP-02 | config/dev.json <-> config/staging.json | Identical DB config block | Severity: MEDIUM
```

## Step 7 — Generate SCAN Report

Compile all findings into a structured report:

```
## SCAN Report — {project_name} — {date}

### Summary
- Entities mapped: N objects, M functions
- Orphaned files: X
- Circular dependencies: Y cycles
- Drift findings: Z (CRITICAL: A | HIGH: B | MEDIUM: C | LOW: D)
- Duplications: W

### CRITICAL
DRIFT-01 | README.md:47 | Claims endpoint /api/v1/blocks | Actual: /api/v2/blocks | Action: UPDATE
GHOST-01 | CLAUDE.md:12 | References utils/old_helper.py | File deleted in commit abc123 | Action: REMOVE

### HIGH
STALE-01 | docs/API.md:89 | Documents 5 params for create_user() | Actual: 3 params since v2.1 | Action: UPDATE
DUP-01   | handlers/booking.py:134 <-> handlers/profile.py:89 | validate_phone() | Action: EXTRACT

### MEDIUM
MISMATCH-01 | services/auth.py:12 docstring | Says timeout=30 | Actual: timeout=60 | Action: FIX
SHADOW-01   | services/export.py | 4 public functions, 0 documented | Action: DOCUMENT

### LOW
STALE-02 | README.md:3 | Version badge shows v1.2 | Actual: v1.4 | Action: UPDATE

### Orphans
- old_migration_v3.py — no imports, no importers → candidate for deletion
- standalone_tool.py — intentionally isolated CLI tool → mark as standalone

### Cycles
- obj-a1b2 → obj-c3d4 → obj-e5f6 → obj-a1b2 (3-node cycle in auth layer)

### Duplications
DUP-01 | booking.py:134 <-> profile.py:89 | validate_phone() | → Extract to shared/validators.py
DUP-02 | dev.json <-> staging.json | DB config block | → Use config inheritance

### Stats
Total files scanned: N
Graph coverage: X% of project files mapped in .dsp/
```

---

## Severity Reference

| Severity | Criteria | Examples |
|----------|----------|---------|
| **CRITICAL** | Wrong behavior if followed, security hole, data loss risk | Wrong auth flow in docs, ghost reference to deleted security module |
| **HIGH** | Significant confusion, wasted developer time | Stale API params, duplicated business logic |
| **MEDIUM** | Misleading but survivable with source inspection | Wrong default value in docstring, minor naming mismatch |
| **LOW** | Cosmetic — old name, stale badge, outdated example | Version badge, old screenshot |

---

## Checklist Before Moving to Phase 2

- [ ] `.dsp/` graph initialized and all reachable files mapped
- [ ] `get-orphans` executed — orphan list reviewed
- [ ] `detect-cycles` executed — all cycles recorded
- [ ] Drift detection completed across all doc sources
- [ ] Duplicate scan completed (hash + block + structural)
- [ ] SCAN Report generated with severity assignments
- [ ] Every CRITICAL finding has an action plan
- [ ] Report saved to `{project}/.refactor/scan_report.md`
