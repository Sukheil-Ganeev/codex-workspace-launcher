SELECT user_email, action_type, table_name, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 100;
SELECT event_type, event_name, severity, created_at FROM system_events ORDER BY created_at DESC LIMIT 50;
SELECT entity_type, field_name, old_value, new_value, changed_by FROM change_history WHERE changed_at > CURRENT_DATE - INTERVAL '7 days';
