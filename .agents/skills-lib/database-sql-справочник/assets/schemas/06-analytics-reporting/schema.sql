-- 06-Analytics & Reporting Schema
CREATE TABLE page_views (id SERIAL PRIMARY KEY, page_url VARCHAR(500), visitor_id VARCHAR(100), session_id VARCHAR(100), view_date TIMESTAMPTZ);
CREATE TABLE user_sessions (id SERIAL PRIMARY KEY, session_id VARCHAR(100) UNIQUE, visitor_id VARCHAR(100), start_time TIMESTAMPTZ, end_time TIMESTAMPTZ, duration_seconds INTEGER, pages_visited INTEGER, conversion BOOLEAN);
CREATE TABLE sales_metrics (id SERIAL PRIMARY KEY, metric_date DATE, total_bookings INTEGER, total_revenue NUMERIC(15,2), avg_booking_value NUMERIC(10,2), conversion_rate NUMERIC(5,2));
CREATE TABLE customer_cohorts (id SERIAL PRIMARY KEY, cohort_date DATE, cohort_size INTEGER, retention_day_1 NUMERIC(5,2), retention_day_7 NUMERIC(5,2), retention_day_30 NUMERIC(5,2));
CREATE TABLE marketing_campaigns (id SERIAL PRIMARY KEY, campaign_name VARCHAR(255), channel VARCHAR(100), start_date DATE, end_date DATE, budget NUMERIC(12,2), spent NUMERIC(12,2), impressions INTEGER, clicks INTEGER, conversions INTEGER);
CREATE TABLE kpi_targets (id SERIAL PRIMARY KEY, kpi_name VARCHAR(255), target_value NUMERIC(15,2), actual_value NUMERIC(15,2), target_month INTEGER, target_year INTEGER, status VARCHAR(50));
