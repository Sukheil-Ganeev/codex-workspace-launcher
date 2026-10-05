INSERT INTO currency_rates (from_currency, to_currency, rate) VALUES ('AED', 'USD', 0.272), ('AED', 'RUB', 27.5), ('AED', 'KZT', 127.8);

INSERT INTO invoices (invoice_number, booking_id, amount, currency, invoice_date, due_date, status) VALUES
('INV-2026-00001', 1, 7200, 'AED', CURRENT_DATE - 5, CURRENT_DATE + 25, 'paid'),
('INV-2026-00002', 2, 12500, 'AED', CURRENT_DATE - 3, CURRENT_DATE + 27, 'sent'),
('INV-2026-00003', 6, 8750, 'AED', CURRENT_DATE, CURRENT_DATE + 30, 'draft');

INSERT INTO revenue_streams (stream_name, revenue_type, monthly_target, currency, ytd_revenue) VALUES
('Desert Safari Tours', 'tours', 100000, 'AED', 450000),
('Yacht Cruises', 'yacht_rental', 150000, 'AED', 620000),
('Car Rentals', 'car_rental', 80000, 'AED', 320000);

INSERT INTO expenses (expense_type, amount, currency, expense_date, category) VALUES
('Fuel', 5000, 'AED', CURRENT_DATE - 1, 'Operations'),
('Staff Salary', 50000, 'AED', CURRENT_DATE - 15, 'Personnel'),
('Insurance', 15000, 'AED', CURRENT_DATE - 30, 'Administration');
