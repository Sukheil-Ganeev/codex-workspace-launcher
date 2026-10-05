# EXP-058: Wave pattern for multi-platform bot creation (3+2 agents)

**Date:** 2026-02-27
**Type:** pattern
**Severity:** high
**Project:** VIP-DXB-CatalogBot (Phase 20-21: Facebook Messenger + Viber)
**Times Applied:** 1

## Context
Creating 2 new platform bots (Facebook Messenger + Viber) simultaneously for a 7-platform CRM system. Each bot requires ~10-12 files (app, API client, FSM, formatters, templates, handlers) plus shared DB migrations, config changes, and tests.

## Pattern: 3+2 Wave Architecture

### Wave 1 (parallel, 3 agents in worktrees):
- **Agent 1:** Complete facebook_bot/ directory (all files)
- **Agent 2:** Complete viber_bot/ directory (all files)
- **Agent 3:** Shared modifications (database.py migrations, core/user_ids.py, bot/config.py)

Key insight: Each agent creates a COMPLETE bot, not split by layer (API vs handlers). This avoids inter-agent dependencies within a bot.

### Wave 2 (parallel, 2 agents after merge):
- **Agent 4:** All Facebook tests (6 files, 168 tests)
- **Agent 5:** All Viber tests (7 files, 211 tests)

### Post-Wave (sequential):
- Merge worktrees -> main repo
- Full pytest run for regressions
- CLAUDE.md + MEMORY.md updates

## Results
- 25 new files + 3 modified, ~4,187 lines
- 379 new tests (168 FB + 211 Viber)
- 2,248 total passed, 0 regressions
- Total wall time: ~35 minutes (vs estimated 5-7 days sequential)

## Lessons Learned

1. **Complete-bot-per-agent > layer-split:** Giving one agent the entire bot directory is better than splitting (e.g., API agent + handler agent). The bot files have tight internal dependencies.

2. **Shared files as separate agent:** database.py + user_ids.py + config.py changes must be a separate agent. These files are shared across all platforms and need to be merged into main before tests run.

3. **Tests in Wave 2:** Tests need the actual code to exist. Launching test agents AFTER code agents complete (but still parallel to each other) is the optimal pattern.

4. **Reference-bot strategy:** Instructing agents to "read instagram_bot/ FIRST as reference" dramatically improves output quality. The agent adapts patterns rather than inventing from scratch.

5. **Viber tracking_data FSM is a novel pattern:** No existing bot in the project uses this approach. The agent needed more detailed spec than Facebook (which closely mirrors Instagram).

6. **Worktree merge for new directories is trivial:** New bot directories have zero merge conflicts. Only shared files (database.py, config.py) need careful merging.

## Evolution from EXP-057

EXP-057 used a 4-agent pattern split by LAYER (Core/Logic/Handlers/Tests) for a SINGLE bot.
EXP-058 uses a 3+2 wave pattern split by PLATFORM (one agent = one complete bot) for MULTIPLE bots.

Key difference: When creating 2+ bots simultaneously, platform-split (EXP-058) is superior to layer-split (EXP-057) because:
- Zero inter-agent dependencies within each bot
- No bridge/harmonization issues between app.py and handlers
- Each agent has full autonomy over their bot directory

## Anti-patterns Avoided
- NOT splitting one bot across 2 agents (tight coupling)
- NOT running tests in Wave 1 (code doesn't exist yet)
- NOT modifying database.py from multiple agents (conflict risk)

## Applicability
Use this pattern whenever adding 2+ new platform integrations that share:
- Same DB (CatalogDB)
- Same webhook architecture (FastAPI)
- Same booking flow (FSM -> add_booking -> Telegram notify)
- Platform-specific API client + formatters + templates
