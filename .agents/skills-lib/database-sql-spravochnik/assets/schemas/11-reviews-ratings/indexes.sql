CREATE INDEX idx_reviews_reviewable ON reviews(reviewable_type, reviewable_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_verified ON reviews(is_verified) WHERE is_verified = TRUE;
CREATE INDEX idx_reviews_date ON reviews(review_date DESC);
CREATE INDEX idx_detailed_ratings_review_id ON detailed_ratings(review_id);
CREATE INDEX idx_rating_criteria_type ON rating_criteria(reviewable_type);
