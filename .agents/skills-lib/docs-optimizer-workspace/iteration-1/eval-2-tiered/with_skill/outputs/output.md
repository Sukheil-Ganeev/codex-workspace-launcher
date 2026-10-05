# TIERED LOADING — ПЛАН
**Проект:** TouristBotEcosystem (`D:/Downloads/TouristBotEcosystem/`)
**Стадия:** ACTIVE (последний коммит 2026-03-05, активная разработка)
**Дата анализа:** 2026-03-12

---

## ТЕКУЩЕЕ СОСТОЯНИЕ (до оптимизации)

### Метрики документации

| Файл | Строк | ~Токенов | Статус | Примечание |
|------|-------|----------|--------|------------|
| **CLAUDE.md** | 557 | ~2 228 | active | CRITICAL: 557 строк — сильно превышает целевые 250 |
| **CHANGELOG.md** | 1 088 | ~4 352 | active | Журнал — растёт, это норма |
| **ISSUES.md** | 110 | ~440 | active | Все закрыты, актуален |
| docs/IDEAL_MASTER_PLAN.md | 2 559 | ~10 236 | archive | READ ONLY, методология (не код) |
| docs/ARCHITECTURE_v1.md | 841 | ~3 364 | stale | Покрыто ARCHITECTURE.md, v1 = архив |
| docs/ARCHITECTURE.md | 424 | ~1 696 | active | Актуальная архитектура |
| docs/UX_DESIGN_v1.md | 1 103 | ~4 412 | stale | v1 = архив, создан 2026-03-03 |
| docs/BUTTON_DESIGN_GUIDE.md | 1 039 | ~4 156 | active | Стандарты — нужен по запросу |
| docs/IMPROVEMENT_MASTER_PLAN.md | 879 | ~3 516 | active | Roadmap UX — нужен при планировании |
| docs/IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1 020 | active | Более свежая версия |
| docs/DEPLOY_GCP.md | 1 062 | ~4 248 | active | Деплой GCP — нужен при деплое |
| docs/DEPLOY.md | 798 | ~3 192 | stale | Дублирует DEPLOY_GCP.md + SERVER_RUNBOOK.md |
| docs/SERVER_RUNBOOK.md | 361 | ~1 444 | active | Операции на сервере |
| docs/CODE_REVIEW_v1.md | 385 | ~1 540 | archive | Завершённый ревью (Phase 9) |
| docs/MANUAL_TESTS.md | 321 | ~1 284 | active | Нужен при тестировании |
| docs/AUDIT_2026-03-03.md | 332 | ~1 328 | archive | Завершённый аудит Phase 0 |
| docs/audit_ecosystem.md | 182 | ~728 | archive | Phase 0 аудит — закрыт |
| docs/audit_business.md | 136 | ~544 | archive | Phase 0 аудит — закрыт |
| docs/audit_content.md | 119 | ~476 | archive | Phase 0 аудит — закрыт |
| docs/audit_voice.md | 123 | ~492 | archive | Phase 0 аудит — закрыт |
| docs/audit_ai_lessons.md | 210 | ~840 | archive | Phase 0 аудит — закрыт |
| docs/audit_infra.md | 178 | ~712 | archive | Phase 0 аудит — закрыт |
| docs/COMMAND_AUDIT.md | 218 | ~872 | archive | Одноразовый аудит команд |
| docs/COMMAND_AUDIT_ADMIN.md | 262 | ~1 048 | archive | Одноразовый аудит команд |
| docs/DATABASE_COVERAGE_AUDIT.md | 337 | ~1 348 | archive | Одноразовый аудит (Session 10) |
| docs/DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | archive | Уроки первого деплоя — разово |
| docs/SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | archive | Одноразовый health snapshot |
| docs/CICD_SETUP.md | 105 | ~420 | active | CI/CD инструкции — нужен при настройке |
| docs/SENTRY_GUIDE.md | 187 | ~748 | active | Для нетехнического пользователя |
| docs/ADMIN_BOT_REDESIGN.md | 278 | ~1 112 | archive | Завершён (реализован в v5.8.0) |
| docs/WHATSAPP_BOT_REDESIGN.md | 522 | ~2 088 | archive | Завершён (реализован в v5.5.0) |
| docs/PROJECT_ACCOMPLISHMENTS.md | 628 | ~2 512 | archive | Ретроспектива — разово |
| docs/USER_GUIDE_admin.md | 390 | ~1 560 | active | Руководство для Марселя/Мухаммада |
| docs/USER_GUIDE_owner.md | 476 | ~1 904 | active | Руководство для Сухейля |
| docs/USER_GUIDE_staff.md | 145 | ~580 | active | Руководство для Камилы |
| docs/plans/2026-03-02-merge-vtb-cf-plan.md | 961 | ~3 844 | archive | Батч-план — реализован (Batch 1-4) |
| docs/plans/2026-03-02-unified-telegram-bot.md | 990 | ~3 960 | archive | Батч-план — реализован |

