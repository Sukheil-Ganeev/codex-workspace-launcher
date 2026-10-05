# Deploy -- Развёртывание и инфраструктура

> Справочник по развёртыванию VoiceTranscriptionBot (v6.1.0)
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Файлы: `docs/ORACLE_DEPLOY.md`, `scripts/*.service`, `scripts/*.bat`, `scripts/nginx_whatsapp.conf`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/`

---

## Oracle Cloud ARM Free Tier

### Always Free ресурсы (бессрочно $0)

| Ресурс | Лимит |
|--------|-------|
| CPU | 4 ARM Ampere A1 ядра |
| RAM | 24 GB |
| Disk | 200 GB (50 GB для boot volume) |
| Traffic | 10 TB/месяц |
| Region | me-dubai-1 (Dubai, UAE) |

### Настройка VM

- **Имя:** `voice-bot`
- **Image:** Ubuntu 22.04 или 24.04
- **Shape:** VM.Standard.A1.Flex (Ampere ARM)
- **OCPU:** 4
- **Memory:** 24 GB

### Системные зависимости

```bash
sudo apt install -y python3 python3-pip python3-venv git ffmpeg
```

### ARM-специфика для STT

На ARM нет GPU. Два варианта:

| Вариант | Описание | Рекомендация |
|---------|----------|--------------|
| A | faster-whisper на CPU (model `small`/`medium`) | Медленно: 30-60s на минуту аудио |
| **B (рекомендуется)** | Groq API only (`FORCE_GROQ_STT=true`) | Быстро, бесплатно, без нагрузки CPU |

### Firewall

| Бот | Порт | Причина |
|-----|------|---------|
| Telegram (long polling) | Нет | Исходящие подключения |
| WhatsApp (webhook) | **443** | HTTPS через nginx |

---

## systemd Units

### voice_bot.service (Telegram Bot)

**Файл:** `scripts/voice_bot.service`

```ini
[Unit]
Description=Voice Transcription Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/VoiceTranscriptionBot
ExecStart=/home/ubuntu/VoiceTranscriptionBot/venv/bin/python -m bot.main
Restart=always
RestartSec=10
EnvironmentFile=/home/ubuntu/VoiceTranscriptionBot/.env

[Install]
WantedBy=multi-user.target
```

| Параметр | Значение | Описание |
|----------|----------|----------|
| `Restart` | always | Перезапуск при любом выходе |
| `RestartSec` | 10 | 10 секунд задержки |
| `User` | ubuntu | Непривилегированный пользователь |
| `EnvironmentFile` | .env | Загрузка переменных окружения |

### whatsapp_bot.service (WhatsApp Bot)

**Файл:** `scripts/whatsapp_bot.service`

```ini
[Unit]
Description=WhatsApp Voice Transcription Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/VoiceTranscriptionBot
ExecStart=/home/ubuntu/VoiceTranscriptionBot/venv/bin/python -m whatsapp.app
Restart=always
RestartSec=5
EnvironmentFile=/home/ubuntu/VoiceTranscriptionBot/.env

[Install]
WantedBy=multi-user.target
```

**Отличие:** `RestartSec=5` (быстрее для WhatsApp -- webhook должен отвечать быстро).

### admin_bot.service (Admin Bot, v5.0.0)

**Файл:** `scripts/admin_bot.service` (аналогичная структура)

```ini
ExecStart=/home/ubuntu/VoiceTranscriptionBot/venv/bin/python -m admin.main
```

### Установка (3 сервиса)

```bash
sudo cp scripts/voice_bot.service /etc/systemd/system/
sudo cp scripts/whatsapp_bot.service /etc/systemd/system/
sudo cp scripts/admin_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable voice_bot whatsapp_bot admin_bot
sudo systemctl start voice_bot whatsapp_bot admin_bot
```

### Управление

```bash
# Статус
sudo systemctl status voice_bot
sudo systemctl status whatsapp_bot

# Логи
sudo journalctl -u voice_bot -f
sudo journalctl -u whatsapp_bot -f

# Перезапуск
sudo systemctl restart voice_bot
sudo systemctl restart whatsapp_bot

