# Справочник скриптов

Полное описание всех 22 скриптов автоматизации туристического бизнеса.

---

## ai/ -- Искусственный интеллект (7 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `claude_classifier.py` | message.json | classification.json | **Главный классификатор** -- определяет type, subtype, priority, intent |
| `sentiment_analysis.py` | message.json | sentiment.json | Анализ тональности: positive/neutral/negative |
| `summarize_dialog.py` | messages[].json | summary.json | Суммаризация диалога для менеджера |
| `auto_responder.py` | classification.json | response.json | Генерация автоматического ответа |
| `auto_followup.py` | client.json | followup.json | Генерация follow-up сообщений |
| `smart_analysis.py` | messages[].json | analysis.json | Глубокий анализ контекста клиента |
| `demand_forecast.py` | history.json | forecast.json | Прогноз спроса на услуги |

---

## marketing/ -- Маркетинг (4 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `referral_program.py` | client.json | referral_code.json | Генерация реферальных ссылок |
| `email_marketing.py` | template, contacts[] | sent_report.json | Массовая email рассылка |
| `sms_twilio.py` | template, phones[] | sent_report.json | SMS рассылка через Twilio |
| `instagram_parser.py` | profile_url | posts.json | Парсинг Instagram профилей |

---

## partners/ -- Партнёры (3 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `agent_portal.py` | agent_id | portal_data.json | Данные для агентского портала |
| `partner_api.py` | request.json | response.json | REST API для партнёров |
| `white_label.py` | config.json | branded_assets/ | Генерация white-label материалов |

---

## media/ -- Обработка медиа (5 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `organize_media.py` | media_folder/ | organized/ | Организация медиафайлов по датам |
| `voice_transcriber.py` | audio.ogg | transcription.json | Транскрипция через SpeechRecognition |
| `transcribe_whisper.py` | audio.* | transcription.json | **Whisper API** -- точная транскрипция |
| `document_ocr.py` | image.* / pdf | ocr_text.json | OCR документов (Tesseract/Vision) |
| `image_analyzer.py` | image.* | analysis.json | Анализ изображений (Claude Vision) |

---

## visualization/ -- Визуализация (3 скрипта)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `dashboard.py` | data/*.json | dashboard.html | Интерактивный дашборд (Plotly) |
| `activity_heatmap.py` | messages.jsonl | heatmap.html | Тепловая карта активности |
| `financial_reports.py` | operations.json | reports/ | Финансовые отчёты (PDF, Excel) |
