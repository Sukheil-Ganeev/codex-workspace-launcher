# Cross-Reference Audit: TouristBotEcosystem CLAUDE.md
**Mode:** audit (cross-reference validation)
**Skill:** docs-optimizer
**Project:** D:/Downloads/TouristBotEcosystem/
**Date:** 2026-03-12

---

## Summary

Total references checked: **157**
- Existing: **155** ✅
- Missing: **2** ❌
- External references checked: **3** (all exist ✅)

---

## MISSING FILES (❌)

| # | Path (relative to project root) | Context in CLAUDE.md | Severity |
|---|--------------------------------|----------------------|----------|
| 1 | `docs/DESIGN_DECISIONS_v1.md` | Architecture section: "Architectural decision records" | MEDIUM |
| 2 | `core/db/migrations/runner.py` | Architecture section: "Async file-based migration runner" | HIGH |

### Detail: `docs/DESIGN_DECISIONS_v1.md`

Mentioned in the architecture tree:
```
docs/DESIGN_DECISIONS_v1.md      # Architectural decision records
```
The file does **not exist** in `docs/`. The directory contains `UX_DESIGN_v1.md` and `BUTTON_DESIGN_GUIDE.md`, but no `DESIGN_DECISIONS_v1.md`. Possibly deleted or never created; it was listed as part of Batch 4 deliverables (CODE_REVIEW_v1.md was written, but DESIGN_DECISIONS_v1.md may have been skipped).

### Detail: `core/db/migrations/runner.py`

Mentioned in the architecture tree:
```
core/db/migrations/runner.py     # Async file-based migration runner
```
The `core/db/migrations/` directory exists and contains only `.sql` files:
- `001_vtb_base.sql`
- `002_cf_base.sql`
- `003_unified.sql`
- `004_bigint_ids.sql`
- `005_team_members_bigint.sql`

No `runner.py` is present. The migration runner logic may have been moved or merged into `core/db/database.py` (the orchestrator file).

---

## ALL EXISTING REFERENCES (✅)

### Root Config Files (12/12)
| Path | Status |
|------|--------|
| `docker-compose.yml` | ✅ |
| `Dockerfile` | ✅ |
| `.dockerignore` | ✅ |
| `requirements.txt` | ✅ |
| `requirements-dev.txt` | ✅ |
| `pytest.ini` | ✅ |
| `mypy.ini` | ✅ |
| `.env.example` | ✅ |
| `.gitignore` | ✅ |
| `ISSUES.md` | ✅ |
| `.github/workflows/deploy.yml` | ✅ |
| `config/settings.py` | ✅ |

### docs/ Files (10/11)
| Path | Status |
|------|--------|
| `docs/BUTTON_DESIGN_GUIDE.md` | ✅ |
| `docs/IMPROVEMENT_MASTER_PLAN.md` | ✅ |
| `docs/plans/2026-03-02-merge-vtb-cf-plan.md` | ✅ |
| `docs/ARCHITECTURE_v1.md` | ✅ |
| `docs/CODE_REVIEW_v1.md` | ✅ |
| `docs/MANUAL_TESTS.md` | ✅ |
| `docs/DESIGN_DECISIONS_v1.md` | ❌ MISSING |
| `docs/IDEAL_MASTER_PLAN.md` | ✅ |
| `deploy/cloudflare-tunnel.yml` | ✅ |
| `deploy/systemd/cloudflared.service` | ✅ |

### scripts/ (5/5)
| Path | Status |
|------|--------|
| `scripts/backup_sqlite.py` | ✅ |
| `scripts/migrate_sqlite_to_pg.py` | ✅ |
| `scripts/setup_server.sh` | ✅ |
| `scripts/deploy.sh` | ✅ |
| `scripts/healthcheck.sh` | ✅ |

### data/ (9/9 + fonts/)
| Path | Status |
|------|--------|
| `data/team.json` | ✅ |
| `data/prices.json` | ✅ |
| `data/platform_rules.json` | ✅ |
| `data/templates.json` | ✅ |
| `data/templates_seed.json` | ✅ |
| `data/admin_templates.json` | ✅ |
| `data/clients.json` | ✅ |
| `data/lessons.json` | ✅ |
| `data/pending_approvals.json` | ✅ |
| `data/fonts/` | ✅ |

### core/ Python modules (all except runner.py)
All 100+ core module files verified ✅ including:
- `core/ai/` (5 files) ✅
- `core/db/` (database.py, __init__.py, mixins/ ×8 files, schema/ ×4 SQL) ✅
- `core/db/migrations/` (3 SQL files) ✅ — but `runner.py` ❌
- `core/formatter/` (8 files) ✅
- `core/lessons/` (11 files) ✅
- `core/business/` (17 files) ✅
- `core/voice/` (11 files) ✅
- `core/content/` (24 files + adapters/ ×6) ✅
- `core/analytics/` (12 files) ✅
- `core/export/` (5 files) ✅
- `core/integrations/` (6 files) ✅
- `core/security/` (2 files) ✅
- `core/i18n/` (3 files) ✅
- `core/infra/` (9 files) ✅

