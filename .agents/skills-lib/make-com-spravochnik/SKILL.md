---
name: make-com-spravochnik
description: "Предоставляет полное руководство по платформе автоматизации Make.com для туристического бизнеса ОАЭ. Make.com, Integromat, сценарии автоматизации, вебхуки, модули, операции."
---
# Make.com (ex-Integromat) -- Полный справочник

## 1. Обзор платформы

Make.com (ранее Integromat) -- визуальная платформа автоматизации, объединяющая 1500+ сервисов. Сценарии строятся из модулей в drag-and-drop редакторе. Каждый выполненный модуль = 1 операция (основная единица тарификации).

**Ключевые концепции:**
- **Сценарий** -- автоматизированный процесс (цепочка модулей)
- **Модуль** -- один шаг сценария (действие, триггер, поиск)
- **Операция** -- выполнение одного модуля с одним bundle данных
- **Bundle** -- пакет данных, проходящий через сценарий
- **Connection** -- авторизованное подключение к сервису

### Тарифы (годовая оплата)

| План | Цена/мес | Операции | Активных сценариев | Мин. интервал | История | Parallel | Data transfer |
|------|----------|----------|--------------------|---------------|---------|----------|---------------|
| Free | $0 | 1,000 | 2 | 15 min | 7 дней | -- | 1 GB |
| Core | $9 | 10,000 | Unlim | 1 min | 30 дней | 2 | 5 GB |
| Pro | $16 | 10,000 | Unlim | 1 min | 60 дней | 5 | Unlim |
| Teams | $29 | 10,000 | Unlim | 1 min | 180 дней | 5 | Unlim |
| Enterprise | Custom | Custom | Unlim | 1 min | 365+ дней | Unlim | Unlim |

**Масштабирование Core:** +10K = $18/мес, +40K (50K total) = $36, +90K (100K total) = $64.

**Рекомендация для Сухейля:** Core ($9/мес, 10K ops) -- достаточно для базовой автоматизации туристического бизнеса.

### Технические лимиты

| Параметр | Значение |
|----------|----------|
| Execution time | 40 мин (Enterprise -- настраиваемо) |
| File size | 50 MB |
| Memory | Free 128MB, Core 256MB, Pro/Teams 512MB |
| Data Store records | Free 500, Core 10K, Pro 50K, Teams 100K |
| Data Store size | Free 1MB, Core 10MB, Pro 100MB |
| Modules per scenario | до 150 |
| Iterator nesting | до 10 уровней |
| Blueprint JSON | до 5 MB |
| Custom variables | до 100 per scenario |

---

## 2. Сценарии -- создание и настройка

### Пошагово

1. **Create a new scenario** -> **+** -> выбрать первый модуль (триггер)
2. Настроить **Connection** (авторизация сервиса)
3. Добавить **action-модули** (действия)
4. Настроить **маппинг** данных между модулями
5. **Run once** (тестовый запуск) -> проверить результат
6. **Toggle ON** -> **Save** (включить сценарий)

### Типы триггеров

| Тип | Описание | Пример | Когда использовать |
|-----|----------|--------|--------------------|
| Instant (Webhook) | Мгновенный, по событию | Telegram Watch Updates | Нужна мгновенная реакция |
| Scheduled (Polling) | По расписанию, проверяет новые данные | Google Sheets Watch Rows | Нет webhook у сервиса |
| Custom Webhook | Пользовательский endpoint | Custom Webhook | Собственные API/формы |

### Типы модулей

- **Trigger** -- запускает сценарий (Watch, Webhook)
- **Action** -- выполняет действие (Create, Update, Delete, Send)
- **Search** -- ищет данные (Search, List, Get)
- **Aggregator** -- объединяет bundles в один (1 op)
- **Iterator** -- разбивает массив на отдельные bundles (0 ops)
- **Transformer** -- преобразует данные

### Connections (авторизация)

