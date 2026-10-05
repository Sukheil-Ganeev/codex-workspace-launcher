# EXP-057: 4-agent worktree pattern for multi-platform bot creation

**Дата:** 2026-02-27
**Тип:** pattern
**Severity:** high
**Проект:** VIP-DXB-CatalogBot (WhatsApp Cloud API Bot, Phase 19)
**Контекст:** Создание WhatsApp бота (13 файлов, 1,861 строк) по паттерну instagram_bot/

## Урок

При создании нового бота для мультиплатформенной системы — 4-agent worktree pattern даёт максимальную скорость:
- Agent 1: Core (app.py, config, webhook, API client)
- Agent 2: Business logic (FSM, formatters, templates)
- Agent 3: Handlers (common, catalog, booking, search)
- Agent 4: Database migration + tests

### Критические точки гармонизации:
1. **Версия миграции** — проверять последнюю миграцию в основном database.py (v18 omnichannel уже существовал → использовали v19)
2. **Дублирующие файлы** — Agent 3 создал свои копии fsm/formatters/templates для автономности. При мерже — ВСЕГДА использовать файлы от primary owner агента
3. **app.py → handlers bridge** — Agent 1 создал app.py который не вызывал process_webhook() из Agent 3. Нужна гармонизация после мержа
4. **WhatsApp API limits** — row titles max 24 chars, max 3 Reply Buttons, max 10 List rows, mark_as_read() обязательно

### Результат:
- 146 тестов passed, 0 failures, 0 регрессий
- Время: ~10 минут параллельной работы 4 агентов + ~5 минут мерж + гармонизация
- Паттерн воспроизводим для будущих платформ (Line, Viber, WeChat)

## Применение
- ВСЕГДА проверять номер последней миграции перед созданием новой
- ВСЕГДА проверять bridge между app.py и handlers после мержа
- При параллельной работе каждый агент создаёт свои зависимости — при мерже выбирать версию primary owner
- Synthetic user_id: разделять диапазоны по платформам (TG: positive, IG: -1..-999, WA: -1000..)

## Times applied
1 (initial recording)

## See also
- **EXP-058 (PAT-029):** Evolution of this pattern for creating 2+ bots simultaneously. Uses platform-split (1 agent = 1 complete bot) instead of layer-split (Core/Logic/Handlers/Tests). Eliminates bridge/harmonization issues.
