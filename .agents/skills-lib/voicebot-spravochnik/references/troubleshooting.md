# Troubleshooting -- Решение проблем

> Справочник по диагностике и решению проблем VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`

---

## STT не работает / ошибка транскрипции

### Симптомы

- "Ошибка распознавания голоса"
- Пустая транскрипция
- Долгая обработка (>30 секунд)

### Причина 1: GPU недоступен

**Диагностика:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Решение:**
1. Установить CUDA Toolkit и cuDNN
2. Или использовать облачный STT:
   ```
   # В .env:
   FORCE_GROQ_STT=true
   ```

### Причина 2: faster-whisper не установлен

**Диагностика:**
```bash
python -c "from faster_whisper import WhisperModel; print('OK')"
```

**Решение:**
```bash
pip install faster-whisper>=1.2.0
```

Или для сервера: `FORCE_GROQ_STT=true`

### Причина 3: Groq API key невалидный

**Диагностика:** В логах: `AuthenticationError` или `401`

**Решение:** Проверить `GROQ_API_KEY` в `.env`, получить новый на console.groq.com

### Причина 4: Groq rate limit

**Диагностика:** В логах: `RateLimitError` или `429`

**Решение:** Retry с backoff включён автоматически (3 попытки). Если постоянно -- уменьшить нагрузку или использовать локальный STT.

---

## Gemini rate limit / ошибки LLM

### Симптомы

- "Ошибка генерации резюме"
- `method="error"` в результатах
- Суммаризация пустая

### Причина 1: Rate limit Gemini API

**Диагностика:** В логах: `429 Resource Exhausted` или `ResourceExhausted`

**Решение:**
- Каскад автоматически переключается: gemini-2.5-flash -> gemini-2.0-flash -> gemini-2.0-flash-lite -> Groq Llama
- Если все упали -- результат safe fallback (method="error")
- При постоянных проблемах: проверить квоты на aistudio.google.com

### Причина 2: Невалидный API key

**Диагностика:** В логах: `InvalidArgument` или `PermissionDenied`

**Решение:** Проверить `GEMINI_API_KEY` в `.env`

### Причина 3: Groq тоже упал

**Диагностика:** Все 4 модели (3 Gemini + Groq) fail

**Решение:** Проверить интернет-подключение. Safe fallback вернёт `method="error"`, pipeline не крашится.

---

## WhatsApp webhook не принимает сообщения

### Причина 1: nginx не настроен

**Диагностика:**
```bash
sudo nginx -t
curl -v https://wa-bot.example.com/health
```

**Решение:**
```bash
sudo cp scripts/nginx_whatsapp.conf /etc/nginx/sites-available/whatsapp
sudo ln -s /etc/nginx/sites-available/whatsapp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### Причина 2: SSL сертификат

**Диагностика:**
```bash
sudo certbot certificates
```

**Решение:**
```bash
sudo certbot --nginx -d wa-bot.example.com
sudo certbot renew  # если истёк
```

### Причина 3: Meta verification не пройдена

**Диагностика:** Meta Developer Dashboard показывает webhook failed

**Решение:**
1. Проверить `WHATSAPP_VERIFY_TOKEN` в `.env` совпадает с Meta Dashboard
2. WhatsApp бот должен быть запущен: `sudo systemctl status whatsapp_bot`
3. Endpoint GET `/webhook` должен отвечать

### Причина 4: HMAC signature mismatch

**Диагностика:** В логах: `403 Invalid signature`

**Решение:**
1. Проверить `WHATSAPP_APP_SECRET` в `.env`
2. Убедиться что nginx проксирует `X-Hub-Signature-256`:
   ```nginx
   proxy_set_header X-Hub-Signature-256 $http_x_hub_signature_256;
   ```

### Причина 5: Port 443 заблокирован

**Диагностика:**
```bash
sudo netstat -tlnp | grep 443
# Или в Oracle Cloud Console: check Security Lists
```

**Решение:** Oracle Cloud Console -> Networking -> Security Lists -> Add Ingress Rule: TCP 443 from 0.0.0.0/0

### Причина 6: Телефон не в whitelist

**Диагностика:** В логах: `Phone ***XXXX not in whitelist`