| Метод | Когда использовать |
|-------|--------------------|
| OAuth 2.0 | Google, Notion, большинство SaaS (автообновление токенов) |
| API Key | OpenAI, Telegram, простые API |
| Basic Auth | Legacy системы (username:password) |
| Bearer Token | JWT, кастомные API |
| Custom Headers | HMAC-подписи, AWS Signature |

### Routers и Filters

**Router** -- ветвление на параллельные пути. Каждая ветка может иметь Filter (условие). Если несколько веток подходят -- выполнятся ВСЕ подходящие. Ветка без фильтра = fallback. **0 операций.**

**Filter** -- условие между модулями. Операторы: Text (contains, starts with, ends with, regex), Numeric (>, <, =), Date, Boolean. **0 операций.**

### Scheduling

Интервалы: 1 min - 24h. Cron expressions (Pro+). Режимы: Immediately, Once, At regular intervals.

### Blueprints

JSON экспорт/импорт сценариев. Для шаринга, бэкапа, версионирования. Menu (...) -> Export Blueprint.

---

## 3. Данные и маппинг

### Типы данных

Text (string), Number, Boolean, Date, Array, Collection (Object), Buffer (binary).

### Маппинг

Передача данных между модулями через панель маппинга. Синтаксис: `{{1.fieldName}}` (где 1 = номер модуля). Вложенные: `{{1.data.user.name}}`.

### Variables (переменные)

- **Set Variable** -- сохранить значение (0 операций)
- **Get Variable** -- получить значение (0 операций)
- **Set Multiple Variables** -- несколько за 1 операцию

### Data Stores (встроенная БД)

Таблицы с полями. CRUD операции, фильтрация, поиск. Используются для кеширования, очередей, маппингов, логирования, конфигурации.

### Data Structures

Шаблоны для webhook/JSON парсинга. Определяют формат входящих данных. Создание: вручную или автоматически через "Determine data structure".

---

## 4. Функции Make.com

**Синтаксис:** `{{functionName(arg1; arg2; arg3)}}` -- разделитель `;` (точка с запятой), НЕ `,`

**Вложенность:** `{{upper(substring(1.email; 0; indexOf(1.email; "@")))}}`

### Math (математические)

| Функция | Описание | Пример |
|---------|----------|--------|
| `add(a; b)` | Сложение | `{{add(5; 3)}}` -> 8 |
| `sub(a; b)` | Вычитание | `{{sub(10; 4)}}` -> 6 |
| `multiply(a; b)` | Умножение | `{{multiply(3; 4)}}` -> 12 |
| `divide(a; b)` | Деление | `{{divide(20; 4)}}` -> 5 |
| `ceil(n)` | Округление вверх | `{{ceil(4.2)}}` -> 5 |
| `floor(n)` | Округление вниз | `{{floor(4.8)}}` -> 4 |
| `round(n; decimals)` | Округление | `{{round(4.567; 2)}}` -> 4.57 |
| `abs(n)` | Модуль числа | `{{abs(-5)}}` -> 5 |
| `min(a; b; ...)` | Минимум | `{{min(5; 3; 8)}}` -> 3 |
| `max(a; b; ...)` | Максимум | `{{max(5; 3; 8)}}` -> 8 |
| `sum(arr)` | Сумма массива | `{{sum(1.prices)}}` |
| `average(arr)` | Среднее | `{{average(1.scores)}}` |
| `mod(a; b)` | Остаток от деления | `{{mod(10; 3)}}` -> 1 |
| `pow(a; b)` | Степень | `{{pow(2; 3)}}` -> 8 |
| `sqrt(n)` | Квадратный корень | `{{sqrt(16)}}` -> 4 |
| `random(min; max)` | Случайное число | `{{random(1; 100)}}` |
| `parseNumber(str)` | Строка в число | `{{parseNumber("42")}}` -> 42 |

### Text (текстовые)

