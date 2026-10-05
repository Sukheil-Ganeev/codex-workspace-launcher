# PuzzleBot -- Шпаргалка (Cheatsheet)

---

## Системные переменные

| Переменная | Описание | Всегда есть? |
|------------|----------|--------------|
| `{user_id}` | Telegram ID пользователя | Да |
| `{first_name}` | Имя | Да |
| `{last_name}` | Фамилия | Нет |
| `{username}` | Username (без @) | Нет |
| `{full_name}` | Полное имя | Да |
| `{language_code}` | Код языка (ru, en, ar) | Да |
| `{bot_username}` | Username бота | Да |
| `{bot_name}` | Название бота | Да |
| `{current_date}` | Текущая дата | Да |
| `{current_time}` | Текущее время | Да |
| `{current_hour}` | Текущий час (0-23) | Да |
| `{current_day}` | День недели | Да |
| `{current_month}` | Месяц | Да |

---

## Переменные магазина

| Переменная | Описание |
|------------|----------|
| `{order_id}` | Номер заказа |
| `{order_total}` | Сумма заказа |
| `{order_items}` | Список товаров |
| `{order_status}` | Статус заказа |
| `{tracking_number}` | Трек-номер |
| `{tracking_url}` | Ссылка отслеживания |
| `{delivery_date}` | Дата доставки |
| `{name}` | Имя покупателя |

---

## Переменные мультипостинга

| Переменная | Описание |
|------------|----------|
| `{channel_name}` | Название канала |
| `{channel_username}` | @username канала |
| `{subscribers_count}` | Кол-во подписчиков |

---

## Синтаксис переменных

| Конструкция | Синтаксис | Пример |
|-------------|-----------|--------|
| Вставка | `{переменная}` | `{first_name}` |
| Fallback | `{переменная\|значение}` | `{first_name\|друг}` |
| Условие IF | `{if:переменная}...{/if}` | `{if:is_vip}Скидка 20%{/if}` |
| IF-ELSE | `{if:переменная}...{else}...{/if}` | `{if:is_vip}VIP{else}Обычный{/if}` |
| Проверка категории | `{if:category:код}...{/if}` | `{if:category:vip}VIP-меню{/if}` |
| Условие с оператором | `{if переменная > N}...{endif}` | `{if bonus > 0}Баллы: {bonus}{endif}` |
| Lower | `{переменная\|lower}` | `{name\|lower}` |
| Upper | `{переменная\|upper}` | `{name\|upper}` |
| Capitalize | `{переменная\|capitalize}` | `{name\|capitalize}` |
| Число с пробелами | `{переменная\|number}` | `{amount\|number}` -> 1 234 567 |
| Дата прописью | `{переменная\|date}` | `{date\|date}` -> 15 января 2026 |
| Trim | `{переменная\|trim}` | `{name\|trim}` |

---

## Формулы

### Базовые операции

| Операция | Символ | Пример |
|----------|--------|--------|
| Сложение | `+` | `{a} + {b}` |
| Вычитание | `-` | `{a} - {b}` |
| Умножение | `*` | `{a} * {b}` |
| Деление | `/` | `{a} / {b}` |
| Остаток | `%` | `{a} % {b}` |

Порядок: скобки -> `*` `/` `%` -> `+` `-`

### Функции

| Функция | Синтаксис | Пример |
|---------|-----------|--------|
| Округление | `round({x})` или `round({x}, N)` | `round({total}, 2)` |
| Минимум | `min({a}, {b})` | `min({balance}, {max_spend})` |
| Максимум | `max({a}, {b})` | `max({score}, 0)` |

### Готовые формулы

```
-- Скидка %
{discount} = {price} * {percent} / 100
{final} = {price} - {discount}

-- Наценка %
{price} = {cost} * (100 + {markup}) / 100

-- Кэшбэк
{cashback} = {order_sum} * {cashback_pct} / 100
{balance} = {balance} + {cashback}

-- Списание бонусов (макс 30%)
{bonus_used} = min({balance}, {order_sum} * 0.3)
{final} = {order_sum} - {bonus_used}
{balance} = {balance} - {bonus_used}

-- Счетчик
{count} = {count} + 1

-- Лимит запросов
{daily_requests} = {daily_requests} + 1
Условие: {daily_requests} > 10 -> "Лимит исчерпан"

-- Конвертация валют
{price_usd} = round({price_aed} / {usd_aed_rate}, 2)
{price_rub} = round({price_aed} * {rub_aed_rate}, 0)
```

