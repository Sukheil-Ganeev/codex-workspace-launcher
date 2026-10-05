# Security -- Безопасность системы

> Справочник по безопасности VoiceTranscriptionBot (v6.1.0)
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Файлы: `whatsapp/security.py`, `whatsapp/app.py`, `whatsapp/handlers.py`, `bot/handlers.py`, `core/approval.py`, `core/log_sanitizer.py`, `core/validators.py`, `core/db_security.py`

---

## HMAC-SHA256 верификация Webhook

**Файл:** `whatsapp/security.py`

### Функция

```python
def verify_signature(payload: bytes, signature: str, app_secret: str) -> bool:
```

### Процесс верификации

1. Проверить наличие `signature` и `app_secret` (отклонить если любое отсутствует)
2. Проверить префикс `sha256=` в заголовке подписи
3. Извлечь hex digest после префикса
4. Вычислить ожидаемый HMAC-SHA256:
   ```python
   hmac.new(key=app_secret.encode(), msg=payload, digestmod=sha256).hexdigest()
   ```
5. **Timing-safe сравнение** через `hmac.compare_digest()` -- защита от timing-атак
6. Return `True` только при совпадении дайджестов

### Вызов из webhook

```python
# whatsapp/app.py
raw_body = await request.body()
signature = request.headers.get("X-Hub-Signature-256", "")
if not verify_signature(raw_body, signature, WHATSAPP_APP_SECRET):
    raise HTTPException(status_code=403, detail="Invalid signature")
```

---

## Replay Protection (защита от replay-атак)

**Файл:** `whatsapp/security.py`

### Функция

```python
def verify_timestamp(timestamp: int, max_age_sec: int = 300) -> bool:
```

### Параметры

| Параметр | Значение | Описание |
|----------|----------|----------|
| `max_age_sec` | 300 (5 минут) | Максимальный возраст сообщения |
| Clock skew | 30 секунд | Допуск для будущих timestamp |

### Логика

- Отклоняет сообщения старше **5 минут**
- Допускает **30-секундный** сдвиг для будущих timestamp (компенсация рассинхронизации часов)
- Функция существует в коде и готова к активации в webhook handler

---

## Phone Whitelist (белый список телефонов)

### WhatsApp

**Файл:** `whatsapp/handlers.py`

```python
def is_allowed(phone: str) -> bool:
    if not WHATSAPP_ALLOWED_PHONES:
        return False  # Пустой whitelist = отклонить всех
    return phone in WHATSAPP_ALLOWED_PHONES
```

- Конфигурация: `WHATSAPP_ALLOWED_PHONES` (телефоны через запятую)
- **Deny-by-default:** пустой whitelist = ВСЕ отклонены
- Несанкционированные сообщения молча игнорируются (без ответа)

### Telegram

**Файл:** `bot/handlers.py`

```python
class WhitelistMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        if user is None or user.id not in config.ALLOWED_USER_IDS:
            return  # молча игнорировать
        return await handler(event, data)
```

- Конфигурация: `ALLOWED_USER_IDS` (Telegram user ID через запятую)
- Применяется к `router.message` (не callback_query)
- **Deny-by-default:** пустой whitelist = ВСЕ отклонены

---

## Approval System (2 уровня)

**Файл:** `core/approval.py`

### 2 уровня авторизации

| Уровень | Срок | Использование |
|---------|------|---------------|
| **A** (lightweight) | 24 часа | Удаление одного элемента, DB VACUUM |
| **B** (full report) | 48 часов | Массовые операции: архивация, объединение, очистка |

### Роли и разрешения

| Роль | Что может подтвердить |
|------|----------------------|
| **admin** | Всё |
| **member** | Только свои элементы (owner_id match) |
| **other** | Ничего |

Определение admin: проверка `team.json` role, первый в `ALLOWED_USER_IDS`, hardcoded admin IDs.

---

## 8 типов действий (approval types)

```python
VALID_TYPES = {
    "delete_client",              # Удаление клиента
    "delete_expense",             # Удаление расхода
    "delete_lesson",              # Удаление урока
    "archive_transcriptions",     # Архивация транскрипций (>6 мес)
    "archive_lessons",            # Архивация уроков (>90 дней)
    "merge_lessons",              # Объединение похожих уроков
    "cleanup_temp",               # Очистка временных файлов
    "db_vacuum",                  # Оптимизация БД
}
```

### Жизненный цикл запроса