| Функция | Описание | Пример |
|---------|----------|--------|
| `concat(a; b; ...)` | Объединение | `{{concat("Hello"; " "; "World")}}` |
| `substring(str; start; end)` | Подстрока | `{{substring("Hello"; 0; 2)}}` -> "He" |
| `replace(str; old; new)` | Замена | `{{replace("abc"; "b"; "x")}}` -> "axc" |
| `trim(str)` | Убрать пробелы | `{{trim("  Hi  ")}}` -> "Hi" |
| `lower(str)` | Нижний регистр | `{{lower("HELLO")}}` -> "hello" |
| `upper(str)` | Верхний регистр | `{{upper("hello")}}` -> "HELLO" |
| `capitalize(str)` | Первая заглавная | `{{capitalize("hello")}}` -> "Hello" |
| `length(str)` | Длина строки | `{{length("Hello")}}` -> 5 |
| `indexOf(str; sub)` | Позиция подстроки | `{{indexOf("Hello"; "l")}}` -> 2 |
| `split(str; sep)` | Разбить в массив | `{{split("a,b,c"; ",")}}` -> ["a","b","c"] |
| `join(arr; sep)` | Объединить массив | `{{join(arr; ", ")}}` |
| `contains(str; sub)` | Содержит ли | `{{contains("Hello"; "ell")}}` -> true |
| `startsWith(str; prefix)` | Начинается с | `{{startsWith("Hello"; "He")}}` -> true |
| `endsWith(str; suffix)` | Заканчивается на | `{{endsWith("Hello"; "lo")}}` -> true |

### Date/Time (дата/время)

| Функция | Описание | Пример |
|---------|----------|--------|
| `now` | Текущее время | `{{now}}` |
| `formatDate(date; format)` | Форматирование | `{{formatDate(now; "DD.MM.YYYY")}}` |
| `parseDate(str; format)` | Парсинг строки | `{{parseDate("15.01.2024"; "DD.MM.YYYY")}}` |
| `addDays(date; n)` | Прибавить дни | `{{addDays(now; 7)}}` |
| `addMonths(date; n)` | Прибавить месяцы | `{{addMonths(now; 1)}}` |
| `addYears(date; n)` | Прибавить годы | `{{addYears(now; 1)}}` |
| `addHours(date; n)` | Прибавить часы | `{{addHours(now; 3)}}` |
| `addMinutes(date; n)` | Прибавить минуты | `{{addMinutes(now; 30)}}` |
| `addSeconds(date; n)` | Прибавить секунды | `{{addSeconds(now; 60)}}` |
| `setDate(date; comp; val)` | Установить компонент | `{{setDate(now; "day"; 1)}}` |
| `dateDifference(d1; d2; unit)` | Разница дат | `{{dateDifference(date1; date2; "days")}}` |

**Форматы дат:** `YYYY` (2024), `YY` (24), `MM` (01-12), `DD` (01-31), `HH` (00-23), `mm` (мин), `ss` (сек), `A` (AM/PM), `dddd` (день недели), `MMMM` (месяц словом), `X` (unix sec), `x` (unix ms).

**Для Дубая (UTC+4):** `{{formatDate(now; "DD.MM.YYYY HH:mm"; "Asia/Dubai")}}`

### Array (массивы)

| Функция | Описание | Пример |
|---------|----------|--------|
| `first(arr)` | Первый элемент | `{{first(arr)}}` |
| `last(arr)` | Последний элемент | `{{last(arr)}}` |
| `length(arr)` | Размер массива | `{{length(arr)}}` |
| `add(arr; val)` | Добавить элемент | `{{add(arr; "new")}}` |
| `remove(arr; idx)` | Удалить по индексу | `{{remove(arr; 2)}}` |
| `contains(arr; val)` | Содержит ли | `{{contains(arr; "value")}}` -> true/false |
| `distinct(arr)` | Уникальные | `{{distinct(arr)}}` |
| `reverse(arr)` | Обратный порядок | `{{reverse(arr)}}` |
| `sort(arr)` | Сортировка | `{{sort(arr)}}` |
| `slice(arr; start; end)` | Срез | `{{slice(arr; 0; 3)}}` |
| `merge(arr1; arr2)` | Объединение | `{{merge(arr1; arr2)}}` |
| `map(arr; field)` | Извлечь поле | `{{map(arr; "name")}}` |
| `flatten(arr)` | Выровнять вложенные | `{{flatten(arr)}}` |
| `emptyarray` | Пустой массив | `{{emptyarray}}` |

