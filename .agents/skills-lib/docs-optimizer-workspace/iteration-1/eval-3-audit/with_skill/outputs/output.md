# DOCS OPTIMIZER — AUDIT REPORT
**Mode:** `audit`
**Project:** TouristBotEcosystem (`D:/Downloads/TouristBotEcosystem/`)
**Date:** 2026-03-12
**Verification Score:** 3/5

---

## PHASE 1: DISCOVERY — FILE METRICS

### Root-level docs

| Файл | Строк | ~Токенов | Последний коммит | Статус |
|------|-------|---------|-----------------|--------|
| CLAUDE.md | 557 | ~2,228 | 2026-03-05 | active |
| CHANGELOG.md | 1,088 | ~4,352 | 2026-03-05 | active |
| ISSUES.md | 110 | ~440 | 2026-03-04 | active (stale version) |
| MASTER_PLAN.md | 1,900 | ~7,600 | 2026-03-03 | stale (7 days ago, status="В ПЛАНИРОВАНИИ") |
| README.md | 351 | ~1,404 | 2026-03-04 | active |

### docs/ directory (36 files)

| Файл | Строк | ~Токенов | Последний коммит | Статус |
|------|-------|---------|-----------------|--------|
| IDEAL_MASTER_PLAN.md | 2,559 | ~10,236 | 2026-03-04 | active (READ ONLY) |
| BUTTON_DESIGN_GUIDE.md | 1,039 | ~4,156 | 2026-03-04 | active |
| DEPLOY_GCP.md | 1,062 | ~4,248 | 2026-03-03 | active |
| UX_DESIGN_v1.md | 1,103 | ~4,412 | 2026-03-03 | stale (9 days) |
| ARCHITECTURE_v1.md | 841 | ~3,364 | 2026-03-03 | stale (superseded by ARCHITECTURE.md) |
| IMPROVEMENT_MASTER_PLAN.md | 879 | ~3,516 | 2026-03-04 | active (v1.0, closed) |
| DEPLOY.md | 798 | ~3,192 | 2026-03-03 | stale (Oracle Cloud — superseded by GCP) |
| PROJECT_ACCOMPLISHMENTS.md | 628 | ~2,512 | 2026-03-04 | orphan (no CLAUDE.md reference) |
| WHATSAPP_BOT_REDESIGN.md | 522 | ~2,088 | 2026-03-04 | active (referenced in CLAUDE.md) |
| CODE_REVIEW_v1.md | 385 | ~1,540 | 2026-03-03 | active (referenced) |
| SERVER_RUNBOOK.md | 361 | ~1,444 | 2026-03-03 | orphan |
| COMMAND_AUDIT_ADMIN.md | 262 | ~1,048 | 2026-03-04 | active (referenced in Batch 5) |
| IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1,020 | 2026-03-04 | orphan (not in CLAUDE.md nav) |
| ADMIN_BOT_REDESIGN.md | 278 | ~1,112 | 2026-03-04 | orphan (not referenced in CLAUDE.md) |
| DATABASE_COVERAGE_AUDIT.md | 337 | ~1,348 | 2026-03-04 | active (referenced in Batch 5) |
| MANUAL_TESTS.md | 321 | ~1,284 | 2026-03-04 | active (referenced) |
| COMMAND_AUDIT.md | 218 | ~872 | 2026-03-04 | active (referenced) |
| AUDIT_2026-03-03.md | 332 | ~1,328 | 2026-03-03 | archive (Phase 0 complete) |
| audit_ecosystem.md | 182 | ~728 | 2026-03-03 | archive |
| audit_infra.md | 178 | ~712 | 2026-03-03 | archive |
| audit_ai_lessons.md | 210 | ~840 | 2026-03-03 | archive |
| audit_business.md | 136 | ~544 | 2026-03-03 | archive |
| audit_content.md | 119 | ~476 | 2026-03-03 | archive |
| audit_voice.md | 123 | ~492 | 2026-03-03 | archive |
| ARCHITECTURE.md | 424 | ~1,696 | 2026-03-03 | active |
| DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | 2026-03-03 | orphan |
| SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | 2026-03-04 | orphan |
| SENTRY_GUIDE.md | 187 | ~748 | 2026-03-03 | orphan |
| USER_GUIDE_admin.md | 390 | ~1,560 | 2026-03-04 | orphan |
| USER_GUIDE_owner.md | 476 | ~1,904 | 2026-03-04 | orphan |
| USER_GUIDE_staff.md | 145 | ~580 | 2026-03-04 | orphan |
| CICD_SETUP.md | 105 | ~420 | 2026-03-03 | orphan |
| IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1,020 | 2026-03-04 | orphan |
| plans/2026-03-02-merge-vtb-cf-plan.md | 961 | ~3,844 | 2026-03-02 | archive (Batch 1-3 complete) |
| plans/2026-03-02-unified-telegram-bot.md | 990 | ~3,960 | 2026-03-02 | archive |

