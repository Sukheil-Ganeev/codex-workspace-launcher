# Шпаргалка: Make.com + Notion

## Database ID форматы

```
❌ 451e17f1d1c54a7793976b5929754567
✅ 451e17f1-d1c5-4a77-9397-6b5929754567
```

## Переменные Make.com

```
{{1.data.field}}           — поле из модуля 1
{{2.properties.Name}}      — свойство Name из модуля 2
{{formatDate(now; "DD-MM-YYYY")}}  — текущая дата
```

## AlAdhan API

```
# Дубай
https://api.aladhan.com/v1/timingsByCity?city=Dubai&country=UAE&method=8

# Абу-Даби
https://api.aladhan.com/v1/timingsByCity?city=Abu%20Dhabi&country=UAE&method=8

# По координатам
https://api.aladhan.com/v1/timings?latitude=25.2048&longitude=55.2708&method=8
```

## Notion API Headers

```
Authorization: Bearer secret_YOUR_TOKEN
Notion-Version: 2022-06-28
Content-Type: application/json
```

## Value Types в Make.com для Notion

| Тип в Notion | Value Type в Make.com |
|--------------|----------------------|
| Title | Title |
| Text | **Rich Text** (не Text!) |
| Number | Number |
| Select | Select |
| Multi-select | Multi-select |
| Date | Date |
| Checkbox | Checkbox |
| URL | URL |
| Email | Email |
| Phone | Phone |

## Методы расчёта намаза (AlAdhan)

| method | Название |
|--------|----------|
| 0 | Shia Ithna-Ansari |
| 1 | University of Islamic Sciences, Karachi |
| 2 | Islamic Society of North America |
| 3 | Muslim World League |
| 4 | Umm Al-Qura, Makkah |
| 5 | Egyptian General Authority |
| 7 | University of Tehran |
| **8** | **Gulf Region** ← для ОАЭ |
| 9 | Kuwait |
| 10 | Qatar |

## Быстрые команды Make.com

| Действие | Как |
|----------|-----|
| Тест одного модуля | ПКМ → Run this module only |
| Клонировать модуль | ПКМ → Clone |
| Выровнять модули | ПКМ на пустом → Auto-align |
| Добавить ветку Router | Навести на Router → + |
| Удалить связь | Клик на линию → Delete |

---

## Навигация по справочнику Make.com

Путь: `D:/Downloads/AI_AGENTS_PROJECT/02_ДОКУМЕНТАЦИЯ/MAKE_COM_СПРАВОЧНИК/`

### Быстрые ссылки

| Нужно | Смотри |
|-------|--------|
| Список функций | `04_ФУНКЦИИ/СПРАВОЧНИК_ФУНКЦИЙ.md` |
| HTTP модуль | `06_WEBHOOKS_API/HTTP_МОДУЛЬ.md` |
| Webhooks | `06_WEBHOOKS_API/WEBHOOKS.md` |
| Обработка ошибок | `05_ОБРАБОТКА_ОШИБОК/` |
| Notion интеграция | `07_МОДУЛИ_ТОП_100/NOTION/` |
| Google Sheets | `07_МОДУЛИ_ТОП_100/GOOGLE_SHEETS/` |

### Популярные функции Make.com

```
formatDate(date; "YYYY-MM-DD")     — форматирование даты
parseDate(string; "DD.MM.YYYY")    — парсинг даты
replace(text; "old"; "new")        — замена текста
split(text; ",")                   — разбивка по разделителю
join(array; ", ")                  — объединение массива
ifempty(value; "default")          — значение по умолчанию
if(condition; true_val; false_val) — условие
length(array)                      — длина массива
get(object; "key")                 — получение значения
```

---

## Паттерны сценариев (копируй структуру)

| Паттерн | Модули | Пример |
|---------|--------|--------|
| Обновление | `Scheduler → HTTP → Notion Update` | Курсы валют |
| Обработка | `Webhook → Router → Notion Create` | Заявки |
| Уведомления | `Notion Watch → Telegram` | Новые записи |
| Массовый | `Schedule → Iterator → HTTP → Notion` | Список городов |

---

## Быстрый старт: клонирование агента

```
1. Открой 03_АГЕНТЫ/INDEX.md
2. Найди похожего агента
3. Скопируй папку целиком
4. Переименуй
5. Адаптируй файлы по очереди
```

---

## API Каталог (полный)

См. `references/api-catalog.md` для:
- Готовых URL с примерами
- Типов авторизации
- Лимитов запросов
- Маппинга ответов
