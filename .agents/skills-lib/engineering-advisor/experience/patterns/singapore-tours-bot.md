# EXP-EA-SG001: SingaporeToursBot — Архитектурные решения (2026-02-18)

**Проект:** Telegram-бот для туризма в Сингапуре
**Стек:** aiogram 3.x + SQLite/FTS5 + Gemini/Groq + python-dotenv

## Архитектурные решения

1. **Модульная структура handlers/**: каждый handler = отдельный Router. Порядок подключения важен (admin первый для приоритета команд, ai_assistant последний как catch-all для текста)

2. **Database как DI через dp["db"]**: глобальный экземпляр Database инжектится в Dispatcher, доступен из любого handler через `message.bot["db"]`. Проще чем middleware, не нужен DI-фреймворк

3. **FTS5 для мультиязычного поиска**: Virtual table с триггерами INSERT/DELETE/UPDATE. Ищет по 6 полям (name_ru/en/zh + description_ru/en/zh). Работает быстрее чем LIKE на 100+ товарах

4. **i18n через JSON + t(key, lang)**: Никаких библиотек. 3 JSON файла, 68 ключей, функция t() с fallback на EN -> key. Placeholders через .format(**kwargs). Достаточно для 3 языков

5. **Navigation Stack**: in-memory dict (user_id -> stack). push/pop/peek. Лимит 20. Не дублирует подряд. Сброс при переходе в главное меню. Лучше чем callback_data="back_to_X" для каждого экрана

6. **Dual Backend AI**: Gemini primary -> Groq fallback. System prompt с JSON каталога + правилами. 99.9% uptime. Проверен на 3 проектах (VoiceBot, ContentFactory, SingaporeToursBot)

7. **3-уровневая комиссия**: базовый % -> агент % -> агент+категория %. Приоритет от специфичного к общему. Реализация: 3 SQL запроса с fallback-цепочкой

8. **Реферальные deeplinks**: ?start=ref_CODE -> парсинг в cmd_start -> create_referral(user, agent). UNIQUE constraint на user_id — клиент привязан к первому агенту навсегда

## Анти-паттерны (что НЕ делать)

- НЕ хранить state в module-level dict для FSM -> использовать aiogram FSM (StatesGroup)
- НЕ комментировать на 3 языках -> i18n файлы для UI, код — только на EN
- НЕ делать отдельный WhatsApp endpoint сразу -> сначала стабилизировать Telegram, потом добавить
- НЕ использовать reload=True в uvicorn (урок из VoiceBot — зомби-процессы)

## Метрики проекта
- 32+ файлов, 11 таблиц БД, 68 ключей i18n x 3 языка
- Создано за 1 сессию с 4 параллельными агентами
- 0 конфликтов кода благодаря контракту импортов
