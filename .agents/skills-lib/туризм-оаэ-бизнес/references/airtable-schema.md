# Airtable Schema - Схема базы данных

## Обзор структуры

```
UAE Tourism CRM (База)
├── Contacts (Таблица контактов)
├── Profiles (Профили клиентов)
├── Operations (Операции/сделки)
└── Referrals (Рефералы)
```

---

## Таблица Contacts (Контакты)

**Описание:** Главная таблица со всеми контактами из WhatsApp

| Поле | Тип Airtable | Обязательное | Описание | Пример |
|------|--------------|--------------|----------|--------|
| Name | Single line text | Да (Primary) | Имя контакта | Иван Петров |
| Phone | Phone number | Да | Номер телефона | +79161234567 |
| JID | Single line text | Нет | WhatsApp ID | 79161234567@s.whatsapp.net |
| Type | Single select | Да | Тип контакта | клиенты |
| Subtype | Single select | Нет | Подтип контакта | VIP |
| Source | Single select | Да | Источник контакта | whatsapp |
| First_Message | Date | Нет | Дата первого сообщения | 2024-01-15 |
| Last_Message | Date | Нет | Дата последнего сообщения | 2026-01-26 |
| Total_Messages | Number (Integer) | Нет | Количество сообщений | 1547 |
| Language | Single select | Нет | Язык общения | ru |
| Country | Single select | Нет | Страна | RU |
| Tags | Multiple select | Нет | Теги для фильтрации | постоянный, яхты |
| Notes | Long text | Нет | Заметки | Предпочитает luxury услуги |

**Варианты для Single select полей:**

| Поле | Допустимые значения |
|------|---------------------|
| Type | клиенты, агенты, поставщики, сотрудники |
| Subtype | турист, VIP, корпоративный, турагент, туроператор, B2B, обменник, водитель, гид, яхтсмен, кейтеринг, менеджер, водитель_штат, админ |
| Source | whatsapp, wa_business, vcf, manual, bitrix24 |
| Language | ru, en, ar, mixed |
| Country | RU, UAE, KZ, BY, UZ, other |

---

## Таблица Profiles (Профили)

**Описание:** Расширенные профили клиентов с предпочтениями

| Поле | Тип Airtable | Обязательное | Описание | Пример |
|------|--------------|--------------|----------|--------|
| Profile_ID | Single line text | Да (Primary) | UUID профиля | 550e8400-e29b-41d4-a716-446655440000 |
| Contact | Link to Contacts | Да | Связь с контактом | Иван Петров |
| Occupation | Single line text | Нет | Профессия | Предприниматель |
| City | Single select | Нет | Город проживания | Москва |
| Family_Status | Single select | Нет | Семейное положение | married |
| Children | Number (Integer) | Нет | Количество детей | 2 |
| Communication_Style | Single select | Нет | Стиль общения | formal |
| Price_Sensitivity | Single select | Нет | Чувствительность к цене | low |
| Decision_Speed | Single select | Нет | Скорость принятия решений | fast |
| Preferred_Time | Single select | Нет | Предпочтительное время связи | morning |
| Tour_Types | Multiple select | Нет | Типы туров | yacht, desert_safari |
| Budget_Category | Single select | Нет | Бюджетная категория | premium |
| Total_Orders | Number (Integer) | Нет | Всего заказов | 12 |
| Total_Spent_AED | Currency (AED) | Нет | Общая сумма покупок | 45000.00 |
| Avg_Order_Value | Currency (AED) | Нет | Средний чек | 3750.00 |
| Last_Order_Date | Date | Нет | Дата последнего заказа | 2026-01-15 |
| Birthday | Single line text | Нет | День рождения | 15.03 |

**Варианты для Single select полей:**

| Поле | Допустимые значения |
|------|---------------------|
| City | Москва, Санкт-Петербург, Алматы, Минск, Ташкент, Дубай, other |
| Family_Status | single, married, divorced |
| Communication_Style | formal, informal, business, friendly |
| Price_Sensitivity | high, medium, low |
| Decision_Speed | fast, medium, slow |
| Preferred_Time | morning, afternoon, evening, any |
| Budget_Category | budget, standard, premium, luxury |

---

## Таблица Operations (Операции)

**Описание:** Все сделки и бронирования

| Поле | Тип Airtable | Обязательное | Описание | Пример |
|------|--------------|--------------|----------|--------|
| Operation_ID | Autonumber | Да (Primary) | ID операции | 1234 |
| Contact | Link to Contacts | Да | Связь с контактом | Иван Петров |
| Date | Date | Да | Дата операции | 2026-01-20 |
| Type | Single select | Да | Тип услуги | yacht |
| Description | Single line text | Нет | Описание | Аренда яхты 65ft на 4 часа |
| Amount | Number (Decimal, 2) | Да | Сумма | 3500.00 |
| Currency | Single select | Да | Валюта | AED |
| Status | Single select | Да | Статус | completed |
| Pax | Number (Integer) | Нет | Количество человек | 8 |
| Pickup_Location | Single line text | Нет | Место сбора | Dubai Marina |
| Pickup_Time | Single line text | Нет | Время сбора | 14:00 |
| Profit | Number (Decimal, 2) | Нет | Прибыль | 700.00 |
| Notes | Long text | Нет | Заметки | День рождения клиента |
| Created_At | Created time | Авто | Дата создания | 2026-01-18T10:00:00 |

