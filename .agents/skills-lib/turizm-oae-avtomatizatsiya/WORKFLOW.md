# Workflow: Туризм ОАЭ - Автоматизация

## Обзор процесса

```
Входящее сообщение (WhatsApp)
        |
        v
  [AI Классификация]
        |
        v
   Категория + Приоритет
        |
        v
  [Автоответ / Эскалация]
        |
        v
   CRM обновление
        |
        v
  [Аналитика]
        |
        v
   Дашборды, Отчёты
```

---

## Этап 1: AI Классификация и Анализ

### scripts/ai/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `claude_classifier.py` | all_messages.jsonl | classified_messages.jsonl, contact_classifications.json | Классифицирует сообщения через Claude API: определяет тип контакта (клиент/агент/поставщик), намерение (запрос цены, бронирование, жалоба), срочность, извлекает сущности (даты, суммы, туры), рекомендует действие |
| `sentiment_analysis.py` | all_messages.jsonl | sentiment_by_contact.json, sentiment_trends.json, alerts.json | Анализирует настроение клиентов: rule-based словари (ru/en/ar), emoji, пунктуация. Находит точки падения настроения, генерирует алерты |
| `auto_responder.py` | текст сообщения | автоматический ответ | Генерирует автоответы на частые вопросы: keyword/fuzzy/intent matching, персонализация (имя, язык, время), интеграция с WhatsApp API |
| `auto_followup.py` | contacts.json, all_messages.jsonl | followup_queue.json, followup_history.json | Определяет "холодных" контактов, генерирует персонализированные follow-up, создаёт задачи в Bitrix24, планирует в Google Calendar |
| `demand_forecast.py` | operations.json | forecast.json, model_metrics.json, forecast_chart.html | ML прогнозирование спроса: Prophet/ARIMA модели, учёт сезонности ОАЭ и праздников, рекомендации по промо-акциям |
| `smart_analysis.py` | чаты | анализ_YYYY-MM-DD.md | Умный анализ: поиск аномалий (необычные суммы, дубликаты), паттерны активности, рекомендации |
| `summarize_dialog.py` | all_messages.jsonl | summaries.json, summaries.md | Суммаризация диалогов через Claude API: краткое содержание, ключевые моменты, структурированный вывод (клиент хотел/предложено/итог) |

### Подробное описание AI скриптов

#### claude_classifier.py
- **Функции:** Классификация типа контакта, определение намерения, извлечение сущностей, оценка срочности
- **API зависимости:** Claude API (Anthropic), модель claude-sonnet-4-20250514
- **Особенности:** Batch processing для экономии токенов, кэширование результатов, rules-based fallback при недоступности API
- **Категории намерений:**
  - `price_inquiry` - запрос цены
  - `booking_request` - бронирование
  - `complaint` - жалоба
  - `support` - поддержка
  - `info_request` - запрос информации
  - `payment_inquiry` - вопрос об оплате
  - `cancellation` - отмена
  - `greeting` - приветствие
- **Запуск:**
```bash
python scripts/ai/claude_classifier.py --input all_messages.jsonl --batch-size 50
```

#### sentiment_analysis.py
- **Функции:** Sentiment scoring, определение эмоций (happy/angry/frustrated/grateful), тренды по времени
- **Словари:** 200+ слов на RU/EN/AR, 100+ emoji с весами
- **Шкала настроения:**
  - 5 - Восторг (запросить отзыв)
  - 4 - Позитив (стандартное обслуживание)
  - 3 - Нейтрально (мониторинг)
  - 2 - Негатив (эскалация менеджеру)
  - 1 - Критично (срочная эскалация руководству)
- **API зависимости:** Нет (rule-based)
- **Запуск:**
```bash
python scripts/ai/sentiment_analysis.py --input all_messages.jsonl --output-dir sentiment/
```

