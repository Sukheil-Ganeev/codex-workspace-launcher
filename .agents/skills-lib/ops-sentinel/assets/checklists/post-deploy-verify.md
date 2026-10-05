# Post-Deploy Verification Checklist

Run after every `git push origin main` that triggers the deploy workflow.
Server: GCP VM `tourist-bot`, zone `europe-west3-b`.

---

## Layer 1: CI/CD (remote, no SSH needed)

- [ ] **GitHub Actions workflow завершён зелёным**
  ```
  gh run list --repo Sukheil-Ganeev/VIP-DXB-CatalogBot --limit=3
  ```
  Ожидаемый статус: `completed / success`. Если `failure` — смотреть логи: `gh run view <run-id> --log-failed`

- [ ] **Нет ошибок security-scan** (bandit / pip-audit)
  Если job `security-scan` упал — блокирующий сбой, не деплоить.

---

## Layer 2: Containers (SSH на tourist-bot)

```bash
gcloud compute ssh tourist-bot --zone=europe-west3-b
```

- [ ] **Все контейнеры Up**
  ```bash
  docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps
  ```
  Ожидаемый результат: все сервисы в статусе `Up` (не `Exited`, не `Restarting`).

- [ ] **Нет crashloop** (контейнер не перезапускается)
  ```bash
  docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml ps | grep -i restarting
  ```
  Пустой вывод = хорошо.

- [ ] **Новый код задеплоен** (проверить IMAGE ID или дату создания)
  ```bash
  docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml images
  ```

---

## Layer 3: Health Checks (webhook боты)

- [ ] **Instagram 8081 ok**
  ```bash
  curl -s localhost:8081/health | python3 -m json.tool
  ```

- [ ] **WhatsApp 8082 ok**
  ```bash
  curl -s localhost:8082/health | python3 -m json.tool
  ```

- [ ] **Facebook 8083 ok**
  ```bash
  curl -s localhost:8083/health | python3 -m json.tool
  ```

- [ ] **Viber 8084 ok**
  ```bash
  curl -s localhost:8084/health | python3 -m json.tool
  ```

- [ ] **Mini App 8080 ok**
  ```bash
  curl -s localhost:8080/health | python3 -m json.tool
  ```

  Все должны вернуть `{"status": "ok", "database": "ok", ...}` с HTTP 200.

- [ ] **Batch check всех портов:**
  ```bash
  for port in 8080 8081 8082 8083 8084; do
    code=$(curl -s -o /dev/null -w "%{http_code}" localhost:$port/health)
    echo "Port $port: $code"
  done
  ```

---

## Layer 4: Long Poll боты

- [ ] **Telegram polling активен**
  ```bash
  docker logs catalog-bot-telegram --tail=30 | grep -E "polling|started|aiogram"
  ```

- [ ] **VK polling активен**
  ```bash
  docker logs catalog-bot-vk --tail=30 | grep -E "polling|longpoll|started"
  ```

---

## Layer 5: Logs — первые 5 минут

- [ ] **Нет критических ошибок в логах**
  ```bash
  docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml logs --since=5m 2>&1 | grep -i "error\|exception\|critical" | head -20
  ```

- [ ] **Нет DB connection ошибок**
  ```bash
  docker compose -f /opt/catalog-bot/deploy/docker-compose.prod.yml logs --since=5m 2>&1 | grep -i "asyncpg\|pool\|connection"
  ```

---

## Layer 6: Security (при изменениях в webhook-ботах)

Выполняй только если деплой включал изменения в `*/app.py`, `*/webhook_verify.py`, или новые зависимости.

- [ ] **HMAC верификация на новых endpoints** (ручная проверка кода)
  Для каждого нового `@app.post("/webhook/...")` убедиться что есть вызов `verify_*_signature()`.

- [ ] **Новые секреты в .env, не в коде**
  ```bash
  grep -rn "os.getenv" /opt/catalog-bot/*/config.py | grep -v "# "
  ```

---

## Layer 7: Functional Smoke Test

- [ ] **Отправить тестовое сообщение в Telegram** (@Dubaiexursions_bot) и получить ответ
- [ ] **Проверить что меню отображается** (главное меню Telegram)
- [ ] **Проверить Viber set_webhook** при деплое viber_bot:
  ```bash
  docker logs catalog-bot-viber --tail=20 | grep "set_webhook"
  ```

---

## Результат

При всех `[OK]` — деплой завершён успешно.

При любом `[FAIL]` или `[WARN]`:
- Определить тип проблемы
- Открыть `ops-sentinel: incident / type: "<тип>"` для runbook
- Типы: `bot-down`, `webhook-dead`, `db-pool-exhausted`, `ai-quota-exceeded`, `gcp-vm-unreachable`
