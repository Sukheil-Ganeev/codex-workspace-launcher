# Пайплайн обработки — подробные инструкции

Детальное описание каждого шага обработки ZIP-экспорта WhatsApp, расширенных функций, скриптов v2.0, AI-агента и интеграций.

---

## Шаг 1: Распаковка архива

```bash
unzip -o "Чат WhatsApp с Иван.zip" -d "D:/Downloads/Иван_extracted/"
```

Структура распакованного архива:
```
Иван_extracted/
├── _chat.txt              # Текст переписки
├── 00000001-AUDIO.opus    # Голосовые сообщения
├── 00000002-PHOTO.jpg     # Изображения
├── 00000003-DOC.pdf       # PDF документы
└── contact.vcf            # Контакт (опционально)
```

## Шаг 2: Расшифровка голосовых (Whisper)

Используется модель `medium` с GPU-ускорением:

```python
import whisper
import sys
sys.stdout.reconfigure(encoding='utf-8')

model = whisper.load_model("medium", device="cuda")
result = model.transcribe(
    "audio.opus",
    language="ru",
    fp16=True
)
print(result["text"])
```

**Параметры Whisper:**
- Модель: `medium` (оптимально для RTX 3060, ~5GB VRAM)
- Device: `cuda` (GPU-ускорение)
- Язык: `ru` (русский)
- fp16: `True` (экономия памяти)

## Шаг 3: Анализ изображений

Использовать Read tool для анализа каждого изображения:
- Описать содержимое
- Извлечь текст (если есть)
- Определить тип (скриншот, фото, документ)

## Шаг 4: Анализ PDF

Использовать Read tool для PDF:
- Извлечь текстовое содержимое
- Определить тип документа (инвойс, договор, билет)
- Выделить ключевые данные

## Шаг 5: Парсинг VCF контактов

```python
def parse_vcf(vcf_path):
    contacts = []
    with open(vcf_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for card in content.split('BEGIN:VCARD'):
        if 'FN:' in card:
            name = card.split('FN:')[1].split('\n')[0].strip()
            phone = ""
            if 'TEL' in card:
                phone = card.split('TEL')[1].split(':')[-1].split('\n')[0].strip()
            contacts.append({'name': name, 'phone': phone})

    return contacts
```

## Шаг 6: Сборка MD документа

Объединить все компоненты в структурированный Markdown:
- Метаданные контакта
- История переписки с расшифровками
- Сводка операций (если есть финансы)
- Реквизиты (если есть банковские данные)

## Шаг 7: Каталогизация

Сохранить в соответствующую папку по типу контакта:
```
D:/Downloads/Chats/
├── клиенты/
├── агенты/
├── поставщики/
└── сотрудники/
```

---

## Структура выходного файла

```markdown
# [Тип]: [Имя контакта]

## Метаданные
- **Тип:** клиент / агент / поставщик / сотрудник
- **Телефон:** +7 XXX XXX-XX-XX
- **Период:** DD.MM.YYYY — DD.MM.YYYY
- **Тематика:** обмен валюты
- **Заметки:** надёжный партнёр

---

## История переписки

### 15.01.2025

**10:30 Иван:**
Привет! Нужен обмен 1000 USD

**10:32 Я:**
Добрый день! Курс сегодня 92.5

**10:35 Иван:**
🎤 *Голосовое сообщение (0:45):*
> Хорошо, давайте на 92.5. Могу подъехать к вам в офис после обеда...

**10:40 Я:**
📷 *Изображение: Карта с адресом офиса*
> Скриншот Google Maps с отмеченной точкой...

---

## Сводка операций

| Дата | Операция | Сумма | Курс | Итого |
|------|----------|-------|------|-------|
| 15.01.2025 | USD → RUB | 1,000 USD | 92.5 | 92,500 RUB |

---

## Реквизиты
### Банковские данные клиента
- **Банк:** Сбербанк
- **Карта:** **** 1234
```

---

