# Runbook Templates — VIP-DXB-CatalogBot

Шаблоны для типичных production-инцидентов на GCP VM `tourist-bot` (zone: `europe-west3-b`).
Сервер: `/opt/catalog-bot`. Deploy: `docker compose --env-file .env.prod -f deploy/docker-compose.prod.yml`.

---

## RB-01: Telegram/VK бот не отвечает

### Симптомы
- Клиенты сообщают что бот не реагирует на сообщения
- Нет новых бронирований в БД
- OWNER_IDS не получают уведомления

### Диагностика

```bash
# 1. Проверить контейнер
gcloud compute ssh tourist-bot --zone=europe-west3-b
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps

# 2. Посмотреть последние логи
docker logs catalog-bot-telegram --tail=100
docker logs catalog-bot-vk --tail=100

# 3. Проверить что процесс живой
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml top

# 4. Проверить DB
docker exec catalog-bot-postgres psql -U postgres -c "SELECT 1 AS db_ok;"
```

### Устранение

**Контейнер упал — перезапустить:**
```bash
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart telegram vk
docker logs catalog-bot-telegram --tail=50 -f
```

**OOM (Out of Memory) — проверить и увеличить:**
```bash
# Проверить память
free -h
docker stats --no-stream

# Рестарт с лимитами если нужно
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml down telegram
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d telegram
```

**Telegram Bot API conflict (polling от двух инстанций):**
```bash
# Ищем 409 Conflict в логах
docker logs catalog-bot-telegram --tail=200 | grep "409"
# Остановить все, подождать 30 секунд, запустить одну инстанцию
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml down telegram
sleep 30
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d telegram
```

**VK token истёк:**
```bash
docker logs catalog-bot-vk --tail=100 | grep -i "token\|403\|expired"
# Обновить VK_BOT_TOKEN в .env.prod и перезапустить
```

### Профилактика
- Добавить polling watchdog (см. SKILL.md → Mode: health)
- Настроить restart: always в docker-compose.prod.yml
- Мониторить `/health` через внешний uptime-монитор (UptimeRobot free tier)

---

## RB-02: Webhook перестал получать события (IG/WA/FB/Viber)

### Симптомы
- Нет входящих сообщений в Instagram / WhatsApp / Facebook / Viber
- Health endpoint отвечает 200, но события не приходят
- Meta / Viber dashboard показывает ошибки доставки

### Диагностика

```bash
# 1. Проверить что контейнер слушает нужный порт
gcloud compute ssh tourist-bot --zone=europe-west3-b
ss -tlnp | grep -E '808[0-4]'

# 2. Проверить health endpoints
curl -s localhost:8081/health  # Instagram
curl -s localhost:8082/health  # WhatsApp
curl -s localhost:8083/health  # Facebook
curl -s localhost:8084/health  # Viber

# 3. Проверить что webhook URL валиден (не истёк ngrok и т.д.)
# Для production — должен быть статический IP/домен

# 4. Проверить HMAC-верификацию в логах
docker logs catalog-bot-instagram --tail=200 | grep -i "hmac\|signature\|403"
```

**Для Instagram/WhatsApp/Facebook:**
```bash
# Проверить webhook через Meta API (нужен FB_PAGE_ACCESS_TOKEN)
curl -G "https://graph.facebook.com/v19.0/me/subscribed_apps" \
  --data-urlencode "access_token=$FB_PAGE_ACCESS_TOKEN"
```

**Для Viber:**
```bash
# Viber сам устанавливает webhook при старте — проверить логи startup
docker logs catalog-bot-viber --tail=50 | grep "set_webhook"
# Если не установился — рестарт
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart viber
```

### Устранение

**Порт не слушается — контейнер упал:**
```bash
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d instagram whatsapp facebook viber
```

**SSL/TLS проблема (Meta требует HTTPS):**
```bash
# Проверить nginx/caddy конфиг
cat /etc/nginx/sites-enabled/catalog-bot
nginx -t
systemctl reload nginx
```

**Webhook URL изменился (например новый IP после перезапуска VM):**
```bash
# Получить внешний IP VM
curl ifconfig.me
# Обновить webhook URL в Meta Developer Portal вручную
# Для Viber — обновить VIBER_WEBHOOK_URL в .env.prod и рестартовать
```

### Профилактика
- Использовать статический IP для GCP VM (Reserved static address)
- Webhook URL должен не зависеть от ngrok
- Добавить внешний мониторинг каждого порта

---

## RB-03: DB Pool Exhausted (asyncpg connection pool)

### Симптомы
- Ошибки в логах: `asyncpg.exceptions.TooManyConnectionsError`
- Новые бронирования не сохраняются
- Все платформы начинают тормозить одновременно

### Диагностика

```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b

# 1. Текущие соединения
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT count(*), state, wait_event_type, wait_event
   FROM pg_stat_activity
   WHERE datname = 'catalog'
   GROUP BY state, wait_event_type, wait_event
   ORDER BY count DESC;"

# 2. Долгие запросы (>5 секунд)
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pid, now() - query_start AS age, query, state
   FROM pg_stat_activity
   WHERE datname = 'catalog'
     AND (now() - query_start) > interval '5 seconds'
   ORDER BY age DESC;"

# 3. Максимально допустимые соединения
docker exec catalog-bot-postgres psql -U postgres -c \
  "SHOW max_connections;"

# 4. Текущий pool в коде (default 10-20)
grep -r "min_size\|max_size\|pool" /opt/catalog-bot/data/database.py | head -20
```

