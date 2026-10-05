CREATE INDEX idx_page_views_date ON page_views(view_date DESC);
CREATE INDEX idx_user_sessions_visitor ON user_sessions(visitor_id);
CREATE INDEX idx_sales_metrics_date ON sales_metrics(metric_date DESC);
CREATE INDEX idx_marketing_campaigns_channel ON marketing_campaigns(channel);
CREATE INDEX idx_kpi_targets_month ON kpi_targets(target_month, target_year);
