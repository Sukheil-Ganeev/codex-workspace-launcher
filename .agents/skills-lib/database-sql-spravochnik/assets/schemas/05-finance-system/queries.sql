SELECT 'Financial Summary' as report;
SELECT SUM(amount) as total_invoiced FROM invoices WHERE status = 'paid';
SELECT SUM(amount) as total_expenses FROM expenses WHERE EXTRACT(MONTH FROM expense_date) = EXTRACT(MONTH FROM CURRENT_DATE);
SELECT stream_name, monthly_target, ytd_revenue FROM revenue_streams ORDER BY ytd_revenue DESC;
