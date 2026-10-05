-- 02-Booking System Sample Data

-- Таблица tour_types
INSERT INTO tour_types (name, description, category, min_participants, max_participants) VALUES
('Dubai City Tour', 'Guided tour of Dubai landmarks: Burj Khalifa, Dubai Mall, Palm Jumeirah', 'city-tour', 1, 30),
('Desert Safari', 'Dune bashing, camel ride, Arabic dinner in the desert', 'desert-safari', 2, 40),
('Yacht Cruise', 'Luxury yacht experience with drinks and sunset viewing', 'yacht', 4, 50),
('Ferrari Driving', 'Drive a Ferrari supercar on professional track', 'adventure', 1, 6),
('Abu Dhabi Day Trip', 'Sheikh Zayed Mosque, Louvre Abu Dhabi, Emirates Palace', 'city-tour', 2, 35),
('Snorkeling Trip', 'Coral reef snorkeling with professional guide', 'adventure', 4, 30),
('Sharjah Culture Tour', 'Blue Souk, museums, traditional souks', 'city-tour', 2, 25),
('Helicopter Tour', 'Aerial view of Dubai Palm, marina, coastline', 'adventure', 1, 5),
('Ras Al Khaimah Hiking', 'Jebal Jais mountain hiking with guides', 'adventure', 2, 15),
('Spa & Wellness Day', 'Luxury spa treatment at 5-star resort', 'city-tour', 1, 20);