## Именование файлов и каталогизация

### Формат имени файла

```
[тип]_[Имя]_[тематика].md
```

**Примеры:**
- `клиент_Иван_обмен-валюты.md`
- `агент_Марина_туры.md`
- `поставщик_Ахмед_трансферы.md`
- `сотрудник_Алексей_общее.md`

### Полная структура папок

```
D:/Downloads/Chats/
│
├── 📁 ПЕРВИЧНЫЕ ФАЙЛЫ (полные расшифровки чатов)
│   ├── клиенты/
│   ├── агенты/
│   ├── поставщики/
│   └── сотрудники/
│
├── 📁 ВТОРИЧНЫЕ ФАЙЛЫ (извлечённые/агрегированные данные)
│   ├── _база/                               ← Данные из ВСЕХ чатов
│   │   ├── реквизиты.md
│   │   ├── операции.csv
│   │   ├── контакты.md
│   │   ├── события.md
│   │   ├── адреса.md
│   │   ├── связи.md
│   │   └── быстрые_ответы.md
│   ├── _индекс/
│   │   ├── index.md
│   │   ├── по_типам.md
│   │   └── теги.md
│   └── _медиа/
│       ├── чеки/
│       ├── скриншоты/
│       └── документы/
```

---

## Первичные vs Вторичные файлы

### Первичные файлы (полные расшифровки)

**Содержат:** полную историю, расшифровки ВСЕХ голосовых, описания изображений/PDF, контактную информацию, сводку операций, реквизиты, статистику.

**Правила:**
- НЕ редактируются после создания (источник истины)
- НЕ удаляются данные
- Можно добавлять статистику

### Вторичные файлы (агрегированные данные)

Данные, извлечённые и объединённые из ВСЕХ первичных файлов. Пересоздаются автоматически скриптами.

---

## Технические требования

### Whisper конфигурация

```python
import whisper
import torch
import sys

sys.stdout.reconfigure(encoding='utf-8')
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

model = whisper.load_model("medium", device="cuda")

def transcribe_audio(audio_path):
    result = model.transcribe(
        audio_path,
        language="ru",
        fp16=True,
        verbose=False
    )
    return result["text"]
```

**Требования к GPU:** RTX 3060+, 6GB VRAM, CUDA 11.x+

### Кодировка (Windows)

```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Или: sys.stdout.reconfigure(encoding='utf-8')
```

---

## Форматирование сообщений

### Иконки для типов контента

| Иконка | Тип | Формат в документе |
|--------|-----|-------------------|
| 🎤 | Голосовое | `🎤 *Голосовое (0:45):*` + расшифровка в блок-цитате |
| 📷 | Изображение | `📷 *Изображение: [описание]*` + детали |
| 📄 | PDF документ | `📄 *PDF: [название]*` + извлечённые данные |
| 📇 | Контакт VCF | `📇 *Контакт: [имя]*` + телефон |
| 📍 | Геолокация | `📍 *Локация: [адрес]*` |
| 🎥 | Видео | `🎥 *Видео (1:30):*` + описание |

---

## РАСШИРЕННЫЕ ФУНКЦИИ

### База данных `_база/`

```
D:/Downloads/Chats/_база/
├── реквизиты.md      # Все банковские реквизиты
├── операции.csv      # Все финансовые операции (для Excel)
├── контакты.md       # Все телефоны и email
├── события.md        # Даты и события
├── адреса.md         # Локации и адреса
├── связи.md          # Граф связей
└── быстрые_ответы.md # Частые ответы
```

### Статистика чата

Каждый чат автоматически получает секцию статистики: всего сообщений, голосовых, фото, PDF, дней переписки, среднее сообщ./день, по отправителям, финансы.

### Автоматическое извлечение

