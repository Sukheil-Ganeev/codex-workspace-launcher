# Docker Compose: полное руководство

> Reference для docker-справочник | Дата: 2026-02-17
> Docker Compose v2.40+ (CLI v5.x) | Docker Engine 29.x | Февраль 2026

---

## 1. Структура compose.yaml

Каноническое имя файла: **`compose.yaml`** (предпочтительно) или `compose.yml`. Имя `docker-compose.yml` -- legacy, только для backwards compatibility. Поле `version` в файле **не нужно** -- Compose v2 его игнорирует.

### Top-level ключи

| Ключ | Описание | Обязателен |
|------|----------|-----------|
| `name` | Имя проекта (вместо имени папки) | Нет |
| `services` | Определение контейнеров | Да |
| `networks` | Пользовательские сети | Нет |
| `volumes` | Named volumes | Нет |
| `configs` | Конфигурационные файлы | Нет |
| `secrets` | Секреты (tmpfs, не на диске) | Нет |
| `include` | Импорт других compose-файлов (v2.20+) | Нет |

```yaml
name: booking-api          # Явное имя проекта
services: ...
networks: ...
volumes: ...
secrets: ...
configs: ...
include:                   # Модульность (v2.20+)
  - compose.db.yaml
  - compose.monitoring.yaml
```

---

## 2. Директивы services

Полная таблица директив для определения сервиса:

| Директива | Описание | Пример |
|-----------|----------|--------|
| `image` | Готовый образ | `image: nginx:1.27-alpine` |
| `build` | Сборка из Dockerfile | `build: ./backend` или `build: { context: ., dockerfile: Dockerfile.prod, target: production }` |
| `container_name` | Фиксированное имя контейнера | `container_name: booking-api` |
| `ports` | Проброс портов | `ports: ["8080:80", "127.0.0.1:9090:9090"]` |
| `volumes` | Тома и bind mounts | `volumes: [db-data:/var/lib/postgresql/data, ./src:/app/src]` |
| `environment` | Переменные окружения | `environment: { NODE_ENV: production, PORT: "3000" }` |
| `env_file` | Файл с переменными | `env_file: [.env, .env.local]` |
| `depends_on` | Зависимости между сервисами | `depends_on: { db: { condition: service_healthy } }` |
| `healthcheck` | Проверка здоровья | См. секцию 3 |
| `restart` | Политика перезапуска | `restart: unless-stopped` |
| `deploy` | Ресурсы и реплики | `deploy: { resources: { limits: { memory: 512M, cpus: '1.0' } } }` |
| `profiles` | Группировка по профилям | `profiles: [dev, debug]` |
| `secrets` | Доступ к секретам | `secrets: [db_password, api_key]` |
| `configs` | Доступ к конфигам | `configs: [nginx-conf]` |
| `develop` | Compose Watch (hot-reload) | См. секцию 5 |
| `command` | Переопределить CMD | `command: ["npm", "run", "dev"]` |
| `entrypoint` | Переопределить ENTRYPOINT | `entrypoint: ["/entrypoint.sh"]` |
| `working_dir` | Рабочая директория | `working_dir: /app` |
| `labels` | Метаданные | `labels: { com.example.env: production }` |
| `logging` | Драйвер логов | `logging: { driver: json-file, options: { max-size: 10m, max-file: "3" } }` |
| `networks` | Подключение к сетям | `networks: [frontend, backend]` |
| `extra_hosts` | Записи в /etc/hosts | `extra_hosts: ["host.docker.internal:host-gateway"]` |

---

## 3. depends_on с условиями

Compose поддерживает 3 условия для `depends_on`:

| Условие | Когда запускать | Применение |
|---------|----------------|-----------|
| `service_started` | Сразу после старта (дефолт) | Сервисы без healthcheck |
| `service_healthy` | После прохождения healthcheck | БД, кэш, очереди |
| `service_completed_successfully` | После успешного завершения (exit 0) | Init-контейнеры, миграции |

### Пример с healthcheck PostgreSQL

```yaml
services:
  api:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrations:
        condition: service_completed_successfully

  migrations:
    build: ./backend
    command: ["python", "-m", "alembic", "upgrade", "head"]
    depends_on:
      db: { condition: service_healthy }

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: bookings
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
```

**Команда запуска с ожиданием:**
```bash
docker compose up -d --wait    # Ждёт пока ВСЕ healthcheck пройдут
```

---

## 4. Override файлы

### Автоматический мерж

Compose автоматически мержит `compose.yaml` + `compose.override.yaml`:

```yaml
# compose.yaml -- базовая конфигурация
services:
  api:
    build: ./backend
    environment:
      PORT: "8000"

# compose.override.yaml -- автоматически подхватывается
services:
  api:
    ports: ["8000:8000"]           # Добавляет порт (dev)
    volumes: ["./backend:/app"]    # Добавляет bind mount (hot-reload)
    environment:
      DEBUG: "true"                # Дополняет env
```

