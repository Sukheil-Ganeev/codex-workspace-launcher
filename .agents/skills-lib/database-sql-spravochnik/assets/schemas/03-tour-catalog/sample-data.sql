-- 03-Tour Catalog Sample Data

INSERT INTO tour_categories (name, slug, description, display_order) VALUES
('City Tours', 'city-tours', 'Guided tours of major cities in UAE', 1),
('Desert & Dunes', 'desert-dunes', 'Desert safari and outdoor adventures', 2),
('Water Activities', 'water-activities', 'Yacht cruises and water sports', 3),
('Adventure', 'adventure', 'Extreme sports and adventure activities', 4),
('Cultural', 'cultural', 'Traditional and cultural experiences', 5),
('Wellness', 'wellness', 'Spa and relaxation packages', 6);

INSERT INTO tours (name, slug, category_id, description, duration_hours, difficulty_level, min_participants, max_participants, price_per_person, languages) VALUES
('Dubai City Tour', 'dubai-city-tour', 1, 'Explore iconic landmarks of Dubai', 4, 'easy', 1, 30, 200, ARRAY['English', 'Russian', 'Arabic']),
('Desert Safari Plus', 'desert-safari-plus', 2, 'Dune bashing with Arabic dinner and entertainment', 6, 'moderate', 2, 40, 250, ARRAY['English', 'Russian']),
('Luxury Yacht Cruise', 'luxury-yacht-cruise', 3, 'Premium yacht experience with drinks and sunset', 3, 'easy', 4, 50, 500, ARRAY['English', 'Russian', 'Arabic']),
('Abu Dhabi Day Trip', 'abu-dhabi-day-trip', 1, 'Sheikh Zayed Mosque and Louvre Abu Dhabi', 8, 'easy', 2, 35, 250, ARRAY['English', 'Russian', 'Arabic']),
('Jebel Jais Mountain Hike', 'jebel-jais-hike', 4, 'Mountain climbing and hiking experience', 6, 'hard', 2, 15, 350, ARRAY['English', 'Russian']),
('Snorkeling Adventure', 'snorkeling-adventure', 3, 'Coral reef exploration and underwater experience', 4, 'moderate', 4, 25, 300, ARRAY['English', 'Russian', 'Arabic']),
('Sharjah Cultural Tour', 'sharjah-culture-tour', 5, 'Traditional souks, museums, and cultural sites', 5, 'easy', 2, 25, 180, ARRAY['English', 'Russian', 'Arabic']),
('Spa Wellness Day', 'spa-wellness-day', 6, 'Full day spa and relaxation treatment', 8, 'easy', 1, 20, 400, ARRAY['English', 'Russian']),
('Helicopter City Tour', 'helicopter-city-tour', 1, 'Aerial view of Dubai from helicopter', 45, 'easy', 1, 5, 2400, ARRAY['English', 'Russian', 'Arabic']),
('Ferrari Driving Experience', 'ferrari-driving', 4, 'Drive a Ferrari supercar on professional track', 3, 'extreme', 1, 6, 3000, ARRAY['English', 'Russian']);

INSERT INTO tour_guides (first_name, last_name, email, phone, languages, license_number, experience_years, rating) VALUES
('Ahmed', 'Al-Mansoori', 'ahmed.guide@tourism.ae', '+971501111111', ARRAY['Arabic', 'English', 'Russian'], 'DXB-GUIDE-001', 12, 4.8),
('Elena', 'Volkova', 'elena.guide@tourism.ae', '+971502222222', ARRAY['Russian', 'English'], 'DXB-GUIDE-002', 8, 4.7),
('Mohammed', 'Al-Suwaidi', 'mohammed.guide@tourism.ae', '+971503333333', ARRAY['Arabic', 'English'], 'DXB-GUIDE-003', 10, 4.9),
('Natasha', 'Petrova', 'natasha.guide@tourism.ae', '+971504444444', ARRAY['Russian', 'English', 'Arabic'], 'DXB-GUIDE-004', 6, 4.6),
('Rashid', 'Al-Khayat', 'rashid.guide@tourism.ae', '+971505555555', ARRAY['Arabic', 'English'], 'DXB-GUIDE-005', 9, 4.8);

