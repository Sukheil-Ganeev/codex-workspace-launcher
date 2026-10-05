# 03-Tour Catalog Schema

**Назначение:** Полный каталог туров и услуг с информацией о маршрутах, ценах, гидах, транспорте и отзывах клиентов.

**Версия:** 1.0.0
**Статус:** Production-ready
**Язык БД:** PostgreSQL 14+

---

## Таблицы

### `tour_categories`
Категории туров (City Tours, Desert Safari, Water Activities и т.д.)

### `tours`
Основной каталог туров с полной информацией.

**Ключевые поля:**
- `slug` - URL-friendly идентификатор (UNIQUE)
- `difficulty_level` - easy, moderate, hard, extreme
- `price_per_person`, `currency` - Базовая цена
- `included_items`, `not_included_items` - Массивы услуг
- `languages` - Доступные языки
- `cancellation_policy`, `refund_policy` - Условия отмены

### `tour_routes`
Маршруты туров с GPS координатами и типами остановок.

**Типы остановок:** pickup, activity, meal, photo, rest

### `tour_schedules`
Расписание туров (дни недели, гиды, вместимость).

### `tour_pricing`
Динамические цены в зависимости от количества участников и сезона.

**Сезоны:** high, low, peak

### `tour_images`
Фотографии туров с возможностью выделения главного изображения.

### `tour_guides`
Информация о гидах (языки, лицензия, опыт, рейтинг).

### `tour_vehicles`
Транспортные средства (яхты, джипы, вертолеты и т.д.)

### `tour_reviews`
Рецензии и отзывы клиентов с верификацией.

### `tour_faqs`
Часто задаваемые вопросы по каждому туру.

### `tour_inclusions` & `tour_exclusions`
Детальные списки включений и исключений.

### `tour_tags`
Теги для гибкой классификации (Popular, New, VIP, Family).

---

## Типичные Запросы

### 1. Топ туры по рейтингам
```sql
SELECT t.name, AVG(tr.rating) as rating, COUNT(tr.id) as reviews
FROM tours t
LEFT JOIN tour_reviews tr ON t.id = tr.tour_id AND tr.is_verified = TRUE
WHERE t.is_active = TRUE
GROUP BY t.id
HAVING COUNT(tr.id) > 0
ORDER BY rating DESC;
```

### 2. Доступные туры на дату
```sql
SELECT t.name, ta.available_slots, ta.price_per_person, tg.first_name
FROM tour_availability ta
JOIN tours t ON ta.tour_type_id = t.id
LEFT JOIN tour_guides tg ON ta.guide_id = tg.id
WHERE ta.tour_date = '2026-02-15' AND ta.status = 'open';
```

### 3. Маршрут тура
```sql
SELECT tr.stop_order, tr.location_name, tr.latitude, tr.longitude,
       tr.duration_minutes, tr.stop_type
FROM tour_routes tr
WHERE tr.tour_id = 1
ORDER BY tr.stop_order;
```

---

## Оптимизация

- Индексы по `slug`, `category_id`, `is_active`
- Полнотекстовый поиск по названиям и описаниям
- Кеширование часто запрашиваемых категорий

---

## Примеры Использования

### Добавление нового тура
```sql
BEGIN;

INSERT INTO tours (name, slug, category_id, description, duration_hours, difficulty_level, price_per_person)
VALUES ('New Adventure Tour', 'new-adventure-tour', 4, 'An exciting new experience', 5, 'moderate', 300);

INSERT INTO tour_inclusions (tour_id, inclusion_type, description)
VALUES (currval('tours_id_seq'), 'transportation', 'Luxury transport');

INSERT INTO tour_inclusions (tour_id, inclusion_type, description)
VALUES (currval('tours_id_seq'), 'meal', 'Lunch included');

COMMIT;
```

### Запрос маршрута с геокодингом
```sql
SELECT tr.location_name, tr.latitude, tr.longitude,
       ST_DistanceSphere(
         ST_MakePoint(55.2744, 25.1972),
         ST_MakePoint(tr.longitude, tr.latitude)
       ) / 1000 as distance_km
FROM tour_routes tr
WHERE tr.tour_id = 1
ORDER BY tr.stop_order;
```

---

## SEO и Фронтенд

- Используйте `slug` для URL-ов: `/tours/desert-safari-plus`
- Meta-описание из `short_description`
- Изображения с `is_featured = TRUE` на главной странице
- JSON-LD структурированные данные для Google

---

## Производительность

- Материализованные представления для популярных туров
- Кеширование в Redis: tour_catalog_[tour_id]
- Индекс GIN для полнотекстового поиска по названиям