| Сущность | Паттерн | Куда сохраняется |
|----------|---------|------------------|
| IBAN | `AE + 21 цифра` | `_база/реквизиты.md` |
| Карта РФ | `4276 **** **** ****` | `_база/реквизиты.md` |
| Телефон РФ | `+7 XXX XXX-XX-XX` | `_база/контакты.md` |
| Телефон ОАЭ | `+971 XX XXX XXXX` | `_база/контакты.md` |
| Email | `*@*.*` | `_база/контакты.md` |
| Счёт РФ | `408...` (20 цифр) | `_база/реквизиты.md` |

### Связи между контактами

Скилл анализирует упоминания и строит граф связей: кто кого рекомендовал, общие бенефициары, связанные контакты.

---

## НОВЫЕ ФУНКЦИИ (v2.0)

### Единый пайплайн `process_all.py`

```bash
python scripts/process_all.py "Чат WhatsApp с Anna.zip"
python scripts/process_all.py chat.zip --name "Anna" --type поставщики --topic обмен-валюты
python scripts/process_all.py chat.zip --skip-whisper
python scripts/process_all.py chat.zip --dry-run
```

### Полнотекстовый поиск `search.py`

```bash
python scripts/search.py "Emirates NBD"
python scripts/search.py --amount-min 100000 --currency RUB
python scripts/search.py --date 2025-01
python scripts/search.py --contact Anna
```

### Аналитические отчёты `generate_report.py`

```bash
python scripts/generate_report.py --month 2025-01
python scripts/generate_report.py --overview
python scripts/generate_report.py --all
```

### Маскирование данных `mask_data.py`

```bash
python scripts/mask_data.py chat.md
python scripts/mask_data.py chat.md -l strict
python scripts/mask_data.py chat.md -t cards phones
```

| Уровень | Карта | Телефон | IBAN |
|---------|-------|---------|------|
| minimal | 4276 **** 9012 | +7 *** **-81 | AE72***584 |
| standard | 4276 **** **** 9012 | +7 *** ***-**-81 | AE72********584 |
| strict | **** **** **** **** | +7 *** ***-**-** | ****************** |

### Извлечение задач `extract_todos.py`

```bash
python scripts/extract_todos.py
python scripts/extract_todos.py chat.md
```

Находит: TODO, обещания, напоминания, незавершённые операции, вопросы без ответа.

### Шаблоны сообщений `generate_templates.py`

```bash
python scripts/generate_templates.py
python scripts/generate_templates.py --sender Сухейль
```

### Версионирование `diff_chats.py`

```bash
python scripts/diff_chats.py chat.md --version
python scripts/diff_chats.py chat.md --diff
python scripts/diff_chats.py --auto-version
python scripts/diff_chats.py --cleanup --keep 10
```

### Умный анализ `smart_analysis.py`

```bash
python scripts/smart_analysis.py
python scripts/smart_analysis.py --anomalies
python scripts/smart_analysis.py --recommendations
```

### Пост-обработка Whisper `whisper_postprocess.py`

```bash
python scripts/whisper_postprocess.py transcripts.txt
python scripts/whisper_postprocess.py -t "текст для обработки"
```

Исправляет: названия банков, имена, финансовые термины, форматирование сумм.

### Централизованная конфигурация `config.py`

```python
from scripts.config import CHATS_DIR, WHISPER_MODEL, ensure_directories
from scripts.config import check_api_key, BANK_CORRECTIONS, NAME_CORRECTIONS
```

---

## Полный пайплайн обработки

```bash
# 1. Обновить базу реквизитов
python scripts/extract_requisites.py
# 2. Обновить CSV операций
python scripts/extract_operations.py
# 3. Обновить паттерны
python scripts/extract_patterns.py
# 4. Обновить индекс
python scripts/build_index.py
# 5. Добавить статистику
python scripts/chat_statistics.py --all
# 6. Извлечь задачи
python scripts/extract_todos.py
# 7. Создать версию
python scripts/diff_chats.py --auto-version
# 8. Умный анализ
python scripts/smart_analysis.py
```

---

## AI-АГЕНТ: АРХИТЕКТУРА ДАННЫХ

