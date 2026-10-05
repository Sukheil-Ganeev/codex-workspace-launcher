# Telegram Bot - Voice Transcription

Production-ready Telegram бот для транскрипции голосовых сообщений через Yandex SpeechKit.

## Описание

Бот для туристического бизнеса в ОАЭ, который автоматически транскрибирует голосовые сообщения от клиентов и агентов.

### Основные возможности

- Автоматическая транскрипция голосовых сообщений
- Поддержка русского, английского, арабского
- Сохранение истории транскрипций
- Статистика использования
- Docker-ready для деплоя на сервер
- Webhook и Long Polling режимы

### Реальный кейс

**Ситуация:** У вас 3 турагента отправляют по 20 голосовых в день с запросами клиентов.

**Решение:** Бот автоматически транскрибирует все сообщения, вы читаете текст и быстро отвечаете.

## Установка

### Локальная установка

```bash
cd C:/Users/londo/.claude/skills/giga-transcribe-туризм/assets/examples/telegram-bot-integration

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### Docker установка

```bash
# Сборка образа
docker-compose build

# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## Конфигурация

### 1. Создайте Telegram бота

Откройте [@BotFather](https://t.me/BotFather) в Telegram:

```
/newbot
# Введите имя: Tourism Voice Transcriber
# Введите username: your_tourism_bot

# Получите токен: 7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

### 2. Настройте .env

```bash
cp .env.example .env
```

Заполните:

```env
# Telegram
TELEGRAM_BOT_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw

# Yandex SpeechKit
YANDEX_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_FOLDER_ID=b1gxxxxxxxxxxxxxxxxx

# Режим работы
BOT_MODE=polling  # или webhook

# Webhook (опционально)
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PORT=8443

# Администраторы (Telegram user IDs)
ADMIN_IDS=123456789,987654321
```

### 3. Получите ваш Telegram User ID

Откройте [@userinfobot](https://t.me/userinfobot) и скопируйте ваш ID в `ADMIN_IDS`.

## Использование

### Запуск бота

**Long Polling (для разработки):**

```bash
python main.py
```

**Webhook (для production):**

```bash
python main.py --webhook
```

**Docker:**

```bash
docker-compose up -d
```

### Команды бота

В Telegram отправьте боту:

- `/start` - Начало работы
- `/help` - Справка
- `/stats` - Ваша статистика
- `/language` - Выбор языка (ru/en/ar)
- `/admin` - Админ панель (только для администраторов)

### Отправка голосовых

1. Откройте чат с ботом
2. Запишите голосовое сообщение (кнопка микрофона)
3. Бот автоматически транскрибирует и отправит текст

## Архитектура

```
telegram-bot-integration/
├── main.py                 # Точка входа
├── bot/
│   ├── __init__.py
│   ├── handlers.py         # Обработчики команд и сообщений
│   ├── transcriber.py      # Интеграция с SpeechKit
│   ├── database.py         # SQLite для хранения истории
│   └── utils.py            # Вспомогательные функции
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Деплой на сервер

### 1. VPS с Docker

```bash
# На сервере
git clone your-repo
cd telegram-bot-integration

# Настроить .env
nano .env

# Запустить
docker-compose up -d

# Проверить логи
docker-compose logs -f
```

### 2. Webhook настройка

Для production рекомендуется webhook через Nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Systemd service

Альтернатива Docker - systemd:

```ini
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Voice Transcription Bot
After=network.target

[Service]
Type=simple
User=telegram-bot
WorkingDirectory=/home/telegram-bot/telegram-bot-integration
Environment="PATH=/home/telegram-bot/venv/bin"
ExecStart=/home/telegram-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## Функционал

### Для пользователей

- Отправка голосовых сообщений
- Получение транскрипций
- Выбор языка транскрипции
- Просмотр истории (последние 10)
- Личная статистика

### Для администраторов

- Просмотр общей статистики
- Список активных пользователей
- Управление доступом
- Экспорт данных
- Мониторинг ошибок

## API Endpoints (Webhook режим)

```
POST /webhook
  - Получение обновлений от Telegram

GET /health
  - Проверка работоспособности

GET /stats
  - Статистика бота (только для админов)
```

## База данных

SQLite схема:

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    language TEXT DEFAULT 'ru-RU',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    file_id TEXT,
    duration INTEGER,
    transcription TEXT,
    confidence REAL,
    language TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE usage_stats (
    user_id INTEGER,
    date DATE,
    messages_count INTEGER DEFAULT 0,
    total_duration INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## Мониторинг

### Логи

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u telegram-bot -f

# Файл
tail -f logs/bot.log
```

### Метрики

Бот логирует:
- Количество обработанных сообщений
- Время транскрипции
- Ошибки API
- Статистика по пользователям

## Стоимость

Yandex SpeechKit:
- 0.2₽/минута для коротких аудио

Примеры:
- 100 голосовых по 30 сек/день = 50 мин = 10₽/день = 300₽/месяц
- 500 голосовых по 20 сек/день = 167 мин = 33₽/день = 1000₽/месяц

## Безопасность

### Рекомендации

1. Используйте webhook через HTTPS
2. Ограничьте доступ через `ADMIN_IDS`
3. Регулярно обновляйте зависимости
4. Храните .env в безопасности (не коммитьте в git)
5. Используйте rate limiting для API

### Rate Limiting

В `bot/handlers.py` включен rate limiter:

```python
# Максимум 10 голосовых в минуту на пользователя
@rate_limit(max_calls=10, period=60)
def handle_voice(update, context):
    ...
```

## Troubleshooting

### Бот не отвечает

```bash
# Проверить статус
docker-compose ps

# Проверить логи
docker-compose logs bot

# Перезапустить
docker-compose restart bot
```

### Ошибка транскрипции

```
Error: Invalid API key
```

**Решение:** Проверьте `YANDEX_API_KEY` в .env

### Webhook не работает

```
Error: Webhook failed
```

**Решение:**
- Проверьте HTTPS сертификат
- Убедитесь что порт 8443 открыт
- Проверьте `WEBHOOK_URL` в .env

## Расширения

### Интеграция с CRM

```python
# В bot/handlers.py
async def handle_voice(update, context):
    transcription = await transcribe_voice(...)

    # Отправить в CRM
    await send_to_crm(
        user_id=update.effective_user.id,
        message=transcription['text']
    )
```

### Автоответы

```python
# Интеграция с Claude API
if any(keyword in text.lower() for keyword in ['экскурсия', 'цена']):
    response = await claude_api.complete(
        prompt=f"Ответь на запрос клиента: {text}"
    )
    await update.message.reply_text(response)
```

## Поддержка

При проблемах:
1. Проверьте логи
2. Убедитесь что все env переменные установлены
3. Проверьте баланс Yandex Cloud
4. Проверьте что бот не заблокирован в Telegram

## Лицензия

MIT License - свободное использование для бизнеса.
