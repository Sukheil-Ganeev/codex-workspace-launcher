DOCS OPTIMIZER — ОТЧЁТ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Проект: TouristBotEcosystem
Путь: D:/Downloads/TouristBotEcosystem/
Стадия: ACTIVE (частые коммиты, CLAUDE.md обновляется каждую сессию — последний: 2026-03-05, текущая дата: 2026-03-12, 7 дней без обновления)
Verification Score: 3/5

---

## МЕТРИКИ

| Файл | Строк | ~Токенов | Статус | Проблемы |
|------|-------|---------|--------|----------|
| **КОРНЕВЫЕ ФАЙЛЫ** | | | | |
| CLAUDE.md | 557 | ~2,228 | active | AP-01 (context stuffing), AP-04 (cache order), AP-10, AP-16, AP-20 |
| CHANGELOG.md | 1,088 | ~4,352 | active | растёт нормально |
| ISSUES.md | 110 | ~440 | stale | обновлён 2026-03-04 (8 дней назад), 5 open Sentry issues без прогресса |
| MASTER_PLAN.md | 1,900 | ~7,600 | stale | дублирует docs/IDEAL_MASTER_PLAN.md, не упоминается в CLAUDE.md |
| README.md | 351 | ~1,404 | active | нормально |
| **АРХИТЕКТУРА** | | | | |
| docs/ARCHITECTURE.md | 424 | ~1,696 | stale | описывает v4.0/970 тестов, проект на v5.9/1263 тестах, Oracle Cloud вместо GCP |
| docs/ARCHITECTURE_v1.md | 841 | ~3,364 | stale | дублирует ARCHITECTURE.md, Oracle Cloud упоминание |
| docs/UX_DESIGN_v1.md | 1,103 | ~4,412 | active | большой, но оправдан — дизайн-документ |
| docs/BUTTON_DESIGN_GUIDE.md | 1,039 | ~4,156 | active | справочник, обновляется |
| docs/ADMIN_BOT_REDESIGN.md | 278 | ~1,112 | archive-candidate | реализовано в v5.8-5.9 |
| docs/WHATSAPP_BOT_REDESIGN.md | 522 | ~2,088 | archive-candidate | реализовано в Batch 5 |
| **ДЕПЛОЙ/ИНФРА** | | | | |
| docs/DEPLOY.md | 798 | ~3,192 | stale | описывает Oracle Cloud (не GCP), устарел |
| docs/DEPLOY_GCP.md | 1,062 | ~4,248 | stale | дублирует деплой-секцию CLAUDE.md, частично устарел |
| docs/SERVER_RUNBOOK.md | 361 | ~1,444 | active | актуальный операционный справочник |
| docs/SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | archive-candidate | разовый отчёт, устарел |
| docs/DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | archive-candidate | уроки деплоя — архив |
| docs/CICD_SETUP.md | 105 | ~420 | stale | устарел после настройки CI/CD |
| docs/SENTRY_GUIDE.md | 187 | ~748 | active | актуален |
| **АУДИТЫ** | | | | |
| docs/AUDIT_2026-03-03.md | 332 | ~1,328 | stale | v4.0 аудит, не архивирован |
| docs/audit_ai_lessons.md | 210 | ~840 | stale | Phase 0, не архивирован |
| docs/audit_business.md | 136 | ~544 | stale | Phase 0, не архивирован |
| docs/audit_content.md | 119 | ~476 | stale | Phase 0, не архивирован |
| docs/audit_ecosystem.md | 182 | ~728 | stale | Phase 0, не архивирован |
| docs/audit_infra.md | 178 | ~712 | stale | Phase 0, не архивирован |
| docs/audit_voice.md | 123 | ~492 | stale | Phase 0, не архивирован |
| docs/DATABASE_COVERAGE_AUDIT.md | 337 | ~1,348 | stale | v5.6.0 данные, не архивирован |
| docs/CODE_REVIEW_v1.md | 385 | ~1,540 | stale | Phase 9 аудит, не архивирован |
| docs/COMMAND_AUDIT.md | 218 | ~872 | stale | не архивирован |
| docs/COMMAND_AUDIT_ADMIN.md | 262 | ~1,048 | stale | не архивирован |
| **ПЛАНЫ/ROADMAPS** | | | | |
| docs/IDEAL_MASTER_PLAN.md | 2,559 | ~10,236 | active | READ ONLY методология |
| docs/IMPROVEMENT_MASTER_PLAN.md | 879 | ~3,516 | stale | v1.0 ЗАКРЫТ в v5.7.0, не архивирован |
| docs/IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1,020 | active | v2.0 ACTIVE |
| docs/plans/2026-03-02-merge-vtb-cf-plan.md | 961 | ~3,844 | archive-candidate | план выполнен (Batch 4 DONE) |
| docs/plans/2026-03-02-unified-telegram-bot.md | 990 | ~3,960 | archive-candidate | план выполнен |
| **ПОЛЬЗОВАТЕЛЬСКИЕ ГАЙДЫ** | | | | |
| docs/USER_GUIDE_owner.md | 476 | ~1,904 | active | актуален |
| docs/USER_GUIDE_admin.md | 390 | ~1,560 | active | актуален |
| docs/USER_GUIDE_staff.md | 145 | ~580 | active | актуален |
| docs/MANUAL_TESTS.md | 321 | ~1,284 | stale | описывает v4.3, проект на v5.9 |
| docs/PROJECT_ACCOMPLISHMENTS.md | 628 | ~2,512 | stale | v5.6.0, дублирует CHANGELOG |
| **ПРОЧЕЕ** | | | | |
| MASTER_PLAN.md (корень) | 1,900 | ~7,600 | orphan | не упомянут в CLAUDE.md, дублирует docs/IDEAL_MASTER_PLAN.md |
| deploy/README.md | 71 | ~284 | active | нормально |