-- Таблица bookings (примерно 30 бронирований)
INSERT INTO bookings (booking_code, contact_id, company_id, tour_type_id, booking_date, start_date, end_date, number_of_participants, total_amount, currency, discount_percent, final_amount, status, payment_status, notes, created_by) VALUES
('BK001', 1, 1, 1, CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_DATE + INTERVAL '15 days', CURRENT_DATE + INTERVAL '15 days', 40, 8000, 'AED', 10, 7200, 'confirmed', 'paid', 'Group tour - Al-Fardan team building', 'Suhail'),
('BK002', 3, 2, 2, CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE + INTERVAL '10 days', 50, 12500, 'AED', 0, 12500, 'confirmed', 'paid', 'Emirates NBD desert experience', 'Suhail'),
('BK003', 5, 3, 3, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_DATE + INTERVAL '8 days', CURRENT_DATE + INTERVAL '8 days', 30, 15000, 'AED', 5, 14250, 'confirmed', 'partial', 'Emaar executive yacht charter', 'Suhail'),
('BK004', 7, 4, 4, CURRENT_TIMESTAMP - INTERVAL '10 days', CURRENT_DATE + INTERVAL '20 days', CURRENT_DATE + INTERVAL '20 days', 6, 18000, 'AED', 15, 15300, 'confirmed', 'paid', 'DP World Ferrari track day', 'Marcel'),
('BK005', 9, 5, 5, CURRENT_TIMESTAMP - INTERVAL '5 days', CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '5 days', 25, 6250, 'AED', 0, 6250, 'confirmed', 'paid', 'ADIB Abu Dhabi exploration', 'Suhail'),
('BK006', 11, 6, 2, CURRENT_TIMESTAMP, CURRENT_DATE + INTERVAL '3 days', CURRENT_DATE + INTERVAL '3 days', 35, 8750, 'AED', 0, 8750, 'pending', 'unpaid', 'Rotana Hotels desert safari', 'Suhail'),
('BK007', 13, 7, 1, CURRENT_TIMESTAMP - INTERVAL '25 days', CURRENT_DATE + INTERVAL '12 days', CURRENT_DATE + INTERVAL '12 days', 45, 9000, 'AED', 20, 7200, 'confirmed', 'paid', 'Spinneys team outing', 'Assistant'),
('BK008', 15, 8, 3, CURRENT_TIMESTAMP - INTERVAL '12 days', CURRENT_DATE + INTERVAL '22 days', CURRENT_DATE + INTERVAL '22 days', 20, 10000, 'AED', 0, 10000, 'confirmed', 'paid', 'Landmark Group VIP yacht experience', 'Suhail'),
('BK009', 17, 9, 5, CURRENT_TIMESTAMP - INTERVAL '8 days', CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE + INTERVAL '7 days', 30, 7500, 'AED', 10, 6750, 'confirmed', 'partial', 'RAK Petroleum Abu Dhabi trip', 'Marcel'),
('BK010', 19, 10, 2, CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE + INTERVAL '10 days', 28, 7000, 'AED', 0, 7000, 'pending', 'unpaid', 'Damas Jewellery desert experience', 'Suhail'),
('BK011', 2, 1, 6, CURRENT_TIMESTAMP - INTERVAL '14 days', CURRENT_DATE + INTERVAL '14 days', CURRENT_DATE + INTERVAL '14 days', 8, 4000, 'AED', 0, 4000, 'confirmed', 'paid', 'Al-Fardan snorkeling trip', 'Assistant'),
('BK012', 4, 2, 8, CURRENT_TIMESTAMP - INTERVAL '20 days', CURRENT_DATE + INTERVAL '11 days', CURRENT_DATE + INTERVAL '11 days', 4, 8000, 'AED', 5, 7600, 'confirmed', 'paid', 'Emirates NBD helicopter tour', 'Suhail'),
('BK013', 6, 3, 7, CURRENT_TIMESTAMP - INTERVAL '18 days', CURRENT_DATE + INTERVAL '16 days', CURRENT_DATE + INTERVAL '16 days', 15, 3750, 'AED', 0, 3750, 'confirmed', 'paid', 'Emaar Sharjah culture tour', 'Suhail'),
('BK014', 8, 4, 9, CURRENT_TIMESTAMP - INTERVAL '9 days', CURRENT_DATE + INTERVAL '25 days', CURRENT_DATE + INTERVAL '25 days', 12, 4800, 'AED', 10, 4320, 'pending', 'unpaid', 'DP World Jebel Jais hiking', 'Marcel'),
('BK015', 10, 5, 10, CURRENT_TIMESTAMP - INTERVAL '6 days', CURRENT_DATE + INTERVAL '6 days', CURRENT_DATE + INTERVAL '6 days', 10, 5000, 'AED', 0, 5000, 'confirmed', 'paid', 'ADIB spa and wellness day', 'Assistant'),
('BK016', 12, 6, 1, CURRENT_TIMESTAMP - INTERVAL '22 days', CURRENT_DATE + INTERVAL '13 days', CURRENT_DATE + INTERVAL '13 days', 50, 10000, 'AED', 15, 8500, 'confirmed', 'paid', 'Rotana Hotels Dubai city tour', 'Suhail'),
('BK017', 14, 7, 4, CURRENT_TIMESTAMP - INTERVAL '7 days', CURRENT_DATE + INTERVAL '18 days', CURRENT_DATE + INTERVAL '18 days', 5, 15000, 'AED', 0, 15000, 'confirmed', 'partial', 'Spinneys Ferrari experience', 'Suhail'),
('BK018', 16, 8, 2, CURRENT_TIMESTAMP - INTERVAL '11 days', CURRENT_DATE + INTERVAL '21 days', CURRENT_DATE + INTERVAL '21 days', 38, 9500, 'AED', 5, 9025, 'pending', 'unpaid', 'Landmark Group desert safari', 'Assistant'),
('BK019', 18, 9, 3, CURRENT_TIMESTAMP - INTERVAL '13 days', CURRENT_DATE + INTERVAL '9 days', CURRENT_DATE + INTERVAL '9 days', 25, 12500, 'AED', 0, 12500, 'confirmed', 'paid', 'RAK Petroleum yacht cruise', 'Suhail'),
('BK020', 20, 10, 5, CURRENT_TIMESTAMP - INTERVAL '4 days', CURRENT_DATE + INTERVAL '11 days', CURRENT_DATE + INTERVAL '11 days', 20, 5000, 'AED', 10, 4500, 'pending', 'unpaid', 'Damas Abu Dhabi day trip', 'Suhail'),
('BK021', 1, 1, 6, CURRENT_TIMESTAMP - INTERVAL '16 days', CURRENT_DATE + INTERVAL '4 days', CURRENT_DATE + INTERVAL '4 days', 6, 3000, 'AED', 0, 3000, 'confirmed', 'paid', 'Al-Fardan snorkeling group', 'Suhail'),
('BK022', 3, 2, 7, CURRENT_TIMESTAMP - INTERVAL '24 days', CURRENT_DATE + INTERVAL '19 days', CURRENT_DATE + INTERVAL '19 days', 18, 4500, 'AED', 10, 4050, 'confirmed', 'paid', 'Emirates NBD Sharjah tour', 'Assistant'),
('BK023', 5, 3, 8, CURRENT_TIMESTAMP - INTERVAL '11 days', CURRENT_DATE + INTERVAL '24 days', CURRENT_DATE + INTERVAL '24 days', 3, 7200, 'AED', 0, 7200, 'pending', 'unpaid', 'Emaar helicopter experience', 'Suhail'),
('BK024', 7, 4, 1, CURRENT_TIMESTAMP - INTERVAL '19 days', CURRENT_DATE + INTERVAL '17 days', CURRENT_DATE + INTERVAL '17 days', 55, 11000, 'AED', 5, 10450, 'confirmed', 'partial', 'DP World city exploration tour', 'Marcel'),
('BK025', 9, 5, 10, CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_DATE + INTERVAL '2 days', CURRENT_DATE + INTERVAL '2 days', 8, 4000, 'AED', 0, 4000, 'pending', 'unpaid', 'ADIB wellness retreat', 'Assistant'),
('BK026', 11, 6, 3, CURRENT_TIMESTAMP - INTERVAL '28 days', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '5 days', 32, 16000, 'AED', 0, 16000, 'completed', 'paid', 'Rotana yacht charter - completed', 'Suhail'),
('BK027', 13, 7, 4, CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_DATE + INTERVAL '30 days', CURRENT_DATE + INTERVAL '30 days', 4, 12000, 'AED', 20, 9600, 'confirmed', 'paid', 'Spinneys Ferrari booking', 'Assistant'),
('BK028', 15, 8, 2, CURRENT_TIMESTAMP - INTERVAL '17 days', CURRENT_DATE + INTERVAL '28 days', CURRENT_DATE + INTERVAL '28 days', 42, 10500, 'AED', 0, 10500, 'pending', 'unpaid', 'Landmark Group safari', 'Suhail'),
('BK029', 17, 9, 9, CURRENT_TIMESTAMP - INTERVAL '6 days', CURRENT_DATE + INTERVAL '23 days', CURRENT_DATE + INTERVAL '23 days', 10, 4000, 'AED', 15, 3400, 'confirmed', 'paid', 'RAK Petroleum Jebel Jais hike', 'Marcel'),
('BK030', 19, 10, 1, CURRENT_TIMESTAMP - INTERVAL '12 days', CURRENT_DATE + INTERVAL '6 days', CURRENT_DATE + INTERVAL '6 days', 30, 6000, 'AED', 0, 6000, 'confirmed', 'partial', 'Damas Dubai city tour VIP', 'Suhail');

