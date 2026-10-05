# Безопасность и Production: полное руководство

> Reference для docker-справочник | Дата: 2026-02-17

---

## 1. Rootless Mode

Rootless Docker запускает демон и контейнеры без root-привилегий. Контейнеры работают в user namespace -- root внутри контейнера = непривилегированный UID на хосте. Production-ready с Engine 27.0+.

### Установка и проверка

```bash
# Зависимости (Ubuntu/Debian)
sudo apt install -y uidmap dbus-user-session

# Установка + запуск
dockerd-rootless-setuptool.sh install
systemctl --user start docker
systemctl --user enable docker
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock

# Проверка
docker info --format '{{.SecurityOptions}}'
# Ожидаемый вывод: [name=rootless ...]
```

### Ограничения

| Ограничение | Обходной путь |
|-------------|---------------|
| Порты < 1024 недоступны | `sysctl net.ipv4.ip_unprivileged_port_start=80` или nginx на хосте |
| Overlay network на bridge не работает | Используй host networking или slirp4netns/pasta |
| Производительность сети ниже | pasta (passt) быстрее slirp4netns, включается через `--net=pasta` |

Rootless Docker на Oracle Cloud Free Tier ARM Ampere -- идеальная конфигурация для бота бронирования экскурсий в ОАЭ.

---

## 2. Non-root User в Dockerfile

Запуск контейнера от root -- главная уязвимость. При escape из контейнера (CVE-2024-21626, CVE-2019-5736) атакующий получает root на хосте.

### Полный пример

```dockerfile
# Создай системного пользователя (без shell, без home)
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app --no-create-home app

# Скопируй файлы с правильным владельцем
COPY --chown=app:app . /app

# Переключись на non-root ДО CMD
USER app
```

### Гибкость через ARG

```dockerfile
ARG UID=1001
ARG GID=1001

RUN addgroup --system --gid ${GID} app && \
    adduser --system --uid ${UID} --ingroup app app

USER app
```

Сборка с кастомным UID: `docker build --build-arg UID=1500 -t myapp .`

### Что нельзя делать

- Запускать от root "потому что проще" -- НЕТ
- Использовать `USER root` в конце Dockerfile -- НЕТ
- Игнорировать permissions на COPY -- используй `--chown=app:app`

---

## 3. Secrets Management

### При сборке (BuildKit)

Секреты доступны только на время выполнения RUN-инструкции. Не попадают в слои образа.

```dockerfile
# Dockerfile
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    ./configure --api-key="$API_KEY"
```

```bash
# Сборка
docker build --secret id=api_key,src=./secret.txt -t myapp .
```

### В runtime (Compose)

```yaml
# compose.yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_token:
    file: ./secrets/api_token.txt

services:
  booking-api:
    image: booking-api:latest
    secrets:
      - db_password
      - api_token
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
      API_TOKEN_FILE: /run/secrets/api_token
```

Секреты монтируются как файлы в `/run/secrets/` (tmpfs). Не видны в `docker inspect`, не сохраняются на диске.

### Пример для бота бронирования (туризм ОАЭ)

```yaml
# compose.yaml -- booking API стек
secrets:
  whatsapp_token:
    file: ./secrets/whatsapp_token.txt
  stripe_secret:
    file: ./secrets/stripe_key.txt
  db_password:
    file: ./secrets/db_password.txt

services:
  booking-api:
    build: .
    secrets: [whatsapp_token, stripe_secret, db_password]
    environment:
      TOURS_CURRENCY: AED
      DEFAULT_LANGUAGE: ru
```

### Что НЕ делать

| Антипаттерн | Почему опасно | Правильно |
|-------------|---------------|-----------|
| `ENV SECRET=abc123` | Видно в `docker inspect`, `docker history` | `secrets:` в Compose |
| `COPY secrets.json /app/` | Остается в слоях образа навсегда | `RUN --mount=type=secret` |
| `ARG API_KEY` при сборке | Видно в `docker history` | `--mount=type=secret` |
| `.env` файл в образе | COPY включит его в слой | `.dockerignore` + `env_file:` в Compose |

---

## 4. Resource Limits

Без лимитов один контейнер может забрать все ресурсы хоста и обрушить остальные сервисы.

### Параметры

