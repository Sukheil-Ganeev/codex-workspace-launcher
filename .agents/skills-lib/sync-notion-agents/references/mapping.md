# Маппинг агентов

## Известные Page IDs

| Агент | Локальная папка | Notion Page ID | Статус |
|-------|-----------------|----------------|--------|
| formatting | NOTION_AI_AGENT_FORMATTING | `2f778820479f8039be03e5e97b990df3` | ✅ |
| bank | NOTION_AI_AGENT_BANK | `2f778820479f80f490fbcfdb749fdc56` | ✅ |
| bookings | NOTION_AI_AGENT_BOOKINGS | `2f778820479f80e09b84c75c7938b997` | ✅ |
| routes | NOTION_AI_AGENT_ROUTES | — | ❌ Нужно создать |
| calculator | NOTION_AI_AGENT_CALCULATOR | — | ❌ Нужно создать |
| requests | NOTION_AI_AGENT_REQUESTS | — | ❌ Нужно создать |

## Как получить Page ID

### Из URL страницы

```
https://www.notion.so/workspace/Agent-Name-2f778820479f8039be03e5e97b990df3
                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                           32 символа без дефисов = Page ID
```

### Через "Copy link"

1. Откройте страницу в Notion
2. Нажмите "..." → "Copy link"
3. Извлеките ID из URL

### Формат ID

Notion использует UUID без дефисов:
- С дефисами: `2f778820-479f-8039-be03-e5e97b990df3`
- Без дефисов: `2f778820479f8039be03e5e97b990df3`

Оба формата работают с API.

## Структура файлов агента

```
D:/Downloads/NOTION_AI_AGENT_<NAME>/
├── INSTRUCTIONS.md      # Основной контент (обязательный)
├── CHEATSHEET.md        # Шпаргалка
├── TEMPLATES.md         # Шаблоны
├── REFERENCE_TABLES.md  # Справочные таблицы
├── CHANGELOG.md         # История версий
├── CLAUDE.md            # Для Claude Code (не синхронизируется)
└── README.md            # Документация (не синхронизируется)
```

## Добавление нового агента

1. Создать папку в `D:/Downloads/`
2. Создать минимум `INSTRUCTIONS.md`
3. Создать страницу в Notion
4. Получить Page ID
5. Добавить в `config.py`:

```python
AGENTS_CONFIG["newagent"] = {
    "folder": "NOTION_AI_AGENT_NEWAGENT",
    "page_id": "abc123...",
    "display_name": "Новый агент",
    "enabled": True,
}
```

## Примечания

- Page ID должен быть 32 символа (UUID без дефисов)
- Страница должна быть расшарена с интеграцией Notion
- Папка должна существовать на локальном диске