### Ручной выбор файлов

```bash
# Продакшн: базовый + prod (без override)
docker compose -f compose.yaml -f compose.prod.yaml up -d

# Тестирование: базовый + test
docker compose -f compose.yaml -f compose.test.yaml up -d
```

**Приоритет:** последний файл побеждает. Если в `compose.yaml` порт `3000:3000`, а в `compose.prod.yaml` порт `80:3000`, используется `80:3000`.

### Переменные окружения

```yaml
services:
  db:
    image: postgres:${PG_VERSION:-17}-alpine     # Дефолт: 17
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:?required} # Ошибка если не задан
      POSTGRES_DB: ${DB_NAME:-bookings}           # Дефолт: bookings
```

Источники переменных (в порядке приоритета):
1. `environment:` в compose.yaml
2. Shell environment (export)
3. `env_file:` (`.env` по умолчанию)
4. Дефолты `${VAR:-default}`

---

## 5. Compose Watch (hot-reload)

GA с Compose v2.22.0. Три режима для разработки:

| Режим | Описание | Когда использовать |
|-------|----------|-------------------|
| `sync` | Копирует изменённые файлы в контейнер | Hot Reload: uvicorn, Vite, nodemon |
| `rebuild` | Полная пересборка образа + контейнера | Изменение зависимостей (package.json, requirements.txt) |
| `sync+restart` | Копирует файлы + перезапускает контейнер | Изменение конфигурации (nginx.conf, env файлы) |

### Конфигурация

```yaml
services:
  api:
    build: ./backend
    develop:
      watch:
        - action: sync
          path: ./backend/app        # Что отслеживать на хосте
          target: /app/app            # Куда копировать в контейнере
          ignore:
            - __pycache__/
            - "*.pyc"
        - action: rebuild
          path: ./backend/requirements.txt
        - action: sync+restart
          path: ./backend/config/
          target: /app/config/

  frontend:
    build: ./frontend
    develop:
      watch:
        - action: sync
          path: ./frontend/src
          target: /app/src
        - action: rebuild
          path: ./frontend/package.json
```

```bash
# Запуск watch
docker compose watch

# Или: фоновый запуск + watch
docker compose up -d && docker compose watch
```

---

## 6. Profiles

Профили группируют сервисы, которые запускаются по запросу. Сервис **без** profile запускается **всегда**.

```yaml
services:
  api:
    build: ./backend
    # Нет profiles -- запускается всегда

  db:
    image: postgres:17-alpine
    # Нет profiles -- запускается всегда

  pgadmin:
    image: dpage/pgadmin4
    ports: ["5050:80"]
    profiles: [dev]                  # Только при --profile dev

  mailhog:
    image: mailhog/mailhog
    ports: ["8025:8025"]
    profiles: [dev]                  # Только при --profile dev

  prometheus:
    image: prom/prometheus
    profiles: [monitoring]           # Только при --profile monitoring

  grafana:
    image: grafana/grafana
    profiles: [monitoring]

  k6:
    image: grafana/k6
    profiles: [test]                 # Только при --profile test
```

```bash
docker compose up -d                          # api + db (без профилей)
docker compose --profile dev up -d            # api + db + pgadmin + mailhog
docker compose --profile monitoring up -d     # api + db + prometheus + grafana
docker compose --profile dev --profile monitoring up -d  # всё
```

---

## 7. Docker Model Runner

Compose v2.35+ поддерживает запуск LLM как сервис через `provider.type: model`. API совместим с OpenAI.

```yaml
services:
  ai:
    provider:
      type: model
      options:
        model: ai/llama3.2:1B-Q8_0

  api:
    build: ./backend
    environment:
      OPENAI_BASE_URL: http://ai:80/v1   # OpenAI-совместимый API
      OPENAI_API_KEY: unused              # Ключ не нужен (локальная модель)
```

Поддерживаемые платформы: Apple Silicon (Metal), NVIDIA GPU (CUDA), Vulkan. Модели берутся из Docker Hub namespace `ai/`.

---

## 8. Secrets и Configs

### Secrets (в tmpfs -- не на диске)

```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt       # Из файла на хосте
  api_key:
    environment: "API_KEY"                # Из переменной окружения (v2.23+)

services:
  api:
    image: myapp
    secrets:
      - db_password                       # Доступен как /run/secrets/db_password
      - api_key
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
```

### Configs (обычные файлы, с версионированием)

```yaml
configs:
  nginx-conf:
    file: ./nginx/nginx.conf

services:
  nginx:
    image: nginx:1.27-alpine
    configs:
      - source: nginx-conf
        target: /etc/nginx/nginx.conf     # Монтируется по пути
        mode: 0444                        # Read-only
```

