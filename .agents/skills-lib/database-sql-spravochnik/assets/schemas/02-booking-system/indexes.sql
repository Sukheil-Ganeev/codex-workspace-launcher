-- 02-Booking System Indexes

-- Основные индексы для быстрого поиска бронирований
CREATE INDEX idx_bookings_contact_id ON bookings(contact_id);
CREATE INDEX idx_bookings_booking_code ON bookings(booking_code);
CREATE INDEX idx_bookings_start_date ON bookings(start_date DESC);
CREATE INDEX idx_bookings_status ON bookings(status) WHERE status != 'cancelled';
CREATE INDEX idx_bookings_payment_status ON bookings(payment_status);
CREATE INDEX idx_bookings_created_at ON bookings(created_at DESC);

-- Составные индексы для частых операций
CREATE INDEX idx_bookings_contact_status ON bookings(contact_id, status);
CREATE INDEX idx_bookings_date_status ON bookings(start_date, status) WHERE status IN ('confirmed', 'completed');

-- Индексы для tour_types
CREATE INDEX idx_tour_types_category ON tour_types(category);

-- Индексы для booking_items
CREATE INDEX idx_booking_items_booking_id ON booking_items(booking_id);
CREATE INDEX idx_booking_items_type ON booking_items(item_type);

-- Индексы для booking_participants
CREATE INDEX idx_booking_participants_booking_id ON booking_participants(booking_id);
CREATE INDEX idx_booking_participants_passport ON booking_participants(passport_number);
CREATE INDEX idx_booking_participants_nationality ON booking_participants(nationality);

-- Индексы для booking_payments
CREATE INDEX idx_booking_payments_booking_id ON booking_payments(booking_id);
CREATE INDEX idx_booking_payments_payment_date ON booking_payments(payment_date DESC);
CREATE INDEX idx_booking_payments_status ON booking_payments(status);
CREATE INDEX idx_booking_payments_method ON booking_payments(payment_method);

-- Индексы для booking_refunds
CREATE INDEX idx_booking_refunds_booking_id ON booking_refunds(booking_id);
CREATE INDEX idx_booking_refunds_refund_date ON booking_refunds(refund_date DESC);
CREATE INDEX idx_booking_refunds_status ON booking_refunds(status);

-- Индексы для booking_changes
CREATE INDEX idx_booking_changes_booking_id ON booking_changes(booking_id);
CREATE INDEX idx_booking_changes_changed_at ON booking_changes(changed_at DESC);
CREATE INDEX idx_booking_changes_type ON booking_changes(change_type);

-- Индексы для booking_cancellations
CREATE INDEX idx_booking_cancellations_booking_id ON booking_cancellations(booking_id);
CREATE INDEX idx_booking_cancellations_date ON booking_cancellations(cancellation_date DESC);

-- Индексы для promo_codes
CREATE INDEX idx_promo_codes_code ON promo_codes(code);
CREATE INDEX idx_promo_codes_active ON promo_codes(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_promo_codes_valid_dates ON promo_codes(valid_from, valid_until);

-- Индексы для promo_code_usage
CREATE INDEX idx_promo_code_usage_promo_id ON promo_code_usage(promo_code_id);
CREATE INDEX idx_promo_code_usage_booking_id ON promo_code_usage(booking_id);

-- Индексы для booking_notifications
CREATE INDEX idx_booking_notifications_booking_id ON booking_notifications(booking_id);
CREATE INDEX idx_booking_notifications_is_sent ON booking_notifications(is_sent) WHERE is_sent = FALSE;
CREATE INDEX idx_booking_notifications_type ON booking_notifications(notification_type);

-- Индексы для booking_reviews
CREATE INDEX idx_booking_reviews_booking_id ON booking_reviews(booking_id);
CREATE INDEX idx_booking_reviews_contact_id ON booking_reviews(contact_id);
CREATE INDEX idx_booking_reviews_rating ON booking_reviews(rating);
CREATE INDEX idx_booking_reviews_is_verified ON booking_reviews(is_verified);

-- Индексы для tour_availability
CREATE INDEX idx_tour_availability_tour_type_id ON tour_availability(tour_type_id);
CREATE INDEX idx_tour_availability_tour_date ON tour_availability(tour_date);
CREATE INDEX idx_tour_availability_status ON tour_availability(status) WHERE status != 'cancelled';

-- Частичный индекс для активных открытых туров
CREATE INDEX idx_tour_availability_open ON tour_availability(tour_date) WHERE status = 'open' AND available_slots > 0;

-- Индексы для booking_sources
CREATE INDEX idx_booking_sources_booking_id ON booking_sources(booking_id);
CREATE INDEX idx_booking_sources_country ON booking_sources(source_country);
CREATE INDEX idx_booking_sources_referrer_type ON booking_sources(referrer_type);
