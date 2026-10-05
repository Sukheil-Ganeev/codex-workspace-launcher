# Анализ токенов при старте сессии — TouristBotEcosystem

**Проект:** `D:/Downloads/TouristBotEcosystem/`
**Дата анализа:** 2026-03-12
**Метод:** docs-optimizer skill, режим `tiered`

---

## Методология подсчёта

- Токены оцениваются по формуле: `ASCII chars / 4 + Cyrillic chars / 2`
- Кириллица стоит примерно вдвое дороже ASCII (2x по токенам на символ)
- Данная оценка является **приблизительной** — реальные числа зависят от tokenizer модели

---

## Что загружается автоматически при каждом старте сессии

Claude Code автоматически загружает все CLAUDE.md по цепочке директорий от корня до CWD.

| Файл | Строк | Chars | ~Токенов | Кириллица (chars) | Статус |
|------|-------|-------|----------|-------------------|--------|
| `C:/Users/londo/.claude/CLAUDE.md` (global) | 139 | 5,129 | **~1,972** | 2,759 | ВСЕГДА |
| `D:/Downloads/CLAUDE.md` (parent) | 659 | 23,549 | **~8,107** | 8,881 | ВСЕГДА |
| `D:/Downloads/TouristBotEcosystem/CLAUDE.md` (project) | 557 | 31,943 | **~9,062** | 4,308 | ВСЕГДА |
| **ИТОГО СТАРТ** | **1,355** | **60,621** | **~19,141** | **15,948** | |

**Вывод: каждая новая сессия начинается с ~19,141 токенов, потраченных на инструкции.**

---

## Полный реестр документации проекта

### Корневые файлы

| Файл | Строк | ~Токенов | Загрузка | Комментарий |
|------|-------|----------|----------|-------------|
| `CLAUDE.md` | 557 | 9,062 | Авто | Включён в ~19K старт |
| `CHANGELOG.md` | 1,088 | 16,549 | По запросу | История изменений |
| `MASTER_PLAN.md` | 1,900 | 25,420 | По запросу | Мастер-план (огромный) |
| `README.md` | 351 | 2,960 | По запросу | Описание проекта |
| `ISSUES.md` | 110 | 2,505 | По запросу | Открытые проблемы |
| **ИТОГО корень** | **4,006** | **56,496** | | |

### docs/ — по убыванию размера

