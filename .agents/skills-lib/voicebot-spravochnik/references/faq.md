# FAQ -- Часто задаваемые вопросы

> Справочник FAQ по VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`

---

## Как добавить новую команду в Telegram бот?

> С v6.0.0 handlers.py -- хаб-маршрутизатор (258 строк). Хендлеры живут в 12 доменных модулях: `handlers_voice`, `handlers_video`, `handlers_export`, `handlers_calc`, `handlers_callbacks`, `handlers_stats`, `handlers_clients`, `handlers_admin_commands`, `handlers_text`, `handlers_common`, `handlers_templates`.

### Шаг 1: Выбрать модуль

Определить, к какому домену относится команда:
- Голосовые → `bot/handlers_voice.py`
- Видео → `bot/handlers_video.py`
- Экспорт → `bot/handlers_export.py`
- Калькулятор/маршруты → `bot/handlers_calc.py`
- Статистика/дайджест/история → `bot/handlers_stats.py`
- Клиенты/расходы/уроки → `bot/handlers_clients.py`
- Approve/reject/archive → `bot/handlers_admin_commands.py`
- Текстовые триггеры → `bot/handlers_text.py`
- /start, /help, /settings → `bot/handlers_common.py`
- Шаблоны → `bot/handlers_templates.py`

### Шаг 2: Создать обработчик в выбранном модуле

```python
@router.message(Command("mycommand"))
async def cmd_mycommand(message: Message) -> None:
    text = format_mycommand(platform="telegram")
    await message.answer(text)
```

### Шаг 3: Зарегистрировать в хабе

В `bot/handlers.py` убедиться что модуль импортирован и его `register_handlers(router)` вызывается.

### Шаг 4: Зарегистрировать в меню

В `bot/main.py` добавить в список `commands`:

```python
BotCommand(command="mycommand", description="Описание команды"),
```

### Шаг 5: Добавить в /help

В `core/formatter.py` в функции `format_help_message()` добавить строку с описанием.

### Шаг 6 (опционально): Добавить в WhatsApp

В `whatsapp/handlers.py` в `handle_text_message()` добавить проверку:

```python
if normalized in ("mycommand", "моякоманда"):
    await wa_mycommand(wa_client, from_phone)
    return
```

---

## Как добавить новую бизнес-категорию?

### Шаг 1: Добавить ключевые слова

В `core/categories.py` в `CATEGORY_KEYWORDS`:

```python
"newcat": ["keyword1", "keyword2", "ключевое_слово"],
```

### Шаг 2: Добавить маршрутизацию

В `core/categories.py` в `CATEGORY_GROUPS`:

```python
"newcat": "newcat",  # или существующая группа
```

### Шаг 3: Назначить ответственного

В `data/team.json` добавить категорию в `categories` нужного участника.

### Шаг 4: Добавить в форматтер

В `core/formatter.py` добавить emoji для новой категории в маппинг.

### Шаг 5: Обновить Smart Categorization

В `core/categories.py` обновить промпт для `categorize_smart()` -- добавить новую категорию в список.

### Шаг 6: Валидация

Добавить в `_VALID_CATEGORIES` set:

```python
_VALID_CATEGORIES = {"excursions", "tickets", ..., "newcat", "general"}
```

---

## Как сменить STT модель?

### Быстро: через .env

```
WHISPER_MODEL=medium
```

Доступные модели faster-whisper: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`

### Рекомендации

| Модель | VRAM | Качество (RU) | Скорость |
|--------|------|---------------|----------|
| `large-v3` | ~6 GB | Отличное | Быстрая (GPU) |
| `medium` | ~2 GB | Хорошее | Быстрая |
| `small` | ~1 GB | Среднее | Очень быстрая |

**Для русского языка** рекомендуется `large-v3`.

### Принудительно облачный STT

```
FORCE_GROQ_STT=true
```

Groq всегда использует `whisper-large-v3` (hardcoded).

---

## Как развернуть бот на сервере?

### Краткий чеклист

1. Oracle Cloud: создать VM ARM (Always Free)
2. Установить: python3, pip, venv, git, ffmpeg, nginx
3. Клонировать проект, создать venv
4. `pip install -r requirements-server.txt` (без faster-whisper)
5. Создать `.env` с `FORCE_GROQ_STT=true`
6. Скопировать 3 systemd units (voice_bot, whatsapp_bot, admin_bot), `systemctl enable && start`
7. Настроить nginx + SSL (или Cloudflare Tunnel) для WhatsApp webhook
8. Настроить Meta webhook URL

**Альтернатива Docker:**
```bash
docker-compose up -d  # Запуск всех 3 сервисов
```

Подробная инструкция: см. `references/deploy.md`

---

## Как добавить нового участника команды?

### Шаг 1: Отредактировать data/team.json

```json
{
    "members": [
        ...existing...,
        {
            "name": "Новый Участник",
            "role": "member",
            "telegram_id": 123456789,
            "phones": ["971501234567"],
            "emoji": "icon",
            "categories": ["newcat"],
            "settings": {}
        }
    ]
}
```

### Шаг 2: Добавить в whitelist

В `.env`:

