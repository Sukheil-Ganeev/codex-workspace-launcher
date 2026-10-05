---
name: туризм-оаэ-автоматизация
description: "AI, боты, рассылки, автоматизация туристического бизнеса ОАЭ. Claude классификация, автоответы, дашборды. Используй для автоматизации процессов."
---
# Туризм ОАЭ - Автоматизация

## Quick Start Guide (5 минут)

### 1. Установка зависимостей (1 мин)
```bash
pip install anthropic openai python-dotenv airtable-python-wrapper
```

### 2. Настройка переменных окружения (2 мин)
```bash
# Создайте файл .env в корне проекта
echo "ANTHROPIC_API_KEY=sk-ant-api03-..." > .env
echo "OPENAI_API_KEY=sk-..." >> .env
echo "AIRTABLE_API_KEY=pat..." >> .env
echo "AIRTABLE_BASE_ID=app..." >> .env
```

### 3. Тест классификации (1 мин)
```python
import anthropic
import json

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    system="Классифицируй сообщение как inquiry/booking/support/complaint. Верни JSON.",
    messages=[{"role": "user", "content": "Сколько стоит экскурсия в Абу-Даби?"}]
)
print(response.content[0].text)
# {"type": "inquiry", "intent": "price_request", "priority": "medium"}
```

### 4. Подключение make.com webhook (1 мин)
1. Создайте новый сценарий в make.com
2. Добавьте Webhook триггер
3. Скопируйте URL webhook
4. Настройте отправку сообщений на этот URL

### Готово!
Теперь входящие сообщения будут автоматически классифицироваться.

---

## Назначение

Полный инструментарий для автоматизации туристического бизнеса ОАЭ. AI-классификация сообщений, автоматические ответы, интеграция с make.com, обработка медиа (Whisper, OCR), визуализация и аналитика.

---

## Архитектура AI-агента

### Общая схема

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI-АГЕНТ ТУРИЗМА ОАЭ                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   WhatsApp ──┐                                                          │
│              │                                                          │
│   Telegram ──┼──► make.com ──► Claude API ──► Классификация             │
│              │        │              │              │                   │
│   Email ─────┘        │              │              │                   │
│                       │              │              ▼                   │
│                       │              │      ┌──────────────┐            │
│                       │              │      │   Airtable   │            │
│                       │              │      │   ─────────  │            │
│                       │              │      │  • Клиенты   │            │
│                       │              │      │  • Операции  │            │
│                       │              │      │  • Логи      │            │
│                       │              │      └──────────────┘            │
│                       │              │              │                   │
│                       │              ▼              │                   │
│                       │      ┌──────────────┐      │                   │
│                       │      │ Автоответ    │◄─────┘                   │
│                       │      │ генерация    │                          │
│                       │      └──────┬───────┘                          │
│                       │             │                                   │
│                       ▼             ▼                                   │
│               ┌─────────────────────────────┐                          │
│               │  Уведомления менеджерам     │                          │
│               │  (Telegram Bot / Email)     │                          │
│               └─────────────────────────────┘                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Компоненты системы

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **Оркестратор** | make.com | Координация потоков данных |
| **AI Engine** | Claude API | Классификация, генерация ответов |
| **База данных** | Airtable | Хранение клиентов, операций |
| **Транскрипция** | Whisper API | Голосовые → текст |
| **OCR** | Tesseract / Vision API | Документы → текст |
| **Уведомления** | Telegram Bot API | Алерты менеджерам |

### Поток данных

```
1. Входящее сообщение (WhatsApp/Telegram/Email)
         │
         ▼
2. make.com Webhook получает сообщение
         │
         ▼
3. Медиа-обработка (если есть):
   • Голосовое → Whisper → текст
   • Фото документа → OCR → текст
   • Локация → геокодинг → адрес
         │
         ▼
4. Claude API классифицирует:
   • Тип: inquiry/booking/support/complaint
   • Срочность: low/medium/high/critical
   • Язык: ru/en/ar
   • Намерение: конкретный запрос
         │
         ▼
5. Airtable обновляется:
   • Создание/обновление клиента
   • Логирование сообщения
   • Создание задачи (если нужно)
         │
         ▼
6. Генерация автоответа (если применимо)
         │
         ▼
7. Уведомление менеджеру (если требуется)
```

