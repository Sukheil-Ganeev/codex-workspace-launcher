-- 02-Booking System Typical Queries

-- 1. Активные бронирования с информацией о туре и клиенте
SELECT
    b.id,
    b.booking_code,
    c.first_name || ' ' || c.last_name AS client_name,
    comp.name AS company_name,
    tt.name AS tour_name,
    b.start_date,
    b.end_date,
    b.number_of_participants,
    b.final_amount,
    b.status,
    b.payment_status
FROM bookings b
INNER JOIN contacts c ON b.contact_id = c.id
LEFT JOIN companies comp ON b.company_id = comp.id
LEFT JOIN tour_types tt ON b.tour_type_id = tt.id
WHERE b.status IN ('confirmed', 'pending')
ORDER BY b.start_date ASC;

-- 2. Доход по турам (последние 30 дней)
SELECT
    tt.name AS tour_name,
    COUNT(DISTINCT b.id) AS booking_count,
    SUM(b.final_amount) AS total_revenue,
    AVG(b.final_amount) AS avg_booking_value,
    SUM(b.number_of_participants) AS total_participants
FROM bookings b
INNER JOIN tour_types tt ON b.tour_type_id = tt.id
WHERE b.status = 'completed'
    AND b.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY tt.id, tt.name
ORDER BY total_revenue DESC;

-- 3. Статус платежей по бронированиям
SELECT
    b.booking_code,
    c.first_name || ' ' || c.last_name AS client,
    b.final_amount,
    COALESCE(SUM(bp.amount), 0) AS paid_amount,
    (b.final_amount - COALESCE(SUM(bp.amount), 0)) AS remaining_balance,
    b.payment_status,
    MAX(bp.payment_date) AS last_payment_date
FROM bookings b
INNER JOIN contacts c ON b.contact_id = c.id
LEFT JOIN booking_payments bp ON b.id = bp.booking_id AND bp.status = 'completed'
WHERE b.status IN ('confirmed', 'pending')
GROUP BY b.id, b.booking_code, c.first_name, c.last_name, b.final_amount, b.payment_status
ORDER BY remaining_balance DESC;

-- 4. Туры с доступными местами
SELECT
    ta.id,
    tt.name AS tour_name,
    ta.tour_date,
    ta.total_capacity,
    ta.available_slots,
    ta.price_per_person,
    ta.meeting_point,
    ta.meeting_time,
    ROUND(100.0 * (ta.total_capacity - ta.available_slots) / ta.total_capacity, 2) AS occupancy_percent,
    ta.status
FROM tour_availability ta
INNER JOIN tour_types tt ON ta.tour_type_id = tt.id
WHERE ta.status IN ('open', 'full')
ORDER BY ta.tour_date ASC;

-- 5. Найти клиентов с рекомендациями в соцсетях
SELECT
    c.id,
    c.first_name || ' ' || c.last_name AS client_name,
    c.email,
    c.mobile,
    COUNT(DISTINCT b.id) AS bookings_count,
    SUM(b.final_amount) AS total_spent,
    STRING_AGG(DISTINCT bs.source_country, ', ') AS source_countries
FROM bookings b
INNER JOIN contacts c ON b.contact_id = c.id
INNER JOIN booking_sources bs ON b.id = bs.booking_id
WHERE bs.referrer_type IN ('recommendation', 'social')
GROUP BY c.id, c.first_name, c.last_name, c.email, c.mobile
ORDER BY total_spent DESC;

-- 6. Предстоящие туры и их загруженность
SELECT
    ta.tour_date,
    tt.name AS tour_name,
    COUNT(DISTINCT bp.id) AS booked_participants,
    ta.total_capacity,
    (ta.total_capacity - COUNT(DISTINCT bp.id)) AS available_slots,
    ROUND(100.0 * COUNT(DISTINCT bp.id) / ta.total_capacity, 2) AS occupancy_percent,
    STRING_AGG(DISTINCT comp.name, ', ') AS companies_booked