#### auto_responder.py
- **Функции:** Определение категории вопроса, выбор шаблона ответа, персонализация
- **Категории:** цены, бронирование, оплата, отмена, приветствие, благодарность
- **Особенности:** Нерабочее время (автоответ 9:00-21:00 GST), FAQ база 100+ вопросов
- **API зависимости:** Нет (шаблоны + fuzzywuzzy)
- **Запуск:**
```bash
python scripts/ai/auto_responder.py "Сколько стоит экскурсия в Абу-Даби?" --name Иван
python scripts/ai/auto_responder.py --interactive
```

#### auto_followup.py
- **Функции:** Анализ неактивных контактов, генерация персонализированных напоминаний, интеграция с CRM
- **Типы follow-up:**
  - `soft_reminder` (1 день) - мягкое напоминание
  - `repeat_offer` (3 дня) - повторное предложение
  - `special_offer` (7 дней) - специальное предложение со скидкой
  - `last_attempt` (14 дней) - последняя попытка
  - `reactivation` (30 дней) - реактивация
- **API зависимости:** Bitrix24 API (опционально), Google Calendar API (опционально)
- **Запуск:**
```bash
python scripts/ai/auto_followup.py --analyze              # Анализ
python scripts/ai/auto_followup.py --generate             # Генерация
python scripts/ai/auto_followup.py --all --dry-run        # Всё вместе (тест)
```

#### demand_forecast.py
- **Функции:** Прогнозирование спроса на 30/60/90 дней, учёт сезонности, праздников ОАЭ и РФ
- **Модели:** Prophet (основная), ARIMA, Simple Moving Average (baseline)
- **API зависимости:** Нет (локальные ML библиотеки)
- **Зависимости:** numpy, pandas, prophet
- **Запуск:**
```bash
python scripts/ai/demand_forecast.py --horizon 30 --category tours
```

#### summarize_dialog.py
- **Функции:** Краткое содержание диалога, извлечение ключевых моментов, определение статуса (active/pending/completed)
- **Типы суммаризации:**
  - Карточка клиента (100-200 слов)
  - Резюме заказа (50-100 слов)
  - История взаимодействий (200-500 слов)
  - Handoff summary для передачи менеджеру (100-150 слов)
- **API зависимости:** Claude API (Anthropic)
- **Особенности:** Batch обработка, кэширование, поиск по summary
- **Запуск:**
```bash
python scripts/ai/summarize_dialog.py --jid 79123456789@s.whatsapp.net
python scripts/ai/summarize_dialog.py --all --limit 100
```

---

## Этап 2: Маркетинг и рассылки

### scripts/marketing/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `email_marketing.py` | контакты, шаблоны | кампании, метрики | Email-рассылки через Mailchimp/SendGrid: welcome, booking, reminder, feedback, promo, birthday. GDPR compliant |
| `instagram_parser.py` | username конкурента | competitor_reports/ | Парсинг Instagram конкурентов: посты, engagement, цены, хэштеги. Анализ рынка ОАЭ |
| `referral_program.py` | телефон, имя | реферальный код, QR | Реферальная программа: генерация кодов, отслеживание, начисление бонусов, выплаты |
| `sms_twilio.py` | телефон, сообщение | SMS | SMS рассылки через Twilio: bulk, шаблоны, webhook для входящих, автоответы |

### Подробное описание

#### email_marketing.py
- **Функции:** Управление подписчиками, сегментация, A/B тесты, drip campaigns, аналитика
- **Провайдеры:** Mailchimp API, SendGrid API
- **Типы писем:** welcome, booking_confirmation, tour_reminder, feedback_request, promo, birthday, newsletter
- **API зависимости:** Mailchimp API, SendGrid API
- **Зависимости:** mailchimp-marketing, sendgrid, jinja2
- **Запуск:**
```bash
python scripts/marketing/email_marketing.py --send-welcome --email client@example.com
python scripts/marketing/email_marketing.py --campaign promo --segment vip
```