---

## Классификация сообщений

### Категории (type)

| Категория | Описание | Примеры | Автоответ |
|-----------|----------|---------|-----------|
| `inquiry` | Запрос информации | "Сколько стоит тур?", "Есть ли экскурсии?" | Да, прайс |
| `booking` | Бронирование | "Хочу забронировать", "Подтверждаю" | Да, форма |
| `support` | Поддержка | "Где водитель?", "Не могу найти" | Частично |
| `complaint` | Жалоба | "Недоволен", "Верните деньги" | Нет, менеджер |
| `spam` | Спам | Реклама, рассылки | Игнор |
| `other` | Прочее | Не относится к бизнесу | Нет |

### Подкатегории (subtype)

| Тип | Подтипы |
|-----|---------|
| `inquiry` | `price`, `availability`, `info`, `comparison` |
| `booking` | `new`, `modify`, `cancel`, `confirm` |
| `support` | `tracking`, `change`, `document`, `question` |
| `complaint` | `service`, `quality`, `timing`, `refund` |

### Срочность (priority)

| Уровень | Критерии | SLA ответа |
|---------|----------|------------|
| `critical` | VIP клиент, жалоба, срочный трансфер | 5 мин |
| `high` | Бронирование на сегодня/завтра | 15 мин |
| `medium` | Стандартный запрос | 1 час |
| `low` | Общий вопрос, информация | 4 часа |

### Намерения (intent)

```json
{
  "inquiry": [
    "price_request",      // Запрос цены
    "availability_check", // Проверка наличия
    "tour_info",          // Информация о туре
    "transfer_info",      // Информация о трансфере
    "visa_info",          // Информация о визе
    "hotel_info",         // Информация об отеле
    "comparison"          // Сравнение вариантов
  ],
  "booking": [
    "new_booking",        // Новое бронирование
    "modify_booking",     // Изменение брони
    "cancel_booking",     // Отмена брони
    "confirm_booking",    // Подтверждение
    "payment_query"       // Вопрос по оплате
  ],
  "support": [
    "driver_location",    // Где водитель?
    "pickup_change",      // Изменить пикап
    "document_request",   // Нужен документ
    "technical_issue",    // Техническая проблема
    "general_question"    // Общий вопрос
  ],
  "complaint": [
    "service_quality",    // Качество услуги
    "driver_behavior",    // Поведение водителя
    "timing_issue",       // Проблема с временем
    "refund_request",     // Запрос возврата
    "mismatch"            // Несоответствие
  ]
}
```

---

## Claude API для классификации

Классификатор использует Claude Sonnet с системным промптом, возвращающим структурированный JSON с type, subtype, priority, intent, language, sentiment, entities и confidence score. Поддерживает batch-обработку через AsyncAnthropic.

→ Подробнее: `references/classifier-prompt.md` -- полный системный промпт, примеры кода classify_message(), generate_auto_response(), classify_batch(), предиктивная аналитика, эскалация и fraud detection, RAG для FAQ.

---

## Скрипты

### ai/ -- Искусственный интеллект (7 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `claude_classifier.py` | message.json | classification.json | **Главный классификатор** -- определяет type, subtype, priority, intent |
| `sentiment_analysis.py` | message.json | sentiment.json | Анализ тональности: positive/neutral/negative |
| `summarize_dialog.py` | messages[].json | summary.json | Суммаризация диалога для менеджера |
| `auto_responder.py` | classification.json | response.json | Генерация автоматического ответа |
| `auto_followup.py` | client.json | followup.json | Генерация follow-up сообщений |
| `smart_analysis.py` | messages[].json | analysis.json | Глубокий анализ контекста клиента |
| `demand_forecast.py` | history.json | forecast.json | Прогноз спроса на услуги |

### marketing/ -- Маркетинг (4 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `referral_program.py` | client.json | referral_code.json | Генерация реферальных ссылок |
| `email_marketing.py` | template, contacts[] | sent_report.json | Массовая email рассылка |
| `sms_twilio.py` | template, phones[] | sent_report.json | SMS рассылка через Twilio |
| `instagram_parser.py` | profile_url | posts.json | Парсинг Instagram профилей |

