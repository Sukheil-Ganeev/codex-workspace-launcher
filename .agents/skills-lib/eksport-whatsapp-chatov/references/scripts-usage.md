# Скрипты: подробные инструкции и примеры

Все скрипты с командами, параметрами, API ключами и примерами использования.

---

## AI И АВТОМАТИЗАЦИЯ

| Скрипт | Назначение | API |
|--------|------------|-----|
| `claude_classifier.py` | Классификация сообщений и намерений | Claude API |
| `auto_responder.py` | Автоответы на частые вопросы | - |
| `sentiment_analysis.py` | Анализ настроения сообщений | Claude/Rules |
| `auto_followup.py` | Автоматические напоминания и follow-up | - |

### Использование Claude Classifier

```bash
# Классификация одного сообщения
python scripts/claude_classifier.py --text "Сколько стоит экскурсия в Абу-Даби?"

# Классификация всех сообщений контакта
python scripts/claude_classifier.py --contact "Anna"

# Определение намерения
python scripts/claude_classifier.py --intent "Хочу забронировать яхту на 10 человек"
```

### Auto Responder

```bash
# Запуск автоответчика
python scripts/auto_responder.py --mode watch

# Тестирование ответа
python scripts/auto_responder.py --test "Какие у вас есть экскурсии?"
```

### Sentiment Analysis

```bash
# Анализ настроения чата
python scripts/sentiment_analysis.py --chat "Anna_79614598181"

# Все чаты
python scripts/sentiment_analysis.py --all
```

---

## МЕДИА-ОБРАБОТКА

| Скрипт | Назначение | API |
|--------|------------|-----|
| `voice_transcriber.py` | Транскрибация голосовых сообщений | Whisper |
| `document_ocr.py` | OCR документов и изображений | Tesseract/Vision |
| `image_analyzer.py` | Анализ изображений (чеки, скриншоты) | Claude Vision |

### Voice Transcriber (Whisper)

```bash
# Транскрибация одного файла
python scripts/voice_transcriber.py audio.opus

# Все голосовые в папке
python scripts/voice_transcriber.py --folder "D:/Downloads/Anna_extracted/"

# С указанием языка
python scripts/voice_transcriber.py audio.opus --language ru
```

**Требования:** GPU: RTX 3060+ (6GB VRAM), CUDA 11.x+, модель `medium`

### Document OCR

```bash
# OCR одного документа
python scripts/document_ocr.py document.jpg

# PDF с OCR
python scripts/document_ocr.py scan.pdf

# Папка с документами
python scripts/document_ocr.py --folder "D:/Downloads/docs/"
```

**Поддерживаемые форматы:** JPG, PNG, PDF, TIFF

### Image Analyzer

```bash
# Анализ изображения
python scripts/image_analyzer.py screenshot.jpg

# Извлечение данных из чека
python scripts/image_analyzer.py receipt.jpg --type receipt

# Анализ скриншота курса валют
python scripts/image_analyzer.py rates.png --type exchange_rate
```

---

## АНАЛИТИКА И ОТЧЁТЫ

| Скрипт | Назначение |
|--------|------------|
| `dashboard.py` | Веб-дашборд Streamlit |
| `financial_reports.py` | P&L, Cash Flow отчёты |
| `demand_forecast.py` | ML прогнозирование спроса |

### Dashboard (Streamlit)

```bash
# Запуск дашборда
streamlit run scripts/dashboard.py

# С указанием порта
streamlit run scripts/dashboard.py --server.port 8080
```

**URL:** http://localhost:8501

**Вкладки дашборда:**
- Обзор: KPI, графики активности
- Контакты: таблица с фильтрами
- Операции: финансовая статистика
- Аналитика: воронка, сезонность

### Financial Reports

```bash
# P&L за месяц
python scripts/financial_reports.py --pnl --month 2026-01

# Cash Flow
python scripts/financial_reports.py --cashflow --month 2026-01

# Все отчёты
python scripts/financial_reports.py --all
```

**Выход:** `D:/Downloads/Chats/_аналитика/financial/`

### Demand Forecast

```bash
# Прогноз на месяц
python scripts/demand_forecast.py --predict 30

# Обучение модели
python scripts/demand_forecast.py --train

# Визуализация
python scripts/demand_forecast.py --visualize
```

---

## ИНТЕГРАЦИИ

| Модуль | API ключ (env) | Функции |
|--------|----------------|---------|
| `notion.py` | NOTION_API_KEY | Синхронизация контактов и операций |
| `google_sheets.py` | GOOGLE_SHEETS_CREDENTIALS | Экспорт в таблицы |
| `telegram_bot.py` | TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID | Уведомления |
| `calendar.py` | GOOGLE_CALENDAR_CREDENTIALS | События в календарь |

**Пример использования:**
```python
from integrations import TelegramBotIntegration

bot = TelegramBotIntegration()
if bot.connect():
    bot.notify_new_chat("Anna", "поставщик", 127)
```

### Telegram Bot