-- Таблица booking_items
INSERT INTO booking_items (booking_id, item_type, description, quantity, unit_price, total_price) VALUES
(1, 'transportation', 'Minibus rental for 40 people', 1, 2000, 2000),
(1, 'guide', 'Professional tour guide', 1, 1000, 1000),
(1, 'meal', 'Lunch at Dubai mall', 1, 3000, 3000),
(1, 'activity', 'Burj Khalifa entrance tickets', 40, 150, 6000),
(2, 'transportation', 'Large coach rental', 1, 3000, 3000),
(2, 'guide', 'Desert safari guide', 1, 1500, 1500),
(2, 'meal', 'Arabic dinner in desert', 50, 150, 7500),
(2, 'activity', 'Camel ride and dune bashing', 50, 100, 5000),
(3, 'yacht', 'Luxury yacht rental', 1, 10000, 10000),
(3, 'beverages', 'Premium drinks package', 30, 150, 4500),
(3, 'activity', 'Water sports equipment', 30, 20, 600),
(4, 'activity', 'Ferrari driving experience', 6, 3000, 18000),
(5, 'transportation', 'Coach rental', 1, 2500, 2500),
(5, 'guide', 'Professional guide', 1, 1000, 1000),
(5, 'activity', 'Louvre Abu Dhabi tickets', 25, 70, 1750);

