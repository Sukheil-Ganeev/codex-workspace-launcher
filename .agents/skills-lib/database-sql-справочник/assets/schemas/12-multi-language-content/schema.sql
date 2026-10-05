CREATE TABLE languages (id SERIAL PRIMARY KEY, language_code VARCHAR(5) UNIQUE, language_name VARCHAR(100), is_active BOOLEAN DEFAULT TRUE);
CREATE TABLE translations (id SERIAL PRIMARY KEY, translatable_type VARCHAR(100), translatable_id INTEGER, language_code VARCHAR(5), field_name VARCHAR(255), translated_value TEXT, created_at TIMESTAMPTZ);
CREATE TABLE translation_keys (id SERIAL PRIMARY KEY, key_name VARCHAR(255) UNIQUE, english_text TEXT, context VARCHAR(100));
CREATE TABLE content_translations (id SERIAL PRIMARY KEY, content_type VARCHAR(100), content_id INTEGER, language_code VARCHAR(5), title VARCHAR(255), description TEXT, short_description TEXT, slug VARCHAR(255));
CREATE TABLE seo_translations (id SERIAL PRIMARY KEY, entity_type VARCHAR(100), entity_id INTEGER, language_code VARCHAR(5), meta_title VARCHAR(255), meta_description VARCHAR(500), meta_keywords VARCHAR(500));
