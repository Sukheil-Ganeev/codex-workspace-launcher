-- 01-CRM System Typical Queries

-- 1. Поиск активных контактов по стране с их компаниями
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    c.mobile,
    c.position,
    comp.name AS company_name,
    comp.industry,
    COUNT(DISTINCT ch.id) AS interaction_count
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
LEFT JOIN contact_history ch ON c.id = ch.contact_id
WHERE c.is_active = TRUE
    AND c.country = 'UAE'
GROUP BY c.id, c.first_name, c.last_name, c.email, c.mobile, c.position, comp.name, comp.industry
ORDER BY interaction_count DESC
LIMIT 20;

-- 2. Найти VIP клиентов с их сегментацией и лайфтайм стоимостью
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    comp.name AS company_name,
    cs.name AS segment,
    cc.priority,
    cc.lifetime_value,
    cc.classification_date
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
LEFT JOIN contact_classifications cc ON c.id = cc.contact_id
LEFT JOIN customer_segments cs ON cc.segment_id = cs.id
WHERE cc.priority IN ('hot', 'vip')
    AND c.is_active = TRUE
ORDER BY cc.lifetime_value DESC;

-- 3. Получить контакты, требующие следующего контакта (follow-up)
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    c.mobile,
    ch.next_follow_up,
    ch.interaction_type,
    ch.notes,
    DATEDIFF(day, CURRENT_DATE, ch.next_follow_up) AS days_until_followup
FROM contacts c
INNER JOIN contact_history ch ON c.id = ch.contact_id
WHERE ch.next_follow_up IS NOT NULL
    AND ch.next_follow_up <= CURRENT_DATE + INTERVAL '7 days'
    AND ch.next_follow_up >= CURRENT_DATE
    AND c.is_active = TRUE
ORDER BY ch.next_follow_up ASC;

-- 4. Контакты по сегментам с количеством задач
SELECT
    cs.name AS segment,
    COUNT(DISTINCT c.id) AS contact_count,
    COUNT(DISTINCT t.id) AS task_count,
    AVG(cc.lifetime_value) AS avg_lifetime_value
FROM customer_segments cs
LEFT JOIN contact_classifications cc ON cs.id = cc.segment_id
LEFT JOIN contacts c ON cc.contact_id = c.id
LEFT JOIN tasks t ON c.id = t.contact_id AND t.status != 'completed'
GROUP BY cs.id, cs.name
ORDER BY contact_count DESC;

-- 5. Контакты с наиболее частыми взаимодействиями
SELECT
    c.id,
    c.first_name,
    c.last_name,
    comp.name AS company_name,
    COUNT(ch.id) AS total_interactions,
    MAX(ch.created_at) AS last_interaction,
    STRING_AGG(DISTINCT ch.interaction_type, ', ') AS interaction_types
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
LEFT JOIN contact_history ch ON c.id = ch.contact_id
WHERE c.is_active = TRUE
GROUP BY c.id, c.first_name, c.last_name, comp.name
HAVING COUNT(ch.id) > 0
ORDER BY total_interactions DESC
LIMIT 15;

-- 6. Открытые задачи с приоритетом
SELECT
    t.id,
    c.first_name,
    c.last_name,
    c.email,
    t.title,
    t.priority,
    t.due_date,
    t.assigned_to,
    DATEDIFF(day, CURRENT_DATE, t.due_date) AS days_until_due
FROM tasks t
INNER JOIN contacts c ON t.contact_id = c.id
WHERE t.status IN ('open', 'in-progress')
    AND t.due_date <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY t.priority DESC, t.due_date ASC;

-- 7. Контакты с документами и сроками истечения
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    d.title AS document_title,
    d.document_type,
    d.expiration_date,
    DATEDIFF(day, CURRENT_DATE, d.expiration_date) AS days_until_expiration
FROM contacts c
INNER JOIN documents d ON c.id = d.contact_id
WHERE d.expiration_date IS NOT NULL
    AND d.expiration_date <= CURRENT_DATE + INTERVAL '90 days'
ORDER BY d.expiration_date ASC;

-- 8. Анализ эффективности контактов по источникам
SELECT
    cs.name AS source,
    cs.category,
    COUNT(DISTINCT c.id) AS contacts_count,
    COUNT(DISTINCT ch.id) AS interactions,
    AVG(cc.lifetime_value) AS avg_lifetime_value,
    COUNT(DISTINCT CASE WHEN cc.priority IN ('hot', 'vip') THEN c.id END) AS high_value_contacts
FROM contact_sources cs
LEFT JOIN contact_history ch ON cs.id = ch.source_id
LEFT JOIN contacts c ON ch.contact_id = c.id
LEFT JOIN contact_classifications cc ON c.id = cc.contact_id
GROUP BY cs.id, cs.name, cs.category
ORDER BY contacts_count DESC;

-- 9. Рассылки: активные подписчики по спискам
SELECT
    ml.name AS mailing_list,
    ml.purpose,
    COUNT(DISTINCT mls.contact_id) AS active_subscribers,
    COUNT(DISTINCT CASE WHEN mls.unsubscribed_at IS NOT NULL THEN mls.contact_id END) AS unsubscribed
