# Pre-Deploy Security Checklist

Используй перед каждым `git push origin main` в VIP-DXB-CatalogBot.
Особенно важно при: добавлении нового бота, изменении webhook endpoint'а, обновлении зависимостей.

---

## Блок 1: Аутентификация и подписи

- [ ] **HMAC на всех webhook endpoints**
  Каждый `@app.post("/webhook/*")` вызывает `verify_meta_signature()` / `verify_viber_signature()` / аналог до начала обработки.
  Проверить: `grep -rn "def.*webhook\|@app.post.*webhook" --include="*.py" .`

- [ ] **Timing-safe сравнение**
  Используется `hmac.compare_digest()`, не обычное `==`. Обычное `==` — уязвимость к timing attack.

- [ ] **Секрет из environment**
  `os.getenv("META_APP_SECRET")`, `os.getenv("VIBER_AUTH_TOKEN")` — не хардкодить.
  Проверить: `grep -rn 'META_APP_SECRET\s*=\s*["'"'"']' --include="*.py" .`

- [ ] **Правильный ключ для Viber**
  Viber использует `VIBER_AUTH_TOKEN`, NOT `META_APP_SECRET`. Разные ключи для разных платформ.

- [ ] **raw_body читается один раз**
  `raw_body = await request.body()` — в одной переменной, передаётся в `verify_hmac()` и `json.loads()`.
  Если читать дважды — второй вызов вернёт пустые bytes.

---

## Блок 2: Secrets — нет в коде

- [ ] **Нет токенов в .py файлах**
  ```bash
  grep -rn --include="*.py" \
    -E "(CATALOG_BOT_TOKEN|META_APP_SECRET|VK_BOT_TOKEN|VIBER_AUTH_TOKEN)\s*=\s*['\"]" .
  ```
  Результат должен быть пустым.

- [ ] **DATABASE_URL не в коде**
  Только через `os.getenv("DATABASE_URL")` или `core/config.py` с `os.getenv`. Не хардкодить PostgreSQL DSN.

- [ ] **.env в .gitignore**
  ```bash
  git check-ignore .env
  ```
  Должно вернуть `.env`. Если нет — добавить немедленно.

- [ ] **Нет .env в git history**
  ```bash
  git log --all --full-history -- .env
  ```
  Если есть коммиты — удалить с помощью BFG Repo Cleaner или `git filter-branch`.

- [ ] **SSH ключи не в коде**
  ```bash
  grep -rn "BEGIN.*PRIVATE KEY\|BEGIN RSA PRIVATE" --include="*.py" --include="*.yml" .
  ```

- [ ] **Нет паролей в docker-compose файлах**
  В `deploy/docker-compose.prod.yml` переменные берутся из `--env-file .env.prod`, не хардкодятся.

---

## Блок 3: Webhook надёжность

- [ ] **Немедленный 200 OK + BackgroundTasks**
  Тяжёлая обработка (DB write, внешние API) — в `background_tasks.add_task()`, не синхронно.
  Meta ждёт 200 максимум 20 секунд. Viber — 5 секунд.

- [ ] **Нет HTTPException(5xx) на плохой payload**
  Ошибки парсинга JSON → `return {"status": "ok"}` + лог. НЕ `raise HTTPException(500)`.
  Meta отключает webhook при нескольких 5xx подряд.

- [ ] **Idempotency реализована**
  Повторный message_id → skip + лог, не двойная обработка.
  Таблица `processed_webhook_events` присутствует в миграциях.

- [ ] **DLQ таблица создана**
  Таблица `webhook_dlq` присутствует в миграциях.
  При 5 неудачных попытках retry → запись в `webhook_dlq`.

- [ ] **Viber: set_webhook в startup**
  В `viber_bot/app.py`: `@app.on_event("startup")` вызывает `set_viber_webhook()`.
  Без этого Viber перестаёт доставлять события после перезапуска.

---

## Блок 4: База данных

- [ ] **Только asyncpg параметры ($1/$2)**
  Нет SQL-конкатенации строк: `f"SELECT ... WHERE id={user_input}"` — SQL injection!
  Только: `await pool.execute("SELECT ... WHERE id=$1", user_id)`