**СУММАРНО (без .claude/worktrees, node_modules, .pytest_cache):** ~38 файлов, ~19,240 строк, ~76,960 токенов

---

## АНТИ-ПАТТЕРНЫ

| ID | Паттерн | Severity | Файл(ы) | Описание |
|----|---------|----------|--------|----------|
| AP-01 | Context Stuffing | HIGH | CLAUDE.md | 557 строк (~2,228 токенов) — ниже критического, но секция "Архитектура" занимает 319 строк (полное дерево файлов) вместо ссылки на docs/ARCHITECTURE.md |
| AP-02 | Stale Docs | HIGH | docs/ARCHITECTURE.md, docs/ARCHITECTURE_v1.md, docs/DEPLOY.md | Описывают Oracle Cloud (устарело), v4.0/970 тестов вместо актуального v5.9/1263 |
| AP-03 | Orphan Docs | MEDIUM | MASTER_PLAN.md (корень), docs/SERVER_HEALTH_REPORT_2026-03-04.md, docs/DEPLOY_LESSONS_2026-03-03.md | Не упомянуты в CLAUDE.md, не индексированы |
| AP-04 | Cache-Hostile Order | MEDIUM | CLAUDE.md | Динамические секции "Статус проекта" (строки 7-17, меняется каждую сессию) находятся выше статических "Архитектура", "Команды" |
| AP-09 | Code-Doc Drift | HIGH | docs/ARCHITECTURE.md, docs/ARCHITECTURE_v1.md, docs/DEPLOY.md, docs/MANUAL_TESTS.md | ARCHITECTURE.md указывает 5 активных ботов — реально 3. DEPLOY.md описывает Oracle Cloud, деплой на GCP. MANUAL_TESTS.md — v4.3 сценарии для v5.9 кода |
| AP-10 | Monolithic Status | LOW | CLAUDE.md | Секция Batch 4 description — одна строка из 800+ символов |
| AP-11 | Duplicate Commands | MEDIUM | CLAUDE.md + docs/DEPLOY.md + docs/DEPLOY_GCP.md + docs/SERVER_RUNBOOK.md | Команды docker compose, деплой-инструкции продублированы в 3-4 файлах |
| AP-13 | Flat Hierarchy | MEDIUM | docs/ | Отсутствует docs/audits/ (8 аудит-файлов в корне docs/), docs/archive/ для устаревших планов |
| AP-14 | Missing Quick Start | MEDIUM | CLAUDE.md | Нет секции "Быстрый старт" в начале файла — сразу статус проекта |
| AP-16 | Cross-File Duplication | HIGH | CLAUDE.md ↔ docs/DEPLOY_GCP.md ↔ docs/SERVER_RUNBOOK.md | IP-адрес GCP (34.107.127.155), параметры VM, Cloudflare Tunnel UUID в 3+ файлах |
| AP-17 | (нет MEMORY.md) | INFO | — | MEMORY.md отсутствует — не нарушение |
| AP-18 | Stale Issues | MEDIUM | ISSUES.md | 5 Sentry issues (SEN-01..05) открыты с 2026-03-04 (8 дней), версия кода в шапке v5.8.0 при текущем v5.9.0 |
| AP-19 | Roadmap Rot | MEDIUM | docs/IMPROVEMENT_MASTER_PLAN.md | v1.0 помечен как ACTIVE, но по CHANGELOG закрыт в v5.7.0 |
| AP-20 | Protocol Sprawl | MEDIUM | CLAUDE.md | Секция "Cloudflare Tunnel" (строки 498-544, 47 строк пошаговых инструкций) в CLAUDE.md — уже выполнено, должно быть в docs/SERVER_RUNBOOK.md |

