# Dockerfile: полное руководство

> Reference для docker-справочник | Дата: 2026-02-17
> Docker Engine 29.x | BuildKit (дефолт с Engine 23.0) | Февраль 2026

---

## 1. Все инструкции Dockerfile

| Инструкция | Описание | Пример |
|------------|----------|--------|
| `FROM` | Базовый образ, начинает новый stage | `FROM python:3.13-slim AS builder` |
| `RUN` | Выполняет команду, создаёт новый слой | `RUN apt-get update && apt-get install -y curl` |
| `COPY` | Копирует файлы из build context | `COPY requirements.txt .` |
| `ADD` | Как COPY + распаковка tar + URL (**предпочитай COPY**) | `ADD app.tar.gz /app/` |
| `WORKDIR` | Устанавливает рабочую директорию | `WORKDIR /app` |
| `ENV` | Переменная окружения (сохраняется в образе) | `ENV PYTHONUNBUFFERED=1` |
| `ARG` | Переменная сборки (НЕ доступна в контейнере) | `ARG VERSION=1.0` |
| `EXPOSE` | Документирует порт (не открывает его) | `EXPOSE 8000` |
| `CMD` | Команда по умолчанию (переопределяется при `docker run`) | `CMD ["uvicorn", "app:app"]` |
| `ENTRYPOINT` | Основной процесс (не переопределяется без `--entrypoint`) | `ENTRYPOINT ["python", "-m"]` |
| `USER` | Задаёт пользователя для RUN/CMD/ENTRYPOINT | `USER appuser` |
| `HEALTHCHECK` | Проверка здоровья контейнера | `HEALTHCHECK CMD curl -f localhost/health` |
| `VOLUME` | Объявляет точку монтирования | `VOLUME ["/data"]` |
| `LABEL` | Метаданные образа (key=value) | `LABEL version="1.0" maintainer="team"` |
| `SHELL` | Меняет shell по умолчанию для RUN | `SHELL ["/bin/bash", "-c"]` |
| `STOPSIGNAL` | Сигнал для graceful shutdown | `STOPSIGNAL SIGQUIT` |

**Важно:** `ADD` используй только для распаковки архивов. Для обычного копирования всегда `COPY` -- он предсказуемее и прозрачнее.

### ARG: область видимости

`ARG` объявленный **перед** `FROM` доступен только в самом `FROM`. Для использования в стадии -- объяви повторно:

```dockerfile
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Нужно объявить снова внутри стадии!
ARG PYTHON_VERSION
RUN echo "Python version: ${PYTHON_VERSION}"
```

### docker init (быстрый старт)

Если не знаешь с чего начать -- запусти `docker init` в корне проекта. Эта команда интерактивно создаёт Dockerfile, compose.yaml и .dockerignore, подходящие для твоего стека (Python, Node.js, Go, Rust, Java). Доступна с Docker Desktop 4.18+.

---

## 2. Multi-stage builds

### Зачем

Multi-stage позволяет разделить **сборку** и **runtime**. В builder-стадии устанавливаются зависимости и компилируется код, а в production-стадию копируется только результат. Итог -- минимальный размер образа и минимальная поверхность атаки.

### Пример 1: Node.js 22

```dockerfile
# === Builder ===
FROM node:22-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production
COPY . .
RUN npm run build

# === Production ===
FROM node:22-slim
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app
WORKDIR /app
COPY --from=builder --chown=app:app /app/dist ./dist
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
COPY --from=builder --chown=app:app /app/package.json ./
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"
CMD ["node", "dist/index.js"]
```

### Пример 2: Python 3.13

```dockerfile
# === Builder ===
FROM python:3.13-slim-bookworm AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# === Production ===
FROM python:3.13-slim-bookworm
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --chown=app:app . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Пример 3: Go 1.26 (scratch)

```dockerfile
# === Builder ===
FROM golang:1.26-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server ./cmd/server

