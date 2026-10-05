# Docs Optimizer — Tiered Loading Report
**Проект:** TouristBotEcosystem (`D:/Downloads/TouristBotEcosystem/`)
**Режим:** `tiered` — классификация по тирам и экономия токенов
**Стадия:** STABLE (Batch 1-6 завершены, активная разработка не ведётся)
**Overall Documentation Quality Score: 2/5**

> Документация значительно разрослась, содержит множество orphan docs, устаревшие файлы и превышает рекомендованные размеры по всем показателям.

---

## PARENT CLAUDE.md CHAIN

| Уровень | Файл | Строк | ~Токенов |
|---------|------|-------|----------|
| `~/.claude/` | CLAUDE.md | 139 | ~556 |
| `D:/Downloads/` | CLAUDE.md | 681 | ~2,724 |
| `D:/Downloads/TouristBotEcosystem/` | CLAUDE.md | 557 | ~2,228 |
| **СУММАРНО при старте** | | **1,377** | **~5,508** |

> **Внимание:** Родительский `D:/Downloads/CLAUDE.md` (~2,724 токенов) загружается автоматически для ВСЕХ проектов в Downloads/ и больше проектного CLAUDE.md по токенам (~2,228). Это увеличивает стартовый контекст на 22%.

---

## МЕТРИКИ ФАЙЛОВ

### Корень проекта

| Файл | Строк | ~Токенов | Статус |
|------|-------|----------|--------|
| CLAUDE.md | 557 | ~2,228 | ⚠️ HIGH (>400 строк, >2.5K токенов) |
| CHANGELOG.md | 1,088 | ~4,352 | Журнал истории |
| MASTER_PLAN.md | 1,900 | ~7,600 | Orphan: нет ссылок из CLAUDE.md |
| README.md | 351 | ~1,404 | Orphan: нет ссылок из CLAUDE.md |
| ISSUES.md | 110 | ~440 | Актуальный список проблем |

### docs/ — полный список

| Файл | Строк | ~Токенов | Ссылки из CLAUDE.md |
|------|-------|----------|---------------------|
| IDEAL_MASTER_PLAN.md | 2,559 | ~10,236 | Нет (Orphan) |
| UX_DESIGN_v1.md | 1,103 | ~4,412 | Нет (Orphan) |
| DEPLOY_GCP.md | 1,062 | ~4,248 | Нет (Orphan) |
| BUTTON_DESIGN_GUIDE.md | 1,039 | ~4,156 | ✅ Да |
| IMPROVEMENT_MASTER_PLAN.md | 879 | ~3,516 | ✅ Да |
| ARCHITECTURE_v1.md | 841 | ~3,364 | Нет (Orphan) |
| DEPLOY.md | 798 | ~3,192 | Нет (Orphan) |
| PROJECT_ACCOMPLISHMENTS.md | 628 | ~2,512 | Нет (Orphan) |
| WHATSAPP_BOT_REDESIGN.md | 522 | ~2,088 | Нет (Orphan) |
| USER_GUIDE_owner.md | 476 | ~1,904 | Нет (Orphan) |
| ARCHITECTURE.md | 424 | ~1,696 | Нет (Orphan) |
| USER_GUIDE_admin.md | 390 | ~1,560 | Нет (Orphan) |
| CODE_REVIEW_v1.md | 385 | ~1,540 | Нет (Orphan) |
| SERVER_RUNBOOK.md | 361 | ~1,444 | Нет (Orphan) |
| DATABASE_COVERAGE_AUDIT.md | 337 | ~1,348 | Нет (Orphan) |
| AUDIT_2026-03-03.md | 332 | ~1,328 | Нет (Orphan) |
| MANUAL_TESTS.md | 321 | ~1,284 | Нет (Orphan) |
| ADMIN_BOT_REDESIGN.md | 278 | ~1,112 | Нет (Orphan) |
| COMMAND_AUDIT_ADMIN.md | 262 | ~1,048 | Нет (Orphan) |
| IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1,020 | Нет (Orphan) |
| COMMAND_AUDIT.md | 218 | ~872 | Нет (Orphan) |
| audit_ai_lessons.md | 210 | ~840 | Нет (Orphan) |
| SENTRY_GUIDE.md | 187 | ~748 | Нет (Orphan) |
| audit_ecosystem.md | 182 | ~728 | Нет (Orphan) |
| audit_infra.md | 178 | ~712 | Нет (Orphan) |
| DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | Нет (Orphan) |
| USER_GUIDE_staff.md | 145 | ~580 | Нет (Orphan) |
| SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | Нет (Orphan) |
| audit_business.md | 136 | ~544 | Нет (Orphan) |
| audit_voice.md | 123 | ~492 | Нет (Orphan) |
| audit_content.md | 119 | ~476 | Нет (Orphan) |
| CICD_SETUP.md | 105 | ~420 | Нет (Orphan) |
| plans/2026-03-02-merge-vtb-cf-plan.md | 961 | ~3,844 | ✅ Да |
| plans/2026-03-02-unified-telegram-bot.md | 990 | ~3,960 | Нет (Orphan) |

