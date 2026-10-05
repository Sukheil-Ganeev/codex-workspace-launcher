SELECT notification_type, status, COUNT(*) as count FROM notifications GROUP BY notification_type, status;
SELECT COUNT(*) as pending_emails FROM email_queue WHERE status = 'pending' AND retry_count < 3;
SELECT notification_type, delivery_status, COUNT(*) FROM notification_log GROUP BY notification_type, delivery_status;
