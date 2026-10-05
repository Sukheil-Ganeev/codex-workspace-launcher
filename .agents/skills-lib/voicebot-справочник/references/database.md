# Database -- SQLite Schema и CRUD

> Справочник по базе данных VoiceTranscriptionBot (v6.1.0)
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Файл: `bot/database.py` (~1764 строк, async aiosqlite)

---

## Общая информация

- **Движок:** SQLite (aiosqlite для async)
- **Путь по умолчанию:** `data/transcriptions.db`
- **Полнотекстовый поиск:** FTS5 с BM25 ранжированием
- **Класс:** `Database` в `bot/database.py`
- **Инициализация:** `await db.init()` -- создание таблиц, индексов, триггеров

---

## 16 таблиц (+ _schema_version)

> **v6.0.0:** 20 миграций через таблицу `_schema_version`. In-memory state управляется через `ExpiringDict` с TTL.

### 1. transcriptions (основная)

| Столбец | Тип | Default / Constraint | Версия |
|---------|-----|---------------------|--------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | v1.0 |
| `user_id` | INTEGER | NOT NULL | v1.0 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | v1.0 |
| `audio_duration` | REAL | -- | v1.0 |
| `language` | TEXT | -- | v1.0 |
| `transcription` | TEXT | NOT NULL | v1.0 |
| `summary` | TEXT | -- | v1.0 |
| `method` | TEXT | -- | v1.0 |
| `category` | TEXT | DEFAULT NULL | migration |
| `bookmarked` | INTEGER | DEFAULT 0 | migration |
| `sentiment` | TEXT | -- | v3.2.0 |
| `source_type` | TEXT | DEFAULT 'voice' | v3.2.0 |
| `confidence` | REAL | -- | v3.2.0 |
| `comment` | TEXT | -- | v3.2.0 |
| `pinned` | INTEGER | DEFAULT 0 | v3.2.0 |
| `key_facts` | TEXT | -- (JSON string) | v3.2.0 |
| `client_phone` | TEXT | -- | v3.2.0 |
| `tags` | TEXT | -- (comma-separated) | v3.7.0 |
| `is_note` | INTEGER | DEFAULT 0 | v3.7.0 |

**Индексы:**
- `idx_user_id` ON `transcriptions(user_id)`
- `idx_created_at` ON `transcriptions(created_at)`

### 2. transcriptions_fts (FTS5 Virtual Table)

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS transcriptions_fts USING fts5(
    transcription,
    summary,
    content='transcriptions',
    content_rowid='id'
);
```

- Content-sync с таблицей `transcriptions`
- Индексирует `transcription` и `summary`
- Токенизатор: unicode61 (default FTS5)
- Ранжирование: BM25 (встроенное)

### 3. transcriptions_archive (v3.6.0)

Идентичная схема с `transcriptions` плюс:

| Столбец | Тип | Default |
|---------|-----|---------|
| `archived_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

`id` -- INTEGER PRIMARY KEY (не AUTOINCREMENT), сохраняет оригинальный ID.

**Индексы:**
- `idx_archive_user` ON `transcriptions_archive(user_id)`
- `idx_archive_created` ON `transcriptions_archive(created_at)`

### 4. reminders

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | TEXT | NOT NULL |
| `text` | TEXT | NOT NULL |
| `remind_date` | TEXT | NOT NULL |
| `source_transcription_id` | INTEGER | -- |
| `created_at` | TEXT | DEFAULT (datetime('now')) |
| `sent` | INTEGER | DEFAULT 0 |

**Индексы:**
- `idx_reminders_user` ON `reminders(user_id)`
- `idx_reminders_date` ON `reminders(remind_date)`

