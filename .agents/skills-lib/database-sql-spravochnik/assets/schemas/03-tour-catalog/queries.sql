-- 03-Tour Catalog Queries

-- 1. Топ туры по количеству рецензий и рейтингу
SELECT t.id, t.name, COUNT(tr.id) as review_count, AVG(tr.rating) as avg_rating
FROM tours t
LEFT JOIN tour_reviews tr ON t.id = tr.tour_id AND tr.is_verified = TRUE
WHERE t.is_active = TRUE
GROUP BY t.id, t.name
HAVING COUNT(tr.id) > 0
ORDER BY avg_rating DESC, review_count DESC;

-- 2. Туры с ценами и включениями
SELECT t.name, tp.price, ti.description as inclusion
FROM tours t
JOIN tour_pricing tp ON t.id = tp.tour_id
JOIN tour_inclusions ti ON t.id = ti.tour_id
WHERE t.is_active = TRUE AND tp.is_active = TRUE
ORDER BY t.name, tp.price;

-- 3. Доступные туры на конкретную дату
SELECT t.name, ta.tour_date, ta.available_slots, ta.price_per_person,
       tg.first_name || ' ' || tg.last_name as guide_name
FROM tour_availability ta
JOIN tours t ON ta.tour_type_id = t.id
LEFT JOIN tour_guides tg ON ta.guide_id = tg.id
WHERE ta.tour_date = CURRENT_DATE + INTERVAL '5 days' AND ta.status = 'open'
ORDER BY ta.tour_date;

-- 4. Маршруты тура с точками GPS
SELECT t.name, tr.stop_order, tr.location_name, tr.latitude, tr.longitude,
       tr.duration_minutes, tr.description
FROM tours t
JOIN tour_routes tr ON t.id = tr.tour_id
WHERE t.id = 1
ORDER BY tr.stop_order;

-- 5. Часто задаваемые вопросы по турам
SELECT t.name, tf.question, tf.answer, tf.display_order
FROM tours t
JOIN tour_faqs tf ON t.id = tf.tour_id
WHERE t.is_active = TRUE
ORDER BY t.name, tf.display_order;

-- 6. Гиды с их специализацией и рейтингом
SELECT g.first_name || ' ' || g.last_name as guide_name,
       ARRAY_TO_STRING(g.languages, ', ') as languages,
       g.experience_years, g.rating
FROM tour_guides g
WHERE g.is_active = TRUE
ORDER BY g.rating DESC, g.experience_years DESC;

-- 7. Транспортные средства и их доступность
SELECT v.registration_number, v.vehicle_type, v.model,
       v.year, v.capacity, v.is_active
FROM tour_vehicles v
WHERE v.is_active = TRUE
ORDER BY v.vehicle_type, v.year DESC;

-- 8. Теги туров и их применимость
SELECT tt.name as tag, COUNT(tta.tour_id) as tour_count
FROM tour_tags tt
LEFT JOIN tour_tag_assignments tta ON tt.id = tta.tag_id
GROUP BY tt.id, tt.name
ORDER BY tour_count DESC;

-- 9. Сезонные цены по турам
SELECT t.name, tp.season, tp.min_quantity || '-' || tp.max_quantity as group_size,
       tp.price as price_per_person
FROM tours t
JOIN tour_pricing tp ON t.id = tp.tour_id
WHERE tp.is_active = TRUE
ORDER BY t.name, tp.season;

-- 10. Категории туров с количеством предложений
SELECT tc.name, COUNT(t.id) as tour_count, AVG(t.price_per_person) as avg_price
FROM tour_categories tc
LEFT JOIN tours t ON tc.id = t.category_id AND t.is_active = TRUE
GROUP BY tc.id, tc.name
ORDER BY tour_count DESC;

-- 11. Полный профиль тура
SELECT t.id, t.name, tc.name as category, t.description,
       t.duration_hours, t.difficulty_level, t.min_participants, t.max_participants,
       t.price_per_person, COUNT(DISTINCT tr.id) as review_count,
       AVG(tr.rating) as avg_rating
FROM tours t
LEFT JOIN tour_categories tc ON t.category_id = tc.id
LEFT JOIN tour_reviews tr ON t.id = tr.tour_id AND tr.is_verified = TRUE
WHERE t.is_active = TRUE
GROUP BY t.id, t.name, tc.name;

-- 12. Рецензии с информацией о клиентах
SELECT t.name, tr.rating, tr.title, tr.comment, c.first_name, c.last_name,
       tr.date_visited, tr.is_verified
FROM tour_reviews tr
JOIN tours t ON tr.tour_id = t.id
LEFT JOIN contacts c ON tr.contact_id = c.id
WHERE tr.is_verified = TRUE
ORDER BY tr.created_at DESC;

-- 13. Поиск туров по сложности и продолжительности
SELECT t.name, t.difficulty_level, t.duration_hours, t.price_per_person,
       COUNT(DISTINCT tr.id) as review_count
FROM tours t
LEFT JOIN tour_reviews tr ON t.id = tr.tour_id AND tr.is_verified = TRUE
WHERE t.is_active = TRUE
  AND t.difficulty_level = 'moderate'
  AND t.duration_hours BETWEEN 3 AND 8
GROUP BY t.id, t.name
ORDER BY t.price_per_person;

-- 14. Выручка по категориям туров (расчетная)
SELECT tc.name, COUNT(DISTINCT b.id) as bookings,
       SUM(b.final_amount) as total_revenue
FROM tour_categories tc
LEFT JOIN tours t ON tc.id = t.category_id
LEFT JOIN bookings b ON t.id = b.tour_type_id AND b.status = 'completed'
GROUP BY tc.id, tc.name
ORDER BY total_revenue DESC NULLS LAST;