```bash
# Запуск бота
python scripts/telegram_bot.py

# Отправка уведомления
python scripts/telegram_bot.py --notify "Новый заказ от Anna"

# Тест соединения
python scripts/telegram_bot.py --test
```

### WhatsApp Cloud API

```bash
# Отправка сообщения
python scripts/whatsapp_api.py --send "+971501234567" "Текст сообщения"

# Отправка шаблона
python scripts/whatsapp_api.py --template "booking_confirmation" --to "+971501234567"

# Получение webhook
python scripts/whatsapp_api.py --webhook --port 5000
```

### Email Sync

```bash
# Синхронизация Gmail
python scripts/email_sync.py --gmail --sync

# Экспорт операций в email
python scripts/email_sync.py --export-report --to "manager@company.com"

# Отправка инвойса
python scripts/email_sync.py --send-invoice "INV-2026-001" --to "client@email.com"
```

---

## ДОКУМЕНТЫ

| Скрипт | Тип документа |
|--------|---------------|
| `invoice_generator.py` | PDF инвойсы |
| `contract_generator.py` | Договоры |
| `voucher_generator.py` | Ваучеры |

### Invoice Generator

```bash
# Создать инвойс
python scripts/invoice_generator.py --client "Anna" --items "Экскурсия Абу-Даби:2000 AED"

# Из JSON
python scripts/invoice_generator.py --from-json invoice_data.json

# Шаблон
python scripts/invoice_generator.py --template "premium"
```

**Выход:** `D:/Downloads/invoices/INV-2026-XXXX.pdf`

### Contract Generator

```bash
# Договор на услуги
python scripts/contract_generator.py --type service --client "Company LLC"

# Агентский договор
python scripts/contract_generator.py --type agency --partner "Travel Agent"
```

### Voucher Generator

```bash
# Ваучер на экскурсию
python scripts/voucher_generator.py --tour "Abu Dhabi City Tour" --client "John Smith" --date "2026-02-15"

# Групповой ваучер
python scripts/voucher_generator.py --tour "Desert Safari" --pax 10 --date "2026-02-20"
```

---

## ГЕОЛОКАЦИЯ И КАРТЫ

| Скрипт | Назначение |
|--------|------------|
| `client_heatmap.py` | Тепловая карта клиентов по странам |
| `pickup_optimizer.py` | TSP оптимизация маршрутов пикапа |
| `driver_routes.py` | Маршруты для водителей (Google Maps, Waze) |

### Особенности

- База 39+ отелей ОАЭ с координатами
- Deep links для Google Maps, Waze, Apple Maps
- Traffic-aware routing

### Использование

```bash
# Тепловая карта клиентов
python scripts/client_heatmap.py

# Оптимизация маршрута пикапа (TSP)
python scripts/pickup_optimizer.py --pickups "Hotel A, Hotel B, Hotel C"

# Генерация маршрута для водителя
python scripts/driver_routes.py --start "Dubai Marina" --stops "JBR, Palm Jumeirah, Atlantis"

# Deep links для навигации
python scripts/driver_routes.py --stops "..." --format google_maps
python scripts/driver_routes.py --stops "..." --format waze
python scripts/driver_routes.py --stops "..." --format apple_maps
```

---

## МАРКЕТИНГ

| Скрипт | Назначение |
|--------|------------|
| `instagram_parser.py` | Парсер Instagram конкурентов |
| `referral_program.py` | Реферальная программа с бонусами |
| `email_marketing.py` | Mailchimp/SendGrid интеграция |
| `sms_twilio.py` | SMS рассылки через Twilio |

### Особенности

- 3-уровневая реферальная система
- QR-коды для реферальных ссылок
- 6 SMS шаблонов на 3 языках

### Использование

```bash
# Парсинг Instagram конкурентов
python scripts/instagram_parser.py --account "competitor_account"

# Реферальная программа
python scripts/referral_program.py --create-link --referrer "Anna"
python scripts/referral_program.py --track --code "REF123"
python scripts/referral_program.py --generate-qr --code "REF123"

# Email маркетинг
python scripts/email_marketing.py --campaign "winter_promo" --list "active_clients"
python scripts/email_marketing.py --provider mailchimp --sync-contacts
python scripts/email_marketing.py --provider sendgrid --send-template "booking_confirmation"

# SMS рассылки через Twilio
python scripts/sms_twilio.py --template "booking_reminder" --to "+971501234567"
python scripts/sms_twilio.py --bulk --list "tomorrow_pickups" --template "pickup_reminder"
python scripts/sms_twilio.py --language ru  # ru, en, ar
```

### SMS шаблоны

| Шаблон | Описание | Языки |
|--------|----------|-------|
| `booking_confirmation` | Подтверждение бронирования | ru, en, ar |
| `booking_reminder` | Напоминание за день | ru, en, ar |
| `pickup_reminder` | Напоминание о пикапе | ru, en, ar |
| `payment_request` | Запрос оплаты | ru, en, ar |
| `review_request` | Запрос отзыва | ru, en, ar |
| `promo_offer` | Промо-предложение | ru, en, ar |

---

## ПАРТНЁРСТВА

