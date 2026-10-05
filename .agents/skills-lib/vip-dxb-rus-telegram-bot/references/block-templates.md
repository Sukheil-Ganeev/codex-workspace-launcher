# Block Templates - Шаблоны контентных блоков

Коллекция готовых шаблонов для создания новых блоков в боте VIP-DXB-RUS.

---

## Содержание

1. [Шаблон экскурсии](#1-шаблон-экскурсии)
2. [Шаблон меню](#2-шаблон-меню)
3. [Шаблон сервиса](#3-шаблон-сервиса)
4. [Шаблон формы](#4-шаблон-формы)
5. [Шаблон лояльности](#5-шаблон-лояльности-new)
6. [Шаблон BANT-квалификации](#6-шаблон-bant-квалификации-new)
7. [Шаблон напоминания](#7-шаблон-напоминания-new)
8. [Примеры использования](#примеры-использования)

---

## 1. Шаблон экскурсии

**Назначение:** Карточка экскурсии с описанием и кнопками бронирования

```markdown
# [ID] [Название экскурсии] from [Эмират]

**Type:** Excursion Card
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[EMOJI] [Название экскурсии]

[1-3 предложения с описанием маршрута]

Продолжительность: [X часов]
Что входит: [список включений]
Цена: от [X] AED
```

---

## Media
- Image: [Yes/No] — [Описание изображения]
- Video: No
- Document: No

---

## Variables

**Uses (reads):** None

**Sets (writes):** None

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | [ID меню] — Excursions from [Эмират] | Button "[EMOJI] [Название]" |

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Оплатить групповой тур | FORM-GT | inline |
| 2 | Оплатить приватный тур | FORM-PT | inline |
| 3 | ⬅ Назад | [ID меню] — Excursions from [Эмират] | inline |

---

## Notes

- Стандартная карточка экскурсии
- 2 варианта бронирования (групповой/приватный)
- Эмират: [Dubai/Abu Dhabi/RAK/Fujairah]
- Форма группового тура: **FORM-GT** (8 полей)
- Форма приватного тура: **FORM-PT** (9 полей)
```

### Emoji для экскурсий:

| Emoji | Категория |
|-------|-----------|
| 🏙️ | Современный Дубай |
| 🕌 | Абу-Даби (мечети) |
| 🌊 | Морские круизы |
| 🏜️ | Джип-сафари/пустыня |
| 🦁 | Зоопарки |
| 🌸 | Парки цветов |
| 🎡 | Развлечения |
| 🏰 | Исторические места |
| 🎣 | Рыбалка |
| 🦀 | Охота на крабов |
| 🏎️ | Авто-туры |

---

## 2. Шаблон меню

**Назначение:** Навигационное меню категории или подкатегории

```markdown
# [ID] [Название категории] Menu

**Type:** Menu/Submenu
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Опционально: приветствие с {{FIRST_NAME_TEXT}}]

[Название меню/категории]

[Опционально: подзаголовок или описание]
```

---

## Media
- Image: [Yes/No]
- Video: No
- Document: No

---

## Variables

**Uses (reads):**
- `{{FIRST_NAME_TEXT}}` — если используется персонализация

**Sets (writes):** None

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | [ID родительского меню] — [Название] | Button "[EMOJI] [Текст]" |

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | [EMOJI] [Услуга 1] | [ID блока] — [Название] | inline |
| 2 | [EMOJI] [Услуга 2] | [ID блока] — [Название] | inline |
| 3 | [EMOJI] [Услуга 3] | [ID блока] — [Название] | inline |
| N | ⬅ Назад | [ID родительского меню] | inline |

---

## Notes

- [Количество] услуг доступно
- Эмират: [Dubai/Abu Dhabi/RAK/Fujairah/All]
```

### Паттерны кнопок:

**Паттерн 1: Кнопки с emoji (классика)**
```
🎢 Тематические парки
💦 Аквапарки
👀 Смотровые площадки
🎨 Музеи
```

**Паттерн 2: Кнопки с описанием**
```
🎢 Тематический парк Ferrari World
🦸 Тематический парк Warner Bros
🐬 Тематический парк SeaWorld
```

**Паттерн 3: Combo-кнопки (пакеты)**
```
🎟 Выгодно: билеты на 2 парка
🎟 Выгодно: билеты на 3 парка
🎟 Выгодно: билеты на 4 парка
```

### Emoji по категориям:

**Эмираты:**
- 🕌 Abu Dhabi
- 🌆 Dubai
- 🏖️ Ras Al Khaimah
- 🌊 Fujairah

**Услуги:**
- 🏙️ Экскурсии
- 🎡 Тематические парки
- 🎢 Аквапарки
- ⛵️ Круизы
- 🛥 Яхты
- 🚗 Аренда авто
- 🪪 Международные права
- 🌊 Водные активности
- 🏜 Багги
- 🏊 Бассейны
- 🏖️ Пляжные клубы
- 🏨 Отели
- 🍽️ Рестораны
- 🧘‍♀️ SPA
- ⭐ Отзывы
- 🎁 Скидки/Лояльность
- ⬅ Кнопка "Назад"

---

## 3. Шаблон сервиса

**Назначение:** Карточка услуги (парки, бассейны, пляжи, SPA и т.д.)

```markdown
# [ID] [Название услуги]

**Type:** Service Card
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[EMOJI] [Название услуги]

[1-3 предложения с описанием]

[Опционально: цена, продолжительность, что включено]
```

---

## Media
- Image: [Yes/No] — [Описание]
- Video: No
- Document: No

---

## Variables

**Uses (reads):** None

**Sets (writes):** None

---

## Incoming Paths

| # | From Block | Via Button/Action |
|---|-----------|------------------|
| 1 | [ID меню] — [Название] | Button "[EMOJI] [Текст]" |

---

## Buttons (Outgoing Paths)

| # | Button Text | Leads to Block | Button Type |
|---|------------|---------------|-------------|
| 1 | Забронировать | [FORM-NAME] | inline |
| 2 | ⬅ Назад | [ID меню] | inline |

---

## Notes

- Категория: [Parks/Activities/Services]
- Эмират: [Dubai/Abu Dhabi/RAK/Fujairah/All]
- Форма бронирования: **[FORM-NAME]** ([X полей])
```

### Шаблоны описания по категориям:

**Парки (Parks):**
```
[EMOJI] [Название парка]

[Описание аттракционов и зон, 1-2 предложения]

Билеты: от [X] AED
Режим работы: [время]
Что включено: [список]
```

**Водные активности:**
```
[EMOJI] [Название активности]

[Описание маршрута/программы, 1-2 предложения]

Продолжительность: [X часов]
Включено: [экипировка, инструктор, трансфер]
Цена: от [X] AED
```

**Бассейны (Pools):**
```
🏊 [Название infinity pool]

[Описание локации и вида, 1-2 предложения]

Сессии: утренняя/sunset/весь день/ночная
Виды: [Palm/Burj Khalifa/Marina/Burj Al Arab]
```

**Пляжные клубы:**
```
🏖️ [Название beach club]

[Описание атмосферы и услуг, 1-2 предложения]

Зоны: pool/beach/restaurant
Опции: single bed/double/VIP villa/cabana
```

**Багги/Сафари:**
```
🏜 [Название программы]

[Описание маршрута по пустыне, 1-2 предложения]

Транспорт: Buggy 2/4-seat, Quad
Модели: PRO Can-Am / Standard Polaris
Продолжительность: 1h/2h/4h
Время: Sunset/Morning/Day
```

**SPA:**
```
🧘‍♀️ [Название услуги SPA]

[Описание процедуры и эффекта, 1-2 предложения]

Локация: Визит на дом / Салон
Тип: Hammam/Massage/Facial/IV Drip
Техники: Relax/Deep/Thai/Bali
Длительность: 60/90/120 минут
```

**Рестораны:**
```
🍽️ [Название ресторана]

[Описание кухни и атмосферы, 1-2 предложения]

Кухня: [тип]
Зоны посадки: Inside Non-smoking/Smoking/Terrace
```

---

## 4. Шаблон формы

**Назначение:** Документация формы бронирования

```markdown
# FORM-[NAME] — [Тип услуги]

**Purpose:** [Описание назначения формы]
**Complexity:** [1-5 звёзд]

---

## Structure

| # | Field | Variable | Type | Required | Notes |
|---|-------|----------|------|----------|-------|
| 1 | Имя | `[prefix]_client_name` | TEXT | Yes | 1-100 chars |
| 2 | Телефон | `[prefix]_phone` | PHONE | Yes | +971-XX-XXX-XXXX |
| 3 | Email | `[prefix]_email` | EMAIL | Yes | name@domain.ext |
| 4 | Дата | `[prefix]_date` | DATE | Yes | YYYY-MM-DD |
| ... | ... | ... | ... | ... | ... |

**Total fields:** [X]

---

## Choice Fields Details

**[Название поля]** (`[prefix]_[variable]`):
```
- Option 1 — [описание]
- Option 2 — [описание]
- Option 3 — [описание]
- Skip — [если опционально]
```

---

## File Upload Fields (если есть)

| Field | Variable | Accepted | Max Size | Required |
|-------|----------|----------|----------|----------|
| Паспорт | `[prefix]_doc_passport` | JPG, PNG, PDF | 10 MB | Yes |
| Права | `[prefix]_doc_license` | JPG, PNG, PDF | 10 MB | Yes |

---

## Incoming Transitions

| # | Block ID | Block Name | Button Text |
|---|----------|------------|-------------|
| 1 | [ID] | [Услуга] | Забронировать |

---

## Outgoing Actions

1. **Data saved** to variables `[prefix]_*`
2. **Notification sent** to manager
3. **User receives** confirmation
4. **Redirect** to block 980-995
```

### Префиксы переменных по формам:

| Form | Prefix | Пример переменной |
|------|--------|-------------------|
| FORM-GT | `gt_` | gt_client_name, gt_tour_date |
| FORM-PT | `pt_` | pt_start_time, pt_count_adults |
| FORM-BUGGY | `buggy_` | buggy_vehicle_type, buggy_duration |
| FORM-RENT | `rent_` | rent_car_name, rent_days |
| FORM-POOL | `pool_` | pool_venue_name, pool_session |
| FORM-BEACH | `beach_` | beach_zone, beach_bed_type |
| FORM-SPA | `spa_` | spa_technique, spa_therapist_sex |
| FORM-TRANSFER | `tr_` | tr_flight_num, tr_car_class |
| FORM-YACHT | `yacht_` | yacht_route, yacht_food |
| FORM-REST | `rest_` | rest_seating, rest_occasion |
| FORM-REVIEW | `review_` | review_rating, review_screenshot |
| FORM-TICKETS | `ticket_` | ticket_attraction, ticket_adults |

---

## 5. Шаблон лояльности (NEW)

**Назначение:** Блоки программы лояльности (скидки, баллы, рефералы)

```markdown
# [ID] [Название функции лояльности]

**Type:** Loyalty System
**Date:** [DD.MM.YYYY]

---

## Message Text
```
🎁 [Название функции]

[Описание выгоды для пользователя]

Как получить:
1. [Шаг 1]
2. [Шаг 2]
3. [Шаг 3]

Скидка действует {{promo_days}} дней!
```

---

## Variables

**Uses (reads):**
- {{balance}} — Баланс баллов
- {{promo_days}} — Дней до окончания

**Sets (writes):**
- {{loyalty_action_completed}} → true

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | [Action] | [Form/External] | inline |
| 2 | Личный кабинет | Block 960 | inline |
| 3 | ⬅ Назад | Main Menu | inline |

---

## Notes

- Интегрируется с системой лояльности
- Промокод истекает через 30 дней
- Одноразовое действие на пользователя
```

### Типы лояльности:

| Тип | Скидка | Условие | Срок |
|-----|--------|---------|------|
| Подписка | 10% | Подписаться на канал | Постоянная |
| Отзыв | 15% | Оставить отзыв на Google | 30 дней |
| Реферал | 25% | Пригласить 3 друзей | 30 дней |
| Баллы | 150 AED | Накопить 150 баллов | Постоянные |

---

## 6. Шаблон BANT-квалификации (NEW)

**Назначение:** Квалификация лидов по методу BANT

```markdown
# [ID] BANT Question: [Budget/Authority/Need/Timeframe]

**Type:** Qualification
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Вопрос]

[Краткое объяснение, зачем спрашиваем]
```

---

## Variables

**Uses (reads):** None

**Sets (writes):**
- {{bant_[field]}} — Ответ пользователя
- {{bant_score}} — +[баллы]

---

## Buttons

| # | Button Text | Points | Leads to | Type |
|---|------------|--------|----------|------|
| 1 | [Вариант 1] | +3 | Next Question | inline |
| 2 | [Вариант 2] | +2 | Next Question | inline |
| 3 | [Вариант 3] | +0 | Next Question | inline |

---

## Logic

После 4 вопросов:
- 9-11 points → Hot → Немедленный звонок
- 5-8 points → Warm → Ответ в течение 2ч
- 0-4 points → Cold → Nurture sequence
```

### Вопросы BANT:

| Вопрос | Поле | Варианты | Баллы |
|--------|------|----------|-------|
| Какой бюджет? | bant_budget | Эконом/Средний/Премиум | 0/2/3 |
| Когда планируете? | bant_timeframe | Неделя/Месяц/3+ месяца | 3/2/0 |
| Сколько человек? | bant_group_size | 1-2/3-5/6+ | 1/2/3 |
| Кто решает? | bant_authority | Сам/Согласовать | 3/1 |

---

## 7. Шаблон напоминания (NEW)

**Назначение:** Автоматические напоминания по событиям

```markdown
# [ID] Reminder: [Тип]

**Type:** Automated Reminder
**Date:** [DD.MM.YYYY]

---

## Message Text
```
[Заголовок напоминания]

[Детали с переменными]
📅 Дата: {{reminder_date}}
🕐 Время: {{reminder_time}}

[Что делать дальше]
```

---

## Trigger

**Category check:** Has category "{{reminder_category}}"
**Wait time:** [X часов/дней] after [событие]

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | [Action] | [Form/Block] | inline |
| 2 | Напомнить позже | Snooze | inline |
| 3 | ⬅ Назад | Main Menu | inline |

---

## Variables

**Uses (reads):**
- {{reminder_date}}
- {{reminder_time}}
- {{user_name}}

**Sets (writes):**
- {{reminder_sent}} → true
- {{reminder_count}} +1
```

### Типы напоминаний:

| Тип | Триггер | Время | Содержание |
|-----|---------|-------|------------|
| До полёта | Дата полёта | -24 часа | Документы, страховка, валюта |
| После бронирования | Бронирование | +3 дня | Виза, страховка, карта |
| До экскурсии | Дата экскурсии | -2 дня | Место встречи, что взять |
| После возвращения | Дата экскурсии | +2 дня | Просьба оставить отзыв |

---

## Примеры использования

### Пример 1: Новая экскурсия в Dubai

```markdown
# 114 Джип-сафари по пустыне from Dubai

**Type:** Excursion Card
**Date:** 01.02.2026

---

## Message Text
```
🏜️ Джип-сафари по пустыне

Незабываемое приключение в дюнах Дубая! Профессиональные водители проведут вас по самым впечатляющим местам пустыни.

Продолжительность: 6 часов
Что входит: трансфер, барбекю-ужин, катание на верблюдах, хна, шоу
Цена: от 180 AED
```

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | Оплатить групповой тур | FORM-GT | inline |
| 2 | Оплатить приватный тур | FORM-PT | inline |
| 3 | ⬅ Назад | 100 — Excursions Dubai | inline |
```

### Пример 2: Пустой блок с заглушкой

```markdown
# 870 Restaurants from Dubai

**Type:** Menu (Placeholder)
**Date:** 01.02.2026

---

## Message Text
```
🍽️ Рестораны Дубая

Раздел в разработке.

Для бронирования ресторана, пожалуйста, свяжитесь с менеджером.
```

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | 📞 Связаться с менеджером | Contact block | inline |
| 2 | ⬅ Назад | 010 — Dubai Menu | inline |
```

### Пример 3: Блок лояльности

```markdown
# 961 Как получить скидки

**Type:** Loyalty System
**Date:** 01.02.2026

---

## Message Text
```
🎁 Как получить скидки?

🔹 Скидка 10% — подпишитесь на канал @vipdxbrus
🔹 Скидка 15% — оставьте отзыв на Google Maps
🔹 Скидка 25% — пригласите 3 друзей

Скидки суммируются с баллами лояльности!
```

---

## Buttons

| # | Button Text | Leads to | Type |
|---|------------|----------|------|
| 1 | Подписаться на канал | External link | inline |
| 2 | Оставить отзыв | FORM-REVIEW | inline |
| 3 | Пригласить друзей | Block 962 | inline |
| 4 | ⬅ Назад | Block 960 | inline |
```

---

## Чеклист создания блока

- [ ] ID блока уникален и в правильном диапазоне
- [ ] Текст заполнен (не пустой)
- [ ] Emoji соответствует категории
- [ ] Кнопка "⬅ Назад" присутствует
- [ ] Все кнопки ведут на существующие блоки
- [ ] Переменные используют правильный префикс
- [ ] Документация обновлена

---

**Связанные файлы:**
- `../SKILL.md` — Основная документация
- `troubleshooting.md` — Решение проблем
- `cheatsheet.md` — Быстрая справка
