# 02-Booking System Schema

**Назначение:** Управление всеми бронированиями туров, яхт, автомобилей и прочих услуг туристического бизнеса ОАЭ с полным отслеживанием платежей, участников и истории изменений.

**Версия:** 1.0.0
**Статус:** Production-ready
**Язык БД:** PostgreSQL 14+

---

## Таблицы

### `tour_types`
Типы туров/услуг: City Tours, Desert Safari, Yacht Cruises, Car Rentals, Adventures

**Ключевые поля:**
- `name` - Название тура (UNIQUE)
- `category` - Категория (city-tour, desert-safari, yacht, car-rental, adventure)
- `min_participants`, `max_participants` - Ограничения по группе

### `bookings`
Главная таблица бронирований.

**Статусы:** pending, confirmed, cancelled, completed
**Платежи:** unpaid, partial, paid, refunded

**Ключевые поля:**
- `booking_code` - Уникальный код (UNIQUE)
- `contact_id` - Клиент (Foreign Key)
- `company_id` - Компания клиента (Optional)
- `tour_type_id` - Тип тура
- `start_date`, `end_date` - Дата начала/окончания
- `number_of_participants` - Количество участников
- `total_amount`, `discount_percent`, `final_amount` - Финансовые показатели
- `currency` - Валюта (AED, USD, RUB, KZT)

**Constraints:**
- Дата окончания >= дате начала
- Количество участников > 0
- Итоговая сумма >= 0

### `booking_items`
Позиции в бронировании (услуги, составляющие тур).

**Типы:** accommodation, transportation, activity, meal, guide

### `booking_participants`
Список участников тура для каждого бронирования.

**Данные:**
- Имя, фамилия, email, телефон
- Паспорт, национальность, дата рождения
- Специальные требования (диета, мобильность, аллергии)

### `booking_payments`
История всех платежей по бронированиям.

**Методы:** cash, credit-card, bank-transfer, check, crypto
**Статусы:** pending, completed, failed, refunded
**Шлюзы:** stripe, paypal, 2checkout, adyen

### `booking_refunds`
Таблица возвратов денежных средств.

**Причины:** Cancellation, Customer Request, Refund Policy

### `booking_changes`
История всех изменений в бронировании (для аудита).

**Типы:** date, participants, amount, status, cancellation

### `booking_cancellations`
Специальная информация об отмене бронирования.

**Политики возврата:** full, partial, none

### `promo_codes`
Управление промокодами и скидками.

**Типы скидок:** percentage, fixed

**Применимость:** all, specific_tours, specific_groups

### `tour_availability`
Доступность туров на конкретные даты (календарь).

**Информация:**
- Дата тура
- Полная вместимость и доступные места
- Цена за человека
- Место сбора и время
- Имя гида, тип транспорта
- Статус (open, full, cancelled)

### `booking_notifications`
Очередь уведомлений о бронированиях.

**Типы:** confirmation, reminder, payment-due, cancellation

### `booking_reviews`
Отзывы и рейтинги после завершения бронирования.

**Рейтинги:** 1-5 звёзд
**Проверка:** is_verified (одобрены администратором)

### `booking_sources`
Источник происхождения бронирования.

**Типы источников:** direct, agency, online, social, recommendation

---

## Типичные Запросы

### 1. Активные бронирования на ближайшие 30 дней
```sql
SELECT b.booking_code, c.first_name, c.last_name, tt.name,
       b.start_date, b.number_of_participants, b.final_amount
FROM bookings b
JOIN contacts c ON b.contact_id = c.id
JOIN tour_types tt ON b.tour_type_id = tt.id
WHERE b.status IN ('confirmed', 'pending')
  AND b.start_date BETWEEN CURRENT_DATE
  AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY b.start_date;
```

### 2. Доход по турам за период
```sql
SELECT tt.name, COUNT(b.id) as bookings,
       SUM(b.final_amount) as revenue
FROM bookings b
JOIN tour_types tt ON b.tour_type_id = tt.id
WHERE b.status = 'completed'
  AND b.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY tt.name
ORDER BY revenue DESC;
```

### 3. Статус платежей по бронированиям
```sql
SELECT b.booking_code, b.final_amount,
       COALESCE(SUM(bp.amount), 0) as paid,
       (b.final_amount - COALESCE(SUM(bp.amount), 0)) as due
FROM bookings b
LEFT JOIN booking_payments bp ON b.id = bp.booking_id
WHERE b.status IN ('confirmed', 'pending')
GROUP BY b.id, b.booking_code
HAVING (b.final_amount - COALESCE(SUM(bp.amount), 0)) > 0;
```