### Object (объекты)

| Функция | Описание | Пример |
|---------|----------|--------|
| `get(obj; key)` | Получить значение | `{{get(obj; "name")}}` |
| `keys(obj)` | Все ключи | `{{keys(obj)}}` |
| `values(obj)` | Все значения | `{{values(obj)}}` |
| `merge(obj1; obj2)` | Объединить | `{{merge(obj1; obj2)}}` |
| `omit(obj; key)` | Исключить ключ | `{{omit(obj; "password")}}` |
| `pick(obj; k1; k2)` | Выбрать ключи | `{{pick(obj; "name"; "email")}}` |
| `has(obj; key)` | Проверить наличие | `{{has(obj; "name")}}` -> true/false |

### General (общие)

| Функция | Описание | Пример |
|---------|----------|--------|
| `if(cond; yes; no)` | Условие | `{{if(a > b; "больше"; "меньше")}}` |
| `ifempty(val; default)` | Дефолт | `{{ifempty(x; "default")}}` |
| `switch(val; c1; r1; ...; def)` | Выбор | `{{switch(x; "a"; "Alpha"; "b"; "Beta"; "?")}}` |
| `coalesce(a; b; c)` | Первое непустое | `{{coalesce(a; b; c)}}` |
| `typeof(val)` | Тип значения | `{{typeof(x)}}` |
| `iif(cond; yes; no)` | Inline if | `{{iif(1.status = "active"; "Da"; "Net")}}` |

**Операторы сравнения:** `=` `!=` `>` `<` `>=` `<=`
**Логические:** `and`, `or`, `not`

### Crypto (криптографические)

| Функция | Описание | Пример |
|---------|----------|--------|
| `md5(str)` | MD5 хеш | `{{md5("text")}}` |
| `sha1(str)` | SHA-1 хеш | `{{sha1("text")}}` |
| `sha256(str)` | SHA-256 хеш | `{{sha256("text")}}` |
| `sha512(str)` | SHA-512 хеш | `{{sha512("text")}}` |
| `hmac(algo; key; data)` | HMAC подпись | `{{hmac("sha256"; "key"; "data")}}` |
| `base64(str)` | Кодирование Base64 | `{{base64("text")}}` |
| `decodeBase64(str)` | Декодирование | `{{decodeBase64("dGV4dA==")}}` |
| `uuid` | Генерация UUID | `{{uuid}}` |

---

## 5. Обработка ошибок

### Типы ошибок

| Тип | Описание | Типичная причина |
|-----|----------|------------------|
| ConnectionError | Сервис недоступен | API упал, сеть, таймаут |
| DataError | Неверные данные | Неправильный формат, пустое обязательное поле |
| RuntimeError | Ошибка выполнения | Логическая ошибка, API вернул ошибку |
| RateLimitError | Превышен лимит API | Слишком частые запросы |
| InvalidConfigurationError | Неверная настройка | Модуль настроен неправильно |
| MaxFileSizeExceededError | Файл слишком большой | Превышен лимит 50 MB |

### Error Handlers (директивы)

ПКМ на модуль -> Add error handler -> выбрать директиву:

| Директива | Что делает | Когда использовать |
|-----------|-----------|-------------------|
| **Resume** | Продолжает выполнение с подставленными данными | Некритичный модуль, можно обойтись без результата |
| **Rollback** | Откатывает ВСЕ операции сценария | Критичные данные, принцип "все или ничего" |
| **Commit** | Фиксирует успешные, останавливает дальше | Часть работы важнее полной |
| **Break** | Прерывает, сохраняет в Incomplete Executions | Временная ошибка, повторить позже |
| **Ignore** | Просто игнорирует ошибку | Совсем некритичные модули |