```
pending -> approved   (действие выполняется автоматически)
pending -> rejected   (с опциональной причиной)
pending -> expired    (авто-проверка периодически)
pending -> modified   (детали обновлены, остаётся pending)
```

### Формат ID запроса

```
OPT-YYYY-MM-DD-xxxx
```

Пример: `OPT-2026-02-18-a3f1`

### Auto-Execute при подтверждении

| Тип | Действие |
|-----|----------|
| `delete_client` | `core.clients.remove_client(phone)` |
| `delete_lesson` | `services.lessons.delete_lesson(id)` |
| `archive_lessons` | `services.lessons.archive_by_ids(ids)` |
| `merge_lessons` | `services.lessons.merge_lessons(ids, master_text)` |
| `archive_transcriptions` | Отложено в scheduler loop |
| `db_vacuum` | Отложено в scheduler loop |

### Хранение

JSON файл: `data/pending_approvals.json`

```json
{"requests": [...]}
```

---

## Admin/Member/Other разрешения

### Определение ролей

```python
def can_approve(user_id, request, team_manager) -> bool:
    if is_admin(user_id, team_manager):
        return True  # admin может всё
    if request.get("owner_id") == user_id:
        return True  # owner может свои
    return False

def is_admin(user_id, team_manager) -> bool:
    # 1. Проверка team.json -> role == "admin"
    # 2. Первый в ALLOWED_USER_IDS
    # 3. Hardcoded admin IDs
```

### Текущая команда

| Участник | Role | Telegram ID |
|----------|------|-------------|
| Сухейль | admin | 6905404901 |
| Марсель | member | 5939002952 |
| Мухаммад-Амин | member | 1336041242 |
| Камила | member | null |

---

## .env Security

### Управление секретами

- Все секреты хранятся в `.env` файле (НЕ hardcoded)
- `.env` загружается через кастомный loader (без `python-dotenv`)
- systemd: `EnvironmentFile=/home/ubuntu/VoiceTranscriptionBot/.env`
- `.env` НЕ коммитится в git
- Google credentials JSON в `data/` (в `.gitignore`)

### Все секреты

