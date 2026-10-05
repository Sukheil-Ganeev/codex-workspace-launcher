# Workflow: WhatsApp Parser

## Обзор процесса

```
Исходные чаты (3050 папок)
        |
    [Парсинг]
        |
  all_messages.jsonl
        |
   [Извлечение]
        |
contacts, locations, banking, etc.
        |
    [Анализ]
        |
статистика, тренды, дубли
```

---

## Этап 1: Парсинг чатов

Основной этап парсинга, преобразующий сырые файлы экспорта WhatsApp в единый формат JSONL.

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `parse_all_chats.py` | 3050 chat.txt из 2 источников | `all_messages.jsonl` | **Главный парсер.** Читает все файлы chat.txt из экспортов WhatsApp и WA Business, парсит заголовки сообщений, текст, медиа, локации, контакты. Создает единый JSONL файл со всеми сообщениями в унифицированном формате. |
| `config.py` | - | - | **Модуль конфигурации.** Определяет все пути (CHATS_DIR, BASE_DIR, JSON_DIR и т.д.), регулярные выражения для парсинга, API ключи, типы контактов. Импортируется всеми остальными скриптами. |

### Детали parse_all_chats.py
- **Вход:** `D:/Downloads/экспорт чатов с ватсапа/` (1063 чата), `D:/Downloads/экспорт чатов с ватсап бизнеса/` (1987 чатов)
- **Выход:** `D:/Downloads/Chats/_база/raw/all_messages.jsonl`, `D:/Downloads/Chats/_база/raw/chat_metadata.json`
- **Зависимости:** `config.py`

---

## Этап 2: Извлечение сущностей

Скрипты, извлекающие различные сущности из базы сообщений.

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `extract_contacts.py` | `all_messages.jsonl` | `contacts.json` | **Агрегация контактов.** Извлекает уникальные контакты по JID, определяет группа/личный чат, извлекает телефон из JID, определяет код страны, детектит язык по частотности слов, объединяет контакты из обоих источников. |
| `extract_urls.py` | `all_messages.jsonl` | `urls.json` | **Извлечение URL.** Находит все ссылки в сообщениях, категоризирует по типу домена (сайты бронирования, соцсети, мессенджеры и т.д.), определяет короткие ссылки, строит статистику URL. |
| `extract_emails.py` | `all_messages.jsonl` | `emails.json` | **Извлечение email.** Находит все email-адреса в сообщениях с помощью regex-паттернов, создает список уникальных email с контекстом (какой контакт, какое сообщение). |
| `extract_locations.py` | `all_messages.jsonl` | `locations.json` | **Извлечение локаций.** Извлекает координаты из пересланных локаций, ссылок Google Maps, названий мест и адресов, строит базу геолокаций. |
| `extract_banking.py` | `all_messages.jsonl` | `banking.json` | **Извлечение банковских реквизитов.** Находит номера карт, IBAN, номера счетов, БИК/SWIFT коды. Маскирует чувствительные данные для безопасности. |
| `extract_requisites.py` | `all_messages.jsonl` | `requisites.json` | **Расширенные реквизиты.** Извлекает полные банковские реквизиты включая ФИО владельца счета, названия банков, назначения платежей. |
| `extract_forwarded.py` | `all_messages.jsonl` | `forwarded.json` | **Анализ пересылок.** Находит пересланные сообщения, определяет источники, строит цепочку пересылок, выявляет популярный контент для рассылки. |
| `extract_operations.py` | `all_messages.jsonl` | `operations.json` | **Извлечение операций.** Находит бизнес-операции: брони, трансферы, туры, оплаты. Извлекает даты, суммы, статусы. |
| `extract_patterns.py` | `all_messages.jsonl` | `patterns.json` | **Детекция паттернов.** Находит повторяющиеся паттерны сообщений, шаблоны, стандартные фразы. Полезно для автоматизации и создания шаблонов. |
| `extract_price_inquiries.py` | `all_messages.jsonl` | `price_inquiries.json` | **Извлечение запросов цен.** Находит запросы цены: "сколько стоит?", "цена?", "стоимость?". Извлекает предмет запроса, ответ агента, предложенную цену. |
| `extract_todos.py` | `all_messages.jsonl` | `todos.json` | **Извлечение задач.** Находит задачи, напоминания, договоренности в сообщениях. Детектит паттерны: "надо", "не забыть", "до завтра". |
| `extract_datetime.py` | `all_messages.jsonl` | `datetimes.json` | **Извлечение дат/времени.** Находит упоминания дат и времени в тексте: "завтра в 10", "15 октября", "на следующей неделе". Нормализует в ISO формат. |
| `multilingual.py` | `all_messages.jsonl` | `multilingual_analysis.json` | **Мультиязычный парсинг.** Определение языка (ru/en/ar), конвертация транслита, нормализация арабских цифр. |
| `extract_financials.py` | `all_messages.jsonl` | `financials.json` | **Парсинг финансов.** Извлечение цен, валют, оплат, скидок, комиссий. |
| `extract_entities.py` | `all_messages.jsonl` | `entities.json` | **Извлечение сущностей.** Отели (80+), туры (30+), аттракционы (40+), типы номеров, даты, PAX. |