# Остановка
sudo systemctl stop voice_bot whatsapp_bot
```

---

## nginx Reverse Proxy

**Файл:** `scripts/nginx_whatsapp.conf`

```nginx
server {
    listen 443 ssl;
    server_name wa-bot.example.com;

    ssl_certificate /etc/letsencrypt/live/wa-bot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wa-bot.example.com/privkey.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Hub-Signature-256 $http_x_hub_signature_256;

        # Rate limiting
        limit_req zone=webhook burst=10 nodelay;
    }

    location / {
        return 404;
    }
}

# В http блоке nginx.conf:
# limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;
```

### Ключевые особенности

| Элемент | Описание |
|---------|----------|
| SSL termination | Let's Encrypt сертификаты |
| Только `/webhook` | Все остальные пути -> 404 |
| X-Hub-Signature-256 | КРИТИЧНО: заголовок проксируется для HMAC |
| Rate limiting | 10 req/s, burst 10 |
| Proxy to localhost | FastAPI не доступен извне напрямую |

### SSL Setup (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d wa-bot.example.com
```

---

## Launch Scripts (Windows .bat)

### start_telegram.bat

```batch
@echo off
chcp 65001 >nul
echo Starting Telegram bot...
cd /d D:\Downloads\VoiceTranscriptionBot
python -m bot.main
pause
```

### start_whatsapp.bat

```batch
@echo off
chcp 65001 >nul
echo Starting WhatsApp Voice Bot...
cd /d D:\Downloads\VoiceTranscriptionBot
python -m whatsapp.app
pause
```

### start_both.bat

```batch
@echo off
chcp 65001 >nul
echo Starting Telegram + WhatsApp bots...
cd /d D:\Downloads\VoiceTranscriptionBot
start "Telegram Bot" cmd /c "python -m bot.main"
timeout /t 3 >nul
start "WhatsApp Bot" cmd /c "python -m whatsapp.app"
echo Both bots started in separate windows.
pause
```

**Особенности:**
- `chcp 65001` -- UTF-8 для Cyrillic
- Каждый бот в отдельном окне (`start "Title" cmd /c`)
- 3 секунды задержки между стартами
- `pause` -- окно остаётся открытым при краше

---

## requirements.txt vs requirements-server.txt

### requirements.txt (Полная -- ноутбук с GPU)

| Пакет | Версия | Назначение |
|-------|--------|-----------|
| `aiogram` | >= 3.25.0 | Telegram бот |
| `groq` | >= 1.0.0 | Groq API (STT + LLM fallback) |
| `google-genai` | >= 1.0.0 | Google Gemini API (LLM primary) |
| `aiosqlite` | >= 0.22.0 | Async SQLite |
| `faster-whisper` | >= 1.2.0 | **Локальный GPU STT** |
| `fastapi` | >= 0.115.0 | WhatsApp webhook |
| `uvicorn[standard]` | >= 0.34.0 | ASGI server |
| `httpx` | >= 0.28.0 | Async HTTP (WhatsApp API) |
| `fpdf2` | >= 2.8.0 | PDF с Cyrillic |
| `openpyxl` | >= 3.1.0 | Excel |
| `yt-dlp` | >= 2026.2.4 | Видео скачивание |
| `google-auth` | >= 2.0.0 | Google Drive auth |

### requirements-server.txt (Сервер -- без GPU)

**Тот же список, но без `faster-whisper`.**

Используется с `FORCE_GROQ_STT=true` для cloud-only STT.

### Когда какой использовать

| Окружение | Файл | FORCE_GROQ_STT |
|-----------|------|----------------|
| Windows + NVIDIA GPU | `requirements.txt` | `false` |
| Oracle Cloud ARM | `requirements-server.txt` | `true` |
| Любой сервер без GPU | `requirements-server.txt` | `true` |
| CI/CD | `requirements-server.txt` | `true` |

---

## FORCE_GROQ_STT для серверного развёртывания

### Назначение

На сервере без GPU локальная модель faster-whisper:
- Работает только на CPU (очень медленно)
- Модель `large-v3` на CPU: 30-60 секунд на минуту аудио
- Потребляет много RAM и CPU

