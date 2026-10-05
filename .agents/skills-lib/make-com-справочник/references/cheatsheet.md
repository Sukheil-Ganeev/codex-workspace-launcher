# Make.com -- Шпаргалка (Cheatsheet)

---

## Синтаксис функций

**Разделитель аргументов: `;` (точка с запятой), НЕ `,` (запятая)!**

```
{{functionName(arg1; arg2; arg3)}}
{{if(1.status = "active"; "Да"; "Нет")}}
{{upper(substring(1.email; 0; indexOf(1.email; "@")))}}
```

---

## Все функции Make.com

### Math

```
{{add(a; b)}}                -- сложение
{{sub(a; b)}}                -- вычитание
{{multiply(a; b)}}           -- умножение
{{divide(a; b)}}             -- деление
{{ceil(n)}}                  -- округление вверх
{{floor(n)}}                 -- округление вниз
{{round(n; decimals)}}       -- округление
{{abs(n)}}                   -- модуль числа
{{min(a; b; ...)}}           -- минимум
{{max(a; b; ...)}}           -- максимум
{{sum(arr)}}                 -- сумма массива
{{average(arr)}}             -- среднее массива
{{mod(a; b)}}                -- остаток от деления
{{pow(a; b)}}                -- степень
{{sqrt(n)}}                  -- квадратный корень
{{random(min; max)}}         -- случайное число
{{parseNumber(str)}}         -- строка в число
```

### Text

```
{{concat(a; b; ...)}}        -- объединение строк
{{substring(str; start; end)}} -- подстрока
{{replace(str; old; new)}}   -- замена
{{trim(str)}}                -- убрать пробелы по краям
{{lower(str)}}               -- нижний регистр
{{upper(str)}}               -- верхний регистр
{{capitalize(str)}}          -- первая буква заглавная
{{length(str)}}              -- длина строки
{{indexOf(str; sub)}}        -- позиция подстроки (-1 если нет)
{{split(str; sep)}}          -- разбить в массив
{{join(arr; sep)}}           -- массив в строку
{{contains(str; sub)}}       -- содержит ли (true/false)
{{startsWith(str; prefix)}}  -- начинается с
{{endsWith(str; suffix)}}    -- заканчивается на
```

### Date/Time

```
{{now}}                              -- текущее время
{{formatDate(date; format)}}         -- форматирование
{{formatDate(now; "DD.MM.YYYY HH:mm"; "Asia/Dubai")}} -- с timezone
{{parseDate(str; format)}}           -- строка в дату
{{addDays(date; n)}}                 -- +дни
{{addMonths(date; n)}}               -- +месяцы
{{addYears(date; n)}}                -- +годы
{{addHours(date; n)}}                -- +часы
{{addMinutes(date; n)}}              -- +минуты
{{addSeconds(date; n)}}              -- +секунды
{{setDate(date; component; value)}}  -- установить компонент
{{dateDifference(d1; d2; unit)}}     -- разница дат
```

**Форматы дат:**

| Токен | Значение | Пример |
|-------|----------|--------|
| YYYY | Год (4 цифры) | 2026 |
| YY | Год (2 цифры) | 26 |
| MM | Месяц (01-12) | 02 |
| MMMM | Месяц словом | February |
| DD | День (01-31) | 15 |
| dddd | День недели словом | Sunday |
| HH | Час (00-23) | 14 |
| hh | Час (01-12) | 02 |
| mm | Минуты | 30 |
| ss | Секунды | 45 |
| A | AM/PM | PM |
| X | Unix timestamp (секунды) | 1708012345 |
| x | Unix timestamp (мс) | 1708012345000 |

**Частые форматы:**
- Россия/ОАЭ: `DD.MM.YYYY` -> `15.02.2026`
- ISO 8601: `YYYY-MM-DDTHH:mm:ssZ`
- US формат: `MM/DD/YYYY`
- С временем: `DD.MM.YYYY HH:mm`
- Дубай: `{{formatDate(now; "DD.MM.YYYY HH:mm"; "Asia/Dubai")}}`

### Array