### partners/ -- Партнёры (3 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `agent_portal.py` | agent_id | portal_data.json | Данные для агентского портала |
| `partner_api.py` | request.json | response.json | REST API для партнёров |
| `white_label.py` | config.json | branded_assets/ | Генерация white-label материалов |

### media/ -- Обработка медиа (5 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `organize_media.py` | media_folder/ | organized/ | Организация медиафайлов по датам |
| `voice_transcriber.py` | audio.ogg | transcription.json | Транскрипция через SpeechRecognition |
| `transcribe_whisper.py` | audio.* | transcription.json | **Whisper API** -- точная транскрипция |
| `document_ocr.py` | image.* / pdf | ocr_text.json | OCR документов (Tesseract/Vision) |
| `image_analyzer.py` | image.* | analysis.json | Анализ изображений (Claude Vision) |

### visualization/ -- Визуализация (3 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `dashboard.py` | data/*.json | dashboard.html | Интерактивный дашборд (Plotly) |
| `activity_heatmap.py` | messages.jsonl | heatmap.html | Тепловая карта активности |
| `financial_reports.py` | operations.json | reports/ | Финансовые отчёты (PDF, Excel) |

→ Подробнее: `references/scripts-reference.md`

---

## Интеграция с make.com

### Webhook сценарии

4 основных webhook сценария:

1. **WhatsApp Message Classification** -- входящее сообщение → медиа-обработка → Claude → Airtable → роутинг по приоритету
2. **Voice Message Transcription** -- загрузка аудио → Whisper API → возврат текста
3. **Auto Price Response** -- inquiry + price_request → поиск продукта в Airtable → Claude генерация → отправка в WhatsApp
4. **Complaint Alert** -- жалоба → история клиента → саммари → Telegram алерт менеджеру → задача в Airtable

### Обработка ошибок в make.com

| Ошибка | Симптомы | Решение |
|--------|---------|---------|
| **Timeout API** | Сценарий падает после 40 сек | Увеличить timeout до 60 сек, retry с backoff (1s, 2s, 4s) |
| **Rate limit Claude API** | Ошибка 429 | Batch API, очередь сообщений, max 50 req/min, кэш |
| **Webhook не отвечает** | WA/TG не получают ответы | Проверить SSL, healthcheck endpoint, firewall/CORS |
| **Airtable rate limit** | Ошибка 422 | Batch записи (до 10), delay 200ms, bulk update |

→ Подробнее: `references/make-webhooks.md` -- полные JSON конфигурации всех 4 сценариев, дашборд метрик.

---

## Медиа обработка

### Whisper транскрипция

```python
def transcribe_tourism_context(audio_path: str) -> dict:
    """Транскрипция с туристическим контекстом."""
    client = openai.OpenAI()

    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            prompt="Туризм ОАЭ: Дубай, Абу-Даби, сафари, яхты, "
                   "Бурдж Халифа, дирхамы AED, трансфер"
        )

    return {"text": transcript.text}
```

**Характеристики Whisper API:**
- Стоимость: $0.006 за минуту
- Лимит: 25 МБ на файл
- Поддержка: ru, en, ar и 90+ языков

**Сравнение Whisper vs SpeechKit:**

| Параметр | SpeechKit | Whisper |
|----------|-----------|---------|
| Русский | Отлично | Очень хорошо |
| Английский | Очень хорошо | Отлично |
| Streaming | Да | Нет |
| Стоимость | ~$0.01/мин | $0.006/мин |

> **Подробнее:** См. скилл `giga-transcribe-туризм` для полной документации.

### Yandex SpeechKit (для русского языка)

Для русскоязычных клиентов рекомендуется Yandex SpeechKit -- лучшее качество распознавания русской речи.

```python
def transcribe_hybrid(audio_path: str, client_language: str = "ru") -> dict:
    """
    Гибридная транскрипция: SpeechKit для русского, Whisper для остальных.
    """
    if client_language in ["ru", "kz", "by", "ua"]:
        text = transcribe_speechkit(audio_path, "ru-RU")
        return {"text": text, "source": "speechkit", "language": "ru-RU"}
    else:
        result = transcribe_voice(audio_path, client_language)
        return {"text": result["text"], "source": "whisper", "language": client_language}
```

### OCR документов

