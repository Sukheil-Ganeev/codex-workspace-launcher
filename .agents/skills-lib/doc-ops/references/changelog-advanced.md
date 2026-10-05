# Changelog Advanced Reference

Keep a Changelog convention + Semantic Versioning + Conventional Commits.
Специфично для VIP-DXB-CatalogBot.

---

## Keep a Changelog — Полный формат

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pending features not yet released

---

## [10.9.0] - 2026-04-01

### Added
- New feature description

### Changed
- Modified behavior description

### Deprecated
- Feature scheduled for removal

### Removed
- Deleted feature

### Fixed
- Bug that was fixed

### Security
- Vulnerability that was patched

---

## [10.8.0] - 2026-03-10

...
```

### Правила категорий

| Категория | Когда использовать | Пример для этого проекта |
|-----------|--------------------|--------------------------|
| **Added** | Новый бот, новая таблица, новый endpoint, новый handler | "Add Max Bot with FastAPI webhook" |
| **Changed** | Изменена логика существующей функции, обновлена зависимость | "Update catalog price helper to support USD/AED auto-detection" |
| **Deprecated** | Функция ещё работает, но будет удалена | "Deprecate SQLite `db._db.execute()` direct access" |
| **Removed** | Удалён код/таблица/endpoint | "Remove legacy `?`-placeholder SQL from database.py" |
| **Fixed** | Исправлена ошибка | "Fix `is_banned` INTEGER→BOOLEAN cast on PostgreSQL" |
| **Security** | Уязвимость, HMAC, инъекция | "Enforce HMAC-SHA256 verification on all Meta webhooks" |

### Что пропускать

- `chore:` коммиты (обновление .gitignore, форматирование)
- `ci:` коммиты (GitHub Actions изменения)
- `docs:` коммиты (если не меняют поведение для пользователя)
- Whitespace / typo фиксы

---

## Semantic Versioning для бот-проекта

Формат: `MAJOR.MINOR.PATCH` (пример: `10.9.0`)

### Когда что менять

| Изменение | Тип | Пример |
|-----------|-----|--------|
| Новый бот (новая платформа) | MINOR | v10.8.0 → v10.9.0 |
| Новая фаза с таблицами БД | MINOR | v10.7.0 → v10.8.0 |
| Новый owner panel / крупная фича | MINOR | v10.8.0 → v10.9.0 |
| Bug fix без новых фич | PATCH | v10.8.0 → v10.8.1 |
| Hotfix в production | PATCH | v10.8.1 → v10.8.2 |
| Breaking change в API/DB | MAJOR | v10.x.x → v11.0.0 |
| Полная переработка архитектуры | MAJOR | v10.x.x → v11.0.0 |

### История версий VIP-DXB-CatalogBot

```
v10.8.0  2026-03-10  Phase 21: Viber Bot + Omni Inbox Audit
v10.7.0  2026-03-08  Owner Panels v3 + text_aliases + dormant handlers
v10.6.0  2026-03-07  Owner Panels v2 (Staff/Finance/Catalog/Broadcast/Dashboard)
v10.5.0  2026-03-06  asyncpg full migration + GCP deploy + GitHub Actions CI/CD
v10.4.0  2026-03-01  Phase 9 UX + Tourism CRM deployment (Vercel + Neon)
v10.3.0  ~2026-02    Phase 21 Facebook Messenger
v10.2.0  ~2026-02    Phase 19 WhatsApp + Phase 20 Facebook (early)
```

---

## Conventional Commits формат

Используется для commit messages в git (не для CHANGELOG.md — там другой формат).

### Синтаксис

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Типы

| Тип | Когда | Пример |
|-----|-------|--------|
| `feat` | Новая функция | `feat(max_bot): add FastAPI webhook handler` |
| `fix` | Исправление бага | `fix(database): cast is_banned to BOOLEAN` |
| `docs` | Только документация | `docs(claude): update Phase 22 changelog table` |
| `refactor` | Рефакторинг без изменения поведения | `refactor(omni): extract platform detection to helper` |
| `test` | Добавление/исправление тестов | `test(max_bot): add 180 pytest tests` |
| `chore` | Обслуживание (зависимости, CI) | `chore(deps): update aiogram to 3.26` |
| `perf` | Улучшение производительности | `perf(catalog): cache category list for 60s` |
| `security` | Исправление уязвимости | `security(webhook): enforce HMAC on Max bot` |

### Scope — для этого проекта

| Scope | Для чего |
|-------|---------|
| `telegram` / `bot` | Telegram бот |
| `vk` / `vk_bot` | VK бот |
| `instagram` | Instagram DM бот |
| `whatsapp` | WhatsApp бот |
| `facebook` | Facebook Messenger бот |
| `viber` | Viber бот |
| `max` | Max бот |
| `miniapp` | Mini App |
| `database` / `db` | data/database.py |
| `omni` | Omni Inbox |
| `core` | core/ shared code |
| `owner` | Owner panels |
| `claude` | CLAUDE.md / docs |

### Примеры commit messages для этого проекта

```
feat(max): add FastAPI webhook for Max messenger (port 8085)

