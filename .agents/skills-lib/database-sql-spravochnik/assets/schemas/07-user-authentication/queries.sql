SELECT email, role, status FROM users WHERE status = 'active';
SELECT u.email, COUNT(up.permission_name) as permission_count FROM users u LEFT JOIN user_permissions up ON u.id = up.user_id GROUP BY u.id;
SELECT email, attempt_time, success FROM login_attempts WHERE email LIKE '%tourism.ae' ORDER BY attempt_time DESC LIMIT 20;
