SELECT reviewable_type, AVG(rating) as avg_rating, COUNT(*) as total_reviews FROM reviews WHERE is_verified = TRUE GROUP BY reviewable_type;
SELECT * FROM reviews WHERE status = 'pending' ORDER BY review_date DESC;
SELECT r.title, r.comment, COUNT(rr.id) as response_count FROM reviews r LEFT JOIN review_responses rr ON r.id = rr.review_id GROUP BY r.id ORDER BY r.review_date DESC;