**Итого docs/:** ~17,114 строк / ~68,456 токенов
**Итого всё:** ~21,199 строк / ~84,796 токенов

---

## PHASE 3: SYNTHESIS — TIER CLASSIFICATION

### Tier-таблица

| Tier | File | Строк | ~Токенов | Reason |
|------|------|-------|----------|--------|
| Essential | CLAUDE.md | 557 | ~2,228 | Навигационный хаб, загружается каждую сессию |
| Essential | ISSUES.md | 110 | ~440 | Актуальный список открытых проблем |
| On-demand | CHANGELOG.md | 1,088 | ~4,352 | Читать при анализе истории изменений |
| On-demand | docs/BUTTON_DESIGN_GUIDE.md | 1,039 | ~4,156 | Читать при создании кнопок и UI |
| On-demand | docs/IMPROVEMENT_MASTER_PLAN.md | 879 | ~3,516 | Читать при работе над UX улучшениями |
| On-demand | docs/DEPLOY_GCP.md | 1,062 | ~4,248 | Читать при деплое/настройке сервера |
| On-demand | docs/ARCHITECTURE.md | 424 | ~1,696 | Читать при изменениях архитектуры |
| On-demand | docs/SERVER_RUNBOOK.md | 361 | ~1,444 | Читать при инцидентах на сервере |
| On-demand | docs/MANUAL_TESTS.md | 321 | ~1,284 | Читать перед релизом (тестирование) |
| On-demand | docs/CICD_SETUP.md | 105 | ~420 | Читать при настройке CI/CD |
| On-demand | docs/plans/2026-03-02-merge-vtb-cf-plan.md | 961 | ~3,844 | Читать при работе с планом миграции |
| Archive | MASTER_PLAN.md | 1,900 | ~7,600 | Orphan: нет ссылок из CLAUDE.md |
| Archive | README.md | 351 | ~1,404 | Orphan: нет ссылок, дублирует CLAUDE.md |
| Archive | docs/IDEAL_MASTER_PLAN.md | 2,559 | ~10,236 | Orphan + READ ONLY методология |
| Archive | docs/UX_DESIGN_v1.md | 1,103 | ~4,412 | Orphan + v1 (устарел) |
| Archive | docs/ARCHITECTURE_v1.md | 841 | ~3,364 | Orphan + v1 (superseded by ARCHITECTURE.md) |
| Archive | docs/DEPLOY.md | 798 | ~3,192 | Orphan: заменён docs/DEPLOY_GCP.md |
| Archive | docs/PROJECT_ACCOMPLISHMENTS.md | 628 | ~2,512 | Orphan: история, не нужна в работе |
| Archive | docs/WHATSAPP_BOT_REDESIGN.md | 522 | ~2,088 | Orphan: redesign документ |
| Archive | docs/USER_GUIDE_owner.md | 476 | ~1,904 | Orphan: пользовательский гайд |
| Archive | docs/USER_GUIDE_admin.md | 390 | ~1,560 | Orphan: пользовательский гайд |
| Archive | docs/CODE_REVIEW_v1.md | 385 | ~1,540 | Orphan + v1 code review |
| Archive | docs/DATABASE_COVERAGE_AUDIT.md | 337 | ~1,348 | Orphan: аудит-файл |
| Archive | docs/AUDIT_2026-03-03.md | 332 | ~1,328 | Orphan: аудит-архив |
| Archive | docs/ADMIN_BOT_REDESIGN.md | 278 | ~1,112 | Orphan: redesign документ |
| Archive | docs/COMMAND_AUDIT_ADMIN.md | 262 | ~1,048 | Orphan: аудит-файл |
| Archive | docs/IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1,020 | Orphan: дублирует IMPROVEMENT_MASTER_PLAN.md |
| Archive | docs/COMMAND_AUDIT.md | 218 | ~872 | Orphan: аудит-файл |
| Archive | docs/audit_ai_lessons.md | 210 | ~840 | Orphan: Phase 0 аудит |
| Archive | docs/SENTRY_GUIDE.md | 187 | ~748 | Orphan: нет ссылок |
| Archive | docs/audit_ecosystem.md | 182 | ~728 | Orphan: Phase 0 аудит |
| Archive | docs/audit_infra.md | 178 | ~712 | Orphan: Phase 0 аудит |
| Archive | docs/DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | Orphan: одноразовый отчёт |
| Archive | docs/USER_GUIDE_staff.md | 145 | ~580 | Orphan: пользовательский гайд |
| Archive | docs/SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | Orphan: одноразовый отчёт |
| Archive | docs/audit_business.md | 136 | ~544 | Orphan: Phase 0 аудит |
| Archive | docs/audit_voice.md | 123 | ~492 | Orphan: Phase 0 аудит |
| Archive | docs/audit_content.md | 119 | ~476 | Orphan: Phase 0 аудит |
| Archive | docs/plans/2026-03-02-unified-telegram-bot.md | 990 | ~3,960 | Orphan: plan документ без ссылок |