### 5. expenses (v3.3.0)

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | NOT NULL |
| `amount` | REAL | NOT NULL |
| `currency` | TEXT | DEFAULT 'AED' |
| `amount_aed` | REAL | -- |
| `vendor` | TEXT | -- |
| `category` | TEXT | NOT NULL |
| `subcategory` | TEXT | -- |
| `expense_date` | TEXT | NOT NULL |
| `payment_method` | TEXT | -- |
| `description` | TEXT | -- |
| `ocr_text` | TEXT | -- |
| `receipt_source` | TEXT | -- |
| `receipt_confidence` | REAL | -- |
| `transcription_id` | INTEGER | FK -> transcriptions(id) |
| `items_json` | TEXT | -- (JSON string) |
| `reference` | TEXT | -- |
| `notes` | TEXT | -- |
| `tags` | TEXT | -- |
| `is_business` | INTEGER | DEFAULT 1 |
| `is_deleted` | INTEGER | DEFAULT 0 |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

**Индексы:**
- `idx_expenses_user` ON `expenses(user_id)`
- `idx_expenses_date` ON `expenses(expense_date)`
- `idx_expenses_category` ON `expenses(category)`
- `idx_expenses_vendor` ON `expenses(vendor)`

### 6. video_downloads (v3.8.0)

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | TEXT | NOT NULL |
| `platform` | TEXT | NOT NULL |
| `url` | TEXT | NOT NULL |
| `title` | TEXT | -- |
| `duration_seconds` | INTEGER | -- |
| `file_path` | TEXT | -- |
| `quality` | TEXT | -- |
| `format` | TEXT | -- |
| `status` | TEXT | NOT NULL DEFAULT 'pending' |
| `action` | TEXT | NOT NULL |
| `transcription_id` | INTEGER | FK -> transcriptions(id) |
| `downloaded_at` | DATETIME | -- |
| `expires_at` | DATETIME | NOT NULL |
| `user_confirmed_download` | INTEGER | DEFAULT 0 |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

**Индексы:**
- `idx_video_downloads_expires` ON `video_downloads(expires_at)`
- `idx_video_downloads_user` ON `video_downloads(user_id)`

### 7. cloud_uploads (v4.2.0)

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | TEXT | NOT NULL |
| `download_id` | INTEGER | -- |
| `service` | TEXT | NOT NULL |
| `file_id` | TEXT | NOT NULL |
| `file_name` | TEXT | -- |
| `file_size` | INTEGER | -- |
| `public_url` | TEXT | NOT NULL |
| `status` | TEXT | NOT NULL DEFAULT 'active' |
| `uploaded_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| `expires_at` | DATETIME | NOT NULL |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

**Индексы:**
- `idx_cloud_uploads_expires` ON `cloud_uploads(expires_at)`
- `idx_cloud_uploads_user` ON `cloud_uploads(user_id)`

**Примечание:** Управляется `CloudUploadTracker` через синхронный `sqlite3`, тот же файл БД.

### 8. conversations (v5.0.0)

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `phone` | TEXT | NOT NULL UNIQUE |
| `platform` | TEXT | NOT NULL (telegram/whatsapp) |
| `name` | TEXT | -- |
| `last_message_at` | DATETIME | -- |
| `unread_count` | INTEGER | DEFAULT 0 |
| `status` | TEXT | DEFAULT 'active' |
| `assigned_to` | TEXT | -- |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 9. messages (v5.0.0)

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `conversation_id` | INTEGER | FK -> conversations(id) |
| `direction` | TEXT | NOT NULL (in/out) |
| `content` | TEXT | NOT NULL |
| `message_type` | TEXT | DEFAULT 'text' |
| `sender_name` | TEXT | -- |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 10. admin_actions (v5.2.0)

Лог действий админов (аудит). Поля: `id`, `admin_id`, `action_type`, `target`, `details`, `created_at`.

### 11. chat_notes (v5.2.0)

Заметки к чатам. Поля: `id`, `conversation_id`, `admin_id`, `text`, `created_at`.

### 12. chat_tags (v5.2.0)

Теги чатов. Поля: `id`, `conversation_id`, `tag`, `created_at`.

### 13. blacklist (v5.2.0)

Чёрный список номеров. Поля: `id`, `phone`, `reason`, `banned_by`, `created_at`.

### 14. admin_reminders (v5.2.0)

Напоминания админа. Поля: `id`, `admin_id`, `conversation_id`, `text`, `remind_at`, `sent`, `created_at`.

### 15. _schema_version (v5.8.0)

| Столбец | Тип | Default / Constraint |
|---------|-----|---------------------|
| `version` | INTEGER | PRIMARY KEY |
| `description` | TEXT | -- |
| `applied_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

