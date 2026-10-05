# project-refactor-pro -- Cheatsheet

## Modes

| Mode | Phases | Destructive? | Use when |
|------|--------|-------------|----------|
| `scan` | 1 | No | Need to see what's wrong |
| `plan` | 1+2 | No | Need a migration plan |
| `full` | 1+2+3+4 | Yes | Ready to refactor |
| `sync` | 4 | Partial | Just update docs |
| `score` | 1+report | No | Quick health check |

## Flags

| Flag | Effect |
|------|--------|
| `--focus=files` | Only file organization issues |
| `--focus=deps` | Only dependency issues |
| `--focus=docs` | Only documentation issues |
| `--focus=refs` | Only dead references |
| `--path=<dir>` | Scan specific directory |
| `--dry-run` | Show what would happen (full mode) |
| `--verbose` | Detailed output |
| `--auto-approve` | Skip confirmations (CI) |

## Pipeline Flow

```
SCAN --> PLAN --> EXECUTE --> SYNC
 |        |        |          |
 graph    move     mv files   update
 orphans  table    update     CLAUDE.md
 drift    arch     refs       CHANGELOG
 dups     RFC      log        health
```

## Severity Codes

| Level | Meaning |
|-------|---------|
| CRITICAL | Wrong behavior, security, data loss |
| HIGH | Significant confusion, wasted time |
| MEDIUM | Misleading but survivable |
| LOW | Cosmetic only |

## Drift Categories

| Code | Meaning | Example |
|------|---------|---------|
| STALE | Changed/removed | Old endpoint in README |
| GHOST | References deleted symbol | CLAUDE.md -> deleted file |
| SHADOW | Code without any docs | New endpoint, zero docs |
| MISMATCH | Right idea, wrong detail | Docstring says timeout=30, code=60 |

## Anti-Pattern IDs (Phase 4)

| ID | What |
|----|------|
| AP-01 | CLAUDE.md > 4K tokens |
| AP-02 | Stale docs (deleted files) |
| AP-03 | Orphan docs (no links) |
| AP-04 | Dynamic at top of CLAUDE.md |
| AP-05 | >30 rules (overload) |
| AP-07 | No experience/lessons |
| AP-09 | Code-doc drift |
| AP-12 | No project stage |
| AP-16 | Cross-file duplication |

## Duplication Format

```
DUP-XX | [file A] <-> [file B] | [what] | Severity: HIGH/MEDIUM/LOW
```

## Freshness Codes

| Code | Meaning |
|------|---------|
| AP-F01 | Not updated in N days |
| AP-F02 | Version mismatch |
| AP-F03 | URL/path doesn't exist |
| AP-F04 | Describes deleted code |

## Health Score Formula

```
Score = Completeness*0.3 + Efficiency*0.3 + Freshness*0.2 + Structure*0.2
```

| Score | Threshold |
|-------|-----------|
| 5/5 | <250 lines, <2.5K tokens, 0 dups, 0 stale |
| 4/5 | <300 lines, 1-3 dups, <20% stale |
| 3/5 | <400 lines, 3-5 dups, <30% stale |
| 2/5 | >400 lines OR >4K tokens, >5 dups |
| 1/5 | Major drift, >50% stale, >500 lines |

## Tier Table

| Tier | Tokens | Action |
|------|--------|--------|
| Essential | ~800 | In CLAUDE.md |
| On-demand | ~500 each | In docs/, linked |
| Archive | 0 | docs/archive/ + .claudeignore |

## Safety Rules (Phase 3)

1. Never delete without user confirmation
2. Log every move immediately in move_log.md
3. Stop on name conflict -- ask user
4. Don't auto-commit -- let user check diff
5. Move in groups of 5-10, verify each group

## CLAUDE.md Target Structure

```
1. Project header (static)
2. Quick Start (static)
3. Commands (static)
4. Project Structure (semi-static, max 40 lines)
5. Rules (semi-static, links to docs/)
6. Docs Navigation (semi-static)
7. Current Status (dynamic)
8. Open Issues (dynamic)
9. What's Next (dynamic)
```

## Rollback Options

| Method | When |
|--------|------|
| `git checkout main && git branch -D refactor/...` | Git available, separate branch |
| Reverse moves from move_log.md | No Git |

## File Naming

- Code/paths: `snake_case`
- Dates in filenames: `YYYY-MM-DD_description.ext`
- Max nesting: 3 levels
- No spaces in filenames
