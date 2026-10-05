-- Низкий уровень запасов
SELECT name, quantity_on_hand, reorder_level FROM inventory_items
WHERE quantity_on_hand <= reorder_level AND is_active = TRUE;

-- Истории движения запасов
SELECT i.name, sm.movement_type, sm.quantity, sm.notes, sm.created_by, sm.created_at
FROM stock_movements sm
JOIN inventory_items i ON sm.item_id = i.id
ORDER BY sm.created_at DESC LIMIT 50;

-- Техническое обслуживание, требующее внимания
SELECT 'Yacht' as type, maintenance_date, next_due_date, cost, status
FROM yacht_maintenance
WHERE status != 'completed' AND next_due_date <= CURRENT_DATE + INTERVAL '30 days'
UNION
SELECT 'Vehicle' as type, maintenance_date, next_due_date, cost, status
FROM vehicle_maintenance
WHERE status != 'completed' AND next_due_date <= CURRENT_DATE + INTERVAL '30 days';

-- Истекающие полисы страховки
SELECT policy_number, provider, coverage_amount, policy_expiry_date FROM insurance_policies
WHERE policy_expiry_date <= CURRENT_DATE + INTERVAL '90 days' AND is_active = TRUE;

-- Истекающие лицензии
SELECT person_name, license_type, license_number, expiry_date FROM licenses_and_certifications
WHERE expiry_date <= CURRENT_DATE + INTERVAL '30 days';

-- Значение активов (расчетное)
SELECT asset_type, COUNT(*) as count, SUM(current_book_value) as total_value
FROM asset_depreciation
GROUP BY asset_type;
