---
name: integration-guardian
description: "Каждая интеграция должна быть надёжной и безопасной. Объединяет security audit, webhook reliability, dependency management и CI/CD в единый guardian workflow. Используй при добавлении нового платформенного бота, настройке webhook endpoint, обновлении зависимостей, настройке CI/CD pipeline или security review."
license: Apache-2.0
metadata:
---
# Integration Guardian

## Overview

Integration Guardian защищает каждую точку интеграции от уязвимостей и сбоев. Он объединяет четыре специализированных скилла в единый, последовательный workflow:

- **security-audit** — обнаружение уязвимостей, утечки секретов, OWASP Top 10
- **webhook-processor** — надёжные webhook endpoints (HMAC + async + idempotency + retry + DLQ)
- **dependency-updater** — аудит зависимостей по уровню угрозы (critical/high/medium)
- **cicd-pipeline** — генерация GitHub Actions: lint → test → security-scan → build → deploy

Главная идея: новый платформенный бот (Instagram, WhatsApp, Facebook, Viber) или любая новая точка интеграции не считается готовой, пока не прошла все четыре проверки Guardian.

---

## When to Use

Активируй этот скилл, если:

- Добавляешь новый платформенный бот в Omni Inbox (WhatsApp Connector, новый Meta-вебхук)
- Настраиваешь или изменяешь `/webhook/*` endpoint
- Обновляешь `requirements.txt` и хочешь убедиться, что нет CVE
- Делаешь security review перед деплоем на GCP
- Настраиваешь `.github/workflows/deploy.yml` для нового этапа pipeline
- Получил сигнал об уязвимости в зависимости (например, CVE в `aiohttp` или `httpx`)
- Webhook стал нестабильным: дубли, потери, Meta отключила доставку

---

## Modes

### Mode 1: `audit`

**Что делает:** OWASP Top 10 + CVE check + поиск hardcoded secrets + проверка HMAC verification на всех `/webhook/*` endpoints.

**Когда использовать:** перед любым деплоем, при code review, после добавления нового endpoint.

**Шаги:**

1. Сканировать зависимости на CVE:
   ```bash
   pip-audit --format=json
   # или safety check -r requirements.txt
   ```

2. Найти hardcoded secrets в коде:
   ```bash
   grep -rn --include="*.py" \
     -E "(password\s*=\s*['\"]|secret\s*=\s*['\"]|api_key\s*=\s*['\"]|token\s*=\s*['\"][^{])" \
     --exclude-dir={__pycache__,.git} .
   ```

3. Проверить, что все `/webhook/*` endpoints имеют HMAC верификацию:
   ```bash
   grep -rn "def.*webhook\|@app\.(post|get).*webhook" --include="*.py" .
   ```
   Для каждого найденного endpoint проверить наличие вызова `verify_hmac`, `verify_meta_signature` или аналога.

4. Проверить OWASP A03 — SQL Injection:
   ```bash
   grep -rn "execute(f\"\|execute(\"\s*SELECT\|execute(\"\s*INSERT" --include="*.py" .
   ```
   Искать конкатенацию пользовательского ввода в SQL. В VIP-DXB-CatalogBot допустимы только `$1/$2` параметры asyncpg.

5. Проверить OWASP A05 — Security Misconfiguration:
   - `DEBUG` mode не включён в production
   - `CORS` не `*` без ограничений
   - `.env` в `.gitignore`

**Пример для VIP-DXB-CatalogBot:**
```
Задача: "Security review перед деплоем Phase 22"

audit → проверяет:
- OWNER_IDS хранится в .env, не в коде
- /webhook/fb, /webhook/ig, /webhook/wa, /webhook/viber — у всех verify_meta_signature() / verify_viber_signature()
- requirements.txt: нет CVE в aiohttp, httpx, aiogram, vkbottle
- Нет f-строк в SQL запросах (asyncpg везде $1/$2)
```

---

### Mode 2: `webhook`

**Что делает:** генерирует production-ready webhook endpoint с полным набором защит.