# === Production ===
FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server
USER 65534:65534
EXPOSE 8080
ENTRYPOINT ["/server"]
```

**Важно:** для Go используй `golang:1.26-bookworm` (не alpine), потому что alpine может сломать CGO-зависимости. Production на `scratch` или `distroless`.

### Сравнение размеров

| Подход | Node.js | Python | Go |
|--------|---------|--------|-----|
| Без multi-stage | ~900 MB | ~600 MB | ~800 MB |
| Multi-stage (slim) | ~150 MB | ~120 MB | -- |
| Multi-stage (scratch/distroless) | -- | -- | ~10 MB |

---

## 3. BuildKit RUN --mount

BuildKit -- дефолтный builder с Engine 23.0. Поддерживает 4 типа `--mount`:

### Cache (кэш между сборками)

```dockerfile
# Кэш pip (Python)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Кэш npm (Node.js)
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# Кэш apt
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && apt-get install -y curl
```

### Secret (секреты при сборке)

```dockerfile
# Секрет не попадает в слои образа!
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    npm install --registry=https://npm.pkg.github.com

# Сборка:
# docker build --secret id=npm_token,src=./npm_token.txt .
```

### SSH (ключи для private repos)

```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:org/private-repo.git

# Сборка:
# docker build --ssh default .
```

### Bind (файлы из build context без COPY)

```dockerfile
# Временный bind -- не создаёт слой, экономит место
RUN --mount=type=bind,source=package.json,target=/app/package.json \
    --mount=type=bind,source=package-lock.json,target=/app/package-lock.json \
    npm ci --only=production
```

---

## 4. COPY варианты

### COPY --link (BuildKit, улучшение кэширования)

```dockerfile
# Слой не зависит от предыдущих -- ускоряет ребазирование
COPY --link --from=builder /app/dist ./dist
```

Когда базовый образ обновляется, `--link` слои не пересобираются. Используй для COPY из другого stage.

### COPY --from (из предыдущего stage или образа)

```dockerfile
# Из предыдущего stage
COPY --from=builder /app/dist ./dist

# Из внешнего образа
COPY --from=nginx:1.27-alpine /etc/nginx/nginx.conf /etc/nginx/nginx.conf
```

### COPY --chown (с правами)

```dockerfile
# Файлы сразу принадлежат пользователю app
COPY --chown=app:app . /app
COPY --from=builder --chown=app:app /app/dist ./dist
```

Всегда используй `--chown` при копировании в каталоги non-root пользователя, иначе файлы будут принадлежать root.

---

## 5. Выбор base image

| Image | Размер | Пакетный менеджер | Когда использовать |
|-------|--------|-------------------|-------------------|
| `alpine:3.21` | ~5 MB | apk | Минимальный размер, утилиты (curl, tar) |
| `python:3.13-slim-bookworm` | ~150 MB | apt (Debian) | Production Python (glibc, C-расширения работают) |
| `node:22-slim` | ~180 MB | apt (Debian) | Production Node.js |
| `golang:1.26-bookworm` | ~800 MB | apt (Debian) | Только builder stage (production на scratch) |
| `gcr.io/distroless/static-debian12` | ~2 MB | Нет | Статические бинарники (Go, Rust), без shell |
| `scratch` | 0 MB | Нет | Абсолютный минимум (Go, Rust, один бинарник) |

### Рекомендации по выбору

- **Python/Node.js:** всегда `-slim` (Debian). Alpine ломает C-расширения Python (musl vs glibc)
- **Go/Rust:** multi-stage с `scratch` или `distroless` для production
- **Утилиты:** `alpine:3.21` для side-car контейнеров (backup, cron)
- **Pin версию:** `python:3.13-slim-bookworm`, НЕ `python:latest`

---

## 6. CMD vs ENTRYPOINT

| Аспект | CMD | ENTRYPOINT |
|--------|-----|------------|
| Переопределяется | Да (`docker run myapp bash`) | Нет (нужен `--entrypoint`) |
| Exec form | `CMD ["node", "app.js"]` | `ENTRYPOINT ["python", "-m"]` |
| Shell form | `CMD node app.js` | `ENTRYPOINT python -m app` |
| С PID 1 | Exec: да, Shell: нет | Exec: да, Shell: нет |
| Комбинация | Аргументы к ENTRYPOINT | Основная команда |

### Exec form vs Shell form

```dockerfile
# Exec form (рекомендуется) -- процесс = PID 1, получает SIGTERM
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]

