SELECT metric_date, total_bookings, total_revenue FROM sales_metrics ORDER BY metric_date DESC LIMIT 30;
SELECT campaign_name, channel, spent, conversions, ROUND(100.0 * conversions / clicks, 2) as conversion_rate FROM marketing_campaigns;
SELECT kpi_name, target_value, actual_value, ROUND(100.0 * actual_value / target_value, 2) as percent_achieved FROM kpi_targets WHERE target_month = EXTRACT(MONTH FROM CURRENT_DATE);