### Цель проекта

Создать систему данных для AI-агента туристического бизнеса:

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Автоматизация | make.com | Сценарии обработки |
| База данных | Airtable | CRM + операции |
| AI-обработка | Claude API | Классификация, ответы |
| Коммуникация | WhatsApp Business API | Сообщения |

### 7 сущностей данных

| Сущность | Описание | Источник |
|----------|----------|----------|
| **Контакты** | Все контакты из чатов | chat.txt заголовки |
| **Профили** | Детальная информация | Анализ переписок |
| **Взаимодействия** | Сессии общения | Группировка по времени |
| **Операции** | Заказы, бронирования | Извлечение из текста |
| **Рефералы** | Кто кого привёл | VCF + упоминания |
| **Реквизиты** | Банковские данные | Паттерны IBAN/карт |
| **Метрики** | Агрегированная статистика | Расчёт по периодам |

### Расположение данных

```
D:/Downloads/Chats/_база/
├── json/           # Машиночитаемые данные (для make.com)
├── csv/            # Для импорта в Airtable
├── md/             # Человекочитаемые отчёты
├── airtable/       # Схема и инструкции
└── raw/            # Исходные JSONL
```

### JSON-схемы сущностей

#### contacts.json
```json
{
  "contacts": [{
    "contact_id": "uuid",
    "jid": "971501234567@s.whatsapp.net",
    "phone": "+971501234567",
    "name": "Имя из адресной книги",
    "type": "клиент|агент|поставщик|сотрудник",
    "subtype": "турист|VIP|турагент|обменник|водитель",
    "source": "whatsapp|wa_business|both",
    "first_message_date": "2024-01-15T10:30:00",
    "last_message_date": "2026-01-26T12:00:00",
    "total_messages": 127,
    "tags": ["обмен_валюты", "VIP"]
  }]
}
```

#### operations.json
```json
{
  "operations": [{
    "operation_id": "uuid",
    "contact_id": "uuid",
    "type": "tour|transfer|yacht|tickets|exchange",
    "description": "Экскурсия в Абу-Даби",
    "date": "2026-01-25",
    "pax": 4,
    "amount": 2000,
    "currency": "AED",
    "status": "inquiry|booked|confirmed|completed"
  }]
}
```

### Скрипты извлечения для AI-агента

| Скрипт | Вход | Выход |
|--------|------|-------|
| `parse_all_chats.py` | 3050 chat.txt | all_messages.jsonl |
| `extract_contacts.py` | all_messages.jsonl | contacts.json |
| `classify_contacts.py` | contacts.json | contacts.json (обновлённый) |
| `build_profiles.py` | all_messages.jsonl | profiles.json |
| `detect_referrals.py` | all_messages.jsonl + VCF | referrals.json |
| `calculate_metrics.py` | все JSON | metrics.json |
| `export_for_airtable.py` | все JSON | *.csv |

### Правила автоклассификации

```python
CLASSIFICATION_RULES = {
    "агенты": {"keywords": ["турагент", "комиссия", "%", "нетто", "партнёр"]},
    "поставщики": {"keywords": ["обменник", "курс", "водитель", "гид", "яхта"]},
    "сотрудники": {"keywords": ["офис", "зарплата", "отпуск", "смена"]},
    "клиенты": {"default": True, "keywords": ["бронирование", "экскурсия", "сколько стоит"]}
}
```

### Аналитические скрипты

| Скрипт | Назначение |
|--------|------------|
| `extract_price_inquiries.py` | Ценовые запросы клиентов |
| `extract_travel_dates.py` | Даты прилёта/отлёта |
| `calculate_response_time.py` | Метрики времени отклика |
| `build_sales_funnel.py` | Воронка продаж |
| `extract_complaints.py` | Жалобы и отмены |
| `seasonal_analysis.py` | Сезонный анализ |
| `calculate_ltv.py` | LTV клиентов |

---

## AI И АВТОМАТИЗАЦИЯ

