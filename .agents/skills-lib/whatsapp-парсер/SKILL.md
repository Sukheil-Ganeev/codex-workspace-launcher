---
name: whatsapp-парсер
description: "Парсинг и анализ WhatsApp чатов. Извлечение контактов, сообщений, медиа, паттернов. Используй когда нужно обработать экспортированные чаты WhatsApp."
---
# WhatsApp Парсер

## Quick Start

```bash
# 1. Парсинг всех чатов
python scripts/parsing/parse_all_chats.py

# 2. Извлечение контактов
python scripts/parsing/extract_contacts.py

# 3. Статистика
python scripts/analysis/chat_statistics.py
```

**Входные данные:** `D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Личный/` и `D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Бизнес/`

**Результаты:** `D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/`

**Трекер обработки:** [CONTACTS_TRACKER.md](CONTACTS_TRACKER.md) — статус углубленной обработки отдельных клиентов

---

## Назначение

Полный инструментарий для извлечения и анализа данных из экспортированных WhatsApp чатов туристического бизнеса ОАЭ. Преобразует сырые текстовые экспорты в структурированные данные для CRM, аналитики и AI-агента.

---

## Исходные данные

| Источник | Путь | Количество |
|----------|------|------------|
| WhatsApp Personal | `D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Личный/` | 1,063 чата |
| WhatsApp Business | `D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Бизнес/` | 1,987 чатов |
| **Всего** | | **3,050 чатов** |

**Формат папок:** Каждый чат хранится в отдельной папке, названной по имени группы/контакта + JID (например: `SUKHEIL & MARSEL BROTHERS_120363196829914006`).

**Legacy пути (старые, не используются):**
- `D:/Downloads/экспорт чатов с ватсапа/`
- `D:/Downloads/экспорт чатов с ватсап бизнеса/`

**Статистика:**
- Сообщений: 880,257
- Медиафайлов: 412,761
- Контактов: 3,220
- Транскрипций: 50,430
- OCR: 59,536
- Чатов: 2,422
- Период: 2020-2026

---

## Результаты парсинга

```
D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/
├── жсонл/              # all_messages_enriched.jsonl (880K, 401 MB)
├── контакты/           # vcf_contacts.json
├── сущности/           # finance, phones, emails, urls, travel_dates (.jsonl)
├── аналитика/          # chat_statistics, contacts_unified
├── метаданные/         # transcriptions
├── итого/              # 30+ файлов: индексы, аналитика, CRM, training data
│   ├── contacts_master.json / contacts_master_v2.json
│   ├── transcription_index.json (50K), ocr_index.json (59K), pdf_index.json (9.8K)
│   ├── contact_graph_full.json (224K узлов, 151 MB)
│   ├── quality_all_chats.json (1,865 чатов с грейдами)
│   ├── funnel_analysis.json (2,133 чатов, 8 стадий)
│   ├── finance_report.json (~90M AED)
│   ├── search_index.db (SQLite FTS5, 773K записей, 322 MB)
│   ├── training_data.jsonl (719 диалогов)
│   ├── crm_export.csv + .json (3,220 контактов)
│   └── SUMMARY.md
├── документы/
├── ocr/
└── логи/
```

---

## Форматы исходных данных

### Формат 1: Кастомный массовый экспорт (chat.txt)

Используется в: `D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Личный/`, `D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Бизнес/`

#### Заголовок чата

```
============================================================
ЧАТ: Марсель Ганеев
JID: 971507705321@s.whatsapp.net
Сообщений: 1547
Экспорт: 26.01.2026 15:30:45
============================================================
```

### Формат сообщений

```
[26.01.2026 10:30:45] Марсель Ганеев:
  Привет! Нужен трансфер из аэропорта
  [ФОТО] media/IMG_20260126_103045.jpg

[26.01.2026 10:32:12] Я:
  Добрый день! Конечно, в какой отель?

[26.01.2026 10:33:00] Марсель Ганеев:
  [ЛОКАЦИЯ] https://maps.google.com/?q=25.197197,55.274376
  Atlantis The Palm
```

### Типы контента

| Тип | Формат в chat.txt | Пример |
|-----|-------------------|--------|
| Текст | Просто текст | Привет |
| Фото | `[ФОТО] media/...` | `[ФОТО] media/IMG_001.jpg` |
| Видео | `[ВИДЕО] media/...` | `[ВИДЕО] media/VID_001.mp4` |
| Аудио | `[АУДИО] media/...` | `[АУДИО] media/AUD_001.opus` |
| Голосовое | `[ГОЛОСОВОЕ] media/...` | `[ГОЛОСОВОЕ] media/PTT_001.opus` |
| Документ | `[ДОКУМЕНТ] media/...` | `[ДОКУМЕНТ] media/doc.pdf` |
| Стикер | `[СТИКЕР] media/...` | `[СТИКЕР] media/STK_001.webp` |
| GIF | `[GIF] media/...` | `[GIF] media/GIF_001.mp4` |
| Локация | `[ЛОКАЦИЯ] url` | `[ЛОКАЦИЯ] https://maps.google.com/?q=...` |
| Контакт | `[КОНТАКТ] имя` | `[КОНТАКТ] Иван Петров.vcf` |
| Удалено | `[УДАЛЕНО]` | `[УДАЛЕНО]` |
| Пересылка | `[ПЕРЕСЛАНО]` | `[ПЕРЕСЛАНО]` |

---

### Формат 2: Стандартный ZIP-экспорт WhatsApp

Используется при экспорте чата через меню WhatsApp "Экспортировать чат" -> ZIP.

**Пример источника:** `D:/Downloads/_whatsapp_parsed/` (лимузинные партнёры, 3 чата, 11,016 сообщений)

#### Формат сообщений

```
[04/11/2021, 21:01:41] LL Suheil: Ok
[04/11/2021, 21:02:15] LL Raja Zaryab: 5 lexus for 10 hours
[05/11/2021, 09:30:00] LL Raja Zaryab: <прикреплено: 00000045-PHOTO.jpg>
```

#### Regex для парсинга

```python
# Стандартный ZIP-экспорт
ZIP_MESSAGE = re.compile(
    r'^\[(\d{2}/\d{2}/\d{4}),\s(\d{2}:\d{2}:\d{2})\]\s(.+?):\s(.+)$'
)
# Группы: (1) дата DD/MM/YYYY, (2) время HH:MM:SS, (3) отправитель, (4) текст

ZIP_ATTACHMENT = re.compile(r'^<прикреплено:\s(.+?)>$')
```

