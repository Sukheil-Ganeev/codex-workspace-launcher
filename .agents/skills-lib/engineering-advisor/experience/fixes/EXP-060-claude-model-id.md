# EXP-060: Claude API model ID — без даты-суффикса

- **Severity:** high
- **Тип:** fix
- **Проект:** ContentFactory (Telegram bot)
- **Дата:** 2026-02-28
- **Контекст:** Подключение Claude Sonnet 4.6 в ai_adapter.py. Использован model ID `claude-sonnet-4-6-20250514` (по аналогии с другими провайдерами где дата = версия). API вернул 404 Not Found.
- **Корневая причина:** Anthropic API использует короткие model ID БЕЗ даты-суффикса. Правильный ID: `claude-sonnet-4-6`, НЕ `claude-sonnet-4-6-20250514`.
- **Урок:** При подключении Anthropic Claude API — всегда использовать короткий model ID без даты. Это отличается от Google Gemini (где `gemini-2.5-flash-preview-05-20` с датой) и OpenAI (где `gpt-4o-2024-08-06` с датой).
- **Правило:**
  - Anthropic: `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5-20251001`
  - Google: `gemini-2.5-flash-preview-05-20` (с датой)
  - OpenAI: `gpt-4o-2024-08-06` (с датой)
  - Groq: `llama-3.3-70b-versatile` (без даты)
- **Применение:** Перед первым вызовом нового провайдера — проверить формат model ID через тестовый вызов или документацию. Не копировать формат одного провайдера на другой.
- **Применено:** 1 раз (ContentFactory)
- **Tags:** #anthropic, #claude, #model-id, #api, #404, #ai-adapter