### Incomplete Executions

Незавершенные выполнения хранятся для ручного/автоматического retry. Retry стратегии: Break + auto-retry, ручной повтор, exponential backoff (1 мин -> 5 мин -> 15 мин).

---

## 6. Webhooks и HTTP модуль

### Webhooks

**Webhook vs Polling:** Webhook = мгновенная реакция + экономия операций. Polling = периодическая проверка (тратит ops на пустые запросы).

**URL формат:** `https://hook.{region}.make.com/{unique-id}` (регионы: eu1, eu2, us1, us2)

**Типы:**
- **Custom Webhook** -- универсальный приемник (JSON, XML, Form Data, Binary)
- **App-specific (Instant)** -- готовые триггеры сервисов
- **Webhook Response** -- отправка ответа вызывающему (таймаут 40 сек)
- **Custom Mailhook** -- прием email

**Безопасность:** HTTPS всегда, IP Restrictions (whitelist), HMAC-SHA256 подпись, секретный параметр в URL.

**Rate limits:** Free 1/сек, Core 5/сек, Pro 15/сек, Teams 25/сек. Payload лимит: 5 MB.

### HTTP Module

| Модуль | Назначение |
|--------|------------|
| Make a request | Универсальный (любой метод: GET, POST, PUT, PATCH, DELETE) |
| Make a Basic Auth request | С Basic Auth (username:password) |
| Make an API Key Auth request | С API Key в header/query |
| Make an OAuth 2.0 request | С OAuth 2.0 |
| Get a file | Скачивание файлов |
| Retrieve headers | Только заголовки (HEAD) |

**Timeout:** по умолчанию 40 сек, максимум 300 сек. Авто-retry при: 429, 500, 502, 503, 504 (до 3 попыток).

**Доступ к ответу:** `{{X.data}}` (тело), `{{X.statusCode}}` (статус), `{{X.headers}}` (заголовки).

### JSON/XML парсинг

- **Parse JSON:** строка -> объект для маппинга
- **Create JSON:** объект -> строка для HTTP body
- **Aggregate to JSON:** множество bundles -> один JSON массив
- **Parse XML / Create XML:** для SOAP и legacy API

### Make.com API

Token: Profile -> API Access -> Create new token. Base URL: `https://{region}.make.com/api/v2`. Rate limit: 100 req/min.

Ключевые endpoints: scenarios (list, run, activate), connections (test), executions (logs, stats, retry), webhooks (queue, toggle).

---

## 7. Топ модули

### Telegram Bot

**Триггер:** Instant (Webhook). **Авторизация:** Bot Token от @BotFather.

Данные из Watch Updates:
```
{{1.message.chat.id}}         -- Chat ID
{{1.message.from.first_name}} -- Имя
{{1.message.text}}            -- Текст
{{1.callback_query.data}}     -- Callback кнопки
```

Actions: Send Text/Photo/Document/Location Message, Edit Message, Delete Message.

**Inline Keyboard (кнопки):**
```json
{"inline_keyboard": [
  [{"text": "Да", "callback_data": "yes"}, {"text": "Нет", "callback_data": "no"}],
  [{"text": "Сайт", "url": "https://example.com"}]
]}
```

**Rate Limits:** 1 msg/сек в один чат, 30 msg/сек в разные чаты, 20 msg/мин в группу. Макс. длина: 4096 символов.

### Google Sheets

**Триггер:** Polling (Watch Rows). **Авторизация:** OAuth 2.0.

| Модуль | Операции |
|--------|----------|
| Watch Rows | 1 |
| Add a Row | 1 |
| Update a Row | 1 |
| Search Rows | 1 |
| **Bulk Add Rows** | **1 (вместо N!)** |
| **Bulk Update Rows** | **1 (вместо N!)** |