| Скрипт | Назначение | API |
|--------|------------|-----|
| `claude_classifier.py` | Классификация сообщений | Claude API |
| `auto_responder.py` | Автоответы на частые вопросы | - |
| `sentiment_analysis.py` | Анализ настроения | Claude/Rules |
| `auto_followup.py` | Автоматические follow-up | - |

```bash
python scripts/claude_classifier.py --text "Сколько стоит экскурсия в Абу-Даби?"
python scripts/auto_responder.py --mode watch
python scripts/sentiment_analysis.py --all
```

---

## МЕДИА-ОБРАБОТКА

| Скрипт | Назначение | API |
|--------|------------|-----|
| `voice_transcriber.py` | Транскрибация голосовых | Whisper |
| `document_ocr.py` | OCR документов | Tesseract/Vision |
| `image_analyzer.py` | Анализ изображений | Claude Vision |

---

## АНАЛИТИКА И ОТЧЁТЫ

| Скрипт | Назначение |
|--------|------------|
| `dashboard.py` | Веб-дашборд Streamlit |
| `financial_reports.py` | P&L, Cash Flow отчёты |
| `demand_forecast.py` | ML прогнозирование спроса |

---

## ИНТЕГРАЦИИ

| Скрипт | Сервис |
|--------|--------|
| `telegram_bot.py` | Telegram Bot API |
| `whatsapp_api.py` | WhatsApp Cloud API |
| `email_sync.py` | Gmail / Outlook |
| `notion.py` | Notion API |
| `google_sheets.py` | Google Sheets API |

---

## ДОКУМЕНТЫ

| Скрипт | Тип документа |
|--------|---------------|
| `invoice_generator.py` | PDF инвойсы |
| `contract_generator.py` | Договоры |
| `voucher_generator.py` | Ваучеры |

---

## ГЕОЛОКАЦИЯ И КАРТЫ

| Скрипт | Назначение |
|--------|------------|
| `client_heatmap.py` | Тепловая карта клиентов |
| `pickup_optimizer.py` | TSP оптимизация маршрутов |
| `driver_routes.py` | Маршруты для водителей |

---

## МАРКЕТИНГ

| Скрипт | Назначение |
|--------|------------|
| `instagram_parser.py` | Парсер Instagram конкурентов |
| `referral_program.py` | Реферальная программа |
| `email_marketing.py` | Mailchimp/SendGrid |
| `sms_twilio.py` | SMS рассылки через Twilio |

---

## ПАРТНЁРСТВА

| Скрипт | Назначение |
|--------|------------|
| `agent_portal.py` | Веб-портал для агентов (FastAPI) |
| `partner_api.py` | REST API для партнёров |
| `white_label.py` | White-label решение |

---

## API КЛЮЧИ И НАСТРОЙКА

### Необходимые API ключи

| API | Переменная окружения | Как получить |
|-----|---------------------|--------------|
| Claude API | `ANTHROPIC_API_KEY` | console.anthropic.com |
| OpenAI Whisper | `OPENAI_API_KEY` | platform.openai.com |
| Telegram Bot | `TELEGRAM_BOT_TOKEN` | @BotFather |
| WhatsApp Cloud | `WHATSAPP_TOKEN` | developers.facebook.com |
| Google Sheets | `GOOGLE_SHEETS_CREDENTIALS` | console.cloud.google.com |
| Notion | `NOTION_API_KEY` | notion.so/my-integrations |
| Airtable | `AIRTABLE_API_KEY` | airtable.com/account |

### Настройка .env файла

```bash
# C:/Users/londo/.claude/skills/экспорт-whatsapp-чатов/scripts/.env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
WHATSAPP_TOKEN=EAAxxxxx
WHATSAPP_PHONE_ID=123456789012345
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
NOTION_API_KEY=secret_xxxxx
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
```

### Проверка настройки

```bash
python scripts/check_api_keys.py
python scripts/check_api_keys.py --service telegram
```