---

## ДУБЛИРОВАНИЕ (SSOT violations)

| Факт | Найден в | Рекомендуемый источник правды |
|------|----------|-------------------------------|
| GCP IP, VM-параметры, Cloudflare UUID | CLAUDE.md + docs/DEPLOY_GCP.md + docs/SERVER_RUNBOOK.md | CLAUDE.md (кратко) + docs/SERVER_RUNBOOK.md (детали) |
| Команды docker compose / деплой | CLAUDE.md + docs/DEPLOY.md + docs/DEPLOY_GCP.md + docs/SERVER_RUNBOOK.md | CLAUDE.md — ссылка на docs/SERVER_RUNBOOK.md |
| Архитектурное дерево (318 строк) | CLAUDE.md (строки 37-353) + docs/ARCHITECTURE.md + docs/ARCHITECTURE_v1.md | docs/ARCHITECTURE.md — одна версия |
| Статус батчей/прогресс | CLAUDE.md + MASTER_PLAN.md (корень) + docs/PROJECT_ACCOMPLISHMENTS.md + CHANGELOG.md | CLAUDE.md (таблица) — ссылка на CHANGELOG.md |
| Количество тестов (1263) | CLAUDE.md (строки 355-370) + docs/ARCHITECTURE.md (970 — устарело!) | CLAUDE.md |
| Количество активных ботов | CLAUDE.md говорит "3 активных" + docs/ARCHITECTURE.md говорит "5 ботов" | CLAUDE.md (3 активных) |
| Пошаговые инструкции Cloudflare Tunnel | CLAUDE.md (строки 506-543) + docs/SERVER_RUNBOOK.md | docs/SERVER_RUNBOOK.md — только ссылка в CLAUDE.md |

---

## КЛАССИФИКАЦИЯ ФАЙЛОВ ПО СТАТУСУ

### Active (нужны, актуальны)
- CLAUDE.md, CHANGELOG.md, ISSUES.md (с оговорками), README.md
- docs/BUTTON_DESIGN_GUIDE.md, docs/UX_DESIGN_v1.md, docs/SENTRY_GUIDE.md
- docs/SERVER_RUNBOOK.md, docs/USER_GUIDE_*.md, docs/IDEAL_MASTER_PLAN.md
- docs/IMPROVEMENT_MASTER_PLAN_v2.md, deploy/README.md

### Stale (нужны, но устарели — требуют обновления)
- docs/ARCHITECTURE.md (v4.0, Oracle Cloud → надо обновить до v5.9, GCP)
- docs/ARCHITECTURE_v1.md (то же, дублирует ARCHITECTURE.md)
- docs/DEPLOY.md (Oracle Cloud — весь устарел)
- docs/MANUAL_TESTS.md (v4.3 сценарии)
- docs/PROJECT_ACCOMPLISHMENTS.md (v5.6.0)
- ISSUES.md (версия кода v5.8.0, должна быть v5.9.0)

### Archive-candidate (выполнено/разовое — переместить в docs/archive/)
- docs/IMPROVEMENT_MASTER_PLAN.md (v1.0 ЗАКРЫТ)
- docs/plans/2026-03-02-merge-vtb-cf-plan.md (Batch 4 DONE)
- docs/plans/2026-03-02-unified-telegram-bot.md (выполнен)
- docs/SERVER_HEALTH_REPORT_2026-03-04.md (разовый отчёт)
- docs/DEPLOY_LESSONS_2026-03-03.md (уроки — архив)
- docs/ADMIN_BOT_REDESIGN.md (реализовано в v5.8-5.9)
- docs/WHATSAPP_BOT_REDESIGN.md (реализовано в Batch 5)
- docs/DEPLOY_GCP.md (дублирует CLAUDE.md + SERVER_RUNBOOK)
- MASTER_PLAN.md (корень) (orphan, дублирует IDEAL_MASTER_PLAN.md)

