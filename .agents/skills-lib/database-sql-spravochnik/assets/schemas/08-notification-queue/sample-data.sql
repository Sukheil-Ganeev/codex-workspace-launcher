INSERT INTO notification_templates (template_name, template_type, subject_template, body_template) VALUES
('booking_confirmation', 'email', 'Booking Confirmation #{booking_code}', 'Dear {client_name}, your booking has been confirmed...'),
('payment_reminder', 'email', 'Payment Reminder for {tour_name}', 'Please complete payment for your booking...'),
('cancellation_notice', 'sms', 'Cancellation Notice', 'Your booking has been cancelled. Refund: {amount}');

INSERT INTO notifications (recipient_email, notification_type, subject, message, status) VALUES
('client@example.com', 'booking_confirmation', 'Booking Confirmed', 'Your desert safari tour is confirmed', 'sent'),
('client2@example.com', 'payment_reminder', 'Payment Reminder', 'Please complete payment', 'pending');
