CREATE INDEX idx_notifications_status ON notifications(status) WHERE status IN ('pending', 'failed');
CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_sms_queue_status ON sms_queue(status);
CREATE INDEX idx_email_queue_created ON email_queue(created_at DESC);
CREATE INDEX idx_notification_templates_name ON notification_templates(template_name);