```
{{first(arr)}}               -- первый элемент
{{last(arr)}}                -- последний элемент
{{length(arr)}}              -- размер массива
{{add(arr; val)}}            -- добавить элемент
{{remove(arr; idx)}}         -- удалить по индексу
{{contains(arr; val)}}       -- содержит ли
{{distinct(arr)}}            -- уникальные элементы
{{reverse(arr)}}             -- обратный порядок
{{sort(arr)}}                -- сортировка
{{slice(arr; start; end)}}   -- срез
{{merge(arr1; arr2)}}        -- объединение массивов
{{map(arr; field)}}          -- извлечь поле из массива объектов
{{flatten(arr)}}             -- выровнять вложенные
{{emptyarray}}               -- пустой массив
```

### Object

```
{{get(obj; key)}}            -- получить значение
{{keys(obj)}}                -- все ключи
{{values(obj)}}              -- все значения
{{merge(obj1; obj2)}}        -- объединить объекты
{{omit(obj; key)}}           -- исключить ключ
{{pick(obj; k1; k2)}}       -- выбрать ключи
{{has(obj; key)}}            -- проверить наличие ключа
```

### General

```
{{if(cond; yes; no)}}                    -- условие
{{ifempty(val; default)}}                -- дефолт для пустого
{{switch(val; c1; r1; c2; r2; default)}} -- переключатель
{{coalesce(a; b; c)}}                    -- первое непустое
{{typeof(val)}}                          -- тип значения
{{iif(cond; yes; no)}}                   -- inline if
```

**Операторы:**
```
=  !=  >  <  >=  <=          -- сравнение
and  or  not                  -- логические
```

### Crypto

```
{{md5(str)}}                 -- MD5 хеш
{{sha1(str)}}                -- SHA-1 хеш
{{sha256(str)}}              -- SHA-256 хеш
{{sha512(str)}}              -- SHA-512 хеш
{{hmac(algo; key; data)}}    -- HMAC подпись
{{base64(str)}}              -- Base64 кодирование
{{decodeBase64(str)}}        -- Base64 декодирование
{{uuid}}                     -- генерация UUID
```

---

## Бесплатные модули (0 операций)

| Модуль | Назначение |
|--------|------------|
| Router | Ветвление на параллельные пути |
| Filter | Условие между модулями |
| Iterator | Разбиение массива на элементы |
| Repeater | Повторение цепочки N раз |
| Set Variable | Сохранить значение |
| Get Variable | Получить значение |
| Sleep | Пауза (до 300 сек) |
| Text Parser | Парсинг текста (Match Pattern, Replace) |
| Error Handlers | Resume, Rollback, Commit, Break, Ignore |

## Платные но экономные (1 операция вместо N)

| Модуль | Экономия |
|--------|----------|
| Array Aggregator | 1 op вместо N bundles |
| Text Aggregator | 1 op (собрать текст) |
| Numeric Aggregator | 1 op (Sum/Avg/Min/Max) |
| Set Multiple Variables | 1 op (несколько переменных) |
| Google Sheets Bulk Add Rows | 1 op вместо N строк |
| Google Sheets Bulk Update Rows | 1 op вместо N строк |

---

## Формула расчета операций

```
Операции/мес = Платных модулей x Bundles x Запусков/день x 30
```

**Примеры:**
- 3 модуля x 1 bundle x 10 запусков x 30 дней = 900 ops/мес
- 5 модулей x 10 bundles x 5 запусков x 30 дней = 7,500 ops/мес
- Bulk: 1 модуль x 1 bundle x 5 запусков x 30 = 150 ops/мес (вместо 1500)

---

## Лимиты по тарифам

| Параметр | Free | Core | Pro | Teams |
|----------|------|------|-----|-------|
| Операции/мес | 1,000 | 10,000 | 10,000 | 10,000 |
| Цена/мес | $0 | $9 | $16 | $29 |
| Активных сценариев | 2 | Unlim | Unlim | Unlim |
| Мин. интервал | 15 мин | 1 мин | 1 мин | 1 мин |
| История | 7 дней | 30 дней | 60 дней | 180 дней |
| Parallel executions | -- | 2 | 5 | 5 |
| Data transfer | 1 GB | 5 GB | Unlim | Unlim |
| Memory | 128 MB | 256 MB | 512 MB | 512 MB |
| Data Store records | 500 | 10K | 50K | 100K |
| Data Store size | 1 MB | 10 MB | 100 MB | 100 MB |
| Webhook rate | 1/sec | 5/sec | 15/sec | 25/sec |

---