### Разница secrets vs configs

| Аспект | Secrets | Configs |
|--------|---------|---------|
| Хранение | tmpfs (RAM) | Обычный файл |
| Путь | /run/secrets/name | Настраиваемый (target) |
| Безопасность | Не на диске, не в docker inspect | Обычная видимость |
| Применение | Пароли, токены, ключи | nginx.conf, настройки приложения |

**Правило:** пароли и токены -- всегда `secrets`, не `environment`. ENV видны в `docker inspect`.

### Чтение секретов в приложении

Многие образы поддерживают суффикс `_FILE` для чтения секрета из файла:

```yaml
environment:
  POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # PostgreSQL читает из файла
```

Для своего приложения читай секрет программно:

```python
# Python
import os
def get_secret(name):
    file_path = f"/run/secrets/{name}"
    if os.path.exists(file_path):
        return open(file_path).read().strip()
    return os.environ.get(name.upper())
```

---

## 9. include (v2.20+)

Разделяй большой compose.yaml на модули:

```yaml
# compose.yaml -- основной файл
include:
  - path: compose.db.yaml            # БД + миграции
  - path: compose.monitoring.yaml    # Prometheus + Grafana
  - path: infra/compose.nginx.yaml   # Nginx reverse proxy
    env_file: ./infra/.env           # Env для включённого файла

services:
  api:
    build: ./backend
    depends_on:
      db: { condition: service_healthy }
```

```yaml
# compose.db.yaml
services:
  db:
    image: postgres:17-alpine
    volumes: [db-data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

volumes:
  db-data:
```

`include` полностью мержит файлы. Сервисы из включённых файлов доступны для `depends_on` в основном файле.

---

## 10. Примеры

### Dev-стек (app + postgres + redis)

Полный compose.yaml для разработки с hot-reload, healthchecks и .env:

```yaml
# compose.yaml -- Dev-окружение
name: booking-dev

services:
  api:
    build:
      context: ./backend
      target: development
    ports: ["8000:8000"]
    volumes:
      - ./backend:/app                # Bind mount для hot-reload
    env_file: .env
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD:-devpass}@db:5432/bookings
      REDIS_URL: redis://redis:6379/0
      DEBUG: "true"
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    develop:
      watch:
        - action: sync
          path: ./backend/app
          target: /app/app
        - action: rebuild
          path: ./backend/requirements.txt

  db:
    image: postgres:17-alpine
    ports: ["5432:5432"]              # Доступ с хоста (dev)
    environment:
      POSTGRES_DB: bookings
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpass}
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      retries: 5
      start_period: 30s

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    command: redis-server --appendonly yes
    volumes: [redis-data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

volumes:
  db-data:
  redis-data:
```

```bash
# .env
DB_PASSWORD=devpass
TOURS_CURRENCY=AED
DEFAULT_LANGUAGE=ru
```

### Prod-стек для бота ОАЭ

Production compose.yaml для бота бронирования экскурсий и билетов в парки Дубая:

```yaml
# compose.yaml -- Production (Booking Bot ОАЭ)
name: booking-prod

services:
  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      api: { condition: service_healthy }
    restart: unless-stopped
    networks: [frontend]
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }

  api:
    image: ghcr.io/myorg/booking-api:${TAG:-latest}
    env_file: .env.prod
    environment:
      DATABASE_URL: postgresql://app:${DB_PASSWORD}@db:5432/bookings
      REDIS_URL: redis://redis:6379/0
      TOURS_CURRENCY: AED
      DEFAULT_LANGUAGE: ru
    secrets:
      - db_password
      - telegram_token
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      start_period: 15s
      retries: 3
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '1.0', memory: 512M }
        reservations: { memory: 256M }
    networks: [frontend, backend]
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: bookings
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '0.5', memory: 256M }
    networks: [backend]

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
    volumes: [redis-data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '0.25', memory: 128M }
    networks: [backend]

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true             # Изолирована от внешнего мира

volumes:
  db-data:
  redis-data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
  telegram_token:
    file: ./secrets/telegram_token.txt
```

**Что здесь применено:**
- Named volumes для персистентных данных (БД, Redis)
- Resource limits (CPU + memory) для каждого сервиса
- Healthchecks + depends_on с `service_healthy`
- `restart: unless-stopped` для автоперезапуска
- Secrets для паролей (не environment)
- Log rotation через logging options
- Двойная сеть: frontend (nginx + api) и backend (api + db + redis, `internal: true`)
- Образ из GHCR (не build в production)
- Переменные бизнес-логики: `TOURS_CURRENCY=AED`, `DEFAULT_LANGUAGE=ru`
