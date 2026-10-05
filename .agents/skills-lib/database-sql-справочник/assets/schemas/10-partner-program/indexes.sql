CREATE INDEX idx_partners_status ON partners(status);
CREATE INDEX idx_partner_commissions_partner_id ON partner_commissions(partner_id);
CREATE INDEX idx_partner_commissions_payment_status ON partner_commissions(payment_status);
CREATE INDEX idx_partner_promotions_partner_id ON partner_promotions(partner_id);
CREATE INDEX idx_partner_performance_partner_id ON partner_performance(partner_id, report_month);