**Решение:** Добавить телефон в `WHATSAPP_ALLOWED_PHONES` в `.env`:
```
WHATSAPP_ALLOWED_PHONES=971553096985,971501234567
```

---

## DB locked / database is locked

### Причина: Параллельный доступ

SQLite не поддерживает множественные параллельные записи.

**Диагностика:** В логах: `database is locked`

### Решение 1: Проверить что только 1 инстанс каждого бота запущен

```bash
ps aux | grep "bot.main"
ps aux | grep "whatsapp.app"
```

### Решение 2: VACUUM

```
/health
```

Если размер БД > 5MB и есть фрагментация:
```
/archive
```

Затем одобрить VACUUM request.

### Решение 3: WAL mode

SQLite по умолчанию использует WAL mode. Проверить:
```python
PRAGMA journal_mode;  # должен быть wal
```

---

## ModuleNotFoundError на сервере

### Симптомы

```
ModuleNotFoundError: No module named 'faster_whisper'
```

### Причина

На сервере установлен `requirements-server.txt` (без faster-whisper), но `FORCE_GROQ_STT` не включён.

### Решение

В `.env`:
```
FORCE_GROQ_STT=true
```

### Другие ModuleNotFoundError

| Модуль | Пакет | Команда |
|--------|-------|---------|
| `aiogram` | aiogram | `pip install aiogram>=3.25.0` |
| `groq` | groq | `pip install groq>=1.0.0` |
| `google.genai` | google-genai | `pip install google-genai>=1.0.0` |
| `aiosqlite` | aiosqlite | `pip install aiosqlite>=0.22.0` |
| `fastapi` | fastapi | `pip install fastapi>=0.115.0` |
| `httpx` | httpx | `pip install httpx>=0.28.0` |
| `fpdf2` | fpdf2 | `pip install fpdf2>=2.8.0` |
| `openpyxl` | openpyxl | `pip install openpyxl>=3.1.0` |
| `yt_dlp` | yt-dlp | `pip install yt-dlp>=2026.2.4` |

---

## Бот не отвечает в Telegram

### Причина 1: Бот не запущен

**Диагностика:**
```bash
# Сервер
sudo systemctl status voice_bot

# Windows
# Проверить окно cmd -- запущен ли процесс
```

### Причина 2: User не в whitelist

**Диагностика:** Бот молча игнорирует сообщения

**Решение:** Добавить user ID в `ALLOWED_USER_IDS`:
```
# Узнать свой ID: отправить сообщение @userinfobot
ALLOWED_USER_IDS=6905404901,5939002952
```

### Причина 3: Token невалидный

**Диагностика:** В логах: `Unauthorized` или `401`

**Решение:** Получить новый token у @BotFather

---

## PDF/Excel экспорт не работает

### Причина 1: Нет шрифтов DejaVu

**Диагностика:** Ошибка `Font not found`

**Решение:** Убедиться что `data/fonts/DejaVuSans*.ttf` существуют

### Причина 2: Нет данных за период

**Диагностика:** "Нет записей для экспорта"

**Решение:** Проверить наличие записей за выбранный период

### Причина 3: Temp директория

**Диагностика:** `PermissionError` или `FileNotFoundError`

**Решение:**
```bash
mkdir -p temp
chmod 755 temp
```

---

## Видео не скачивается

### Причина 1: yt-dlp устарел

**Диагностика:** Ошибки при скачивании YouTube

**Решение:**
```bash
pip install --upgrade yt-dlp
```

### Причина 2: FFmpeg не установлен

**Диагностика:** Ошибки при извлечении аудио (MP3)

**Решение:**
```bash
# Ubuntu
sudo apt install ffmpeg

# Windows
# Скачать ffmpeg.exe и добавить в PATH
```

### Причина 3: Видео приватное/геоблокировано

**Диагностика:** Сообщение "Видео приватное" или "заблокировано"

**Решение:** Нет решения -- ограничение платформы

---

## Чеки (receipts) не распознаются

### Причина 1: Нет Google Vision API key

**Диагностика:** OCR возвращает пустой текст

**Решение:**
```
GOOGLE_VISION_API_KEY=AIza...
```

### Причина 2: Плохое качество фото

**Решение:** Сфотографировать чек при хорошем освещении, четко, без бликов

### Причина 3: Gemini Vision не определяет как чек