Содержит 20 миграций. Каждая миграция проверяет `MAX(version)` перед выполнением.

**Версионирование миграций (v6.0.0+):**
- При `init()` вызывается `_run_migrations()`, которая последовательно применяет непримеённые миграции
- Каждая миграция -- идемпотентная (безопасна при повторном запуске)
- Примеры миграций: добавление колонок (tags, is_note, pinned, key_facts), создание таблиц (expenses, conversations, messages, admin_actions, chat_notes, chat_tags, blacklist, admin_reminders, video_downloads, cloud_uploads), создание индексов

### 16. Не в SQLite: in-memory state

Глобальные dict с TTL через `ExpiringDict` (`core/expiring_dict.py`):
- `_search_queries`, `_merge_state`, `_pending_notes`, `_last_commands`, `_improve_state`

---

## FTS5 Search с BM25 Ranking

### Search метод

```python
async def search(
    self, user_id: int, query: str,
    offset: int = 0, limit: int = 5
) -> tuple[list[dict], int]:
```

### Как работает

1. JOIN между `transcriptions` и `transcriptions_fts`
2. FTS5 MATCH запрос: `f.transcriptions_fts MATCH ?`
3. Результаты упорядочены по `f.rank` (BM25 relevance)
4. Текст транскрипции обрезается до 200 символов
5. Возвращает `(results_list, total_count)`

### Поддерживаемый синтаксис FTS5

| Синтаксис | Пример | Описание |
|-----------|--------|----------|
| Простые слова | `яхта` | Поиск слова "яхта" |
| Фразы | `"аренда авто"` | Точная фраза |
| Boolean OR | `яхта OR авто` | Любой термин |
| Prefix | `транс*` | Префиксный поиск |

### Поля результата

`id`, `created_at`, `audio_duration`, `language`, `transcription` (200 chars), `summary`, `method`, `category`, `sentiment`, `source_type`, `confidence`, `pinned`

---

## Триггеры для FTS sync

Три триггера автоматически синхронизируют FTS5 с основной таблицей:

```sql
-- AFTER INSERT: добавить в FTS
CREATE TRIGGER transcriptions_ai AFTER INSERT ON transcriptions BEGIN
    INSERT INTO transcriptions_fts(rowid, transcription, summary)
    VALUES (new.id, new.transcription, new.summary);
END;

-- AFTER DELETE: удалить из FTS
CREATE TRIGGER transcriptions_ad AFTER DELETE ON transcriptions BEGIN
    INSERT INTO transcriptions_fts(transcriptions_fts, rowid, transcription, summary)
    VALUES ('delete', old.id, old.transcription, old.summary);
END;

-- AFTER UPDATE: обновить FTS (delete + insert)
CREATE TRIGGER transcriptions_au AFTER UPDATE ON transcriptions BEGIN
    INSERT INTO transcriptions_fts(transcriptions_fts, rowid, transcription, summary)
    VALUES ('delete', old.id, old.transcription, old.summary);
    INSERT INTO transcriptions_fts(rowid, transcription, summary)
    VALUES (new.id, new.transcription, new.summary);
END;
```

---

## 52 Async CRUD методов

