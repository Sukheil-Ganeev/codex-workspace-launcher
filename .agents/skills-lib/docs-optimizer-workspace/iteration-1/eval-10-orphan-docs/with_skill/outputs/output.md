# Docs Optimizer — AP-03: Orphan Docs Detection
**Проект:** D:/Downloads/TouristBotEcosystem/
**Анти-паттерн:** AP-03 — Orphan Docs (MD файлы без ссылок ниоткуда)
**Режим:** `analyze`
**Дата анализа:** 2026-03-12
**Score:** 2/5

---

## Фаза 1: Discovery — все файлы в docs/

Итого в docs/: **32 файла MD** (+ поддиректории plans/)

| Файл | Строк | ~Токенов | Дата (git) |
|------|-------|---------|------------|
| IDEAL_MASTER_PLAN.md | 2 559 | ~10 236 | **untracked** |
| UX_DESIGN_v1.md | 1 103 | ~4 412 | 2026-03-03 |
| DEPLOY_GCP.md | 1 062 | ~4 248 | 2026-03-03 |
| BUTTON_DESIGN_GUIDE.md | 1 039 | ~4 156 | 2026-03-04 |
| IMPROVEMENT_MASTER_PLAN.md | 879 | ~3 516 | 2026-03-04 |
| ARCHITECTURE_v1.md | 841 | ~3 364 | 2026-03-03 |
| DEPLOY.md | 798 | ~3 192 | 2026-03-03 |
| PROJECT_ACCOMPLISHMENTS.md | 628 | ~2 512 | 2026-03-04 |
| WHATSAPP_BOT_REDESIGN.md | 522 | ~2 088 | 2026-03-04 |
| USER_GUIDE_owner.md | 476 | ~1 904 | 2026-03-03 |
| ARCHITECTURE.md | 424 | ~1 696 | 2026-03-03 |
| USER_GUIDE_admin.md | 390 | ~1 560 | 2026-03-03 |
| CODE_REVIEW_v1.md | 385 | ~1 540 | 2026-03-03 |
| SERVER_RUNBOOK.md | 361 | ~1 444 | 2026-03-04 |
| DATABASE_COVERAGE_AUDIT.md | 337 | ~1 348 | 2026-03-04 |
| AUDIT_2026-03-03.md | 332 | ~1 328 | 2026-03-03 |
| MANUAL_TESTS.md | 321 | ~1 284 | 2026-03-03 |
| ADMIN_BOT_REDESIGN.md | 278 | ~1 112 | 2026-03-04 |
| COMMAND_AUDIT_ADMIN.md | 262 | ~1 048 | 2026-03-04 |
| IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1 020 | 2026-03-04 |
| COMMAND_AUDIT.md | 218 | ~872 | 2026-03-04 |
| audit_ai_lessons.md | 210 | ~840 | 2026-03-03 |
| SENTRY_GUIDE.md | 187 | ~748 | 2026-03-04 |
| audit_ecosystem.md | 182 | ~728 | 2026-03-03 |
| audit_infra.md | 178 | ~712 | 2026-03-03 |
| DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | 2026-03-03 |
| USER_GUIDE_staff.md | 145 | ~580 | 2026-03-03 |
| SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | 2026-03-04 |
| audit_business.md | 136 | ~544 | 2026-03-03 |
| audit_voice.md | 123 | ~492 | 2026-03-03 |
| audit_content.md | 119 | ~476 | 2026-03-03 |
| CICD_SETUP.md | 105 | ~420 | 2026-03-04 |
| plans/2026-03-02-merge-vtb-cf-plan.md | 961 | ~3 844 | — |
| plans/2026-03-02-unified-telegram-bot.md | 990 | ~3 960 | — |
| DESIGN_DECISIONS_v1.md | ~180 | ~720 | 2026-03-03 |

**ИТОГО docs/ (32 MD файла):** ~17 114 строк, ~68 456 токенов

---

## Фаза 2: Проверка ссылок из CLAUDE.md

Явные навигационные ссылки из CLAUDE.md на docs/:

