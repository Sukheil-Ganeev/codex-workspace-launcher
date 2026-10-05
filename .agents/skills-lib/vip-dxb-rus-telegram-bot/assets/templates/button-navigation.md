# Button Navigation Template

Шаблон для документирования навигационных кнопок в VIP-DXB-RUS боте.

---

## Базовый шаблон кнопок (таблица)

```markdown
## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | [EMOJI] [Текст кнопки] | [ID блока] — [Название блока] | inline |
| 2 | [EMOJI] [Текст кнопки] | [ID блока] — [Название блока] | inline |
| ... | ... | ... | ... |
| N | ⬅ Назад | [ID родительского меню] — [Название] | inline |
```

---

## Паттерны кнопок

### Паттерн 1: Кнопки с emoji (Классический)

Используется в **меню категорий** для быстрой визуальной навигации.

**Шаблон:**
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | 🎢 Тематические парки | [ID] — Theme Parks Menu | inline |
| 2 | 💦 Аквапарки | [ID] — Aquaparks Menu | inline |
| 3 | 👀 Смотровые площадки | [ID] — Observation Decks | inline |
| 4 | 🎨 Музеи | [ID] — Museums Menu | inline |
| 5 | ⬅ Назад | [ID] — Main Menu [Emirate] | inline |
```

**Применение:**
- Главные меню эмиратов (010-013)
- Категории парков (500-560)
- Меню услуг

---

### Паттерн 2: Кнопки с описанием

Используется в **субменю** для конкретных объектов.

**Шаблон:**
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | 🎢 Тематический парк Ferrari World | [ID] — Ferrari World Card | inline |
| 2 | 🦸 Тематический парк Warner Bros | [ID] — Warner Bros Card | inline |
| 3 | 🐬 Тематический парк SeaWorld | [ID] — SeaWorld Card | inline |
| 4 | ⬅ Назад | [ID] — Theme Parks Menu | inline |
```

**Применение:**
- Списки конкретных парков
- Списки экскурсий
- Списки ресторанов/beach clubs

---

### Паттерн 3: Combo-кнопки (Пакетные предложения)

Используется для **специальных предложений** и комбо-билетов.

**Шаблон:**
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | 🎟 Выгодно: билеты на 2 парка | [ID] — 2 Parks Package | inline |
| 2 | 🎟 Выгодно: билеты на 3 парка | [ID] — 3 Parks Package | inline |
| 3 | 🎟 Выгодно: билеты на 4 парка | [ID] — 4 Parks Package | inline |
| 4 | ⬅ Назад | [ID] — Parks Menu | inline |
```

**Применение:**
- Пакеты билетов в парки
- Комбо экскурсии
- Специальные предложения

---

### Паттерн 4: Кнопки бронирования (Action Buttons)

Используется в **карточках услуг** для действий пользователя.

**Шаблон для экскурсий:**
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Оплатить групповой тур | [ID формы GT] — Group Excursion Booking | inline |
| 2 | Оплатить приватный тур | [ID формы PT] — Private Excursion Booking | inline |
| 3 | ⬅ Назад | [ID] — Excursions Menu [Emirate] | inline |
```

**Шаблон для услуг (парки, активности):**
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Забронировать [Название услуги] | [ID формы] — [FORM-NAME] | inline |
| 2 | ⬅ Назад | [ID] — [Category Menu] | inline |
```

**Применение:**
- Карточки экскурсий (2 варианта: групповой/приватный)
- Карточки услуг (1 вариант: бронирование)
- Карточки парков (покупка билетов)

---

### Паттерн 5: Навигация "Назад" (Back Button)

**КРИТИЧЕСКИ ВАЖНО:** Каждый блок ДОЛЖЕН иметь кнопку "Назад"!

**Шаблон:**
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| N | ⬅ Назад | [ID родительского меню] — [Название] | inline |
```

**Правила:**
- Всегда последняя кнопка в списке
- Emoji: ⬅ (стрелка влево)
- Ведет к **родительскому меню** в иерархии

**Пример иерархии:**
```
Main Menu Dubai (010)
  ↓
Excursions from Dubai
  ↓
Modern Dubai (101) ← "⬅ Назад" → Excursions from Dubai
```

---

## Таблица входящих путей (Incoming Paths)

Документирует, откуда пользователь может попасть в данный блок.

**Шаблон:**
```markdown
## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | [ID] — [Название блока] | Button "[EMOJI] [Текст кнопки]" |
| 2 | [ID] — [Название блока] | Button "[EMOJI] [Текст кнопки]" |
```

**Пример для экскурсии:**
```markdown
## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | Excursions from Dubai | Button "🏙️ Современный Дубай" |
```

**Пример для услуги, доступной из нескольких мест:**
```markdown
## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | Main Menu Dubai (010) | Button "🏙️ Экскурсии" |
| 2 | Main Menu Abu Dhabi (011) | Button "🏙️ Экскурсии" |
| 3 | Main Menu RAK (012) | Button "🏙️ Экскурсии" |
```

---

## Emoji стандарты для кнопок

### Эмираты:
```
🕌 Abu Dhabi
🌆 Dubai
🏖️ Ras Al Khaimah
🌊 Fujairah
```

