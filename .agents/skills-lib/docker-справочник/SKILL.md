---
name: docker-справочник
description: "Production-ready руководство по Docker - образы, контейнеры, Compose, networking, безопасность, CI/CD, деплой на VPS/ARM. Триггеры: docker, докер, контейнер, dockerfile, docker compose, docker build/run/pull/push/exec/logs/stop/ps, деплой контейнера, контейнеризация, docker hub, registry, rootless, docker security."
version: 1.0.0
author: Сухейль
---
# Docker -- Полный справочник

> Версия: 1.0 | Docker Engine 29.x | Compose v2.40+ (CLI v5.x) | Desktop 4.60 | Февраль 2026

Практическое руководство по контейнеризации приложений: от установки до production-деплоя. Охватывает Docker Engine, Compose, networking, безопасность, CI/CD и AI-интеграции (Model Runner, MCP Toolkit).

**Для кого:** разработчики, DevOps-инженеры, предприниматели, контейнеризирующие бизнес-сервисы (боты, API, webhook-серверы).

**Когда использовать:**
- Контейнеризация приложения (бот, API, веб-сервис)
- Настройка multi-container стека (app + db + cache + nginx)
- Деплой на VPS/ARM-сервер через Docker Compose
- CI/CD pipeline с Docker (GitHub Actions, GitLab CI)
- Вопросы по безопасности контейнеров, образам, сетям

**Для туристического бизнеса ОАЭ:** контейнеризация Telegram/WhatsApp ботов бронирования, Booking API с валютой AED, деплой на Oracle Cloud Free Tier (ARM), nginx reverse proxy для webhook-серверов. Примеры: `assets/examples/04-booking-api-uae/`.

## Содержание