### Transcriptions (12 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `save()` | `(user_id, audio_duration, language, transcription, summary, method, category?, sentiment?, source_type?, confidence?, key_facts?, client_phone?, tags?, is_note?) -> int` | Вставить запись |
| `get_record()` | `(record_id) -> dict|None` | Одна запись (без фильтра user) |
| `get_history()` | `(user_id, limit=10) -> list[dict]` | Последние N, текст 200 chars |
| `get_history_full()` | `(user_id, limit=10) -> list[dict]` | Последние N, полный текст |
| `get_history_page()` | `(user_id, offset=0, limit=5, category?, bookmarked?, pinned_first=True) -> (list, int)` | Пагинация с фильтрами |
| `get_transcription()` | `(record_id) -> dict|None` | SELECT * по ID |
| `get_notes()` | `(user_id, tag?, offset=0, limit=20) -> (list, int)` | Заметки с пагинацией |
| `get_today_transcriptions()` | `(user_id) -> list[dict]` | За сегодня |
| `get_week_transcriptions()` | `(user_id) -> list[dict]` | За 7 дней |
| `get_month_transcriptions()` | `(user_id) -> list[dict]` | За 30 дней |
| `get_transcriptions_by_category()` | `(user_id, category, limit=10) -> list[dict]` | По категории |
| `get_transcriptions_by_date()` | `(user_id, date_str) -> list[dict]` | По точной дате |
| `get_bookmarked()` | `(user_id) -> list[dict]` | Все закладки |

### Update Operations (7 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `toggle_bookmark()` | `(record_id, user_id) -> bool` | Toggle закладки |
| `toggle_pin()` | `(record_id, user_id) -> bool` | Toggle закрепления |
| `update_category()` | `(record_id, category) -> bool` | Обновить категорию + undo log |
| `update_sentiment()` | `(record_id, sentiment) -> bool` | Обновить тональность |
| `add_comment()` | `(record_id, comment) -> bool` | Добавить комментарий |
| `undo_last_action()` | `(user_id) -> dict|None` | Отмена за 30 сек |
| `find_duplicate()` | `(user_id, duration, within_seconds=60) -> bool` | Детекция дубликатов |

### Statistics (8 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `get_stats()` | `(user_id) -> dict` | total_count, total_duration_minutes, methods |
| `get_category_stats()` | `(user_id, date_filter) -> dict` | {category: count} по периоду |
| `get_period_stats()` | `(user_id, start_date, end_date) -> dict` | Статистика за период |
| `get_dashboard_stats()` | `(team_user_ids?) -> dict` | today/yesterday/week, тренды |
| `get_peak_hours()` | `(user_id, days=7) -> dict[int,int]` | {hour: count} |
| `get_category_trends()` | `(user_id) -> dict` | Текущий vs предыдущий месяц |
| `get_sentiment_by_category()` | `(user_id) -> dict` | Тональность по категориям |
| `get_month_comparison()` | `(user_id) -> dict` | Месяц vs месяц |

### Search (1 метод)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `search()` | `(user_id, query, offset=0, limit=5) -> (list, int)` | FTS5 поиск с BM25 |

### Reminders (5 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `add_reminder()` | `(user_id, text, remind_date, source_id?) -> int` | Создать |
| `get_pending_reminders()` | `(target_date) -> list[dict]` | Неотправленные |
| `get_user_reminders()` | `(user_id, limit=10) -> list[dict]` | Напоминания пользователя |
| `mark_reminder_sent()` | `(reminder_id)` | Пометить отправленным |
| `delete_reminder()` | `(reminder_id) -> bool` | Удалить |

### Expenses (6 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `save_expense()` | `(user_id, amount, category, expense_date, ...) -> int` | Создать (16 параметров) |
| `get_expenses()` | `(user_id?, period, category?, limit=50) -> list[dict]` | Фильтрованный список |
| `get_expense()` | `(expense_id) -> dict|None` | Одна запись |
| `delete_expense()` | `(expense_id) -> bool` | Soft delete (is_deleted=1) |
| `update_expense()` | `(expense_id, **fields) -> bool` | Частичное обновление |
| `get_expense_stats()` | `(user_id?, period='month') -> dict` | Статистика расходов |