| Тип | Описание | Извлекаемые данные |
|-----|----------|-------------------|
| `bank_transfer` | Скриншот перевода | amount, currency, reference, date |
| `passport` | Паспорт | name, number (masked), nationality |
| `receipt` | Чек | total, items, date |
| `invoice` | Инвойс | number, amount, due_date |

OCR реализован через Claude Vision API (`document_ocr.py`), возвращает JSON с document_type, text, extracted_data и confidence.

### Анализ изображений

Классификация: receipt, bank_transfer, passport, attraction, hotel, vehicle, document, screenshot. Используется Claude Vision (`image_analyzer.py`).

→ Подробнее: `references/media-processing.md` -- полный код transcribe_voice(), transcribe_with_context(), transcribe_speechkit(), transcribe_hybrid(), ocr_document(), ocr_batch(), analyze_image(), classify_image(), парсинг банковских переводов, маскирование данных, организация медиа, дедупликация (phash), семантический поиск CLIP, VCF контакты, видео анализ, статистика по отправителям.

---

## AI Анализ и классификация

### Intent Classification (Классификация намерений)

| Intent | Описание | Примеры | Автоответ |
|--------|----------|---------|-----------|
| `price_inquiry` | Запрос цены | "Сколько стоит тур?" | Да, прайс |
| `booking_request` | Бронирование | "Хочу забронировать" | Да, форма |
| `complaint` | Жалоба | "Очень недоволен" | Нет, эскалация |
| `support` | Поддержка | "Где водитель?" | Частично |
| `payment_inquiry` | Оплата | "Куда перевести?" | Да, реквизиты |
| `cancellation` | Отмена | "Хочу отменить" | Нет, менеджер |

### Sentiment Analysis (Анализ тональности)

| Уровень | Значение | Действие |
|---------|----------|----------|
| 5 | Восторг | Запросить отзыв |
| 4 | Позитив | Стандартное обслуживание |
| 3 | Нейтрально | Мониторинг |
| 2 | Негатив | Эскалация менеджеру |
| 1 | Критично | Срочная эскалация руководству |

### NER (Named Entity Recognition)

Извлекаемые сущности для туризма:

| Entity | Примеры | Использование |
|--------|---------|---------------|
| `DATE` | завтра, 15 января | Планирование |
| `MONEY` | 500$, 2000 дирхам | Бюджет |
| `LOCATION` | Дубай, Бурдж Халифа | Маршрут |
| `HOTEL` | Atlantis, JW Marriott | Размещение |
| `TOUR` | сафари, морская прогулка | Продукт |
| `PERSON_COUNT` | 2 взрослых, 3 ребенка | Группа |

### Кластеризация клиентов (Customer Segmentation)

| Сегмент | Описание | Стратегия |
|---------|----------|-----------|
| **Budget Travelers** | Экономные путешественники | Акции, групповые туры, эконом-варианты |
| **Luxury Seekers** | VIP клиенты | Эксклюзивные предложения, персональный менеджер |
| **Family Adventurers** | Семьи с детьми | Семейные пакеты, детские активности |
| **Business Frequent** | Корпоративные клиенты | B2B условия, быстрое бронирование |
| **First Timers** | Новые клиенты | Обзорные туры, много информации |

### Предиктивная аналитика

```python
# Модель вероятности покупки
features = {
    "message_count": 10,          # Количество сообщений
    "price_mentions": 3,          # Упоминания цены
    "has_specific_dates": True,   # Указаны даты
    "has_budget": True,           # Указан бюджет
    "positive_sentiment": 0.7,    # Доля позитива
    "days_since_contact": 2       # Дней с первого контакта
}

# Результат
prediction = {
    "purchase_probability": 0.85,
    "recommendation": "Высокая вероятность. Предложите скидку за быстрое решение."
}
```

### Автоматическая эскалация

```python
ESCALATION_RULES = {
    'immediate': {
        'conditions': ['sentiment <= 1', 'intent == "complaint"'],
        'action': 'notify_manager',
        'sla_minutes': 5
    },
    'urgent': {
        'conditions': ['sentiment <= 2', 'vip_client'],
        'action': 'assign_senior',
        'sla_minutes': 15
    },
    'standard': {
        'conditions': ['no_response_hours >= 2'],
        'action': 'reminder',
        'sla_minutes': 60
    }
}
```

