# Runbook Advanced — VIP-DXB-CatalogBot

Расширенные runbooks для production-инцидентов на GCP VM `tourist-bot` (zone: `europe-west3-b`).
Сервер: `/opt/catalog-bot`. Docker Compose: `deploy/docker-compose.prod.yml`.

---

## RB-01: Bot не отвечает (Telegram / VK)

### Симптомы
- Клиенты сообщают что бот не реагирует на сообщения в Telegram или VK
- Нет новых бронирований в БД
- OWNER_IDS не получают уведомления о новых заявках

### Диагностика

```bash
# Шаг 1: войти на VM
gcloud compute ssh tourist-bot --zone=europe-west3-b

# Шаг 2: проверить статус контейнеров
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps

# Шаг 3: посмотреть последние логи
docker logs catalog-bot-telegram --tail=100
docker logs catalog-bot-vk --tail=100

# Шаг 4: проверить что процесс живой
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml top

# Шаг 5: проверить DB доступна
docker exec catalog-bot-postgres psql -U postgres -c "SELECT 1 AS db_ok;"
```

### Устранение

**А. Контейнер упал (статус Exited) — перезапустить:**
```bash
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart telegram vk
# Следить за логами 60 секунд
docker logs catalog-bot-telegram --tail=50 -f
```

**Б. OOM (Out of Memory) — проверить память:**
```bash
free -h
docker stats --no-stream
# Перезапуск с освобождением памяти
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml down telegram vk
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d telegram vk
```

**В. Telegram Bot API conflict 409 (два polling-процесса):**
```bash
# Найти 409 в логах
docker logs catalog-bot-telegram --tail=200 | grep "409"
# Остановить, подождать, запустить одну инстанцию
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml down telegram
sleep 30
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d telegram
```

**Г. VK token истёк:**
```bash
docker logs catalog-bot-vk --tail=100 | grep -i "token\|403\|expired"
# Обновить VK_BOT_TOKEN в .env.prod
nano /opt/catalog-bot/.env.prod
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart vk
```

### Профилактика
- `restart: always` в docker-compose.prod.yml для telegram и vk контейнеров
- Polling watchdog (см. monitoring-observability SKILL.md → Mode: health)
- UptimeRobot мониторинг через health endpoint или внешний ping

---

## RB-02: Webhook не получает события (Instagram / WhatsApp / Facebook / Viber)

### Симптомы
- Нет входящих сообщений через IG/WA/FB/Viber
- Health endpoint отвечает 200, но события не приходят
- Meta или Viber dashboard показывает ошибки доставки

### Диагностика

```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b

# Шаг 1: проверить что порты слушаются
ss -tlnp | grep -E '808[0-4]'

# Шаг 2: health checks
curl -s localhost:8081/health  # Instagram
curl -s localhost:8082/health  # WhatsApp
curl -s localhost:8083/health  # Facebook
curl -s localhost:8084/health  # Viber

# Шаг 3: проверить HMAC-ошибки (Meta отключает webhook при 403)
docker logs catalog-bot-instagram --tail=200 | grep -i "hmac\|signature\|403\|forbidden"
docker logs catalog-bot-whatsapp --tail=200 | grep -i "hmac\|signature\|403"

# Шаг 4: проверить webhook подписку Meta (IG/WA/FB)
curl -G "https://graph.facebook.com/v19.0/me/subscribed_apps" \
  --data-urlencode "access_token=$FB_PAGE_ACCESS_TOKEN"

# Шаг 5: Viber — проверить set_webhook при старте
docker logs catalog-bot-viber --tail=50 | grep "set_webhook"
```

### Устранение

**А. Контейнер упал — поднять:**
```bash
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml up -d instagram whatsapp facebook viber
```

**Б. SSL-проблема (Meta требует HTTPS на webhook URL):**
```bash
# Проверить nginx/caddy
nginx -t
systemctl status nginx
systemctl reload nginx
# Проверить сертификат
openssl s_client -connect your-domain.com:443 -servername your-domain.com < /dev/null 2>&1 | grep "Verify"
```

**В. IP VM изменился (после перезапуска VM без статического IP):**
```bash
# Получить новый внешний IP
curl ifconfig.me
# Обновить webhook URL:
# - Meta: в Meta Developer Portal → Webhooks → Edit
# - Viber: обновить VIBER_WEBHOOK_URL в .env.prod и рестартовать viber
```

