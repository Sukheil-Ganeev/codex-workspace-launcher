# Pattern: Clarification Before Solution

**Тип:** Communication Pattern
**Применимость:** Все запросы по Instagram competitor analysis

## Описание

ВСЕГДА задавать clarifying questions ДО предложения решения, даже если user говорит "срочно".

## Почему важно

**Baseline тесты показали:**
- Агенты задавали вопросы ✅
- НО при "срочности" могли skip к решению ❌

**Проблема skip:**
- 10 мин clarification vs 2 часа неправильной работы
- User ожидает "быструю аналитику" → получает "сырые данные"
- Mismatch expectations → недовольство

## The Pattern

```
1. Acknowledge request
2. Set expectations (3 quick questions)
3. Ask questions
4. THEN recommend solution
```

## Три обязательных вопроса

### Q1: Scope Definition
**Что именно нужно?**
- Просто скриншоты постов?
- Цены конкурентов?
- Полный анализ стратегии (тон, частота, engagement)?
- Comparison table?

### Q2: Budget Reality
**Какой бюджет?**
- $0 (бесплатное решение)
- $50-150/мес (облачный сервис)
- $100+/мес (AI-powered)
- Разово для презентации vs постоянный мониторинг?

### Q3: Technical Context
**Технические возможности:**
- Умеете Python?
- Есть доступ к Instagram аккаунту?
- Предпочитаете визуальный интерфейс?

## Примеры

### ❌ Skip clarification (bad):

```
User: "Помоги отследить конкурентов в Instagram, срочно нужно!"

Agent: "Начинаю настройку Instaloader..."
[Оказывается user не умеет Python и нужна была просто табличка цен]
```

### ✅ Clarify first (good):

```
User: "Помоги отследить конкурентов в Instagram, срочно нужно!"

Agent: "Помогу! Понимаю срочность. 3 быстрых вопроса (1 минута):
1. Что конкретно нужно для презентации: скриншоты / цены / анализ?
2. Бюджет: только разово или постоянный мониторинг?
3. Умеете Python или нужен визуальный интерфейс?

[Ответы помогут выбрать правильное решение и не тратить время впустую]"
```

## Red Flag: "Urgent"

**Когда user говорит "urgent":**
→ НЕ прыгать к решению
→ STOP и спросить: "Что значит urgent? К какому времени нужно?"

**Часто оказывается:**
- "Urgent" = "сегодня вечером" → manual collection
- "Urgent" = "на следующей неделе" → automation подходит

## Exceptions

**Единственный случай skip:**
User даёт ВСЕ детали в первом сообщении:
```
"Помоги настроить мониторинг 5 конкурентов в Instagram.
Бюджет $50-100/мес, не умею программировать, нужен
ежедневный чек цен и постов. Хочу автоматические отчёты."
```
→ Можно сразу рекомендовать Approach 2 (Phantom Buster)

## Метрика

**Success:** User answers 3 questions → gets precise recommendation → implements
**Failure:** Skip questions → wrong solution → user frustrated

## См. также

- `experience/improvements/progressive-disclosure-pattern.md`
- `SKILL.md` → Red Flags section
