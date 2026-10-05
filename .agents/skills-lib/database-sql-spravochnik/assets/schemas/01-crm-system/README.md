# 01-CRM System Schema

**Назначение:** Управление клиентами, контактами, компаниями, историей взаимодействия и коммуникационными предпочтениями для туристического бизнеса ОАЭ.

**Версия:** 1.0.0
**Статус:** Production-ready
**Язык БД:** PostgreSQL 14+

---

## Таблицы

### `companies`
Информация о компаниях-клиентах.

**Ключевые поля:**
- `id` - Primary Key
- `name` - Название компании (UNIQUE)
- `industry` - Отрасль (Finance, Hospitality, Retail, Energy)
- `country`, `city` - Местоположение
- `annual_revenue` - Годовой оборот (NUMERIC)
- `tax_id` - Налоговый ID (UNIQUE)
- `is_active` - Статус активности

**Индексы:**
- `idx_companies_country` - Поиск по стране (частичный)
- `idx_companies_email` - Поиск по email
- `idx_companies_active` - Фильтр активных

### `contacts`
Физические лица (представители компаний).

**Ключевые поля:**
- `id` - Primary Key
- `company_id` - Foreign Key (companies)
- `email` - Email адрес (UNIQUE, с валидацией)
- `phone`, `mobile` - Телефоны
- `position` - Должность
- `language` - Язык (English, Russian, Arabic)
- `is_active` - Статус активности

**Индексы:**
- `idx_contacts_company_id` - Поиск контактов компании
- `idx_contacts_email` - Поиск по email
- `idx_contacts_active` - Фильтр активных
- `idx_contacts_search` - Full-text поиск (GIN index)

### `contact_sources`
Источники появления контактов.

**Категории:** website, referral, event, social, advertising, cold-call

**Использование:** Отслеживание эффективности каналов привлечения.

### `contact_history`
История всех взаимодействий с контактом.

**Типы взаимодействий:** call, email, meeting, message, visit

**Ключевые поля:**
- `interaction_type` - Тип (call, email, meeting)
- `notes` - Текст заметок
- `duration_minutes` - Длительность (для звонков)
- `next_follow_up` - Дата следующего контакта
- `status` - completed, pending, cancelled

**Индексы:**
- `idx_contact_history_contact_id` - Все взаимодействия контакта
- `idx_contact_history_next_followup` - Предстоящие контакты
- `idx_contact_history_contact_date` - Составной индекс

### `customer_segments`
Сегменты классификации клиентов.

**Примеры:** Enterprise, Mid-Market, SMB, Startup, Government, VIP, Educational

### `contact_classifications`
Классификация контактов по сегментам и приоритетам.

**Приоритеты:** hot, warm, cold, vip

**Ключевые поля:**
- `priority` - Приоритет (hot, warm, cold, vip)
- `lifetime_value` - Ожидаемая стоимость клиента
- `classification_date` - Дата классификации

### `tasks`
Задачи и напоминания для сотрудников.

**Статусы:** open, in-progress, completed, cancelled

**Приоритеты:** low, medium, high, critical

**Ключевые поля:**
- `contact_id` - Связь с контактом
- `title` - Название задачи
- `due_date` - Срок выполнения
- `assigned_to` - Назначено сотруднику
- `completed_at` - Время завершения

### `documents`
Документы и файлы, связанные с контактами/компаниями.

**Типы:** contract, invoice, proposal, agreement

**Ключевые поля:**
- `file_path` - Путь к файлу
- `mime_type` - Тип файла
- `expiration_date` - Срок истечения

### `contact_tags`
Теги для гибкой классификации контактов.

**Примеры:** VIP, Recurring, New, Decision Maker, Budget Holder, Technical, Stakeholder, Inactive

### `communication_preferences`
Предпочтения по способам связи для каждого контакта.

**Ключевые поля:**
- `prefers_email`, `prefers_phone`, `prefers_sms`, `prefers_whatsapp`
- `do_not_call`, `do_not_email` - GDPR compliance
- `timezone` - Часовой пояс
- `language_preference` - Язык

### `mailing_lists`
Списки для рассылок и кампаний.

**Цели:** marketing, newsletter, announcements

### `mailing_list_subscriptions`
Подписки контактов на списки рассылок.

**Ключевые поля:**
- `is_active` - Статус подписки
- `unsubscribed_at` - Дата отписания (GDPR)

---

## Типичные Запросы

### 1. Найти активных контактов по стране с количеством взаимодействий
```sql
SELECT c.id, c.first_name, c.last_name, c.email,
       comp.name, COUNT(ch.id) as interactions
FROM contacts c
LEFT JOIN companies comp ON c.company_id = comp.id
LEFT JOIN contact_history ch ON c.id = ch.contact_id
WHERE c.is_active = TRUE AND c.country = 'UAE'
GROUP BY c.id, comp.name
ORDER BY interactions DESC;
```

### 2. VIP клиенты с лайфтайм стоимостью
```sql
SELECT c.first_name, c.last_name, comp.name, cc.priority,
       cc.lifetime_value
FROM contacts c
LEFT JOIN contact_classifications cc ON c.id = cc.contact_id
LEFT JOIN companies comp ON c.company_id = comp.id
WHERE cc.priority IN ('hot', 'vip') AND c.is_active = TRUE
ORDER BY cc.lifetime_value DESC;
```