FROM mailing_lists ml
LEFT JOIN mailing_list_subscriptions mls ON ml.id = mls.mailing_list_id
GROUP BY ml.id, ml.name, ml.purpose
ORDER BY active_subscribers DESC;

-- 10. Поиск контактов по тегам
SELECT
    ct.name AS tag,
    COUNT(DISTINCT c.id) AS contact_count,
    STRING_AGG(DISTINCT c.first_name || ' ' || c.last_name, ', ') AS contacts
FROM contact_tags ct
LEFT JOIN contact_tag_assignments cta ON ct.id = cta.tag_id
LEFT JOIN contacts c ON cta.contact_id = c.id
GROUP BY ct.id, ct.name
ORDER BY contact_count DESC;

-- 11. Контакты, не имеющие взаимодействий в последние 6 месяцев
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    c.mobile,
    comp.name AS company_name,
    c.updated_at AS last_updated,
    MAX(ch.created_at) AS last_interaction
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
LEFT JOIN contact_history ch ON c.id = ch.contact_id
WHERE c.is_active = TRUE
GROUP BY c.id, c.first_name, c.last_name, c.email, c.mobile, comp.name, c.updated_at
HAVING MAX(ch.created_at) < CURRENT_DATE - INTERVAL '180 days'
    OR MAX(ch.created_at) IS NULL
ORDER BY c.updated_at DESC;

-- 12. Предпочтения контактов по языкам и каналам
SELECT
    cp.language_preference,
    COUNT(DISTINCT cp.contact_id) AS contact_count,
    SUM(CASE WHEN cp.prefers_email = TRUE THEN 1 ELSE 0 END) AS prefers_email,
    SUM(CASE WHEN cp.prefers_phone = TRUE THEN 1 ELSE 0 END) AS prefers_phone,
    SUM(CASE WHEN cp.prefers_sms = TRUE THEN 1 ELSE 0 END) AS prefers_sms,
    SUM(CASE WHEN cp.prefers_whatsapp = TRUE THEN 1 ELSE 0 END) AS prefers_whatsapp
FROM communication_preferences cp
GROUP BY cp.language_preference
ORDER BY contact_count DESC;

-- 13. Полный профиль контакта (для CRM dashboard)
SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.email,
    c.phone,
    c.mobile,
    c.position,
    comp.name AS company_name,
    comp.industry,
    comp.country,
    cs.name AS segment,
    cc.priority,
    cc.lifetime_value,
    COUNT(DISTINCT ch.id) AS total_interactions,
    MAX(ch.created_at) AS last_contact_date,
    COUNT(DISTINCT t.id) AS open_tasks,
    STRING_AGG(DISTINCT ct.name, ', ') AS tags
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
LEFT JOIN contact_classifications cc ON c.id = cc.contact_id
LEFT JOIN customer_segments cs ON cc.segment_id = cs.id
LEFT JOIN contact_history ch ON c.id = ch.contact_id
LEFT JOIN tasks t ON c.id = t.contact_id AND t.status != 'completed'
LEFT JOIN contact_tag_assignments cta ON c.id = cta.contact_id
LEFT JOIN contact_tags ct ON cta.tag_id = ct.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.first_name, c.last_name, c.email, c.phone, c.mobile, c.position,
         comp.name, comp.industry, comp.country, cs.name, cc.priority, cc.lifetime_value;

-- 14. Компании с наивысшей активностью
SELECT
    comp.id,
    comp.name,
    comp.industry,
    COUNT(DISTINCT c.id) AS contact_count,
    COUNT(DISTINCT ch.id) AS interaction_count,
    AVG(cc.lifetime_value) AS avg_contact_value,
    SUM(cc.lifetime_value) AS total_company_value,
    MAX(ch.created_at) AS last_interaction
FROM companies comp
LEFT JOIN contacts c ON comp.id = c.company_id AND c.is_active = TRUE
LEFT JOIN contact_history ch ON c.id = ch.contact_id
LEFT JOIN contact_classifications cc ON c.id = cc.contact_id
GROUP BY comp.id, comp.name, comp.industry
HAVING COUNT(DISTINCT c.id) > 0
ORDER BY total_company_value DESC NULLS LAST
LIMIT 20;

-- 15. Статус выполнения задач по сотрудникам
SELECT
    assigned_to,
    COUNT(DISTINCT CASE WHEN status = 'open' THEN id END) AS open_tasks,
    COUNT(DISTINCT CASE WHEN status = 'in-progress' THEN id END) AS in_progress_tasks,
    COUNT(DISTINCT CASE WHEN status = 'completed' THEN id END) AS completed_tasks,
    COUNT(DISTINCT CASE WHEN status = 'cancelled' THEN id END) AS cancelled_tasks,
    COUNT(*) AS total_tasks
FROM tasks
WHERE due_date <= CURRENT_DATE + INTERVAL '30 days'
GROUP BY assigned_to
ORDER BY total_tasks DESC;