**Г. Viber webhook не установлен (требуется после каждого рестарта):**
```bash
# Viber set_webhook вызывается автоматически при @app.on_event("startup")
# Если не вызвался — рестартовать контейнер
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart viber
docker logs catalog-bot-viber --tail=30 | grep "set_webhook"
```

**Д. HMAC-верификация падает (META_APP_SECRET изменился):**
```bash
# Проверить что META_APP_SECRET актуальный
grep META_APP_SECRET /opt/catalog-bot/.env.prod
# Сравнить с Meta Developer Portal → App Settings → Basic → App Secret
```

### Профилактика
- Зарезервировать статический IP в GCP Console → VPC network → External IP addresses
- Webhook URL не должен зависеть от ngrok в production
- UptimeRobot мониторинг каждого порта (8080-8084)

---

## RB-03: DB Pool Exhausted

### Симптомы
- Ошибки в логах: `asyncpg.exceptions.TooManyConnectionsError`
- Новые бронирования не сохраняются, ошибки у всех платформ одновременно
- Health endpoints возвращают 503 (DB check fails)

### Диагностика

```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b

# Шаг 1: текущие соединения по состоянию
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT count(*), state, wait_event_type
   FROM pg_stat_activity
   WHERE datname = 'catalog'
   GROUP BY state, wait_event_type
   ORDER BY count DESC;"

# Шаг 2: долгие запросы (>5 секунд)
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pid, now() - query_start AS age, left(query, 120) AS query, state
   FROM pg_stat_activity
   WHERE datname = 'catalog'
     AND (now() - query_start) > interval '5 seconds'
   ORDER BY age DESC;"

# Шаг 3: лимит соединений PostgreSQL
docker exec catalog-bot-postgres psql -U postgres -c "SHOW max_connections;"

# Шаг 4: текущий pool size в коде
grep -n "min_size\|max_size" /opt/catalog-bot/data/database.py | head -10
```

### Устранение

**А. Убить зависшие idle-соединения (>10 мин без активности):**
```bash
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'catalog'
     AND state = 'idle'
     AND (now() - state_change) > interval '10 minutes';"
```

**Б. Убить долгие активные запросы (>30 сек):**
```bash
docker exec catalog-bot-postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'catalog'
     AND (now() - query_start) > interval '30 seconds'
     AND state != 'idle';"
```

**В. Перезапуск всех ботов (освобождает pool мгновенно):**
```bash
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart
# Подождать 30 секунд, проверить health
sleep 30
curl -s localhost:8081/health
```

**Г. Постоянное решение — увеличить max_size в database.py:**
```python
# В data/database.py найти create_pool и увеличить max_size:
self._pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=5,
    max_size=30,  # увеличить с 20 до 30
)
# Задеплоить: git push origin main
```

### Профилактика
- Pool stats logging каждые 60 сек (см. monitoring-observability → DB Pool Monitoring)
- `alert-design` alert при utilization > 80%

---

## RB-04: AI Search Quota Exceeded

### Симптомы
- Логи содержат `429 Too Many Requests` от Gemini или OpenAI
- AI-поиск не работает или возвращает fallback-результаты
- Клиенты видят обычный поиск вместо умного

### Диагностика

```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b

# Шаг 1: найти 429 в логах AI adapter
docker logs catalog-bot-telegram --tail=200 | grep -i "quota\|429\|gemini\|openai\|rate.limit"

# Шаг 2: посчитать AI запросы за последний час
docker logs catalog-bot-telegram --since=1h 2>&1 | grep '"event": "request_completed"' | wc -l

# Шаг 3: стоимость за последние 24 часа
docker logs catalog-bot-telegram --since=24h 2>&1 | \
  python3 -c "import sys,json; costs=[json.loads(l).get('cost_usd',0) for l in sys.stdin if 'cost_usd' in l]; print(f'Total: \${sum(costs):.4f}')"
```

### Устранение

**А. Gemini quota исчерпана — переключить на OpenAI:**
```bash
# В .env.prod добавить/изменить:
echo "AI_SEARCH_MODEL=gpt-4o-mini" >> /opt/catalog-bot/.env.prod
# Перезапустить боты
docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml restart telegram vk
```

**Б. Оба провайдера недоступны — ждать сброса лимита:**
- Google AI: лимиты сбрасываются по минутам (RPM) и дням (daily tokens)
- OpenAI: по минутам и месяцам
- Обычно Gemini free tier сбрасывается в начале следующего дня UTC