### Зависимости скриптов извлечения

Все скрипты извлечения зависят от:
- `config.py` - пути и настройки
- `all_messages.jsonl` - основная база сообщений

---

## Этап 3: Анализ данных

Скрипты для глубокого анализа данных.

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `chat_statistics.py` | `all_messages.jsonl` | `statistics.json` | **Общая статистика.** Количество сообщений, активные контакты, активность по времени, топ собеседников. Базовые метрики по всей базе. |
| `find_duplicates.py` | `contacts.json`, `all_messages.jsonl` | `duplicates.json` | **Поиск дубликатов.** Находит одного человека с разных номеров: fuzzy matching имен, одинаковый email, похожий стиль общения. Нормализация телефонов (+7 vs 8), группировка дубликатов, merge suggestions. |
| `detect_spam.py` | `all_messages.jsonl` | `spam_analysis.json` | **Детекция спама.** Детекция повторяющихся сообщений, массовых рассылок, признаков спама (ссылки, призывы, капс, шаблоны), паттернов ботов. Spam score 0-100, автоматическая маркировка. |
| `contact_graph.py` | `contacts.json`, `all_messages.jsonl` | `contact_graph.json`, `.gexf`, `.html` | **Граф связей контактов.** Построение графа связей (узлы = контакты, ребра = взаимодействия). Типы связей: пересылки, упоминания, общие группы, рефералы, VCF. Метрики: degree centrality, betweenness, PageRank. Кластеризация Louvain. Интерактивная HTML визуализация. |
| `detect_groups.py` | `all_messages.jsonl` | `groups.json` | **Анализ групповых чатов.** Определение группового чата по JID и количеству участников. Извлечение и анализ участников. Определение ролей (Admin, Активные, Читатели). Анализ тематики группы. |
| `detect_language.py` | `all_messages.jsonl` | `language_statistics.json` | **Детекция языка.** Определение языка каждого сообщения (RU, EN, AR, DE, FR и т.д.). Профиль языков контакта (% каждого языка). Обнаружение смешанных сообщений (code-switching). Использует langdetect и lingua-py. |
| `analyze_activity_time.py` | `all_messages.jsonl` | `activity_time_analysis.json`, PNG | **Анализ времени активности.** Распределение по часам, дням недели. Тепловая карта (час x день). Определение "активных часов" контакта. Лучшее время для связи. Выходные vs будни. Визуализация (heatmap, bar charts). |
| `analyze_trends.py` | `all_messages.jsonl` | `trends_analysis.json`, CSV, PNG | **Анализ трендов.** Агрегация по периодам (дни, недели, месяцы). Метрики: сообщения, новые контакты, активные контакты. Рост/падение (% изменения). Выявление сезонности. Прогноз (скользящее среднее). Сравнение периодов (YoY, MoM, WoW). |
| `analyze_words.py` | `all_messages.jsonl` | `word_analysis.json`, PNG | **Частотный анализ слов.** Токенизация сообщений (RU, EN, AR). Удаление стоп-слов. Частотный анализ: топ слов общий, по контакту, по n-grams. TF-IDF для важных терминов. Word Cloud генерация. Тематическое моделирование (LDA). |
| `analyze_emoji.py` | `all_messages.jsonl` | `emoji_analysis.json`, PNG | **Анализ эмодзи.** Извлечение всех эмодзи из сообщений. Частотный анализ по контактам. Sentiment mapping (позитив/негатив/вопрос/нейтрал). Эмодзи-профиль контакта. Тренды использования по времени. |
| `analyze_message_length.py` | `all_messages.jsonl` | `message_length_analysis.json` | **Анализ длины сообщений.** Статистика длины (средняя, медиана, мода) по контактам и времени. Категоризация: короткие/средние/длинные. Соотношение входящие/исходящие. Определение типа общения контакта. |
| `funnel_analysis.py` | `all_messages.jsonl` | `funnel.json` | **Анализ воронки.** 6 этапов воронки, причины выхода, конверсия. |
| `quality_metrics.py` | `all_messages.jsonl` | `quality.json` | **Метрики качества.** FRT, ART, SLA, жалобы, удовлетворенность, грейды A+ до D. |
| `session_analysis.py` | `all_messages.jsonl` | `sessions.json` | **Анализ сессий.** Разбиение на диалоги (gap > 4ч), результат, тема, reply-to. |
| `intent_classifier.py` | `all_messages.jsonl` | `intents.json` | **Классификация интентов.** 12 интентов (PRICE_REQUEST, COMPLAINT...), SLA для каждого. |