-- Таблица booking_participants
INSERT INTO booking_participants (booking_id, first_name, last_name, email, phone, nationality, date_of_birth) VALUES
(1, 'Ahmed', 'Al-Mansouri', 'ahmed@alfardan.ae', '+971501234567', 'UAE', '1985-03-15'),
(1, 'Fatima', 'Al-Mazrouei', 'fatima@alfardan.ae', '+971501234568', 'UAE', '1990-07-22'),
(2, 'Mohammed', 'Al-Suwaidi', 'mohammed@emiratesnbd.com', '+971505678901', 'UAE', '1982-05-10'),
(3, 'Elena', 'Petrova', 'elena@emiratesnbd.com', '+971509876543', 'Russia', '1988-09-14'),
(4, 'Sergei', 'Volkov', 'sergei@emaar.com', '+971502468135', 'Russia', '1980-11-28'),
(5, 'Amira', 'Khan', 'amira@emaar.com', '+971503691357', 'Pakistan', '1995-01-19'),
(26, 'Viktor', 'Smirnov', 'viktor@dpworld.com', '+971504135792', 'Russia', '1987-06-05'),
(26, 'Noor', 'Al-Kaabi', 'noor@dpworld.com', '+971505792468', 'UAE', '1991-08-30'),
(26, 'Yuri', 'Petrov', 'yuri@adib.ae', '+971506543210', 'Russia', '1983-02-17'),
(27, 'Layla', 'Hassan', 'layla@adib.ae', '+971506543211', 'UAE', '1992-04-09');

-- Таблица booking_payments
INSERT INTO booking_payments (booking_id, payment_date, amount, currency, payment_method, status) VALUES
(1, CURRENT_DATE - INTERVAL '25 days', 7200, 'AED', 'bank-transfer', 'completed'),
(2, CURRENT_DATE - INTERVAL '15 days', 12500, 'AED', 'credit-card', 'completed'),
(3, CURRENT_DATE - INTERVAL '10 days', 7125, 'AED', 'bank-transfer', 'completed'),
(4, CURRENT_DATE - INTERVAL '5 days', 15300, 'AED', 'credit-card', 'completed'),
(5, CURRENT_DATE - INTERVAL '2 days', 6250, 'AED', 'bank-transfer', 'completed'),
(7, CURRENT_DATE - INTERVAL '20 days', 7200, 'AED', 'bank-transfer', 'completed'),
(8, CURRENT_DATE - INTERVAL '7 days', 10000, 'AED', 'credit-card', 'completed'),
(11, CURRENT_DATE - INTERVAL '10 days', 4000, 'AED', 'bank-transfer', 'completed'),
(12, CURRENT_DATE - INTERVAL '15 days', 7600, 'AED', 'credit-card', 'completed'),
(13, CURRENT_DATE - INTERVAL '13 days', 3750, 'AED', 'bank-transfer', 'completed'),
(15, CURRENT_DATE - INTERVAL '1 day', 5000, 'AED', 'bank-transfer', 'completed'),
(16, CURRENT_DATE - INTERVAL '17 days', 8500, 'AED', 'credit-card', 'completed'),
(19, CURRENT_DATE - INTERVAL '8 days', 12500, 'AED', 'bank-transfer', 'completed'),
(26, CURRENT_DATE - INTERVAL '5 days', 16000, 'AED', 'bank-transfer', 'completed'),
(27, CURRENT_DATE, 9600, 'AED', 'credit-card', 'completed');