#### Отличия от кастомного формата

| Параметр | ZIP-экспорт | Кастомный массовый |
|----------|-------------|-------------------|
| Дата | `[DD/MM/YYYY, HH:MM:SS]` | `[DD.MM.YYYY HH:MM:SS]` |
| Отправитель | На той же строке | Отдельная строка |
| Вложения | `<прикреплено: file>` | `[ФОТО] media/file` |
| Заголовок | Нет | `ЧАТ:`, `JID:` |
| Многострочные | Строки без `[дата]` | Строки с отступом |

#### VIP Transfer Blank (специальный формат заказа)

В лимузинных чатах используется стандартизированный бланк:

```
VIP Transfer Blank:
ORDER DATE: 15/11/2022
MEETING TIME: 14:00
TRANSPORT MODEL: Lexus ES 350
FULL NAME: John Smith
CONTACT NUMBER: +971 50 123 4567
PICK UP: Dubai Mall
DROP OFF: Dubai Airport Terminal 3
FLIGHT NUMBER: EK 302
HOURS: 3
RATE: 180 AED
```

```python
BLANK_START = re.compile(r'VIP\s+Transfer\s+Blank', re.IGNORECASE)
VIP_FIELDS = {
    'order_date': re.compile(r'ORDER\s+DATE[:\s]*(.+)', re.IGNORECASE),
    'meeting_time': re.compile(r'MEETING\s+TIME[:\s]*(.+)', re.IGNORECASE),
    'transport': re.compile(r'TRANSPORT\s+MODEL[:\s]*(.+)', re.IGNORECASE),
    'full_name': re.compile(r'FULL\s+NAME[:\s]*(.+)', re.IGNORECASE),
    'contact': re.compile(r'CONTACT\s+NUMBER[:\s]*(.+)', re.IGNORECASE),
    'pickup': re.compile(r'PICK\s*UP[:\s]*(.+)', re.IGNORECASE),
    'dropoff': re.compile(r'DROP\s*OFF[:\s]*(.+)', re.IGNORECASE),
    'rate': re.compile(r'RATE[:\s]*(.+)', re.IGNORECASE),
}
```

**Кейс:** 113 заказов извлечено, 55 уникальных клиентов. См. `D:/MARSEL_BUSINESS/` и скилл `/limo-order-manager`.

---

## Регулярные выражения для парсинга (кастомный формат)

```python
import re

# Заголовок чата
CHAT_HEADER = re.compile(r'^ЧАТ: (.+)$', re.MULTILINE)
JID_PATTERN = re.compile(r'^JID: (.+)$', re.MULTILINE)
MSG_COUNT = re.compile(r'^Сообщений: (\d+)$', re.MULTILINE)
EXPORT_DATE = re.compile(r'^Экспорт: (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})$', re.MULTILINE)

# Сообщение
MESSAGE = re.compile(r'^\[(\d{2}\.\d{2}\.\d{4}) (\d{2}:\d{2}:\d{2})\] (.+):$')
# Группы: (1) дата, (2) время, (3) отправитель

# Типы контента
MEDIA = re.compile(r'^\s+\[(.+?)\] media/(.+)$')
LOCATION = re.compile(r'^\s+\[ЛОКАЦИЯ\] (https://maps\.google\.com/\?q=[\d\.,\-]+)')
CONTACT = re.compile(r'^\s+\[КОНТАКТ\] (.+\.vcf)$')
DELETED = re.compile(r'^\s+\[УДАЛЕНО\]$')
FORWARDED = re.compile(r'^\s+\[ПЕРЕСЛАНО\]$')

# Извлечение данных
PHONE = re.compile(r'\+?(\d{1,3}[-\s]?\d{2,3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})')
EMAIL = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
URL = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
IBAN = re.compile(r'[A-Z]{2}\d{2}[A-Z0-9]{4,30}')
CARD = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
```

---

## Нормализация телефонов

```
Входные форматы:
+971 50 123 4567
971-50-123-4567
00971501234567
+7 (961) 459-81-81
89614598181

Выходной формат:
+971501234567
+79614598181
```

---

## Определение страны по коду телефона

| Код | Страна |
|-----|--------|
| +971 | ОАЭ |
| +7 | Россия/Казахстан |
| +1 | США/Канада |
| +44 | Великобритания |
| +966 | Саудовская Аравия |

---

## Извлечение сумм и валют

| Паттерн | Пример | Регулярка |
|---------|--------|-----------|
| AED | `1500 AED` | `(\d[\d\s,\.]*)\s*AED` |
| USD | `$500` | `\$(\d+)` |
| RUB | `50000₽` | `(\d+)\s*[₽руб]` |

---

## Криптовалюта

| Сеть | Паттерн |
|------|---------|
| USDT TRC20 | `T[A-Za-z0-9]{33}` |
| USDT ERC20 | `0x[a-fA-F0-9]{40}` |

---

## Ключевые слова классификации

### Бизнес

```python
BUSINESS_KEYWORDS = [
    "экскурсия", "тур", "трансфер", "яхта", "билет",
    "цена", "стоимость", "оплата", "бронь"
]
```

### Личные (пропускаем)

```python
PERSONAL_KEYWORDS = [
    "мама", "папа", "брат", "сестра",
    "семья", "др", "люблю"
]
```

---

## Паттерн диалога заказа

```
1. Запрос: "сколько стоит экскурсия?"
2. Ответ: "1200 AED на 4 человека"
3. Согласие: "давайте забронируем"
4. Детали: "25 января, отель Atlantis"
5. Подтверждение: "бронь подтверждена"
6. Оплата: "оплата получена"
```

---

## Поиск рефералов

```
Паттерны:
- "от [Имя]"
- "по рекомендации"
- "[Имя] посоветовал"
- Прислан VCF контакт
```

---

## Фазы парсинга (обновлённый пайплайн)

**Параллельные фазы** (запускаются одновременно через команду агентов):

