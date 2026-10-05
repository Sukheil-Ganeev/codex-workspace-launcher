# EXP-064: Parallel Refactoring with Strict File Ownership

**Date:** 2026-02-28
**Severity:** high
**Type:** pattern
**Project:** VIP-DXB-CatalogBot
**Times applied:** 1

## Context
Major refactoring of 7-platform bot (115K LOC, 57% duplication). Needed to consolidate i18n, config, FSM, formatters, and services into core/ while also migrating AI backend.

## Pattern
1. **Security first** — fix vulnerabilities BEFORE structural changes
2. **Strict file ownership** — each parallel agent gets exclusive file set
3. **Phases with dependencies** — Phase 1 (quick wins) completes before Phase 2 (abstraction)
4. **Backup before everything** — full project copy before first change
5. **Tests between phases** — full pytest run after each wave of agents
6. **Composition over inheritance** — FSM uses inheritance, but formatters and services use delegation

## File ownership map (no conflicts)
- Agent A: */fsm.py files only
- Agent B: */formatters.py files only
- Agent C: bot/services/*.py deletions + import updates
- Agent D: core/services/ai_adapter.py (new) + existing AI services

## Results
- 6 parallel agents, 0 merge conflicts
- 2,321 tests pass (73 new tests added)
- ~20,000 lines of duplication eliminated
- Session duration: ~3 hours total (agents ran up to 90 min each)

## Anti-patterns avoided
- Do NOT let multiple agents edit the same file (database.py, config.py)
- Do NOT run more than 6 agents — context pressure
- Do NOT skip test verification between phases

## Keywords
refactoring, parallel agents, file ownership, duplication, consolidation