INSERT INTO tour_vehicles (registration_number, vehicle_type, model, year, capacity) VALUES
('UAE-YACHT-001', 'yacht', 'Sunseeker 95', 2020, 50),
('UAE-YACHT-002', 'yacht', 'Azimut 75', 2019, 40),
('UAE-JEEP-001', 'jeep', 'Land Rover Defender', 2021, 7),
('UAE-JEEP-002', 'jeep', 'Toyota 4Runner', 2021, 8),
('UAE-BUS-001', 'minibus', 'Mercedes Sprinter', 2020, 30),
('UAE-BUS-002', 'minibus', 'Coaster Bus', 2019, 35),
('UAE-HELI-001', 'helicopter', 'Airbus H135', 2022, 5);

INSERT INTO tour_tags (name, color) VALUES
('Popular', '#FF0000'),
('New', '#00FF00'),
('VIP', '#FFD700'),
('Family', '#0000FF'),
('Adventure', '#FF6600'),
('Luxury', '#9370DB');

INSERT INTO tour_images (tour_id, image_url, caption, display_order, is_featured) VALUES
(1, 'https://example.com/dubai-tour-1.jpg', 'Dubai skyline from Burj Khalifa', 1, TRUE),
(1, 'https://example.com/dubai-tour-2.jpg', 'Palm Jumeirah aerial view', 2, FALSE),
(2, 'https://example.com/desert-safari-1.jpg', 'Desert dunes at sunset', 1, TRUE),
(2, 'https://example.com/desert-safari-2.jpg', 'Traditional Arabic dinner', 2, FALSE),
(3, 'https://example.com/yacht-1.jpg', 'Luxury yacht in marina', 1, TRUE),
(3, 'https://example.com/yacht-2.jpg', 'Sunset on yacht deck', 2, FALSE);

INSERT INTO tour_routes (tour_id, stop_order, location_name, latitude, longitude, description, duration_minutes, stop_type) VALUES
(1, 1, 'Burj Khalifa', 25.1972, 55.2744, 'World tallest building', 60, 'activity'),
(1, 2, 'Dubai Mall', 25.1946, 55.2739, 'Largest shopping mall', 90, 'activity'),
(1, 3, 'Palm Jumeirah', 25.1409, 55.1469, 'Artificial palm-shaped island', 45, 'photo'),
(2, 1, 'Desert Camp', 25.0630, 55.5390, 'Starting point for dunes', 15, 'pickup'),
(2, 2, 'Dune Bashing Area', 25.0650, 55.5450, 'Main dune bashing experience', 120, 'activity'),
(2, 3, 'Traditional Camp', 25.0700, 55.5500, 'Arabic dinner and entertainment', 90, 'meal');

INSERT INTO tour_pricing (tour_id, price_type, min_quantity, max_quantity, price, season) VALUES
(1, 'per_person', 1, 10, 200, 'low'),
(1, 'per_person', 11, 30, 180, 'low'),
(2, 'per_person', 2, 10, 250, 'low'),
(2, 'per_person', 11, 40, 230, 'low'),
(3, 'per_person', 4, 20, 500, 'peak'),
(3, 'per_person', 21, 50, 450, 'peak');

INSERT INTO tour_faqs (tour_id, question, answer, display_order) VALUES
(1, 'What is the best time to visit Dubai?', 'October to April when weather is cool', 1),
(1, 'Do I need to book in advance?', 'Yes, we recommend booking at least 1 week before', 2),
(2, 'What should I bring for desert safari?', 'Sunscreen, camera, comfortable clothes, and money for tips', 3),
(3, 'Is the yacht cruise safe?', 'Yes, all our yachts are fully insured and equipped with safety equipment', 1);

INSERT INTO tour_reviews (tour_id, contact_id, rating, title, comment, date_visited, is_verified) VALUES
(1, 1, 5, 'Amazing Dubai experience', 'The tour was well-organized and the guide was very knowledgeable', CURRENT_DATE - INTERVAL '10 days', TRUE),
(1, 3, 5, 'Highly recommended', 'Great views and professional service throughout the day', CURRENT_DATE - INTERVAL '15 days', TRUE),
(2, 5, 4, 'Great desert adventure', 'Exciting dune bashing and delicious Arabic dinner', CURRENT_DATE - INTERVAL '5 days', TRUE),
(3, 7, 5, 'Unforgettable yacht experience', 'Beautiful sunset, comfortable yacht, and excellent service', CURRENT_DATE - INTERVAL '3 days', TRUE);
