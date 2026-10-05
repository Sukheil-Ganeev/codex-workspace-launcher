# Troubleshooting — prompt-engineering-patterns

## Проблема 1: Модель не следует инструкциям
**Симптом:** LLM игнорирует часть промпта, добавляет лишнее, не соблюдает формат.
**Решение:**
- Переместите критические инструкции в начало и конец промпта
- Используйте CAPS для ключевых правил: "IMPORTANT:", "NEVER:", "ALWAYS:"
- Структурируйте XML-тегами: `<rules>`, `<format>`, `<constraints>`
- Добавьте negative examples ("Do NOT do this: ...")
- Упростите: одна задача = один промпт. Разбейте сложный промпт на chain
- Повторите критическое правило в конце: "Remember: ..."

## Проблема 2: Непоследовательные ответы на один и тот же промпт
**Симптом:** Один и тот же запрос даёт разные результаты каждый раз — разная структура, длина, стиль.
**Решение:**
- Установите `temperature: 0` для детерминизма
- Добавьте few-shot примеры с точным форматом выхода
- Используйте structured output (JSON mode, tool_use)
- Фиксируйте seed (если API поддерживает)
- Задайте жёсткий шаблон: "Format your response EXACTLY as: ..."
- Self-consistency: генерируйте N ответов, выбирайте мажоритарный

## Проблема 3: Модель "галлюцинирует" факты
**Симптом:** LLM уверенно выдаёт неверную информацию — несуществующие ссылки, выдуманные цифры, ложные факты.
**Решение:**
- Предоставьте source documents в контексте
- Инструкция: "Use ONLY information from the provided context. If the answer is not in the context, say 'Information not available'"
- Требуйте цитирование: "For each claim, cite the specific source paragraph"
- Добавьте verification step: "After answering, verify each fact against the source"
- Снизьте temperature до 0-0.2
- Для критичных задач: двухэтапная генерация (draft -> fact-check -> final)

## Проблема 4: Модель отказывается выполнять задачу
**Симптом:** "I can't help with that", "As an AI, I shouldn't..." на безобидные запросы.
**Решение:**
- Добавьте контекст зачем это нужно: "For educational purposes...", "As part of a software testing task..."
- Переформулируйте: вместо "hack" -> "security audit", вместо "bypass" -> "test edge cases"
- Разбейте на подзадачи — каждая по отдельности безобидна
- Используйте system prompt для установки роли: "You are a security researcher helping identify vulnerabilities"
- Если задача действительно безопасна — поменяйте формулировку, убрав trigger-слова

## Проблема 5: Ответы слишком длинные / слишком короткие
**Симптом:** Модель пишет эссе когда нужен один абзац, или даёт отписку на сложный вопрос.
**Решение:**
- Явно задайте длину: "Answer in 2-3 sentences", "Maximum 100 words", "Provide a detailed 500-word analysis"
- Формат: "Bullet points, max 5 items" или "One paragraph, no lists"
- Few-shot: покажите примеры нужной длины
- Для коротких ответов: "Be concise. No preamble, no conclusion."
- Для длинных: "Elaborate on each point. Include examples."
- `max_tokens` в API для жёсткого ограничения (но обрезает на полуслове)

## Проблема 6: Плохое качество при chain-of-thought
**Симптом:** Модель "рассуждает" формально, но делает логические ошибки в reasoning steps.
**Решение:**
- Покажите примеры правильного рассуждения (few-shot CoT лучше zero-shot)
- Разбейте на явные шаги: "Step 1: Identify... Step 2: Analyze... Step 3: Conclude..."
- Self-consistency: генерируйте 5+ рассуждений (temperature 0.5-0.7), выбирайте мажоритарный ответ
- Verification step: "Now check your reasoning for logical errors"
- Tree-of-Thought: "Consider 3 different approaches, evaluate each, then choose the best"
