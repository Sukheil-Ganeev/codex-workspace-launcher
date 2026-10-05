# Telegram Bot -- Полная справка

> Справочник по Telegram-боту VoiceTranscriptionBot (v6.1.0)
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Основные файлы: `bot/main.py`, `bot/handlers.py` (хаб-маршрутизатор, 258 строк) + 12 доменных модулей, `bot/auto_delete.py`

---

## Фреймворк и конфигурация

- **Фреймворк:** aiogram v3.x
- **Режим:** Long polling (не webhook)
- **Parse mode:** HTML (по умолчанию)
- **Обработка:** `message` и `callback_query` update types

```python
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(router)  # Единый Router(name="main"), хаб-маршрутизатор регистрирует 12 доменных модулей
await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
```

---

## Startup Sequence

1. Создание `TEMP_DIR` и директории для `DB_PATH`
2. `await init_services()` -- инициализация Transcriber, Summarizer, Database
3. Создание Bot и Dispatcher, подключение router
4. Установка Telegram menu commands (23 команды в меню)
5. Запуск фоновых задач:
   - `run_daily_digest()` -- дайджест в 21:00 по Дубаю
   - `run_cloud_cleanup_loop()` -- очистка облачных загрузок каждый час
6. Запуск polling
7. На shutdown: отмена задач, закрытие сессии бота

---

## Все 30 команд

> **Архитектура v6.0.0+:** `bot/handlers.py` -- хаб-маршрутизатор (258 строк), регистрирует 12 доменных модулей:
> `handlers_voice`, `handlers_video`, `handlers_export`, `handlers_calc`, `handlers_callbacks`,
> `handlers_stats`, `handlers_clients`, `handlers_admin_commands`, `handlers_text`, `handlers_common`, `handlers_templates`
>
> **v6.1.0 -- LLMClient:** Все AI-вызовы проходят через единый `core/llm_client.py` с каскадом Gemini -> Groq.
> Используется в `handlers_voice` (транскрипция, коррекция), `handlers_text` (перевод, улучшение, форматирование),
> а также в OCR-обработке фото/PDF. 6 типов задач (`TaskType`): CLASSIFICATION, ANALYSIS, CREATIVE, VISION, TRANSFORMATION, PLANNING.

### 23 команды в меню Telegram

| # | Команда | Описание | Обработчик | Модуль |
|---|---------|----------|-----------|--------|
| 1 | `/start` | Начать работу | `cmd_start` | handlers_common |
| 2 | `/help` | Справка по командам | `cmd_help` | handlers_common |
| 3 | `/stats` | Статистика и дашборд | `cmd_stats` | handlers_stats |
| 4 | `/digest` | AI-резюме дня | `cmd_digest` | handlers_stats |
| 5 | `/history` | История записей | `cmd_history` | handlers_stats |
| 6 | `/search` | Поиск по записям | `cmd_search` | handlers_stats |
| 7 | `/notes` | Голосовые заметки | `cmd_notes` | handlers_stats |
| 8 | `/merge` | Объединить голосовые | `cmd_merge` | handlers_stats |
| 9 | `/export` | Экспорт записей | `cmd_export` | handlers_export |
| 10 | `/date` | Поиск по дате | `cmd_date` | handlers_stats |
| 11 | `/compare` | Сравнение периодов | `cmd_compare` | handlers_stats |
| 12 | `/clients` | База клиентов | `cmd_clients` | handlers_clients |
| 13 | `/price` | Прайс-лист | `cmd_price` | handlers_common |
| 14 | `/expenses` | Расходы | `cmd_expenses` | handlers_clients |
| 15 | `/report` | Финансовый отчёт | `cmd_report` | handlers_export |
| 16 | `/settings` | Настройки | `cmd_settings` | handlers_common |
| 17 | `/health` | Здоровье системы | `cmd_health` | handlers_clients |
| 18 | `/archive` | Архивация записей | `cmd_archive` | handlers_admin_commands |
| 19 | `/calc` | Калькулятор (валюты, туры, агент) | `cmd_calc` | handlers_calc |
| 20 | `/rate` | Текущие курсы валют | `cmd_rate` | handlers_calc |
| 21 | `/route` | Маршруты Google Maps | `cmd_route` | handlers_calc |
| 22 | `/improve` | Улучшить текст (4 получателя, 3 тона) | `cmd_improve` | handlers_text |
| 23 | `/templates` | Шаблоны быстрых ответов | -- | handlers_templates |