---

## Операторы сравнения (условия)

| Оператор | Описание | Пример |
|----------|----------|--------|
| `==` | Равно | `{status} == "VIP"` |
| `!=` | Не равно | `{blocked} != true` |
| `>` | Больше | `{balance} > 1000` |
| `<` | Меньше | `{age} < 18` |
| `>=` | Больше или равно | `{total} >= 5000` |
| `<=` | Меньше или равно | `{count} <= 10` |
| `contains` | Содержит | `{text} contains "доставка"` |
| `startswith` | Начинается с | `{text} startswith "заказ"` |
| `exists` | Существует | `{phone} exists` |

**Логические операторы:** `AND`, `OR`, `NOT`

```
({balance} >= 1000 OR {is_vip} == true) AND {verified} == true
```

---

## Текстовые триггеры

| Тип | Описание | Пример |
|-----|----------|--------|
| Точное совпадение | Только точный текст | "прайс" |
| Содержит | Любое вхождение | "доставка" |
| Начинается с | Начало строки | "заказ" |
| Заканчивается на | Конец строки | "?" |
| Несколько слов (ИЛИ) | Любое из слов | "цена" ИЛИ "стоимость" |
| Regex | Регулярное выражение | `^\d{10,11}$` |

**Приоритет:** точное > начинается > содержит > regex > любое сообщение

### Полезные regex

```
^\d+$              -- только цифры
^[а-яА-Я]+$        -- только кириллица
.*@.*\..*           -- email (упрощенный)
^\+7\d{10}$         -- телефон +7
^[A-Z]{2}\d{4}$     -- код (AB1234)
```

---

## Форматирование текста (Markdown)

| Стиль | Синтаксис |
|-------|-----------|
| **Жирный** | `*текст*` или `**текст**` |
| *Курсив* | `_текст_` или `__текст__` |
| ~~Зачеркнутый~~ | `~текст~` |
| `Моноширинный` | `` `текст` `` |
| Спойлер | `\|\|текст\|\|` |
| Подчеркнутый | `++текст++` |
| Ссылка | `[Текст](https://url)` |

---

## Типы кнопок

| Тип | Расположение | Действие |
|-----|-------------|----------|
| Reply | Под полем ввода | Отправляет текст в чат |
| Inline Callback | Под сообщением | Отправляет callback_data (скрытно) |
| Inline URL | Под сообщением | Открывает ссылку |
| Inline Web App | Под сообщением | Открывает Mini App |
| Reply Контакт | Под полем ввода | Запрашивает номер телефона |
| Reply Геолокация | Под полем ввода | Запрашивает местоположение |

**Лимиты кнопок:**

| Параметр | Inline | Reply |
|----------|--------|-------|
| Кнопок в ряду | 8 | 12 |
| Рядов | 100 | Неограничено |
| Символов в кнопке | ~64 | ~64 |

**Кнопки под постами:**
```
[Текст кнопки](https://link.com)        -- URL-кнопка
[Кнопка 1](url1) | [Кнопка 2](url2)     -- несколько в ряд
[Действие](callback:action_name)         -- Callback-кнопка
```

---

## Типы медиа и лимиты

| Тип | Макс. размер | Форматы |
|-----|-------------|---------|
| Фото | 10 МБ | JPG, PNG, WebP, BMP, GIF |
| Видео | 50 МБ | MP4 (рекомендуется H.264) |
| Документ | 50 МБ | Любые |
| Аудио | 50 МБ | MP3, OGG |
| Голосовое | 50 МБ | OGG |
| Видеосообщение | 50 МБ, до 60 сек | MP4 |
| Анимация (GIF) | 50 МБ | GIF, MP4 без звука |
| Медиа-группа | до 10 фото/видео | Подпись только к первому |

3 способа отправки: загрузка файла, по URL, по File ID.