#### instagram_parser.py
- **Функции:** Сбор постов конкурентов, извлечение цен из описаний, анализ engagement, отслеживание хэштегов
- **API зависимости:** Нет (instaloader)
- **Зависимости:** instaloader, pandas, schedule
- **Запуск:**
```bash
python scripts/marketing/instagram_parser.py --add dubaidesertsafari
python scripts/marketing/instagram_parser.py --analyze-all
python scripts/marketing/instagram_parser.py --schedule daily  # Автоматический мониторинг
```

#### referral_program.py
- **Функции:** Генерация уникальных кодов, QR-коды, короткие ссылки, многоуровневая система бонусов
- **API зависимости:** Bitrix24 API (синхронизация), pyshorteners
- **Зависимости:** qrcode, pyshorteners, pandas
- **Запуск:**
```bash
python scripts/marketing/referral_program.py --generate --phone +971501234567 --name "Иван"
python scripts/marketing/referral_program.py --register --code REF-ABC123 --referred-phone +971507654321
python scripts/marketing/referral_program.py --balance --phone +971501234567
```

#### sms_twilio.py
- **Функции:** Отправка одиночных и bulk SMS, шаблоны, webhook для входящих, rate limiting
- **API зависимости:** Twilio API
- **Зависимости:** twilio, flask (webhook)
- **Запуск:**
```bash
python scripts/marketing/sms_twilio.py --send --to +971501234567 --message "Ваш тур завтра в 9:00"
python scripts/marketing/sms_twilio.py --bulk --file contacts.csv --template tour_reminder
python scripts/marketing/sms_twilio.py --webhook --port 5000  # Запуск webhook сервера
```

---

## Этап 3: Партнёрский портал

### scripts/partners/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `agent_portal.py` | credentials | веб-интерфейс | Веб-портал для агентов: авторизация (JWT), каталог туров, бронирование, личный кабинет, отчёты |
| `partner_api.py` | API запросы | JSON responses | REST API для партнёров: каталог, проверка наличия, создание бронирований, webhooks |
| `white_label.py` | настройки бренда | PDF, виджеты, landing | White-label решение: брендированные материалы, встраиваемый виджет бронирования, landing page генератор |

### Подробное описание

#### agent_portal.py
- **Функции:** JWT авторизация, уровни доступа (agent/manager/admin), каталог с ценами для агентов, система бронирования, комиссии
- **Технологии:** FastAPI, SQLAlchemy, Pydantic, Jinja2
- **API зависимости:** Нет (самостоятельный сервис)
- **Зависимости:** fastapi, sqlalchemy, jose, passlib, jinja2
- **Запуск:**
```bash
uvicorn scripts.partners.agent_portal:app --reload --port 8000
# Доступ: http://localhost:8000
```

#### partner_api.py
- **Функции:** REST API (OpenAPI/Swagger), rate limiting, API keys, webhook callbacks
- **Endpoints:** GET /tours, GET /availability, POST /bookings, GET /bookings/{id}, DELETE /bookings/{id}
- **API зависимости:** Нет (самостоятельный сервис)
- **Зависимости:** fastapi, slowapi, httpx
- **Запуск:**
```bash
uvicorn scripts.partners.partner_api:app --reload --port 8001
# Документация: http://localhost:8001/docs
```

#### white_label.py
- **Функции:** Кастомизация бренда (логотип, цвета), генерация PDF (ваучеры, инвойсы), виджет бронирования (iframe/JS), SEO landing pages
- **API зависимости:** Нет
- **Зависимости:** jinja2, weasyprint, pillow, qrcode
- **Запуск:**
```bash
python scripts/partners/white_label.py --setup --agent-id AG001 --company "Travel Plus"
python scripts/partners/white_label.py --generate-voucher --booking-id BK12345
python scripts/partners/white_label.py --generate-widget --agent-id AG001
```

---

## Этап 4: Обработка медиа