### Dead/Orphan (не упоминаются, нет ссылок)
- docs/AUDIT_2026-03-03.md + 6 × audit_*.md (Phase 0 — не в docs/audits/)
- docs/DATABASE_COVERAGE_AUDIT.md, docs/CODE_REVIEW_v1.md
- docs/COMMAND_AUDIT.md, docs/COMMAND_AUDIT_ADMIN.md
- MASTER_PLAN.md (корень) — не упомянут в CLAUDE.md

---

## РЕКОМЕНДАЦИИ

### HIGH priority

1. **[HIGH] Вынести архитектурное дерево из CLAUDE.md** (AP-01, AP-16)
   Строки 37-353 в CLAUDE.md — полное дерево из 319 строк (~1,276 токенов). Заменить на:
   `**Архитектура:** docs/ARCHITECTURE.md — полная структура проекта`
   Это сократит CLAUDE.md примерно до 240 строк (~960 токенов).

2. **[HIGH] Исправить stale docs с Oracle Cloud → GCP** (AP-02, AP-09)
   - docs/DEPLOY.md: полностью устарел (Oracle Cloud). Либо обновить под GCP, либо архивировать.
   - docs/ARCHITECTURE.md: обновить до v5.9, 1263 тестов, 3 активных бота (не 5), GCP.
   - docs/ARCHITECTURE_v1.md: архивировать — дублирует ARCHITECTURE.md.

3. **[HIGH] Обновить ISSUES.md до v5.9.0** (AP-18)
   Версия кода в шапке: v5.8.0 → v5.9.0. Проверить SEN-01..05 — 8 дней без обновления.

4. **[HIGH] Убрать Cloudflare Tunnel инструкцию из CLAUDE.md** (AP-20)
   Строки 498-544 (47 строк пошаговых инструкций настройки) уже выполнены и должны жить в docs/SERVER_RUNBOOK.md. В CLAUDE.md оставить только статус: `Cloudflare Tunnel: ✅ настроен → docs/SERVER_RUNBOOK.md`.

### MEDIUM priority

5. **[MEDIUM] Создать docs/archive/ и переместить завершённые документы** (AP-13)
   Переместить (не удалять):
   - docs/IMPROVEMENT_MASTER_PLAN.md (v1.0 закрыт)
   - docs/plans/ оба файла (планы выполнены)
   - docs/SERVER_HEALTH_REPORT_2026-03-04.md, docs/DEPLOY_LESSONS_2026-03-03.md
   - docs/ADMIN_BOT_REDESIGN.md, docs/WHATSAPP_BOT_REDESIGN.md (реализованы)

6. **[MEDIUM] Создать docs/audits/ и переместить аудит-файлы** (AP-13)
   8 аудит-файлов (AUDIT_2026-03-03.md, 6×audit_*.md, DATABASE_COVERAGE_AUDIT.md) лежат в корне docs/ без иерархии. Переместить в docs/audits/ — там они READ ONLY, не источник правды.

7. **[MEDIUM] Добавить Quick Start в начало CLAUDE.md** (AP-14)
   Первая секция сейчас — "Статус проекта" (динамическое). Вставить перед ней 5-шаговый Quick Start:
   ```
   ## Quick Start
   1. Запустить PostgreSQL: `docker compose up -d`
   2. Запустить бот: `python -m bots.telegram_main.main`
   3. Тесты: `pytest -q`
   4. Проблемы: ISSUES.md
   5. Деплой: docs/SERVER_RUNBOOK.md
   ```

8. **[MEDIUM] Исправить порядок секций в CLAUDE.md** (AP-04)
   Текущий порядок (сверху вниз): Статус проекта (динамическое) → Стандарты → Источники → Архитектура (статическое) → Статистика → Команды → AI → Деплой
   Оптимальный: Quick Start → Стек/Git → Команды → Архитектура → AI → Деплой → Статус → Открытые проблемы