### 7 дополнительных команд (не в меню)

| # | Команда | Описание | Обработчик | Модуль |
|---|---------|----------|-----------|--------|
| 24 | `/add_expense` | Ручной расход: `/add_expense 150 бензин ADNOC` | `cmd_add_expense` | handlers_clients |
| 25 | `/lessons` | Уроки бота: `/lessons [list|stats|type]` | `cmd_lessons` | handlers_clients |
| 26 | `/fix` | Исправить расход: `/fix EID field VALUE` | `cmd_fix` | handlers_clients |
| 27 | `/pending` | Ожидающие подтверждения | `cmd_pending` | handlers_admin_commands |
| 28 | `/approvals` | История подтверждений | `cmd_approvals` | handlers_admin_commands |
| 29 | `/approve` | Одобрить: `/approve OPT-XXXX-XX-XX-XXXX` | `cmd_approve` | handlers_admin_commands |
| 30 | `/reject` | Отклонить: `/reject OPT-XXXX-XX-XX-XXXX [причина]` | `cmd_reject` | handlers_admin_commands |

---

## 19+ текстовых триггеров

Триггеры без `/` -- обрабатываются как текстовые сообщения (модуль `handlers_text`).
Также: 32 триггера переводчика, 32 триггера форматирования, 20 триггеров улучшения (см. `core/translator.py`, `core/improver.py`).

| # | Триггер | Действие | Обработчик |
|---|---------|----------|-----------|
| 1 | `дайджест за неделю` | Дайджест за неделю | `text_digest_week` |
| 2 | `дайджест за месяц` | Дайджест за месяц | `text_digest_month` |
| 3 | `дайджест` | Дайджест за день | `text_digest` |
| 4 | `объедини [N]` | Объединить N голосовых | `text_merge` |
| 5 | `дата <дата>` | Поиск по дате | `text_date` |
| 6 | `сравни` / `compare` / `сравнение` | Сравнение периодов | `text_compare` |
| 7 | `экспорт пдф` | Экспорт PDF | `text_export_pdf` |
| 8 | `экспорт эксель` | Экспорт Excel | `text_export_xlsx` |
| 9 | `экспорт мд` | Экспорт Markdown | `text_export_md` |
| 10 | `экспорт` / `export` | Меню экспорта | `text_export` |
| 11 | `заметки [#тег]` | Список заметок | `text_notes` |
| 12 | `настройки` / `settings` | Настройки | `text_settings` |
| 13 | `статус` / `статистика` / `stats` / `дашборд` / `пульс` / `dashboard` / `кабинет` / `cabinet` | Дашборд | `text_stats` |
| 14 | `клиенты` / `clients` | Список клиентов | `text_clients` |
| 15 | `команда` / `team` | Доска команды | `text_team` |
| 16 | `история` / `history` | История | `text_history` |
| 17 | `назад` / `back` (через `is_back_command()`) | Назад | `text_back` |
| 18 | `добавить клиент PHONE Name [type]` | Добавить клиента | `text_add_client` |
| 19 | `удалить клиент PHONE` | Удалить клиента | `text_remove_client` |

**Особый триггер:** Любой URL видео (YouTube, TikTok, etc.) -- `handle_video_url`.

---

## 50+ Callback паттернов

Все callbacks маршрутизируются через единый обработчик:

```python
@router.callback_query()
async def cb_handler(callback: CallbackQuery) -> None:
```

Роутинг через `data.startswith()` в цепочке if/elif.

### Навигация

| Паттерн | Описание |
|---------|----------|
| `back:TARGET` | Назад к: start, stats, history, clients, digest, merge, export, settings |

### История