**СУММАРНО (до):** ~38 файлов, ~18 869 строк, **~75 456 токенов**

> Примечание: в каждой сессии Claude автоматически загружает из `.claude/`: настройки, инструкции. Сам CLAUDE.md загружается всегда через system-reminder. Остальные файлы — только при явном чтении.

---

## TIERED LOADING — КЛАССИФИКАЦИЯ

### TIER 1: ESSENTIAL (~800 токенов в сессии)

Загружается автоматически через system-reminder (CLAUDE.md). Цель: сделать CLAUDE.md компактным.

| Файл | Текущих токенов | Целевых токенов | Действие |
|------|----------------|----------------|----------|
| **CLAUDE.md** | ~2 228 | **~800** | Оптимизировать: убрать inline-контент → ссылки |

**Что должно остаться в CLAUDE.md:**
- Шапка: стек, Git, статус (5 строк)
- Quick Start (5 шагов)
- Таблица команд (компактная)
- Структура проекта (40 строк дерева, не 120)
- Статус Batch 1-4 (таблица, без деталей)
- Навигация: "Когда читать какой файл" (таблица 15 строк)
- Деплой: только IP + ссылка на `docs/SERVER_RUNBOOK.md`

**Что убрать из CLAUDE.md (вынести в docs/ или удалить):**
- Детальное дерево файлов с комментариями (сейчас ~120 строк → ссылка на ARCHITECTURE.md)
- Полный раздел "Деплой (GCP)" с 40+ строками → ссылка на SERVER_RUNBOOK.md
- Полный раздел "Cloudflare Tunnel" с инструкциями → ссылка на DEPLOY_GCP.md
- Таблица зависимостей requirements.txt (~25 строк) → убрать, она в файле
- AI Backends таблица → оставить только 2 строки (Primary/Fallback)
- Детальные статистики (250+ строк архитектурного дерева)

---

### TIER 2: ON-DEMAND (~500 токенов каждый, читать по запросу)

| Файл | ~Токенов | Когда читать |
|------|----------|--------------|
| CHANGELOG.md | ~4 352 | "что изменилось", история версий |
| ISSUES.md | ~440 | есть баги / проблемы |
| docs/ARCHITECTURE.md | ~1 696 | вопросы по архитектуре, новые модули |
| docs/BUTTON_DESIGN_GUIDE.md | ~4 156 | новые кнопки / callback_data |
| docs/IMPROVEMENT_MASTER_PLAN_v2.md | ~1 020 | планирование следующей сессии |
| docs/MANUAL_TESTS.md | ~1 284 | тестирование новых фич |
| docs/SERVER_RUNBOOK.md | ~1 444 | операции на GCP сервере |
| docs/DEPLOY_GCP.md | ~4 248 | полный деплой / re-provision |
| docs/CICD_SETUP.md | ~420 | настройка CI/CD |
| docs/SENTRY_GUIDE.md | ~748 | мониторинг ошибок |
| docs/USER_GUIDE_admin.md | ~1 560 | работа с admin-функциями |
| docs/USER_GUIDE_owner.md | ~1 904 | работа с owner-функциями |
| docs/USER_GUIDE_staff.md | ~580 | работа с staff-функциями |

**Суммарно ON-DEMAND:** ~23 852 токенов (читается только когда нужно)

---

### TIER 3: ARCHIVE (0 токенов автозагрузки, в .claudeignore)