### 3. Задачи, требующие follow-up
```sql
SELECT c.first_name, c.last_name, c.email,
       ch.next_follow_up,
       DATEDIFF(day, CURRENT_DATE, ch.next_follow_up) as days_left
FROM contacts c
INNER JOIN contact_history ch ON c.id = ch.contact_id
WHERE ch.next_follow_up BETWEEN CURRENT_DATE
      AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY ch.next_follow_up ASC;
```

### 4. Анализ эффективности источников
```sql
SELECT cs.name as source, cs.category,
       COUNT(DISTINCT c.id) as contacts,
       AVG(cc.lifetime_value) as avg_value
FROM contact_sources cs
LEFT JOIN contact_history ch ON cs.id = ch.source_id
LEFT JOIN contacts c ON ch.contact_id = c.id
LEFT JOIN contact_classifications cc ON c.id = cc.contact_id
GROUP BY cs.id, cs.name, cs.category
ORDER BY contacts DESC;
```

### 5. Контакты без взаимодействий последние 6 месяцев
```sql
SELECT c.id, c.first_name, c.last_name, c.email,
       MAX(ch.created_at) as last_interaction
FROM contacts c
LEFT JOIN contact_history ch ON c.id = ch.contact_id
GROUP BY c.id
HAVING MAX(ch.created_at) < CURRENT_DATE - INTERVAL '180 days'
   OR MAX(ch.created_at) IS NULL
ORDER BY c.updated_at DESC;
```

---

## Ограничения (Constraints)

### Foreign Keys
```sql
-- Каскадное удаление при удалении компании
ALTER TABLE contacts
  ADD CONSTRAINT fk_contacts_company
  FOREIGN KEY (company_id) REFERENCES companies(id)
  ON DELETE SET NULL ON UPDATE CASCADE;
```

### Check Constraints
```sql
-- Email валидация
CONSTRAINT check_email_format
  CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
```

### Unique Constraints
```sql
-- Email контакта должен быть уникален
UNIQUE(email)

-- Компания может иметь только одну запись коммуникационных предпочтений
UNIQUE(contact_id) in communication_preferences
```

---

## Оптимизация

### Производительность
1. **Частичные индексы** для активных контактов:
   ```sql
   CREATE INDEX idx_contacts_active_vip ON contacts(id)
   WHERE is_active = TRUE AND position ILIKE '%Manager%';
   ```

2. **Составные индексы** для частых JOIN-операций:
   ```sql
   CREATE INDEX idx_contact_history_contact_date
   ON contact_history(contact_id, created_at DESC);
   ```

3. **Full-text поиск** для быстрого поиска по ФИ и email:
   ```sql
   CREATE INDEX idx_contacts_search ON contacts USING GIN(
     to_tsvector('russian', first_name || ' ' || last_name)
   );
   ```

### Рекомендации
- Индексируйте часто используемые фильтры (is_active, status, priority)
- Используйте TIMESTAMPTZ для корректной работы временных зон
- Регулярно выполняйте ANALYZE для обновления статистики
- Archivируйте старые контакты (is_active = FALSE) чтобы ускорить запросы

---

## Примеры Использования

### Создание нового контакта с классификацией
```sql
BEGIN;

INSERT INTO contacts (company_id, first_name, last_name, email, position)
VALUES (1, 'Ivan', 'Ivanov', 'ivan@example.com', 'Manager');

INSERT INTO contact_classifications
  (contact_id, segment_id, priority, lifetime_value)
VALUES (currval('contacts_id_seq'), 1, 'hot', 100000.00);

COMMIT;
```

### Логирование взаимодействия
```sql
INSERT INTO contact_history
  (contact_id, source_id, interaction_type, notes, next_follow_up, status, created_by)
VALUES
  (1, 1, 'call', 'Обсудили пакет туров для 40 сотрудников',
   CURRENT_DATE + INTERVAL '7 days', 'completed', 'Suhail');
```

### Отсчет дней до follow-up
```sql
SELECT
  c.first_name || ' ' || c.last_name as contact,
  ch.next_follow_up,
  (ch.next_follow_up - CURRENT_DATE) as days_until_followup
FROM contact_history ch
JOIN contacts c ON ch.contact_id = c.id
WHERE ch.next_follow_up IS NOT NULL
ORDER BY ch.next_follow_up ASC;
```

---

## Миграции и Версионирование

### Версия 1.0.0
- Базовая CRM функциональность
- Управление контактами и компаниями
- История взаимодействий
- Предпочтения коммуникации
- Классификация клиентов

### Планы на будущее
- Интеграция с внешними системами (Salesforce, HubSpot)
- Расширенная аналитика (AI-предсказания чёрна)
- Multi-currency поддержка
- Встроенные workflow автоматизации

---

## Требования к Безопасности

1. **Role-Based Access Control (RBAC)**
   ```sql
   -- Создать роль для агентов
   CREATE ROLE tourism_agent;
   GRANT SELECT ON contacts TO tourism_agent;
   GRANT INSERT ON contact_history TO tourism_agent;
   ```

2. **Row Level Security (RLS)**
   ```sql
   ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
   CREATE POLICY contacts_own_company
     ON contacts FOR SELECT
     USING (company_id = current_user_company_id());
   ```

3. **Audit Logging**
   - Все изменения контактов логируются в audit_logs
   - Сохраняются modified_by, modified_at, old_values

---

## Статус Данных

Используется реальные данные компаний и клиентов из ОАЭ:
- Контакты из финансового, торгового, гостинично-туристического секторов
- Телефоны и email реалистичного формата
- Языковые предпочтения (English, Russian, Arabic)
- Временные зоны (UTC+4 для ОАЭ)

**Образец:** 20 компаний с 20 контактами и полной историей взаимодействий.