| Паттерн | Описание |
|---------|----------|
| `hist_full:RECORD_ID` | Полные детали записи |
| `hist:PAGE[:bk|:cat:NAME]` | Пагинация с фильтрами |
| `hist_cat_menu` | Меню фильтра по категории |
| `edit_cat:RECORD_ID` | UI редактирования категории |
| `cat_set:RECORD_ID:CATEGORY` | Применить категорию |

### Поиск

| Паттерн | Описание |
|---------|----------|
| `srch:HASH:PAGE` | Пагинация результатов поиска |

### Дайджест

| Паттерн | Описание |
|---------|----------|
| `dig:day|week|month` | Выбор периода дайджеста |

### Объединение

| Паттерн | Описание |
|---------|----------|
| `mrg_confirm:COUNT` | Подтвердить объединение |
| `mrg:last|today|cat` | Выбор режима объединения |
| `merge:COUNT` | Объединить из inline-кнопок голосового |

### Экспорт

| Паттерн | Описание |
|---------|----------|
| `exp_f:PERIOD:FORMAT` | Выбор формата (pdf, xlsx, md, txt, all, bk) |
| `exp_p:PERIOD` | Выбор периода (day, week, month, all) |
| `export_FORMAT` | Legacy-кнопки экспорта |

### Клиенты

| Паттерн | Описание |
|---------|----------|
| `cl_hist:PHONE` | История клиента |
| `cl_note:PHONE` | Добавить заметку |
| `cl_del:PHONE` | Удалить (через approval) |
| `cl_add` | Добавить клиента |
| `cl_search` | Поиск клиентов |
| `cl:PHONE` | Карточка клиента |

### Действия с записями

| Паттерн | Описание |
|---------|----------|
| `pin:RECORD_ID` | Toggle pin |
| `undo:USER_ID` | Отмена последнего действия |
| `bookmark:RECORD_ID` | Toggle закладки |
| `forward:RECORD_ID` | Переслать команде |

### Быстрые действия

| Паттерн | Описание |
|---------|----------|
| `digest` | Быстрый дайджест |
| `history` | Быстрая история |
| `team` | Доска команды |
| `team_filter_CATEGORY` | Фильтр команды по категории |

### Статистика

| Паттерн | Описание |
|---------|----------|
| `stats_detail` | Toast "уже на экране" |
| `stats_compare` | Перенаправление на сравнение |
| `stats` | Перерисовка статистики |

### Настройки

| Паттерн | Описание |
|---------|----------|
| `settings_notifications` | Toggle уведомлений |
| `settings_forward` | Toggle пересылки |
| `settings_language` | Toggle языка (ru/en) |
| `settings_digest` | Изменить время дайджеста |

### Расходы

| Паттерн | Описание |
|---------|----------|
| `exp_e:today|week|month|stats` | Период/статистика расходов |
| `fix_rcpt:FIELD:EID` | Коррекция чека |
| `fix_rcpt_cat:CATEGORY:EID` | Категория чека + урок |

### Голосовые исправления

| Паттерн | Описание |
|---------|----------|
| `fix_voice_cat:RECORD_ID` | UI коррекции категории |
| `fix_voice_cat_set:CAT:RID` | Применить + урок |
| `fix_voice_sent:RECORD_ID` | UI коррекции тональности |
| `fix_voice_sent_set:SENT:RID` | Применить + урок |

### Подтверждения (Approvals)

| Паттерн | Описание |
|---------|----------|
| `approve:OPT_ID` | Одобрить запрос |
| `reject:OPT_ID` | Отклонить запрос |
| `detail:OPT_ID` | Детали запроса |

### Видео

| Паттерн | Описание |
|---------|----------|
| `vid_action:DL_ID:ACTION` | Действие (download/transcribe/both) |
| `vid_quality:DL_ID:QUALITY` | Выбор качества |
| `vid_format:DL_ID:FORMAT` | Выбор формата -> начало загрузки |
| `vid_confirm:DL_ID` | Подтвердить загрузку |
| `vid_delete:DL_ID` | Удалить файл |
| `vid_dl_file:DL_ID` | Скачать файл после транскрипции |
| `cloud_up:DL_ID:SERVICE` | Облачная загрузка (gdrive/yadisk/skip) |

### Прочие

