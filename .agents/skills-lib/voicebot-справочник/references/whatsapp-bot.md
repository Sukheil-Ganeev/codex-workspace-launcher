# WhatsApp Bot -- Полная справка

> Справочник по WhatsApp-боту VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Основные файлы: `whatsapp/app.py`, `whatsapp/handlers.py`, `whatsapp/client.py`, `whatsapp/security.py`

---

## Архитектура

WhatsApp бот -- **отдельный FastAPI процесс** на порту 8000. Полностью независим от Telegram бота. Оба бота разделяют общий пакет `core/`.

```python
# whatsapp/app.py
app = FastAPI(
    title="WhatsApp Voice Transcription Bot",
    docs_url=None,       # Swagger UI отключён (безопасность)
    redoc_url=None,      # ReDoc отключён
    lifespan=lifespan,
)
```

---

## Webhook Endpoints

| Метод | Путь | Назначение |
|-------|------|-----------|
| `GET` | `/webhook` | Handshake верификации Meta -- echo `hub.challenge` |
| `POST` | `/webhook` | Приём входящих сообщений и статусов |
| `GET` | `/health` | Health check с метриками системы |

---

## Lifecycle (Startup/Shutdown)

### При запуске (`lifespan`):

1. `init_handler()` -- инициализация `WhatsAppClient`, shared core services, `TEMP_DIR`
2. Запуск daily digest background task (21:00 Dubai)
3. Запуск cloud cleanup loop (каждый час)

### При остановке:

1. Отмена фоновых задач
2. `close_handler()` -- закрытие HTTP клиента и services

---

## POST /webhook -- Конвейер обработки

```
1. Верификация HMAC-SHA256 (X-Hub-Signature-256 header)
2. Парсинг JSON payload
3. Извлечение entry[0].changes[0].value.messages
4. Для каждого сообщения:
   a. Маскировка номера для логов (***XXXX)
   b. Проверка whitelist (is_allowed)
   c. Dispatch по типу:
      - "audio"       -> handle_audio_message
      - "text"        -> handle_text_message
      - "image"       -> handle_image_message
      - "interactive" -> handle_interactive_message
5. Return 200 немедленно (handlers в background tasks)
```

### Обёртка безопасности

```python
async def _safe_handle(handler, *args) -> None:
    try:
        await handler(*args)
    except Exception:
        logger.exception("Unhandled error in %s", handler.__name__)
```

Все обработчики обёрнуты в `_safe_handle()` -- сервер никогда не крашится.

---

## 35+ текстовых команд

### Приветствие / Помощь

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `привет` | `помощь`, `help`, `старт`, `start`, `/start`, `/help` | Welcome + список команд |

### История и поиск

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `история` | `history` | Последние 5 транскрипций |
| `поиск <запрос>` | `search <query>` | FTS5 полнотекстовый поиск |
| `дата <дата>` | `date <date>` | Поиск по дате |
| `закладки` | `bookmarks` | Закладки |
| `сохрани <ID>` | -- | Toggle закладка по ID |

### Статистика и аналитика

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `статус` | `статистика`, `stats`, `status` | Статистика + кнопки |
| `кабинет` | `cabinet` | Персональный кабинет |
| `команда` | `team` | Доска команды |
| `сравни` | `сравнение`, `compare` | Сравнение неделя vs неделя |
| `дашборд` | `пульс`, `dashboard`, `пульс бизнеса` | Бизнес-дашборд |
| `здоровье` | `здоровье бота`, `health` | Здоровье системы |

### Обработка контента

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `объедини <N>` | -- | Объединить последние N записей |
| `объедини` (без N) | -- | Показать кнопки режимов объединения |
| `дайджест` | -- | Кнопки выбора периода |
| `дайджест за неделю` | -- | Недельный дайджест напрямую |
| `дайджест за месяц` | -- | Месячный дайджест напрямую |
| `экспорт` | `export` | Меню экспорта (list menu) |
| `экспорт pdf` | `экспорт пдф` | PDF отчёт |
| `экспорт xlsx` | `экспорт эксель`, `экспорт excel` | Excel отчёт |
| `экспорт md` | `экспорт мд`, `экспорт markdown` | Markdown отчёт |
| `экспорт txt` | `экспорт текст` | Текстовый экспорт |