**Обязательные компоненты:**
1. HMAC-SHA256 verification (до обработки, до записи в БД)
2. Немедленный 200 OK + async обработка через BackgroundTasks
3. Idempotency key в PostgreSQL (таблица `processed_webhook_events`)
4. Retry с exponential backoff (3s → 9s → 27s, max 5 попыток)
5. DLQ → PostgreSQL таблица `webhook_dlq`
6. Structured logging: `[platform] action: details`

**Когда использовать:** при добавлении нового `/webhook/*` endpoint в любой из ботов.

**Пример для VIP-DXB-CatalogBot — добавление WhatsApp Connector в Omni Inbox:**
```
Задача: "Добавить WhatsApp Connector в Omni Inbox"

webhook → генерирует:
1. whatsapp_bot/app.py: POST /webhook/whatsapp с verify_meta_signature(META_APP_SECRET)
2. Вызов omni_service.on_incoming_message() с idempotency по wa_message_id
3. INSERT INTO processed_webhook_events (message_id='wamid.xxx', platform='whatsapp')
4. retry_with_backoff() для вызовов к omni_inbox
5. DLQ при 5 неудачных попытках
6. Логи: [whatsapp] incoming: wamid.xxx from +971... | [whatsapp] processed: omni_conv_id=42
```

**Security checklist для webhook (встроенный):**
- [ ] HMAC верификация вызывается ДО любой бизнес-логики
- [ ] raw_body читается ОДИН раз и передаётся дальше
- [ ] `hmac.compare_digest()` — не обычное `==`
- [ ] Ошибки структуры payload → 200 OK (не 4xx/5xx) — Meta отключит webhook
- [ ] Нет синхронной тяжёлой обработки в теле endpoint (>1 сек → в BackgroundTasks)
- [ ] Idempotency: повторный message_id → skip + log, не raise

**Шаблон:** `assets/templates/webhook-handler.py`

---

### Mode 3: `deps`

**Что делает:** аудит зависимостей в `requirements.txt` с классификацией по severity и планом обновления.

**Шаги:**

1. Запустить pip-audit:
   ```bash
   pip-audit --format=json -o audit-results.json
   ```

2. Классифицировать результаты:
   - **Critical** — CVE CVSS >= 9.0. Блокирующий. Обновить немедленно.
   - **High** — CVE CVSS 7.0–8.9. Обновить в текущем спринте.
   - **Medium** — CVE CVSS 4.0–6.9. Запланировать в следующем спринте.
   - **Stale** — нет релизов 12+ месяцев. Рассмотреть замену.

3. Для critical/high — проверить breaking changes:
   ```bash
   # Для каждого пакета с critical CVE:
   pip index versions <package>
   # Сравнить changelog между текущей и исправленной версией
   ```

4. Сформировать план обновления:
   - Critical → немедленно, изолированный PR, запустить тесты
   - High → в течение 48 часов
   - Medium → плановое обновление
   - Stale → оценка замены

5. Critical CVE автоматически добавляются в CI как blocking gate (см. Mode 4: `ci`).

**Пример для VIP-DXB-CatalogBot:**
```
Задача: "Обновить зависимости"

deps → сканирует requirements.txt:
- aiogram 3.25+: проверить CVE, сравнить с последней 3.x
- vkbottle 4.7.0: проверить CVE
- aiohttp: частые CVE — приоритет проверки
- httpx: проверить
- asyncpg: проверить

Если найдено critical: → создать отдельный PR "fix: critical CVE in <package>"
Если medium: → добавить в следующий плановый update
```

---

### Mode 4: `ci`

**Что делает:** генерирует или обновляет `.github/workflows/deploy.yml` с полным security pipeline.

**Структура pipeline:**
```
lint (flake8/black)
    ↓
test (pytest + PostgreSQL service)
    ↓
security-scan (bandit + safety/pip-audit)
    ↓
build (docker build)
    ↓
deploy (SSH to GCP) ← только на main branch
```

