---
name: changelog-generator
description: "Create or update CHANGELOG.md, generate release notes from git commits, update changelog in CLAUDE.md, summarize version changes. Triggers - changelog, обнови changelog, что изменилось, release notes."
license: Apache-2.0
compatibility: Works with any git repository
metadata:
---
# Changelog Generator

## Overview

Generate structured changelogs and release notes from git commit history.
Follows the **Keep a Changelog** convention. Supports four modes:

| Mode | When to use |
|------|-------------|
| `generate` | Create a new CHANGELOG.md entry from git history |
| `release` | Full release notes: technical changelog + user-facing summary |
| `update` | Update the `## 9. Changelog (последние 6)` table in CLAUDE.md |
| `summary` | Quick session summary — what changed right now |

---

## Mode: generate — From Git History

### Step 1: Determine the scope

```bash
# Show recent tags to find version boundaries
git tag --sort=-creatordate | head -10

# Last tag name
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
echo "Last tag: $LAST_TAG"

# All commits since last tag
git log "$LAST_TAG"..HEAD --oneline --no-merges

# Commits between two specific tags
git log v1.1.0..v1.2.0 --oneline --no-merges

# Commits in the last N days
git log --since="7 days ago" --oneline --no-merges

# Full details: hash + message + author + date
git log "$LAST_TAG"..HEAD --format="%h %s (%an, %ad)" --date=short --no-merges

# See what files changed in a commit
git show --stat <commit-hash>
```

### Step 2: Categorize commits

| Category | Commit prefixes | Description |
|----------|----------------|-------------|
| **Added** | `feat:`, `feature:`, `add:` | New features or capabilities |
| **Changed** | `refactor:`, `perf:`, `update:` | Changes to existing functionality |
| **Deprecated** | `deprecate:` | Features scheduled for removal |
| **Removed** | `remove:`, `breaking:` | Deleted features |
| **Fixed** | `fix:`, `bugfix:`, `hotfix:` | Bug fixes |
| **Security** | `security:`, `vuln:` | Vulnerability fixes |

Skip: `chore:`, `ci:`, `build:`, `docs:` (unless user-facing)