### Обнаружение аномалий (Fraud Detection)

```python
FRAUD_SIGNALS = {
    'high_risk': [
        'срочно перевод', 'альтернативные реквизиты',
        'другой счёт', 'крипто оплата'
    ],
    'behavioral': [
        'новый аккаунт + большая сумма',
        'смена локации',
        'нетипичный паттерн сообщений'
    ]
}

# Действия при обнаружении
risk_score >= 0.5 -> manual_review
risk_score >= 0.7 -> block + alert_manager
```

### RAG система для FAQ

```python
# Архитектура
FAQ_Database → Sentence Embeddings → FAISS Index
                     ↓
User Query → Embedding → Similarity Search → Top-K Results
                     ↓
             Claude → Персонализированный ответ

# Порог автоответа
if similarity_score > 0.85:
    auto_send_response()
else:
    route_to_human()
```

---

## Визуализация

### Интерактивный дашборд (Plotly)
- 6 графиков: сообщения по дням, типы (pie), активность по часам (bar), приоритеты (pie), sentiment (pie), top клиенты (bar)
- Сохранение в HTML для просмотра в браузере

### Тепловая карта активности
- Группировка по дням недели и часам
- Визуализация через `plotly.express.imshow` с палитрой YlOrRd

### Финансовые отчёты (PDF)
- Генерация через reportlab (A4)
- Таблица выручки по услугам с долями

→ Подробнее: `references/visualization-code.md` -- полный код create_dashboard(), create_heatmap(), generate_financial_report().

---

## Автоматизация процессов

### Напоминания и follow-up

| Триггер | Время | Действие |
|---------|-------|----------|
| Тур завтра | -24ч | Напоминание клиенту + водителю |
| Неоплаченная бронь | +2ч, +6ч, +12ч | Напоминание об оплате |
| Тур завершён | +2ч | Запрос отзыва |
| Тур завершён | +24ч | Отправка фото |
| Нет ответа | +7д | Предложение скидки |

### Workflow статусов заказа

```
NEW_REQUEST → QUOTED → BOOKED → PAID → CONFIRMED → COMPLETED
     │           │        │                           │
     v           v        v                           v
  EXPIRED    EXPIRED  CANCELLED                   REFUNDED
  (24ч)      (48ч)    (24ч без оплаты)           (если отмена)
```

### Lead Scoring

| Фактор | Баллы |
|--------|-------|
| dates_confirmed | +25 |
| group_size > 4 | +20 |
| budget_mentioned | +20 |
| repeat_client | +15 |
| engagement_level | +20 |

**Результат:** HOT (>80) -- срочно, WARM (40-80) -- nurture, COLD (<40) -- рассылка.

### Динамическое ценообразование

```python
# Факторы
demand_score = bookings / capacity  # 0-100
time_score = days_to_tour < 3 ? 20 : 0
season_score = is_peak_season ? 30 : 0

# Расчёт
adjustment = (demand_score * 0.4 + time_score * 0.2 + season_score * 0.3) / 100
final_price = base_price * (1 + adjustment * 0.3)  # ±30% max
```

### Автоматическая генерация документов

```python
# Триггер: оплата получена
trigger = "payment.success"

# Действия:
actions = [
    "generate_voucher_pdf",      # Генерация ваучера с QR-кодом
    "create_calendar_event",     # События в Google Calendar
    "notify_driver",             # Уведомление водителю
    "send_whatsapp_voucher",     # Отправка клиенту
    "update_crm_status"          # Обновление CRM
]
```

### Рассылки и уведомления

#### Telegram уведомления команде

| Шаблон | Триггер | Содержание |
|--------|---------|------------|
| `new_lead` | Новый запрос | Клиент, телефон, страна, сообщение, score, SLA |
| `complaint` | Жалоба | Клиент, телефон, сообщение, требуется реакция |
| `daily_report` | Ежедневно | Лиды, конверсия, выручка, средний чек, завтрашние туры |

#### Типовые автоответы

