-- 03-Tour Catalog Indexes
CREATE INDEX idx_tours_category_id ON tours(category_id);
CREATE INDEX idx_tours_slug ON tours(slug);
CREATE INDEX idx_tours_is_active ON tours(is_active);
CREATE INDEX idx_tours_difficulty ON tours(difficulty_level);
CREATE INDEX idx_tour_images_tour_id ON tour_images(tour_id);
CREATE INDEX idx_tour_routes_tour_id ON tour_routes(tour_id);
CREATE INDEX idx_tour_schedules_tour_id ON tour_schedules(tour_id);
CREATE INDEX idx_tour_schedules_available_date ON tour_schedules(available_date);
CREATE INDEX idx_tour_pricing_tour_id ON tour_pricing(tour_id);
CREATE INDEX idx_tour_reviews_tour_id ON tour_reviews(tour_id);
CREATE INDEX idx_tour_reviews_rating ON tour_reviews(rating);
CREATE INDEX idx_tour_guides_is_active ON tour_guides(is_active);
CREATE INDEX idx_tour_vehicles_is_active ON tour_vehicles(is_active);
CREATE INDEX idx_tour_tag_assignments_tour_id ON tour_tag_assignments(tour_id);
CREATE INDEX idx_tour_categories_slug ON tour_categories(slug);