## Rate Limits по сервисам

| Сервис | Лимит | Рекомендация |
|--------|-------|-------------|
| Make HTTP per scenario | 100 req/min | Sleep между запросами |
| Make API | Free 10, Core 100, Pro 200 req/min | Проверять заголовки X-RateLimit |
| Telegram (разные чаты) | 30 msg/sec | Sleep 35ms при рассылке |
| Telegram (один чат) | 1 msg/sec | Sleep 1sec |
| Telegram (группа) | 20 msg/min | Sleep 3sec |
| Google Sheets | 100 req/100 sec | Bulk операции |
| Notion | 3 req/sec | Sleep 350ms |
| WhatsApp | По плану Meta | Templates для инициации |
| OpenAI | По tier (TPM/RPM) | gpt-4o-mini для бюджета |
| Webhook payload | 5 MB макс | Сжимать данные |
| Webhook response | 40 сек timeout | Быстрый 202 + callback |
| HTTP timeout | 300 сек макс | По умолчанию 40 сек |
| Sleep max | 300 сек | -- |
| Execution timeout | 40 мин | Разбить на части |

---

## Технические лимиты

| Параметр | Лимит |
|----------|-------|
| Modules per scenario | 150 |
| Iterator nesting | 10 уровней |
| Blueprint JSON | 5 MB |
| Custom variables | 100 per scenario |
| File size | 50 MB |
| Binary data (HTTP) | 100 MB |
| Telegram message | 4,096 символов |
| Google Sheets cells | 10,000,000 |
| Google Sheets columns | 18,278 (ZZZ) |
| Notion property value | 2,000 символов |

---

## Горячие клавиши редактора

| Комбинация | Действие |
|-----------|----------|
| Ctrl+S | Сохранить сценарий |
| Ctrl+Z | Отменить действие |
| Delete | Удалить модуль |
| Ctrl+клик | Мультивыбор модулей |
| Колесо мыши | Масштабирование |
| Зажать пробел + тянуть | Перемещение по холсту |

---

## Маппинг данных -- быстрая справка

```
{{1.fieldName}}              -- поле из модуля 1
{{1.data.user.name}}         -- вложенное поле
{{1.`Имя клиента`}}         -- поле со спецсимволами (обратные кавычки)
{{1.items[0].name}}          -- первый элемент массива
{{2.choices[0].message.content}} -- OpenAI ответ
{{1.message.chat.id}}        -- Telegram Chat ID
{{1.message.text}}           -- Telegram текст
{{1.callback_query.data}}    -- Telegram callback data
{{X.data}}                   -- HTTP response body
{{X.statusCode}}             -- HTTP status code
{{X.headers}}                -- HTTP response headers
```

---

## Error Handlers -- когда какой

| Директива | Описание | Когда |
|-----------|----------|-------|
| **Resume** | Продолжить с заменой | Некритичный модуль |
| **Break** | Прервать + retry позже | Временная ошибка (rate limit, timeout) |
| **Rollback** | Откатить ВСЕ | Критичные данные, "все или ничего" |
| **Commit** | Зафиксировать успешные | Часть важнее целого |
| **Ignore** | Пропустить молча | Совсем некритично |

---

## Telegram Bot -- основные данные

```
Из Watch Updates:
  Chat ID:    {{1.message.chat.id}}
  User ID:    {{1.message.from.id}}
  Имя:        {{1.message.from.first_name}}
  Username:   {{1.message.from.username}}
  Текст:      {{1.message.text}}
  Callback:   {{1.callback_query.data}}
  Photo:      {{1.message.photo[last].file_id}}

Inline Keyboard:
  {"inline_keyboard": [
    [{"text": "Кнопка", "callback_data": "value"}],
    [{"text": "Ссылка", "url": "https://..."}]
  ]}

Parse Mode: HTML или MarkdownV2
HTML: <b>жирный</b>, <i>курсив</i>, <a href="url">ссылка</a>
```

---

## Паттерны оптимизации -- быстрый выбор

| Проблема | Решение | Экономия |
|----------|---------|----------|
| 100 строк x Add Row | Array Aggregator -> Bulk Add | 100x |
| Polling каждые 5 мин без данных | Переключиться на Webhook | 288 ops/день |
| 50 email по одному | Text Aggregator -> 1 digest | 50x |
| Запрос курса валют каждый запуск | Data Store кеш + Schedule обновление | 10-100x |
| Все ветки Router выполняются | Добавить Filter на каждую ветку | 2-5x |
| Много мелких HTTP запросов | GraphQL или batch endpoint | 3-10x |