- [ ] Фаза 1: Базовый парсинг (chat.txt → JSONL) — дедупликация бизнес/личный
- [ ] Фаза 2: Извлечение сущностей (телефоны, даты, суммы, крипто, банк.реквизиты)
- [ ] Фаза 3: Транскрипция голосовых (faster-whisper medium/large-v3 + автокоррекция)
- [ ] Фаза 4: Анализ PDF/документов (pdfplumber → классификация + извлечение)
- [ ] Фаза 5: OCR изображений (скриншоты оплат, паспорта, чеки)
- [ ] Фаза 6: Парсинг VCF контактов (дедупликация, страна по коду)
- [ ] Фаза 7: Граф связей (рефералы, VCF-пересылки, семья, агент-клиент)
- [ ] Фаза 8: Качество обслуживания (SLA, время ответа, тональность)
- [ ] Фаза 9: **Полный текстовый чат** (мердж всего контента inline)

**Зависимости:** Фазы 1-6 параллельны. Фаза 7-8 требует Фазу 1. Фаза 9 требует ВСЕ предыдущие.

---

## Концепция "Полный текстовый чат"

**Ключевая идея:** Финальный Markdown-файл, где КАЖДОЕ вложение раскрыто текстом. Вместо `[ДОКУМЕНТ] invoice.pdf` — содержимое инвойса. Вместо `[ГОЛОСОВОЕ]` — транскрипция. Вместо `[ФОТО]` — OCR текст.

**Пример:**

```
[26.01.2024 10:30] Сухейль:
  Вот инвойс за трансфер

  📄 [ДОКУМЕНТ] invoice_101524.pdf:
  ┌──────────────────────────────────
  │ INVOICE #INV-2024-0153
  │ Marsel Luxury Car Rental LLC
  │ Client: Иван Петров
  │ Service: Airport Transfer (DXB → JBR)
  │ Amount: 350 AED
  │ Date: 2024-01-26
  └──────────────────────────────────

[26.01.2024 10:31] Марсель:
  🎤 [ГОЛОСОВОЕ] 45 сек:
  «Окей, получил. Скажи клиенту что водитель будет
   у терминала 3 в 14:00, белый Лексус, номер D 45821»

[26.01.2024 10:33] Сухейль:
  📷 [ФОТО] screenshot_payment.jpg:
  ┌──────────────────────────────────
  │ Скриншот оплаты Сбербанк
  │ Получатель: Ганеев С.
  │ Сумма: 25,000 ₽
  │ Дата: 26.01.2024
  └──────────────────────────────────
```

**Источники текста для каждого типа медиа:**

| Тип медиа | Источник текста | Инструмент |
|-----------|----------------|------------|
| Голосовые (.opus) | Транскрипция | faster-whisper (medium/large-v3) |
| PDF с текстом | Извлечение текста | pdfplumber / pypdf |
| PDF-сканы (без текста) | OCR | Yandex Vision / Tesseract |
| Фото (скриншоты оплат) | OCR → извлечение сумм | /ocr-туризм |
| Фото (паспорта) | OCR → MRZ | /ocr-туризм |
| Фото (бронирования) | OCR → confirmation | /ocr-туризм |
| VCF контакт | Парсинг vCard | vobject / regex |
| Локация | Координаты + адрес | Google Maps reverse geocode |

**Результат:** Полностью читаемый и поисковый чат без необходимости открывать отдельные файлы.

---

## JSON схемы

Схемы данных: message, contact, chat_metadata, message JSONL, ExtractedDateTime, session, payment, hotel_booking, contact_graph.

**Подробно:** [references/json-schemas.md](references/json-schemas.md)

---

## Скрипты

### parsing/ — Извлечение данных (16 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `parse_all_chats.py` | 3050 chat.txt | all_messages.jsonl | **Главный парсер** — обходит все папки, парсит chat.txt |
| `parse_vcf.py` | *.vcf файлы | vcf_contacts.json | Парсинг контактов из VCF |
| `parse_vcf_advanced.py` | *.vcf файлы | vcf_full.json | Расширенный парсинг с фото |
| `extract_contacts.py` | all_messages.jsonl | contacts.json | Извлечение уникальных контактов |
| `extract_urls.py` | all_messages.jsonl | urls.json | Все ссылки из сообщений |
| `extract_emails.py` | all_messages.jsonl | emails.json | Email адреса |
| `extract_locations.py` | all_messages.jsonl | locations.json | Геолокации |
| `extract_banking.py` | all_messages.jsonl | banking.json | IBAN, карты, реквизиты |
| `extract_datetime.py` | all_messages.jsonl | datetime_mentions.json | Упоминания дат и времени |
| `extract_forwarded.py` | all_messages.jsonl | forwarded.json | Пересланные сообщения |
| `extract_operations.py` | all_messages.jsonl | operations_raw.json | Туры, трансферы, заказы |
| `extract_requisites.py` | all_messages.jsonl | requisites.json | Банковские реквизиты |
| `extract_todos.py` | all_messages.jsonl | todos.json | Задачи и напоминания |
| `extract_patterns.py` | all_messages.jsonl | patterns.json | Паттерны общения |
| `extract_price_inquiries.py` | all_messages.jsonl | price_inquiries.json | Запросы цен |
| `extract_travel_dates.py` | all_messages.jsonl | travel_dates.json | Даты поездок |

### analysis/ — Анализ данных (11 скриптов)

| Скрипт | Вход | Выход | Описание |
|--------|------|-------|----------|
| `chat_statistics.py` | all_messages.jsonl | statistics.json | Общая статистика по чатам |
| `analyze_emoji.py` | all_messages.jsonl | emoji_stats.json | Статистика использования эмодзи |
| `analyze_words.py` | all_messages.jsonl | word_frequency.json | Частотный анализ слов |
| `analyze_activity_time.py` | all_messages.jsonl | activity_time.json | Активность по часам/дням |
| `analyze_message_length.py` | all_messages.jsonl | message_length.json | Распределение длины сообщений |
| `analyze_trends.py` | all_messages.jsonl | trends.json | Тренды по периодам |
| `detect_language.py` | all_messages.jsonl | languages.json | Определение языка сообщений |
| `detect_spam.py` | all_messages.jsonl | spam_candidates.json | Обнаружение спама |
| `detect_groups.py` | all_messages.jsonl | groups_analysis.json | Анализ групповых чатов |
| `find_duplicates.py` | contacts.json | duplicates.json | Поиск дублей контактов |
| `contact_graph.py` | all_messages.jsonl | contact_graph.json | Граф связей между контактами |