**Оптимизация:** Array Aggregator -> Bulk Add Rows = 1 операция вместо 100.

**Rate limit:** 100 requests / 100 seconds. Лимит: 10M ячеек.

### WhatsApp Business

**Триггер:** Instant (Webhook). **Авторизация:** Meta Business Account + Access Token.

**24-часовое окно:** свободная переписка 24ч после последнего сообщения клиента. Вне окна -- только через одобренные Templates.

Типы сообщений: Text, Template, Image, Document, Location, Interactive (Buttons до 3, List).

Формат номера: `79991234567` (без +, без пробелов, с кодом страны).

### OpenAI

**Авторизация:** API Key. Только Actions (нет триггеров).

| Модель | Контекст | Input/1M | Output/1M |
|--------|----------|----------|-----------|
| gpt-4o | 128K | $2.50 | $10 |
| gpt-4o-mini | 128K | $0.15 | $0.60 |

Temperature: 0 = детерминированный (классификация), 0.3-0.7 = баланс, 1.0+ = креативный.

Output: `{{2.choices[0].message.content}}` (текст), `{{2.usage.total_tokens}}` (токены).

### Flow Control

| Модуль | Что делает | Операции |
|--------|-----------|----------|
| **Router** | Ветвление на параллельные пути | 0 |
| **Iterator** | Массив -> отдельные bundles | 0 |
| **Repeater** | Повтор цепочки N раз | 0 |
| **Array Aggregator** | Bundles -> массив | 1 |
| **Text Aggregator** | Bundles -> текст с разделителем | 1 |
| **Numeric Aggregator** | Sum/Avg/Min/Max/Count | 1 |

### Tools (служебные)

- **Set Variable / Get Variable** -- переменные (0 ops)
- **Set Multiple Variables** -- несколько за 1 операцию
- **Sleep** -- пауза до 300 сек (rate limiting)
- **Switch** -- выбор значения по условию
- **Increment** -- счетчик

---

## 8. Advanced

### Custom Apps

Создание собственных интеграций для API без готового модуля. Структура: Base URL + Connections + Modules (Action, Search, Trigger) + RPCs (динамические списки) + Webhooks.

**Когда Custom App:** много модулей, сложная авторизация, командная работа.
**Когда HTTP:** разовая интеграция, простой API.

### AI Agents

AI Agent = LLM + Tools (Make-сценарии через webhook) + Memory (Data Store) + System Prompt. Agent сам решает какой Tool вызвать. Макс 10-15 tools на агента.

### MCP Server (Model Context Protocol)

Протокол от Anthropic для подключения LLM к внешним системам. Claude может напрямую вызывать Make-сценарии. Конфигурация: `.claude/mcp_servers.json`.

### Make Bridge

Подключение локальных (on-premise) систем к облачному Make.com БЕЗ открытия входящих портов. Docker или Node.js агент. URL scheme: `bridge://`.

---

## 9. Best Practices

### Именование

```
Сценарии:  [КАТЕГОРИЯ] Действие - Источник -> Назначение (версия)
Модули:    [N] Глагол + Объект
Connection: [Сервис] PROD/DEV - описание (владелец)
Data Store: [КАТЕГОРИЯ] Назначение
Переменные: var_ (обычные), tmp_ (временные), cfg_ (конфиг), cnt_ (счетчики), dt_ (даты), arr_ (массивы)
```

Категории: `[CRM]`, `[SALES]`, `[MARKETING]`, `[SUPPORT]`, `[SYNC]`, `[NOTIFY]`, `[REPORT]`, `[AI]`, `[TEST]`.

### Организация

Папки: `01_PRODUCTION/`, `02_DEVELOPMENT/`, `03_STAGING/`, `04_ARCHIVE/`, `05_TEMPLATES/`. Версионирование через клонирование. Notes внутри каждого модуля.

### Оптимизация операций

**Формула:** `Операции = Запуски x Платные_модули x Bundles`