---

## Именование -- шаблоны

```
Сценарий:    [CRM] New Lead - Tilda -> Google Sheets (v2.1)
Модуль:      [3] Search Contact by Email
Connection:  [Google Sheets] CRM Database (admin)
Data Store:  [CACHE] Exchange Rates
Webhook:     [CRM] Tilda - New Lead Submission
Variable:    var_customer_name, tmp_calc_result, cfg_api_url, cnt_processed
```

---

## Полезные формулы для туризма ОАЭ

```
Дата/время Дубай:
  {{formatDate(now; "DD.MM.YYYY HH:mm"; "Asia/Dubai")}}

Конвертация валют (примерные курсы):
  AED -> USD: {{divide(1.priceAED; 3.67)}}
  AED -> RUB: {{multiply(1.priceAED; 25.5)}}
  USD -> AED: {{multiply(1.priceUSD; 3.67)}}
  USD -> RUB: {{multiply(1.priceUSD; 93.5)}}

Приветствие по времени суток:
  {{switch(
    formatDate(now; "HH"; "Asia/Dubai");
    "06"; "07"; "08"; "09"; "10"; "11"; "Доброе утро";
    "12"; "13"; "14"; "15"; "16"; "17"; "Добрый день";
    "Добрый вечер"
  )}}

Дата экскурсии на завтра:
  {{formatDate(addDays(now; 1); "DD.MM.YYYY (dddd)"; "Asia/Dubai")}}

Номер телефона -- нормализация (убрать +, пробелы):
  {{replace(replace(1.phone; "+"; ""); " "; "")}}

Классификация запроса (для Router):
  {{if(contains(lower(1.text); "яхт"); "yacht";
    if(contains(lower(1.text); "экскурс"); "tour";
      if(contains(lower(1.text); "авто"); "car";
        if(contains(lower(1.text); "билет"); "ticket"; "other")
      )
    )
  )}}
```

---

## HTTP Module -- шаблоны запросов

```
OpenAI Chat:
  POST https://api.openai.com/v1/chat/completions
  Headers: Authorization: Bearer {{cfg_openai_key}}
  Body: {"model":"gpt-4o-mini","messages":[{"role":"user","content":"..."}]}

Telegram Send:
  POST https://api.telegram.org/bot{{cfg_bot_token}}/sendMessage
  Body: {"chat_id":"123","text":"Hello","parse_mode":"HTML"}

Google Sheets (via API):
  POST https://sheets.googleapis.com/v4/spreadsheets/ID/values/Sheet1:append
  Headers: Authorization: Bearer {{oauth_token}}

Notion Create Page:
  POST https://api.notion.com/v1/pages
  Headers: Authorization: Bearer {{notion_token}}, Notion-Version: 2022-06-28
```

---

## Make.com API -- ключевые endpoints

```
Base URL: https://{region}.make.com/api/v2
Auth:     Authorization: Token {api-token}

GET    /scenarios                    -- список сценариев
PATCH  /scenarios/{id}               -- вкл/выкл (isActive: true/false)
POST   /scenarios/{id}/run           -- запустить
GET    /scenarios/{id}/blueprint     -- получить blueprint
GET    /scenarios/{id}/executions    -- список выполнений
GET    /connections                  -- список connections
POST   /connections/{id}/test        -- проверить connection
GET    /hooks                        -- список webhooks
DELETE /hooks/{id}/queue             -- очистить очередь webhook

Rate limit: 100 req/min
Regions: eu1, eu2, us1, us2
```

---

## Checklist перед деплоем

- [ ] Все Connections активны и проверены
- [ ] Error Handlers настроены на критичных модулях
- [ ] Scheduling настроено правильно
- [ ] Notes добавлены к модулям
- [ ] Тестовый Run Once прошел успешно
- [ ] Blueprint экспортирован (бэкап)
- [ ] Мониторинг настроен (Notifications ON)
- [ ] Секреты только в Connections (не захардкожены)
- [ ] Имя сценария по конвенции: `[КАТЕГОРИЯ] Действие - Источник -> Назначение`