**Решение:** `FORCE_GROQ_STT=true` -- всё STT через Groq API (быстро, бесплатно).

### Настройка в .env

```
FORCE_GROQ_STT=true
```

### Как работает (v6.1.0)

При `FORCE_GROQ_STT=true`:
1. `bot/transcriber.py` полностью пропускает инициализацию faster-whisper
2. Все аудио отправляются в Groq API (модель whisper-large-v3-turbo)
3. LLM-вызовы (резюме, коррекция, категоризация) идут через `core/llm_client.py`:
   - Primary: Gemini 2.5-flash (облачный, не требует GPU)
   - Fallback: Groq Llama
4. Semaphore Groq: 5 параллельных запросов (STT + LLM делят лимит)

### Настройка в systemd

`EnvironmentFile` автоматически подтягивает `.env`.

---

## Полный процесс развёртывания на Oracle Cloud

### 1. Создание VM

1. Oracle Cloud Console -> Compute -> Instances -> Create
2. Image: Ubuntu 24.04
3. Shape: VM.Standard.A1.Flex, 4 OCPU, 24 GB RAM
4. SSH key: добавить публичный ключ

### 2. Подготовка сервера

```bash
ssh ubuntu@<public-ip>

# Обновление системы
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git ffmpeg nginx

# Клонирование проекта
cd ~
git clone <repo-url> VoiceTranscriptionBot
cd VoiceTranscriptionBot

# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-server.txt
```

### 3. Конфигурация

```bash
# Создать .env
cp .env.example .env
nano .env
# Заполнить все переменные, включая FORCE_GROQ_STT=true
```

### 4. Установка systemd units

```bash
sudo cp scripts/voice_bot.service /etc/systemd/system/
sudo cp scripts/whatsapp_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable voice_bot whatsapp_bot
```

### 5. Настройка nginx (для WhatsApp)

```bash
sudo cp scripts/nginx_whatsapp.conf /etc/nginx/sites-available/whatsapp
sudo ln -s /etc/nginx/sites-available/whatsapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL

```bash
sudo certbot --nginx -d wa-bot.example.com
```

### 7. Firewall (Oracle Cloud)

В Oracle Cloud Console -> Networking -> Security Lists:
- Добавить Ingress Rule: TCP port 443 from 0.0.0.0/0

### 8. Запуск

```bash
sudo systemctl start voice_bot whatsapp_bot
sudo systemctl status voice_bot whatsapp_bot
```

---

## Архитектура процессов

```
[systemd: voice_bot.service]      -- Telegram bot (aiogram, long polling) + healthcheck :8081
[systemd: whatsapp_bot.service]   -- WhatsApp bot (FastAPI, webhook :8000)
[systemd: admin_bot.service]      -- Admin bot (aiogram, polling) + healthcheck :8082

Все 3 разделяют:
  - core/ (Transcriber, Summarizer, Database, etc.)
  - data/transcriptions.db
  - .env

nginx :443 -> proxy_pass -> FastAPI :8000 (/webhook only)
Альтернатива nginx: Cloudflare Tunnel -> :8000
```

---

## Data Files (на сервере)

| Файл | Формат | Назначение |
|------|--------|-----------|
| `data/transcriptions.db` | SQLite | Основная БД (авто-создание) |
| `data/clients.json` | JSON | База клиентов |
| `data/pending_approvals.json` | JSON | Запросы на подтверждение |
| `data/team.json` | JSON | Профили команды |
| `data/prices.json` | JSON | Прайс-лист |
| `data/templates.json` | JSON | Шаблоны ответов |
| `data/lessons.json` | JSON | Уроки бота |
| `data/fonts/` | TTF | DejaVu шрифты для PDF |

---

## Мониторинг

### Health check

- **Telegram:** `/health` команда + healthcheck endpoint на порту **8081** (`core/health.py`)
- **WhatsApp:** `GET /health` endpoint (порт 8000)
- **Admin:** healthcheck endpoint на порту **8082** (`core/health.py`)
- Показывает: размер БД, кол-во записей, temp файлы, pending approvals

### Логи

```bash
# Telegram bot
sudo journalctl -u voice_bot -f --no-pager