### scripts/media/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `transcribe_whisper.py` | папка с .opus | transcripts.txt | Расшифровка голосовых сообщений через локальный Whisper |
| `voice_transcriber.py` | медиафайлы | voice_transcripts.json | Транскрибация через OpenAI Whisper API: конвертация, batch processing, обновление сообщений |
| `whisper_postprocess.py` | текст | исправленный текст | Пост-обработка транскрипций: исправление банков, имён, терминов, нормализация чисел |
| `document_ocr.py` | изображение | DocumentData | OCR документов: паспорта, визы, чеки, билеты. Движки: Tesseract, Google Vision, Claude Vision |
| `image_analyzer.py` | изображение | ImageAnalysis | Анализ изображений через Claude Vision: классификация, извлечение текста, объектов, локаций |
| `organize_media.py` | папки чатов | организованные файлы | Организация медиафайлов по категориям: чеки, счета, документы, скриншоты, фото |

### Подробное описание

#### transcribe_whisper.py
- **Функции:** Batch транскрибация .opus файлов, локальная обработка
- **Модели:** tiny/base/small/medium/large (medium по умолчанию)
- **Особенности:** Поддержка туристического контекста (Дубай, сафари, дирхамы)
- **API зависимости:** Нет (локальный Whisper)
- **Зависимости:** openai-whisper, ffmpeg
- **Запуск:**
```bash
python scripts/media/transcribe_whisper.py "D:/Downloads/голосовые" -m medium -d cuda
python scripts/media/transcribe_whisper.py "D:/Downloads/голосовые" -m base -d cpu  # На слабом железе
```

#### voice_transcriber.py
- **Функции:** Транскрибация через облачный API, параллельная обработка, конвертация форматов, обновление JSONL
- **API зависимости:** OpenAI Whisper API
- **Зависимости:** openai, ffmpeg
- **Ограничения:** 25 MB на файл, 50 запросов/минуту
- **Запуск:**
```bash
python scripts/media/voice_transcriber.py --scan                    # Найти все аудио
python scripts/media/voice_transcriber.py --process --workers 4    # Обработать
python scripts/media/voice_transcriber.py --update-messages        # Обновить JSONL
```

#### document_ocr.py
- **Функции:** Распознавание документов, валидация форматов, извлечение данных, маскирование персональных данных
- **Типы документов:** passport, visa, receipt, bank_transfer, ticket, id_card
- **Провайдеры:** Tesseract (локальный), Google Vision API, Claude Vision API
- **Особенности:** Парсинг банковских переводов (ENBD, FAB, Сбер, Тинькофф, Kaspi)
- **API зависимости:** Google Vision API (опционально), Claude API (опционально)
- **Зависимости:** pytesseract, pillow, anthropic
- **Запуск:**
```bash
python scripts/media/document_ocr.py --file passport.jpg --provider tesseract
python scripts/media/document_ocr.py --file receipt.png --provider claude
python scripts/media/document_ocr.py --batch --dir documents/ --output ocr_results.json
```

#### image_analyzer.py
- **Функции:** Классификация изображений по категориям, извлечение текста и объектов
- **Категории:** document, screenshot, tour_photo, promo, personal, meme, receipt, bank_transfer, passport, visa, attraction, hotel, transport, food
- **API зависимости:** Claude Vision API (Anthropic)
- **Зависимости:** anthropic, pillow
- **Запуск:**
```bash
python scripts/media/image_analyzer.py --file photo.jpg
python scripts/media/image_analyzer.py --batch --dir media/ --category tour_photo
python scripts/media/image_analyzer.py --analyze-payments --dir screenshots/
```

#### organize_media.py
- **Функции:** Сортировка по типам (images/videos/audio/documents), сортировка по датам, дедупликация через perceptual hash
- **API зависимости:** Нет
- **Зависимости:** pillow, imagehash
- **Запуск:**
```bash
python scripts/media/organize_media.py --source media/ --output organized/
python scripts/media/organize_media.py --deduplicate --dir images/
```

---

## Этап 5: Визуализация