**В. Добавить circuit breaker (постоянное решение):**
```python
# В core/services/ai_adapter.py добавить счётчик подряд идущих 429
# При N=5 подряд — отключить AI на 30 мин и алертить
```

### Профилактика
- Бюджетный алерт в Google AI Studio и OpenAI Dashboard ($5 порог)
- `alert-design` alert при cost_per_hour > $0.50
- Circuit breaker в ai_adapter.py

---

## RB-05: GCP VM Недоступна

### Симптомы
- SSH не устанавливается (`Connection timed out` или `Connection refused`)
- Все 7 ботов упали одновременно
- GitHub Actions деплой завис на SSH-шаге

### Диагностика (с локальной машины, без SSH)

```bash
# Шаг 1: статус VM через gcloud API (не требует SSH)
gcloud compute instances describe tourist-bot --zone=europe-west3-b \
  --format="get(status)"
# Ожидаемый ответ: RUNNING. Если TERMINATED или STAGING — см. устранение.

# Шаг 2: serial port output (логи загрузки VM, не требует SSH)
gcloud compute instances get-serial-port-output tourist-bot \
  --zone=europe-west3-b --tail=30

# Шаг 3: проверить billing
gcloud billing accounts list

# Шаг 4: проверить GitHub Actions
gh run list --repo Sukheil-Ganeev/VIP-DXB-CatalogBot --limit=5
```

### Устранение

**А. VM остановлена (статус TERMINATED) — запустить:**
```bash
gcloud compute instances start tourist-bot --zone=europe-west3-b
# Подождать 90 секунд (VM + Docker boot)
sleep 90
gcloud compute ssh tourist-bot --zone=europe-west3-b -- \
  'docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps'
```

**Б. VM завислась — hard reset:**
```bash
gcloud compute instances reset tourist-bot --zone=europe-west3-b
# Контейнеры с restart:always запустятся автоматически
# Подождать 2 минуты
sleep 120
curl -s http://YOUR_VM_IP:8081/health
```

**В. Диск заполнен (OOM killer убил Docker daemon):**
```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b
df -h
# Очистить Docker мусор
docker system prune -f
docker volume prune -f
# Проверить логи на размер
du -sh /var/lib/docker/containers/*/
```

**Г. Billing проблема (GCP заморозил VM):**
- Зайти в Google Cloud Console → Billing → Check account
- Пополнить баланс или активировать кредиты
- VM автоматически стартует после решения billing-проблемы
- Проверить: `gcloud compute instances describe tourist-bot --zone=europe-west3-b`

### Профилактика
- Google Cloud Monitoring → Uptime check на VM (бесплатно, уведомление на email)
- Billing alert при 80% использования бюджета
- `restart: always` для всех контейнеров в docker-compose.prod.yml
- Регулярная очистка: `docker system prune -f` в cron еженедельно

---

## Escalation Matrix

Кто что делает при каждом типе инцидента:

| Инцидент | Первая реакция | Если не помогло | Эскалация |
|----------|----------------|-----------------|-----------|
| RB-01: Bot down | Рестарт контейнера (5 мин) | Проверить DB, memory | Проверить GCP VM |
| RB-02: Webhook dead | Рестарт контейнера (5 мин) | Проверить SSL, IP | Обновить webhook в Meta/Viber |
| RB-03: DB Pool | Убить idle conn (2 мин) | Перезапуск всех ботов | Увеличить pool + задеплоить |
| RB-04: AI Quota | Переключить на OpenAI (2 мин) | Отключить AI поиск | Ждать сброс лимита (до 24ч) |
| RB-05: VM down | `gcloud instances start` (2 мин) | Hard reset | Billing check + GCP Support |

**Время реакции по уровням CRITICAL alert:**
- `bot-down` / `webhook-dead`: реагировать в течение 15 минут
- `db-pool-exhausted`: реагировать в течение 5 минут
- `gcp-vm-unreachable`: реагировать немедленно (все боты упали)
- `ai-quota-exceeded`: реагировать в течение 30 минут (fallback работает)

---

## Шаблон нового runbook

Скопируй для нового типа инцидента:

```markdown
## RB-0X: [Название]

### Симптомы
- Что видит пользователь
- Что показывают health checks
- Что в логах

### Диагностика
\```bash
# SSH на tourist-bot
gcloud compute ssh tourist-bot --zone=europe-west3-b
# Команды диагностики
\```

### Устранение
**А. Причина А:**
\```bash
# Команды
\```

### Профилактика
- Что добавить чтобы не повторялось
```