**Правила:**
- lint и test — на каждый PR и push
- security-scan — блокирует merge при critical CVE
- build — собирает docker образ
- deploy — только при push в `main`, требует `SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`
- Параллельность: lint || test (не зависят друг от друга)
- Concurrency: отменять предыдущий run для той же ветки при новом push

**Шаблон:** `assets/templates/github-actions-ci.yml`

**Пример для VIP-DXB-CatalogBot:**
```
Задача: "Добавить security gate в CI"

ci → обновляет .github/workflows/deploy.yml:
- Добавить job security-scan между test и build
- bandit -r bot/ vk_bot/ instagram_bot/ whatsapp_bot/ facebook_bot/ viber_bot/ core/ data/
- safety check -r requirements.txt --full-report
- Если safety находит critical: step fails → deploy не запускается
```

---

### Mode 5: `hardening`

**Что делает:** полный Guardian pipeline для нового платформенного бота или endpoint.

**Последовательность:** `audit` → `webhook` → `deps` → `ci`

**Когда использовать:**
- Добавление нового платформенного бота в Omni Inbox (это самый важный триггер)
- Полный security review перед крупным релизом
- После инцидента (webhook потерял события, была утечка данных)

**Пример для VIP-DXB-CatalogBot — добавление WhatsApp Connector:**
```
Задача: "Добавить WhatsApp Connector в Omni Inbox"

hardening →

Шаг 1 (audit):
- Проверить META_APP_SECRET в .env (не в коде)
- Убедиться, что /webhook/whatsapp имеет verify_meta_signature()
- Проверить омни-сервис: нет SQL-конкатенации

Шаг 2 (webhook):
- Создать endpoint: verify_meta_signature → 200 OK → BackgroundTask
- Idempotency: INSERT INTO processed_webhook_events (wa_message_id, 'whatsapp')
- omni_service.on_incoming_message(platform='whatsapp', ...) с retry 3x backoff
- DLQ: webhook_dlq при 5 неудачах
- Логи: [whatsapp-omni] incoming: from=+971553096985 | processed: conv_id=42

Шаг 3 (deps):
- httpx CVE check (используется для notify менеджера)
- aiohttp CVE check (используется в webhook)
- Нет critical → OK

Шаг 4 (ci):
- .github/workflows/deploy.yml: добавить security-scan job
- Проверить, что WhatsApp Connector тесты включены в pytest run
```

---

## Synergy Rules

Правила автоматических связей между режимами:

| Триггер | Автоматическое действие |
|---------|------------------------|
| `audit` находит endpoint без HMAC | Переключиться в `webhook` для этого endpoint |
| `webhook` финализирует новый endpoint | Выполнить security checklist из `audit` |
| `deps` находит critical CVE | Добавить его в CI как blocking gate (`ci`) |
| `hardening` запускается | Выполнить все 4 режима последовательно |
| Новый платформенный бот | Всегда использовать `hardening` |

**Связь audit + webhook:**
Если `audit` обнаружил endpoint `/webhook/whatsapp` без HMAC — не просто пометить как предупреждение. Немедленно сгенерировать исправленный вариант через `webhook` mode.

**Связь deps + ci:**
Если `deps` нашёл критическую CVE в `aiohttp` — добавить строку в CI workflow:
```yaml
- name: Check critical CVE
  run: safety check -r requirements.txt --full-report
  # aiohttp==X.Y.Z known CVE-XXXX-XXXXX — must upgrade to X.Y+1
```

**Связь hardening + новый бот:**
Каждый новый платформенный коннектор в Omni Inbox должен пройти `hardening` перед первым деплоем. Это правило заменяет ручной code review для типовых ошибок безопасности.

---

## Security Checklist (встроенный для webhook endpoints)

Используй перед каждым `git push` с изменениями в `*/app.py`, `*/webhook_verify.py`, или `bot/handlers/`:

**Аутентификация и подписи:**
- [ ] HMAC верификация есть на всех POST `/webhook/*` endpoints
- [ ] Используется `hmac.compare_digest()`, не `==`
- [ ] `raw_body = await request.body()` вызывается ровно один раз
- [ ] Секретный ключ берётся из `os.getenv()`, не из кода