### Управление клиентами

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `клиенты` | `clients` | Список клиентов (list menu <=10, текст >10) |
| `добавить клиент <phone> <name> [type]` | `add client` | Добавить клиента |
| `удалить клиент <phone>` | `remove client` | Удалить (через approval) |

### Финансы / Расходы

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `расходы` | `expenses` | Список за месяц + кнопки периодов |
| `расходы сегодня` | `expenses today` | За сегодня |
| `расходы неделя` | `expenses week` | За неделю |
| `расходы месяц` | `expenses month` | За месяц |
| `расходы стат` | `expenses stats` | Статистика за месяц |
| `добавить расход <сумма> <описание>` | `add expense` | Ручной расход |
| `отчёт` | `отчет`, `report` | PDF финансовый отчёт (неделя) |
| `отчёт месяц` | `report month` | Месячный отчёт |
| `исправить <ID> <field> <value>` | `fix` | Коррекция расхода + урок |

### Заметки и уроки

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `заметки` | `notes` | Список заметок |
| `уроки` | `lessons` | Последние 10 уроков |
| `уроки стат` | `lessons stats` | Статистика уроков |

### Подтверждения

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `ожидающие` | `pending` | Pending-запросы с кнопками |
| `подтверждения` | `approvals` | История (последние 10) |
| `одобрить <ID>` | `approve <ID>` | Одобрить (owner-only) |
| `отклонить <ID> [причина]` | `reject <ID> [reason]` | Отклонить |

### Архивация

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `архив` | `архивация`, `archive` | Найти записи >6 мес, создать approval |

### Навигация

| Команда | Алиасы | Действие |
|---------|--------|----------|
| `назад` | `back` | Вернуться (screen stack) |

### Настройки

| Команда | Формат | Действие |
|---------|--------|----------|
| `настройки` / `settings` | -- | Текущие настройки |
| `настройки дайджест <HH:MM>` | -- | Изменить время дайджеста |
| `настройки уведомления <вкл/выкл>` | -- | Toggle уведомлений |
| `настройки язык <ru/en>` | -- | Сменить язык |
| `настройки пересылка <вкл/выкл>` | -- | Toggle автопересылки |

### Видео URL

Любой URL видео (YouTube, TikTok, Instagram, VK) автоматически обнаруживается и запускает поток загрузки/транскрипции.

### Ответ по умолчанию

Если ни одна команда не совпала:
> "Отправьте голосовое сообщение для расшифровки. Напишите **help** для списка команд."

---

## Интерактивные элементы

### Reply Buttons (макс 3 на сообщение)

```python
wa_client.send_buttons(to, body, buttons)
# buttons: [{"id": "callback_id", "title": "Текст (макс 20 символов)"}]
```

| Контекст | Кнопки | Callback IDs |
|----------|--------|-------------|
| Статистика | Подробнее / Команда / Сравнить | `cmd_details`, `cmd_team`, `cmd_compare` |
| Период дайджеста | Сегодня / Неделя / Месяц | `dig_day`, `dig_week`, `dig_month` |
| Режим объединения | Последние N / Сегодня / По категории | `mrg_last`, `mrg_today`, `mrg_cat` |
| Действия с видео | Скачать / Транскр. / Оба | `vid_dl:{id}`, `vid_tr:{id}`, `vid_both:{id}` |
| Видео скачано | Подтвердить / Удалить | `vid_ok:{id}`, `vid_del:{id}` |
| После транскрипции | Скачать / Удалить | `vid_get:{id}`, `vid_del:{id}` |
| Облако | Google Drive / Yandex / Пропустить | `cloud_gd:{id}`, `cloud_yd:{id}`, `cloud_skip:{id}` |
| Чек подтверждён | Верно / Расходы | `fix_ok_{eid}`, `exp_e_today` |
| Период расходов | Сегодня / Неделя / Статистика | `exp_e_today`, `exp_e_week`, `exp_e_stats` |
| Удаление клиента | Одобрить / Отклонить | `approve_{rid}`, `reject_{rid}` |
| Pending approvals | Одобрить (первые 3) | `approve_{rid}` |

### List Menus (прокручиваемый список)

```python
wa_client.send_list(to, body, button_text, sections)
# sections: [{"title": "Секция", "rows": [{"id": ..., "title": ..., "description": ...}]}]
```