FROM tour_availability ta
INNER JOIN tour_types tt ON ta.tour_type_id = tt.id
LEFT JOIN bookings b ON tt.id = b.tour_type_id AND b.start_date = ta.tour_date
LEFT JOIN booking_participants bp ON b.id = bp.booking_id
LEFT JOIN companies comp ON b.company_id = comp.id
WHERE ta.tour_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
GROUP BY ta.id, ta.tour_date, tt.name, ta.total_capacity
ORDER BY ta.tour_date ASC;

-- 7. Анализ использования промокодов
SELECT
    pc.code,
    pc.description,
    COUNT(DISTINCT pcu.booking_id) AS usage_count,
    SUM(pcu.discount_applied) AS total_discount,
    AVG(pcu.discount_applied) AS avg_discount,
    pc.max_uses,
    ROUND(100.0 * COUNT(DISTINCT pcu.booking_id) / COALESCE(pc.max_uses, 1), 2) AS usage_percent
FROM promo_codes pc
LEFT JOIN promo_code_usage pcu ON pc.id = pcu.promo_code_id
WHERE pc.is_active = TRUE
GROUP BY pc.id, pc.code, pc.description, pc.max_uses
ORDER BY usage_count DESC;

-- 8. Бронирования, требующие подтверждения платежа
SELECT
    b.id,
    b.booking_code,
    c.first_name || ' ' || c.last_name AS client,
    c.email,
    c.mobile,
    b.final_amount,
    COALESCE(SUM(bp.amount), 0) AS paid_amount,
    (b.final_amount - COALESCE(SUM(bp.amount), 0)) AS outstanding_balance,
    b.created_at::DATE AS booking_date,
    (CURRENT_DATE - b.created_at::DATE) AS days_since_booking
FROM bookings b
INNER JOIN contacts c ON b.contact_id = c.id
LEFT JOIN booking_payments bp ON b.id = bp.booking_id AND bp.status = 'completed'
WHERE b.payment_status != 'paid'
    AND b.status IN ('confirmed', 'pending')
GROUP BY b.id, c.first_name, c.last_name, c.email, c.mobile, b.final_amount, b.created_at, b.booking_code, b.payment_status
HAVING (b.final_amount - COALESCE(SUM(bp.amount), 0)) > 0
ORDER BY days_since_booking DESC, outstanding_balance DESC;

-- 9. Динамика продаж по источникам
SELECT
    bs.referrer_type,
    bs.source_country,
    COUNT(DISTINCT b.id) AS booking_count,
    SUM(b.final_amount) AS total_revenue,
    AVG(b.number_of_participants) AS avg_group_size,
    ROUND(100.0 * COUNT(DISTINCT b.id) /
        SUM(COUNT(DISTINCT b.id)) OVER (), 2) AS percent_of_total
FROM booking_sources bs
INNER JOIN bookings b ON bs.booking_id = b.id
WHERE b.status = 'completed'
    AND b.created_at >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY bs.referrer_type, bs.source_country
ORDER BY total_revenue DESC;

-- 10. Список участников для экскурсии (с фильтром по дате)
SELECT
    ta.tour_date,
    tt.name AS tour_name,
    b.booking_code,
    comp.name AS company_name,
    bp.first_name,
    bp.last_name,
    bp.email,
    bp.phone,
    bp.nationality,
    bp.special_requirements
FROM tour_availability ta
INNER JOIN tour_types tt ON ta.tour_type_id = tt.id
INNER JOIN bookings b ON tt.id = b.tour_type_id AND b.start_date = ta.tour_date
INNER JOIN booking_participants bp ON b.id = bp.booking_id
LEFT JOIN companies comp ON b.company_id = comp.id
WHERE ta.tour_date = CURRENT_DATE + INTERVAL '3 days'
    AND b.status = 'confirmed'
ORDER BY b.booking_code, bp.first_name;

-- 11. Отмены бронирований и их причины
SELECT
    bc.booking_id,
    b.booking_code,
    c.first_name || ' ' || c.last_name AS client,
    tt.name AS tour_name,
    bc.cancellation_date,
    bc.cancellation_reason,
    bc.refund_policy,
    bc.refund_amount,
    bc.cancellation_fee