### Step 3: Write the entry

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature description in user-understandable language (#PR)

### Changed
- What changed and why it matters

### Fixed
- Bug description and what was corrected (#PR)
```

Rules:
- Write from the **user's perspective**, not the developer's
- Start each item with a verb: Add, Fix, Update, Remove, Improve
- Group related changes into one entry
- Mark breaking changes prominently with **[BREAKING]**
- Use ISO 8601 dates: `YYYY-MM-DD`
- Skip trivial commits (typo, whitespace) unless user wants everything

---

## Mode: release — Full Release Notes

Combines technical CHANGELOG entry + user-facing summary.

```bash
# Get commit range
git log v2.2.0..v2.3.0 --oneline --no-merges

# Get diff stats
git diff v2.2.0..v2.3.0 --stat

# Get PR numbers if available
git log v2.2.0..v2.3.0 --oneline --grep="Merge pull request"
```

Output structure:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- ...

### Fixed
- ...

---

## Release Notes for Users (EN/RU)

**What's new in vX.Y.Z**

Short highlight paragraph for non-technical readers.

**Highlights:**
- ...

**Bug Fixes:**
- ...
```

---

## Mode: update — Update CLAUDE.md Changelog Table

This project uses a specific format in `CLAUDE.md` section **"9. Changelog (последние 6)"**:

```markdown
## 9. Changelog (последние 6)

| Дата | Фаза | Что сделано |
|------|------|------------|
| 2026-03-10 | Omni Inbox Audit | Full 8-agent audit... |
| 2026-03-08 | Owner Panels v3 Wave 2 | Owner Settings panel... |
| ... | ... | ... |
```

### Rules for this table:
- **Maximum 6 rows** — drop the oldest when adding a new one
- **Дата** — ISO date `YYYY-MM-DD` (Dubai timezone context)
- **Фаза** — short phase/feature name, e.g. `Phase 21`, `Omni Inbox`, `Bug Fix`, `Owner Panels v3`
- **Что сделано** — 1–3 sentences: what was done, key changes, new tables/files/tests count
- Write in **Russian** unless the entry is purely technical (then English is fine)
- Never duplicate an existing entry — check current table before inserting

### Workflow:
1. Read the current `CLAUDE.md` changelog table
2. Compose the new row based on what was done in this session
3. Prepend the new row, drop row 7 if table has 6 rows
4. Edit `CLAUDE.md` with the updated table

### Example new row:
```
| 2026-03-12 | Changelog Generator Skill | Создан скилл changelog-generator с 4 режимами (generate/release/update/summary). Поддержка Keep a Changelog + CLAUDE.md формат таблицы. |
```

---

## Mode: summary — Quick Session Summary

When a coding session ends and you need a one-liner for CLAUDE.md or a commit message.

```bash
# See what changed in the working tree
git diff --stat HEAD

# Recent commits since session start (adjust time)
git log --since="4 hours ago" --oneline

# Count changed files
git diff --name-only HEAD | wc -l
```

Output format:

```
Session summary (YYYY-MM-DD):
- [Added/Fixed/Changed]: <short description>
- [Added/Fixed/Changed]: <short description>

Suggested CLAUDE.md row:
| YYYY-MM-DD | <Фаза> | <1-2 sentences what was done, key files/counts> |

Suggested commit message:
<type>: <short description>
```

---

## Keep a Changelog Categories — Reference

| Category | Use for | Example |
|----------|---------|---------|
| **Added** | New features, new files, new endpoints | "Add Viber Bot webhook handler" |
| **Changed** | Modified behavior, updated dependencies, refactors | "Update catalog price logic to use centralized helper" |
| **Deprecated** | Still works but will be removed | "Deprecate SQLite fallback in db utilities" |
| **Removed** | Deleted features, removed endpoints | "Remove legacy ?-placeholder SQL style" |
| **Fixed** | Bug fixes, error corrections | "Fix is_banned INTEGER→BOOLEAN cast on PostgreSQL" |
| **Security** | Auth, HMAC, injection fixes | "Enforce HMAC-SHA256 on all Meta webhooks" |

---

## Git Commands Reference

```bash
# --- Scope ---
git tag --sort=-creatordate | head -10          # Recent tags
git describe --tags --abbrev=0                   # Latest tag
git log --oneline -20                            # Last 20 commits

# --- Range queries ---
git log v1.0..HEAD --oneline --no-merges         # Since tag
git log main..feature/x --oneline --no-merges    # Branch diff
git log --since="2026-03-01" --oneline           # Since date
git log --after="2026-03-01" --before="2026-03-12" --oneline

# --- Filters ---
git log --grep="fix" --oneline                   # Only fix commits
git log --grep="feat" --oneline
git log --author="Name" --oneline               # By author

# --- Detail ---
git show --stat <hash>                           # Files changed
git diff v1.0..HEAD --stat                       # Overall stats
git log --format="%h %s (%an, %ad)" --date=short # Rich format

# --- Count ---
git log v1.0..HEAD --oneline | wc -l            # Commit count
git diff v1.0..HEAD --shortstat                 # +/- lines
```

---

## Examples

### Example 1: Technical changelog entry

**Context:** VIP-DXB-CatalogBot, adding Viber Bot (Phase 21)

```bash
git log v10.7.0..HEAD --oneline --no-merges
```

```markdown
## [10.8.0] - 2026-03-10

### Added
- Add Viber Bot with FastAPI webhook (port 8084)
- Add Rich Media 6-column carousel for catalog
- Add 7-step booking FSM via tracking_data
- Add `viber_users` DB table with synthetic user_id -3000..
- Add `get_or_create_viber_user()` DB method
- Add migration v21_viber
- Add 211 tests for Viber Bot

### Changed
- Register ViberConnector in Omni Inbox startup sequence
```

### Example 2: CLAUDE.md table row

```
| 2026-03-10 | Phase 21: Viber Bot | FastAPI webhook, Rich Media 6-col carousel, 7-step FSM (tracking_data), viber_users table, synthetic -3000.., 211 tests. |
```

### Example 3: User-facing release notes (Russian)

```markdown
## Что нового в v10.8.0

Добавлена поддержка **Viber** — теперь клиенты могут бронировать экскурсии
прямо в Viber с красивыми карточками и пошаговой формой бронирования.

**Новое:**
- Viber бот с каталогом экскурсий
- Карусели карточек с фото и описанием
- Бронирование за 7 шагов

**Исправлено:**
- Отображение цен в USD/AED
```

---

## Quick Reference

```
generate  → CHANGELOG.md entry from git history
release   → Technical + user-facing release notes
update    → Update CLAUDE.md "Changelog (последние 6)" table
summary   → One-liner session summary + suggested commit message
```

---

## Common Mistakes

| Mistake | Correct approach |
|---------|-----------------|
| Writing from dev perspective: "Refactored FSMManager" | Write from user view: "Improve booking flow reliability" |
| Forgetting the date | Always include `YYYY-MM-DD` |
| Adding 7th row to CLAUDE.md table | Drop the oldest row — max 6 |
| Using past tense inconsistently | Stick to present tense imperative: "Add", "Fix", "Update" |
| Including chore/ci/docs commits | Skip unless they affect user behavior |
| Not checking existing CHANGELOG.md format | Read existing format first, match it |
| Writing CLAUDE.md row in English when project uses Russian | Use Russian for CLAUDE.md changelog rows |

---

## Sources

- Original skill: https://github.com/TerminalSkills/skills/tree/main/skills/changelog-generator
- Keep a Changelog spec: https://keepachangelog.com/en/1.1.0/
- Semantic Versioning: https://semver.org/
- Project CLAUDE.md format: VIP-DXB-CatalogBot section "9. Changelog (последние 6)"

**Skill size:** ~5.5 KB | **Version:** 1.1.0 | **Adapted:** 2026-03-12