| Параметр | CLI | Compose | Описание |
|----------|-----|---------|----------|
| Memory limit | `--memory 512m` | `deploy.resources.limits.memory: 512M` | Жёсткий лимит RAM |
| Memory reservation | `--memory-reservation 256m` | `deploy.resources.reservations.memory: 256M` | Мягкий лимит (гарантия) |
| CPU limit | `--cpus 0.5` | `deploy.resources.limits.cpus: '0.5'` | Макс. количество ядер |
| PID limit | `--pids-limit 100` | `deploy.resources.limits.pids: 100` | Защита от fork bomb |
| Memory swap | `--memory-swap 1g` | -- | Лимит swap (вкл. RAM) |

### Пример Compose для production

```yaml
services:
  booking-api:
    image: booking-api:latest
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
          pids: 100
        reservations:
          memory: 256M
          cpus: '0.25'
    restart: unless-stopped

  postgres:
    image: postgres:17-alpine
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M

  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

---

## 5. HEALTHCHECK

### В Dockerfile

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### В Compose

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 5s
  start_period: 10s
  retries: 3
```

### Параметры

| Параметр | По умолчанию | Рекомендация |
|----------|-------------|--------------|
| `interval` | 30s | 10-30s для API, 30-60s для БД |
| `timeout` | 30s | 3-5s (не больше interval) |
| `start_period` | 0s | 10-60s (дай приложению время на старт) |
| `retries` | 3 | 3-5 (больше для нестабильных сервисов) |

### Healthcheck по типу сервиса

```yaml
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  start_period: 30s

# Redis
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s

# Node.js / Python API
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
  interval: 30s
  start_period: 15s

# Nginx
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost/ || exit 1"]
  interval: 30s
```

### Рекомендации

- Используй lightweight endpoint: `/health`, не `/api/complex-query`
- `start_period` критически важен для БД и тяжелых Java-приложений
- В Compose: `depends_on: { db: { condition: service_healthy } }` ждет healthcheck
- Без curl в образе: используй встроенные инструменты (`pg_isready`, `redis-cli`, `python -c "..."`, `node -e "..."`)

---

## 6. Log Rotation

Без ротации логи заполнят диск. Это проблема #15 в troubleshooting.md.

### Глобально через daemon.json

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Путь: `/etc/docker/daemon.json` (Linux) или Docker Desktop -> Settings -> Docker Engine.

После изменения: `sudo systemctl restart docker`.

### Для конкретного контейнера (Compose)

```yaml
services:
  booking-api:
    image: booking-api:latest
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
```

### Альтернативные log-драйверы

| Драйвер | Когда использовать |
|---------|-------------------|
| `json-file` | По умолчанию, большинство случаев |
| `local` | Production на одном сервере (быстрее json-file) |
| `journald` | Интеграция с systemd |
| `fluentd` / `loki` | Централизованный сбор (ELK, Grafana) |

---

## 7. cgroup v2

cgroup v1 **deprecated** в Docker Engine 29. cgroup v2 -- единый унифицированный контроллер ресурсов.

### Проверка

```bash
# Проверить текущую версию cgroup
stat -fc %T /sys/fs/cgroup
# cgroup2fs = v2 (правильно)
# tmpfs = v1 (нужна миграция)
```

### Совместимость

Ubuntu 22.04+, Debian 12+, Fedora 31+, RHEL 9+ -- cgroup v2 по умолчанию. Ubuntu 20.04 -- cgroup v1, НЕ использовать для новых хостов.

### Миграция

Рекомендация: обнови ОС до Ubuntu 22.04+ / Debian 12+. Ручная миграция: добавь `systemd.unified_cgroup_hierarchy=1` в GRUB_CMDLINE_LINUX, затем `update-grub && reboot`.

---

## 8. Read-only Filesystem

Контейнер с read-only FS не может быть модифицирован изнутри -- защита от записи вредоносного кода.

### CLI

```bash
docker run --read-only --tmpfs /tmp --tmpfs /run myapp
```

### Compose

```yaml
services:
  booking-api:
    image: booking-api:latest
    read_only: true
    tmpfs:
      - /tmp
      - /run
    volumes:
      - uploads:/app/uploads   # Только нужные writable-директории
```

### Что нужно tmpfs

Большинство приложений требуют writable `/tmp` и `/run`. Некоторые фреймворки пишут в `/app/.cache` -- добавь tmpfs или named volume для таких путей.

---

## 9. Дополнительные меры

### Минимальные capabilities

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp
```

Compose:
```yaml
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

