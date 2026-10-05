# Шаблон CRM для туристического бизнеса ОАЭ в Notion

> Готовая структура из 4 связанных баз данных для семейного бизнеса Сухейля.

---

## Структура баз данных

### 1. Clients (Клиенты)

| Свойство | Тип | Настройки | Описание |
|----------|-----|-----------|----------|
| Name | title | -- | ФИО клиента |
| Phone | phone_number | -- | Основной номер (+971...) |
| WhatsApp | url | -- | wa.me/номер |
| Telegram | url | -- | t.me/username |
| Email | email | -- | Email |
| Country | select | RU, KZ, UZ, UA, BY, AE, Other | Страна клиента |
| Source | select | Instagram, Telegram, WhatsApp, Referral, Walk-in, Website | Источник лида |
| Status | status | Lead, Active, VIP, Archived | Статус клиента |
| Agent | people | -- | Ответственный (Сухейль/Марсель/Муфамад) |
| Bookings | relation | -> Bookings DB (two-way) | Связь с бронированиями |
| Total Revenue | rollup | sum(Bookings.Price AED) | Общая сумма заказов |
| Notes | rich_text | -- | Заметки о клиенте |

### 2. Bookings (Бронирования)

| Свойство | Тип | Настройки | Описание |
|----------|-----|-----------|----------|
| Booking Name | title | -- | Название бронирования |
| Booking ID | unique_id | prefix: "BOOK" | Автоинкремент BOOK-001 |
| Client | relation | -> Clients DB (two-way) | Связь с клиентом |
| Product | relation | -> Products DB (two-way) | Связь с продуктом |
| Date | date | -- | Дата экскурсии/услуги |
| Status | select | Inquiry, Confirmed, Paid, Completed, Cancelled | Статус |
| Pax | number | number | Количество гостей |
| Price AED | number | number | Цена для клиента |
| Cost Price | number | number | Себестоимость |
| Profit | formula | prop("Price AED") - prop("Cost Price") | Прибыль |
| Client Currency | select | AED, USD, RUB, KZT, Crypto | Валюта клиента |
| Amount in Currency | number | number | Сумма в валюте клиента |
| Amount AED | formula | (см. формулу конвертации ниже) | Сумма в AED |
| Payment Method | select | Cash AED, Cash USD, Sber RUB, Kaspi KZT, Crypto, Bank Transfer | Способ оплаты |
| Pickup Location | rich_text | -- | Место подачи |
| Agent | people | -- | Ответственный |
| Notes | rich_text | -- | Заметки |

### 3. Products (Продукты/Услуги)

| Свойство | Тип | Настройки | Описание |
|----------|-----|-----------|----------|
| Product Name | title | -- | Название продукта |
| Category | select | Excursion, Park Ticket, Yacht, Car Rental, Transfer, MVU | Категория |
| Responsible | people | -- | Кто отвечает |
| Price Regular AED | number | number | Обычная цена |
| Price High Season AED | number | number | Цена в сезон (Oct-Mar) |
| Cost Price | number | number | Себестоимость |
| Current Price | formula | (см. формулу сезонной цены ниже) | Текущая цена |
| Place | place | -- | Геолокация точки |
| Duration | rich_text | -- | Длительность |
| Status | select | Active, Paused | Статус |
| Supplier | relation | -> Suppliers DB | Поставщик |
| Bookings | relation | -> Bookings DB (two-way) | Бронирования |
| Total Sold | rollup | count(Bookings) | Сколько раз продано |

### 4. Suppliers (Поставщики)

| Свойство | Тип | Настройки | Описание |
|----------|-----|-----------|----------|
| Company | title | -- | Название компании |
| Contact Person | rich_text | -- | Контактное лицо |
| Phone | phone_number | -- | Телефон |
| WhatsApp | url | -- | wa.me/номер |
| Email | email | -- | Email |
| Type | multi_select | Excursion, Yacht, Car, Transfer, Ticket | Тип услуг |
| Commission % | number | percent | Процент комиссии |
| Products | relation | -> Products DB (two-way) | Связанные продукты |
| Notes | rich_text | -- | Заметки |

---

## Ключевые формулы

### Прибыль
```
prop("Price AED") - prop("Cost Price")
```

### Конвертация валюты в AED
```
if(prop("Client Currency") == "USD", prop("Amount in Currency") * 3.67,
if(prop("Client Currency") == "RUB", prop("Amount in Currency") * 0.04,
if(prop("Client Currency") == "KZT", prop("Amount in Currency") * 0.007,
prop("Amount in Currency"))))
```

### Сезонная цена (High Season: Oct-Mar)
```
if(month(now()) >= 10 or month(now()) <= 3,
  prop("Price High Season AED"),
  prop("Price Regular AED"))
```

### Статус дедлайна
```
if(empty(prop("Date")), "No date",
  if(prop("Date") < now(), "Overdue",
    if(dateBetween(prop("Date"), now(), "days") <= 1, "Tomorrow", "Upcoming")))
```

### Маржинальность (%)
```
if(prop("Price AED") > 0,
  round(((prop("Price AED") - prop("Cost Price")) / prop("Price AED")) * 100),
  0)
```

---

## Рекомендуемые Views

### Bookings DB

| View | Тип | Фильтр/группировка |
|------|-----|---------------------|
| Pipeline | Kanban Board | Group by: Status |
| Calendar | Calendar | Property: Date |
| Today | Table | Filter: Date = Today, Status != Cancelled |
| Unpaid | Kanban Board | Filter: Status = Confirmed, Group by: Payment Method |
| By Agent | Kanban Board | Group by: Agent |
| Weekly Report | Table | Filter: Date = This week, Sort: Date asc |

### Clients DB

| View | Тип | Фильтр/группировка |
|------|-----|---------------------|
| All Clients | Table | Sort: Last edited desc |
| VIP | Table | Filter: Status = VIP |
| By Source | Kanban Board | Group by: Source |
| New Leads | Table | Filter: Status = Lead, Sort: Created desc |

### Products DB

| View | Тип | Фильтр/группировка |
|------|-----|---------------------|
| Catalog | Gallery | Filter: Status = Active |
| By Category | Kanban Board | Group by: Category |
| Price List | Table | Sort: Category, then Price Regular |

---

## Распределение по братьям

| Брат | Категории | Примеры продуктов |
|------|-----------|-------------------|
| **Сухейль** | Excursion, Park Ticket | City Tour, Desert Safari, Burj Khalifa, Aquaventure |
| **Марсель** | Car Rental, Transfer, MVU | Luxury/Sport/Economy cars, Airport transfers, МВУ |
| **Муфамад** | Yacht | Paramount Yachts (300+ яхт), Water Activities, Catering |

---

## Быстрый старт

1. Создать Teamspace "Tourism CRM"
2. Создать 4 базы данных в порядке: Suppliers -> Products -> Clients -> Bookings
3. Настроить Relations между базами (two-way)
4. Добавить формулы и rollups
5. Создать Views для каждой базы
6. Расшарить с Internal Integration для API доступа
7. Настроить Database Automations (Status changed -> Slack)