**Диагностика:** `is_receipt: false` в ответе

**Решение:** Система автоматически fallback на OCR. Расход можно добавить вручную:
```
/add_expense 150 бензин ADNOC
```

---

## Дайджест не приходит автоматически

### Причина 1: Уведомления отключены

**Проверка:** `/settings`

**Решение:**
```
/settings notifications on
```

### Причина 2: Неправильное время

**Проверка:** `/settings`

**Решение:**
```
/settings digest_time 21:00
```

### Причина 3: Нет записей за день

Дайджест пропускается если нет голосовых сообщений.

### Причина 4: Фоновая задача упала

**Диагностика:** В логах проверить scheduler

**Решение:** Перезапуск бота:
```bash
sudo systemctl restart voice_bot
```

---

## Облачная загрузка видео не работает

### Причина 1: Токен не настроен

**Диагностика:** Облачная загрузка не предлагается

**Решение:** Настроить хотя бы один сервис:
```
YANDEX_DISK_TOKEN=y0_...
# или
GOOGLE_DRIVE_CREDENTIALS=data/google_credentials.json
```

### Причина 2: Хранилище заполнено

**Диагностика:** Ошибка 507

**Решение:** Очистить облачное хранилище или использовать другой сервис

---

## Общие советы по диагностике

### Проверка логов

```bash
# Telegram bot
sudo journalctl -u voice_bot -f --no-pager -n 100

# WhatsApp bot
sudo journalctl -u whatsapp_bot -f --no-pager -n 100

# Admin bot
sudo journalctl -u admin_bot -f --no-pager -n 100

# Ротируемые логи (v6.0.0)
ls -la logs/              # JSON-формат, 10MB x 5 файлов
```

### Health check

```
/health  (Telegram)
здоровье (WhatsApp)
GET /health (HTTP)
```

### Проверка всех сервисов

```bash
sudo systemctl status voice_bot whatsapp_bot admin_bot nginx
```

### Healthcheck endpoints (v6.0.0)

```bash
curl http://localhost:8081/health  # Telegram bot
curl http://localhost:8000/health  # WhatsApp bot
curl http://localhost:8082/health  # Admin bot
```

---

## Cloudflare Tunnel не работает

### Причина 1: cloudflared не запущен

**Диагностика:**
```bash
sudo systemctl status cloudflared
```

**Решение:**
```bash
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### Причина 2: Неправильная конфигурация

**Диагностика:** Проверить `~/.cloudflared/config.yml`

**Решение:**
```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/ubuntu/.cloudflared/<TUNNEL_ID>.json
ingress:
  - hostname: webhook.vipdxbrus.com
    service: http://localhost:8000
  - service: http_status:404
```

### Причина 3: DNS не настроен

**Диагностика:**
```bash
dig webhook.vipdxbrus.com
```

**Решение:**
```bash
cloudflared tunnel route dns <TUNNEL_NAME> webhook.vipdxbrus.com
```

### Причина 4: Meta webhook URL не обновлён

**Решение:** В Meta Developer Dashboard обновить Webhook URL на `https://webhook.vipdxbrus.com/webhook`

---

## Админ-бот не работает

### Причина 1: Токен не настроен

**Диагностика:** В логах: `ADMIN_BOT_TOKEN is not set`

**Решение:** Добавить в `.env`:
```
ADMIN_BOT_TOKEN=7123456789:BBH...
ADMIN_USER_IDS=6905404901
```

### Причина 2: Сервис не запущен

**Решение:**
```bash
# Сервер
sudo systemctl start admin_bot
sudo systemctl status admin_bot

# Windows
scripts\start_admin.bat
```

### Причина 3: Конфликт портов healthcheck

**Диагностика:** `Address already in use: port 8082`

**Решение:** Убедиться что только один экземпляр admin_bot запущен:
```bash
ps aux | grep "admin.main"
```

---

## Docker контейнеры не стартуют

### Причина 1: .env файл отсутствует

**Диагностика:**
```bash
docker-compose logs telegram
```

**Решение:** Создать `.env` в корне проекта со всеми обязательными переменными

### Причина 2: Порты заняты

**Диагностика:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Решение:**
```bash
docker-compose down
# Остановить конфликтующие процессы
docker-compose up -d
```