### utils/ — Утилиты (4 скрипта)

| Скрипт | Описание |
|--------|----------|
| `config.py` | **Главный конфиг** — пути, схемы, константы |
| `mask_data.py` | Маскирование персональных данных (GDPR) |
| `search.py` | Полнотекстовый поиск по сообщениям |
| `diff_chats.py` | Сравнение двух экспортов чатов |

---

## Использование

### Полный пайплайн парсинга

```bash
# 1. Парсинг всех чатов в JSONL
python scripts/parsing/parse_all_chats.py

# 2. Извлечение контактов
python scripts/parsing/extract_contacts.py

# 3. Базовая статистика
python scripts/analysis/chat_statistics.py

# 4. Извлечение специфичных данных
python scripts/parsing/extract_operations.py
python scripts/parsing/extract_requisites.py
python scripts/parsing/extract_locations.py
```

### Примеры использования в коде

```python
from scripts.utils.config import PATHS, load_messages
from scripts.analysis.chat_statistics import calculate_stats

# Загрузка сообщений
messages = load_messages(PATHS['all_messages'])

# Расчёт статистики
stats = calculate_stats(messages)
print(f"Всего сообщений: {stats['total_messages']}")
print(f"Уникальных контактов: {stats['unique_contacts']}")
```

### Поиск по сообщениям

```python
from scripts.utils.search import search_messages

# Поиск упоминаний Ferrari World
results = search_messages(
    query="Ferrari World",
    date_from="2025-01-01",
    date_to="2026-01-26"
)

for msg in results:
    print(f"{msg['datetime']} | {msg['sender']}: {msg['text'][:50]}...")
```

---

## Конфигурация (config.py)

```python
# Пути к данным
PATHS = {
    'export_personal': 'D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Личный/',
    'export_business': 'D:/Downloads/Туризм-ОАЭ-Проект/01-Исходные-данные/WhatsApp-Бизнес/',
    # Legacy (старые пути, не используются):
    # 'export_personal': 'D:/Downloads/экспорт чатов с ватсапа/',
    # 'export_business': 'D:/Downloads/экспорт чатов с ватсап бизнеса/',
    'output_dir': 'D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/',
    'all_messages': 'D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/жсонл/all_messages_enriched.jsonl',
    'contacts': 'D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/контакты/vcf_contacts.json',
    'metadata': 'D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/метаданные/chat_metadata.json',
}

# Источники данных
SOURCES = {
    'whatsapp': {
        'path': PATHS['export_personal'],
        'label': 'WhatsApp Personal',
        'count': 1063,
        'folder_format': 'Имя контакта/группы_JID'  # напр: SUKHEIL & MARSEL BROTHERS_120363196829914006
    },
    'wa_business': {
        'path': PATHS['export_business'],
        'label': 'WhatsApp Business',
        'count': 1987,
        'folder_format': 'Имя контакта/группы_JID'
    }
}
```

---

## Обработка ошибок

### Частые проблемы парсинга

| Проблема | Причина | Решение |
|----------|---------|---------|
| Битая кодировка | Эмодзи, арабский текст | UTF-8 с errors='replace' |
| Многострочные сообщения | Переносы в тексте | Склейка до следующего `[дата]` |
| Отсутствует JID | Старый формат экспорта | Генерация из имени папки |
| Дубли сообщений | Повторный экспорт | Дедупликация по datetime+sender+text |

### Логирование

```python
import logging

logging.basicConfig(
    filename='D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/логи/parsing.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
```

---

## Полный пайплайн обработки клиентского чата

8-этапный пайплайн для углубленной обработки отдельного клиента:

1. **Парсинг** — `parse_client_chat.py --jid 971XXXXXXXXX` (текст + метаданные медиа)
2. **Транскрибация** — faster-whisper (large-v3 GPU / medium CPU), автодетект языка
3. **Исправление ошибок** — словарь корректировок имён, топонимов, терминов
4. **Пунктуация** — DeepPavlov RuBERT (для SpeechKit транскрипций без пунктуации)
5. **Объединение** — мердж текстовых + транскрипций в единый JSON
6. **Анализ медиа** — классификация фото/видео/документов + опциональный OCR
7. **Досье клиента** — профиль, стиль общения, история заказов, LTV
8. **Экспорт** — Markdown с группировкой по датам

**Подробно (код всех этапов + примеры):** [references/client-pipeline.md](references/client-pipeline.md)

---

## Кейс: Фарход-Досье

**Полный цикл обработки реального клиента (2023-2026)**

**Расположение:** `D:/Downloads/Фарход-Досье/`

### Структура проекта

```
Фарход-Досье/
├── output/              # Финальные результаты
│   ├── farkhod_complete_chat.json (4.5 MB)
│   ├── farkhod_complete_chat.md (1.8 MB)
│   ├── farkhod_transcriptions.json (1.9 MB)
│   ├── FINAL_REPORT.md
│   ├── CORRECTIONS_REPORT.md (798 KB)
│   ├── ДОСЬЕ_ФАРХОД.md
│   └── АНАЛИЗ_МЕДИА_ФАРХОДА.md
├── source/              # Исходные данные
│   ├── farkhod_messages_all.json
│   ├── farkhod_messages_business.json
│   ├── farkhod_messages_personal.json
│   ├── farkhod_chat_path.txt
│   └── files_to_transcribe.json
├── scripts/             # Python скрипты обработки
│   ├── parse_farkhod_chat.py
│   ├── batch_transcribe_speechkit.py
│   ├── transcribe_missing.py
│   ├── merge_chat_with_transcriptions.py
│   ├── add_punctuation.py
│   ├── create_dossier.py
│   ├── analyze_communication_style.py
│   └── export_chat_to_md.py
├── logs/                # Логи обработки
│   ├── transcription_missing.log
│   ├── transcription_log.txt
│   └── batch_runner.log
└── backups/             # Резервные копии
    ├── farkhod_complete_chat_backup_*.json
    └── farkhod_transcriptions_backup.json
```

### Статистика обработки