### bots/ Python modules (all 55 checked)
All bots module files verified ✅:
- `bots/telegram_voice/` (9 checked) ✅
- `bots/telegram_content/` (3 checked) ✅
- `bots/whatsapp/` (8 files) ✅
- `bots/telegram_main/` (17 files) ✅
- `bots/admin/` (15 files) ✅

### tests/ (33/33)
All test files verified ✅.

### External references (3/3)
| Path | Status |
|------|--------|
| `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md` | ✅ |
| `D:/Downloads/VoiceTranscriptionBot/` | ✅ |
| `D:/Downloads/ContentFactory/` | ✅ |

---

## ORPHAN DOCS (exist but NOT referenced in CLAUDE.md)

These files exist in `docs/` but are not mentioned in CLAUDE.md's architecture section. They are informational — not broken links, but potential AP-03 (orphan docs):

| File | Notes |
|------|-------|
| `docs/ADMIN_BOT_REDESIGN.md` | Batch 5 design doc |
| `docs/ARCHITECTURE.md` | Unversioned, duplicate of ARCHITECTURE_v1.md? |
| `docs/AUDIT_2026-03-03.md` | Date-stamped audit |
| `docs/CICD_SETUP.md` | CI/CD guide |
| `docs/COMMAND_AUDIT.md` | Command audit (Batch 5 S2) |
| `docs/COMMAND_AUDIT_ADMIN.md` | Admin command audit |
| `docs/DATABASE_COVERAGE_AUDIT.md` | DB audit (Batch 5 S10) |
| `docs/DEPLOY.md` | Deploy guide |
| `docs/DEPLOY_GCP.md` | GCP-specific deploy |
| `docs/DEPLOY_LESSONS_2026-03-03.md` | Session lessons |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | v2 exists, only v1 referenced in CLAUDE.md |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | Milestone doc |
| `docs/SENTRY_GUIDE.md` | Sentry setup guide |
| `docs/SERVER_HEALTH_REPORT_2026-03-04.md` | Health report |
| `docs/SERVER_RUNBOOK.md` | Operations runbook |
| `docs/USER_GUIDE_admin.md` | User guide |
| `docs/USER_GUIDE_owner.md` | User guide |
| `docs/USER_GUIDE_staff.md` | User guide |
| `docs/UX_DESIGN_v1.md` | UX design doc |
| `docs/WHATSAPP_BOT_REDESIGN.md` | WA redesign (Batch 5 S7) |
| `docs/architecture/` | Subdirectory (contents unchecked) |
| `docs/formatting/` | Subdirectory (contents unchecked) |
| `docs/node_modules/` | ⚠️ Should NOT exist — likely .gitignore issue |

---

## NOTABLE OBSERVATIONS

1. **`docs/node_modules/` in docs/** — This directory should not be present in `docs/`. It may indicate an accidental `npm install` run inside `docs/`. Should be added to `.gitignore` and removed.

2. **`core/db/migrations/runner.py` gap** — CLAUDE.md documents this as an "Async file-based migration runner" but the file is absent. The migrations directory only has `.sql` files. Two possibilities: (a) runner logic was integrated into `core/db/database.py`, or (b) the file was accidentally deleted. The CLAUDE.md text should be updated to reflect reality.

3. **`docs/IMPROVEMENT_MASTER_PLAN_v2.md` exists** but CLAUDE.md still references v1. If v2 supersedes v1, update the reference.

4. **4 extra SQL migration files** beyond what CLAUDE.md lists — `004_bigint_ids.sql` and `005_team_members_bigint.sql` exist but are not documented. These are legitimate (from Hotfix phase) and should be added to CLAUDE.md.

---

## RECOMMENDED ACTIONS

| Priority | Action |
|----------|--------|
| HIGH | Fix `core/db/migrations/runner.py` reference — either restore file or update CLAUDE.md to reflect that migration runner is in `database.py` |
| HIGH | Remove `docs/node_modules/` and add it to `.gitignore` |
| MEDIUM | Either create `docs/DESIGN_DECISIONS_v1.md` or remove reference from CLAUDE.md |
| LOW | Update CLAUDE.md to reference `docs/IMPROVEMENT_MASTER_PLAN_v2.md` instead of v1 (or note both) |
| LOW | Document the 2 extra migration SQL files (`004_bigint_ids.sql`, `005_team_members_bigint.sql`) in CLAUDE.md |
| LOW | Add the 20 orphaned docs/ files to CLAUDE.md navigation or confirm they are intentionally unlisted |