feat(db): add max_users table with synthetic user_id -4000..-4999

fix(owner): fix is_banned INTEGER→BOOLEAN cast in PostgreSQL queries

docs(claude): update Phase 22 changelog row in CLAUDE.md

test(max): add 180 pytest tests for Max Bot handlers

chore(ci): add max_bot to GitHub Actions docker-compose services
```

---

## CHANGELOG.md — Полный пример для VIP-DXB-CatalogBot

```markdown
# Changelog

All notable changes to VIP-DXB-CatalogBot are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- (nothing yet)

---

## [11.0.0] - 2026-06-01

### Added
- Add Omni Inbox Phase 2: all 7 platforms fully connected
- Add real-time message routing between platforms

### Changed
- **[BREAKING]** Omni Inbox replaces per-platform notification logic
- All 7 connectors now registered in omni_service at startup

---

## [10.9.0] - 2026-04-01

### Added
- Add Max Bot with FastAPI webhook (port 8085)
- Add `max_users` DB table — synthetic user_id range -4000..-4999
- Add `get_or_create_max_user(max_id, max_name)` DB method
- Add migration `_migrate_v22_max()` (idempotent)
- Add MaxConnector to Omni Inbox startup sequence
- Add 180 pytest tests (webhook verify, catalog, booking FSM, search)

### Changed
- `core/user_ids.py` — added MAX_ID_OFFSET, `is_max_user()`, updated `get_platform()`
- Omni Inbox now supports 7 connectors (added Max)

### Fixed
- Fix Max webhook 200 response for non-text event types

---

## [10.8.0] - 2026-03-10

### Added
- Add Viber Bot with FastAPI webhook (port 8084)
- Add Rich Media 6-column carousel for catalog display
- Add 7-step booking FSM via tracking_data hybrid state
- Add `viber_users` DB table — synthetic user_id range -3000..-3999
- Add `get_or_create_viber_user(viber_id, viber_name, viber_avatar, country)` DB method
- Add migration `_migrate_v21_viber()`
- Add 211 pytest tests for Viber Bot
- Add Omni Inbox audit: OMNI_BUTTON_AUDIT.md (400+ entry points)
- Add OMNI_INBOX_ROLLOUT_BACKLOG.md (21 tasks P0-P3)

### Changed
- Register ViberConnector in Omni Inbox startup sequence

### Fixed
- Fix Facebook Messenger manager Telegram notification format
- Fix Mini App booking auth token validation
```

---

## CLAUDE.md Changelog Table Format

Секция `## 9. Changelog (последние 6)` в проекте:

```markdown
## 9. Changelog (последние 6)

| Дата | Фаза | Что сделано |
|------|------|------------|
| 2026-04-01 | Phase 22: Max Bot | FastAPI webhook :8085, 8-step FSM, max_users table, synthetic -4000.., MaxConnector в Omni Inbox, 180 тестов. |
| 2026-03-10 | Omni Inbox Audit | Аудит 400+ entry points (8 агентов), фиксы FB/MiniApp/Inbox, docs: OMNI_BUTTON_AUDIT.md, OMNI_INBOX_ROLLOUT_BACKLOG.md (21 задача P0-P3). |
| 2026-03-08 | Owner Panels v3 Wave 2 | Settings panel (working hours, currency, notifications, welcome msgs), text_aliases.py (68 shortcuts), migration v27. 81 тест. |
| 2026-03-08 | Dormant Handlers | Подключены 11 dormant роутеров (31→42), 3 кнопки клиентского меню (Trip/Weather/Visa), split_payment ordering fix. |
| 2026-03-08 | Owner Panels v3 Wave 1 | 4 панели: Bookings, Reviews, Calendar, Export. csv_export.py, migration v26, is_banned fix. 213 тестов. |
| 2026-03-07 | Owner Panels v2 | 5 панелей: Staff, Finance, Catalog, Broadcast, Dashboard. migration v25 (broadcast tables). pdf_report asyncpg fix. |
```

### Правила таблицы

- **Максимум 6 строк** — при добавлении новой удалять самую старую (строку 7)
- **Дата** — `YYYY-MM-DD` (Dubai timezone)
- **Фаза** — краткое название: `Phase 22: Max Bot`, `Bug Fix`, `Refactoring`
- **Что сделано** — 1-3 предложения на русском; технические детали (имена файлов, количество тестов)
- Всегда включать количество тестов если они добавлялись
- Никогда не дублировать существующую строку

---

## Sources

- Keep a Changelog: https://keepachangelog.com/en/1.1.0/
- Semantic Versioning: https://semver.org/
- Conventional Commits: https://www.conventionalcommits.org/