| Метрика | Значение |
|---------|----------|
| Период переписки | 03.02.2023 — 24.01.2026 (3 года) |
| Всего сообщений | 5,314 |
| Текстовых | 3,178 (59.8%) |
| Голосовых | 2,136 (40.2%) |
| Транскрибировано | 2,105 (98.5%) |
| Исправлено ошибок | 657 (31.2% транскрипций) |
| Медиафайлов | 180+ (фото, видео, документы) |
| Размер данных | 10+ MB |

### Применённые улучшения

1. **Исправление ошибок распознавания**
   - Словарь: 25 корректировок
   - Категории: имена (11), топонимы (8), термины (6)
   - Покрытие: 657 исправлений

2. **Добавление пунктуации**
   - Обработано: 2,105 транскрипций
   - Модель: DeepPavlov RuBERT
   - Результат: запятые, точки, заглавные буквы

3. **Анализ медиа**
   - Фото: 155 файлов
   - Видео: 16 файлов
   - Документы: 9 файлов (PDF, DOCX)

### Ключевые инсайты

- **Профиль:** Постоянный клиент, русскоязычный
- **Продукты:** Сафари в пустыне, трансферы, экскурсии
- **География:** Дубай, Шарджа, Абу-Даби
- **Стиль:** Дружеский, использует голосовые (40%)
- **Частота:** 1-2 заказа в месяц
- **Средний чек:** 800-1,500 AED

### Применение данных

1. **CRM интеграция** — импорт профиля и истории заказов
2. **AI-агент обучение** — примеры успешных диалогов продаж
3. **Аналитика продаж** — паттерны покупательского поведения
4. **Персонализация** — индивидуальные предложения на основе истории

**Статус:** ✅ Полностью завершено (см. [CONTACTS_TRACKER.md](CONTACTS_TRACKER.md))

---

### Кейс: SUKHEIL & MARSEL BROTHERS (группа + личный чат)

**Полный цикл обработки семейной рабочей группы и личного чата (2023-2026)**

**Расположение:** `D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/sukheil_marsel_brothers/` и `marsel_personal/`

#### Источники данных

| Чат | Тип | Сообщений | Голосовых | PDF | Фото | VCF |
|-----|-----|-----------|-----------|-----|------|-----|
| SUKHEIL & MARSEL BROTHERS (группа) | Бизнес + Личный | 26,317 | 1,413 | 686 | 2,409 | 4,292 |
| Марсель (личный) | Бизнес + Личный | 9,775 | 1,276 | 187 | 765 | 2,165 |

#### Участники группы

| Участник | Сообщений | % | Роль |
|----------|-----------|---|------|
| Сухейль | 17,789 | 67.6% | Экскурсии, билеты |
| Марсель | 4,731 | 18.0% | Аренда авто, яхты |
| Мадина | 1,515 | 5.8% | Ассистент |
| VIP_DXB_RUS | 244 | 0.9% | Бот |

#### Результаты обработки

| Анализ | Группа | Личный чат |
|--------|--------|------------|
| Качество (грейд) | A+ (92) | A+ (90) |
| Медиана ответа Сухейль | 0.4 мин | 0.4 мин |
| AED оборот | 2,985,012 | 2,993,749 |
| RUB оборот | 25,085,415 | 3,945,895 |
| Телефонов уникальных | 129 | 80 |
| Реферальных связей | 150 | - |
| Узлов в графе | 162 | - |
| Крипто-адресов (TRC20) | 7 | 5 |
| Банковских карт | 47 | - |

#### Инструменты и подход

- **Парсинг:** Python скрипт, дедупликация бизнес/личный экспорт
- **Транскрипция:** faster-whisper medium, автодетект языка, checkpoint/resume
- **PDF:** pdfplumber, классификация по 8 типам (invoice, receipt, contract, booking, passport, visa, license, other)
- **VCF:** Regex парсинг vCard, определение страны по коду
- **Сущности:** Regex извлечение телефонов, сумм (AED/RUB/USD/USDT), email, URL, IBAN, карт, крипто
- **Качество:** SLA, время ответа, тональность, грейды A+-D
- **Граф связей:** Рефералы, VCF-пересылки, семья, агент-клиент, кластеры

#### Выходные файлы

```
sukheil_marsel_brothers/
├── messages.jsonl           # 26,317 сообщений (14 MB)
├── chat_metadata.json       # Метаданные
├── participants.json        # 5 участников
├── media_index.json         # 10,412 медиа (3.7 MB)
├── transcriptions.jsonl     # Транскрипции голосовых
├── documents_analysis.jsonl # 688 PDF классифицированы
├── contacts_vcf.json        # 30 уникальных контактов
├── contact_graph.json       # 162 узла, 5,483 связи
├── referral_report.md       # Реферальный отчёт
├── quality_analysis.json    # SLA, грейды
├── quality_report.md        # Отчёт качества
├── entities/                # Телефоны, суммы, email, URL, крипто
└── scripts/                 # Все скрипты обработки

marsel_personal/
├── messages.jsonl           # 9,775 сообщений
├── chat_metadata.json
├── media_index.json
├── transcriptions.jsonl     # Транскрипции голосовых
├── documents_analysis.jsonl # 187 PDF
├── contacts_vcf.json        # 15 контактов
├── quality_analysis.json
├── quality_report.md
├── entities/
└── scripts/
```

**Статус:** 🚧 В процессе (транскрипция голосовых, OCR изображений, финальный мердж)

---

## OCR для медиафайлов

Автоматическое распознавание текста на изображениях при парсинге: чеки/скриншоты оплат, паспорта, бронирования. Включает классификацию типов изображений, интеграцию с `enhanced_parse_chat()`, и суммирование оплат.

**Подробно (код + примеры):** [references/ocr-integration.md](references/ocr-integration.md)

**См. скилл:** `/ocr-туризм` — полная документация по OCR

---

## Связанные скиллы

| Скилл | Использует | Для чего |
|-------|------------|----------|
| **туризм-оаэ-бизнес** | contacts.json, operations_raw.json | CRM, профили клиентов |
| **туризм-оаэ-автоматизация** | all_messages.jsonl | AI классификация, автоответы |
| **giga-transcribe-туризм** | голосовые сообщения | Транскрипция русскоязычных голосовых |
| **ocr-туризм** | изображения из media/ | Распознавание текста на изображениях (чеки, паспорта) |
| **limo-order-manager** | VIP Transfer Blank, CRM данные | Управление лимузинными заказами, подбор партнёра |

