SELECT partner_name, commission_rate, status FROM partners WHERE status = 'active' ORDER BY partner_name;
SELECT p.partner_name, SUM(pc.commission_amount) as total_commission FROM partners p LEFT JOIN partner_commissions pc ON p.id = pc.partner_id WHERE pc.payment_status = 'pending' GROUP BY p.id, p.partner_name;
SELECT pp.partner_name, SUM(pm.total_commission) as monthly_commission FROM partner_performance pm JOIN partners pp ON pm.partner_id = pp.id GROUP BY pp.id, pp.partner_name;