**Бесплатные модули (0 ops):** Router, Filter, Iterator, Repeater, Set/Get Variable, Sleep, Error handlers.

**Ключевые техники:**
1. **Bulk > Iteration:** Sheets Bulk Add = 1 op вместо N
2. **Webhook > Polling:** 0 ops в ожидании vs 288 ops/день (polling каждые 5 мин)
3. **Aggregator > Iterator+Action:** собрать данные -> 1 отправка вместо N
4. **Data Store кеширование:** справочники обновлять по расписанию, не запрашивать каждый раз
5. **Conditional execution:** Router с фильтрами -- ненужные ветки не тратят ops

**Правило 80/20:** 80% операций тратят 20% сценариев. Оптимизируйте их первыми.

### Безопасность

- Секреты ТОЛЬКО в Connections (зашифрованы, обновляемы)
- НИКОГДА: hardcode в модулях, Notes, переменных (видны в History)
- IP Restrictions для webhooks
- PII маскирование: `j***@example.com`, `+7***1234`
- GDPR: сценарий "Right to Deletion"
- Webhook Signature: HMAC-SHA256 проверка подписи

### Отладка

1. **Run Once** -- тестовый запуск, просмотр Input/Output каждого модуля
2. **History** -- фильтр по Status/Date, детали каждого выполнения
3. **Set Variable** -- "sandwich debugging": переменные до и после проблемного модуля
4. **Бинарный поиск** -- отключить половину модулей, Run Once, сузить

### Мониторинг

- Email уведомления: Organization -> Settings -> Notifications
- Telegram/Slack алерты: Error Handler -> HTTP POST -> webhook алерт-сценария
- Health Checks: ежечасная проверка connections, API, Data Stores
- Эскалация: L1 (0-15 мин, Telegram), L2 (15-30 мин, +Email), L3 (30+ мин, +звонок)

---

## 10. Применение в туризме ОАЭ

### Типичные сценарии для Сухейля

**Лидогенерация:** Telegram/WhatsApp -> Webhook в Make -> Validate -> Google Sheets (CRM) -> Уведомление менеджеру в Telegram.

**Мультиканальные уведомления:** Router по каналу клиента -> Telegram + WhatsApp + Email.

**AI-классификация запросов:** Webhook -> OpenAI (temp=0) -> Router по категории (экскурсия / яхта / авто / билет) -> соответствующий менеджер (Сухейль / Муфамад / Марсель).

**Конвертация валют:** Math функции для пересчета AED/USD/RUB/KZT.

**Формат дат для Дубая:** `{{formatDate(now; "DD.MM.YYYY HH:mm"; "Asia/Dubai")}}`.

### Примеры сценариев

**CRM:** Tilda Form -> Webhook -> Search Contact -> Create/Update -> Assign Manager (round-robin) -> Telegram notification.

**SMM:** RSS -> Filter -> Deduplicate (Data Store) -> Format -> Telegram channel.

**AI Workflow:** Telegram voice -> Download -> Whisper API -> GPT extract entities -> CRM.

**Data Sync:** Google Sheets <-> Notion (двусторонняя через Data Store mapping + timestamp comparison).

**Notifications:** Webhook -> User Preferences (Data Store) -> Router -> Telegram / WhatsApp / Email -> Log delivery.

---

## 11. API Rate Limits -- сводная таблица

| Сервис | Лимит |
|--------|-------|
| Make HTTP | 100 requests/min per scenario |
| Make API | Free 10/min, Core 100/min, Pro/Teams 200/min |
| Telegram | 30 msg/sec (разные чаты), 1 msg/sec (один чат) |
| Google Sheets | 100 req/100 sec |
| Notion | 3 req/sec |
| WhatsApp | Depends on plan (1000 free service conversations/month) |
| OpenAI | Depends on tier (TPM/RPM) |
| Webhook incoming | Free 1/sec, Core 5, Pro 15, Teams 25 |
