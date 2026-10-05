# Шпаргалка команд

## Основные команды

```bash
# Один агент
python sync_agents.py formatting

# Все агенты
python sync_agents.py all

# Тестовый режим
python sync_agents.py all --dry-run

# Принудительно
python sync_agents.py formatting --force

# Подробный вывод
python sync_agents.py all --verbose

# Список агентов
python sync_agents.py --list
```

## Несколько агентов

```bash
python sync_agents.py formatting bank bookings
```

## Комбинации флагов

```bash
# Тест + подробно
python sync_agents.py all --dry-run --verbose

# Принудительно + подробно
python sync_agents.py formatting -f -v
```

## Переменные окружения

```bash
# PowerShell
$env:NOTION_API_KEY = "secret_xxx"

# CMD
set NOTION_API_KEY=secret_xxx

# Bash
export NOTION_API_KEY="secret_xxx"
```

## Проверка конфигурации

```bash
python config.py
```

## Тест конвертера MD

```bash
python md_to_notion.py
```

## Доступные агенты

| Имя | Описание |
|-----|----------|
| `formatting` | Форматирование текстов |
| `bank` | Банковские реквизиты |
| `bookings` | Подтверждения бронирований |
| `routes` | Оптимизация маршрутов |
| `calculator` | Калькулятор валют |
| `requests` | Обработка запросов |

## Структура папки агента

```
NOTION_AI_AGENT_XXX/
├── INSTRUCTIONS.md     # → Основной контент
├── CHEATSHEET.md       # → Toggle "📋 Шпаргалка"
├── TEMPLATES.md        # → Toggle "📝 Шаблоны"
├── REFERENCE_TABLES.md # → Toggle "📊 Справочники"
└── CHANGELOG.md        # → Toggle "📜 История версий"
```

## Полезные пути

```
# Скрипты
C:/Users/londo/.claude/skills/sync-notion-agents/scripts/

# Агенты
D:/Downloads/NOTION_AI_AGENT_*/
```

## Быстрый рабочий процесс

```bash
# 1. Редактируем файлы агента
# 2. Обновляем версию в CHANGELOG.md
# 3. Тестируем
python sync_agents.py formatting --dry-run

# 4. Синхронизируем
python sync_agents.py formatting

# 5. Проверяем в Notion
```
