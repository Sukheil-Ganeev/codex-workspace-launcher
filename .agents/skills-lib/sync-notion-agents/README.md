# sync-notion-agents

Скилл для синхронизации локальных файлов Notion AI агентов с Notion страницами.

## Структура

```
sync-notion-agents/
├── SKILL.md                    # Инструкции скилла
├── README.md                   # Этот файл
├── references/
│   ├── mapping.md              # Маппинг агентов и Page IDs
│   ├── troubleshooting.md      # Решение проблем
│   └── cheatsheet.md           # Шпаргалка команд
└── scripts/
    ├── config.py               # Конфигурация + маппинг
    ├── sync_agents.py          # Основной скрипт
    └── md_to_notion.py         # Конвертер MD → Notion blocks
```

## Быстрый старт

```bash
# Установка
pip install notion-client

# Настройка API ключа
export NOTION_API_KEY="secret_xxx..."

# Синхронизация
cd C:/Users/londo/.claude/skills/sync-notion-agents/scripts
python sync_agents.py all
```

## Агенты

| Имя | Папка | Page ID |
|-----|-------|---------|
| formatting | NOTION_AI_AGENT_FORMATTING | 2f778820479f8039be03e5e97b990df3 |
| bank | NOTION_AI_AGENT_BANK | 2f778820479f80f490fbcfdb749fdc56 |
| bookings | NOTION_AI_AGENT_BOOKINGS | 2f778820479f80e09b84c75c7938b997 |
| routes | NOTION_AI_AGENT_ROUTES | TODO |
| calculator | NOTION_AI_AGENT_CALCULATOR | TODO |
| requests | NOTION_AI_AGENT_REQUESTS | TODO |

## Зависимости

- Python 3.8+
- notion-client (`pip install notion-client`)

## Переменные окружения

- `NOTION_API_KEY` — API ключ интеграции Notion

## Автор

Создано для туристического бизнеса ОАЭ.