| Скрипт | Назначение |
|--------|------------|
| `agent_portal.py` | Веб-портал для агентов (FastAPI) |
| `partner_api.py` | REST API для партнёров |
| `white_label.py` | White-label решение |

### Особенности

- JWT авторизация с 3 уровнями доступа
- Swagger документация API
- Генерация материалов с брендом агента

### Использование

```bash
# Запуск портала для агентов
python scripts/agent_portal.py --host 0.0.0.0 --port 8000

# REST API для партнёров
python scripts/partner_api.py --start
# Swagger UI: http://localhost:8000/docs

# White-label материалы
python scripts/white_label.py --agent "TravelPlus" --generate vouchers
python scripts/white_label.py --agent "TravelPlus" --generate invoices
python scripts/white_label.py --agent "TravelPlus" --generate catalog
```

### Уровни доступа

| Уровень | Права | Описание |
|---------|-------|----------|
| `viewer` | Только просмотр | Просмотр каталога, цен |
| `agent` | Бронирование | + создание заказов, комиссии |
| `admin` | Полный доступ | + управление пользователями, отчёты |

### API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/auth/login` | Получение JWT токена |
| `GET` | `/catalog/tours` | Список туров |
| `GET` | `/catalog/prices` | Актуальные цены |
| `POST` | `/bookings` | Создание бронирования |
| `GET` | `/bookings/{id}` | Статус бронирования |
| `GET` | `/reports/commission` | Отчёт по комиссиям |

---

## API КЛЮЧИ И НАСТРОЙКА

### Необходимые API ключи

| API | Переменная окружения | Как получить |
|-----|---------------------|--------------|
| **Claude API** | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) -> API Keys |
| **OpenAI Whisper** | `OPENAI_API_KEY` (опционально) | [platform.openai.com](https://platform.openai.com) -> API Keys |
| **Telegram Bot** | `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) -> /newbot |
| **Telegram Chat ID** | `TELEGRAM_CHAT_ID` | [@userinfobot](https://t.me/userinfobot) |
| **WhatsApp Cloud** | `WHATSAPP_TOKEN` | [developers.facebook.com](https://developers.facebook.com) -> WhatsApp |
| **WhatsApp Phone ID** | `WHATSAPP_PHONE_ID` | Meta Business Suite -> WhatsApp |
| **Google Sheets** | `GOOGLE_SHEETS_CREDENTIALS` | [console.cloud.google.com](https://console.cloud.google.com) -> APIs -> Sheets API |
| **Notion** | `NOTION_API_KEY` | [notion.so/my-integrations](https://www.notion.so/my-integrations) |
| **Airtable** | `AIRTABLE_API_KEY` | [airtable.com/account](https://airtable.com/account) -> API |

### Настройка .env файла

```bash
# C:/Users/londo/.claude/skills/экспорт-whatsapp-чатов/scripts/.env

# Claude API (обязательно для AI-функций)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Telegram (для уведомлений)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# WhatsApp Cloud API
WHATSAPP_TOKEN=EAAxxxxx
WHATSAPP_PHONE_ID=123456789012345

# Google Services
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json

# Notion
NOTION_API_KEY=secret_xxxxx

# Airtable
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
```

### Инструкции по получению ключей

#### Claude API (Anthropic)
1. Перейти на [console.anthropic.com](https://console.anthropic.com)
2. Зарегистрироваться / войти
3. Settings -> API Keys -> Create Key
4. Скопировать ключ `sk-ant-api03-...`

#### Telegram Bot
1. Открыть [@BotFather](https://t.me/BotFather) в Telegram
2. Отправить `/newbot`
3. Указать имя и username бота
4. Получить токен вида `123456:ABC-DEF...`
5. Для Chat ID: написать боту, затем открыть `https://api.telegram.org/bot<TOKEN>/getUpdates`

#### WhatsApp Cloud API
1. Создать Meta Business Account на [business.facebook.com](https://business.facebook.com)
2. Перейти в [developers.facebook.com](https://developers.facebook.com)
3. Создать приложение -> Business -> WhatsApp
4. WhatsApp -> Getting Started -> получить токен и Phone Number ID
5. Добавить тестовые номера в Whitelist

#### Google Sheets API
1. Перейти в [Google Cloud Console](https://console.cloud.google.com)
2. Создать проект
3. APIs & Services -> Enable APIs -> Google Sheets API
4. Credentials -> Create Credentials -> Service Account
5. Скачать JSON-файл credentials

#### Notion API
1. Перейти на [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. New Integration -> указать имя и workspace
3. Скопировать Internal Integration Token
4. В Notion: Share страницу/базу с интеграцией

#### Airtable API
1. Перейти на [airtable.com/account](https://airtable.com/account)
2. Generate API Key (или Personal Access Token)
3. Base ID можно найти в URL базы: `airtable.com/appXXXXXX/...`

### Проверка настройки

```bash
# Проверить все API ключи
python scripts/check_api_keys.py

# Проверить конкретный сервис
python scripts/check_api_keys.py --service telegram
python scripts/check_api_keys.py --service claude
```