```
ALLOWED_USER_IDS=6905404901,5939002952,1336041242,123456789
WHATSAPP_ALLOWED_PHONES=971553096985,971525007780,971501234567
```

### Шаг 3: Перезапустить бот

```bash
sudo systemctl restart voice_bot whatsapp_bot
```

---

## Как изменить время дайджеста?

### Через бот

**Telegram:**
```
/settings digest_time 20:00
```

**WhatsApp:**
```
настройки дайджест 20:00
```

### Через team.json

```json
"settings": {
    "digest_time": "20:00"
}
```

### По умолчанию

21:00 Dubai time (UTC+4).

### Для всех пользователей

Каждый пользователь может установить своё время. Default берётся из `DEFAULT_SETTINGS`:

```python
DEFAULT_SETTINGS = {
    "digest_time": "21:00",
    "notifications": True,
    "language": "ru",
    "auto_forward": True,
}
```

---

## Как добавить новую категорию расходов?

### В core/expense_categories.py

Добавить в `EXPENSE_CATEGORIES`:

```python
{
    "id": "newexpcat",
    "name": "Название",
    "emoji": "icon",
    "keywords": ["keyword1", "keyword2"],
}
```

### Валидация

Добавить в `VALID_EXPENSE_CATEGORIES` set.

---

## Как настроить облачное хранилище для больших видео?

### Google Drive

1. Создать сервисный аккаунт в Google Cloud Console
2. Скачать JSON credentials
3. Положить в `data/google_credentials.json`
4. В `.env`:
   ```
   GOOGLE_DRIVE_CREDENTIALS=data/google_credentials.json
   ```

### Yandex Disk

1. Получить OAuth token на oauth.yandex.ru
2. В `.env`:
   ```
   YANDEX_DISK_TOKEN=y0_AgAAAABk5...
   ```

---

## Как работает система уроков?

### Поток

1. Бот обрабатывает сообщение (категоризация, чек, и т.д.)
2. Пользователь видит ошибку, нажимает кнопку коррекции
3. Пользователь выбирает правильное значение
4. Бот записывает урок через `services.lessons.record_lesson()`
5. При следующей обработке подобного сообщения:
   - `get_relevant_lessons()` находит подходящие уроки
   - `format_lessons_for_prompt()` форматирует их
   - Уроки инжектируются в промпт Gemini/Groq

### Пример

Бот категоризировал чек ADNOC как "parking". Пользователь исправляет на "fuel".

Урок:
```
Тип: receipt_category
Контекст: ADNOC
Было: parking
Стало: fuel
Текст: "ADNOC -- категория 'fuel', не 'parking'"
```

При следующем чеке ADNOC -- урок инжектируется в промпт и бот правильно категоризирует.

---

## Как экспортировать данные?

### Форматы

| Формат | Команда TG | Команда WA |
|--------|-----------|-----------|
| PDF | `/export pdf` | `экспорт pdf` |
| Excel | `/export xlsx` | `экспорт эксель` |
| Markdown | `/export md` | `экспорт мд` |
| TXT | `/export txt` | `экспорт txt` |

### Периоды

| Период | Описание |
|--------|----------|
| today / day | За сегодня |
| week | За неделю |
| month | За месяц |
| all | За всё время |

### Через меню

1. Отправить `/export`
2. Выбрать период (кнопки)
3. Выбрать формат (кнопки)
4. Получить файл

---

## Как работает автоматический архив?

### Расписание

- **Когда:** 1-е число каждого месяца, 04:00 Dubai
- **Что архивируется:** Транскрипции старше 180 дней
- **Процесс:**
  1. Scheduler считает записи для архивации
  2. Создаёт approval request (Level B, 48h)
  3. Администратор получает уведомление
  4. После одобрения: записи переносятся в `transcriptions_archive`
  5. FTS индекс автоматически обновляется

### Ручная архивация

```
/archive
```

Команда считает записи >6 месяцев и создаёт approval request.

---

## Как перезапустить при зависании?

### Windows (локально)

Закрыть окно и запустить `.bat` заново:
- `scripts/start_all.bat` — все 3 бота
- `scripts/start_telegram.bat` — только Telegram
- `scripts/start_whatsapp.bat` — только WhatsApp
- `scripts/start_admin.bat` — только Admin

### Сервер (systemd)

```bash
sudo systemctl restart voice_bot
sudo systemctl restart whatsapp_bot
sudo systemctl restart admin_bot
```

systemd автоматически перезапускает при краше (`Restart=always`).

### Docker

```bash
docker-compose restart          # Все сервисы
docker-compose restart telegram # Один сервис
```

---

## Как проверить здоровье системы?

### Telegram

```
/health
```

### WhatsApp

```
здоровье
```

### HTTP endpoint

```
GET https://wa-bot.example.com/health
```

### Healthcheck endpoints (v6.0.0)

```
GET http://localhost:8081/health  # Telegram bot
GET http://localhost:8082/health  # Admin bot
GET http://localhost:8000/health  # WhatsApp bot
```

### Что показывает

- Размер БД (MB)
- Количество транскрипций (активные + архивные)
- Количество расходов
- Количество temp файлов / размер
- Pending approval requests
- Статистика уроков
- API token usage (Gemini/Groq/Maps/Vision)