## Трекер обработки контактов

**Файл:** [CONTACTS_TRACKER.md](CONTACTS_TRACKER.md)

### Завершённые обработки

| # | Чат/Контакт | Тип | Сообщений | Голосовых | Транскрипция | PDF | Период | Результат |
|---|-------------|-----|-----------|-----------|-------------|-----|--------|-----------|
| 1 | **Фарход** | Личный (2 аккаунта) | 5,314 | 2,136 | 98.5% SpeechKit | 9 | 2023-2026 | `D:/Downloads/Фарход-Досье/` |
| 2 | **Лимузинные партнёры** (Raja + TJ) | 3 группы | 11,016 | - | - | - | 2021-2026 | `D:/MARSEL_BUSINESS/` |
| 3 | **Anna (Обмен)** | Личный (ZIP-экспорт) | ~200 | ~30 | - | ~5 | 2025 | `D:/Downloads/Anna_chat_extracted/` |

### В процессе

| # | Чат/Контакт | Тип | Сообщений | Голосовых | Транскрипция | PDF | Фото | Статус |
|---|-------------|-----|-----------|-----------|-------------|-----|------|--------|
| 4 | **SUKHEIL & MARSEL BROTHERS** | Группа (2 аккаунта) | 26,317 | 1,413 | ~82% faster-whisper | 686 | 2,409 | Транскрипция + OCR |
| 5 | **Марсель** (личный) | Личный (2 аккаунта) | 9,775 | 1,276 | ~10% faster-whisper | 187 | 765 | Транскрипция |

**Результаты "В процессе":**
- Группа: `D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/sukheil_marsel_brothers/`
- Марсель: `D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/marsel_personal/`

**Что уже сделано для обоих:**
- Парсинг chat.txt (дедупликация бизнес/личный)
- Извлечение сущностей (телефоны, суммы, email, крипто)
- Анализ PDF/документов (классификация по типам)
- Парсинг VCF контактов
- Граф связей (группа: 162 узла, 5,483 связи)
- Качество обслуживания (группа: A+ 92 балла, личный: A+ 90)

**Что осталось:**
- Завершить транскрипцию голосовых (faster-whisper)
- OCR изображений (скриншоты оплат, паспорта, чеки)
- Финальный мердж → "Полный текстовый чат" (все медиа раскрыты inline)

### Запланировано

- 📋 Пусто

### Статистика по всем обработкам

| Метрика | Значение |
|---------|----------|
| Обработано чатов | 5 (из 3,050) |
| Сообщений обработано | ~52,622 |
| Голосовых транскрибировано | ~4,000+ |
| PDF проанализировано | ~880 |
| VCF спаршено | ~6,500 |

**Используй трекер для:**
- Отслеживания статуса обработки клиентов
- Просмотра статистики (сообщения, транскрипции, медиа)
- Доступа к созданным файлам и отчетам
- Планирования следующих обработок

---

## Архитектура безопасности

Парсер — первый уровень в системе безопасности данных:

```
Парсер (этот скилл)          →  Агенты (/правила-ai-агентов)
• Определяет ЧТО является PII    • Определяет КТО видит PII
• Классифицирует данные          • Фильтрует под профиль агента
• Хранит полные данные           • Маскирует при передаче
```

**Подробная схема:** см. `/правила-ai-агентов` → раздел "Архитектура безопасности данных"

**Файлы безопасности в этом скилле:**
- `references/pii-classification.md` — классификация PII, regex паттерны, стратегии маскирования
- `utils/mask_data.py` — скрипт маскирования для экспорта

---

## Производительность

| Операция | Время | Память |
|----------|-------|--------|
| Парсинг 3050 чатов | ~5-10 мин | ~2 GB |
| Извлечение контактов | ~1 мин | ~500 MB |
| Полнотекстовый поиск | ~10 сек | ~1 GB |

**Рекомендации:**
- Используйте SSD для быстрого I/O
- Запускайте парсинг с `--batch-size 100` для экономии памяти
- Результаты кэшируются в JSONL для повторного использования

---

## Аналитика на масштабе (Фаза I-II)

9 скриптов для анализа всех 880K сообщений и 3,220 контактов:

| Скрипт | Выход | Описание |
|--------|-------|----------|
| `build_contact_graph_full.py` | `contact_graph_full.json` (224K узлов, 151 MB) | Граф связей через NetworkX: betweenness centrality (k=500 sampling), BFS кластеризация |
| `analyze_quality_full.py` | `quality_all_chats.json` | SLA, время ответа, грейды A+-D для 1,865 чатов |
| `analyze_funnel.py` | `funnel_analysis.json` | Воронка продаж 8 стадий, 2,133 чатов проанализировано |
| `analyze_finance.py` | `finance_report.json` | Финансовый анализ: 48K записей, 4 валюты (AED/USD/RUB/USDT), ~90M AED |
| `search.py` | `search_index.db` (322 MB) | SQLite FTS5 полнотекстовый поиск: 773K записей (text+voice+ocr+pdf), <0.1 сек |
| `enrich_contacts.py` | `contacts_master_v2.json` | 11 новых полей, 97.9% контактов обогащено |
| `export_crm.py` | `crm_export.csv` + `.json` | Экспорт 3,220 контактов для CRM систем |
| `build_training_data.py` | `training_data.jsonl` | 719 диалогов для обучения AI-агента |
| `update_summary.py` | `SUMMARY.md` | Автогенерация итогового отчёта по всем данным |

---

## Воронка продаж (Sales Funnel)

### Этапы воронки

```
ЗАПРОС → ИНТЕРЕС → ПРЕДЛОЖЕНИЕ → БРОНЬ → ОПЛАТА → ВЫПОЛНЕНО
 100%      70%        50%          25%    20%       18%
```

| Этап | Маркеры | Паттерны regex |
|------|---------|----------------|
| ЗАПРОС | Первое обращение | `хочу`, `сколько стоит`, `интересует` |
| ИНТЕРЕС | Уточнение деталей | `а если`, `подробнее`, `какие варианты` |
| ПРЕДЛОЖЕНИЕ | КП отправлено | `предлагаю`, `стоимость составит`, `\d+ AED` |
| БРОНЬ | Подтверждение | `бронирую`, `давайте`, `согласен` |
| ОПЛАТА | Деньги получены | `оплатил`, `чек`, `платеж получен` |
| ВЫПОЛНЕНО | Услуга оказана | `спасибо за`, `понравилось` |