**Обработка payload:**
- [ ] Ошибки парсинга JSON → `return {"status": "ok"}` (не raise HTTPException)
- [ ] Тяжёлая обработка (>1 сек) идёт в BackgroundTasks
- [ ] Нет synchronous DB calls в теле endpoint

**Idempotency:**
- [ ] Повторный message_id → skip (не ошибка)
- [ ] `processed_webhook_events` таблица присутствует в миграциях

**Retry / DLQ:**
- [ ] Временные сбои (ConnectionError, TimeoutError) → retry с backoff
- [ ] Неисправимые ошибки → `webhook_dlq` таблица

**Логирование:**
- [ ] Каждый входящий webhook логируется: платформа, sender, message_id
- [ ] Каждый обработанный event логируется: результат или ошибка
- [ ] Нет PII в логах (номера телефонов, паспортные данные)

---

## Handler-Level Input Validation

Валидация пользовательского ввода на уровне handler -- до того, как данные попадут в DB или AI-сервис. Закрывает пробелы между webhook-уровневой защитой (HMAC) и бизнес-логикой.

### 1. Валидация поискового ввода

```python
# Validate before AI/DB query
MAX_SEARCH_LENGTH = 500
BLOCKED_PATTERNS = [";--", "/*", "*/", "xp_", "DROP ", "DELETE ", "UPDATE "]

def validate_search_input(text: str) -> str | None:
    """Returns sanitized text or None if invalid."""
    if not text or len(text) > MAX_SEARCH_LENGTH:
        return None
    if any(p.lower() in text.lower() for p in BLOCKED_PATTERNS):
        return None
    return text.strip()
```

### 2. Валидация callback_data

```python
# Validate callback_data format before processing
import re

VALID_CALLBACK_PATTERNS = {
    "book": re.compile(r"^book:\d{1,5}$"),
    "cat": re.compile(r"^cat:[A-Z]{2,4}:\d{1,5}$"),
    "page": re.compile(r"^page:[A-Z]{2,4}:\d{1,5}:\d{1,3}$"),
}

def validate_callback(data: str) -> bool:
    prefix = data.split(":")[0]
    pattern = VALID_CALLBACK_PATTERNS.get(prefix)
    return pattern is not None and pattern.match(data) is not None
```

### 3. Защита от AI prompt injection

```python
# Sanitize user input before including in AI prompts
def sanitize_for_ai(user_text: str) -> str:
    """Remove potential prompt injection patterns."""
    # Remove instruction-like prefixes
    dangerous = ["ignore previous", "system:", "assistant:", "you are now"]
    text = user_text
    for d in dangerous:
        text = text.replace(d, "")
    return text[:1000]  # Hard length cap
```

### 4. AI API key security checklist

Дополнение к общему Security Checklist для AI-сервисов:

- [ ] `GOOGLE_AI_API_KEY` в `.env` only, не в коде
- [ ] `OPENAI_API_KEY` в `.env` only, не в коде
- [ ] API keys имеют usage quotas в dashboard провайдера
- [ ] API keys scoped до минимальных необходимых permissions
- [ ] Fallback не раскрывает API errors пользователю (generic "try again" message)
- [ ] Token usage логируется per request для cost monitoring
- [ ] User input sanitized через `sanitize_for_ai()` перед включением в prompt
- [ ] AI response length capped -- не отправлять пользователю ответ > 4096 символов (Telegram limit)

---

## Quick Reference