FROM booking_cancellations bc
INNER JOIN bookings b ON bc.booking_id = b.id
INNER JOIN contacts c ON b.contact_id = c.id
LEFT JOIN tour_types tt ON b.tour_type_id = tt.id
WHERE bc.cancellation_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY bc.cancellation_date DESC;

-- 12. Рейтинги и отзывы туров
SELECT
    tt.name AS tour_name,
    COUNT(DISTINCT br.id) AS review_count,
    AVG(br.rating) AS avg_rating,
    SUM(CASE WHEN br.would_recommend = TRUE THEN 1 ELSE 0 END) AS recommend_count,
    ROUND(100.0 * SUM(CASE WHEN br.would_recommend = TRUE THEN 1 ELSE 0 END) /
        COUNT(DISTINCT br.id), 2) AS recommend_percent,
    STRING_AGG(DISTINCT br.title, '; ') AS review_titles
FROM tour_types tt
INNER JOIN bookings b ON tt.id = b.tour_type_id
LEFT JOIN booking_reviews br ON b.id = br.booking_id AND br.is_verified = TRUE
WHERE b.status = 'completed'
GROUP BY tt.id, tt.name
HAVING COUNT(DISTINCT br.id) > 0
ORDER BY avg_rating DESC;

-- 13. Детальный отчет по бронированию (полный профиль)
SELECT
    b.id,
    b.booking_code,
    c.first_name || ' ' || c.last_name AS client,
    c.email,
    c.mobile,
    comp.name AS company_name,
    tt.name AS tour_name,
    b.start_date,
    b.end_date,
    b.number_of_participants,
    b.total_amount,
    b.discount_percent,
    b.final_amount,
    b.status,
    b.payment_status,
    COALESCE(SUM(DISTINCT bp.amount), 0) AS paid_amount,
    (b.final_amount - COALESCE(SUM(DISTINCT bp.amount), 0)) AS balance_due,
    COUNT(DISTINCT bpart.id) AS participant_count,
    MAX(bp.payment_date) AS last_payment_date,
    b.notes
FROM bookings b
INNER JOIN contacts c ON b.contact_id = c.id
LEFT JOIN companies comp ON b.company_id = comp.id
LEFT JOIN tour_types tt ON b.tour_type_id = tt.id
LEFT JOIN booking_payments bp ON b.id = bp.booking_id
LEFT JOIN booking_participants bpart ON b.id = bpart.booking_id
WHERE b.booking_code = 'BK001'  -- Заменить на нужный код
GROUP BY b.id, c.first_name, c.last_name, c.email, c.mobile, comp.name,
         tt.name, b.start_date, b.end_date, b.number_of_participants,
         b.total_amount, b.discount_percent, b.final_amount, b.status,
         b.payment_status, b.notes;

-- 14. Топ-10 клиентов по сумме затрат
SELECT
    c.id,
    c.first_name || ' ' || c.last_name AS client_name,
    c.email,
    comp.name AS company_name,
    COUNT(DISTINCT b.id) AS booking_count,
    SUM(b.final_amount) AS total_spent,
    AVG(b.final_amount) AS avg_booking_value,
    SUM(b.number_of_participants) AS total_participants,
    MAX(b.created_at) AS last_booking_date
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
INNER JOIN bookings b ON c.id = b.contact_id
WHERE b.status = 'completed'
    AND b.created_at >= CURRENT_DATE - INTERVAL '365 days'
GROUP BY c.id, c.first_name, c.last_name, c.email, comp.name
ORDER BY total_spent DESC
LIMIT 10;

-- 15. Финансовый отчет по статусам платежей
SELECT
    b.payment_status,
    COUNT(DISTINCT b.id) AS booking_count,
    SUM(b.final_amount) AS total_amount,
    ROUND(AVG(b.final_amount), 2) AS avg_booking_amount,
    ROUND(100.0 * COUNT(DISTINCT b.id) /
        SUM(COUNT(DISTINCT b.id)) OVER (), 2) AS percent_of_bookings
FROM bookings b
WHERE b.status IN ('confirmed', 'pending', 'completed')
    AND b.created_at >= CURRENT_DATE - INTERVAL '60 days'
GROUP BY b.payment_status
ORDER BY total_amount DESC;