9. **[MEDIUM] Создать .claudeignore** (отсутствует)
   Файл отсутствует. Создать для исключения архивов и node_modules:
   ```
   docs/archive/
   docs/audits/
   docs/node_modules/
   MASTER_PLAN.md
   docs/PROJECT_ACCOMPLISHMENTS.md
   ```

10. **[MEDIUM] Разрешить конфликт MASTER_PLAN.md в корне** (AP-03)
    1,900 строк, статус "В ПЛАНИРОВАНИИ" (2026-03-03), не упомянут в CLAUDE.md. Либо добавить ссылку и дату обновления, либо архивировать (содержание покрыто docs/IDEAL_MASTER_PLAN.md).

### LOW priority

11. **[LOW] Архивировать docs/DEPLOY_GCP.md** (AP-16)
    1,062 строки. Содержание дублируется в CLAUDE.md (секция "Деплой GCP") и docs/SERVER_RUNBOOK.md. Если нужно оставить как туториал "с нуля" — добавить ссылку из CLAUDE.md. Если нет — архивировать.

12. **[LOW] Обновить PROJECT_ACCOMPLISHMENTS.md или архивировать** (AP-15)
    628 строк, дата v5.6.0. Дублирует CHANGELOG.md по сути. Либо обновить до v5.9, либо считать историческим документом и архивировать.

13. **[LOW] Проверить MANUAL_TESTS.md** (AP-09)
    321 строка, сценарии для v4.3. Обновить или архивировать — тестов стало 1263 (было 970 на момент создания).

---

## ПРОГНОЗ ЭКОНОМИИ

| Действие | До | После | Сокращение |
|----------|-----|-------|-----------|
| Убрать дерево архитектуры из CLAUDE.md | 557 строк | ~240 строк | -317 строк (-57%) |
| Архивировать выполненные планы (5 файлов) | 3,851 строк | 0 (в archive) | из автозагрузки |
| Убрать Cloudflare Tunnel инструкцию из CLAUDE.md | — | -47 строк | — |
| **CLAUDE.md итого** | **557 строк (~2,228 токенов)** | **~190 строк (~760 токенов)** | **-66%** |
| **Суммарно docs (активная загрузка)** | **~19,240 строк (~76,960 токенов)** | **~10,500 строк (~42,000 токенов)** | **-45%** |

---

## СТАТУС ISSUES.md

| Статус | Количество |
|--------|-----------|
| 🔴 ОТКРЫТ | 5 (SEN-01..05 — Sentry, без обновлений 8 дней) |
| ⚪ DORMANT | 1 (DB-01) |
| ✅ ЗАКРЫТ | 30+ |

ISSUES.md в целом в хорошем состоянии — формат соблюдён, единственный источник правды используется корректно. Нужно обновить версию кода в шапке (v5.8.0 → v5.9.0) и проверить SEN-01..05.

---

## ИТОГОВАЯ ОЦЕНКА

**Verification Score: 3/5**

**Обоснование:**
- (+) CLAUDE.md регулярно обновляется (каждую сессию), формат соблюдён
- (+) ISSUES.md существует как SSOT для проблем, формат соблюдён
- (+) CHANGELOG.md ведётся корректно, история не смешана со статусом
- (+) .claudeignore нет, но docs/ реально не загружается автоматически
- (-) docs/ARCHITECTURE.md содержит активно вводящие в заблуждение данные (Oracle Cloud, 5 ботов, 970 тестов) при реальном GCP, 3 ботах, 1263 тестах — это AP-09 High
- (-) docs/DEPLOY.md полностью устарел (Oracle Cloud вся инфраструктура)
- (-) 319 строк дерева файлов в CLAUDE.md вместо ссылки на docs/ — это значимый bloat
- (-) 8 аудит-файлов лежат неструктурированно в docs/ без docs/audits/, без .claudeignore
- (-) ISSUES.md не обновлялся с момента выхода v5.9.0 (версия кода застряла на v5.8.0)
- (-) Нет .claudeignore — архивные файлы потенциально загружаются в контекст

**Стадия проекта: ACTIVE → переходит в STABLE**
Все Batch завершены (1-6), деплой работает. Основная разработка позади. Документация накопила стандартный "после-релизный" долг — устаревшие планы, старые аудиты, stale архитектурные доки.

---

*Отчёт создан: 2026-03-12 | Режим: analyze | Скилл: docs-optimizer v1.0*