### Video Downloads (6 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `save_video_download()` | `(user_id, platform, url, title, ...) -> int` | Создать |
| `update_video_status()` | `(download_id, status, file_path?) -> None` | Обновить статус |
| `confirm_video_downloaded()` | `(download_id)` | expires_at = now + 1 day |
| `delete_video_download()` | `(download_id)` | status='deleted' |
| `get_expired_videos()` | `() -> list[dict]` | Истёкшие, не удалённые |
| `get_video_download()` | `(download_id) -> dict|None` | По ID |

### System (5 методов)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `init()` | `() -> None` | Создание таблиц, индексов, триггеров, миграции |
| `close()` | `() -> None` | Закрыть соединение |
| `get_system_health()` | `() -> dict` | db_size_mb, counts |
| `get_db_size_mb()` | `() -> float` | Размер файла БД |
| `vacuum()` | `() -> dict` | VACUUM + ANALYZE, returns {before_mb, after_mb} |

### Archive (2 метода)

| Метод | Сигнатура | Описание |
|-------|-----------|----------|
| `count_archivable_transcriptions()` | `(days=180) -> int` | Количество для архивации |
| `execute_archive_transcriptions()` | `(days=180) -> int` | INSERT INTO archive + DELETE |

---

## Archive Logic (180 дней)

### Процесс архивации

1. `INSERT INTO transcriptions_archive SELECT ... WHERE created_at < datetime('now', '-180 days')`
2. `DELETE FROM transcriptions WHERE created_at < datetime('now', '-180 days')`
3. FTS5 триггеры автоматически очищают индекс
4. Возвращает количество архивированных записей

### Расписание

- **Когда:** 1-е число каждого месяца, 04:00 Dubai
- **Процесс:** Создаётся approval request (level B)
- **Выполнение:** После одобрения администратором

---

## VACUUM (monthly, >5MB)

```python
async def vacuum(self) -> dict:
    # 1. PRAGMA wal_checkpoint(TRUNCATE)
    # 2. Close connection
    # 3. Open new, run VACUUM + ANALYZE
    # 4. Close, reopen with row_factory
    # Returns: {"before_mb": float, "after_mb": float}
```

### Расписание

- **Когда:** 1-е число каждого месяца, 04:00 Dubai
- **Условие:** Только если DB > 5 MB
- **Процесс:** Создаётся approval request (level A)

---

## Конфигурация

| Переменная | Default | Описание |
|------------|---------|----------|
| `DB_PATH` | `{BASE_DIR}/data/transcriptions.db` | Путь к SQLite файлу |

---

## Расписание очистки

| Что | Когда | Условие |
|-----|-------|---------|
| Архивация транскрипций | 1-е число, 04:00 | >180 дней -> approval B |
| DB VACUUM | 1-е число, 04:00 | DB >5MB -> approval A |
| Video downloads | 03:00 ежедневно | expires_at прошёл |
| Cloud uploads | Каждый час | expires_at прошёл |
| Expired approvals | Каждый час | Автопометка |
| Old approvals purge | Воскресенье 04:00 | >90 дней resolved |

---

## Интеграция с LLMClient (v6.1.0)

### lessons.json и AI-промпты

**Файл:** `data/lessons.json` -- хранилище уроков (12 типов, дедупликация).

Уроки интегрируются в AI-промпты через `core/llm_client.py`:
- `LessonManager.get_relevant(type, context)` -- выбирает релевантные уроки
- Уроки инжектируются в промпт 6 модулей: `accounting.py`, `corrector.py`, `categories.py`, `sentiment.py`, `summarizer.py`, `key_facts.py`
- Все эти модули вызывают AI через единый `services.llm.generate()` (каскад Gemini -> Groq)
- Модели: `gemini-2.5-flash` (primary), `gemini-2.5-flash-lite` (lightweight), Groq Llama (fallback)

### TaskType routing в БД-контексте

Когда данные извлекаются из БД для AI-обработки, используется `TaskType`:
- `CLASSIFICATION` -- категоризация транскрипций (-> `transcriptions.category`)
- `ANALYSIS` -- тональность (-> `transcriptions.sentiment`), ключевые факты (-> `transcriptions.key_facts`)
- `VISION` -- OCR чеков (-> `expenses` таблица)
