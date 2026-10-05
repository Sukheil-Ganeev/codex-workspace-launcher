# Анализ: какие файлы в docs/ Claude скорее всего никогда не читает

**Проект:** D:/Downloads/TouristBotEcosystem/
**Дата анализа:** 2026-03-12
**Метод:** сравнение всех файлов docs/ с явными ссылками в CLAUDE.md

---

## Файлы, на которые есть явные ссылки в CLAUDE.md (читаются)

| Файл | Тип ссылки |
|------|-----------|
| `docs/BUTTON_DESIGN_GUIDE.md` | Явная директива: "ЧИТАТЬ перед созданием кнопок" |
| `docs/IMPROVEMENT_MASTER_PLAN.md` | Явная директива: "Мастер-план улучшений" |
| `docs/plans/2026-03-02-merge-vtb-cf-plan.md` | Явная ссылка: "Полный план миграции" |
| `docs/ARCHITECTURE_v1.md` | Упомянут в дереве структуры CLAUDE.md |
| `docs/CODE_REVIEW_v1.md` | Упомянут в дереве структуры CLAUDE.md |
| `docs/MANUAL_TESTS.md` | Упомянут в дереве структуры CLAUDE.md |
| `docs/IDEAL_MASTER_PLAN.md` | Упомянут в дереве + пометка "READ ONLY" |
| `docs/audit_*.md` (6 файлов) | Упомянут в дереве + пометка "Phase 0 audit files (READ ONLY)" |

---

## Файлы, которые Claude скорее всего НИКОГДА не читает (orphans)

Нет ни одной ссылки в CLAUDE.md, не упомянуты в директивах:

### Высокая уверенность — точно не читаются

| Файл | Причина |
|------|---------|
| `docs/ARCHITECTURE.md` | Есть `ARCHITECTURE_v1.md` — вероятно устаревшая версия без версии в имени |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | В CLAUDE.md ссылка только на v1 (`IMPROVEMENT_MASTER_PLAN.md`), v2 нигде не упомянут |
| `docs/ADMIN_BOT_REDESIGN.md` | Нигде не упомянут, не включён ни в одну директиву |
| `docs/WHATSAPP_BOT_REDESIGN.md` | Упомянут только в строке истории Batch 5 как "создан", не как "читать" |
| `docs/CICD_SETUP.md` | Нигде не упомянут, CI/CD инфо есть прямо в CLAUDE.md |
| `docs/DEPLOY.md` | Нигде не упомянут, деплой-инфо есть прямо в CLAUDE.md |
| `docs/DEPLOY_GCP.md` | Нигде не упомянут, GCP-инфо есть прямо в CLAUDE.md |
| `docs/DEPLOY_LESSONS_2026-03-03.md` | Временный отчёт по урокам деплоя, нигде не ссылаются |
| `docs/SENTRY_GUIDE.md` | Нигде не упомянут, Sentry-инфо есть в CLAUDE.md |
| `docs/SERVER_RUNBOOK.md` | Нигде не упомянут |
| `docs/SERVER_HEALTH_REPORT_2026-03-04.md` | Разовый отчёт, нигде не ссылаются |
| `docs/USER_GUIDE_admin.md` | Нигде не упомянут |
| `docs/USER_GUIDE_owner.md` | Нигде не упомянут |
| `docs/USER_GUIDE_staff.md` | Нигде не упомянут |
| `docs/UX_DESIGN_v1.md` | Нигде не упомянут |
| `docs/COMMAND_AUDIT.md` | Упомянут только как "создан" в истории Batch 5, не как "читать" |
| `docs/COMMAND_AUDIT_ADMIN.md` | То же самое |
| `docs/DATABASE_COVERAGE_AUDIT.md` | То же самое — создан в Batch 5, не используется |
| `docs/AUDIT_2026-03-03.md` | Разовый аудит с датой, нет ссылки как "читать" |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | Нигде не упомянут |
| `docs/plans/2026-03-02-unified-telegram-bot.md` | В CLAUDE.md ссылка только на `merge-vtb-cf-plan.md`, этот план не упомянут |

### Технические файлы (не документация)

| Файл | Причина |
|------|---------|
| `docs/node_modules/` (14 файлов) | JS-зависимости в папке docs — явно случайно, Claude не читает |
| `docs/architecture/.gitkeep` | Пустой placeholder |
| `docs/formatting/.gitkeep` | Пустой placeholder |

---

## Итог

| Категория | Количество файлов |
|-----------|------------------|
| Читаются (есть ссылки) | ~14 (8 явных + 6 audit_*.md) |
| Orphans — скорее всего не читаются | 21 документ |
| Технический мусор (node_modules, .gitkeep) | 16 |
| **Всего в docs/** | **~51** |

### Главные orphans (приоритет на внимание)

1. `docs/IMPROVEMENT_MASTER_PLAN_v2.md` — возможно актуальнее v1, но Claude читает v1
2. `docs/ARCHITECTURE.md` — возможно дублирует `ARCHITECTURE_v1.md`
3. `docs/DEPLOY.md`, `docs/DEPLOY_GCP.md` — дублируют инфо в CLAUDE.md
4. `docs/USER_GUIDE_*.md` (3 файла) — пользовательские гайды, не используются в работе Claude
5. `docs/node_modules/` — JS-зависимости в папке docs, вероятно попали сюда по ошибке

### Рекомендации

- Добавить ссылки в CLAUDE.md для файлов, которые нужно читать
- Перенести `node_modules/` из `docs/` — это не документация
- Архивировать или удалить разовые отчёты (`SERVER_HEALTH_REPORT`, `DEPLOY_LESSONS`)
- Уточнить: `IMPROVEMENT_MASTER_PLAN_v2.md` — обновлённая версия или черновик?