# Shell form -- обёрнут в /bin/sh -c, НЕ получает SIGTERM напрямую
CMD uvicorn app:app --host 0.0.0.0
```

**Всегда используй exec form.** Shell form запускает процесс через shell, и `docker stop` отправляет SIGTERM шеллу, а не приложению.

### Комбинация ENTRYPOINT + CMD

```dockerfile
# ENTRYPOINT -- фиксированная команда
ENTRYPOINT ["python", "-m", "gunicorn"]

# CMD -- аргументы по умолчанию (переопределяются при docker run)
CMD ["app.main:app", "-w", "4", "-b", "0.0.0.0:8000"]

# docker run myapp app.other:app -w 2  <-- CMD заменяется
```

### Когда что

- **CMD:** обычные приложения (веб-серверы, боты, API)
- **ENTRYPOINT:** CLI-инструменты, обёртки (entrypoint.sh), контейнеры-утилиты
- **ENTRYPOINT + CMD:** гибкость с дефолтами (gunicorn + аргументы)

---

## 7. Оптимизация слоев

### Порядок инструкций (от редко к часто меняемым)

```dockerfile
FROM python:3.13-slim-bookworm        # 1. Base image (редко)
WORKDIR /app                           # 2. Рабочая папка (никогда)
RUN apt-get update && apt-get install -y curl  # 3. Системные пакеты (редко)
COPY requirements.txt .               # 4. Зависимости (иногда)
RUN pip install -r requirements.txt    # 5. Установка зависимостей
COPY . .                              # 6. Исходный код (часто!)
```

Каждый слой кэшируется. Если слой 4 не изменился, Docker переиспользует кэш слоёв 1-5 и пересобирает только 6.

### Объединение RUN

```dockerfile
# ПЛОХО -- 3 слоя, apt cache остаётся
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ХОРОШО -- 1 слой, apt cache удалён
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

### .dockerignore (обязателен!)

Без `.dockerignore` весь контекст (включая `.git`, `node_modules`, `.env`) отправляется демону:

```dockerignore
.git
.env
*.env
node_modules
__pycache__
.venv
*.md
Dockerfile*
compose*.yaml
.dockerignore
*.log
*.pem
*.key
```

### Multi-stage для production

Зависимости сборки (gcc, make, dev-пакеты) остаются в builder-стадии и не попадают в production-образ. Это уменьшает размер в 3-10x и сокращает количество CVE.

### Сканирование образа

После сборки проверь образ на уязвимости:

```bash
docker scout quickview myapp:latest      # обзор
docker scout cves --epss myapp:latest    # CVE с вероятностью эксплуатации
docker scout recommendations myapp       # рекомендации по обновлению base image
```

---

## 8. Пример: Booking API для туризма ОАЭ

Полный production-ready Dockerfile для FastAPI booking API (экскурсии, билеты в парки Дубая и Абу-Даби).

```dockerfile
# =============================================================================
# Dockerfile -- Booking API для туризма ОАЭ
# Python 3.13 | FastAPI | Gunicorn | Multi-stage
# Docker Engine 29.x | Февраль 2026
# =============================================================================

# --- Stage 1: Builder ---
FROM python:3.13-slim-bookworm AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Виртуальное окружение для чистого копирования
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Зависимости (кэшируются если requirements.txt не изменился)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Production ---
FROM python:3.13-slim-bookworm

# Аргументы для гибкости (UID/GID)
ARG UID=1001
ARG GID=1001

# Non-root пользователь
RUN addgroup --system --gid ${GID} app && \
    adduser --system --uid ${UID} --ingroup app app

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Переменные приложения (специфичные для ОАЭ)
ENV TOURS_CURRENCY=AED \
    DEFAULT_LANGUAGE=ru \
    PORT=8000

# Исходный код
COPY --chown=app:app . .

USER app
EXPOSE ${PORT}

# Healthcheck для depends_on: condition: service_healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Gunicorn + Uvicorn workers для production
CMD ["gunicorn", "app.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-"]
```

**Что здесь применено:**
- Multi-stage build (builder + production)
- Non-root user с настраиваемым UID/GID
- Cache mount для pip
- HEALTHCHECK для интеграции с Compose depends_on
- Venv для чистого копирования зависимостей
- Переменные окружения для бизнес-логики (валюта AED, язык RU)
- Exec form CMD (PID 1 = gunicorn, получает SIGTERM)