---

## Типы полей форм

| Тип | Описание | Валидация |
|-----|----------|-----------|
| Текст | Произвольный текст | мин/макс длина |
| Число | Целые/дробные | мин/макс значение |
| Email | Email-адрес | Автовалидация формата |
| Телефон | Номер телефона | Формат, страна |
| Дата | ДД.ММ.ГГГГ | мин/макс дата |
| Время | ЧЧ:ММ | -- |
| Фото | Изображение | File ID |
| Документ | Файл | Формат, размер |
| Геолокация | Координаты | Широта + долгота |
| Выбор из списка | Кнопки | Варианты |

---

## PuzzleBot API

### Базовая информация

- **URL:** `https://api.puzzlebot.top/v1/`
- **Авторизация:** `Authorization: Bearer pb_abc123xyz...`
- **Токен:** Настройки бота -> API -> Получить токен

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/bot/info` | Информация о боте |
| GET | `/bot/stats?period=7d` | Статистика |
| POST | `/messages/send` | Отправить сообщение |
| POST | `/messages/sendPhoto` | Отправить фото |
| POST | `/messages/sendDocument` | Отправить документ |
| POST | `/broadcast/send` | Массовая рассылка |
| GET | `/users/{telegram_id}` | Получить пользователя |
| GET | `/users?limit=100&tag=premium` | Список пользователей |
| PATCH | `/users/{telegram_id}` | Обновить пользователя |
| POST | `/users/{telegram_id}/tags` | Управление тегами |
| PUT | `/users/{telegram_id}/variables` | Установить переменные |
| POST | `/users/{telegram_id}/block` | Заблокировать |
| GET | `/scenarios` | Список сценариев |
| POST | `/scenarios/run` | Запустить сценарий |

### Rate Limits

| Тип | Лимит |
|-----|-------|
| Общий | 1000/мин |
| Отправка сообщений | 30/сек |
| Массовая рассылка | 1/мин |
| Получение данных | 100/мин |

Заголовки: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

При 429: экспоненциальная задержка -- `retry_after * 2^attempt`.

### Коды ошибок

| Код | Описание |
|-----|----------|
| INVALID_TOKEN | Неверный API-токен |
| TOKEN_EXPIRED | Токен истек |
| RATE_LIMIT_EXCEEDED | Превышен лимит запросов |
| USER_NOT_FOUND | Пользователь не найден |
| SCENARIO_NOT_FOUND | Сценарий не найден |
| BOT_BLOCKED | Бот заблокирован пользователем |

### Примеры запросов

**Отправка сообщения:**
```json
POST /messages/send
{
  "chat_id": "123456789",
  "text": "Привет!",
  "parse_mode": "HTML"
}
```

**Отправка с кнопками:**
```json
POST /messages/send
{
  "chat_id": "123456789",
  "text": "Выберите:",
  "reply_markup": {
    "inline_keyboard": [
      [{"text": "Кнопка 1", "callback_data": "btn1"}],
      [{"text": "Сайт", "url": "https://example.com"}]
    ]
  }
}
```

**Запуск сценария для пользователя:**
```json
POST /scenarios/run
{
  "scenario_id": "sc_123",
  "telegram_id": "123456789",
  "variables": {"promo": "SALE20"}
}
```

**Массовая рассылка с фильтром:**
```json
POST /broadcast/send
{
  "text": "Акция!",
  "filter": {
    "tags": ["premium"],
    "subscribed_after": "2025-01-01"
  },
  "schedule": "2026-02-20T10:00:00Z"
}
```

---

## Внешние API (URL для HTTP-запросов)

| Сервис | URL | Назначение |
|--------|-----|-----------|
| PuzzleBot API | `https://api.puzzlebot.top/v1/` | Управление ботом |
| PuzzleBot Webhook | `https://puzzlebot.top/webhook/bot{ID}/{name}` | Входящий вебхук |
| ЮKassa Webhook | `https://api.puzzlebot.top/webhook/payment/yookassa/{bot_id}` | Платежи |
| Bitrix24 | `https://домен.bitrix24.ru/rest/1/TOKEN/` | CRM |
| Google Sheets API | `https://sheets.googleapis.com/v4/spreadsheets/{id}/values/` | Таблицы |
| Google Apps Script | `https://script.google.com/macros/s/{id}/exec` | Скрипты |
| OpenAI ChatGPT | `https://api.openai.com/v1/chat/completions` | AI |
| OpenAI Moderation | `https://api.openai.com/v1/moderations` | Фильтрация |
| Claude (Anthropic) | `https://api.anthropic.com/v1/messages` | AI |
| YandexGPT | `https://llm.api.cloud.yandex.net/foundationModels/v1/completion` | AI |
| GigaChat | `https://gigachat.devices.sberbank.ru/api/v1/chat/completions` | AI |
| Discord | `https://discord.com/api/webhooks/{id}/{token}` | Вебхук |
| Slack | `https://hooks.slack.com/services/T.../B.../XXX` | Вебхук |