### scripts/visualization/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `dashboard.py` | JSON данные | веб-дашборд (Streamlit) | Интерактивный дашборд: KPI, графики, топ контактов, воронка продаж, просмотр чатов |
| `activity_heatmap.py` | all_messages.jsonl | PNG, HTML, JSON | Тепловые карты активности: час x день недели, GitHub-style calendar, лучшее время для контакта |
| `financial_reports.py` | operations.json | PDF, CSV, JSON, MD | Финансовые отчёты: P&L, Cash Flow, Unit Economics, агентские отчёты |

### Подробное описание

#### dashboard.py
- **Функции:** KPI карточки, графики трендов, топ контактов, воронка продаж, просмотр переписки, поиск
- **Страницы:** Обзор, Контакты, Операции, Аналитика, Чаты
- **Технологии:** Streamlit, Plotly, Pandas
- **API зависимости:** Нет
- **Зависимости:** streamlit, plotly, pandas
- **Запуск:**
```bash
streamlit run scripts/visualization/dashboard.py
# Доступ: http://localhost:8501
```

#### activity_heatmap.py
- **Функции:** Матрица час x день недели, GitHub-style calendar (год), определение лучшего времени для контакта
- **Форматы вывода:** PNG (matplotlib/seaborn), HTML (plotly), JSON
- **API зависимости:** Нет
- **Зависимости:** matplotlib, seaborn, plotly, numpy, pandas
- **Запуск:**
```bash
python scripts/visualization/activity_heatmap.py --contact 79123456789
python scripts/visualization/activity_heatmap.py --all --format html
python scripts/visualization/activity_heatmap.py --github-style --year 2024
```

#### financial_reports.py
- **Функции:** P&L (выручка/себестоимость/прибыль по категориям), Cash Flow (поступления/платежи/прогноз), Unit Economics (CAC/LTV/средний чек), агентские отчёты
- **Форматы вывода:** JSON, CSV, PDF, Markdown
- **API зависимости:** Нет
- **Зависимости:** reportlab (PDF), pandas
- **Запуск:**
```bash
python scripts/visualization/financial_reports.py --report pnl --period 2024-01
python scripts/visualization/financial_reports.py --report cashflow --forecast 90
python scripts/visualization/financial_reports.py --report agents --top 10
python scripts/visualization/financial_reports.py --all --format pdf
```

---

## Этап 6: Автоматизация процессов

### Интеграция с make.com

#### Сценарий 1: Классификация входящих сообщений
```
[WhatsApp Webhook]
       |
       v
[HTTP Request: claude_classifier]
       |
       v
[Router: по категории]
       |
       +---> [price_inquiry] --> Отправить прайс
       +---> [booking] --> Создать лид в Bitrix24
       +---> [complaint] --> Уведомить менеджера
       +---> [urgent] --> Telegram alert
       v
[Airtable: Логирование]
```

#### Сценарий 2: Автоматические follow-up
```
[Schedule: каждый день 10:00]
       |
       v
[HTTP Request: auto_followup.py --analyze]
       |
       v
[Iterator: cold_contacts]
       |
       v
[HTTP Request: auto_followup.py --generate]
       |
       v
[WhatsApp: Send Message]
       |
       v
[Bitrix24: Create Activity]
```

#### Сценарий 3: Голосовые сообщения
```
[WhatsApp Webhook: voice message]
       |
       v
[HTTP Request: Download media]
       |
       v
[HTTP Request: voice_transcriber.py]
       |
       v
[HTTP Request: claude_classifier.py]
       |
       v
[Router: по намерению]
       |
       v
[WhatsApp: Auto-reply]
```

#### Сценарий 4: Оплата -> ваучер -> клиенту
```
[Stripe/PayPal Webhook: payment.success]
       |
       v
[Найти бронирование в CRM]
       |
       v
[Обновить статус -> PAID]
       |
       +---> [Генерация PDF ваучера + QR-код]
       +---> [Уведомление команде в Telegram]
       v
[WhatsApp: отправка ваучера клиенту]
       |
       v
[Email: копия ваучера]
```

