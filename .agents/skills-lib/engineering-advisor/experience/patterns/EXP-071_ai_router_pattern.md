# EXP-071: AIRouter паттерн для проектов с минимальным AI

**Дата:** 2026-03-01
**Проект:** MLCR Investor Bot (04-investor-bot)
**Тип:** pattern
**Severity:** medium
**times_applied:** 1

## Контекст
Проект имел 1 AI touchpoint (weekly SLS analysis) с hardcoded вызовами Gemini/Groq в analyzer.py. Модель устарела (gemini-2.0-flash), не было fallback chain, не было параметров temperature/max_tokens.

## Паттерн
Даже при 1 AI touchpoint — создавать AIRouter с полной инфраструктурой:
- MODEL_CONFIG (4 бэкенда: gemini_flash, gemini3_flash, flash_lite, groq_llama)
- TASK_ROUTING (10 категорий задач с fallback chains)
- TASK_PARAMS (temperature + max_tokens per task type)
- 30s timeout per backend, structured logging
- Singleton instance: `ai_router = AIRouter()`

## Результат
- ~200 строк кода AIRouter
- Добавление новой AI-фичи = 1 строка: `await ai_router.route("category", prompt)`
- Fallback chain автоматический
- Стоимость $0/мес (free tier Gemini)

## Применение
При создании/аудите любого бота с AI:
1. Проверить наличие AIRouter или аналога
2. Если hardcoded API вызовы — предложить миграцию на Router
3. Использовать ai-model-selection-framework.md для выбора тиров
4. Максимизировать free tiers (Gemini Flash-Lite 1000 RPD, Gemini 2.5 Flash 250 RPD)

## Связанные уроки
- EXP-060: Model ID без даты-суффикса
- Фреймворк: C:/Users/londo/.claude/refs/ai-model-selection-framework.md
- Прайсинг: D:/Downloads/AI_Models_Comparison_2026/AI_MODELS_PRICING_2026.md