| Паттерн | Описание |
|---------|----------|
| `bookmarks_cb` | Закладки (legacy) |
| `notes` | Показать заметки |
| `delete_note:RECORD_ID` | Удалить заметку (approval) |
| `lessons_stats` | Статистика уроков |

---

## Middleware

### WhitelistMiddleware

```python
class WhitelistMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        if user is None or user.id not in config.ALLOWED_USER_IDS:
            return  # молча игнорировать
        return await handler(event, data)
```

- **Применяется к:** `router.message` (не callback_query)
- **Поведение:** Молча отбрасывает сообщения от неавторизованных пользователей
- **Безопасность callback_query:** Callbacks могут прийти только от пользователей, прошедших whitelist для сообщений

---

## Обработка голосовых сообщений

### Регистрация

```python
@router.message(F.voice | F.audio)
async def handle_voice(message: Message, bot: Bot) -> None:
```

### Pipeline

1. **Download:** `bot.download(voice.file_id, destination=temp_path)` -- сохраняет `.ogg`
2. **Progress:** Отправляет "Распознаю голосовое...", создаёт `_progress` callback
3. **Pipeline:** `process_voice(audio_path, user_id, platform, progress_callback)`
4. **Error:** При `result.error` -- удаляет progress msg, отправляет ошибку через `send_temp()`
5. **Note shortcut:** При `result.is_note` -- компактный формат с кнопками Save/Delete/All Notes
6. **Full transcription:**
   - Форматирование через `format_transcription()`
   - Добавление перевода (если есть)
   - Добавление ключевых фактов
   - Inline keyboard (5 рядов)
7. **Urgent auto-forward:** При `result.is_urgent` -- рассылка всем участникам команды
8. **Cleanup:** Удаление `.ogg` в `finally` блоке

---

## Inline Keyboard Layouts (15+ типов)

### Ответ на голосовое сообщение

```
[Сохранить]  [Закрепить]
[Объединить 2]  [Объединить 3]
[Дайджест]  [История]
[Категория]  [Тональность]
[-> Переслать NAME]  (условная, если ответственный != отправитель)
```

### Ответ на заметку

```
[Сохранить]  [Удалить]
[Все заметки]
```

### Дашборд статистики

```
[Подробнее]  [Команда]
[Сравнить]  [<- Назад]
```

### Выбор периода дайджеста

```
[Сегодня]  [Неделя]  [Месяц]
[<- Назад]
```

### История (пагинация)

```
[<- пред]  [след ->]        (условные стрелки)
[Избранные]  [Категория]     (фильтры)
[#id1]  [#id2]  [#id3]      (до 3 записей)
[<- Назад]
```

### Детали записи

```
[Сохранить]  [Закрепить/Открепить]
[Изменить категорию]  [<- Назад]
```

### Режим объединения

```
[Последние N]  [Сегодня]  [По категории]
[<- Назад]
```

### Выбор количества (режим Last N)

```
[2]  [3]  [5]  [10]
[<- Назад]
```

### Период экспорта

```
[Сегодня]  [Неделя]
[Месяц]  [Всё]
[<- Назад]
```

### Формат экспорта

```
[PDF]  [Excel]
[Markdown]  [TXT]
[Все форматы]  [Только закладки]
[<- Назад]
```

### Список клиентов

```
[Клиент1]  [Клиент2]     (до 10 клиентов, 2 в ряд)
...
[+ Добавить]  [Поиск]  [<- Назад]
```

### Карточка клиента

```
[История]  [Заметка]
[Удалить]  [<- Назад]
```

### Расходы

```
[Сегодня]  [Неделя]  [Месяц]
[Статистика]  [<- Назад]
```

### Подтверждение чека

```
[Сумма]  [Продавец]  [Категория]
[Верно]  [Удалить]
[Расходы]  [Статистика]
```

### Настройки

```
[Время дайджеста]  [Уведомления: Вкл/Выкл]
[Язык: RU/EN]  [Автопересылка: Вкл/Выкл]
[<- Назад]
```

### Доска команды

```
[Экскурсии]  [Авто]  [Яхты]
[Абаи]  [Все]  [<- Назад]
```

### Ожидающие подтверждения

