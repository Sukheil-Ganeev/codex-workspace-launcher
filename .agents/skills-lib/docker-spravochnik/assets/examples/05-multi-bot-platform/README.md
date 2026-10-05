# 05-multi-bot-platform -- Мульти-бот платформа (Telegram + WhatsApp)

Полная платформа из нескольких ботов для туристического бизнеса ОАЭ.
Каждый бот -- отдельный контейнер, общая БД и кэш.

## Архитектура

```
                    Internet
                       |
                   [ Nginx ]          -- reverse proxy (webhook)
                   /        \
        [ Telegram Bot ]   [ WhatsApp Bot ]
          (polling)          (webhook :8000)
                   \        /
                [ PostgreSQL ]        -- общая БД
                   [ Redis ]          -- кэш и очереди
```

## Быстрый запуск

```bash
# 1. Скопируй переменные окружения
cp .env.example .env
# Заполни TELEGRAM_BOT_TOKEN, WHATSAPP_TOKEN и другие

# 2. Запусти стек
docker compose up -d --wait

# 3. Проверь работу
curl http://localhost/health            # nginx
curl http://localhost/webhook           # whatsapp webhook verify (403 без параметров)
```

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| nginx | 80, 443 | Reverse proxy для webhook |
| telegram-bot | 8081 (internal) | Telegram polling бот (aiogram) |
| whatsapp-bot | 8000 (internal) | WhatsApp webhook (FastAPI) |
| db | 5432 (internal) | PostgreSQL 17 |
| redis | 6379 (internal) | Redis 7 (кэш + очереди) |

## Сети

- **frontend** -- nginx + whatsapp-bot (доступ из интернета)
- **backend** (internal) -- все сервисы (изолирована от внешнего мира)

## Остановка

```bash
docker compose down      # остановка, данные сохраняются
docker compose down -v   # остановка + удаление данных
```

## Структура

```
05-multi-bot-platform/
  compose.yml                # Docker Compose стек (5 сервисов)
  .env.example               # Шаблон переменных окружения
  telegram-bot/
    Dockerfile               # Multi-stage Python 3.13
    bot.py                   # Telegram бот (aiogram)
    requirements.txt         # Зависимости
  whatsapp-bot/
    Dockerfile               # Multi-stage Python 3.13
    app.py                   # WhatsApp webhook (FastAPI)
    requirements.txt         # Зависимости
  nginx/
    nginx.conf               # Reverse proxy конфигурация
  README.md
```