**СУММАРНО:** 36 docs/ файлов + 5 root файлов = **41 MD файл**
**Строк:** ~20,300 в docs/ + ~4,006 в root = **~24,306 строк**
**~Токенов:** ~81,224 (авто-загрузка = сжигание контекста)

---

## PHASE 2: ANALYSIS

### 2A. ANTI-PATTERN SCAN

| ID | Паттерн | Severity | Найден в | Детали |
|----|---------|----------|---------|--------|
| AP-01 | Context Stuffing | HIGH | CLAUDE.md | 557 строк / ~2,228 токенов — превышает target 250 строк |
| AP-07 | Stale Documentation | CRITICAL | MASTER_PLAN.md | Статус "В ПЛАНИРОВАНИИ" — проект в ACTIVE/STABLE стадии. Последний коммит 2026-03-03 |
| AP-07 | Stale Documentation | HIGH | docs/DEPLOY.md | Описывает Oracle Cloud деплой — проект уже на GCP (2026-03-03). Устарел на 9 дней |
| AP-07 | Stale Documentation | HIGH | docs/ARCHITECTURE_v1.md | Версия v4.0 (Phase 0 + Batch 1-4). Есть более свежий docs/ARCHITECTURE.md |
| AP-07 | Stale Documentation | HIGH | docs/UX_DESIGN_v1.md | Последний коммит 2026-03-03, не обновлялся за 9 дней при активной разработке |
| AP-08 | Missing Index | MEDIUM | docs/ | Нет docs/README.md или индексного файла — 36 файлов без навигации |
| AP-09 | Orphan Docs | MEDIUM | 10+ files | PROJECT_ACCOMPLISHMENTS, SERVER_RUNBOOK, DEPLOY_LESSONS, SERVER_HEALTH_REPORT, SENTRY_GUIDE, USER_GUIDE_*, CICD_SETUP, ADMIN_BOT_REDESIGN, IMPROVEMENT_MASTER_PLAN_v2 — не referenced в CLAUDE.md |
| AP-10 | Code-Doc Drift | HIGH | CLAUDE.md | Строка 244: "11 unified роутеров", но реально 13 (unified_expenses + unified_report добавлены). Строка 285: "40 файлов" tests, реально 47 .py файлов. test_whatsapp_calc/clients/expenses/history/route/stats не упомянуты в docs |
| AP-11 | Cache-Hostile Ordering | HIGH | CLAUDE.md | Статус батчей (динамика) — строки 12-17 в самом начале, до архитектуры |
| AP-16 | Cross-File Duplication | CRITICAL | Multiple | Deployment params: в CLAUDE.md + docs/DEPLOY.md + docs/DEPLOY_GCP.md. Architecture: в CLAUDE.md + docs/ARCHITECTURE.md + docs/ARCHITECTURE_v1.md. FORMATTING_GUIDE путь: в CLAUDE.md + docs/IMPROVEMENT_MASTER_PLAN.md (оба копируют) |
| AP-18 | Dead Pointers | MEDIUM | CLAUDE.md | docs/DESIGN_DECISIONS_v1.md упомянут в строке 337 — файл не существует (не в git) |
| AP-19 | Stale Issues | HIGH | ISSUES.md | Версия кода: v5.8.0, текущая v5.9.0 (2026-03-05). SEN-01..05 открыты 8 дней без обновления |
| AP-20 | Memory-Doc Overlap | N/A | — | MEMORY.md не существует в проекте |