```
[Одобрить]  [Отклонить]  [Детали]    (на каждый запрос)
```

### Действия с видео

```
[Скачать]  [Транскрибировать]
[Скачать + Транскрибировать]
```

### Облачная загрузка (для файлов >49MB)

```
[Google Drive]  [Yandex Disk]  [Не загружать]
```

---

## Auto-Delete System

**Файл:** `bot/auto_delete.py`

### Функции

```python
async def auto_delete(msg: Message, delay: float) -> None:
    """Фоновая задача -- удаляет сообщение через delay секунд."""

async def send_temp(target: Message, text: str, delay: float, **kwargs) -> Message:
    """Отправляет сообщение и планирует его удаление."""
```

### Задержки

| Константа | Секунды | Использование |
|-----------|---------|---------------|
| `DELAY_CONFIRM` | 15 | Подтверждения ("Настройка обновлена") |
| `DELAY_ERROR` | 20 | Ошибки ("Не найдено") |
| `DELAY_HINT` | 25 | Подсказки ("Формат: /search запрос") |
| `DELAY_SESSION` | 20 | Истечение сессии поиска |

### Silent Failure

Если удаление не удалось (сообщение уже удалено, нет прав), логируется на DEBUG уровне без ошибки.

---

## Навигация (Screen Stack)

```python
push_screen(user_id, screen_name, params)  # Добавить экран в стек
pop_screen(user_id)                         # Вернуться назад
clear_stack(user_id)                        # Сбросить стек
is_back_command(text)                       # Проверка: "назад"/"back"
```

### Маршрутизация кнопки "Назад"

| Target | Действие |
|--------|----------|
| `start` | Стартовое сообщение |
| `stats` | Перерисовка дашборда |
| `history` | Страница 1 истории |
| `clients` | Список клиентов |
| `digest` | Выбор периода дайджеста |
| `merge` | Выбор режима объединения |
| `export` | Выбор периода экспорта |
| `settings` | Перерисовка настроек |

---

## Module-Level State

| Переменная | Тип | Назначение |
|------------|-----|-----------|
| `_search_queries` | `dict[str, str]` | MD5 хеш -> поисковый запрос |
| `_merge_state` | `dict[int, dict]` | user_id -> состояние объединения |
| `_pending_notes` | `dict[int, str]` | user_id -> phone (ожидание ввода заметки) |
| `_team` | `TeamManager | None` | Lazy-loaded singleton |

---

## Обработка фото и документов

### Photo Handler

```python
@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot) -> None:
```

1. Сначала пытается распознать чек через `parse_receipt()`
2. Если чек -- сохраняет как расход с кнопками коррекции
3. Иначе -- стандартный OCR через `process_image()`

### Document Handler (PDF)

```python
@router.message(F.document)
async def handle_document(message: Message, bot: Bot) -> None:
```

- Только `application/pdf` MIME тип
- Обработка через `process_image()` с `source_type="document"`

---

## Система уроков (Self-Learning)

### Типы уроков

- `receipt_amount`, `receipt_vendor`, `receipt_category` -- коррекция чеков
- `voice_correction`, `voice_category`, `voice_sentiment` -- коррекция голосовых

### Поток коррекции

1. Пользователь нажимает "Категория" или "Тональность"
2. Бот показывает кнопки выбора
3. Пользователь выбирает правильное значение
4. Бот обновляет запись И вызывает `services.lessons.record_lesson()`
5. Подтверждение "Урок записан!"
6. При следующей обработке -- уроки инжектируются в промпт

---

## Scheduler (фоновые задачи)

| Задача | Расписание | Описание |
|--------|-----------|----------|
| Daily Digest (TG) | Персональное время (default 21:00 Dubai) | AI дайджест в Telegram |
| Weekly Report | Воскресенье 20:00 Dubai | PDF отчёт всем пользователям |
| Temp Cleanup | Каждый час | Удаление temp файлов > 24ч |
| Approval Expiration | Каждый час | Пометка истёкших запросов |
| Cloud Upload Cleanup | Каждый час | Удаление истёкших облачных загрузок |
| Video Cleanup | 03:00 Dubai ежедневно | Удаление истёкших видео |
| Monthly Archive | 1-е число, 04:00 Dubai | Архивация записей >6 мес. |
| Monthly VACUUM | 1-е число, 04:00 Dubai | Оптимизация БД (если >5MB) |

