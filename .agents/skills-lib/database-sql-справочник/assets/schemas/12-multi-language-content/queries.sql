SELECT language_code, language_name FROM languages WHERE is_active = TRUE;
SELECT translatable_type, COUNT(*) as translation_count FROM translations GROUP BY translatable_type;
SELECT entity_type, COUNT(*) as seo_entries FROM seo_translations GROUP BY entity_type;
