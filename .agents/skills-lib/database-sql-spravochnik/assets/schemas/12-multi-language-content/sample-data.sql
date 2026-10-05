INSERT INTO languages (language_code, language_name, is_active) VALUES
('en', 'English', TRUE),
('ru', 'Russian', TRUE),
('ar', 'Arabic', TRUE),
('kk', 'Kazakh', TRUE);

INSERT INTO translation_keys (key_name, english_text) VALUES
('welcome_message', 'Welcome to our tourism service'),
('book_now', 'Book Now'),
('price', 'Price'),
('availability', 'Availability');

INSERT INTO content_translations (content_type, content_id, language_code, title, slug) VALUES
('tour', 1, 'en', 'Desert Safari Plus', 'desert-safari-plus'),
('tour', 1, 'ru', 'Сафари в пустыне плюс', 'safari-v-pustyne-plus'),
('tour', 1, 'ar', 'سفاري الصحراء بلاس', 'safari-al-sahara-blur');

INSERT INTO seo_translations (entity_type, entity_id, language_code, meta_title, meta_description) VALUES
('tour', 1, 'en', 'Desert Safari Plus Dubai | Best Adventure Tour', 'Experience the best desert safari in Dubai...'),
('tour', 1, 'ru', 'Сафари в пустыне Дубай | Лучшие приключения', 'Испытайте лучшее сафари в пустыне...');
