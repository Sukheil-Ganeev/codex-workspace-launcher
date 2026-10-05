# Progressive Disclosure Pattern

**Дата:** 2024-02-05
**Тип:** Improvement
**Статус:** Implemented

## Проблема

Baseline тесты показали: агенты задавали хорошие вопросы, НО затем предлагали ВСЕ варианты одновременно → overwhelming.

## Решение

Использовать **progressive disclosure**:
1. Спросить budget → filter подходы
2. Спросить technical skills → filter дальше
3. Предложить ТОЛЬКО релевантные (1-2 варианта max)

## Пример До/После

### ❌ До (overwhelming):

```
Есть 3 подхода:

1. Python + Instaloader ($0)
   - Требует Python
   - Риск блокировки
   - 1 час настройки
   ...

2. Облачные сервисы ($50-150/мес)
   - Apify: $49/мес
   - Phantom Buster: $59/мес
   ...

3. AI-powered ($100+/мес)
   - Make.com + Claude API
   - 1-2 дня настройки
   ...

Что выбираете?
```

### ✅ После (progressive):

```
Помогу! Быстро 3 вопроса:
1. Бюджет: $0 / $50-150 / $100+?
2. Технические навыки: умеете Python / предпочитаете no-code?
3. Как часто проверять: раз в неделю / каждый день?

[User: $0, не умею программировать, раз в неделю]

Понял! В вашем случае:
→ Бесплатный вариант (Instaloader) не подойдёт (нужен Python)
→ Рекомендую: Phantom Buster ($59/мес)
  - Визуальный интерфейс, код не нужен
  - Настройка 10 минут
  - Еженедельное расписание встроено

Хотите пошаговую инструкцию?
```

## Метрика успеха

**До:** User overwhelmed → много вопросов уточняющих
**После:** 3 вопроса → 1 чёткая рекомендация → User action

## Применение

Использовать ВСЕГДА когда:
- Есть 3+ варианта решения
- User не технический
- Варианты сильно отличаются по сложности/цене

## Код паттерна

```javascript
// Decision tree
if (budget === 0) {
  if (hasPython) recommend(Approach1)
  else recommend("Manual check or save money for cloud")
}
else if (budget < 150) {
  if (techSkills) recommend(Approach2_Apify)
  else recommend(Approach2_PhantomBuster)
}
else {
  recommend(Approach3_AI)
}
```

## Связанные паттерны

- `experience/patterns/clarification-before-solution.md`
- `experience/improvements/decision-flowchart.md`