---

## Bitrix24 -- ключевые методы

| Метод | Описание |
|-------|----------|
| `crm.contact.add` | Создать контакт |
| `crm.contact.list` | Список контактов |
| `crm.lead.add` | Создать лид |
| `crm.lead.list` | Список лидов |
| `crm.deal.add` | Создать сделку |
| `crm.deal.update` | Обновить сделку |
| `crm.deal.list` | Список сделок |
| `crm.deal.productrows.set` | Товары к сделке |
| `tasks.task.add` | Создать задачу |

Стадии сделок: `NEW`, `PREPARATION`, `EXECUTING`, `WON`, `LOSE`.

---

## Google Sheets -- Apps Script шаблон

```javascript
// Запись данных (POST)
function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  var sheet = SpreadsheetApp.getActiveSheet();
  sheet.appendRow([
    data.user_id,
    new Date(),
    data.name,
    data.phone,
    data.email,
    data.request
  ]);
  return ContentService.createTextOutput(
    JSON.stringify({status: "success"})
  ).setMimeType(ContentService.MimeType.JSON);
}

// Поиск данных (GET)
function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var userId = e.parameter.user_id;
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == userId) {
      return ContentService.createTextOutput(
        JSON.stringify({found: true, row: data[i]})
      ).setMimeType(ContentService.MimeType.JSON);
    }
  }
  return ContentService.createTextOutput(
    JSON.stringify({found: false})
  ).setMimeType(ContentService.MimeType.JSON);
}
```

**Лимиты Google Sheets:** 10 млн ячеек, 50,000 символов/ячейка, 300 запросов/мин, Apps Script -- 6 мин выполнения.

---

## ChatGPT -- шаблон HTTP-запроса

```
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer {openai_api_key}
Content-Type: application/json

{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "Ты консультант туристической компании в Дубае..."},
    {"role": "user", "content": "{user_message}"}
  ],
  "max_tokens": 500,
  "temperature": 0.7
}

Парсинг ответа: $.choices[0].message.content -> {ai_response}
```

**Модели и цены:**

| Модель | Вход/1K токенов | Выход/1K токенов |
|--------|-----------------|------------------|
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-4o | $0.005 | $0.015 |

1000 токенов ~ 400 слов (RU), ~750 слов (EN).

---

## JSONPath (парсинг webhook)

| JSONPath | Результат |
|----------|-----------|
| `$.name` | Корневое поле |
| `$.user.email` | Вложенное поле |
| `$.items[0]` | Первый элемент массива |
| `$.items[*].name` | Все name в массиве |
| `$.object.amount.value` | Глубоко вложенное |
| `$.object.metadata.telegram_id` | Метаданные |

---

## Горячие клавиши

### Конструктор

| Клавиша | Действие |
|---------|----------|
| Ctrl+S | Сохранить |
| Ctrl+Z | Отменить |
| Ctrl+Y | Повторить |
| Ctrl+C / Ctrl+V | Копировать / Вставить |
| Ctrl+N | Добавить блок |
| Delete | Удалить блок |
| Space+Drag | Перемещение по canvas |
| Scroll | Масштабирование |

### Диалоги

| Клавиша | Действие |
|---------|----------|
| Up/Down | Навигация по списку |
| Enter | Открыть диалог |
| Ctrl+F | Поиск |
| Ctrl+Enter | Отправить сообщение |
| R | Обновить |