- [Quick Start](#quick-start)
- [0. Установка и настройка](#0-установка-и-настройка)
- [1. Основы Docker](#1-основы-docker)
- [2. Образы (Images)](#2-образы-images)
- [3. Dockerfile](#3-dockerfile)
- [4. Docker Compose](#4-docker-compose)
- [5. Volumes и данные](#5-volumes-и-данные)
- [6. Networking](#6-networking)
- [7. Docker Registry](#7-docker-registry)
- [8. Безопасность и Production](#8-безопасность-и-production)
- [9. CI/CD с Docker](#9-cicd-с-docker)
- [Типичные ошибки (Top 15)](#типичные-ошибки-top-15)
- [Связанные справочники](#связанные-справочники)
- [Навигация по справочнику](#навигация-по-справочнику)
- [Ресурсы](#ресурсы)

---

## Quick Start

Три сценария для быстрого старта -- от первого контейнера до полного стека.

### Сценарий А: Первый контейнер за 2 минуты

Запусти Nginx и открой в браузере -- контейнеризация в одну команду.

```bash
docker run -d -p 8080:80 --name mysite nginx:1.27-alpine
# Открой http://localhost:8080 -- сайт работает!
docker stop mysite && docker rm mysite  # очистка
```

### Сценарий Б: FastAPI бот за 10 минут

Создай `Dockerfile` для FastAPI-приложения, собери и запусти.

```dockerfile
FROM python:3.13-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t mybot:v1 .
docker run -d -p 8000:8000 --name bot mybot:v1
curl http://localhost:8000/health  # проверка
```

### Сценарий В: Fullstack стек за 15 минут

Один файл `compose.yaml` -- три сервиса: приложение, база данных, кэш.

```yaml
# compose.yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    depends_on:
      db: { condition: service_healthy }
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/app
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      retries: 5
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes

volumes:
  pgdata:
```

```bash
docker compose up -d --wait   # запуск + ожидание healthcheck
docker compose logs -f app    # логи приложения
docker compose down -v        # остановка + очистка
```

> После Quick Start переходи к модулям ниже для углублённого изучения.

---

## 0. Установка и настройка

### Docker Desktop (Windows / macOS)

**Требования:** Windows 10 22H2+ (WSL2), macOS текущая и 2 предыдущие мажорные версии, 4 GB RAM.

**Шаг 1: Включи WSL2 (Windows)**
```powershell
wsl --install
```

**Шаг 2:** Скачай Docker Desktop с [docker.com](https://www.docker.com/products/docker-desktop/), установи, включи WSL2-интеграцию.

**macOS:** через `.dmg` или `brew install --cask docker`. На Apple Silicon образы `linux/arm64` работают нативно. **VirtioFS** -- дефолтный механизм file sharing (macOS 12.5+), значительно быстрее legacy osxfs.

### Docker Engine (Linux / сервер)

```bash
# Ubuntu 24.04 / 22.04 (x86_64 и arm64)
sudo apt update && sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

**Post-install:**
```bash
sudo usermod -aG docker $USER && newgrp docker
sudo systemctl enable docker.service containerd.service
docker run hello-world
```

### Конфигурация daemon.json

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "default-address-pools": [{ "base": "172.17.0.0/12", "size": 24 }],
  "features": { "containerd-snapshotter": true },
  "live-restore": true
}
```

**Ключевые параметры:** `log-opts` -- ротация логов (без неё логи растут бесконечно), `containerd-snapshotter` -- containerd image store (дефолт для новых установок Engine 29+), `live-restore` -- контейнеры живут при рестарте демона.

### Лицензирование Docker Desktop (с декабря 2024)

| План | Стоимость (annual) | Pull Limits |
|------|--------------------|-------------|
| **Personal** | Бесплатно | 100 pulls/час |
| **Pro** | $9/мес | Безлимитно |
| **Team** | $15/юзер/мес | Безлимитно |
| **Business** | $24/юзер/мес | Безлимитно |

Docker Desktop бесплатен для компаний < 250 человек И < $10M дохода. **Docker Engine** -- полностью бесплатный (Apache 2.0).

Docker Hub без аутентификации: **10 pulls/час** (с 1 апреля 2025). Всегда авторизуйся в CI/CD.

> Подробнее: `references/cheatsheet.md`, `references/troubleshooting.md`

---

## 1. Основы Docker

### Архитектура

```
Docker CLI (docker) --> REST API --> dockerd (daemon)
                                       |
                                  containerd (CNCF)
                                       |
                                  containerd-shim
                                       |
                                    runc (OCI)
```

**Docker CLI** отправляет запросы к **dockerd** через REST API. Демон управляет образами, контейнерами, сетями, томами. **containerd** -- управление жизненным циклом контейнеров. **runc** -- низкоуровневый OCI runtime (namespaces, cgroups).

### Образы vs контейнеры

| Понятие | Суть |
|---------|------|
| **Image** | Неизменяемый шаблон из слоёв (layers). Read-only |
| **Container** | Запущенный экземпляр образа. Writable layer поверх read-only слоёв |
| **Layer** | Diff файловой системы, создаётся одной инструкцией Dockerfile |
| **Registry** | Хранилище образов (Docker Hub, GHCR, self-hosted) |

### Ключевые команды

```bash
docker run -d --name web -p 8080:80 nginx:1.27  # запуск
docker ps                                         # список запущенных
docker ps -a                                      # все (включая остановленные)
docker logs -f web                                # логи (follow)
docker exec -it web bash                          # shell внутри контейнера
docker stop web && docker rm web                  # остановка и удаление
docker system prune -a                            # очистка всего неиспользуемого
docker stats                                      # потребление ресурсов
docker inspect web                                # полная информация (JSON)
```

### Жизненный цикл контейнера

`created` -> `running` -> `paused` -> `stopped` -> `removed`

**Restart policies:** `no` (дефолт), `on-failure:N`, `always`, `unless-stopped` (рекомендуется для сервисов).

> Подробнее: `references/cheatsheet.md`

---

## 2. Образы (Images)

### Актуальные base images (февраль 2026)

| Image | Размер | Когда использовать |
|-------|--------|-------------------|
| `python:3.13-slim-bookworm` | ~150 MB | Production Python (glibc) |
| `node:22-slim` | ~180 MB | Production Node.js |
| `golang:1.26-bookworm` | ~800 MB | Только для сборки, prod на `scratch` |
| `alpine:3.21` | ~5 MB | Минимальный размер, осторожно с Python C-ext |
| `gcr.io/distroless/static-debian12` | ~2 MB | Статические бинарники (Go, Rust), без shell |
| `scratch` | 0 MB | Абсолютный минимум |

**Рекомендации:** `-slim` (Debian) для Python/Node.js, не Alpine (проблемы с musl libc). Всегда pin версию: `python:3.13-slim-bookworm`, не `python:latest`. Для Go/Rust: multi-stage с `scratch` или `distroless`.

### Команды управления образами

```bash
docker pull nginx:1.27-alpine           # скачать
docker build -t myapp:v1.0 .            # собрать
docker tag myapp:v1.0 ghcr.io/org/app   # тег
docker push ghcr.io/org/app:v1.0        # push
docker image prune -a                    # удалить неиспользуемые
docker manifest inspect python:3.13-slim # показать платформы
```

### Multi-platform Images

```bash
docker buildx create --name multibuilder --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t myregistry.com/myapp:v1.0 --push .
```

Multi-platform образы содержат **manifest list** -- Docker выбирает нужный для текущей архитектуры. Кросс-сборка через QEMU в 5-8x медленнее нативной; для тяжёлых билдов используй **Docker Build Cloud**.

> Подробнее: `references/cheatsheet.md`

---

## 3. Dockerfile

### Ключевые инструкции

| Инструкция | Назначение | Пример |
|------------|-----------|--------|
| `FROM` | Базовый образ / новый stage | `FROM python:3.13-slim AS builder` |
| `WORKDIR` | Рабочая директория | `WORKDIR /app` |
| `COPY` | Копирование файлов | `COPY requirements.txt .` |
| `RUN` | Выполнить команду (новый слой) | `RUN pip install -r requirements.txt` |
| `ENV` | Переменная окружения (в образе) | `ENV PYTHONUNBUFFERED=1` |
| `ARG` | Переменная сборки (НЕ в контейнере) | `ARG VERSION=1.0` |
| `EXPOSE` | Документировать порт (не открывает) | `EXPOSE 8000` |
| `USER` | Пользователь (безопасность!) | `USER appuser` |
| `HEALTHCHECK` | Проверка здоровья | `HEALTHCHECK CMD curl -f localhost:8000/health` |
| `CMD` | Команда по умолчанию (переопределяется) | `CMD ["uvicorn", "app:app"]` |
| `ENTRYPOINT` | Основной процесс (не переопределяется) | `ENTRYPOINT ["python"]` |

### Multi-Stage Build (production-ready Python)

```dockerfile
# === Builder ===
FROM python:3.13-slim-bookworm AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt
COPY . .

# === Production ===
FROM python:3.13-slim-bookworm AS production
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=builder /usr/local/lib/python3.13/site-packages \
     /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### BuildKit фичи

BuildKit -- дефолтный builder с Engine 23.0 (2023). `docker build` = alias для `docker buildx build` с Engine 24.0.

- **Cache mounts:** `RUN --mount=type=cache,target=/root/.cache/pip` -- кэш между сборками
- **Secrets:** `RUN --mount=type=secret,id=key cat /run/secrets/key` -- не попадают в слои
- **COPY --link:** слой не зависит от предыдущих, ускоряет ребазирование

### .dockerignore (обязателен!)

```dockerignore
.git
.env
*.env
node_modules
__pycache__
.venv
*.md
Dockerfile*
compose*.yml
.dockerignore
*.log
*.pem
*.key
```

**Порядок слоёв (от редко меняющихся к часто):** base image -> системные пакеты -> зависимости -> исходный код. Это максимизирует кэширование.

> См. также: `references/dockerfile-guide.md` для детального разбора multi-stage и BuildKit.
> Подробнее: `references/faq.md`

---

## 4. Docker Compose

### Основы

Compose v2 -- плагин Docker CLI (`docker compose`, без дефиса). Compose v1 (`docker-compose`, Python) мёртв с июня 2023. Compose CLI перешел на нумерацию **v5.x** (пропущены v3/v4, чтобы не путать с форматами compose-файлов).

Рекомендуемое имя файла: **`compose.yaml`** (каноническое) или `compose.yml`. Поле `version` в файле **не нужно** -- Compose v2 его игнорирует.

### Пример: FastAPI + PostgreSQL + Redis + Nginx

```yaml
# compose.yaml
services:
  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      api: { condition: service_healthy }
    restart: unless-stopped

  api:
    build:
      context: ./backend
      target: production
    env_file: .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '1.0', memory: 512M }
    develop:
      watch:
        - action: sync
          path: ./backend/app
          target: /app/app
        - action: rebuild
          path: ./backend/requirements.txt

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      retries: 5
      start_period: 30s
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb
    volumes: [redis-data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    restart: unless-stopped

volumes:
  db-data:
  redis-data:
```

### Compose Watch (GA с v2.22.0)

Три режима hot-reload для разработки:

| Action | Что делает | Когда |
|--------|-----------|-------|
| `sync` | Копирует файлы в контейнер | Hot Reload (uvicorn, Vite) |
| `rebuild` | Пересборка образа + контейнера | Изменение зависимостей |
| `sync+restart` | Копирует + рестарт процесса | Изменение конфигурации |

```bash
docker compose watch              # запуск watch
docker compose up -d && docker compose watch  # фоновый запуск + watch
```

### Docker Model Runner (GA)

Локальный запуск LLM прямо в Docker. Совместим с OpenAI API. Поддержка: Apple Silicon, NVIDIA GPU, Vulkan. Полезно для AI-функций в боте бронирования (генерация описаний туров, перевод текстов, классификация запросов).

```yaml
services:
  ai:
    provider:
      type: model
      options:
        model: ai/llama3.2:1B-Q8_0
  app:
    build: .
    environment:
      OPENAI_BASE_URL: http://ai/v1  # Совместим с OpenAI SDK
```

### Пример: Booking API для экскурсий ОАЭ

Добавь переменные для туристического бизнеса в Compose-стек:

```yaml
# compose.yaml -- Booking API для туров по ОАЭ
services:
  booking-api:
    build: ./backend
    environment:
      TOURS_CURRENCY: AED
      DEFAULT_LANGUAGE: ru
      TIMEZONE: Asia/Dubai
      WHATSAPP_PHONE: "+971565906911"
    env_file: .env
    depends_on:
      db: { condition: service_healthy }
    ports: ["8000:8000"]
    restart: unless-stopped

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: booking
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [booking-data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s

volumes:
  booking-data:
```

> См. Модуль 6 для networking в Compose (multi-network изоляция frontend/backend).
> Полный пример: `assets/examples/04-booking-api-uae/`

### Ключевые команды Compose

```bash
docker compose up -d --wait       # запуск + ждать healthcheck
docker compose down -v            # остановка + удаление томов
docker compose logs -f api        # логи сервиса
docker compose exec db psql -U postgres  # shell в БД
docker compose build --no-cache   # пересборка без кэша
docker compose --profile dev up   # активация профиля
```

> См. также: `references/compose-guide.md` для override-файлов, profiles, secrets и Compose Watch.
> Подробнее: `references/cheatsheet.md`

---

## 5. Volumes и данные

### Четыре типа хранилищ

| Тип | Персистентность | Скорость | Когда |
|-----|----------------|----------|-------|
| **Named Volume** | Да | Нативная | Данные БД, uploads, кэш сборки |
| **Bind Mount** | Да (хост) | macOS/Win медленнее | Разработка (hot-reload), конфиги (:ro) |
| **tmpfs** | Нет (RAM) | Макс. | Секреты, временные файлы |
| **type=image** (Docker 28+) | Нет | Нативная | Read-only данные из другого образа |

```bash
docker run -v pgdata:/var/lib/postgresql/data postgres:17  # named
docker run -v $(pwd)/src:/app/src:ro myapp                 # bind mount
docker run --tmpfs /app/tmp:rw,size=100m myapp             # tmpfs
docker run --mount type=image,source=mydata:v1,target=/data myapp  # image (v28+)
```

**`mount type=image`** (Engine 28+) -- монтирование содержимого образа как read-only volume. Полезно для статических ресурсов, конфигов, ML-моделей. Не требует отдельного volume -- данные берутся прямо из образа.

### Bind Mounts vs Named Volumes для production

| Аспект | Bind Mount | Named Volume |
|--------|-----------|--------------|
| **Управление** | Ручное (путь на хосте) | Docker управляет |
| **Переносимость** | Привязан к хосту | Портируемый |
| **Бэкап** | Обычный cp/rsync | `docker run --volumes-from` |
| **Production** | Только для конфигов (:ro) | **Рекомендован для данных** |
| **Производительность (macOS/Win)** | Медленнее (VirtioFS/gRPC) | Нативная скорость |
| **Docker Compose** | `./path:/container/path` | `volume_name:/path` |

**Правило:** в production используй named volumes для данных (БД, uploads) и bind mounts только для read-only конфигов.

### Backup и Restore

```bash
# Backup named volume (универсальный способ через tar)
docker run --rm -v pgdata:/data:ro -v $(pwd)/backups:/backup \
  alpine tar czf /backup/pgdata_$(date +%Y%m%d).tar.gz -C /data .

# Backup volume через --volumes-from (PostgreSQL)
docker run --rm --volumes-from my_postgres \
  -v $(pwd)/backups:/backup alpine \
  tar czf /backup/pgdata.tar.gz /var/lib/postgresql/data

# Логический дамп БД (без остановки контейнера)
docker exec my_postgres pg_dump -U postgres mydb > backup.sql

# Restore volume из tar
docker run --rm -v pgdata:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/pgdata_20260217.tar.gz -C /data
```

> Скрипт автоматического бэкапа с ротацией: `scripts/backup-volumes.sh`

### Производительность по ОС

- **Linux:** нативная скорость для всех типов
- **macOS:** VirtioFS (дефолт) -- named volumes быстрее bind mounts; для `node_modules` используй named volume
- **Windows:** храни код внутри WSL2 FS (`/home/user/project`, НЕ `/mnt/c/...`)

> Подробнее: `references/networking-volumes.md`, `references/troubleshooting.md`

---

## 6. Networking

### Типы сетей

| Driver | Изоляция | DNS | Multi-host | Когда |
|--------|----------|-----|------------|-------|
| **bridge** | Да (NAT) | Custom: Да | Нет | 99% случаев |
| **host** | Нет | Хоста | Нет | Макс. скорость (HAProxy, Nginx) |
| **overlay** | Да (VXLAN) | Да | Да | Docker Swarm, multi-host |
| **macvlan** | Да (MAC) | Нет | Нет | Контейнер как устройство в LAN |
| **none** | Полная | Нет | Нет | Полная изоляция |

**Правило:** всегда создавай custom bridge network. Default bridge НЕ имеет DNS resolution.

```bash
docker network create backend
docker run -d --name db --network backend postgres:16
docker run -d --name app --network backend -e DB_HOST=db myapp
# app обращается к db по имени -- DNS работает!
```

### DNS в Docker-сетях

**В custom bridge сети контейнеры доступны по имени сервиса** -- встроенный DNS автоматически резолвит имена. Default bridge НЕ имеет DNS -- используй только custom networks.

```bash
# Custom bridge -- DNS работает
docker network create mynet
docker run -d --name api --network mynet myapp
docker run -d --name db --network mynet postgres:17
# api может обращаться к db по имени: postgres://db:5432
```

В Compose все сервисы автоматически в одной сети `projectname_default`. Имя сервиса = DNS-имя.

### Multi-Network изоляция в Compose

Разделяй сервисы на изолированные сети для безопасности. Сеть `backend` с `internal: true` недоступна из внешнего мира -- идеально для БД и кэша.

```yaml
# compose.yaml -- multi-network изоляция
services:
  nginx:
    image: nginx:1.27-alpine
    networks: [frontend]
    ports: ["80:80"]

  api:
    build: ./backend
    networks: [frontend, backend]  # доступ к обеим сетям

  db:
    image: postgres:17-alpine
    networks: [backend]  # только backend -- изолирован от внешнего мира

  redis:
    image: redis:7-alpine
    networks: [backend]

networks:
  frontend:
  backend:
    internal: true  # Изолирована от внешнего мира
```

**Логика:** nginx видит только api, api видит nginx + db + redis, db и redis не видят nginx. Внешний трафик заходит только через nginx.

### Docker Compose Networking

Compose автоматически создаёт сеть `projectname_default`. Используй отдельные сети для изоляции (frontend/backend с `internal: true`).

**Engine 29:** экспериментальная поддержка **nftables** (замена iptables). Включить: `"ip6tables": true, "iptables": false` в `daemon.json`.

**Port binding:** `-p 127.0.0.1:8080:80` -- привязка только к localhost. По умолчанию Docker биндит на `0.0.0.0`, что может обойти firewall хоста. Для UDP: `-p 8080:80/udp`.

> Подробнее: `references/networking-volumes.md`, `references/faq.md`

---

## 7. Docker Registry

### Docker Hub

| Тип | Pull Limit (с 1 апреля 2025) |
|-----|------------------------------|
| Без аутентификации | **10 pulls/час** |
| Personal (бесплатный) | **100 pulls/час** |
| Pro / Team / Business | **Безлимитно** |

### GHCR (GitHub Container Registry)

```yaml
# GitHub Actions
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

`docker.pkg.github.com` мёртв с 24 февраля 2025 -- только `ghcr.io`.

### Self-hosted Registry

```bash
docker run -d -p 5000:5000 --restart=always --name registry registry:3
# Registry v3 -- стабильный GA (с июня 2025)
```

Для production: TLS + аутентификация + Nginx reverse proxy. Enterprise: **Harbor** (CNCF Graduated).

### Docker Scout

Анализ безопасности образов: SBOM, CVE, EPSS scoring (вероятность эксплуатации).

```bash
docker scout quickview myapp:latest    # обзор уязвимостей
docker scout cves --epss myapp:latest  # CVE с EPSS
docker scout recommendations myapp     # рекомендации
```

> Подробнее: `references/registry-ci-cd.md` для настройки GHCR, Docker Scout и self-hosted registry.

### Альтернативы Docker

| | Docker | Podman | containerd + nerdctl |
|-|--------|--------|---------------------|
| Архитектура | Daemon (dockerd) | Daemonless, rootless by design | Low-level runtime |
| Rootless | Engine 27.0+ | С рождения | Да |
| Kubernetes | Нет (containerd внутри) | CRI-O совместим | Дефолт K8s runtime |
| CI/CD | DinD хаки | Нативно без демона | nerdctl CLI |
| Экосистема | Максимальная | Совместима с Docker | WASM first-class |

> Подробнее: `references/faq.md`

---

## 8. Безопасность и Production

### Rootless Mode (production-ready с Engine 27.0+)

```bash
dockerd-rootless-setuptool.sh install
systemctl --user start docker
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock
```

Root внутри контейнера = непривилегированный UID на хосте. Сеть через slirp4netns/pasta (user-space). Порты < 1024 недоступны без доп. настройки.

### Чеклист Production-Ready

| # | Пункт | Как |
|---|-------|-----|
| 1 | Non-root user | `USER appuser` в Dockerfile |
| 2 | Minimal base image | `-slim`, `distroless`, `scratch` |
| 3 | HEALTHCHECK | В Dockerfile или Compose |
| 4 | Resource limits | `--memory`, `--cpus`, `--pids-limit` |
| 5 | Log rotation | `daemon.json`: `max-size` + `max-file` |
| 6 | Read-only FS | `--read-only` + tmpfs для writable |
| 7 | Секреты НЕ в ENV/ARG | BuildKit `--mount=type=secret` |
| 8 | Сканирование | `docker scout cves` или `trivy image` |
| 9 | Pin версии | `python:3.13-slim-bookworm`, не `:latest` |
| 10 | .dockerignore | Исключить .git, .env, node_modules |

### Secrets

```yaml
# compose.yaml
services:
  app:
    secrets: [db_password]
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

Секреты монтируются в `/run/secrets/` -- не видны в `docker inspect`. Для build-time: `--mount=type=secret`.

### Docker Content Trust -- удалён в Engine v29

DCT удален из CLI. Может быть собран как плагин. Замены: **Sigstore (cosign)** -- keyless signing через OIDC, **Notation** -- OCI-совместимые подписи (CNCF).

### Engine 29: ключевые изменения

- **containerd image store** -- дефолт для новых установок
- **cgroup v1 deprecated** -- миграция на cgroup v2
- **nftables** -- экспериментальная замена iptables
- Минимальная API версия: 1.44 (Engine < v25 = EOL)
- **Docker Debug** -- бесплатный для всех (shell с инструментами даже в distroless)

> Полный чеклист: `references/security-production.md`
> Подробнее: `references/troubleshooting.md`

---

## 9. CI/CD с Docker

### GitHub Actions Pipeline

```yaml
name: CI/CD
on:
  push:
    branches: [main]
permissions:
  contents: read
  packages: write

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/myapp
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

### Кэширование в CI

| Стратегия | Размер | Скорость |
|-----------|--------|----------|
| **GHA Cache** (`type=gha`) | До 10 GB | Быстрый |
| **Registry Cache** | Безлимитный | Средний (сеть) |
| **Local Cache** | Runner зависит | Самый быстрый |

`mode=max` кэширует все слои, включая промежуточные -- критически важно для multi-stage builds.

### ARM-билд для Oracle Cloud

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/build-push-action@v6
  with:
    platforms: linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
```

**Oracle Cloud Free Tier:** до 4 OCPU + 24 GB RAM ARM Ampere A1, бесплатно навсегда. Все основные образы (Python, Node.js, Nginx, Postgres) поддерживают `linux/arm64`.

### Деплой бота бронирования на Oracle Cloud

Oracle Cloud Free Tier (ARM Ampere A1: до 4 OCPU + 24 GB RAM) -- идеальная платформа для деплоя Docker-приложений туристического бизнеса. Собери ARM-образ в GitHub Actions, задеплой по SSH:

```yaml
# В GitHub Actions workflow (см. pipeline выше)
deploy:
  needs: build-and-push
  runs-on: ubuntu-latest
  steps:
    - uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.ORACLE_HOST }}
        username: ubuntu
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/booking-bot
          echo ${{ secrets.GHCR_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker compose pull
          docker compose up -d --remove-orphans
          docker image prune -f
```

> Полный пример CI/CD pipeline: `assets/examples/05-ci-cd-pipeline/`

### Docker Swarm (кратко)

Встроенный оркестратор для простых кластеров (3-10 узлов): `docker swarm init`, `docker service create`. Для серьёзного production рассмотри Kubernetes. Docker Compose достаточен для 1-3 VPS.

> Подробнее: `references/registry-ci-cd.md`, `references/cheatsheet.md`

---

## Типичные ошибки (Top 15)

| # | Ошибка | Решение |
|---|--------|---------|
| 1 | `FROM python:latest` | Pin версию: `python:3.13-slim-bookworm` |
| 2 | Секреты через ENV/ARG | BuildKit `--mount=type=secret` |
| 3 | Запуск от root | `USER appuser` в Dockerfile |
| 4 | Нет `.dockerignore` | Исключить .git, node_modules, .env |
| 5 | `docker-compose` (v1) | `docker compose` (v2, без дефиса) |
| 6 | `version: "3.8"` в compose | Удалить поле `version` |
| 7 | Нет HEALTHCHECK | Добавить в Dockerfile или Compose |
| 8 | Один контейнер = всё | Один процесс = один контейнер |
| 9 | Нет log rotation | `daemon.json`: max-size + max-file |
| 10 | Alpine + Python C-ext | Использовать `-slim` (Debian-based) |
| 11 | `docker system` забит | Регулярно `docker system prune` |
| 12 | Bind mount в production | Named volumes для данных |
| 13 | Нет resource limits | `--memory`, `--cpus`, `--pids-limit` |
| 14 | `pip install --no-deps` | `--no-cache-dir` (--no-deps только с pre-built wheels) |
| 15 | Watchtower для авто-обновлений | ARCHIVED (дек. 2025), используй WUD или DIUN |

---

## Связанные справочники

| Скилл | Связь с Docker |
|-------|---------------|
| `git-github-справочник` | GitHub Actions CI/CD, Container Registry (GHCR), автоматический деплой |
| `yandex-cloud-справочник` | Serverless Containers, Container Registry, деплой на облачные VPS |
| `javascript-nodejs-справочник` | Контейнеризация Express/Fastify API, multi-stage для Node.js |
| `database-sql-справочник` | PostgreSQL/Redis в Docker Compose, volume management, бэкапы |
| `telegram-bot-справочник` | Контейнеризация Telegram-ботов, деплой через Compose |
| `whatsapp-bot-справочник` | WhatsApp бот в Docker, webhook через nginx reverse proxy |

---

## Навигация по справочнику

### Когда читать какой reference

| Ситуация | Начни с | Затем |
|----------|---------|-------|
| Первый раз с Docker | `cheatsheet.md` | `troubleshooting.md` |
| Пишешь Dockerfile | `dockerfile-guide.md` | `cheatsheet.md` |
| Настраиваешь Compose | `compose-guide.md` | `cheatsheet.md` |
| Деплоишь в production | `security-production.md` | `registry-ci-cd.md` |
| Проблемы с сетью/volumes | `networking-volumes.md` | `troubleshooting.md` |
| Вопросы по Docker | `faq.md` | `cheatsheet.md` |

### Шаблоны (assets/templates/)

Готовые production-ready шаблоны -- копируй и адаптируй под свой проект.

| Шаблон | Описание |
|--------|----------|
| `Dockerfile.node` | Multi-stage для Node.js 22: builder + production, non-root, healthcheck |
| `Dockerfile.python` | Multi-stage для Python 3.13: pip venv + gunicorn, non-root, healthcheck |
| `docker-compose.dev.yml` | Dev-окружение: app + postgres + redis, bind mounts, Compose Watch |
| `docker-compose.prod.yml` | Production: nginx + app + db + redis, secrets, resource limits, logging |
| `.dockerignore` | Универсальный для Node.js + Python проектов |
| `daemon.json` | Рекомендуемая конфигурация Docker Engine (log rotation, DNS, snapshotter) |
| `nginx.conf` | Reverse proxy: gzip, security headers, proxy pass, SSL placeholder |
| `.github/workflows/docker-ci.yml` | GitHub Actions: buildx, GHCR, multi-platform, cache |

### Примеры (assets/examples/)

Рабочие примеры -- запусти одной командой для изучения.

| Пример | Описание | Команда |
|--------|----------|---------|
| `01-simple-node-api/` | Минимальный Node.js API в контейнере | `docker build && docker run` |
| `02-python-flask-app/` | Flask + gunicorn с multi-stage build | `docker build && docker run` |
| `03-fullstack-compose/` | Nginx + Node.js + PostgreSQL + Redis стек | `docker compose up -d` |
| `04-booking-api-uae/` | Booking API для туризма ОАЭ (экскурсии, AED) | `docker compose up -d` |
| `05-ci-cd-pipeline/` | Полный CI/CD: GitHub Actions + GHCR + deploy | GitHub Actions workflow |

### Скрипты (scripts/)

| Скрипт | Описание |
|--------|----------|
| `cleanup-docker.sh` | Очистка Docker-ресурсов (контейнеры, images, cache, volumes) |
| `backup-volumes.sh` | Бэкап named volumes с ротацией (tar.gz + pg_dump) |
| `deploy-compose.sh` | Deploy Compose стека с healthcheck и rollback |

---

## Ресурсы

### Docker MCP Toolkit

Управление контейнеризированными MCP-серверами из Docker Desktop. MCP Catalog на Docker Hub -- 100+ готовых MCP-серверов. MCP Gateway -- безопасный шлюз. Поддержка Claude, Cursor и других MCP-клиентов. Все образы `mcp/` подписаны Docker и включают SBOM.

### Watchtower -- ARCHIVED

Watchtower **официально заархивирован** (декабрь 2025), несовместим с Docker 28+/29+ (устаревший API). Альтернативы:
- **What's Up Docker (WUD):** мониторинг + обновление + dashboard
- **DIUN:** только нотификации о новых версиях (не обновляет контейнеры)

### Docker Init

`docker init` -- интерактивный генератор Dockerfile, compose.yaml и .dockerignore для твоего проекта. Распознаёт Node.js, Python, Go, Rust, Java. Запусти в корне проекта -- получишь production-ready конфигурацию за 30 секунд.

```bash
cd /path/to/myproject
docker init
# Ответь на вопросы -- Docker создаст Dockerfile, compose.yaml, .dockerignore
```

### Документация

- [Docker Docs](https://docs.docker.com/) -- официальная документация
- [Docker Blog](https://www.docker.com/blog/) -- новости и руководства
- [Docker Hub](https://hub.docker.com/) -- реестр образов
- [Compose Specification](https://compose-spec.io/) -- спецификация Compose файлов

## Таблица references

| Файл | Описание |
|------|----------|
| `references/cheatsheet.md` | Шпаргалка: все команды Docker, Compose, Dockerfile инструкции |
| `references/faq.md` | FAQ: 29 вопросов-ответов по Docker |
| `references/troubleshooting.md` | Решение типичных проблем (симптом -> причина -> решение, 22 проблемы) |
| `references/dockerfile-guide.md` | Полное руководство по Dockerfile: все инструкции, multi-stage, BuildKit |
| `references/compose-guide.md` | Полное руководство по Compose: директивы, override, Watch, profiles, secrets |
| `references/security-production.md` | Безопасность и production: rootless, secrets, resource limits, чеклист |
| `references/networking-volumes.md` | Сети и хранилища: типы, DNS, multi-network, бэкапы, производительность |
| `references/registry-ci-cd.md` | Registry и CI/CD: Docker Hub, GHCR, Scout, GitHub Actions, деплой |

---

> Docker-справочник v1.0 | Февраль 2026 | Автор: Сухейль