- [ ] **Нет прямого db._db.execute()**
  Только `CatalogDB` методы или `db._pool` asyncpg calls.
  `db._db` — legacy SQLite, не использовать в новом коде.

- [ ] **html.escape() на пользовательский ввод в Telegram**
  Перед вставкой в HTML-сообщение: `html.escape(user_text)`.
  VK, IG, WA, FB, Viber — plain text, html.escape не нужен.

- [ ] **PostgreSQL миграции идемпотентны**
  `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`.
  Повторный запуск `CatalogDB.init()` не ломает существующую схему.

---

## Блок 5: Зависимости

- [ ] **Нет critical CVE**
  ```bash
  pip-audit -r requirements.txt
  ```
  Нет пакетов с CRITICAL или HIGH severity.

- [ ] **requirements.txt актуален**
  Если добавляли новые пакеты через `pip install` — зафиксировать в requirements.txt:
  ```bash
  pip freeze | grep <package_name> >> requirements.txt
  ```

- [ ] **Нет stale пакетов** (необязательно, но рекомендуется)
  Пакеты без релизов 12+ месяцев стоит заменить на поддерживаемые альтернативы.

---

## Блок 6: CORS и API endpoints

- [ ] **CORS не `*` на webhook endpoints**
  Webhook endpoints принимают запросы только от провайдеров (Meta, Viber).
  В FastAPI: `allow_origins` — конкретные домены, не `["*"]`.

- [ ] **Rate limiting на публичных endpoints**
  `/webhook/*` и другие публичные endpoints должны иметь rate limiting (через middleware или Nginx).

- [ ] **HTTPS на production**
  Все webhook URLs используют `https://`. Meta не принимает `http://`.
  GCP VM: Nginx с SSL-сертификатом (Let's Encrypt или CloudFlare).

---

## Блок 7: Логирование (без PII)

- [ ] **Нет номеров телефонов в логах**
  Клиентские данные (номер телефона, email, паспорт) не попадают в `logger.info/debug`.
  Логировать только: `user_id`, `message_id`, `platform`, статус операции.

- [ ] **Нет личных данных в DLQ**
  В `webhook_dlq.payload` не должны храниться паспортные данные или полные номера карт.
  Только `summary` или минимальный контекст для отладки.

- [ ] **Лог входящего события**
  `[platform] incoming: mid=XXX from=user_id_only`

- [ ] **Лог результата обработки**
  `[platform] processed: conv_id=42` или `[platform] error: ...`

---

## Блок 8: Backup и восстановление

- [ ] **PostgreSQL backup настроен**
  На GCP VM: автоматические snapshots диска или pg_dump cron job.
  Минимум: ежедневный backup с retention 7 дней.

- [ ] **Процедура восстановления проверена**
  Был хоть один test restore из backup? Если нет — backup ненадёжен.

- [ ] **.env.prod на VM защищён**
  `/opt/catalog-bot/.env.prod` — права `600` (только владелец может читать):
  ```bash
  chmod 600 /opt/catalog-bot/.env.prod
  ```

---

## Финальная проверка перед деплоем

```bash
# 1. Статус git
git status --short

# 2. CVE check
pip-audit -r requirements.txt

# 3. Поиск секретов в изменённых файлах
git diff --name-only HEAD | xargs grep -l "secret\|token\|password" 2>/dev/null

# 4. Запуск тестов локально (если есть PostgreSQL)
pytest tests/ -q -p no:cacheprovider --tb=short -x

# 5. Убедиться что деплой-workflow существует
ls .github/workflows/deploy.yml
```

**Если все пункты выполнены → `git push origin main`**

---

## Когда этот чеклист особенно важен

| Сценарий | Критичные пункты |
|----------|-----------------|
| Новый платформенный бот | Блоки 1, 2, 3 полностью |
| Обновление зависимостей | Блок 5 полностью |
| Изменение webhook endpoint | Блоки 1, 3 полностью |
| Изменение database.py | Блок 4 полностью |
| Первый деплой после долгого перерыва | Все блоки |