### Устранение

**Убить зависшие idle соединения:**
```bash
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'catalog'
     AND state = 'idle'
     AND (now() - state_change) > interval '10 minutes';"
```

**Убить долгие запросы:**
```bash
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'catalog'
     AND (now() - query_start) > interval '30 seconds'
     AND state != 'idle';"
```

**Временно перезапустить все боты (освободит pool):**
```bash
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart
```

**Постоянное решение — увеличить pool или max_connections:**
```python
# В data/database.py — увеличить max_size
self._pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=5,
    max_size=30,  # было 20
)
```

### Профилактика
- Логировать pool stats каждые 60 секунд (см. SKILL.md → DB Pool Monitoring)
- Алерт при utilization > 80%
- Проверить что все DB-методы используют `async with pool.acquire()` правильно

---

## RB-04: AI Search Quota Exceeded

### Симптомы
- AI поиск возвращает ошибку или fallback результаты
- Логи содержат `429 Too Many Requests` или `quota exceeded`
- Клиенты видят "обычные" результаты поиска вместо AI-ответов

### Диагностика

```bash
# 1. Проверить логи AI adapter
docker logs catalog-bot-telegram --tail=200 | grep -i "quota\|429\|gemini\|openai"

# 2. Посчитать AI запросы за последний час
docker logs catalog-bot-telegram --since=1h | grep '"event": "request_completed"' | wc -l

# 3. Посмотреть стоимость запросов
docker logs catalog-bot-telegram --since=24h | jq 'select(.event == "request_completed") | .cost_usd' | awk '{sum+=$1} END {print "Total USD:", sum}'
```

### Устранение

**Gemini quota исчерпана — переключиться на OpenAI:**
```bash
# В .env.prod временно переключить fallback
# AI_SEARCH_MODEL=gpt-4o-mini  (OpenAI)
# Перезапустить
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart telegram vk
```

**Оба провайдера недоступны — отключить AI поиск:**
```python
# core/services/ai_adapter.py — временно вернуть пустой результат
# Или в bot/handlers/search.py пропустить ai_assistant вызов
```

**Quota сброситься сама (обычно в начале следующего дня/месяца):**
- Google AI: лимиты по минутам (RPM) и по дням (daily tokens)
- OpenAI: лимиты по минутам и по месяцам

### Профилактика
- Бюджетные алерты в Google AI Console и OpenAI Dashboard
- `alert_if_threshold` для cost_per_hour > $0.50
- Добавить circuit breaker в ai_adapter.py (отключать AI после N подряд 429)

---

## RB-05: GCP VM Недоступна

### Симптомы
- Все боты перестали работать одновременно
- SSH не устанавливается
- GitHub Actions деплой завис или упал

### Диагностика

```bash
# 1. Проверить статус VM через gcloud (с локальной машины)
gcloud compute instances describe tourist-bot --zone=europe-west3-b --format="get(status)"

# 2. Посмотреть serial port output (логи BIOS/kernel)
gcloud compute instances get-serial-port-output tourist-bot --zone=europe-west3-b --tail=50

# 3. Проверить billing account (не истёк ли trial/кредиты)
gcloud billing accounts list

# 4. Проверить GitHub Actions
gh run list --repo Sukheil-Ganeev/VIP-DXB-CatalogBot --limit=5
```

### Устранение

**VM остановлена — запустить:**
```bash
gcloud compute instances start tourist-bot --zone=europe-west3-b
# Подождать 60-90 секунд
gcloud compute ssh tourist-bot --zone=europe-west3-b
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d
```

**VM завислась — hard reset:**
```bash
gcloud compute instances reset tourist-bot --zone=europe-west3-b
# После reset контейнеры с restart:always запустятся сами
```

**OOM Killer убил процессы — проверить память:**
```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b
dmesg | grep -i "oom\|killed"
free -h
# Рестартовать контейнеры
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d
```

**Billing проблема:**
- Зайти в Google Cloud Console → Billing
- Проверить баланс и активировать если нужно
- VM сама запустится после решения billing-проблемы

**Диск заполнен:**
```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b
df -h
# Очистить старые Docker образы
docker system prune -f
docker volume prune -f
```

### Профилактика
- Включить VM uptime monitoring в Google Cloud Monitoring (бесплатно)
- Настроить billing alerts при 80% использования бюджета
- Добавить внешний ping-мониторинг VM IP (UptimeRobot)
- Регулярно чистить Docker образы: `docker system prune -f` в cron

---

## Шаблон нового runbook

Скопируй этот шаблон для нового инцидента:

```markdown
## RB-XX: [Название инцидента]

### Симптомы
- Что видит пользователь
- Что видит владелец
- Что показывают логи

### Диагностика
\```bash
# Команды для диагностики
\```

### Устранение
**Причина А:**
\```bash
# Команды для устранения А
\```

**Причина Б:**
\```bash
# Команды для устранения Б
\```

### Профилактика
- Что добавить чтобы не повторилось
```
