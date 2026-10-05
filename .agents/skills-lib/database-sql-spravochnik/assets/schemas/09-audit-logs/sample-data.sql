INSERT INTO audit_logs (user_email, action_type, table_name, record_id) VALUES
('suhail@tourism.ae', 'INSERT', 'bookings', 1),
('suhail@tourism.ae', 'UPDATE', 'bookings', 1),
('assistant@tourism.ae', 'VIEW', 'contacts', 5);

INSERT INTO system_events (event_type, event_name, severity) VALUES
('database', 'Backup completed', 'info'),
('security', 'Multiple failed login attempts', 'warning'),
('payment', 'Payment processing error', 'critical');

INSERT INTO compliance_records (record_type, subject, regulatory_requirement) VALUES
('data_privacy', 'GDPR Compliance', 'EU Data Protection'),
('financial', 'Annual Tax Filing', 'UAE Tax Compliance');