# WhatsApp bot
sudo journalctl -u whatsapp_bot -f --no-pager

# Admin bot
sudo journalctl -u admin_bot -f --no-pager

# nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Ротация логов (v6.0.0)

**Файл:** `core/logging_config.py`

- `RotatingFileHandler`, JSON-формат
- 10 MB x 5 файлов
- Санитайзер API-ключей через `core/log_sanitizer.py`

### Автобэкапы БД (v6.0.0)

**Файл:** `core/backup.py`

- Ежедневно в 04:00
- Ротация: 7 дней
- `scripts/backup_db.sh` (Linux), `scripts/backup_db.bat` (Windows)

---

## Docker (v6.0.0+)

### Dockerfile

**Файл:** `Dockerfile` -- multi-stage build, Python 3.13

```dockerfile
# Stage 1: builder
FROM python:3.13-slim AS builder
WORKDIR /build
COPY requirements-server.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-server.txt

# Stage 2: runtime
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
```

**Ключевые особенности multi-stage build:**
- Builder stage компилирует зависимости, runtime stage копирует только результат
- Используется `requirements-server.txt` (без faster-whisper, без GPU-зависимостей)
- Финальный образ существенно меньше за счёт отсутствия build tools
- `FORCE_GROQ_STT=true` в `.env` -- обязательно для Docker (нет GPU)

### docker-compose.yml

**Файл:** `docker-compose.yml` -- 3 сервиса

```yaml
services:
  telegram:
    build: .
    command: python -m bot.main
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./temp:/app/temp
    ports:
      - "8081:8081"    # healthcheck
    restart: unless-stopped

  whatsapp:
    build: .
    command: python -m whatsapp.app
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./temp:/app/temp
    ports:
      - "8000:8000"    # webhook
    restart: unless-stopped

  admin:
    build: .
    command: python -m admin.main
    env_file: .env
    volumes:
      - ./data:/app/data
      - ./temp:/app/temp
    ports:
      - "8082:8082"    # healthcheck
    restart: unless-stopped
```

**Healthcheck порты:**

| Сервис | Порт | Endpoint | Описание |
|--------|------|----------|----------|
| Telegram | 8081 | `GET /health` | Размер БД, записи, temp, pending approvals |
| WhatsApp | 8000 | `GET /health` | FastAPI встроенный health + метрики |
| Admin | 8082 | `GET /health` | Аналогично Telegram |

### Запуск

```bash
docker compose up -d             # Запуск всех 3
docker compose logs -f           # Логи
docker compose restart telegram  # Перезапуск одного
docker compose down              # Остановка всех
```

---

## Cloudflare Tunnel (v6.0.0)

Замена ngrok для постоянного webhook URL без открытия портов.

**Документация:** `docs/CLOUDFLARE_TUNNEL.md`

### Преимущества

- Постоянный URL (не меняется при перезапуске)
- Бесплатно
- Не требует открытия порта 443
- Автоматический SSL

### Настройка

```bash
# Установка
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Логин и создание туннеля
cloudflared tunnel login
cloudflared tunnel create voicebot

# Конфигурация (~/.cloudflared/config.yml)
tunnel: <TUNNEL_ID>
credentials-file: /home/ubuntu/.cloudflared/<TUNNEL_ID>.json
ingress:
  - hostname: webhook.vipdxbrus.com
    service: http://localhost:8000
  - service: http_status:404
```

### Скрипты

- `scripts/start_tunnel.sh` -- Linux
- `scripts/start_tunnel.bat` -- Windows

---

## CI/CD GitHub Actions (v6.0.0)

### Автотесты

**Файл:** `.github/workflows/tests.yml`

- Запускается при каждом push и PR
- Python 3.13
- `pip install -r requirements-server.txt`
- `pytest` (~2138 тестов)

### Линтинг

**Файл:** `.github/workflows/lint.yml`

- Запускается при каждом push и PR
- Проверка стиля кода

---

## API Monitor (v6.0.0)

**Файл:** `core/api_monitor.py`

Трекинг расхода API-токенов с лимитами и алертами:
- Gemini API
- Groq API
- Google Maps API
- Google Vision API
