INSERT INTO partners (partner_name, partner_type, contact_person, email, commission_rate, status, onboarded_date) VALUES
('Emirates Travel Agency', 'travel_agency', 'Ahmed Al-Dhaheri', 'ahmed@emiratestravel.ae', 15, 'active', '2024-06-01'),
('Luxury Tours Dubai', 'tour_operator', 'Fatima Al-Mansouri', 'info@luxurytours.ae', 20, 'active', '2024-03-15'),
('Online Booking Hub', 'online_platform', 'John Smith', 'support@bookshub.com', 10, 'active', '2024-01-01');

INSERT INTO partner_commissions (partner_id, booking_id, commission_amount, commission_percentage, payment_status) VALUES
(1, 1, 1080, 15, 'paid'),
(2, 3, 2850, 20, 'pending'),
(3, 5, 562.5, 10, 'paid');

INSERT INTO partner_promotions (partner_id, promotion_name, promo_code, discount_percent, valid_from, valid_until, is_active) VALUES
(1, 'Special Summer Offer', 'SUMMER25', 15, '2026-06-01', '2026-08-31', TRUE),
(2, 'VIP Referral Bonus', 'VIP-REF-20', 20, '2026-01-01', '2026-12-31', TRUE);