| Файл | Тип ссылки | Строка в CLAUDE.md |
|------|-----------|---------------------|
| docs/BUTTON_DESIGN_GUIDE.md | **Явная навигационная** | строка 23 |
| docs/IMPROVEMENT_MASTER_PLAN.md | **Явная навигационная** | строка 26 |
| docs/plans/2026-03-02-merge-vtb-cf-plan.md | **Явная** (план миграции) | строки 333, 557 |
| docs/ARCHITECTURE_v1.md | Упоминание в дереве структуры | строка 334 |
| docs/CODE_REVIEW_v1.md | Упоминание в дереве структуры | строка 335 |
| docs/MANUAL_TESTS.md | Упоминание в дереве структуры | строка 336 |
| docs/DESIGN_DECISIONS_v1.md | Упоминание в дереве структуры | строка 337 |
| docs/IDEAL_MASTER_PLAN.md | Упоминание в дереве (READ ONLY) | строка 340 |
| docs/audit_*.md (6 файлов) | Групповая ссылка (READ ONLY) | строка 341 |

**Не упомянуты нигде (полные orphans):** 22 файла из 32.

---

## Фаза 3: Synthesis — Tier-таблица

AP-03 (Orphan Docs): файлы без навигационных ссылок ОБЯЗАТЕЛЬНО классифицируются в тир `Archive`.

| Tier | File | Reason |
|------|------|--------|
| Essential | CLAUDE.md | Загружается каждую сессию, навигационный хаб |
| On-demand | docs/BUTTON_DESIGN_GUIDE.md | Явная ссылка — читать при работе с UI кнопками |
| On-demand | docs/IMPROVEMENT_MASTER_PLAN.md | Явная ссылка — активный roadmap на 12 сессий |
| On-demand | docs/plans/2026-03-02-merge-vtb-cf-plan.md | Явная ссылка — план миграции VTB+CF |
| On-demand | docs/ARCHITECTURE_v1.md | Упомянут в дереве CLAUDE.md — архитектурные вопросы |
| On-demand | docs/CODE_REVIEW_v1.md | Упомянут в дереве CLAUDE.md — при code review |
| On-demand | docs/MANUAL_TESTS.md | Упомянут в дереве CLAUDE.md — при тестировании |
| On-demand | docs/DESIGN_DECISIONS_v1.md | Упомянут в дереве CLAUDE.md — при ARD/решениях |
| On-demand | docs/audit_ai_lessons.md | Групповая ссылка audit_*.md |
| On-demand | docs/audit_ecosystem.md | Групповая ссылка audit_*.md |
| On-demand | docs/audit_infra.md | Групповая ссылка audit_*.md |
| On-demand | docs/audit_business.md | Групповая ссылка audit_*.md |
| On-demand | docs/audit_voice.md | Групповая ссылка audit_*.md |
| On-demand | docs/audit_content.md | Групповая ссылка audit_*.md |
| Archive | docs/IDEAL_MASTER_PLAN.md | Orphan: нет ссылок; untracked в git; READ ONLY — методологический документ, не операционный |
| Archive | docs/UX_DESIGN_v1.md | Orphan: нет ссылок; создан 2026-03-03, не обновлялся |
| Archive | docs/DEPLOY_GCP.md | Orphan: нет ссылок; деплой-гайд GCP без навигационной ссылки |
| Archive | docs/DEPLOY.md | Orphan: нет ссылок; устарел — Oracle Cloud, проект на GCP |
| Archive | docs/PROJECT_ACCOMPLISHMENTS.md | Orphan: нет ссылок |
| Archive | docs/WHATSAPP_BOT_REDESIGN.md | Orphan: нет ссылок; только в changelog-строке |
| Archive | docs/USER_GUIDE_owner.md | Orphan: нет ссылок |
| Archive | docs/ARCHITECTURE.md | Orphan: нет ссылок; дубль с ARCHITECTURE_v1.md |
| Archive | docs/USER_GUIDE_admin.md | Orphan: нет ссылок |
| Archive | docs/SERVER_RUNBOOK.md | Orphan: нет ссылок |
| Archive | docs/DATABASE_COVERAGE_AUDIT.md | Orphan: нет ссылок; только в changelog-строке |
| Archive | docs/AUDIT_2026-03-03.md | Orphan: нет ссылок; только в changelog-строке |
| Archive | docs/ADMIN_BOT_REDESIGN.md | Orphan: нет ссылок; только в changelog-строке |
| Archive | docs/COMMAND_AUDIT_ADMIN.md | Orphan: нет ссылок; только в changelog-строке |
| Archive | docs/IMPROVEMENT_MASTER_PLAN_v2.md | Orphan: нет ссылок; конфликт с v1 |
| Archive | docs/COMMAND_AUDIT.md | Orphan: нет ссылок; только в changelog-строке |
| Archive | docs/SENTRY_GUIDE.md | Orphan: нет ссылок |
| Archive | docs/DEPLOY_LESSONS_2026-03-03.md | Orphan: нет ссылок |
| Archive | docs/USER_GUIDE_staff.md | Orphan: нет ссылок |
| Archive | docs/SERVER_HEALTH_REPORT_2026-03-04.md | Orphan: нет ссылок |
| Archive | docs/CICD_SETUP.md | Orphan: нет ссылок |
| Archive | docs/plans/2026-03-02-unified-telegram-bot.md | Orphan: нет ссылок |

