# Критические уроки (Топ-5)

**ЧИТАТЬ ПРИ АКТИВАЦИИ СКИЛЛА!**

## 1. Не предлагать все 3 подхода сразу

**Проблема:** Overwhelm пользователя выбором
**Решение:** Использовать decision framework → спросить budget/skills → предложить 1-2 релевантных варианта

**Пример:**
```
❌ "Есть 3 подхода: бесплатный, облачный и AI..."
✅ "Быстро: какой бюджет ($0 / $50+ / $100+)?" → предложить соответствующий подход
```

## 2. Начинать с вопросов, НЕ с решений

**Проблема:** Даже при "срочности" пропуск clarification → неправильное решение
**Решение:** ВСЕГДА задать 3 ключевых вопроса: budget, technical skills, frequency

**Триггер:** User says "urgent" → STOP → Clarify scope first (10 мин вопросов vs 2 часа неправильной работы)

## 3. Переводить технический жаргон для нетехнических пользователей

**Проблема:** API, scraping, rate limits → confusion
**Решение:** Использовать переводы:
- API → "подключение" / "соединение"
- Scraping → "автоматический сбор данных"
- Rate limits → "ограничения Instagram на скорость"
- Cloud service → "облачный сервис (работает 24/7 без вашего компьютера)"

## 4. Предупреждать о Instagram ToS и рисках блокировки

**КРИТИЧНО:** Упомянуть ДО начала реализации:
> "Instagram запрещает автоматический сбор данных в ToS, но миллионы используют для бизнес-аналитики. Используйте на свой риск."

**Для Approach 1 (Instaloader):**
- Использовать secondary аккаунт (НЕ основной бизнес-аккаунт)
- Задержки 60-120 сек между запросами
- Не более 50 постов/час

## 5. Ссылаться на существующий проект вместо recreate from scratch

**Проблема:** Тратить время на создание кода который уже есть
**Решение:** Проверить `D:/Downloads/instagram_competitor_analysis/` → если есть → point to specific folder

**Структура проекта:**
- `approach_1_instaloader/` → готовый Python скрипт
- `approach_2_cloud_services/` → API клиенты для Apify
- `approach_3_full_automation/` → Claude API analyzer + Make.com workflows

---

## Когда применять этот скилл

**DO:**
- Любой вопрос про Instagram competitor monitoring/scraping/tracking
- Выбор между инструментами (Instaloader vs Apify vs Phantom Buster)
- Автоматизация сбора данных из соцсетей конкурентов

**DON'T:**
- Общий social media management (не competitor-focused)
- Instagram content creation (другой use case)
- Разовый ручной чек одного конкурента

---

**Дата создания опыта:** 2024-02-05
**Источник:** TDD baseline testing + GREEN phase compliance testing