---

## ЧТО ЗАГРУЖАЕТСЯ В КАЖДОЙ СЕССИИ

### До оптимизации (текущее состояние)

| Тир | Файлов | Строк | ~Токенов |
|-----|--------|-------|----------|
| Auto-load (CLAUDE.md) | 1 | 557 | ~2,228 |
| Auto-load (parent chain) | 2 | 820 | ~3,280 |
| **ИТОГО авто-загрузка** | **3** | **1,377** | **~5,508** |

Типичная рабочая сессия (CLAUDE.md + 3-4 on-demand + ISSUES.md):
~2,228 + ~440 + ~4,248 + ~3,516 + ~4,156 = **~14,588 токенов**

### После оптимизации (с применением тиров)

| Тир | Файлов | ~Токенов | Действие |
|-----|--------|----------|---------|
| Essential (авто) | 2 | ~2,668 | CLAUDE.md (~800 после оптимизации) + ISSUES.md |
| On-demand (по запросу) | 9 | ~25,960 | Загружать только когда нужно |
| Archive (0 токенов) | 26 | ~51,584 | Перенести в docs/archive/ + .claudeignore |

Типичная рабочая сессия после оптимизации:
~800 + ~440 + ~4,248 (если деплой) = **~5,488 токенов**

**Экономия в типичной сессии: ~62% (14,588 → 5,488 токенов)**

---

## ОБНАРУЖЕННЫЕ АНТИ-ПАТТЕРНЫ

