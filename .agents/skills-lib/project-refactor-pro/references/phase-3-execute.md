# Phase 3: EXECUTE -- Detailed Reference

> **Input:** User-approved plan from Phase 2 (mapping old -> new, target folder structure)
> **Output:** Files moved, references updated, change log created

---

## Step 1: Preparation

Ensure clean working directory before any changes:

```bash
git status
# If uncommitted changes -- commit or stash
git stash push -m "before-refactor-$(date +%Y%m%d)"
```

Create a refactoring branch:

```bash
git checkout -b refactor/restructure-$(date +%Y%m%d)
```

## Step 2: Create New Folders

Create the entire target directory structure from the approved plan:

```bash
mkdir -p src/components src/utils src/services docs/guides tests/unit tests/integration
```

Rule: create ALL folders before starting any moves. Do not create them one-by-one during the process.

## Step 3: Move Files by Mapping

Move each file according to the `old -> new` mapping from Phase 2:

```bash
# Move preserving structure
mv "old/path/file.ts" "new/path/file.ts"
```

**Move rules:**
- One file at a time -- do not use wildcards (`mv *.ts`)
- On name conflict (file already exists) -- STOP and ask the user
- Log every move in `move_log.md` immediately (format below)

## Step 4: Update References in ALL Files

After moving -- find and update all references to old paths:

**HTML** -- `src`, `href` attributes:
```bash
grep -rn 'src="old/path' --include="*.html"
grep -rn 'href="old/path' --include="*.html"
```

**CSS** -- `url()` paths:
```bash
grep -rn 'url(.*old/path' --include="*.css"
```

**Markdown** -- `[text](path)` links:
```bash
grep -rn '](old/path' --include="*.md"
```

**Python** -- `import` and `Path()`:
```bash
grep -rn 'from old.path' --include="*.py"
grep -rn "Path('old/path" --include="*.py"
```

**CLAUDE.md and configs** -- paths in tables and descriptions:
```bash
grep -rn 'old/path' CLAUDE.md README.md .github/ docs/
```

Replace each found path with the new one. Use `Edit` tool -- not sed with regexes (dangerous for complex paths).

## Step 5: Delete Duplicates

**ONLY with explicit user confirmation.**

Show the list of files to delete:
```
The following files became empty/duplicate after moving:
- old/path/file.ts (moved to new/path/file.ts)
- old/empty-dir/ (empty directory)

Delete? (yes/no)
```

Delete ONLY after "yes". Use `rmdir` for empty directories (not `rm -rf`).

## Step 6: Update .dsp/ Graph (if used)

If the project uses `.dsp/` for the dependency graph:

```bash
# For each moved file
# move-entity updates the graph without losing connections
```

If no `.dsp/` -- skip.

## Step 7: Create Change Log

Create `move_log.md` in the project root:

```markdown
# Move Log -- Restructure [YYYY-MM-DD]

## Summary
- Files moved: N
- References updated: N
- Directories created: N
- Directories removed: N

## Moves

| # | Old Path | New Path | Status |
|---|----------|----------|--------|
| 1 | old/path/file.ts | new/path/file.ts | OK |
| 2 | old/path/utils.ts | new/path/utils.ts | OK |

## Reference Updates

| File | Old Reference | New Reference |
|------|---------------|---------------|
| index.html | src="old/path" | src="new/path" |
| CLAUDE.md | `old/path/` | `new/path/` |

## Git Branch
`refactor/restructure-YYYYMMDD`
```

---

## Safety Rules

1. **NEVER delete without user confirmation** -- even empty folders
2. **Log EVERYTHING** -- every move recorded in `move_log.md` immediately, not at the end
3. **On name conflict** -- stop and ask (don't overwrite, don't add suffix)
4. **Git: do NOT auto-commit** -- let the user inspect `git diff` and `git status`
5. **Incremental** -- move files in groups of 5-10, verify nothing broke

---

## Rollback

### Option A: via Git (recommended)

If done in a separate branch:

```bash
# Return to main branch, discard all changes
git checkout main
git branch -D refactor/restructure-YYYYMMDD
```

If changes were on the current branch:

```bash
# Revert all uncommitted changes
git checkout -- .
# Or if stashed
git stash pop
```

### Option B: via move_log.md (if Git unavailable)

Read `move_log.md` and execute reverse moves:

```bash
# For each row in the Moves table -- swap old and new
mv "new/path/file.ts" "old/path/file.ts"
```

Rollback order: reverse of move order (last moved = first returned).