| Файл | ~Токенов | Причина архивации |
|------|----------|-------------------|
| docs/IDEAL_MASTER_PLAN.md | ~10 236 | READ ONLY методология, не проектная doc |
| docs/ARCHITECTURE_v1.md | ~3 364 | Заменён docs/ARCHITECTURE.md |
| docs/UX_DESIGN_v1.md | ~4 412 | Заменён BUTTON_DESIGN_GUIDE.md + текущим кодом |
| docs/DEPLOY.md | ~3 192 | Дублируется в DEPLOY_GCP.md + SERVER_RUNBOOK.md |
| docs/CODE_REVIEW_v1.md | ~1 540 | Завершённый Phase 9 review |
| docs/AUDIT_2026-03-03.md | ~1 328 | Завершённый Phase 0 аудит |
| docs/audit_ecosystem.md | ~728 | Phase 0 аудит — закрыт |
| docs/audit_business.md | ~544 | Phase 0 аудит — закрыт |
| docs/audit_content.md | ~476 | Phase 0 аудит — закрыт |
| docs/audit_voice.md | ~492 | Phase 0 аудит — закрыт |
| docs/audit_ai_lessons.md | ~840 | Phase 0 аудит — закрыт |
| docs/audit_infra.md | ~712 | Phase 0 аудит — закрыт |
| docs/COMMAND_AUDIT.md | ~872 | Одноразовый аудит — исполнен |
| docs/COMMAND_AUDIT_ADMIN.md | ~1 048 | Одноразовый аудит — исполнен |
| docs/DATABASE_COVERAGE_AUDIT.md | ~1 348 | Session 10 аудит — исполнен |
| docs/DEPLOY_LESSONS_2026-03-03.md | ~664 | Уроки первого деплоя — разово |
| docs/SERVER_HEALTH_REPORT_2026-03-04.md | ~568 | Snapshot 2026-03-04 — устарел |
| docs/ADMIN_BOT_REDESIGN.md | ~1 112 | Реализован в v5.8.0 |
| docs/WHATSAPP_BOT_REDESIGN.md | ~2 088 | Реализован в v5.5.0 |
| docs/PROJECT_ACCOMPLISHMENTS.md | ~2 512 | Ретроспектива — архив |
| docs/IMPROVEMENT_MASTER_PLAN.md | ~3 516 | Заменён v2 версией |
| docs/plans/2026-03-02-merge-vtb-cf-plan.md | ~3 844 | Реализован (Batch 1-4) |
| docs/plans/2026-03-02-unified-telegram-bot.md | ~3 960 | Реализован (Batch 1-4) |

**Суммарно ARCHIVE:** ~49 444 токенов — исключаются из автозагрузки через .claudeignore

---

## ГЕНЕРИРУЕМЫЙ .claudeignore

```
# =============================================================
# TouristBotEcosystem .claudeignore
# Файлы, исключённые из автозагрузки Claude (архивы и устаревшие доки)
# Обновлено: 2026-03-12
# =============================================================

# --- Завершённые batch-планы (реализованы) ---
docs/plans/

# --- Phase 0 аудиты (все закрыты) ---
docs/audit_*.md
docs/AUDIT_2026-03-03.md

# --- Одноразовые аудиты (исполнены) ---
docs/COMMAND_AUDIT.md
docs/COMMAND_AUDIT_ADMIN.md
docs/DATABASE_COVERAGE_AUDIT.md

# --- Устаревшие v1 документы (заменены свежими) ---
docs/ARCHITECTURE_v1.md
docs/UX_DESIGN_v1.md
docs/CODE_REVIEW_v1.md

# --- Реализованные redesign-документы ---
docs/ADMIN_BOT_REDESIGN.md
docs/WHATSAPP_BOT_REDESIGN.md

# --- Одноразовые отчёты и ретроспективы ---
docs/DEPLOY_LESSONS_2026-03-03.md
docs/SERVER_HEALTH_REPORT_2026-03-04.md
docs/PROJECT_ACCOMPLISHMENTS.md

# --- Методология (не проектная документация) ---
docs/IDEAL_MASTER_PLAN.md

# --- Дублирующий деплой-файл (заменён GCP + Runbook) ---
docs/DEPLOY.md

# --- Устаревший roadmap (заменён v2) ---
docs/IMPROVEMENT_MASTER_PLAN.md

# --- Worktree артефакты (временные) ---
.claude/worktrees/

# --- Кэш и сборка ---
.pytest_cache/
__pycache__/
*.pyc
node_modules/
```

---

## ИТОГОВАЯ ЭКОНОМИЯ ТОКЕНОВ