| Режим | Триггер | Время | Результат |
|-------|---------|-------|-----------|
| `audit` | Перед деплоем, code review | 15-30 мин | Отчёт с критикой по severity |
| `webhook` | Новый /webhook/* endpoint | 30-60 мин | Production-ready endpoint файл |
| `deps` | Обновление requirements.txt | 10-20 мин | CVE отчёт + план обновления |
| `ci` | Изменение pipeline | 20-40 мин | Обновлённый deploy.yml |
| `hardening` | Новый платформенный бот | 2-3 часа | Полный цикл audit+webhook+deps+ci |

---

## Common Mistakes — Частые ошибки интеграций

### 1. HMAC верификация после обработки (критично)

**Неправильно:**
```python
@app.post("/webhook/whatsapp")
async def handler(request: Request):
    payload = await request.json()  # СНАЧАЛА парсим
    await process_event(payload)    # ПОТОМ обрабатываем
    # HMAC забыли!
```

**Правильно:**
```python
@app.post("/webhook/whatsapp")
async def handler(request: Request, bg: BackgroundTasks):
    raw_body = await request.body()
    if not verify_meta_signature(raw_body, request.headers.get("X-Hub-Signature-256", "")):
        raise HTTPException(status_code=403)
    bg.add_task(process_event, raw_body)
    return {"status": "ok"}
```

### 2. Синхронная блокирующая обработка

**Неправильно:** Вызывать `await db._pool.execute(...)` или `await send_telegram_notification(...)` прямо в теле endpoint. Если это займёт 10+ секунд — Meta пометит webhook как dead.

**Правильно:** BackgroundTasks. Endpoint отвечает 200 за <100ms, обработка продолжается в фоне.

### 3. Хранить META_APP_SECRET в коде

**Неправильно:**
```python
META_APP_SECRET = "abc123secretkey"  # В коде!
```

**Правильно:** только через `.env` → `os.getenv("META_APP_SECRET")`. Проверять `git log --all --full-history -- .env`.

### 4. Нет idempotency → дублирующиеся бронирования

Meta и Viber ретраят доставку при медленном ответе. Без idempotency одно сообщение клиента создаёт 2-3 бронирования. В VIP-DXB-CatalogBot: `processed_webhook_events` таблица с `ON CONFLICT DO NOTHING`.

### 5. Возвращать 5xx на плохой payload

**Неправильно:** `raise HTTPException(500)` при ошибке парсинга.
**Правильно:** `return {"status": "ok"}` + лог ошибки. Meta отключает webhook при нескольких 5xx.

### 6. Timing attack в сравнении HMAC

**Неправильно:** `expected == received` — атакующий может угадать ключ побайтово.
**Правильно:** `hmac.compare_digest(expected, received)` — constant-time сравнение.

### 7. Читать request.body() дважды

**Неправильно:**
```python
signature = verify_signature(await request.body())  # Первое чтение
payload = await request.json()                        # Второй вызов → empty bytes!
```

**Правильно:**
```python
raw_body = await request.body()  # Один раз
verify_signature(raw_body)
payload = json.loads(raw_body)
```

### 8. Critical CVE в production без блокировки CI

Если `safety check` находит critical CVE — это должно ломать CI pipeline, не просто выдавать предупреждение. В `.github/workflows/deploy.yml` job `security-scan` должен предшествовать `build` и `deploy`.

### 9. Новый платформенный бот без hardening

Добавить бота в `router.py` / `run_both.py` недостаточно. Каждый новый коннектор (WA, FB, IG, Viber) должен пройти `hardening` mode Guardian: audit всех endpoints, webhook patterns, deps check, CI update.

### 10. Viber set_webhook не вызван после рестарта

Viber требует `set_webhook` при КАЖДОМ старте приложения. Без этого события перестанут доставляться. В VIP-DXB-CatalogBot: `@app.on_event("startup")` в `viber_bot/app.py`.

---

## Sources

- [Meta Webhooks Developer Docs](https://developers.facebook.com/docs/graph-api/webhooks/)
- [Telegram Bot API setWebhook](https://core.telegram.org/bots/api#setwebhook)
- [Viber REST API Callbacks](https://developers.viber.com/docs/api/rest-bot-api/#callbacks)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI BackgroundTasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- security-audit skill (Apache-2.0): TerminalSkills/skills
- webhook-processor skill (VIP-DXB-CatalogBot)
- dependency-updater skill (Apache-2.0): TerminalSkills/skills
- cicd-pipeline skill (Apache-2.0): TerminalSkills/skills
