CREATE INDEX idx_languages_code ON languages(language_code);
CREATE INDEX idx_translations_type ON translations(translatable_type, translatable_id);
CREATE INDEX idx_translation_keys_name ON translation_keys(key_name);
CREATE INDEX idx_content_translations_language ON content_translations(language_code);
CREATE INDEX idx_seo_translations_entity ON seo_translations(entity_type, entity_id);