| Категория | Текущая автозагрузка | После оптимизации |
|-----------|---------------------|-------------------|
| CLAUDE.md | ~2 228 | **~800** |
| CHANGELOG.md (не авто) | 0 | 0 |
| ISSUES.md (не авто) | 0 | 0 |
| Archive файлы (если Claude открывает вручную) | ~49 444 риска | **0** (в .claudeignore) |

**Авто-загрузка в каждой сессии:**
- До: ~2 228 токенов (CLAUDE.md)
- После: ~800 токенов (оптимизированный CLAUDE.md)
- **Экономия авто-загрузки: ~1 428 токенов (~64%) per сессия**

**Защита от случайной загрузки архивов:**
- Архивные файлы: ~49 444 токенов
- После .claudeignore: 0 токенов авторизованной загрузки
- **Защищено: ~49 444 токенов архивного контента**

**Типичная рабочая сессия (загружается реально):**
- Essential (CLAUDE.md): ~800 токенов
- 2-3 on-demand файла (в среднем): ~3 000 токенов
- **Итого рабочей сессии: ~3 800 токенов vs ~52 000 токенов (если всё загружено)**
- **Реальная экономия: ~93% от теоретического максимума**

---

## ЧТО ЗАГРУЖАЕТСЯ В КАЖДОЙ СЕССИИ (ПРЯМОЙ ОТВЕТ НА ВОПРОС)

### Сейчас (до оптимизации):

```
АВТОМАТИЧЕСКИ (system-reminder):
  ✅ CLAUDE.md — 557 строк / ~2 228 токенов  ← ВСЕГДА

ЕСЛИ Claude открывает вручную (риск):
  ⚠️  docs/IDEAL_MASTER_PLAN.md — ~10 236 токенов (методология!)
  ⚠️  docs/ARCHITECTURE_v1.md — ~3 364 токенов (устарело!)
  ⚠️  docs/plans/*.md — ~7 804 токенов (реализовано!)
  ⚠️  docs/audit_*.md — ~4 590 токенов (закрыто!)
  (и т.д.)
```

### После оптимизации:

```
АВТОМАТИЧЕСКИ (system-reminder):
  ✅ CLAUDE.md — ~200 строк / ~800 токенов  ← ВСЕГДА

BY NEED (читается только когда нужно):
  📋 CHANGELOG.md           — при вопросах "что менялось"
  📋 ISSUES.md              — при работе с багами
  📋 docs/ARCHITECTURE.md   — при архитектурных вопросах
  📋 docs/BUTTON_DESIGN_GUIDE.md — при работе с кнопками
  📋 docs/SERVER_RUNBOOK.md — при деплое
  📋 docs/USER_GUIDE_*.md   — при работе с ролями
  ... (13 файлов, читается только нужный)

NEVER (в .claudeignore):
  🚫 docs/IDEAL_MASTER_PLAN.md
  🚫 docs/ARCHITECTURE_v1.md
  🚫 docs/audit_*.md (6 файлов)
  🚫 docs/plans/*.md (2 файла)
  🚫 docs/CODE_REVIEW_v1.md
  🚫 docs/ADMIN_BOT_REDESIGN.md
  🚫 docs/WHATSAPP_BOT_REDESIGN.md
  🚫 docs/PROJECT_ACCOMPLISHMENTS.md
  🚫 ... (23 файла, ~49 444 токенов)
```

---

## РЕКОМЕНДАЦИИ (приоритет)

| Приоритет | Действие | Экономия |
|-----------|----------|----------|
| **HIGH** | Создать .claudeignore с архивами (список выше) | ~49 444 токенов защищено |
| **HIGH** | Оптимизировать CLAUDE.md: 557 → ~200 строк | ~1 428 токенов per сессия |
| **MEDIUM** | Переместить архивные доки в `docs/archive/` | Структурная чистота |
| **MEDIUM** | Удалить дублирующий docs/DEPLOY.md | ~3 192 токена |
| **LOW** | Убрать docs/IMPROVEMENT_MASTER_PLAN.md (есть v2) | ~3 516 токенов |
| **LOW** | Зарефакторить дерево архитектуры в CLAUDE.md → ссылка | ~800 токенов |

---

*Анализ выполнен по методологии docs-optimizer skill, режим `tiered`.*
*Токены рассчитаны как строки × 4 (среднее для смешанного RU/EN контента с кодом).*
