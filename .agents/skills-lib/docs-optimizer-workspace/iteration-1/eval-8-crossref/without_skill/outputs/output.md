# Аудит ссылок на файлы в CLAUDE.md

**Проект:** D:/Downloads/TouristBotEcosystem/
**Файл:** CLAUDE.md
**Дата проверки:** 2026-03-12
**Всего проверено ссылок:** 270
**Существуют:** 268
**Отсутствуют:** 2

---

## Итог: 2 битые ссылки

### ОТСУТСТВУЮЩИЕ ФАЙЛЫ

| # | Путь в CLAUDE.md | Полный путь | Раздел в CLAUDE.md |
|---|-----------------|-------------|---------------------|
| 1 | `core/db/migrations/runner.py` | `D:/Downloads/TouristBotEcosystem/core/db/migrations/runner.py` | Архитектура → core/db/migrations/ |
| 2 | `docs/DESIGN_DECISIONS_v1.md` | `D:/Downloads/TouristBotEcosystem/docs/DESIGN_DECISIONS_v1.md` | Архитектура → docs/ |

---

## Детали по каждому отсутствующему файлу

### 1. `core/db/migrations/runner.py`

**Где упоминается в CLAUDE.md:**
```
core/db/migrations/runner.py    # Async file-based migration runner
```

**Что есть в директории `core/db/migrations/`:**
- `.gitkeep`
- `001_vtb_base.sql`
- `002_cf_base.sql`
- `003_unified.sql`
- `004_bigint_ids.sql` (не упоминается в CLAUDE.md)
- `005_team_members_bigint.sql` (не упоминается в CLAUDE.md)

**Вывод:** Файл `runner.py` был указан в CLAUDE.md как часть архитектуры, но физически отсутствует. Также в CLAUDE.md не упомянуты два новых SQL-файла миграций: `004_bigint_ids.sql` и `005_team_members_bigint.sql`.

---

### 2. `docs/DESIGN_DECISIONS_v1.md`

**Где упоминается в CLAUDE.md:**
```
docs/DESIGN_DECISIONS_v1.md    # Architectural decision records
```

**Что есть в директории `docs/`:**
`ADMIN_BOT_REDESIGN.md`, `ARCHITECTURE.md`, `ARCHITECTURE_v1.md`, `AUDIT_2026-03-03.md`, `audit_ai_lessons.md`, `audit_business.md`, `audit_content.md`, `audit_ecosystem.md`, `audit_infra.md`, `audit_voice.md`, `BUTTON_DESIGN_GUIDE.md`, `CICD_SETUP.md`, `CODE_REVIEW_v1.md`, `COMMAND_AUDIT.md`, `COMMAND_AUDIT_ADMIN.md`, `DATABASE_COVERAGE_AUDIT.md`, `DEPLOY.md`, `DEPLOY_GCP.md`, `DEPLOY_LESSONS_2026-03-03.md`, `IDEAL_MASTER_PLAN.md`, `IMPROVEMENT_MASTER_PLAN.md`, `IMPROVEMENT_MASTER_PLAN_v2.md`, `MANUAL_TESTS.md`, `PROJECT_ACCOMPLISHMENTS.md`, `SENTRY_GUIDE.md`, `SERVER_HEALTH_REPORT_2026-03-04.md`, `SERVER_RUNBOOK.md`, `UX_DESIGN_v1.md`, `USER_GUIDE_admin.md`, `USER_GUIDE_owner.md`, `USER_GUIDE_staff.md`, `WHATSAPP_BOT_REDESIGN.md`

**Вывод:** Файл `DESIGN_DECISIONS_v1.md` был удалён или никогда не создавался. В docs/ есть `UX_DESIGN_v1.md` — возможно, это замена или переименование.

---

## Дополнительно: файлы в docs/, не упомянутые в CLAUDE.md

Следующие файлы существуют в `docs/`, но не отражены в CLAUDE.md:

| Файл | Примечание |
|------|-----------|
| `ADMIN_BOT_REDESIGN.md` | Не упоминается |
| `ARCHITECTURE.md` | Есть только `ARCHITECTURE_v1.md` в CLAUDE.md |
| `AUDIT_2026-03-03.md` | Не упоминается |
| `CICD_SETUP.md` | Не упоминается |
| `COMMAND_AUDIT.md` | Упоминается в Batch 5 описании, но не в файловом дереве |
| `COMMAND_AUDIT_ADMIN.md` | Упоминается в Batch 5 описании, но не в файловом дереве |
| `DATABASE_COVERAGE_AUDIT.md` | Упоминается в Batch 5 описании, но не в файловом дереве |
| `DEPLOY.md` | Не упоминается |
| `DEPLOY_GCP.md` | Не упоминается |
| `DEPLOY_LESSONS_2026-03-03.md` | Не упоминается |
| `IMPROVEMENT_MASTER_PLAN_v2.md` | Есть только v1 в CLAUDE.md |
| `PROJECT_ACCOMPLISHMENTS.md` | Не упоминается |
| `SENTRY_GUIDE.md` | Не упоминается |
| `SERVER_HEALTH_REPORT_2026-03-04.md` | Не упоминается |
| `SERVER_RUNBOOK.md` | Не упоминается |
| `USER_GUIDE_admin.md` | Не упоминается |
| `USER_GUIDE_owner.md` | Не упоминается |
| `USER_GUIDE_staff.md` | Не упоминается |
| `UX_DESIGN_v1.md` | Не упоминается (возможная замена DESIGN_DECISIONS_v1.md?) |
| `WHATSAPP_BOT_REDESIGN.md` | Упоминается в Batch 5 описании, но не в файловом дереве |

## Дополнительно: SQL-миграции в core/db/migrations/, не упомянутые в CLAUDE.md

| Файл | Статус |
|------|--------|
| `004_bigint_ids.sql` | Существует, не упомянут в CLAUDE.md |
| `005_team_members_bigint.sql` | Существует, не упомянут в CLAUDE.md |

---

## Резюме

| Категория | Кол-во |
|-----------|--------|
| Всего проверено ссылок | 270 |
| Существующих файлов | 268 (99.3%) |
| Битых ссылок (файл упомянут, не существует) | **2** |
| Файлов не упомянутых в CLAUDE.md (docs/) | ~20 |
| SQL-миграций не упомянутых в CLAUDE.md | 2 |

**Критичность битых ссылок:**
- `core/db/migrations/runner.py` — УМЕРЕННАЯ. Описан как "Async file-based migration runner". Функционально важен, но его отсутствие означает либо что миграции запускаются иначе, либо файл был удалён после рефакторинга.
- `docs/DESIGN_DECISIONS_v1.md` — НИЗКАЯ. Документация, не влияет на работу кода.