| Код | Файл | Описание | Severity |
|-----|------|----------|----------|
| AP-01 | CLAUDE.md | Context Stuffing: 557 строк / ~2,228 токенов (цель: <250 строк / <1.2K токенов) | HIGH |
| AP-03 | 26 файлов | Orphan Docs: большинство docs/*.md не имеют ссылок ни из CLAUDE.md ни из других nav документов | CRITICAL |
| AP-10 | CLAUDE.md | Monolithic Status: детальные описания Cloudflare Tunnel (30+ строк) вместо краткой таблицы | MEDIUM |
| AP-11 | CLAUDE.md | Duplicate Commands: команды деплоя дублируются в docs/DEPLOY_GCP.md | MEDIUM |
| AP-13 | docs/ | Flat Hierarchy: все 32 файла в одной папке docs/, нет подпапок по типам | MEDIUM |
| AP-16 | CLAUDE.md ↔ docs/DEPLOY_GCP.md | Cross-File Duplication: GCP параметры (IP, VM, зона, деплой-команды) | HIGH |
| AP-20 | CLAUDE.md | Protocol Sprawl: Cloudflare Tunnel (шаги 1-4 + альтернативы) = 40+ строк инструкций в CLAUDE.md | MEDIUM |

---

## CONTENT DRIFT

| Файл | Проблема | Severity |
|------|---------|----------|
| docs/ARCHITECTURE_v1.md | "v1" — superseded, ARCHITECTURE.md актуален | MEDIUM |
| docs/UX_DESIGN_v1.md | "v1" — устарел, redesign уже применён | HIGH |
| docs/CODE_REVIEW_v1.md | "v1" код-ревью проведён, исправления применены в Batch 5-6 | MEDIUM |
| docs/IMPROVEMENT_MASTER_PLAN_v2.md | Дублирует IMPROVEMENT_MASTER_PLAN.md с минорными отличиями | MEDIUM |

---

## ORPHAN DOCS — AP-F04

```
AP-F04 | MASTER_PLAN.md | Нет ссылок из CLAUDE.md, orphan root файл | Severity: HIGH
AP-F04 | docs/IDEAL_MASTER_PLAN.md | READ ONLY + orphan, не используется в сессиях | Severity: HIGH
AP-F04 | docs/DEPLOY.md | Orphan: заменён GCP деплоем, но не помечен как архив | Severity: HIGH
AP-F04 | docs/plans/2026-03-02-unified-telegram-bot.md | Orphan plan без ссылок | Severity: MEDIUM
```

---

## РЕКОМЕНДАЦИИ

### HIGH priority

1. **Оптимизировать CLAUDE.md** — сократить с 557 до ~250 строк (~2,228 → ~1,000 токенов):
   - Убрать детальные инструкции Cloudflare Tunnel → `docs/DEPLOY_GCP.md`
   - Убрать полный список зависимостей → `requirements.txt`
   - Сократить архитектурное дерево до ключевых модулей

2. **Перенести 26 архивных файлов** в `docs/archive/` и добавить в `.claudeignore`:
   - Все `audit_*.md`, `*_v1.md`, `*REDESIGN*.md`, одноразовые отчёты
   - Сохранить физически — не удалять!

3. **Добавить ссылки** в CLAUDE.md на DEPLOY_GCP.md, ARCHITECTURE.md, SERVER_RUNBOOK.md (сейчас orphan)

### MEDIUM priority

4. **Создать .claudeignore** (см. ниже)
5. **Реструктурировать docs/** на подпапки: `docs/guides/`, `docs/audits/`, `docs/plans/`, `docs/archive/`
6. **Добавить MASTER_PLAN.md в CLAUDE.md** или перенести в Archive

---

## ГЕНЕРИРУЕМЫЙ .claudeignore

```
# TouristBotEcosystem — .claudeignore
# Автоматически создан docs-optimizer

# === ARCHIVE TIER: Phase 0 аудит-файлы ===
docs/audit_ai_lessons.md
docs/audit_ecosystem.md
docs/audit_infra.md
docs/audit_business.md
docs/audit_voice.md
docs/audit_content.md
docs/AUDIT_2026-03-03.md

# === ARCHIVE TIER: Одноразовые отчёты ===
docs/DEPLOY_LESSONS_2026-03-03.md
docs/SERVER_HEALTH_REPORT_2026-03-04.md
docs/DATABASE_COVERAGE_AUDIT.md
docs/COMMAND_AUDIT.md
docs/COMMAND_AUDIT_ADMIN.md
docs/CODE_REVIEW_v1.md
docs/PROJECT_ACCOMPLISHMENTS.md

# === ARCHIVE TIER: Устаревшие версии ===
docs/ARCHITECTURE_v1.md
docs/UX_DESIGN_v1.md
docs/IMPROVEMENT_MASTER_PLAN_v2.md
docs/DEPLOY.md

# === ARCHIVE TIER: Redesign документы ===
docs/WHATSAPP_BOT_REDESIGN.md
docs/ADMIN_BOT_REDESIGN.md

# === ARCHIVE TIER: User guides (on request only) ===
docs/USER_GUIDE_owner.md
docs/USER_GUIDE_admin.md
docs/USER_GUIDE_staff.md

# === ARCHIVE TIER: Orphan планы ===
docs/IDEAL_MASTER_PLAN.md
docs/plans/2026-03-02-unified-telegram-bot.md

# === ROOT ORPHANS ===
MASTER_PLAN.md
README.md

# === SYSTEM ===
backups/
logs/
temp/
*.bak
*.log
```

---

## ИТОГ: ПРОГНОЗ ЭКОНОМИИ

| Метрика | До | После | Экономия |
|---------|-----|-------|---------|
| Авто-загрузка (CLAUDE.md) | ~2,228 токенов | ~800 токенов | **-64%** |
| Файлов в docs/ | 34 | 10 в активном тире | -71% |
| Orphan файлов | 26 | 0 | -100% |
| Типичная сессия | ~14,588 токенов | ~5,488 токенов | **-62%** |
| docs/ строк всего | ~17,114 | ~25,960 (on-demand, не авто) | archived |

> **Стратегия Archive != Delete.** Все 26 файлов архивируются в `docs/archive/` и добавляются в `.claudeignore`. Физически они остаются, но не потребляют токены в сессии.