По умолчанию Docker даёт 14 capabilities. `--cap-drop=ALL` убирает все, `--cap-add` добавляет только нужные.

### Запрет повышения привилегий

```bash
docker run --security-opt=no-new-privileges:true myapp
```

Compose:
```yaml
security_opt:
  - no-new-privileges:true
```

Предотвращает `setuid`/`setgid` внутри контейнера.

### Docker Scout для сканирования CVE

```bash
docker scout quickview myapp:latest    # Обзор уязвимостей
docker scout cves --epss myapp:latest  # CVE с вероятностью эксплуатации
docker scout recommendations myapp     # Рекомендации по обновлению base image
```

Free tier: 3 репозитория, безлимитные local scans.

### Подпись образов

DCT (Docker Content Trust) удален из CLI в Engine 29. Альтернативы:

- **cosign (Sigstore):** keyless signing через OIDC. `cosign sign --yes ghcr.io/org/app:v1.0`
- **Notation (CNCF):** OCI-совместимые подписи. `notation sign ghcr.io/org/app:v1.0`

---

## 10. Production Checklist

| # | Пункт | Команда проверки | Приоритет |
|---|-------|-----------------|-----------|
| 1 | Non-root user в Dockerfile | `docker inspect --format '{{.Config.User}}' <image>` | P0 |
| 2 | Rootless mode или --userns-remap | `docker info --format '{{.SecurityOptions}}'` | P0 |
| 3 | Resource limits (memory + CPU) | `docker inspect --format '{{.HostConfig.Memory}}'` | P0 |
| 4 | HEALTHCHECK определен | `docker inspect --format '{{.Config.Healthcheck}}'` | P0 |
| 5 | Log rotation настроена | `docker inspect --format '{{.HostConfig.LogConfig}}'` | P0 |
| 6 | Read-only filesystem где возможно | `docker inspect --format '{{.HostConfig.ReadonlyRootfs}}'` | P1 |
| 7 | Секреты через secrets, НЕ через ENV | `docker inspect` -- нет секретов в Env[] | P0 |
| 8 | .dockerignore (нет .env, .git) | `cat .dockerignore` | P0 |
| 9 | Multi-stage build (минимум в runtime) | `docker history <image>` -- минимум слоев | P1 |
| 10 | Базовый образ slim/distroless (не :latest) | `docker inspect --format '{{.RepoTags}}'` | P0 |
| 11 | Docker Scout scan без critical CVE | `docker scout cves --only-severity critical` | P1 |
| 12 | restart: unless-stopped | `docker inspect --format '{{.HostConfig.RestartPolicy.Name}}'` | P0 |
| 13 | Named volumes для данных (не bind mounts) | `docker inspect --format '{{.Mounts}}'` | P1 |
| 14 | Backup strategy для volumes | `crontab -l` -- есть бэкап скрипт | P1 |
| 15 | Мониторинг: docker stats / Prometheus + cAdvisor | `curl localhost:9090` | P2 |

### Минимальный production-стек для бота ОАЭ

```yaml
# compose.yaml -- Production booking bot
services:
  bot:
    image: ghcr.io/org/booking-bot:v1.0
    read_only: true
    tmpfs: [/tmp]
    user: "1001:1001"
    deploy:
      resources:
        limits: { memory: 512M, cpus: '1.0' }
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      start_period: 15s
    secrets: [whatsapp_token, db_password]
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }
    restart: unless-stopped
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    environment:
      TOURS_CURRENCY: AED
      DEFAULT_LANGUAGE: ru

  db:
    image: postgres:17-alpine
    volumes: [db-data:/var/lib/postgresql/data]
    deploy:
      resources:
        limits: { memory: 1G }
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      start_period: 30s
    secrets: [db_password]
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 128mb
    volumes: [redis-data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    deploy:
      resources:
        limits: { memory: 256M }
    restart: unless-stopped

volumes:
  db-data:
  redis-data:

secrets:
  whatsapp_token:
    file: ./secrets/whatsapp_token.txt
  db_password:
    file: ./secrets/db_password.txt
```

Этот стек применяет все 15 пунктов чеклиста: non-root, resource limits, healthcheck, log rotation, secrets, read-only FS, capabilities drop, no-new-privileges, named volumes, restart policy.

---

> Безопасность -- не опциональна. Каждый пункт чеклиста -- конкретное действие, а не рекомендация. Начни с P0 (пункты 1-5, 7-8, 10, 12), затем добавь P1 и P2.