-- Таблица tour_availability
INSERT INTO tour_availability (tour_type_id, tour_date, total_capacity, available_slots, price_per_person, meeting_point, meeting_time, status) VALUES
(1, CURRENT_DATE + INTERVAL '5 days', 30, 22, 200, 'Dubai Mall Main Entrance', '09:00:00', 'open'),
(1, CURRENT_DATE + INTERVAL '12 days', 35, 35, 200, 'Dubai Mall Main Entrance', '09:00:00', 'open'),
(1, CURRENT_DATE + INTERVAL '15 days', 40, 0, 200, 'Dubai Mall Main Entrance', '09:00:00', 'full'),
(2, CURRENT_DATE + INTERVAL '3 days', 50, 20, 250, 'Dune Bashing Camp', '15:00:00', 'open'),
(2, CURRENT_DATE + INTERVAL '8 days', 45, 10, 250, 'Dune Bashing Camp', '15:00:00', 'open'),
(2, CURRENT_DATE + INTERVAL '10 days', 40, 0, 250, 'Dune Bashing Camp', '15:00:00', 'full'),
(3, CURRENT_DATE + INTERVAL '7 days', 50, 25, 500, 'Marina Mall Pier', '16:00:00', 'open'),
(3, CURRENT_DATE + INTERVAL '22 days', 50, 30, 500, 'Marina Mall Pier', '16:00:00', 'open'),
(4, CURRENT_DATE + INTERVAL '18 days', 6, 2, 3000, 'Dubai Autodrome', '10:00:00', 'open'),
(4, CURRENT_DATE + INTERVAL '20 days', 6, 6, 3000, 'Dubai Autodrome', '10:00:00', 'open'),
(5, CURRENT_DATE + INTERVAL '5 days', 30, 5, 250, 'Sheikh Zayed Mosque', '08:00:00', 'open'),
(6, CURRENT_DATE + INTERVAL '4 days', 20, 14, 500, 'JBR Beach', '08:00:00', 'open'),
(7, CURRENT_DATE + INTERVAL '19 days', 25, 10, 200, 'Sharjah Blue Souk', '09:00:00', 'open'),
(8, CURRENT_DATE + INTERVAL '24 days', 5, 2, 2400, 'Dubai Marina Helipad', '11:00:00', 'open'),
(9, CURRENT_DATE + INTERVAL '23 days', 15, 5, 400, 'Jebel Jais Base', '06:00:00', 'open'),
(10, CURRENT_DATE + INTERVAL '2 days', 20, 12, 500, 'Spa & Wellness Center', '10:00:00', 'open');

-- Таблица promo_codes
INSERT INTO promo_codes (code, description, discount_type, discount_value, max_uses, valid_from, valid_until, is_active) VALUES
('WELCOME2025', 'Welcome discount for new customers', 'percentage', 10, 100, CURRENT_DATE, CURRENT_DATE + INTERVAL '90 days', TRUE),
('VIP15', 'VIP customer discount', 'percentage', 15, 50, CURRENT_DATE, CURRENT_DATE + INTERVAL '180 days', TRUE),
('GROUP20', 'Group booking discount', 'percentage', 20, 30, CURRENT_DATE, CURRENT_DATE + INTERVAL '180 days', TRUE),
('EARLYBIRD', 'Early bird special', 'percentage', 25, 20, CURRENT_DATE, CURRENT_DATE + INTERVAL '60 days', TRUE),
('FLAT500', 'Fixed AED 500 discount', 'fixed', 500, 40, CURRENT_DATE, CURRENT_DATE + INTERVAL '90 days', TRUE),
('CORPORATE30', 'Corporate partnerships discount', 'percentage', 30, 15, CURRENT_DATE, CURRENT_DATE + INTERVAL '365 days', TRUE);

-- Таблица booking_sources
INSERT INTO booking_sources (booking_id, source_country, referrer_type, referrer_name) VALUES
(1, 'UAE', 'direct', 'Al-Fardan Exchange'),
(2, 'UAE', 'agency', 'Emirates Travel Agency'),
(3, 'Russia', 'online', 'Google Search'),
(4, 'UAE', 'recommendation', 'Previous Customer'),
(5, 'UAE', 'direct', 'ADIB'),
(6, 'UAE', 'direct', 'Rotana Hotels'),
(7, 'UAE', 'agency', 'Spinneys Corporate Travel'),
(8, 'Kazakhstan', 'online', 'Facebook Ad'),
(9, 'Russia', 'recommendation', 'Referral Partner'),
(10, 'UAE', 'direct', 'Damas Jewellery');
