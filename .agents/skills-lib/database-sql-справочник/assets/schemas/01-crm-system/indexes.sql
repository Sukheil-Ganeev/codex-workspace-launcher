-- 01-CRM System Indexes
-- Оптимальные индексы для быстрого поиска и фильтрации

-- Индексы для таблицы companies
CREATE INDEX idx_companies_country ON companies(country) WHERE is_active = TRUE;
CREATE INDEX idx_companies_email ON companies(email);
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_active ON companies(is_active);

-- Индексы для таблицы contacts
CREATE INDEX idx_contacts_company_id ON contacts(company_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_mobile ON contacts(mobile);
CREATE INDEX idx_contacts_country ON contacts(country) WHERE is_active = TRUE;
CREATE INDEX idx_contacts_city ON contacts(city);
CREATE INDEX idx_contacts_created_at ON contacts(created_at DESC);
CREATE INDEX idx_contacts_active ON contacts(is_active);
-- Составной индекс для частых запросов
CREATE INDEX idx_contacts_company_active ON contacts(company_id, is_active);
-- Частичный индекс для активных контактов
CREATE INDEX idx_contacts_active_vip ON contacts(id) WHERE is_active = TRUE AND position ILIKE '%Manager%';

-- Индексы для таблицы contact_sources
CREATE INDEX idx_contact_sources_category ON contact_sources(category);

-- Индексы для таблицы contact_history
CREATE INDEX idx_contact_history_contact_id ON contact_history(contact_id);
CREATE INDEX idx_contact_history_created_at ON contact_history(created_at DESC);
CREATE INDEX idx_contact_history_type ON contact_history(interaction_type);
CREATE INDEX idx_contact_history_status ON contact_history(status);
CREATE INDEX idx_contact_history_next_followup ON contact_history(next_follow_up) WHERE next_follow_up IS NOT NULL;
-- Составной индекс
CREATE INDEX idx_contact_history_contact_date ON contact_history(contact_id, created_at DESC);

-- Индексы для таблицы contact_classifications
CREATE INDEX idx_contact_classifications_contact_id ON contact_classifications(contact_id);
CREATE INDEX idx_contact_classifications_segment_id ON contact_classifications(segment_id);
CREATE INDEX idx_contact_classifications_priority ON contact_classifications(priority);
-- Составной индекс
CREATE INDEX idx_contact_classifications_segment_priority ON contact_classifications(segment_id, priority);

-- Индексы для таблицы tasks
CREATE INDEX idx_tasks_contact_id ON tasks(contact_id);
CREATE INDEX idx_tasks_status ON tasks(status) WHERE status != 'completed';
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_priority ON tasks(priority);
-- Составной индекс для открытых задач
CREATE INDEX idx_tasks_open_due ON tasks(due_date) WHERE status != 'completed' AND status != 'cancelled';

-- Индексы для таблицы documents
CREATE INDEX idx_documents_contact_id ON documents(contact_id);
CREATE INDEX idx_documents_company_id ON documents(company_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_date ON documents(document_date DESC);
CREATE INDEX idx_documents_expiration ON documents(expiration_date) WHERE expiration_date IS NOT NULL;

-- Индексы для таблицы contact_tags
CREATE INDEX idx_contact_tags_name ON contact_tags(name);

-- Индексы для таблицы contact_tag_assignments
CREATE INDEX idx_contact_tag_assignments_contact_id ON contact_tag_assignments(contact_id);
CREATE INDEX idx_contact_tag_assignments_tag_id ON contact_tag_assignments(tag_id);

-- Индексы для таблицы communication_preferences
CREATE INDEX idx_communication_preferences_contact_id ON communication_preferences(contact_id);
CREATE INDEX idx_communication_preferences_language ON communication_preferences(language_preference);

-- Индексы для таблицы mailing_lists
CREATE INDEX idx_mailing_lists_name ON mailing_lists(name);

-- Индексы для таблицы mailing_list_subscriptions
CREATE INDEX idx_mailing_list_subscriptions_list_id ON mailing_list_subscriptions(mailing_list_id);
CREATE INDEX idx_mailing_list_subscriptions_contact_id ON mailing_list_subscriptions(contact_id);
CREATE INDEX idx_mailing_list_subscriptions_active ON mailing_list_subscriptions(is_active);
-- Составной индекс
CREATE INDEX idx_mailing_list_subscriptions_list_active ON mailing_list_subscriptions(mailing_list_id, is_active);

-- Индексы для частых вычислений
CREATE INDEX idx_contacts_search ON contacts USING GIN(
    to_tsvector('russian', first_name || ' ' || last_name || ' ' || COALESCE(email, ''))
);