```python
AUTO_RULES = [
    {
        'triggers': ['график работы', 'режим работы'],
        'response': 'Мы работаем ежедневно с 9:00 до 22:00 по времени ОАЭ (UTC+4)',
        'confidence_threshold': 0.8
    },
    {
        'triggers': ['способ оплаты', 'как оплатить'],
        'response': 'Способы оплаты: банковский перевод, карты Visa/Mastercard, наличные, USDT',
        'confidence_threshold': 0.85
    },
    {
        'triggers': ['отмена', 'вернуть деньги'],
        'response': 'По вопросам отмены свяжитесь с менеджером: +971-XX-XXX-XXXX',
        'escalate': True
    }
]
```

→ Подробнее: `references/automation-workflows.md` -- развёрнутые workflow-диаграммы, шаблоны Telegram уведомлений с форматированием, ежедневный отчёт.

---

## Переменные окружения

### Обязательные

```bash
# Claude API (Anthropic)
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI (для Whisper)
OPENAI_API_KEY=sk-...

# Airtable
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=appXXX

# make.com
MAKE_WEBHOOK_SECRET=your_secret
```

### Опциональные

```bash
# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=@channel_name

# WhatsApp Business API
WHATSAPP_TOKEN=...
WHATSAPP_PHONE_ID=...

# Google Cloud (OCR альтернатива)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Yandex Cloud SpeechKit (для русского языка)
YANDEX_CLOUD_API_KEY=AQVN...
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f
```

### Файл .env

```bash
# D:/Downloads/туризм-оаэ-автоматизация/.env

# === ОБЯЗАТЕЛЬНЫЕ ===
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-xxxxx
AIRTABLE_API_KEY=patxxxxx
AIRTABLE_BASE_ID=appxxxxx

# === ОПЦИОНАЛЬНЫЕ ===
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TELEGRAM_BOT_TOKEN=123456:ABCxxxxx

# === YANDEX CLOUD (SpeechKit) ===
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f

# === НАСТРОЙКИ ===
LOG_LEVEL=INFO
DEFAULT_LANGUAGE=ru
AUTO_RESPONSE_ENABLED=true
```

### Загрузка переменных

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка из .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Проверка обязательных переменных
REQUIRED_VARS = [
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
    'AIRTABLE_API_KEY',
    'AIRTABLE_BASE_ID'
]

missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {missing}")

# Использование
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
```

---

## Использование

### Классификация сообщения

```bash
# Одиночное сообщение
python scripts/ai/claude_classifier.py --input message.json

# Пакетная обработка
python scripts/ai/claude_classifier.py --batch messages.jsonl --output classified.jsonl
```

### Транскрипция голосового

```bash
# Whisper API
python scripts/media/transcribe_whisper.py --file audio.ogg --language ru

# С контекстом
python scripts/media/transcribe_whisper.py --file audio.ogg --context "Ferrari World, Burj Khalifa"
```

### OCR документа

```bash
# Одиночный документ
python scripts/media/document_ocr.py --file passport.jpg

# Папка документов
python scripts/media/document_ocr.py --dir documents/ --output ocr_results.json
```

### Генерация дашборда

```bash
# Полный дашборд
python scripts/visualization/dashboard.py --data analytics.json --output dashboard.html

# Только heatmap
python scripts/visualization/activity_heatmap.py --messages all_messages.jsonl
```

### Финансовый отчёт

```bash
python scripts/visualization/financial_reports.py \
    --period "2026-01" \
    --format pdf \
    --output reports/january_2026.pdf
```

---

## Производительность

| Операция | Время | Стоимость API |
|----------|-------|---------------|
| Классификация (1 сообщение) | ~1 сек | ~$0.003 |
| Классификация (100 сообщений batch) | ~30 сек | ~$0.25 |
| Whisper транскрипция (1 мин аудио) | ~5 сек | ~$0.006 |
| SpeechKit транскрипция (1 мин аудио) | ~1 сек | ~$0.01 |
| OCR документа | ~2 сек | ~$0.01 |
| Генерация автоответа | ~2 сек | ~$0.005 |

**Рекомендации:**
- Используйте batch-обработку для массовых операций
- Кэшируйте частые запросы (прайсы, FAQ)
- Устанавливайте rate limits в make.com
- Мониторьте расходы через Anthropic/OpenAI dashboard

---

## Мониторинг и алерты

### Метрики для отслеживания

| Метрика | Target | Critical |
|---------|--------|----------|
| Время ответа API | < 2s | > 5s |
| Успешность классификации | > 95% | < 90% |
| Стоимость API в день | < $50 | > $100 |
| Ошибки в час | < 5 | > 20 |
| Queue backlog | < 100 | > 500 |

→ Подробнее: `references/security-monitoring.md` -- GDPR соответствие, маскирование PII (телефоны, карты, IBAN, email), ротация API ключей, настройка алертов (Slack, email, SMS), аудит-логи, безопасное хранение секретов.

---

## Troubleshooting

### Частые проблемы

| Проблема | Причина | Решение |
|----------|---------|---------|
| Claude API 429 | Rate limit | Добавить retry с backoff |
| Whisper timeout | Большой файл | Разбить на chunks < 25MB |
| OCR низкое качество | Плохое изображение | Улучшить preprocessing |
| make.com timeout | Долгая обработка | Асинхронная обработка |

### Логирование

```python
import logging