### Зависимости скриптов анализа

```
parse_all_chats.py
    |
    +-- all_messages.jsonl
           |
           +-- extract_contacts.py --> contacts.json
           |       |
           |       +-- find_duplicates.py --> duplicates.json
           |       |
           |       +-- contact_graph.py --> graph.json/html/gexf
           |
           +-- extract_*.py --> *.json
           |       (включая multilingual.py, extract_financials.py, extract_entities.py)
           |
           +-- chat_statistics.py --> statistics.json
           |
           +-- detect_spam.py --> spam_analysis.json
           |
           +-- detect_groups.py --> groups.json
           |
           +-- detect_language.py --> language_statistics.json
           |
           +-- analyze_*.py --> *.json, *.png
           |
           +-- funnel_analysis.py --> funnel.json
           |
           +-- quality_metrics.py --> quality.json
           |
           +-- session_analysis.py --> sessions.json
           |
           +-- intent_classifier.py --> intents.json
```

---

## Утилиты

Вспомогательные скрипты для работы с данными.

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `search.py` | Файлы чатов (.md) | Результаты поиска | **Полнотекстовый поиск.** Поиск по тексту, суммам, датам, контактам по всем чатам. Поддерживает regex. Возвращает результаты с контекстом. |
| `diff_chats.py` | Файлы чатов | diff output | **Версионирование и сравнение.** Создает копии чатов, отслеживает изменения. Сравнивает версии, показывает различия. Полезно для отслеживания обновлений переписки. |
| `mask_data.py` | Текст/файлы | Замаскированный текст | **Маскирование данных.** Маскирует карты, телефоны, IBAN, счета. Три уровня маскирования: minimal, standard, strict. Для безопасной передачи данных. |
| `config.py` | - | - | **Центральная конфигурация.** Все пути, паттерны, API ключи, настройки. Импортируется всеми скриптами. Единый источник истины для конфигурации. |

---

## Зависимости

### Главный граф зависимостей

```
config.py (конфигурация)
    |
    +-- parse_all_chats.py (главный парсер)
            |
            +-- all_messages.jsonl
            |       |
            |       +-- extract_contacts.py
            |       |       |
            |       |       +-- contacts.json
            |       |               |
            |       |               +-- find_duplicates.py
            |       |               +-- contact_graph.py
            |       |
            |       +-- extract_urls.py
            |       +-- extract_emails.py
            |       +-- extract_locations.py
            |       +-- extract_banking.py
            |       +-- extract_requisites.py
            |       +-- extract_forwarded.py
            |       +-- extract_operations.py
            |       +-- extract_patterns.py
            |       +-- extract_price_inquiries.py
            |       +-- extract_todos.py
            |       +-- extract_datetime.py
            |       +-- multilingual.py
            |       +-- extract_financials.py
            |       +-- extract_entities.py
            |       |
            |       +-- chat_statistics.py
            |       +-- detect_spam.py
            |       +-- detect_groups.py
            |       +-- detect_language.py
            |       +-- analyze_activity_time.py
            |       +-- analyze_trends.py
            |       +-- analyze_words.py
            |       +-- analyze_emoji.py
            |       +-- analyze_message_length.py
            |       +-- funnel_analysis.py
            |       +-- quality_metrics.py
            |       +-- session_analysis.py
            |       +-- intent_classifier.py
            |
            +-- chat_metadata.json
```

### Python зависимости

```
# Обязательные
- python >= 3.10

# Парсинг (parse_all_chats.py)
- нет внешних зависимостей

# Анализ (опционально, расширяют функциональность)
- fuzzywuzzy          # find_duplicates.py - fuzzy matching имен
- python-Levenshtein  # find_duplicates.py - ускорение fuzzywuzzy
- phonenumbers        # find_duplicates.py - валидация телефонов
- networkx            # contact_graph.py - построение графа
- pyvis               # contact_graph.py - HTML визуализация
- python-louvain      # contact_graph.py - кластеризация
- langdetect          # detect_language.py - детекция языка
- lingua-language-detector  # detect_language.py - точная детекция коротких текстов
- pandas              # analyze_*.py - обработка данных
- numpy               # analyze_*.py - вычисления
- matplotlib          # analyze_*.py - визуализация
- seaborn             # analyze_activity_time.py - тепловые карты
- wordcloud           # analyze_words.py - облака слов
- nltk                # analyze_words.py - токенизация
- scikit-learn        # analyze_words.py - TF-IDF
- gensim              # analyze_words.py - LDA тематическое моделирование
- emoji               # analyze_emoji.py - извлечение эмодзи
```

