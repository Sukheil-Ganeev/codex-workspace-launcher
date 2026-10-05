# Fix: Instagram ToS Warning Missing

**Дата:** 2024-02-05 (discovered during baseline testing)
**Severity:** MEDIUM
**Status:** FIXED

## Проблема

Baseline agents НЕ упоминали о нарушении Instagram Terms of Service при рекомендации scraping решений.

**Risk:**
- User не знает о юридических рисках
- Использует основной бизнес-аккаунт → ban
- Претензии "ты не предупредил!"

## Исправление

Добавлен **обязательный disclaimer** в SKILL.md:

```markdown
## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Recommending scraping without warning about Instagram ToS | Always mention: "Instagram prohibits automated scraping in ToS, but millions use it for business intelligence. Use at own risk." |
```

## Когда упоминать

**ВСЕГДА перед:**
- Рекомендацией Approach 1 (Instaloader)
- Рекомендацией Approach 2 (cloud scraping)
- Рекомендацией Approach 3 (AI-powered scraping)

**Формулировка (Russian):**
> "⚠️ Важно: Instagram запрещает автоматический сбор данных в своих правилах использования (ToS). Однако миллионы компаний используют это для бизнес-аналитики конкурентов. Используйте на свой риск и ответственность."

**Формулировка (English):**
> "⚠️ Important: Instagram prohibits automated data collection in their Terms of Service. However, millions of businesses use it for competitive intelligence. Use at your own risk."

## Дополнительные риски для Approach 1

**Для Instaloader добавить:**
```
Риски блокировки аккаунта:
- Используйте ВТОРИЧНЫЙ аккаунт (не основной бизнес)
- Задержки 60-120 секунд между запросами
- Не более 50 постов/час
```

## Проверка compliance

После рекомендации любого подхода:
- [ ] Упомянул Instagram ToS warning
- [ ] Для Approach 1: упомянул использовать secondary аккаунт
- [ ] Для Approach 1: упомянул задержки и rate limits

## Примеры

### ❌ Before (no warning):

```
Agent: "Рекомендую Approach 1 (Instaloader).
Установите через pip install instaloader..."
```

### ✅ After (with warning):

```
Agent: "Рекомендую Approach 1 (Instaloader).

⚠️ Важно: Instagram запрещает автоматический сбор данных
в ToS, но миллионы используют для бизнес-аналитики.
Используйте на свой риск.

Рекомендации безопасности:
- Используйте вторичный Instagram аккаунт (НЕ основной)
- Задержки 60-120 сек между запросами
- Максимум 50 постов/час

Установка:
pip install instaloader
..."
```

## Impact

**Before fix:** 0/3 baseline agents mentioned ToS
**After fix:** Mandatory in SKILL.md → 100% compliance expected

## Related

- `experience/_index.md` → Critical Lesson #4
- `SKILL.md` → Common Mistakes section
