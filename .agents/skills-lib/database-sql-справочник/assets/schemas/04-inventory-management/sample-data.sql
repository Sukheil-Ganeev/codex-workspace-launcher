INSERT INTO inventory_categories (name, description) VALUES
('Equipment', 'General equipment and supplies'),
('Safety Gear', 'Life jackets, helmets, safety equipment'),
('Spare Parts', 'Replacement parts for vehicles and yachts'),
('Beverages', 'Drinks for yacht cruises'),
('Catering', 'Food and meal supplies');

INSERT INTO inventory_items (category_id, name, sku, quantity_on_hand, reorder_level, unit_cost, unit_price) VALUES
(1, 'Snorkeling Set', 'SNORKEL-001', 25, 10, 50, 120),
(1, 'Life Jacket', 'LIFE-JACKET-001', 40, 20, 100, 250),
(2, 'Safety Helmet', 'HELMET-001', 15, 5, 80, 150),
(3, 'Engine Oil (Yacht)', 'OIL-YACHT-001', 50, 20, 25, 50),
(4, 'Bottled Water (500ml)', 'WATER-BOTTLE-001', 200, 100, 2, 5),
(4, 'Premium Whiskey', 'WHISKEY-PREMIUM-001', 30, 10, 400, 800);

INSERT INTO storage_locations (name, location_type, address, is_climate_controlled) VALUES
('Dubai Marina Warehouse', 'warehouse', 'Marina, Dubai', TRUE),
('Dune Camp Storage', 'warehouse', 'Desert Area, Dubai', FALSE),
('Dock - Pier 5', 'dock', 'Dubai Marina', FALSE),
('Vehicle Garage', 'garage', 'Al Quoz, Dubai', TRUE);

INSERT INTO insurance_policies (asset_type, asset_id, policy_number, provider, coverage_amount, premium, policy_start_date, policy_expiry_date) VALUES
('yacht', 1, 'YCH-2024-001', 'Gulf Insurance', 5000000, 150000, '2024-01-01', '2026-01-01'),
('vehicle', 1, 'VEH-2024-001', 'Emirates Insurance', 1000000, 25000, '2024-01-01', '2025-01-01'),
('general_liability', NULL, 'GEN-2024-001', 'Allianz', 2000000, 50000, '2024-01-01', '2025-01-01');

INSERT INTO licenses_and_certifications (person_id, person_name, license_type, license_number, issued_date, expiry_date) VALUES
(1, 'Ahmed Al-Mansoori', 'pilot', 'PILOT-DXB-001', '2021-01-01', '2026-01-01'),
(2, 'Elena Volkova', 'maritime', 'MARITIME-001', '2022-06-01', '2027-06-01'),
(3, 'Mohammed Al-Suwaidi', 'diving', 'DIVING-DXB-001', '2020-03-01', '2025-03-01');
