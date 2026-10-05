# Phase 2: PLAN -- Detailed Reference

## Goal

Turn the raw SCAN Report from Phase 1 into a concrete, user-approved action plan. No file moves or renames until explicit OK.

---

## Step 1. Extract SCAN Report Data

Read the Phase 1 report. Extract:
- Full list of files (paths, types, sizes, dates)
- Discovered issues (duplicates, dead code, structural violations)
- Current directory tree

## Step 2. Group Files by Purpose

Assign each file to one category:

| Category | Examples |
|----------|---------|
| **code** | `.py`, `.js`, `.ts`, `.html`, `.css` -- source code |
| **docs** | `.md`, `.txt`, `.pdf` -- documentation, guides, notes |
| **assets** | Images, fonts, icons, video |
| **config** | `.json`, `.yaml`, `.env`, `.gitignore`, `Dockerfile` |
| **archive** | Outdated versions, backups, files untouched 6+ months |
| **unknown** | Files not fitting any category -- require user decision |

Within each category, sub-group by purpose (e.g., code: backend vs frontend; docs: guides vs reports).

## Step 3. Propose New Folder Structure

Build an ASCII tree of the target hierarchy. Rules:

- Folder names: `snake_case` or `kebab-case`, no spaces
- Files with dates: `YYYY-MM-DD_description.ext`
- Max nesting depth: 3 levels (exception: monorepo)
- Each folder must have one clear purpose
- `_archive/` for outdated files (archive, don't delete)

Example:

```
project/
+-- src/
|   +-- backend/
|   +-- frontend/
|   +-- shared/
+-- docs/
|   +-- guides/
|   +-- reports/
+-- assets/
|   +-- images/
|   +-- fonts/
+-- config/
+-- scripts/
+-- tests/
+-- _archive/
```

## Step 4. Create Move Table

For each file/group:

```markdown
| # | Current Path | New Path | Action | Note |
|---|-------------|----------|--------|------|
| 1 | src/utils.py | src/shared/utils.py | move | Shared module |
| 2 | old_handler.py | _archive/old_handler.py | archive | Unused since 2025-08 |
| 3 | README (1).md | -- | delete | Duplicate of README.md |
| 4 | photo cover.html | photo_cover.html | rename | Space in filename |
```

Actions: `move`, `rename`, `archive`, `delete`, `merge`, `keep`.

Files marked `delete` -- highlight separately for explicit confirmation.

## Step 5. Identify References to Update

Scan all files for references that will break on move:

| Ref Type | Where to search | Pattern |
|----------|----------------|---------|
| HTML src/href | `.html` files | `src="..."`, `href="..."` |
| CSS url() | `.css` files | `url(...)`, `@import` |
| Markdown links | `.md` files | `[text](path)`, `![img](path)` |
| Python imports | `.py` files | `import`, `from ... import` |
| JS/TS imports | `.js`, `.ts` | `import`, `require()` |
| Config paths | `.json`, `.yaml` | String values with paths |

For each reference:
- Source file (where the reference is)
- Current value
- New value after the move

## Step 6. Evaluate Code Architecture

Apply the **Deep Modules** concept (John Ousterhout):

> Deep module = small interface, large implementation.
> Shallow module = interface almost as complex as implementation.

**6a. Evaluate module depth:**

For each significant module/file:
- Count exported functions/classes (= interface size)
- Count implementation lines (= hidden complexity)
- Implementation / interface ratio = "depth"

**6b. Find merge candidates:**

Tightly coupled modules -- candidates for merging into one deep module:
- Modules always imported together
- Modules sharing the same types/data structures
- Modules where understanding one requires reading the other
- Small utilities extracted "for testability" but not actually testing the right thing

Format:

```markdown
### Merge: {module_a} + {module_b} -> {new_module}

**Why related:** Shared types, always imported together
**Current interface:** 12 functions total
**Proposed interface:** 4 functions
**Hidden complexity:** all validation and transformation logic
**Test impact:** 8 unit tests -> 4 boundary tests
```

**6c. For heavy refactors -- RFC:**

If a merge affects >5 files or >500 lines:
- Create RFC as GitHub Issue (`gh issue create`)
- Template: problem -> proposed solution -> affected files -> migration plan
- Don't block the rest of the plan -- RFC runs in parallel

## Step 7. Show Plan to User

Assemble the final plan:

```markdown
# Refactor Plan: {project_name}

## Current State
- Total files: X
- Categories: code (N), docs (N), assets (N), config (N), archive (N)
- Issues: [from SCAN Report]

## Proposed Structure
[ASCII tree from Step 3]

## Moves and Renames
[Table from Step 4]

## References to Update
[Table from Step 5]
Total references to update: N

## Architectural Proposals (code)
[From Step 6 -- module merges, if applicable]

## Files Requiring Your Decision
- [List of unknown files and files marked for deletion]

## Execution Order
1. Create new folders
2. Move/rename files
3. Update all references
4. Archive outdated items
5. Delete duplicates (after confirmation)
6. [If applicable] Apply architectural merges

---
Approve plan? (yes / no / modify)
```

---

## Critical Rules

1. **NEVER execute moves without explicit "yes" from user**
2. Unknown category files -- always ask, never guess
3. Deletions shown as separate list with reason
4. Rename conventions: `snake_case` for code and paths, `YYYY-MM-DD` for dates in filenames
5. Preserve original modification dates on move
6. Archive instead of delete when in doubt
7. RFC for heavy refactors -- don't try everything in one step
8. If project uses Git -- respect `.gitignore`, don't break history (rename detection works at >50% content match)

## Phase 2 Output

User-approved **Refactor Plan** -- input document for Phase 3 (EXECUTE).