---

## Примеры запуска

### Полный пайплайн

```bash
# Шаг 1: Парсинг всех чатов
python scripts/parsing/parse_all_chats.py

# Шаг 2: Извлечение контактов
python scripts/parsing/extract_contacts.py

# Шаг 3: Извлечение сущностей
python scripts/parsing/extract_urls.py
python scripts/parsing/extract_emails.py
python scripts/parsing/extract_locations.py
python scripts/parsing/extract_banking.py

# Шаг 4: Анализ
python scripts/analysis/chat_statistics.py
python scripts/analysis/find_duplicates.py
python scripts/analysis/detect_spam.py
python scripts/analysis/contact_graph.py --build --html
```

### Быстрая статистика

```bash
# Получить базовую статистику
python scripts/analysis/chat_statistics.py
```

### Поиск дубликатов контактов

```bash
# Найти дубликаты с авто-объединением при высокой уверенности
python scripts/analysis/find_duplicates.py --auto-merge 0.8
```

### Построение графа контактов

```bash
# Построить граф и экспортировать все форматы
python scripts/analysis/contact_graph.py --build --export-all

# Найти топ influencers
python scripts/analysis/contact_graph.py --build --influencers --top 30

# Анализ конкретного контакта
python scripts/analysis/contact_graph.py --build --analyze --phone +971501234567
```

### Детекция спама

```bash
# Детекция спама с кастомным порогом
python scripts/analysis/detect_spam.py --threshold 50

# Добавить контакт в whitelist
python scripts/analysis/detect_spam.py --add-whitelist "+79123456789"
```

### Поиск

```bash
# Полнотекстовый поиск
python scripts/utils/search.py --text "трансфер в аэропорт"

# Поиск по сумме
python scripts/utils/search.py --amount 5000
```

### Маскирование данных

```bash
# Маскирование чувствительных данных (стандартный уровень)
python scripts/utils/mask_data.py --input chat.md --output chat_masked.md --level standard
```

---

## Директории выхода

```
D:/Downloads/Chats/
    |
    +-- _база/
    |       +-- raw/
    |       |     +-- all_messages.jsonl    # Главная база сообщений
    |       |     +-- chat_metadata.json    # Метаданные чатов
    |       |
    |       +-- json/
    |       |     +-- contacts.json         # Список контактов
    |       |     +-- urls.json             # Извлеченные URL
    |       |     +-- emails.json           # Извлеченные email
    |       |     +-- locations.json        # Извлеченные локации
    |       |     +-- banking.json          # Банковские реквизиты
    |       |     +-- duplicates.json       # Дубликаты контактов
    |       |     +-- spam_analysis.json    # Анализ спама
    |       |     +-- groups.json           # Групповые чаты
    |       |     +-- ...
    |       |
    |       +-- csv/
    |       |     +-- trends_daily.csv
    |       |     +-- trends_weekly.csv
    |       |     +-- ...
    |       |
    |       +-- md/
    |             +-- отчеты...
    |
    +-- _аналитика/
    |       +-- graph/
    |       |     +-- contact_graph.json
    |       |     +-- contact_graph.gexf
    |       |     +-- contact_graph.html
    |       |     +-- influencers.json
    |       |     +-- clusters.json
    |       |
    |       +-- emoji/
    |       +-- activity_heatmap.png
    |       +-- activity_hours.png
    |       +-- trends_*.png
    |       +-- wordcloud_*.png
    |
    +-- клиенты/
    +-- агенты/
    +-- поставщики/
    +-- сотрудники/
```

---

## Заметки

1. **Порядок важен:** Всегда запускайте `parse_all_chats.py` первым, затем `extract_contacts.py`, затем остальные скрипты.

2. **Опциональные зависимости:** Большинство скриптов анализа работают без опциональных библиотек, но с ограниченной функциональностью.

3. **Большие данные:** Для 3050+ чатов с миллионами сообщений обработка может занять несколько минут. Прогресс отображается.

4. **Кодировка:** Все скрипты используют UTF-8. Консоль Windows должна поддерживать вывод UTF-8.

5. **Пути:** Все пути настраиваются в `config.py`. Измените там, если ваши данные в другом месте.
