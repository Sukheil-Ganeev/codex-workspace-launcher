INSERT INTO sales_metrics (metric_date, total_bookings, total_revenue, avg_booking_value) VALUES
(CURRENT_DATE - 1, 15, 75000, 5000),
(CURRENT_DATE - 2, 18, 92000, 5111),
(CURRENT_DATE - 3, 12, 61000, 5083);

INSERT INTO marketing_campaigns (campaign_name, channel, start_date, end_date, budget, spent, impressions, clicks, conversions) VALUES
('Desert Safari Promo', 'social', CURRENT_DATE - 30, CURRENT_DATE, 50000, 45000, 500000, 5000, 150),
('Google Ads - Dubai Tours', 'google', CURRENT_DATE - 20, CURRENT_DATE, 30000, 28000, 300000, 3000, 120);

INSERT INTO kpi_targets (kpi_name, target_value, actual_value, target_month, target_year, status) VALUES
('Monthly Revenue Target', 500000, 425000, 2, 2026, 'in_progress'),
('Booking Conversion Rate', 5, 4.5, 2, 2026, 'in_progress');