---

## Лимиты платформы (полная таблица)

### По тарифам

| Параметр | Бесплатный | Креативный | Расширенный | Проф. |
|----------|------------|------------|-------------|-------|
| Подписчики | 150 | 1,000 | 10,000 | 20,000 |
| Блоки | 15 | 100 | 200 | 400 |
| Боты | 1 | 2 | 4 | 8 |
| Ресурсы | 2 | 3 | 6 | 12 |

### Telegram API

| Параметр | Лимит |
|----------|-------|
| Сообщений/сек (всего) | 30 |
| Сообщений/сек (одному) | 1 |
| Размер файла | 50 МБ |
| Размер фото | 10 МБ |
| Текст сообщения | 4,096 символов |
| Подпись к медиа | 1,024 символа |
| Кнопок callback_data | 64 байта |

### Конструктор и сценарии

| Параметр | Лимит |
|----------|-------|
| Inline кнопок в ряду | 8 |
| Reply кнопок в ряду | 12 |
| Рядов Inline | 100 |
| Медиа в альбоме | 10 |
| Вложенность категорий | 3 уровня |

### Таймеры

| Параметр | Лимит |
|----------|-------|
| Мин. задержка | 1 секунда |
| Макс. задержка | 30 дней |
| Отложенных/пользователя | 100 |
| Одновременных | 10,000 |

### Постинг и рассылки

| Параметр | Лимит |
|----------|-------|
| Каналов в мультипосте | 50 |
| Источников кросс-постинга | 10 |
| Запланированных постов | 500 |
| Планирование вперед | до 1 года |
| Слотов очереди/день | 24 |
| Повторяющихся публикаций | 50 |
| Получателей рассылки | 1,000,000 |
| Категорий | 100 |
| Условий в фильтре | 20 |
| Переменных в сообщении | 50 |

### Воронки

| Параметр | Лимит |
|----------|-------|
| Воронок | 50 |
| Сообщений в воронке | 100 |
| Условий/веток | 20 |

### Магазин

| Параметр | Лимит |
|----------|-------|
| Товаров | 10,000 |
| Категорий | 100 |
| Фото на товар | 10 |
| Вариантов на товар | 100 |
| Валют | 20 |
| Способов доставки | 20 |
| Статусов заказов | 15 |

### API

| Параметр | Лимит |
|----------|-------|
| Общий | 1,000/мин |
| Отправка сообщений | 30/сек |
| Массовая рассылка | 1/мин |
| Получение данных | 100/мин |
| Экспорт записей | 50,000 |

---

## Скорость рассылки

| Режим | Скорость | Когда использовать |
|-------|----------|-------------------|
| Быстрый | 25-30/сек | Срочные уведомления |
| Нормальный | 15-20/сек | Обычные рассылки |
| Медленный | 5-10/сек | Большая аудитория |
| Безопасный | 1-3/сек | >50,000 получателей |

Формула: получатели / скорость = время (10,000 / 20 = ~8.5 мин).

---

## Статусы заказов

```
Новый -> Ожидает оплаты -> Оплачен -> В обработке -> Отправлен -> Доставлен
                                                                 -> Отменен
                                                                 -> Возврат
```

---

## Полезные контакты

| Ресурс | Контакт |
|--------|---------|
| Техподдержка | @HelpMePuzzleBot |
| Сообщество | @LovePuzzleBot |
| Шаблоны | @Sample_PuzzleBot |
| Новости | @PuzzleBotNews |
| Email поддержки | support@puzzlebot.top |
| Партнерка | partners@puzzlebot.top |
| Жалобы | feedback@puzzlebot.top |
| Документация | https://docs.puzzlebot.top |
| Статус сервиса | https://status.puzzlebot.top |
| YouTube | youtube.com/@puzzlebot |
| Roadmap | puzzlebot.top/roadmap |

**Часы работы поддержки:** Пн-Пт 10:00-19:00 МСК.

**Время ответа:** критичный баг -- до 2ч, оплата -- до 4ч, тех. вопрос -- до 24ч, предложение -- до 48ч.