---

### 2B. CROSS-FILE DUPLICATION MAP

**Формат: DUP-XX | [файл A] ↔ [файл B] | [что дублируется] | Severity**

```
DUP-01 | CLAUDE.md ↔ docs/DEPLOY_GCP.md | GCP deployment params (IP, zone, VM type) | Severity: CRITICAL
DUP-02 | CLAUDE.md ↔ docs/DEPLOY.md ↔ docs/DEPLOY_GCP.md | Docker compose команды | Severity: HIGH
DUP-03 | CLAUDE.md ↔ docs/ARCHITECTURE.md ↔ docs/ARCHITECTURE_v1.md | Архитектурное дерево файлов | Severity: HIGH
DUP-04 | CLAUDE.md ↔ docs/IMPROVEMENT_MASTER_PLAN.md | FORMATTING_GUIDE путь (строки 20 vs 13) | Severity: MEDIUM
DUP-05 | CLAUDE.md ↔ MASTER_PLAN.md | Текущий статус батчей (строки 12-17 vs раздел "В ПЛАНИРОВАНИИ") | Severity: MEDIUM
DUP-06 | CLAUDE.md ↔ docs/IMPROVEMENT_MASTER_PLAN.md | BUTTON_DESIGN_GUIDE путь | Severity: LOW
```

| DUP | Файлы | Что дублируется | Источник правды | Severity |
|-----|-------|----------------|-----------------|----------|
| DUP-01 | CLAUDE.md ↔ docs/DEPLOY_GCP.md | GCP deployment params (IP, zone, VM type) | CLAUDE.md | CRITICAL |
| DUP-02 | CLAUDE.md ↔ docs/DEPLOY.md ↔ docs/DEPLOY_GCP.md | Docker compose команды | CLAUDE.md | HIGH |
| DUP-03 | CLAUDE.md ↔ docs/ARCHITECTURE.md ↔ docs/ARCHITECTURE_v1.md | Архитектура (дерево файлов) | CLAUDE.md | HIGH |
| DUP-04 | CLAUDE.md ↔ docs/IMPROVEMENT_MASTER_PLAN.md | FORMATTING_GUIDE путь | CLAUDE.md | MEDIUM |
| DUP-05 | CLAUDE.md ↔ MASTER_PLAN.md | Статус батчей | CLAUDE.md | MEDIUM |
| DUP-06 | CLAUDE.md ↔ docs/IMPROVEMENT_MASTER_PLAN.md | BUTTON_DESIGN_GUIDE путь | CLAUDE.md | LOW |

---

### 2C. FRESHNESS CHECK (git log)