**Варианты для Single select полей:**

| Поле | Допустимые значения |
|------|---------------------|
| Type | tour, transfer, yacht, tickets, exchange, car_rental, catering, other |
| Currency | AED, USD, RUB, EUR, KZT |
| Status | pending, confirmed, completed, cancelled, refunded |

---

## Таблица Referrals (Рефералы)

**Описание:** Связи между клиентами (кто кого привёл)

| Поле | Тип Airtable | Обязательное | Описание | Пример |
|------|--------------|--------------|----------|--------|
| Referral_ID | Autonumber | Да (Primary) | ID реферала | 567 |
| Referrer | Link to Contacts | Да | Кто привёл | Анна Петрова |
| Referred | Link to Contacts | Да | Кого привели | Иван Сидоров |
| Source | Single select | Да | Источник обнаружения | vcf |
| Detected_Date | Date | Да | Дата обнаружения | 2026-01-15 |
| Confidence | Single select | Нет | Уровень уверенности | high |
| Context | Long text | Нет | Контекст/цитата | VCF карточка: Иван Сидоров |
| Total_Operations | Number (Integer) | Нет | Операций от реферала | 3 |
| Total_Revenue_AED | Currency (AED) | Нет | Выручка от реферала | 12500.00 |
| Commission_Percent | Percent | Нет | Процент комиссии | 10% |
| Commission_Paid | Checkbox | Нет | Комиссия выплачена | false |

**Варианты для Single select полей:**

| Поле | Допустимые значения |
|------|---------------------|
| Source | vcf, mention, direct, manual |
| Confidence | high, medium, low |

---

## Связи между таблицами

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONTACTS                                  │
│                    (главная таблица)                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ contact_id (Primary Key)                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ 1:N               │ 1:N               │ 1:N
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
│   PROFILES   │    │  OPERATIONS  │    │      REFERRALS       │
│              │    │              │    │                      │
│ contact_id   │    │ contact_id   │    │ referrer_contact_id  │
│ (FK)         │    │ (FK)         │    │ referred_contact_id  │
│              │    │              │    │ (оба FK)             │
└──────────────┘    └──────────────┘    └──────────────────────┘
```

### Настройка связей в Airtable

1. **Contacts -> Profiles** (1:N)
   - В таблице Profiles создайте поле "Contact" типа "Link to another record"
   - Выберите таблицу Contacts
   - Allow linking to multiple records: No

2. **Contacts -> Operations** (1:N)
   - В таблице Operations создайте поле "Contact" типа "Link to another record"
   - Выберите таблицу Contacts
   - Allow linking to multiple records: No

3. **Contacts -> Referrals** (1:N, два поля)
   - Создайте поле "Referrer" типа "Link to another record" -> Contacts
   - Создайте поле "Referred" типа "Link to another record" -> Contacts

---

## Rollup и Lookup поля (рекомендуемые)

### В таблице Contacts добавьте:

| Поле | Тип | Настройка |
|------|-----|-----------|
| Total_Orders_Rollup | Rollup | Таблица: Operations, Поле: Operation_ID, Функция: COUNT |
| Total_Spent_Rollup | Rollup | Таблица: Operations, Поле: Amount, Функция: SUM |
| Referred_Count | Rollup | Таблица: Referrals (как Referrer), Функция: COUNT |

### В таблице Operations добавьте:

| Поле | Тип | Настройка |
|------|-----|-----------|
| Contact_Name | Lookup | Поле: Contact -> Name |
| Contact_Phone | Lookup | Поле: Contact -> Phone |
| Contact_Type | Lookup | Поле: Contact -> Type |

---

## Представления (Views)

### Contacts - рекомендуемые представления

| Название | Фильтр | Сортировка |
|----------|--------|------------|
| Все контакты | - | Last_Message DESC |
| Клиенты | Type = "клиенты" | Total_Messages DESC |
| VIP клиенты | Subtype = "VIP" | Total_Spent_Rollup DESC |
| Агенты | Type = "агенты" | Name ASC |
| Поставщики | Type = "поставщики" | Type ASC |
| Новые (7 дней) | First_Message >= TODAY()-7 | First_Message DESC |

### Operations - рекомендуемые представления

| Название | Фильтр | Сортировка |
|----------|--------|------------|
| Все операции | - | Date DESC |
| Ожидающие | Status = "pending" | Date ASC |
| Сегодня | Date = TODAY() | Pickup_Time ASC |
| Этот месяц | Date >= FIRST_DAY_OF_MONTH() | Date DESC |
| По типам | - | Type ASC, Date DESC |