### Причины выхода из воронки

| Причина | Паттерны |
|---------|----------|
| price_too_high | `дорого`, `нашли дешевле`, `не по карману` |
| dates_unavailable | `планы изменились`, `перенесли` |
| competitor_chosen | `уже забронировали`, `у других` |
| trip_cancelled | `отменили поездку`, `не дали визу` |

---

## Граф связей контактов

### Типы связей

| Тип | Источник | Вес |
|-----|----------|-----|
| `referral` | "от [Имя]", "порекомендовал" | 3.0 |
| `family` | "муж/жена/брат", общие бронирования | 5.0 |
| `colleague` | Общий email домен, компания | 2.5 |
| `agent_client` | "мой клиент", бронирования через агента | 2.0 |
| `group_membership` | Общие групповые чаты | 1.0 |
| `vcf_share` | Отправка VCF контакта | 2.0 |

### Реферальные паттерны

```python
REFERRAL_PATTERNS = [
    r'от\s+([А-Яа-яЁё]+)',
    r'по\s+рекомендации\s+([А-Яа-яЁё]+)',
    r'посоветовал[аи]?\s+([А-Яа-яЁё]+)',
    r'referred\s+by\s+([A-Za-z]+)',
]
```

### JSON структура графа

```json
{
  "nodes": [{"id": "+971501234567", "name": "Иван", "type": "client"}],
  "edges": [{"source": "+971...", "target": "+971...", "type": "referral", "weight": 3.0}],
  "clusters": [{"id": "cluster_0", "members": [...], "nature": "referral_chain"}]
}
```

---

## Мультиязычный парсинг

### Определение языка

```python
RUSSIAN_PATTERN = r'[а-яА-ЯёЁ]+'
ENGLISH_PATTERN = r'[a-zA-Z]+'
ARABIC_PATTERN = r'[\u0600-\u06FF\u0750-\u077F]+'
```

### Транслит → Кириллица

```python
TRANSLIT = {
    'privet': 'привет', 'skolko': 'сколько', 'stoit': 'стоит',
    'hochu': 'хочу', 'zabronirovat': 'забронировать',
    'spasibo': 'спасибо', 'zavtra': 'завтра',
}
```

### Арабские цифры

```python
ARABIC_NUMERALS = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                   '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}
```

### Валюты на разных языках

```python
CURRENCIES = {
    '$': 'USD', '€': 'EUR', '₽': 'RUB', 'د.إ': 'AED',
    'дирхам': 'AED', 'درهم': 'AED', 'рублей': 'RUB',
}
```

---

## Метрики качества обслуживания

### Время ответа (Response Time)

```python
SLA_THRESHOLDS = {
    'first_response_minutes': 15,    # FRT < 15 минут
    'regular_response_minutes': 60,  # Обычный ответ < 1 час
    'working_hours': (9, 21),        # 9:00-21:00
}
```

### Индикаторы проблем

```python
COMPLAINT_MARKERS = {
    'strong': [r'ужасн', r'кошмар', r'обман', r'верн[иу]те\s+деньги'],
    'medium': [r'проблем', r'плохо', r'недовол', r'ошибк'],
    'weak': [r'долго\s+ждать', r'почему\s+так\s+долго'],
}
```

### Позитивные маркеры (удовлетворённость)

```python
POSITIVE_MARKERS = [
    r'спасибо', r'благодар', r'отлично', r'супер',
    r'рекомендую', r'обращусь\s+ещё', r'вернусь',
]
```

### Грейды качества

| Балл | Грейд | Описание |
|------|-------|----------|
| 90-100 | A+ | Превосходное обслуживание |
| 85-89 | A | Отличное обслуживание |
| 80-84 | A- | Очень хорошее обслуживание |
| 75-79 | B+ | Хорошее обслуживание |
| 70-74 | B | Удовлетворительное обслуживание |
| < 70 | C-D | Требует улучшения |

---

## Парсинг финансовых данных

### Паттерны цен

```regex
# Основные валюты
(?P<amount>[\d\s,.]+)\s*(?P<currency>AED|USD|\$|EUR|€|руб|₽|RUB|KZT|₸|USDT)

# За человека / за группу
(?P<amount>\d+)\s*(?P<currency>AED|USD|\$)\s*(?:за|per)\s*(?P<unit>чел|человека|pax|группу)
```

### Паттерны оплат

```regex
# Факт оплаты
(?:оплатил|оплачено|paid|перев[её]л|получил\s+оплату)[\s:]*(?P<amount>[\d\s,.]+)[\s]*(?P<currency>AED|USD|\$|руб)?

# Предоплата
(?:предоплата|аванс|deposit)[\s:]*(?P<amount>\d+)
```

### Паттерны комиссий

```regex
# Процент комиссии
(?:комисс\w+|commission|ваш\w*\s+%)[\s:]*(?P<percent>\d+)[\s]*%

# Нетто/Брутто
(?:нетто|net)[\s:]*(?P<net>\d+).*?(?:брутто|gross)[\s:]*(?P<gross>\d+)
```

### JSON структура платежа

```json
{
  "payment": {
    "amount": 500,
    "currency": "USD",
    "method": "card",
    "type": "partial",
    "percentage_paid": 50,
    "remaining": 500
  }
}
```

### Unit Economics формулы

```python
aov = total_revenue / total_orders          # Средний чек
ltv = aov * avg_orders * gross_margin       # Lifetime Value
cac = marketing_spend / new_customers       # Acquisition Cost
ltv_cac_ratio = ltv / cac                   # Должно быть > 3
```

---

## Извлечение сущностей (Named Entity Recognition)

### Отели ОАЭ

```python
HOTELS_UAE = {
    "atlantis": {"canonical": "Atlantis The Palm", "city": "Dubai", "stars": 5},
    "burj al arab": {"canonical": "Burj Al Arab", "city": "Dubai", "stars": 5},
    "emirates palace": {"canonical": "Emirates Palace", "city": "Abu Dhabi", "stars": 5},
    "jw marriott": {"canonical": "JW Marriott Marquis", "city": "Dubai", "stars": 5},
    # ... и другие
}
```