### Услуги:
```
🏙️ Экскурсии
🎡 Тематические парки
🎢 Аквапарки
⛵️ Круизы
🛥 Яхты
🚗 Аренда авто
🪪 Международные права
🌊 Водные активности
🏜 Багги
🏊 Infinity pools
🏖️ Beach clubs
🏨 Отели
🍽️ Рестораны
🧘‍♀️ SPA
```

### Парки:
```
🎢 Тематические парки общие
🦁 Зоопарки
🌸 Парки цветов
👀 Смотровые площадки
🎨 Музеи
💦 Аквапарки
🏰 Исторические места
```

### Специальные:
```
⬅ Назад (всегда для кнопки Back)
🎟 Выгодно (для пакетов)
📞 Связаться с менеджером
💰 Оплатить
📋 Забронировать
```

---

## Примеры полной документации кнопок

### Пример 1: Главное меню эмирата

```markdown
# 010 Main Menu Dubai

**Type:** Main Menu
**Date:** 01.02.2026

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | 🏙️ Экскурсии из Дубая | Excursions from Dubai | inline |
| 2 | 🎡 Парки и развлечения | Parks Dubai Menu | inline |
| 3 | 🚗 Аренда авто | Car Rental Menu | inline |
| 4 | 🏊 Infinity pools | Pools Menu | inline |
| 5 | 🏖️ Beach clubs | Beach Clubs Dubai | inline |
| 6 | 🍽️ Рестораны | Restaurants Dubai | inline |
| 7 | 🧘‍♀️ SPA & Wellness | SPA Dubai | inline |
| 8 | ⬅ Назад | /start — Select Emirate | inline |

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | 001 /start | Button "🌆 Dubai" |
```

### Пример 2: Карточка экскурсии

```markdown
# 101 Modern Dubai from Dubai

**Type:** Excursion Card
**Date:** 01.02.2026

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Оплатить групповой тур | Group excursion booking (FORM-GT) | inline |
| 2 | Оплатить приватный тур | Private excursion booking (FORM-PT) | inline |
| 3 | ⬅ Назад | Excursions from Dubai | inline |

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | Excursions from Dubai | Button "🏙️ Современный Дубай" |
```

### Пример 3: Категория парков

```markdown
# 500 Parks Dubai Menu

**Type:** Category Menu
**Date:** 01.02.2026

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | 🎢 Тематические парки | Theme Parks Submenu | inline |
| 2 | 💦 Аквапарки | Aquaparks Submenu | inline |
| 3 | 👀 Смотровые площадки | Observation Decks | inline |
| 4 | 🎨 Музеи | Museums Menu | inline |
| 5 | ⬅ Назад | 010 — Main Menu Dubai | inline |

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | 010 — Main Menu Dubai | Button "🎡 Парки и развлечения" |
```

---

## Типы кнопок (Button Types)

| Type | Описание | Применение |
|------|----------|-----------|
| **inline** | Inline кнопка внутри сообщения | Основная навигация |
| **reply** | Reply кнопка под полем ввода | Редко используется |
| **url** | Внешняя ссылка | Ссылки на сайты, оплату |
| **callback** | Callback с данными | Формы, выбор опций |

**В VIP-DXB-RUS боте используется почти исключительно тип `inline`.**

---

## Checkpoint для проверки кнопок

При документировании блока проверьте:

- [ ] Все кнопки задокументированы в таблице
- [ ] Указаны ID блоков назначения
- [ ] Есть кнопка "⬅ Назад" (КРИТИЧНО!)
- [ ] Emoji соответствуют стандартам
- [ ] Входящие пути (Incoming Paths) задокументированы
- [ ] Тип кнопок указан (обычно `inline`)
- [ ] Проверены реальные переходы в конструкторе бота

---

## Типичные ошибки

### ❌ Ошибка 1: Отсутствие кнопки "Назад"
```markdown
| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Забронировать | FORM-POOL | inline |
```

**Решение:** Всегда добавляйте Back button!

### ❌ Ошибка 2: Неверный emoji
```markdown
| 1 | 🔙 Назад | Main Menu | inline |
```

**Решение:** Используйте ⬅ для кнопки "Назад"

### ❌ Ошибка 3: Отсутствие ID блока назначения
```markdown
| 1 | 🏙️ Экскурсии | Excursions Menu | inline |
```

**Решение:** Указывайте ID: `[ID] — Excursions Menu`

### ❌ Ошибка 4: Циклические ссылки
```markdown
Block A → Button leads to Block B
Block B → Button leads to Block A (и нет других путей)
```

**Решение:** Обеспечьте путь к родительскому меню или /start

---

## Полезные команды для тестирования навигации

1. **Проверка всех путей от /start:**
   - /start → Выбор эмирата → Главное меню → Категория → Услуга → Форма

2. **Проверка Back button:**
   - Нажмите "⬅ Назад" на каждой странице
   - Убедитесь, что возвращаетесь на правильный уровень

3. **Проверка cross-emirate услуг:**
   - Некоторые услуги доступны из всех эмиратов
   - Убедитесь, что Back возвращает к правильному меню эмирата

---

**Итого:** Правильная навигация = довольный пользователь! 🎯