### 4. Туры с доступными местами
```sql
SELECT ta.tour_date, tt.name, ta.available_slots,
       ROUND(100.0 * (ta.total_capacity - ta.available_slots) /
       ta.total_capacity, 2) as occupancy_percent
FROM tour_availability ta
JOIN tour_types tt ON ta.tour_type_id = tt.id
WHERE ta.status = 'open' AND ta.available_slots > 0
ORDER BY ta.tour_date;
```

### 5. Список участников для конкретного тура
```sql
SELECT bp.first_name, bp.last_name, bp.nationality,
       bp.email, bp.phone, bp.special_requirements
FROM booking_participants bp
JOIN bookings b ON bp.booking_id = b.id
WHERE b.tour_type_id = 2 AND b.start_date = '2026-02-15'
ORDER BY b.booking_code;
```

---

## Оптимизация

### Индексы
1. **Основные поиски:**
   - `idx_bookings_contact_id` - Поиск бронирований клиента
   - `idx_bookings_status` - Фильтр по статусу (WHERE status != 'cancelled')
   - `idx_bookings_start_date` - Сортировка по дате

2. **Составные индексы:**
   - `idx_bookings_contact_status` - Часто используются вместе
   - `idx_tour_availability_open` - Активные туры (partial index)

3. **Текстовые поиски:**
   - GIN индекс на `booking_code` для быстрого поиска

### Производительность
- Используйте MATERIALIZED VIEW для сводных отчётов
- Архивируйте старые бронирования (> 3 лет)
- Регулярный VACUUM и ANALYZE

---

## Финансовый Поток

```
bookings (total_amount, discount_percent)
    ↓
final_amount = total_amount * (1 - discount_percent/100)
    ↓
booking_payments (payment_date, amount, status)
    ↓
Если сумма платежей == final_amount → payment_status = 'paid'
Если 0 < сумма < final_amount → payment_status = 'partial'
Если сумма == 0 → payment_status = 'unpaid'
    ↓
booking_refunds (если необходимо возвратить)
```

---

## Примеры Использования

### Создание нового бронирования
```sql
BEGIN;

INSERT INTO bookings
  (booking_code, contact_id, company_id, tour_type_id,
   booking_date, start_date, end_date, number_of_participants,
   total_amount, discount_percent, final_amount, status, created_by)
VALUES
  ('BK-2026-00123', 1, 1, 2, CURRENT_TIMESTAMP,
   CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE + INTERVAL '7 days', 25,
   6250, 10, 5625, 'pending', 'Suhail');

INSERT INTO booking_items (booking_id, item_type, description, quantity, unit_price, total_price)
VALUES (currval('bookings_id_seq'), 'activity', 'Desert Safari - Dune Bashing',
        25, 200, 5000);

INSERT INTO booking_items (booking_id, item_type, description, quantity, unit_price, total_price)
VALUES (currval('bookings_id_seq'), 'meal', 'Arabic Dinner', 25, 125, 3125);

COMMIT;
```

### Регистрация платежа
```sql
INSERT INTO booking_payments
  (booking_id, payment_date, amount, currency, payment_method, status)
VALUES
  (1, CURRENT_DATE, 5625, 'AED', 'bank-transfer', 'completed');

UPDATE bookings SET payment_status = 'paid' WHERE id = 1;
```

### Обновление статуса бронирования
```sql
BEGIN;

UPDATE bookings SET status = 'cancelled' WHERE id = 1;

INSERT INTO booking_changes
  (booking_id, change_type, old_value, new_value, reason, changed_by)
VALUES
  (1, 'status', 'confirmed', 'cancelled', 'Customer requested cancellation', 'Suhail');

INSERT INTO booking_cancellations
  (booking_id, cancellation_date, cancellation_reason, refund_policy, refund_amount)
VALUES
  (1, CURRENT_DATE, 'Customer request', 'full', 5625);

COMMIT;
```

---

## Безопасность

### Row Level Security (RLS)
```sql
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

CREATE POLICY bookings_own_company
  ON bookings FOR SELECT
  USING (company_id = current_user_company_id());
```

### Валидация Email
```sql
-- При вставке в booking_participants
ALTER TABLE booking_participants
ADD CONSTRAINT check_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');
```

---

## Статистика Данных

**Образец данные:**
- 10 типов туров (город, пустыня, яхта, авто, приключения)
- 30 бронирований (различных статусов)
- 6 активных промокодов
- 50 участников в бронированиях
- 15 платежей

**Распределение клиентов:**
- Компании из ОАЭ: 50%
- Туристы из России: 30%
- Туристы из других стран: 20%

**Валюты:** AED (основная), USD, RUB, KZT