| Файл | Строк | ~Токенов | Тип | Рекомендация |
|------|-------|----------|-----|--------------|
| `docs/IDEAL_MASTER_PLAN.md` | 2,559 | **30,520** | Методология | ARCHIVE |
| `MASTER_PLAN.md` (корень) | 1,900 | **25,420** | Мастер-план | ARCHIVE |
| `docs/plans/2026-03-02-merge-vtb-cf-plan.md` | 961 | 14,301 | Завершённый план | ARCHIVE |
| `docs/IMPROVEMENT_MASTER_PLAN.md` | 879 | 13,285 | Роадмап | On-demand |
| `docs/DEPLOY_GCP.md` | 1,062 | 11,590 | Деплой | On-demand |
| `docs/BUTTON_DESIGN_GUIDE.md` | 1,039 | 11,363 | Стандарты | On-demand |
| `docs/UX_DESIGN_v1.md` | 1,103 | 11,272 | Дизайн | On-demand |
| `docs/AUDIT_2026-03-03.md` | 332 | 9,814 | Аудит | ARCHIVE |
| `docs/ARCHITECTURE_v1.md` | 841 | 9,788 | Архитектура | On-demand |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | 628 | 9,210 | История | ARCHIVE |
| `docs/plans/2026-03-02-unified-telegram-bot.md` | 990 | 8,487 | Завершённый план | ARCHIVE |
| `docs/WHATSAPP_BOT_REDESIGN.md` | 522 | 6,515 | Redesign doc | On-demand |
| `docs/DEPLOY.md` | 798 | 6,137 | Деплой | On-demand |
| `docs/DATABASE_COVERAGE_AUDIT.md` | 337 | 5,860 | Аудит | ARCHIVE |
| `docs/USER_GUIDE_owner.md` | 476 | 5,686 | Гайд | On-demand |
| `docs/CODE_REVIEW_v1.md` | 385 | 5,161 | Code review | ARCHIVE |
| `docs/USER_GUIDE_admin.md` | 390 | 4,904 | Гайд | On-demand |
| `docs/MANUAL_TESTS.md` | 321 | 4,616 | Тесты | On-demand |
| `docs/COMMAND_AUDIT.md` | 218 | 4,612 | Аудит | ARCHIVE |
| `docs/ARCHITECTURE.md` | 424 | 4,314 | Архитектура v2 | On-demand |
| `docs/COMMAND_AUDIT_ADMIN.md` | 262 | 4,278 | Аудит | ARCHIVE |
| `docs/audit_infra.md` | 178 | 4,026 | Аудит | ARCHIVE |
| `docs/audit_ai_lessons.md` | 210 | 3,912 | Аудит | ARCHIVE |
| `docs/audit_business.md` | 136 | 3,815 | Аудит | ARCHIVE |
| `docs/ADMIN_BOT_REDESIGN.md` | 278 | 3,383 | Redesign | On-demand |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | 255 | 3,114 | Роадмап v2 | On-demand |
| `docs/audit_content.md` | 119 | 3,042 | Аудит | ARCHIVE |
| `docs/audit_voice.md` | 123 | 3,011 | Аудит | ARCHIVE |
| `docs/SERVER_RUNBOOK.md` | 361 | 2,683 | Runbook | On-demand |
| `docs/audit_ecosystem.md` | 182 | 2,415 | Аудит | ARCHIVE |
| `docs/SERVER_HEALTH_REPORT_2026-03-04.md` | 142 | 2,153 | Отчёт | ARCHIVE |
| `docs/SENTRY_GUIDE.md` | 187 | 1,886 | Гайд | On-demand |
| `docs/USER_GUIDE_staff.md` | 145 | 1,665 | Гайд | On-demand |
| `docs/DEPLOY_LESSONS_2026-03-03.md` | 166 | 1,441 | Уроки деплоя | ARCHIVE |
| `docs/CICD_SETUP.md` | 105 | 937 | CI/CD | On-demand |
| **ИТОГО docs/** | **17,114** | **219,196** | | |

### Итог по всему репозиторию

| Категория | Файлов | Строк | ~Токенов |
|-----------|--------|-------|----------|
| Root MD files | 5 | 4,006 | 56,496 |
| docs/ | 34 | 17,114 | 219,196 |
| **ИТОГО в репо** | **39** | **21,120** | **275,692** |

---

## Структура стоимости старта сессии

```
СТАРТ СЕССИИ: ~19,141 токенов
├── Global CLAUDE.md         1,972 токенов  (10.3%)
├── Parent CLAUDE.md         8,107 токенов  (42.4%)   ← ГЛАВНЫЙ ВИНОВНИК
└── Project CLAUDE.md        9,062 токенов  (47.3%)   ← ГЛАВНЫЙ ВИНОВНИК
```

**Проблема:** Parent CLAUDE.md (`D:/Downloads/CLAUDE.md`) содержит 659 строк и тратит **8,107 токенов** каждую сессию, хотя большая часть его содержимого (TouristBotEcosystem архитектура, Tourism CRM детали) уже продублирована в project CLAUDE.md.

---

## Анализ анти-паттернов (применимые к проекту)

| ID | Паттерн | Severity | Проблема |
|----|---------|----------|---------|
| AP-01 | Context Stuffing | CRITICAL | Project CLAUDE.md = 9,062 токенов (целевой максимум: 2,500) |
| AP-01 | Context Stuffing | CRITICAL | Parent CLAUDE.md = 8,107 токенов (дублирует project) |
| AP-16 | Cross-File Duplication | HIGH | TouristBotEcosystem архитектура есть и в parent и в project CLAUDE.md |
| AP-03 | Orphan Docs | HIGH | 34 файла в docs/, .claudeignore отсутствует |
| AP-11 | Duplicate Commands | MEDIUM | Команды запуска дублируются в CLAUDE.md и docs/DEPLOY.md |
| AP-04 | Cache-Hostile Order | MEDIUM | Динамический "Статус проекта" стоит выше статических разделов |
| AP-18 | Stale Issues | LOW | ISSUES.md показывает все проблемы как закрытые — возможно устарел |
| AP-19 | Roadmap Rot | MEDIUM | IMPROVEMENT_MASTER_PLAN.md + v2 + IDEAL — какой актуальный? |
| AP-20 | Protocol Sprawl | HIGH | Детальная архитектура дерева (>200 строк) прямо в CLAUDE.md |

---

## Рекомендации по снижению стоимости

### Быстрые победы (HIGH impact, LOW effort)

**1. Создать `.claudeignore` — сэкономить до ~219K токенов при явном вызове**
```
docs/IDEAL_MASTER_PLAN.md
docs/PROJECT_ACCOMPLISHMENTS.md
docs/AUDIT_2026-03-03.md
docs/DATABASE_COVERAGE_AUDIT.md
docs/CODE_REVIEW_v1.md
docs/COMMAND_AUDIT.md
docs/COMMAND_AUDIT_ADMIN.md
docs/audit_*.md
docs/SERVER_HEALTH_REPORT_2026-03-04.md
docs/DEPLOY_LESSONS_2026-03-03.md
docs/plans/
MASTER_PLAN.md
CHANGELOG.md
```
*Примечание: `.claudeignore` работает для автоматической индексации, но файлы всё равно можно читать явно.*

**2. Урезать Project CLAUDE.md с 9,062 до ~2,500 токенов**

Что убрать из CLAUDE.md (перенести в docs/ со ссылкой):
- Детальное дерево архитектуры (>200 строк, ~2,500 токенов) → `docs/ARCHITECTURE.md`
- Полный список зависимостей requirements.txt → оставить только ссылку
- Детали GCP деплоя (таблица + cloudflare) → `docs/DEPLOY_GCP.md` уже есть
- История батчей (развёрнутые описания всех фаз) → краткая таблица
- Полный список команд с комментариями → оставить только ключевые

Экономия: ~6,500 токенов на каждой сессии.

**3. Сократить Parent CLAUDE.md (`D:/Downloads/CLAUDE.md`)**

Parent CLAUDE.md включает детали TouristBotEcosystem и Tourism CRM, которые уже есть в project CLAUDE.md. Достаточно оставить только глобальные ссылки.

Экономия: ~5,000-6,000 токенов.

### Потенциальная экономия

| Действие | Экономия токенов |
|----------|-----------------|
| Урезать Project CLAUDE.md (9,062 → 2,500) | ~6,562 токенов |
| Урезать Parent CLAUDE.md (8,107 → 2,500) | ~5,607 токенов |
| Создать .claudeignore для docs/audit_*.md и планов | ~0 на старте (docs не авто-загружаются) |
| **Итого возможная экономия** | **~12,169 токенов** |

**Результат после оптимизации:**
- Было: ~19,141 токенов на старт
- Станет: ~7,000-8,000 токенов на старт
- Экономия: **~60% снижение стоимости старта**

---

## Tiered Loading Plan

### Essential (загружается всегда — цель ~7,000 токенов)

| Файл | Целевой размер | Что оставить |
|------|---------------|--------------|
| `C:/Users/londo/.claude/CLAUDE.md` | ~1,500 токенов | Без изменений (уже компактный) |
| `D:/Downloads/CLAUDE.md` | ~2,500 токенов | Только ссылки на проекты, убрать дублирующие разделы |
| `D:/Downloads/TouristBotEcosystem/CLAUDE.md` | ~2,500 токенов | Quick Start + таблицы + ссылки |

### On-demand (~500-2,000 токенов каждый, читать явно)

- `docs/ARCHITECTURE.md` — когда работа с архитектурой
- `docs/DEPLOY_GCP.md` — когда деплой
- `docs/BUTTON_DESIGN_GUIDE.md` — когда кнопки/UI
- `docs/IMPROVEMENT_MASTER_PLAN.md` — когда планирование фичей
- `CHANGELOG.md` — когда нужна история
- `ISSUES.md` — когда нужны открытые проблемы

### Archive (0 токенов, через .claudeignore)

- `docs/IDEAL_MASTER_PLAN.md` — методология, читается редко
- `docs/PROJECT_ACCOMPLISHMENTS.md` — история, не нужна в работе
- `docs/AUDIT_2026-03-03.md` — завершённый аудит
- `docs/audit_*.md` (6 файлов) — завершённые аудиты
- `docs/plans/` — завершённые планы
- `MASTER_PLAN.md` — дублирует docs/IDEAL_MASTER_PLAN.md
- `docs/SERVER_HEALTH_REPORT_2026-03-04.md` — разовый отчёт

---

## Итоговые метрики

| Метрика | Текущее | Цель | Статус |
|---------|---------|------|--------|
| Стоимость старта | ~19,141 токенов | ~7,000 токенов | CRITICAL |
| Project CLAUDE.md | 9,062 токенов / 557 строк | 2,500 / 250 строк | CRITICAL |
| Parent CLAUDE.md | 8,107 токенов / 659 строк | 2,500 / 250 строк | CRITICAL |
| Файлов в docs/ | 34 | 34 (архивировать 15+) | WARNING |
| .claudeignore | отсутствует | создать | HIGH |
| Verification Score | 2/5 | 4/5 | — |

**Verification Score = 2/5:** Project CLAUDE.md содержит детальную архитектуру (AP-01), дублирование с parent (AP-16), нет .claudeignore (AP-03), нет cache-optimized ordering (AP-04).
