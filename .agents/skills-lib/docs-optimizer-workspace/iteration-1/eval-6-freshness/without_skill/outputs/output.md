# Анализ свежести документации — TouristBotEcosystem

**Дата анализа:** 2026-03-12
**Последний коммит:** 2026-03-05
**Текущая версия:** v5.9.0
**Всего .md файлов:** 41 (в основном репо, без .claude/worktrees/)

---

## Итог

Все файлы документации были последний раз обновлены в период **2026-03-02 — 2026-03-05**, то есть **7–10 дней назад**. За это время вышли версии v5.7.0 → v5.8.0 → v5.9.0 с существенными изменениями в коде, которые не отражены в ряде "живых" документов.

---

## Таблица: все .md файлы по дате последнего обновления

| Файл | Последнее обновление (git) | Дней назад | Коммитов | Тип |
|------|---------------------------|------------|----------|-----|
| `CHANGELOG.md` | 2026-03-05 | 7 | 35 | Живой |
| `CLAUDE.md` | 2026-03-05 | 7 | 41 | Живой |
| `ISSUES.md` | 2026-03-04 | 8 | 27 | Живой |
| `README.md` | 2026-03-04 | 8 | 2 | Живой |
| `docs/ADMIN_BOT_REDESIGN.md` | 2026-03-04 | 8 | 1 | Архив/дизайн |
| `docs/BUTTON_DESIGN_GUIDE.md` | 2026-03-04 | 8 | 1 | Живой |
| `docs/CICD_SETUP.md` | 2026-03-04 | 8 | 1 | Живой |
| `docs/COMMAND_AUDIT.md` | 2026-03-04 | 8 | 1 | Живой — устарел |
| `docs/COMMAND_AUDIT_ADMIN.md` | 2026-03-04 | 8 | 2 | Живой — устарел |
| `docs/DATABASE_COVERAGE_AUDIT.md` | 2026-03-04 | 8 | 1 | Аудит-снимок |
| `docs/IMPROVEMENT_MASTER_PLAN.md` | 2026-03-04 | 8 | 1 | Устарел (v1.0 закрыт) |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | 2026-03-04 | 8 | 1 | Живой — требует обновления статуса |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | 2026-03-04 | 8 | 1 | Снимок |
| `docs/SENTRY_GUIDE.md` | 2026-03-04 | 8 | 1 | Живой |
| `docs/SERVER_HEALTH_REPORT_2026-03-04.md` | 2026-03-04 | 8 | 1 | Архив (dated) |
| `docs/SERVER_RUNBOOK.md` | 2026-03-04 | 8 | 4 | Живой |
| `docs/WHATSAPP_BOT_REDESIGN.md` | 2026-03-04 | 8 | 1 | Архив/дизайн |
| `docs/ARCHITECTURE.md` | 2026-03-03 | 9 | 2 | **Устарел (v4.0 → v5.9.0)** |
| `docs/ARCHITECTURE_v1.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/AUDIT_2026-03-03.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/audit_ai_lessons.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/audit_business.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/audit_content.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/audit_ecosystem.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/audit_infra.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/audit_voice.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/CODE_REVIEW_v1.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `docs/DEPLOY.md` | 2026-03-03 | 9 | 1 | Живой — возможно устарел |
| `docs/DEPLOY_GCP.md` | 2026-03-03 | 9 | 2 | Живой — возможно устарел |
| `docs/DEPLOY_LESSONS_2026-03-03.md` | 2026-03-03 | 9 | 1 | Архив (dated) — ОК |
| `docs/MANUAL_TESTS.md` | 2026-03-03 | 9 | 1 | **Устарел (v4.3.0+ → v5.9.0)** |
| `docs/USER_GUIDE_admin.md` | 2026-03-03 | 9 | 1 | **Устарел (v1.0)** |
| `docs/USER_GUIDE_owner.md` | 2026-03-03 | 9 | 1 | **Устарел** |
| `docs/USER_GUIDE_staff.md` | 2026-03-03 | 9 | 1 | **Устарел** |
| `docs/UX_DESIGN_v1.md` | 2026-03-03 | 9 | 1 | Архив — ОК |
| `deploy/README.md` | 2026-03-03 | 9 | 1 | Живой — возможно устарел |
| `MASTER_PLAN.md` | 2026-03-03 | 9 | 2 | **Устарел** |
| `docs/plans/2026-03-02-merge-vtb-cf-plan.md` | 2026-03-02 | 10 | 1 | Архив (завершён план) — ОК |
| `docs/plans/2026-03-02-unified-telegram-bot.md` | 2026-03-02 | 10 | 1 | Архив (завершён план) — ОК |
| `docs/IDEAL_MASTER_PLAN.md` | не в git (untracked) | — | 0 | Новый файл, не закоммичен |
| `.pytest_cache/README.md` | не в git | — | 0 | Авто-сгенерирован |

---

## Критически устаревшие "живые" документы

Эти файлы **должны** отражать текущее состояние кода, но содержат устаревшую информацию:

### 🔴 Высокий приоритет

| Файл | Указанная версия | Текущая версия | Что изменилось |
|------|-----------------|----------------|----------------|
| `docs/ARCHITECTURE.md` | v4.0 (2026-03-03) | v5.9.0 | Добавлены: i18n модуль, /expenses, /report, /areas карточная навигация, inline action callbacks, 13 handlers вместо 11, 3 бота вместо 5 |
| `docs/MANUAL_TESTS.md` | v4.3.0+ (2026-03-03) | v5.9.0 | Новые команды /expenses, /report, inline кнопки действий, i18n, /areas навигация |
| `docs/USER_GUIDE_admin.md` | v1.0 (2026-03-03) | v5.9.0 | Admin ReplyKeyboard меню, inline панель (6 секций), action кнопки в чатах |
| `docs/USER_GUIDE_owner.md` | 2026-03-03 | v5.9.0 | /expenses, /report handlers, новые source команды |
| `docs/USER_GUIDE_staff.md` | 2026-03-03 | v5.9.0 | Аналогично owner |
| `MASTER_PLAN.md` | 2026-03-03 | v5.9.0 | Batch 6 завершён, статусы устарели |

### 🟡 Средний приоритет (требуют проверки)

| Файл | Последнее обновление | Что может устареть |
|------|---------------------|-------------------|
| `docs/COMMAND_AUDIT.md` | 2026-03-04 (Batch 5) | Новые команды /expenses, /report, /areas, /events из Batch 6 не аудированы |
| `docs/COMMAND_AUDIT_ADMIN.md` | 2026-03-04 (v5.3.0) | Inline action callbacks (v5.9.0: 📝/🏷️/👤/⏰) не отражены |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | 2026-03-04 | Статус: ACTIVE, но нужно проверить — реализованы ли M-01..M-15 в v5.5.0–v5.9.0 |
| `docs/DEPLOY.md` | 2026-03-03 | `--remove-orphans` fix от 2026-03-04 не отражён |
| `docs/DEPLOY_GCP.md` | 2026-03-03 | deploy.sh hotfix (--remove-orphans) не отражён |
| `deploy/README.md` | 2026-03-03 | Аналогично DEPLOY.md |

### ⚪ Не требуют обновления (архивные/завершённые)

Следующие файлы являются **намеренными снимками** прошлых состояний и не должны изменяться:

- `docs/ARCHITECTURE_v1.md` — versioned snapshot Phase 9
- `docs/AUDIT_2026-03-03.md`, `docs/audit_*.md` — Phase 0 audit archive
- `docs/CODE_REVIEW_v1.md` — dated code review
- `docs/UX_DESIGN_v1.md` — versioned UX snapshot
- `docs/DEPLOY_LESSONS_2026-03-03.md` — dated lessons
- `docs/SERVER_HEALTH_REPORT_2026-03-04.md` — dated report
- `docs/plans/2026-03-02-*.md` — завершённые планы миграции
- `docs/IMPROVEMENT_MASTER_PLAN.md` — v1.0 закрыт (v5.7.0)

---

## Специальный случай: docs/IDEAL_MASTER_PLAN.md

Файл **не добавлен в git** (untracked). Судя по названию — методологический документ READ ONLY. Нужно либо добавить в `.gitignore`, либо закоммитить с `git add docs/IDEAL_MASTER_PLAN.md`.

---

## Что изменилось в коде с момента последнего обновления "живых" документов

Коммиты после 2026-03-03 (дата большинства живых docs):

| Фича | Версия | Затронутые docs |
|------|--------|-----------------|
| Admin inline action callbacks (📝/🏷️/👤/⏰) | v5.9.0 | ARCHITECTURE, USER_GUIDE_admin, COMMAND_AUDIT_ADMIN |
| i18n EN/AR/ZH полный перевод | v5.8.0 | ARCHITECTURE, MANUAL_TESTS |
| /expenses и /report handlers | v5.7.x | ARCHITECTURE, MANUAL_TESTS, USER_GUIDE_* |
| /areas карточная навигация ◀▶ | v5.7.x | MANUAL_TESTS, USER_GUIDE_* |
| Admin ReplyKeyboard меню (12 команд) | v5.7.0 | USER_GUIDE_admin, COMMAND_AUDIT_ADMIN |
| Admin inline панель (apanel:, 6 секций) | v5.7.0 | USER_GUIDE_admin, COMMAND_AUDIT_ADMIN |
| 5 source команды /events /rss /trends | v5.7.x | ARCHITECTURE, MANUAL_TESTS |
| deploy --remove-orphans fix | v5.8.0 | DEPLOY.md, DEPLOY_GCP.md |
| format_error helper (ADD-01) | v5.5.0 | — |

---

## Рекомендации по порядку обновления

1. **`docs/ARCHITECTURE.md`** — самый устаревший живой документ, версия v4.0 вместо v5.9.0
2. **`docs/USER_GUIDE_admin.md`** — admin бот сильно изменился (ReplyKeyboard + inline panel + action callbacks)
3. **`docs/MANUAL_TESTS.md`** — нужно добавить тест-сценарии для новых команд
4. **`docs/COMMAND_AUDIT_ADMIN.md`** — обновить до v5.9.0 (action callbacks)
5. **`MASTER_PLAN.md`** — обновить статус Batch 6 как завершённого
6. **`docs/USER_GUIDE_owner.md`**, **`docs/USER_GUIDE_staff.md`** — добавить /expenses, /report
7. **`docs/DEPLOY.md`** / **`docs/DEPLOY_GCP.md`** — добавить --remove-orphans в инструкции
8. **Закоммитить `docs/IDEAL_MASTER_PLAN.md`** или добавить в .gitignore