logging.basicConfig(
    filename='D:/Downloads/туризм-оаэ-автоматизация/logs/automation.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

logger = logging.getLogger('ai_agent')
logger.info("Message classified", extra={'type': 'inquiry', 'priority': 'medium'})
```

### Безопасность персональных данных

- GDPR: хранить данные в EU/UAE, шифровать PII, логировать доступы
- Маскирование: телефоны (`+971****4567`), карты (`**** **** **** 1234`), IBAN (`AE72****642584`)
- Ротация API ключей каждые 90 дней
- `.env` НЕ коммитить в git, использовать secrets manager для production

→ Подробнее: `references/security-monitoring.md`

---

## Результаты

```
D:/Downloads/UAE-Tourism-Data/_аналитика/
├── classifications/   # Результаты классификации
│   ├── daily/         # Ежедневные отчёты
│   └── aggregated/    # Агрегированные данные
├── heatmaps/          # Тепловые карты активности
├── graphs/            # Графы связей
├── reports/           # AI-отчёты и финансы
│   ├── weekly/        # Еженедельные
│   └── monthly/       # Ежемесячные
├── trends/            # Тренды и паттерны
├── forecasts/         # Прогнозы спроса
└── dashboards/        # HTML дашборды
```

---

## Связанные скиллы

| Скилл | Использует | Для чего |
|-------|------------|----------|
| **whatsapp-парсер** | all_messages.jsonl | Источник сообщений для классификации |
| **туризм-оаэ-бизнес** | classification.json | CRM обновления, профили клиентов |
| **обработка-запросов-турагентов** | auto_responder.py | Генерация ответов агентам |
| **форматирование-турпродуктов** | templates | Шаблоны для автоответов |
| **giga-transcribe-туризм** | transcribe_speechkit() | Транскрипция голосовых на русском языке |

---

## Дополнительные ресурсы

| Файл | Описание |
|------|----------|
| `references/classifier-prompt.md` | Системный промпт, batch-классификация, эскалация, fraud detection, RAG |
| `references/make-webhooks.md` | JSON конфигурации 4 webhook сценариев, обработка ошибок, дашборд метрик |
| `references/scripts-reference.md` | Полное описание всех 22 скриптов (вход/выход) |
| `references/media-processing.md` | Полный код: Whisper, SpeechKit, OCR, Vision, CLIP, дедупликация, VCF, видео |
| `references/visualization-code.md` | Полный код: Plotly дашборд, тепловая карта, финансовые PDF отчёты |
| `references/automation-workflows.md` | Workflow-диаграммы, автоответы, шаблоны уведомлений, динамическое ценообразование |
| `references/security-monitoring.md` | GDPR, маскирование PII, алерты, аудит-логи, ротация ключей |
| `references/faq.md` | Часто задаваемые вопросы |
| `references/troubleshooting.md` | Решение проблем |
| `references/api-costs.md` | Стоимость API вызовов |
| `references/security.md` | Полное руководство по безопасности |
| `D:/Downloads/Идеи-туризм-автоматизация/ИДЕИ_AI_АНАЛИЗ.md` | AI/ML анализ WhatsApp чатов |
| `D:/Downloads/Идеи-туризм-автоматизация/ИДЕИ_АВТОМАТИЗАЦИЯ.md` | Автоматизация процессов |
| `D:/Downloads/Идеи-туризм-автоматизация/ИДЕИ_ОБРАБОТКА_МЕДИА.md` | Обработка медиафайлов |