| Секрет | Описание |
|--------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `GROQ_API_KEY` | Groq API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GOOGLE_VISION_API_KEY` | Google Cloud Vision key |
| `WHATSAPP_TOKEN` | WhatsApp Cloud API bearer token |
| `WHATSAPP_APP_SECRET` | HMAC verification key |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verification secret |
| `YANDEX_DISK_TOKEN` | Yandex Disk OAuth token |
| `GOOGLE_DRIVE_CREDENTIALS` | Path to Google service account JSON |

---

## 12 паттернов безопасности из кодовой базы

### 1. Криптографическая верификация подписей

HMAC-SHA256 для каждого входящего webhook. `hmac.compare_digest()` для timing-safe сравнения.

### 2. Deny-by-Default контроль доступа

Оба бота (Telegram + WhatsApp) используют явные whitelist. Пустой whitelist = отклонить всех. Несанкционированные сообщения молча отбрасываются.

### 3. Отключение API документации

```python
FastAPI(docs_url=None, redoc_url=None)
```

Предотвращает раскрытие внутренней структуры API.

### 4. Минимальная поверхность атаки (nginx)

- Только `/webhook` проксируется, всё остальное -> 404
- Rate limiting: 10 req/s, burst 10
- SSL termination на nginx, FastAPI на localhost
- Заголовок `X-Hub-Signature-256` явно проксируется

### 5. Маскировка телефонов в логах

```python
masked = f"***{from_phone[-4:]}" if len(from_phone) >= 4 else "***"
```

Полные телефоны никогда не появляются в лог-файлах.

### 6. Очистка временных файлов

- Каждый handler использует `try/finally` для удаления temp файлов
- Cloud upload cleanup каждый час
- Размер temp директории мониторится в `/health`

### 7. Непривилегированное выполнение

- systemd: `User=ubuntu` (не root)
- Автоматический перезапуск: `Restart=always`

### 8. Управление секретами

Все секреты в `.env`, не в коде. systemd `EnvironmentFile` для загрузки.

### 9. Валидация входных данных

- WhatsApp API лимиты на стороне клиента: button titles 20 chars, row titles 24, descriptions 72
- Document captions 1024 chars
- Макс 3 кнопки, 10 строк в секции
- Даты валидируются паттерн-матчингом
- Суммы расходов валидируются как float
- Настройки проверяются по допустимым множествам

### 10. Approval System для деструктивных операций

- Удаление клиента требует approval workflow
- Архивация транскрипций требует approval
- Owner-only проверки (role-based через TeamManager)
- Запросы истекают через 24-48 часов

### 11. Replay Protection (активна, v6.0.0)

- `verify_timestamp()` с 5-минутным окном и 30-секундным допуском
- **ExpiringDict nonce** для WhatsApp -- предотвращает повторную обработку одного и того же сообщения

### 12. Graceful Error Handling

- Все handlers обёрнуты в `_safe_handle()` -- сервер никогда не крашится
- Health endpoint использует try/except
- `mark_as_read` молча проваливается
- Status updates от Meta молча подтверждаются

---

## Структура запроса Approval

```json
{
    "id": "OPT-2026-02-18-a3f1",
    "type": "archive_transcriptions",
    "title": "Архивировать 50 старых транскрипций",
    "details": {"days": 180, "count": 50},
    "summary": "Перенос 50 транскрипций (>6 месяцев) в архив",
    "level": "B",
    "status": "pending",
    "requested_by": 6905404901,
    "owner_id": null,
    "created_at": "2026-02-18T21:00:00+04:00",
    "expires_at": "2026-02-20T21:00:00+04:00",
    "resolved_at": null,
    "resolved_by": null,
    "reject_reason": null,
    "modifications": null
}
```

---

## Ключевые методы ApprovalManager

| Метод | Описание |
|-------|----------|
| `request_approval()` | Создать запрос, вернуть ID |
| `approve()` | Одобрить + auto-execute |
| `reject()` | Отклонить с причиной |
| `modify()` | Изменить details pending запроса |
| `check_expired()` | Пометить истёкшие |
| `get_pending()` | Все pending |
| `get_history()` | Resolved запросы |
| `get_stats()` | total, pending, approved, rejected, expired |
| `purge_old()` | Удалить resolved >90 дней |
| `can_approve()` | Проверка авторизации |
| `is_admin()` | Проверка admin роли |

---

## Фичи безопасности v6.0.0

### 13. Log Sanitizer (маскировка секретов в логах)

**Файл:** `core/log_sanitizer.py`

Автоматическая маскировка API-ключей и секретов в лог-файлах. Перехватывает все лог-записи и заменяет паттерны токенов/ключей на `***MASKED***`.

Маскируемые паттерны:
- API-ключи Gemini, Groq, Google Vision, Google Maps, Google Translate
- Токены Telegram Bot, WhatsApp, Yandex Disk, Admin API
- WhatsApp App Secret, Exchange Rate API key
- Любые строки, совпадающие с паттернами `key=`, `token=`, `secret=`, `Bearer `

### 14. .env Validation (валидация переменных при старте)

**Файл:** `core/validators.py`

Проверка обязательных и опциональных переменных окружения при старте бота с подсказками:
- Обязательные: `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `ALLOWED_USER_IDS`
- Опциональные: проверка формата, предупреждения

### 15. HTTPS Enforcement (middleware для admin API)

Middleware в `admin/api.py` принудительно требует HTTPS для production (`ENFORCE_HTTPS=true`).
- Проверяет заголовок `X-Forwarded-Proto` или схему запроса
- В development (localhost) -- HTTPS не требуется
- Конфигурация: `ENFORCE_HTTPS=true` в `.env`

### 16. File Size Validation (лимиты размеров)

| Тип файла | Лимит |
|-----------|-------|
| Audio | 25 MB |
| Photo | 10 MB |
| Video | 100 MB |
| PDF | 20 MB |

### 17. Rate Limiting (API Semaphore)

`asyncio.Semaphore` для всех внешних API-вызовов:

| API | Semaphore Limit | Описание |
|-----|----------------|----------|
| Gemini API | 10 | Primary LLM (резюме, коррекция, категоризация, OCR) |
| Groq API | 5 | Fallback LLM + STT (whisper-large-v3-turbo) |
| Google Maps API | 5 | Маршруты, геокодирование, distance matrix |
| Google Vision API | 5 | OCR распознавание текста с фотографий |

Предотвращает превышение rate limits при массовой обработке. Все вызовы через `core/llm_client.py` автоматически проходят через semaphore.

### 18. Safe phone_to_user_id

SHA-256 int64 вместо int32 hash для генерации `user_id` из номера телефона. Устраняет коллизии при большом количестве номеров.