| Файл | Последний коммит | Дней назад | Вывод |
|------|-----------------|-----------|-------|
| CLAUDE.md | 2026-03-05 | 7 | OK (ACTIVE стадия) |
| CHANGELOG.md | 2026-03-05 | 7 | OK |
| ISSUES.md | 2026-03-04 | 8 | STALE: не обновлён после v5.9.0 (2026-03-05) |
| MASTER_PLAN.md | 2026-03-03 | 9 | STALE: статус "В ПЛАНИРОВАНИИ" при completed batches |
| docs/ARCHITECTURE_v1.md | 2026-03-03 | 9 | STALE: superseded by ARCHITECTURE.md |
| docs/DEPLOY.md | 2026-03-03 | 9 | STALE: Oracle Cloud — заменён GCP деплоем |
| docs/UX_DESIGN_v1.md | 2026-03-03 | 9 | STALE: не обновлялся при добавлении 5+ новых handlers |
| docs/audit_*.md (6 файлов) | 2026-03-03 | 9 | ARCHIVE: Phase 0 завершён, но нет .claudeignore |
| docs/plans/*.md (2 файла) | 2026-03-02 | 10 | ARCHIVE: планы выполнены |
| docs/SERVER_HEALTH_REPORT_2026-03-04.md | 2026-03-04 | 8 | ORPHAN: нет ссылок |

---

### 2D. ISSUES.MD STALE DETECTION

**Статус ISSUES.md:**
- Версия кода в заголовке: `v5.8.0 (2026-03-04)` — но текущая версия v5.9.0 (2026-03-05)
- SEN-01..05 открыты с 2026-03-04 (8 дней) — нет признаков обновления

**Открытые issues — анализ актуальности:**

| ID | Статус в ISSUES.md | Анализ | Вывод |
|----|-------------------|--------|-------|
| SEN-01 | ОТКРЫТ | Sentry инвестигация — ещё актуально | OK |
| SEN-02 | ОТКРЫТ | gemini-2.5-flash-lite найден в core/ai/models.py строка 5 — проблема реальна | OK |
| SEN-03 | ОТКРЫТ | asyncpg race condition — ещё актуально | OK |
| SEN-04 | ОТКРЫТ | aiogram rate limits — ещё актуально | OK |
| SEN-05 | ОТКРЫТ | Post-deploy baseline — может быть устаревшим если деплой прошёл | Needs check |
| DB-01 | DORMANT | 20 CF-таблиц dormant — актуально | OK |

**Вывод:** ISSUES.md версия кода не обновлена до v5.9.0 — нарушение протокола.

---

### 2E. FILE PATH REFERENCES IN CLAUDE.md — VALIDATION

| Ссылка в CLAUDE.md | Файл существует? | Статус |
|-------------------|-----------------|--------|
| `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md` | ✅ ДА | OK |
| `docs/BUTTON_DESIGN_GUIDE.md` | ✅ ДА | OK |
| `docs/IMPROVEMENT_MASTER_PLAN.md` | ✅ ДА | OK |
| `docs/plans/2026-03-02-merge-vtb-cf-plan.md` | ✅ ДА | OK |
| `docs/ARCHITECTURE_v1.md` (строка 334) | ✅ ДА | OK — но дублируется с docs/ARCHITECTURE.md |
| `docs/CODE_REVIEW_v1.md` (строка 335) | ✅ ДА | OK |
| `docs/MANUAL_TESTS.md` (строка 336) | ✅ ДА | OK |
| `docs/DESIGN_DECISIONS_v1.md` (строка 337) | ❌ НЕТ | **БИТАЯ ССЫЛКА** — файл не существует |
| `docs/IDEAL_MASTER_PLAN.md` (строка 340) | ✅ ДА | OK |
| `docs/WHATSAPP_BOT_REDESIGN.md` (строка 341, неявно) | ✅ ДА | OK |
| `docs/audit_*.md` (строка 341) | ✅ ДА | OK — но нет .claudeignore для исключения |

**КРИТИЧЕСКАЯ НАХОДКА:** `docs/DESIGN_DECISIONS_v1.md` — в CLAUDE.md строка 337 указан как "Architectural decision records", файл не существует ни в рабочей копии, ни в git истории.

---

## PHASE 3: SYNTHESIS

### TIER CLASSIFICATION TABLE

| Tier | File | Reason |
|------|------|--------|
| Essential | CLAUDE.md | Загружается каждую сессию, навигационный хаб |
| Essential | ISSUES.md | Актуальный список проблем — читать при старте |
| Essential | CHANGELOG.md | История изменений для контекста |
| On-demand | docs/ARCHITECTURE.md | Читать при изменениях архитектуры |
| On-demand | docs/DEPLOY_GCP.md | Читать при деплое на GCP |
| On-demand | docs/BUTTON_DESIGN_GUIDE.md | Читать при UI изменениях |
| On-demand | docs/IDEAL_MASTER_PLAN.md | READ ONLY, читать для контекста планирования |
| On-demand | docs/IMPROVEMENT_MASTER_PLAN.md | Текущий план улучшений |
| On-demand | docs/WHATSAPP_BOT_REDESIGN.md | Читать при работе с WA ботом |
| On-demand | docs/MANUAL_TESTS.md | Читать при тестировании |
| On-demand | docs/COMMAND_AUDIT.md | Читать при аудите команд |
| On-demand | docs/CODE_REVIEW_v1.md | Читать при code review |
| Archive | docs/ARCHITECTURE_v1.md | Устарел, superseded by ARCHITECTURE.md |
| Archive | docs/DEPLOY.md | Oracle Cloud — заменён GCP деплоем |
| Archive | docs/UX_DESIGN_v1.md | Устарел, не обновлялся 9+ дней |
| Archive | docs/audit_*.md (6 шт.) | Phase 0 complete, более не релевантны |
| Archive | docs/plans/*.md (2 шт.) | Планы выполнены (Batch 1-3) |
| Archive | MASTER_PLAN.md | Статус "В ПЛАНИРОВАНИИ" устарел — все Batch завершены |
| Archive | docs/SERVER_HEALTH_REPORT_2026-03-04.md | Разовый отчёт, orphan |
| Archive | docs/DEPLOY_LESSONS_2026-03-03.md | Orphan, архивный урок |

---

### ИТОГОВЫЕ МЕТРИКИ

| Метрика | Значение | Target | Статус |
|---------|---------|--------|--------|
| CLAUDE.md строк | 557 | < 250 | 🔴 CRITICAL (2x превышение) |
| CLAUDE.md ~токенов | ~2,228 | < 2,500 | 🟡 WARNING |
| Docs суммарно строк | ~24,306 | < 5,000 | 🔴 CRITICAL (5x превышение) |
| Orphan files | 10+ | 0 | 🔴 CRITICAL |
| Stale files (>7 дней) | 8 файлов | 0% | 🔴 CRITICAL |
| Cross-file дублей | 6 | 0 | 🔴 CRITICAL |
| Битые ссылки | 1 | 0 | 🔴 CRITICAL |
| ISSUES.md stale ratio | v5.8 вместо v5.9 | 0% | 🟡 WARNING |
| Archive files без .claudeignore | 10+ | 0 | 🟡 WARNING |
| Verification score | 3/5 | 5/5 | 🟡 MEDIUM |

---

### РАНЖИРОВАННЫЕ ПРОБЛЕМЫ

#### HIGH IMPACT (исправить немедленно)

**H-01 [CRITICAL] Битая ссылка: `docs/DESIGN_DECISIONS_v1.md`**
- Файл: CLAUDE.md строка 337
- Проблема: `docs/DESIGN_DECISIONS_v1.md` указан как "Architectural decision records" — файл не существует
- Исправление: удалить строку или заменить на `docs/ARCHITECTURE.md` + `docs/CODE_REVIEW_v1.md`

**H-02 [CRITICAL] CLAUDE.md = 557 строк (target: 250)**
- Проблема: AP-01 Context Stuffing. Архитектурное дерево занимает ~200 строк, команды ~80, деплой ~60
- Исправление: вынести детальное дерево в docs/ARCHITECTURE.md, оставить компактную версию (~30 строк)

**H-03 [CRITICAL] ISSUES.md версия не обновлена до v5.9.0**
- Файл: ISSUES.md заголовок
- Проблема: `Версия кода: v5.8.0` при текущей v5.9.0 (2026-03-05). Нарушение протокола
- Исправление: обновить до `v5.9.0 (2026-03-05)`, добавить SEN-05 update после деплоя

**H-04 [HIGH] Code-Doc Drift в CLAUDE.md статистике**
- Строка 244: "11 unified роутеров" → реально **13** (+ unified_expenses.py, unified_report.py)
- Строка 285: "1263 тестов (40 файлов)" → реально **47 .py файлов** в tests/
- Новые test_whatsapp_calc/clients/expenses/history/route/stats не упомянуты в docs

**H-05 [HIGH] Cache-Hostile Ordering в CLAUDE.md**
- Проблема: AP-11. Таблица батчей (строки 12-17) — динамический контент ВЫШЕ архитектуры
- Исправление: переместить "Статус проекта" → вниз CLAUDE.md, архитектуру оставить вверху

---

#### MEDIUM IMPACT

**M-01 [HIGH] 10+ orphan docs без ссылок из CLAUDE.md**
- Файлы: `PROJECT_ACCOMPLISHMENTS.md`, `SERVER_RUNBOOK.md`, `DEPLOY_LESSONS_2026-03-03.md`, `SERVER_HEALTH_REPORT_2026-03-04.md`, `SENTRY_GUIDE.md`, `USER_GUIDE_admin.md`, `USER_GUIDE_owner.md`, `USER_GUIDE_staff.md`, `CICD_SETUP.md`, `ADMIN_BOT_REDESIGN.md`, `IMPROVEMENT_MASTER_PLAN_v2.md`
- Исправление: добавить в CLAUDE.md навигационную таблицу или переместить в docs/archive/

**M-02 [HIGH] docs/DEPLOY.md устарел (Oracle Cloud)**
- Файл: docs/DEPLOY.md (798 строк)
- Проблема: описывает Oracle Cloud деплой — проект переехал на GCP 2026-03-03
- Исправление: переместить в docs/archive/DEPLOY_oracle_cloud.md, добавить в .claudeignore

**M-03 [HIGH] 6 audit_*.md файлов без .claudeignore**
- Файлы: docs/audit_*.md (6 штук) + docs/AUDIT_2026-03-03.md + docs/plans/*.md
- Проблема: Phase 0 завершён — эти файлы загружаются в контекст впустую
- Исправление: создать .claudeignore, добавить docs/audit_*.md, docs/plans/, docs/AUDIT_*.md

**M-04 [HIGH] Два конкурирующих ARCHITECTURE файла**
- `docs/ARCHITECTURE.md` (424 строки, 2026-03-03) — "обновлённый"
- `docs/ARCHITECTURE_v1.md` (841 строк, 2026-03-03) — "AS-IS"
- CLAUDE.md ссылается только на ARCHITECTURE_v1.md
- Исправление: ARCHITECTURE.md = active, ARCHITECTURE_v1.md → archive

**M-05 [MEDIUM] MASTER_PLAN.md статус "В ПЛАНИРОВАНИИ"**
- Файл: MASTER_PLAN.md (1900 строк)
- Статус: "В ПЛАНИРОВАНИИ" при том что все Batch 1-6 завершены
- CLAUDE.md на него не ссылается
- Исправление: обновить статус или переместить в docs/archive/

**M-06 [MEDIUM] IMPROVEMENT_MASTER_PLAN_v2.md — orphan**
- Файл: docs/IMPROVEMENT_MASTER_PLAN_v2.md (255 строк)
- Создан 2026-03-04, не упомянут в CLAUDE.md
- CLAUDE.md ссылается только на v1 как "(12 сессий)", но v2 — следующий активный план
- Исправление: добавить ссылку в CLAUDE.md, обновить описание с "(12 сессий)" на "(закрыт v5.7) + v2: 15 областей"

---

#### LOW IMPACT

**L-01 Cross-file duplication: FORMATTING_GUIDE путь**
- CLAUDE.md строка 20 + docs/IMPROVEMENT_MASTER_PLAN.md строка 13 — дублируется путь
- IMPROVEMENT_MASTER_PLAN.md = контекстный документ для сессий, допустимо

**L-02 Нет docs/README.md (AP-08)**
- 36 файлов в docs/ без индексного файла
- Добавить docs/README.md с таблицей файлов и назначением

**L-03 ISSUES.md "Аудит-архивы: не обнаружены" — неточность**
- Файл: ISSUES.md строка 9
- В docs/ есть 7+ архивных аудит-файлов Phase 0
- Исправление: обновить на "Аудит-архивы: docs/audit_*.md, docs/AUDIT_2026-03-03.md (READ ONLY)"

---

## ДУБЛИРОВАНИЕ — КАРТА SSOT

| Факт | Источник правды | Дублируется в | Действие |
|------|----------------|--------------|---------|
| GCP VM params | CLAUDE.md | docs/DEPLOY_GCP.md | docs/ — on-demand, OK |
| Docker команды | CLAUDE.md | docs/DEPLOY.md (Oracle) | DEPLOY.md → archive |
| Архитектурное дерево | CLAUDE.md | docs/ARCHITECTURE.md | CLAUDE.md → compact version |
| Batch статус | CLAUDE.md | MASTER_PLAN.md | MASTER_PLAN.md → update status |
| FORMATTING_GUIDE путь | CLAUDE.md | IMPROVEMENT_MASTER_PLAN.md | Допустимо (contextual) |

---

## ACTION PLAN (приоритизировано)

### Сделать немедленно (1 сессия):

1. **[CRITICAL]** Исправить битую ссылку `docs/DESIGN_DECISIONS_v1.md` в CLAUDE.md строка 337
2. **[CRITICAL]** Обновить ISSUES.md: версия v5.8.0 → v5.9.0, добавить примечание о v5.9.0 изменениях
3. **[HIGH]** Исправить Code-Doc Drift: "11 роутеров" → "13", "40 файлов" → "47 файлов" в CLAUDE.md
4. **[HIGH]** Создать `.claudeignore` для archive файлов:
   ```
   docs/audit_*.md
   docs/AUDIT_*.md
   docs/plans/
   docs/DEPLOY.md
   docs/ARCHITECTURE_v1.md
   MASTER_PLAN.md
   ```

### Сделать в следующей сессии:

5. **[HIGH]** Переместить docs/DEPLOY.md → docs/archive/DEPLOY_oracle_cloud.md
6. **[HIGH]** Переместить docs/ARCHITECTURE_v1.md → docs/archive/
7. **[MEDIUM]** Добавить ссылку на IMPROVEMENT_MASTER_PLAN_v2.md в CLAUDE.md
8. **[MEDIUM]** Сократить CLAUDE.md: убрать детальное дерево файлов (~200 строк), заменить ссылкой на docs/ARCHITECTURE.md
9. **[MEDIUM]** Добавить docs/README.md — индекс docs/

### Долгосрочно:

10. **[MEDIUM]** Cache-optimized reorder CLAUDE.md: архитектура/команды вверх, статус батчей вниз
11. **[LOW]** Создать docs/archive/ и переместить все orphan/stale файлы

---

## ПРОГНОЗ ЭКОНОМИИ

| До | После |
|----|-------|
| ~24,306 строк docs | ~16,000 строк (убрать archive, compact CLAUDE.md) |
| ~81,224 токенов (если читать всё) | ~20,000 токенов активных файлов |
| 41 MD файл всего | ~25 активных + ~16 в archive |
| 10+ orphan files | 0 orphan files |
| 557 строк CLAUDE.md | ~300 строк |

**Reduction: ~37% строк, ~75% токенов при целевой загрузке (без архивов)**

---

## VERIFICATION SCORE: 3/5

| Критерий | Статус | Причина |
|---------|--------|---------|
| Факты актуальны | PARTIAL | ISSUES.md = v5.8.0, реально v5.9.0; роутеры 11 вместо 13 |
| Нет дублей | FAIL | 6 cross-file дублей |
| SSOT соблюдён | PARTIAL | Архитектура в 3 файлах |
| Нет orphan файлов | FAIL | 10+ orphan docs |
| Нет битых ссылок | FAIL | DESIGN_DECISIONS_v1.md |

**Итог: 3/5 — есть stale секции, 3+ дубля, 1 битая ссылка**

---

*Отчёт сгенерирован: 2026-03-12 | docs-optimizer skill v1.0 | audit mode*