---

## Анти-паттерны (AP-XX)

**AP-03** | docs/ directory | 22 файла из 32 не имеют навигационных ссылок из CLAUDE.md — полные orphan docs | Severity: **HIGH**

Детали по orphan docs:
- 16 файлов без единого упоминания в CLAUDE.md
- 6 файлов упомянуты только в changelog-строке (не как "читай для X")
- Итого orphan токенов: ~43 000 из ~68 456 (63%)

---

## Итоговая статистика

| Метрика | Значение |
|---------|----------|
| Всего MD файлов в docs/ | 32 |
| Tier Essential | 1 (CLAUDE.md) |
| Tier On-demand (referenced) | 10 |
| Tier Archive (orphan) | **22** |
| Orphan токенов (~) | ~43 000 |
| Orphan % от total docs | ~63% |

---

## Топ-5 orphan файлов по токенам

1. **IDEAL_MASTER_PLAN.md** — ~10 236 токенов. Untracked в git. Методологический документ для владельца, не для Claude.
2. **UX_DESIGN_v1.md** — ~4 412 токенов. Не обновлялся с 2026-03-03. Нет ссылок.
3. **plans/2026-03-02-unified-telegram-bot.md** — ~3 960 токенов. Второй план миграции без ссылки.
4. **DEPLOY_GCP.md** — ~4 248 токенов. Актуальный деплой-гайд, но нет навигационной ссылки.
5. **DEPLOY.md** — ~3 192 токенов. Устаревший гайд Oracle Cloud.

---

## Рекомендации

### [HIGH] AP-03 — 22 orphan файла → добавить в .claudeignore

Все 22 файла из тира `Archive` следует добавить в `.claudeignore`. Предлагаемый блок:

```
# Orphan docs — Archive tier (AP-03)
docs/IDEAL_MASTER_PLAN.md
docs/UX_DESIGN_v1.md
docs/DEPLOY.md
docs/DEPLOY_GCP.md
docs/PROJECT_ACCOMPLISHMENTS.md
docs/WHATSAPP_BOT_REDESIGN.md
docs/USER_GUIDE_owner.md
docs/ARCHITECTURE.md
docs/USER_GUIDE_admin.md
docs/SERVER_RUNBOOK.md
docs/DATABASE_COVERAGE_AUDIT.md
docs/AUDIT_2026-03-03.md
docs/ADMIN_BOT_REDESIGN.md
docs/COMMAND_AUDIT_ADMIN.md
docs/IMPROVEMENT_MASTER_PLAN_v2.md
docs/COMMAND_AUDIT.md
docs/SENTRY_GUIDE.md
docs/DEPLOY_LESSONS_2026-03-03.md
docs/USER_GUIDE_staff.md
docs/SERVER_HEALTH_REPORT_2026-03-04.md
docs/CICD_SETUP.md
docs/plans/2026-03-02-unified-telegram-bot.md
```

### [HIGH] DEPLOY_GCP.md — добавить навигационную ссылку или архивировать

Файл содержит актуальный деплой-гайд для GCP. Если используется — добавить в CLAUDE.md:
`"Развёртывание на GCP → docs/DEPLOY_GCP.md"` и переместить из Archive в On-demand.

### [MEDIUM] ARCHITECTURE.md vs ARCHITECTURE_v1.md — SSOT нарушение

Оба файла описывают архитектуру. ARCHITECTURE_v1.md упомянут в CLAUDE.md, ARCHITECTURE.md — нет. Определить актуальный, второй → archive.

### [LOW] Audit файлы — переместить в docs/audits/

6 файлов audit_*.md сейчас в корне docs/. Переместить в `docs/audits/`, добавить в `.claudeignore`.

---

**Потенциальная экономия:** ~30 000 токенов (44%) при добавлении orphan файлов в `.claudeignore`.

*Анализ по методологии docs-optimizer, режим `analyze`, AP-03. Дата: 2026-03-12.*