---

## Обработка очереди

In-memory очередь для управления нагрузкой:

```python
add_to_queue(user_id) -> int      # Добавить, вернуть позицию
remove_from_queue(user_id)         # Удалить после обработки
get_queue_message(user_id)         # Сообщение если очередь >= 5
```

`QUEUE_DISPLAY_THRESHOLD = 5` -- позиция показывается только при 5+ ожидающих.

---

## Новые фичи v5.4-v6.0

### Цветные кнопки (Bot API 9.4, aiogram 3.25)

~230 inline-кнопок со стилями `success` (зелёный), `danger` (красный), `primary` (синий).
Зелёные для подтверждений, красные для удалений, синие для основных действий.

### FSM-состояния калькулятора

4 состояния: конвертация / тур / агент / маршрут. Умный парсинг чисел, кнопка отмена.

### Onboarding

Мини-тур для новых пользователей (0 транскрипций = короткое приветствие + кнопки).

### /quick

Повтор последней команды (24ч TTL).

### ExpiringDict

Глобальные state-dict с TTL и size limit (`core/expiring_dict.py`). 5 dict конвертированы.

---

## AI Architecture (v6.1.0)

### LLMClient -- единый AI-клиент

**Файл:** `core/llm_client.py`

Все AI-вызовы в боте проходят через `services.llm.generate()` вместо прямого доступа к Gemini/Groq SDK.

**Каскад:** Gemini (primary) -> Groq Llama (fallback)

**6 типов задач (TaskType):**

| TaskType | Описание | Где используется |
|----------|----------|-----------------|
| `CLASSIFICATION` | Категоризация, определение типа | categories.py, note_detector.py |
| `ANALYSIS` | Анализ тональности, ключевых фактов | sentiment.py, key_facts.py |
| `CREATIVE` | Резюме, улучшение текста | summarizer.py, improver.py |
| `VISION` | OCR, распознавание чеков | ocr.py, accounting.py |
| `TRANSFORMATION` | Перевод, коррекция, форматирование | translator.py, corrector.py, formatter_tour.py |
| `PLANNING` | Маршруты, расчёты | calculator.py, router.py |

**Константы моделей:**
- `GEMINI_MODELS` = gemini-2.5-flash (primary)
- `GEMINI_MODELS_LIGHT` = gemini-2.5-flash-lite (lightweight tasks)
- `GROQ_MODEL` = llama fallback

**Deprecated модели (заменены в v6.1.0):**
- `gemini-2.0-flash` -> `gemini-2.5-flash`
- `gemini-2.0-flash-lite` -> `gemini-2.5-flash-lite`

### Split handlers (v6.0.0)

Монолит `bot/handlers.py` (6325 строк) разбит на 12 доменных модулей:

| Модуль | Строк | Ответственность |
|--------|-------|-----------------|
| `handlers_voice.py` | ~200 | Голосовые, аудио (транскрипция, коррекция, прогресс) |
| `handlers_video.py` | ~150 | Видео-ссылки (скачивание, облачная загрузка) |
| `handlers_export.py` | ~100 | Экспорт (PDF, Excel, MD, TXT) |
| `handlers_calc.py` | ~150 | Калькулятор, маршруты (FSM) |
| `handlers_callbacks.py` | ~400 | Inline-кнопки, callback routing |
| `handlers_stats.py` | ~200 | Статистика, дайджест, история, поиск |
| `handlers_clients.py` | ~200 | Клиенты, расходы, уроки, здоровье |
| `handlers_admin_commands.py` | ~100 | Approve, reject, archive |
| `handlers_text.py` | ~150 | Текстовые триггеры (перевод, улучшение, форматирование) |
| `handlers_common.py` | ~100 | /start, /help, /settings, /quick |
| `handlers_templates.py` | ~80 | Шаблоны быстрых ответов |
| `handlers.py` (хаб) | 258 | Регистрация модулей, middleware, router |

**2138 тестов** -- все проходят (pytest).