#### Сценарий 5: Жалоба -> эскалация
```
[Жалоба обнаружена]
       |
       v
[Claude AI: Анализ серьёзности]
       |
       +---> CRITICAL --> Звонок CEO + SMS всем
       +---> HIGH --> Telegram старшему менеджеру
       +---> MEDIUM/LOW --> Email + тикет
       v
[Notion: Create Support Ticket]
```

### Автоматические напоминания

#### За 24 часа до тура
```
[Ежедневный cron 20:00]
       |
       v
[Фильтр: туры завтра]
       |
       v
[Для каждого тура:]
  - Подтверждение даты/времени
  - Место pickup
  - Контакт водителя
  - QR-код ваучера
  - Прогноз погоды
  - Рекомендации (что взять)
```

#### Неоплаченные брони
```
Бронь создана
      |
      v
+2 часа   --> Напоминание 1: "Забронировано, ожидаем оплату"
      |
+6 часов  --> Напоминание 2: "Места ограничены"
      |
+12 часов --> Напоминание 3: "Последний шанс" + скидка 5%
      |
+24 часа  --> Автоотмена + уведомление менеджеру
```

#### Follow-up после тура
```
Тур завершён
      |
+2 часа   --> "Как прошёл тур? Оставьте отзыв" + ссылка
      |
+24 часа  --> "Фото с тура готовы!" + Google Drive ссылка
      |
+3 дня    --> "Скидка 10% на следующий тур" (если нет отзыва)
      |
+7 дней   --> "Рекомендуйте друзьям - получите бонус"
```

### Первичная квалификация лидов

```
[Новый контакт]
      |
      v
[Бот: Приветствие + вопросы]
  1. Откуда вы?
  2. Сколько человек?
  3. Какие даты интересуют?
  4. Какой бюджет планируете?
      |
      v
[Claude AI: Анализ ответов]
[Scoring: HOT / WARM / COLD]
      |
      +---> HOT (>80)  --> Срочно! Звонок менеджера
      +---> WARM (40-80) --> Nurturing campaign
      +---> COLD (<40) --> Рассылка
```

---

## Примеры запуска

### Полный цикл обработки сообщений
```bash
# 1. Классификация всех сообщений
python scripts/ai/claude_classifier.py --input all_messages.jsonl

# 2. Анализ настроения
python scripts/ai/sentiment_analysis.py --input all_messages.jsonl

# 3. Генерация follow-up
python scripts/ai/auto_followup.py --all

# 4. Запуск дашборда
streamlit run scripts/visualization/dashboard.py
```

### Обработка голосовых сообщений
```bash
# Локальная транскрибация (бесплатно, медленнее)
python scripts/media/transcribe_whisper.py "D:/Downloads/voice" -m medium

# Облачная транскрибация (быстро, платно)
python scripts/media/voice_transcriber.py --process

# Пост-обработка
python scripts/media/whisper_postprocess.py transcripts.txt
```

### Генерация отчётов
```bash
# Финансовые отчёты за месяц
python scripts/visualization/financial_reports.py --period 2024-01 --format all

# Тепловая карта активности
python scripts/visualization/activity_heatmap.py --all --output heatmaps/

# Прогноз спроса
python scripts/ai/demand_forecast.py --horizon 30
```

### Маркетинг
```bash
# Email рассылка VIP клиентам
python scripts/marketing/email_marketing.py --campaign promo --segment vip

# Мониторинг конкурентов
python scripts/marketing/instagram_parser.py --analyze-all

# Генерация реферального кода
python scripts/marketing/referral_program.py --generate --phone +971501234567
```

### Партнёрский портал
```bash
# Запуск портала для агентов
uvicorn scripts.partners.agent_portal:app --host 0.0.0.0 --port 8000

# Запуск Partner API
uvicorn scripts.partners.partner_api:app --host 0.0.0.0 --port 8001

# Генерация white-label материалов
python scripts/partners/white_label.py --generate-voucher --booking-id BK12345
```

---

## Переменные окружения