### Типы номеров

```python
ROOM_TYPES = {
    "стандарт": "Standard Room", "делюкс": "Deluxe Room",
    "сьют": "Suite", "люкс": "Suite",
    "сивью": "Sea View Room", "вид на море": "Sea View Room",
}
```

### Паттерны периодов проживания

```regex
# "с 15 по 20 января"
с\s*(\d{1,2})\s*по\s*(\d{1,2})\s*(января|февраля|...)

# "15-20 января"
(\d{1,2})\s*[-–]\s*(\d{1,2})\s*(января|февраля|...)

# Количество ночей
(\d+)\s*(ноч[еиь]й?|nights?|n(?:ts)?)
```

### Туристические продукты

```python
PRODUCTS_UAE = {
    "desert safari": "Сафари в пустыне",
    "ferrari world": "Ferrari World Abu Dhabi",
    "burj khalifa": "Burj Khalifa At The Top",
    "dhow cruise": "Круиз на Доу",
    "abu dhabi tour": "Обзорная Абу-Даби",
}
```

### JSON схема сущности

```json
{
  "entity_type": "hotel_booking",
  "hotel_name": "Atlantis The Palm",
  "city": "Dubai",
  "check_in": "2025-01-15",
  "check_out": "2025-01-20",
  "nights": 5,
  "room_type": "Deluxe Room",
  "guests": {"adults": 2, "children": 1}
}
```

---

## Сессии и диалоги

### Правила разбиения на сессии

| Условие | Результат |
|---------|-----------|
| Gap > 4 часов | Возможно новый диалог (нужна проверка контекста) |
| Gap > 24 часов | Точно новый диалог |
| Смена темы | Новый диалог независимо от времени |

### Результаты диалога

| Результат | Маркеры | Описание |
|-----------|---------|----------|
| `sale` | оплачено, забронировано, подтверждено, сделка | Успешная продажа |
| `rejection` | отказ, дорого, не подходит, передумал, отменить | Клиент отказался |
| `pending` | подумаю, позже напишу, ещё не решил | В процессе решения |

### JSON схема сессии

```json
{
  "session_id": "uuid-v4",
  "jid": "971501234567@s.whatsapp.net",
  "chat_name": "Иван Иванов",
  "started_at": "2026-01-15T10:30:00",
  "ended_at": "2026-01-15T12:45:00",
  "duration_minutes": 135,
  "message_count": 24,
  "messages": ["msg_id_1", "msg_id_2", "..."],
  "topic": "yacht_rental",
  "result": "sale",
  "result_confidence": 0.95,
  "entities_mentioned": ["яхта", "50 футов", "4 часа", "2500 AED"],
  "intents": ["PRICE_REQUEST", "AVAILABILITY_REQUEST", "BOOKING_CONFIRM"],
  "reply_chains": [
    {"reply_id": "msg_003", "reply_to_id": "msg_001"}
  ]
}
```

---

## Паттерны запросов клиентов

### PRICE_REQUEST — Запрос цены

```python
PRICE_REQUEST_PATTERNS = [
    r'сколько\s+стоит',
    r'какая\s+цена',
    r'почём',
    r'во\s+сколько\s+обойд[её]тся',
    r'прайс',
    r'ценник',
    r'стоимость',
    r'how\s+much',
    r'what.*price',
]
```

### AVAILABILITY_REQUEST — Проверка наличия

```python
AVAILABILITY_REQUEST_PATTERNS = [
    r'есть\s+ли',
    r'доступн[оа]',
    r'свободн[оа]',
    r'можно\s+ли',
    r'available',
    r'есть\s+на\s+\d+',
    r'работаете\s+\d+',
]
```

### BOOKING_CONFIRM — Подтверждение бронирования

```python
BOOKING_CONFIRM_PATTERNS = [
    r'бронирую',
    r'подтверждаю',
    r'беру',
    r'давайте',
    r'записывайте',
    r'оформляйте',
    r'да,\s+хочу',
    r'согласен',
    r'договорились',
    r'i\s+confirm',
    r'book\s+it',
]
```

---

## Дополнительные ресурсы

| Файл | Описание |
|------|----------|
| [WORKFLOW.md](WORKFLOW.md) | Подробное описание каждого скрипта и порядок выполнения |
| [references/faq.md](references/faq.md) | Частые вопросы |
| [references/troubleshooting.md](references/troubleshooting.md) | Решение проблем |
| [references/regex-cheatsheet.md](references/regex-cheatsheet.md) | Справочник регулярок |
| [references/funnel-patterns.md](references/funnel-patterns.md) | Паттерны воронки продаж |
| [references/quality-metrics.md](references/quality-metrics.md) | Метрики качества |
| [references/multilingual.md](references/multilingual.md) | Мультиязычный парсинг |
| [references/reply-parsing.md](references/reply-parsing.md) | **Парсинг цепочек сообщений (reply-to)** |
| [references/rejection-patterns.md](references/rejection-patterns.md) | **Паттерны отказов и жалоб** |
| [references/pii-classification.md](references/pii-classification.md) | **Классификация персональных данных (PII/GDPR)** |
| [references/json-schemas.md](references/json-schemas.md) | **JSON схемы всех сущностей (message, contact, chat, session, payment)** |
| [references/ocr-integration.md](references/ocr-integration.md) | **OCR интеграция с парсером (код + примеры)** |
| [references/client-pipeline.md](references/client-pipeline.md) | **8-этапный пайплайн обработки клиента (код всех этапов)** |

### Файлы идей (подробные)

| Файл | Описание |
|------|----------|
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_ВОРОНКА.md` | Полный анализ воронки продаж |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_СВЯЗИ.md` | Граф связей контактов |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_ЯЗЫКИ.md` | Мультиязычный парсинг |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_КАЧЕСТВО.md` | Метрики качества обслуживания |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_ФИНАНСЫ.md` | Парсинг финансовых данных |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_СУЩНОСТИ.md` | Извлечение сущностей (отели, туры, локации) |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_ПРОДВИНУТЫЙ.md` | Сессии, reply-to, интенты |
| `D:/Downloads/Идеи-парсинга/ИДЕИ_ПАРСИНГ_ПАТТЕРНЫ.md` | Паттерны запросов и подтверждений |
