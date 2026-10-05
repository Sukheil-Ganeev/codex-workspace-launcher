INSERT INTO rating_criteria (reviewable_type, criteria_name) VALUES
('tour', 'Guide Knowledge'),
('tour', 'Safety & Comfort'),
('tour', 'Value for Money'),
('yacht', 'Service Quality'),
('yacht', 'Cleanliness');

INSERT INTO reviews (reviewable_type, reviewable_id, reviewer_id, rating, title, comment, is_verified, status) VALUES
('tour', 1, 1, 5, 'Amazing experience!', 'Best desert safari I have experienced. Highly recommended!', TRUE, 'published'),
('tour', 2, 3, 4, 'Great tour with minor issues', 'Good experience but timing could be better', TRUE, 'published'),
('yacht', 1, 5, 5, 'Luxurious yacht experience', 'Excellent service and beautiful sunset view', TRUE, 'published');

INSERT INTO review_responses (review_id, responder_name, response_text) VALUES
(1, 'Suhail Manager', 'Thank you for your wonderful feedback! We appreciate it.'),
(2, 'Suhail Manager', 'We appreciate your feedback and will improve our timing.');