```bash
# AI
ANTHROPIC_API_KEY=sk-ant-...          # Claude API
OPENAI_API_KEY=sk-...                  # Whisper API

# Маркетинг
MAILCHIMP_API_KEY=...
SENDGRID_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# OCR
GOOGLE_VISION_KEY=...
TESSERACT_PATH=D:\Downloads\10_PROJECTS\Projects\PROJECT__UNASSIGNED_ROOT_FILES\inbox\06_Installers\tesseract.exe

# Интеграции
BITRIX24_DOMAIN=...
BITRIX24_USER_ID=...
BITRIX24_WEBHOOK_KEY=...

# Портал
PORTAL_SECRET_KEY=...
PORTAL_DATABASE_URL=sqlite:///agent_portal.db

# make.com webhooks
MAKE_WEBHOOK_INCOMING=https://hook.eu1.make.com/whatsapp-incoming
MAKE_WEBHOOK_PAYMENT=https://hook.eu1.make.com/payment-reminder
MAKE_WEBHOOK_VOUCHER=https://hook.eu1.make.com/generate-voucher
```

---

## Структура файлов

```
туризм-оаэ-автоматизация/
|-- scripts/
|   |-- ai/
|   |   |-- claude_classifier.py      # Классификация сообщений
|   |   |-- sentiment_analysis.py     # Анализ настроения
|   |   |-- auto_responder.py         # Автоответы
|   |   |-- auto_followup.py          # Follow-up напоминания
|   |   |-- demand_forecast.py        # Прогнозирование спроса
|   |   |-- smart_analysis.py         # Умный анализ
|   |   |-- summarize_dialog.py       # Суммаризация диалогов
|   |   +-- __init__.py
|   |
|   |-- marketing/
|   |   |-- email_marketing.py        # Email рассылки
|   |   |-- instagram_parser.py       # Парсинг Instagram
|   |   |-- referral_program.py       # Реферальная программа
|   |   |-- sms_twilio.py             # SMS через Twilio
|   |   +-- __init__.py
|   |
|   |-- partners/
|   |   |-- agent_portal.py           # Веб-портал агентов
|   |   |-- partner_api.py            # REST API для партнёров
|   |   |-- white_label.py            # White-label решение
|   |   +-- __init__.py
|   |
|   |-- media/
|   |   |-- transcribe_whisper.py     # Локальная транскрибация
|   |   |-- voice_transcriber.py      # Облачная транскрибация
|   |   |-- whisper_postprocess.py    # Пост-обработка
|   |   |-- document_ocr.py           # OCR документов
|   |   |-- image_analyzer.py         # Анализ изображений
|   |   |-- organize_media.py         # Организация файлов
|   |   +-- __init__.py
|   |
|   |-- visualization/
|   |   |-- dashboard.py              # Streamlit дашборд
|   |   |-- activity_heatmap.py       # Тепловые карты
|   |   |-- financial_reports.py      # Финансовые отчёты
|   |   +-- __init__.py
|   |
|   |-- config.py                     # Общая конфигурация
|   +-- __init__.py
|
|-- SKILL.md                          # Описание скилла
+-- WORKFLOW.md                       # Этот файл
```

---

## Зависимости

### Основные
```bash
pip install anthropic openai          # AI APIs
pip install pandas numpy              # Data processing
pip install plotly streamlit          # Visualization
pip install fastapi uvicorn           # Web APIs
pip install sqlalchemy pydantic       # ORM & validation
```

### Опциональные
```bash
pip install fuzzywuzzy python-Levenshtein  # Fuzzy matching
pip install prophet                         # Forecasting
pip install mailchimp-marketing sendgrid    # Email
pip install twilio                          # SMS
pip install instaloader                     # Instagram
pip install qrcode pillow                   # Images
pip install weasyprint reportlab            # PDF
pip install openai-whisper                  # Local transcription
pip install pytesseract                     # Local OCR
pip install imagehash                       # Image deduplication
pip install langdetect                      # Language detection
```

---

*Последнее обновление: январь 2025*
