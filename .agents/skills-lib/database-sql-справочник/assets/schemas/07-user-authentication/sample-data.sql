INSERT INTO users (email, phone, first_name, last_name, role, status) VALUES
('suhail@tourism.ae', '+971501234567', 'Suhail', 'Manager', 'admin', 'active'),
('assistant@tourism.ae', '+971502222222', 'Assistant', 'Staff', 'staff', 'active'),
('marcel@tourism.ae', '+971503333333', 'Marcel', 'Brother', 'admin', 'active');

INSERT INTO user_permissions (user_id, permission_name, resource_type) VALUES
(1, 'create_booking', 'bookings'),
(1, 'view_analytics', 'analytics'),
(2, 'create_booking', 'bookings'),
(3, 'manage_vehicles', 'vehicles');