| Контекст | Текст кнопки | Строки |
|----------|-------------|--------|
| Период экспорта | "Выбрать" | Сегодня/Неделя/Месяц/Всё (`exp_today`..`exp_all`) |
| Формат экспорта | "Выбрать формат" | PDF/Excel/Markdown/Text (`expf_{period}_{fmt}`) |
| Категории объединения | "Категории" | Динамический список из CATEGORY_KEYWORDS (до 10) |
| Список клиентов (<=10) | "Показать" | Динамические строки (`cli_{phone}`) |
| Качество видео | "Качество" | 360p/720p/1080p/Best |
| Формат видео | "Формат" | MP4/MP3/MKV |

### Лимиты WhatsApp API

| Элемент | Лимит |
|---------|-------|
| Button title | 20 символов |
| Row title (list) | 24 символа |
| Row description | 72 символа |
| Max buttons | 3 на сообщение |
| Max rows per section | 10 |
| Document caption | 1024 символа |
| Text message | 4096 символов (автоматический сплит) |

### Reactions (эмодзи на сообщения)

```python
wa_client.send_reaction(to, message_id, emoji)
```

- Галочка на обработанные голосовые
- Значок заметки на голосовые-заметки
- Галочка на обработанные фото/чеки

---

## WhatsAppClient API Wrapper

**Файл:** `whatsapp/client.py`

Base URL: `https://graph.facebook.com/v21.0`

HTTP client: `httpx.AsyncClient` с таймаутами:
```python
httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
```

### Методы

| Метод | Описание |
|-------|----------|
| `download_media(media_id, dest_path) -> str` | 2-step: GET media URL -> GET binary -> save |
| `download_image(media_id, dest_path) -> str` | Alias для `download_media()` |
| `send_text(to, text) -> dict` | Отправка текста (автосплит >4096 символов) |
| `send_document(to, file_path, caption) -> dict` | 2-step: upload media -> send document |
| `mark_as_read(message_id) -> None` | Blue checkmarks (fail silently) |
| `send_buttons(to, body, buttons) -> dict` | Interactive Reply Buttons (макс 3) |
| `send_list(to, body, button_text, sections) -> dict` | Interactive List Menu |
| `send_reaction(to, message_id, emoji) -> dict` | Emoji reaction |

### Text Splitting

```python
def _split_text(text: str, max_len: int) -> list[str]:
```

Приоритет разбивки: newline -> space -> hard cut.

---

## Навигация (Screen Stack)

Идентичная система как в Telegram:

```python
push_screen(user_id, screen_name, params)
pop_screen(user_id) -> tuple | None
clear_stack(user_id)
is_back_command(text)
_render_screen()  # перерисовка экрана из стека (15+ типов экранов)
```

---

## Типы сообщений

| Тип | Обработчик | Обработка |
|-----|-----------|-----------|
| `audio` | `handle_audio_message` | Download OGG -> transcribe -> correct -> summarize -> respond |
| `text` | `handle_text_message` | Маршрутизация 35+ команд, детекция видео URL |
| `image` | `handle_image_message` | Receipt detection (OCR) или generic OCR |
| `interactive` | `handle_interactive_message` | Reply button callbacks и list menu selections |

---

## Конфигурация (.env)

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `WHATSAPP_TOKEN` | Да | Bearer token для Cloud API |
| `WHATSAPP_PHONE_ID` | Да | Phone Number ID |
| `WHATSAPP_VERIFY_TOKEN` | Да | Webhook verification token |
| `WHATSAPP_APP_SECRET` | Да | HMAC signature key |
| `WHATSAPP_ALLOWED_PHONES` | Да | Whitelist телефонов (через запятую) |

### Источники токенов

| Secret | Где получить |
|--------|-------------|
| `WHATSAPP_TOKEN` | Meta Business Suite -> System Users |
| `WHATSAPP_PHONE_ID` | Meta Developer Dashboard -> API Setup |
| `WHATSAPP_VERIFY_TOKEN` | Произвольная строка (вы выбираете) |
| `WHATSAPP_APP_SECRET` | Meta App Settings -> Basic |

---

## Запуск

### Локально (Windows)

```batch
cd /d D:\Downloads\VoiceTranscriptionBot
python -m whatsapp.app
```

### На сервере (systemd)

```bash
sudo systemctl start whatsapp_bot
```

Слушает на `0.0.0.0:8000`, за nginx reverse proxy.
