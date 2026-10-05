# Решение проблем

## Ошибки установки

### "notion-client не установлен"

```bash
pip install notion-client
```

Если pip не работает:
```bash
python -m pip install notion-client
```

### Ошибка импорта модулей

Убедитесь что запускаете из папки scripts:
```bash
cd C:/Users/londo/.claude/skills/sync-notion-agents/scripts
python sync_agents.py all
```

## Ошибки авторизации

### "NOTION_API_KEY не установлен"

Установите переменную окружения:

**PowerShell:**
```powershell
$env:NOTION_API_KEY = "secret_xxx..."
```

**CMD:**
```cmd
set NOTION_API_KEY=secret_xxx...
```

**Bash:**
```bash
export NOTION_API_KEY="secret_xxx..."
```

### 401 Unauthorized

Причины:
1. Неправильный API ключ
2. Ключ устарел
3. Страница не расшарена с интеграцией

Решение:
1. Проверьте ключ на https://www.notion.so/my-integrations
2. Создайте новый ключ если нужно
3. Расшарьте страницу: Share → Invite → выберите интеграцию

### 403 Forbidden

Интеграция не имеет доступа к странице.

Решение:
1. Откройте страницу в Notion
2. Нажмите "Share"
3. "Invite" → найдите вашу интеграцию
4. Подтвердите доступ

## Ошибки API

### 400 Bad Request

Возможные причины:
- Некорректный Page ID
- Слишком много блоков (>100)
- Некорректный Markdown

Решение:
1. Проверьте Page ID (32 символа)
2. Уменьшите размер файлов
3. Проверьте синтаксис Markdown

### 429 Rate Limit

Слишком много запросов. Скрипт автоматически делает паузы между запросами.

Если ошибка повторяется:
```python
# В config.py увеличьте задержку
RATE_LIMIT_DELAY = 0.5  # было 0.35
```

### 500 Internal Server Error

Проблема на стороне Notion. Подождите и повторите.

## Ошибки синхронизации

### "Файлы агента не найдены"

Проверьте:
1. Папка существует: `D:/Downloads/NOTION_AI_AGENT_<NAME>/`
2. Есть файл INSTRUCTIONS.md

### "Page ID не указан"

Добавьте Page ID в config.py для этого агента.

### "Агент отключён"

В config.py установите `"enabled": True`.

### Версии совпадают, пропускается

Используйте флаг `--force`:
```bash
python sync_agents.py formatting --force
```

## Проблемы с контентом

### Таблицы не отображаются корректно

Notion не поддерживает сложные таблицы. Упростите:
- Уберите colspan/rowspan
- Используйте простой текст в ячейках
- Ограничьте ширину таблицы

### Код не форматируется

Проверьте синтаксис:
```markdown
```python
def hello():
    print("Hello")
```
```

### Ссылки не работают

Формат: `[текст](https://url.com)`

Не забывайте `https://` в начале URL.

### Секция "Воспоминания" удалилась

Секция должна называться точно "Воспоминания" (toggle или heading).

Если удалилась — это баг, проверьте:
1. Название секции
2. Тип блока (toggle/heading)

## Проверка конфигурации

```bash
python config.py
```

Выведет статус всех агентов и ошибки конфигурации.

## Тестовый режим

Всегда сначала запускайте с `--dry-run`:
```bash
python sync_agents.py all --dry-run
```

Это покажет что будет сделано без реальных изменений.

## Логи

Для подробного вывода:
```bash
python sync_agents.py all --verbose
```

## Получить помощь

```bash
python sync_agents.py --help
```
