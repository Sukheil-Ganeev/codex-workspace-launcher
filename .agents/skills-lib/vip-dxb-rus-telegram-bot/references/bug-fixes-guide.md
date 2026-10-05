# Bug Fixes Guide - Руководство по исправлению багов

Полное руководство по исправлению известных багов в боте VIP-DXB-RUS.

---

## Содержание

1. [Критические баги (20)](#критические-баги-20)
2. [Баги высокого приоритета (60+)](#баги-высокого-приоритета-60)
3. [Пошаговые инструкции](#пошаговые-инструкции)
4. [Чеклист проверки](#чеклист-проверки)

---

## Критические баги (20)

**Критический баг** = пользователь застревает без возможности выйти

### Пустые блоки без кнопки "Назад" (16 блоков)

Эти блоки не содержат текста, кнопок и навигации. Пользователь застревает.

| # | Block ID | Категория | Эмират | Статус |
|---|----------|-----------|--------|--------|
| 1 | 850 | Beach Clubs | Dubai | EMPTY |
| 2 | 850 | Beach Clubs | Abu Dhabi | EMPTY |
| 3 | 850 | Beach Clubs | Fujairah | EMPTY |
| 4 | 850 | Beach Clubs | RAK | EMPTY |
| 5 | 860 | Hotels | Dubai | EMPTY |
| 6 | 860 | Hotels | Abu Dhabi | EMPTY |
| 7 | 860 | Hotels | Fujairah | EMPTY |
| 8 | 860 | Hotels | RAK | EMPTY |
| 9 | 870 | Restaurants | Dubai | EMPTY |
| 10 | 870 | Restaurants | Abu Dhabi | EMPTY |
| 11 | 870 | Restaurants | Fujairah | EMPTY |
| 12 | 870 | Restaurants | RAK | EMPTY |
| 13 | 880 | SPA/Wellness | Dubai | EMPTY |
| 14 | 880 | SPA/Wellness | Abu Dhabi | EMPTY |
| 15 | 880 | SPA/Wellness | Fujairah | EMPTY |
| 16 | 880 | SPA/Wellness | RAK | EMPTY |

#### Шаблон исправления для пустых блоков:

```yaml
# [ID] [Category] from [Emirate]

message:
  text: |
    [EMOJI] [Название категории] - [Эмират]

    Раздел находится в разработке.

    Для бронирования, пожалуйста, свяжитесь с менеджером.

buttons:
  - text: "📞 Связаться с менеджером"
    action: contact_manager
  - text: "⬅ Назад"
    screen: [ID меню эмирата]
```

#### Конкретные исправления:

**850-BEACH-CLUBS-DUBAI:**
```yaml
message:
  text: |
    🏖️ Пляжные клубы Дубая

    Раздел в разработке.

    Для бронирования свяжитесь с менеджером.

buttons:
  - text: "📞 Связаться с менеджером"
    action: contact_manager
  - text: "⬅ Назад"
    screen: 010  # Dubai Menu
```

**860-HOTELS-ABU-DHABI:**
```yaml
message:
  text: |
    🏨 Отели Абу-Даби

    Раздел в разработке.

    Для бронирования свяжитесь с менеджером.

buttons:
  - text: "📞 Связаться с менеджером"
    action: contact_manager
  - text: "⬅ Назад"
    screen: 011  # Abu Dhabi Menu
```

**870-RESTAURANTS-RAK:**
```yaml
message:
  text: |
    🍽️ Рестораны Рас-аль-Хаймы

    Раздел в разработке.

    Для бронирования свяжитесь с менеджером.

buttons:
  - text: "📞 Связаться с менеджером"
    action: contact_manager
  - text: "⬅ Назад"
    screen: 012  # RAK Menu
```

**880-SPA-FUJAIRAH:**
```yaml
message:
  text: |
    🧘‍♀️ SPA и Wellness в Фуджейре

    Раздел в разработке.

    Для бронирования свяжитесь с менеджером.

buttons:
  - text: "📞 Связаться с менеджером"
    action: contact_manager
  - text: "⬅ Назад"
    screen: 013  # Fujairah Menu
```

---

### Дополнительные критические баги (4)

| # | Bug | Описание | Приоритет |
|---|-----|----------|-----------|
| 17 | FORM-CRUISE | Форма полностью ПУСТАЯ (0 полей) | CRITICAL |
| 18 | FORM-HOTEL | Форма готова (10 полей), но НЕДОСТУПНА | CRITICAL |
| 19 | 600-PARKS-AD-FUJ | Parks Abu Dhabi (Fujairah) нет кнопки Назад | CRITICAL |
| 20 | 201-JEEP-SAFARI | Jeep Safari Abu Dhabi нет кнопки Назад | CRITICAL |

#### Исправление FORM-CRUISE:

```yaml
# FORM-CRUISE — Круизы по заливу

# Блок 1: Выбор типа круиза
block: FORM-CRUISE-START-900
  message:
    text: |
      🛳️ Круиз по заливу

      Выберите тип круиза:
  buttons:
    - text: "🌆 Вечерний круиз с ужином"
      screen: FORM-CRUISE-DATE-910
      set: cruise_type = "dinner"
    - text: "🌃 Ночной круиз"
      screen: FORM-CRUISE-DATE-910
      set: cruise_type = "night"
    - text: "☀️ Дневной круиз"
      screen: FORM-CRUISE-DATE-910
      set: cruise_type = "day"
    - text: "🔙 Назад"
      screen: MAIN-MENU

# Блок 2: Дата
block: FORM-CRUISE-DATE-910
  message:
    input: true
    text: |
      📅 Выберите дату круиза:
      Формат: ДД.ММ.ГГГГ
  variable_name: cruise_date
  validation:
    regex: "^\\d{2}\\.\\d{2}\\.\\d{4}$"
  buttons:
    - text: "🔙 Назад"
      screen: FORM-CRUISE-START-900

# Блок 3: Количество гостей
block: FORM-CRUISE-GUESTS-920
  message:
    input: true
    text: |
      👥 Количество гостей:
      (максимум 50 человек)
  variable_name: cruise_guests
  validation:
    type: number
    min: 1
    max: 50
  buttons:
    - text: "🔙 Назад"
      screen: FORM-CRUISE-DATE-910

# Блок 4: Имя
block: FORM-CRUISE-NAME-930
  message:
    input: true
    text: "👤 Ваше имя:"
  variable_name: cruise_name
  buttons:
    - text: "🔙 Назад"
      screen: FORM-CRUISE-GUESTS-920

# Блок 5: Телефон
block: FORM-CRUISE-PHONE-940
  message:
    input: true
    text: |
      📱 Номер телефона:
      Формат: +971XXXXXXXXX
  variable_name: cruise_phone
  validation:
    regex: "^\\+971[0-9]{9}$"
  buttons:
    - text: "🔙 Назад"
      screen: FORM-CRUISE-NAME-930

# Блок 6: Проверка
block: FORM-CRUISE-REVIEW-950
  message:
    text: |
      ✅ Проверьте ваш заказ:

      🛳️ Тип: {{cruise_type}}
      📅 Дата: {{cruise_date}}
      👥 Гостей: {{cruise_guests}}
      👤 Имя: {{cruise_name}}
      📱 Телефон: {{cruise_phone}}

      Все верно?
  buttons:
    - text: "✏️ Редактировать"
      screen: FORM-CRUISE-DATE-910
    - text: "✅ Подтвердить"
      screen: FORM-CRUISE-SUBMIT-960

# Блок 7: Отправка
block: FORM-CRUISE-SUBMIT-960
  message:
    text: |
      🎉 Заявка отправлена!
      Наш менеджер свяжется с вами в течение 15 минут.
  actions:
    - type: send_to_admin
      message: "Новая заявка на круиз: {{cruise_type}}, {{cruise_date}}"
  buttons:
    - text: "🏠 Главное меню"
      screen: MAIN-MENU
```

#### Переменные FORM-CRUISE:

```yaml
variables:
  - cruise_type      # dinner/night/day
  - cruise_date      # DD.MM.YYYY
  - cruise_guests    # 1-50
  - cruise_name      # string
  - cruise_phone     # +971XXXXXXXXX
```

#### Исправление 600-PARKS-AD-FUJ (добавить кнопку Назад):

```yaml
# Было:
buttons:
  - text: "🎢 Ferrari World"
    screen: 601
  - text: "🦸 Warner Bros"
    screen: 602

# Стало:
buttons:
  - text: "🎢 Ferrari World"
    screen: 601
  - text: "🦸 Warner Bros"
    screen: 602
  - text: "⬅ Назад"      # ДОБАВЛЕНО
    screen: 013          # Fujairah Menu
```

#### Исправление 201-JEEP-SAFARI (добавить кнопку Назад):

```yaml
# Добавить кнопку:
buttons:
  - text: "Оплатить групповой тур"
    screen: FORM-GT
  - text: "Оплатить приватный тур"
    screen: FORM-PT
  - text: "⬅ Назад"      # ДОБАВЛЕНО
    screen: 200          # Abu Dhabi Excursions Menu
```

---

## Баги высокого приоритета (60+)

### 1. Water Activities без кнопки бронирования (13 блоков)

| # | Block ID | Название | Проблема | Решение |
|---|----------|----------|----------|---------|
| 1 | 710 | Flyboard Dubai | Нет кнопки | + FORM-TICKETS |
| 2 | 711 | Jet Ski Dubai | Нет кнопки | + FORM-TICKETS |
| 3 | 712 | Parasailing Dubai | Нет кнопки | + FORM-TICKETS |
| 4 | 713 | Wakeboarding Dubai | Нет кнопки | + FORM-TICKETS |
| 5 | 714 | Banana Boat Dubai | Нет кнопки | + FORM-TICKETS |
| 6 | 715 | Kayaking Dubai | Нет кнопки | + FORM-TICKETS |
| 7 | 716 | Paddle Board Dubai | Нет кнопки | + FORM-TICKETS |
| 8 | 720 | Flyboard Abu Dhabi | Нет кнопки | + FORM-TICKETS |
| 9 | 721 | Jet Ski Abu Dhabi | Нет кнопки | + FORM-TICKETS |
| 10 | 730 | Snorkeling Fujairah | Нет кнопки | + FORM-TICKETS |
| 11 | 731 | Diving Fujairah | Нет кнопки | + FORM-TICKETS |
| 12 | 732 | Fishing Fujairah | Нет кнопки | + FORM-TICKETS |
| 13 | 733 | Kayaking Fujairah | Нет кнопки | + FORM-TICKETS |

**Шаблон исправления:**
```yaml
buttons:
  - text: "🎫 Забронировать"
    screen: FORM-TICKETS
    set: ticket_attraction = "[Название активности]"
  - text: "⬅ Назад"
    screen: [ID меню водных активностей]
```

---

### 2. Cruises & Yachts без контента (10 блоков)

| # | Block ID | Название | Проблема | Решение |
|---|----------|----------|----------|---------|
| 1 | 700 | Dhow Cruise Dubai Creek | Пустой | Заполнить + FORM-CRUISE |
| 2 | 701 | Dhow Cruise Marina | Пустой | Заполнить + FORM-CRUISE |
| 3 | 702 | Luxury Yacht Dubai | Пустой | Заполнить + FORM-YACHT |
| 4 | 703 | Speed Boat Tour | Пустой | Заполнить + FORM-YACHT |
| 5 | 704 | Yellow Boat Tour | Пустой | Заполнить + FORM-TICKETS |
| 6 | 705 | Catamaran Cruise | Пустой | Заполнить + FORM-CRUISE |
| 7 | 706 | Fishing Trip Dubai | Пустой | Заполнить + FORM-TICKETS |
| 8 | 707 | Sunset Yacht | Пустой | Заполнить + FORM-YACHT |
| 9 | 708 | Party Yacht | Пустой | Заполнить + FORM-YACHT |
| 10 | 709 | Private Yacht | Пустой | Заполнить + FORM-YACHT |

**Шаблон контента для круиза:**
```yaml
message:
  text: |
    ⛵️ [Название круиза]

    [Описание маршрута и особенностей, 2-3 предложения]

    Продолжительность: [X часов]
    Включено: [еда, напитки, развлечения]
    Цена: от [X] AED

buttons:
  - text: "🎫 Забронировать"
    screen: FORM-CRUISE  # или FORM-YACHT для яхт
  - text: "⬅ Назад"
    screen: 700  # Cruises Menu
```

---

### 3. Dubai Parks без кнопки покупки билетов (17 блоков)

| # | Block ID | Название | Форма |
|---|----------|----------|-------|
| 1 | 501 | Burj Khalifa At The Top | FORM-TICKETS |
| 2 | 502 | Dubai Frame | FORM-TICKETS |
| 3 | 503 | Museum of the Future | FORM-TICKETS |
| 4 | 504 | Dubai Aquarium | FORM-TICKETS |
| 5 | 505 | Madame Tussauds | FORM-TICKETS |
| 6 | 510 | IMG Worlds | FORM-TICKETS |
| 7 | 511 | Legoland | FORM-TICKETS |
| 8 | 512 | Motiongate | FORM-TICKETS |
| 9 | 513 | Bollywood Parks | FORM-TICKETS |
| 10 | 520 | Aquaventure | FORM-TICKETS |
| 11 | 521 | Wild Wadi | FORM-TICKETS |
| 12 | 530 | Dubai Safari | FORM-TICKETS |
| 13 | 531 | Green Planet | FORM-TICKETS |
| 14 | 540 | Ski Dubai | FORM-TICKETS |
| 15 | 550 | Global Village | FORM-TICKETS |
| 16 | 551 | Miracle Garden | FORM-TICKETS |
| 17 | 552 | Glow Garden | FORM-TICKETS |

**Шаблон добавления кнопки:**
```yaml
buttons:
  - text: "🎫 Купить билеты"
    screen: FORM-TICKETS
    set: ticket_attraction = "[Название парка]"
  - text: "⬅ Назад"
    screen: 500  # Dubai Parks Menu
```

---

### 4. Abu Dhabi Parks без кнопки покупки билетов (14 блоков)

| # | Block ID | Название | Форма |
|---|----------|----------|-------|
| 1 | 601 | Ferrari World | FORM-TICKETS |
| 2 | 602 | Warner Bros World | FORM-TICKETS |
| 3 | 603 | Yas Waterworld | FORM-TICKETS |
| 4 | 604 | SeaWorld | FORM-TICKETS |
| 5 | 605 | Louvre Abu Dhabi | FORM-TICKETS |
| 6 | 606 | Qasr Al Watan | FORM-TICKETS |
| 7 | 607 | Sheikh Zayed Mosque | FORM-TICKETS |
| 8 | 608 | Emirates Park Zoo | FORM-TICKETS |
| 9 | 609 | Mangrove Kayaking | FORM-TICKETS |
| 10 | 610 | CLYMB | FORM-TICKETS |
| 11 | 611 | Yas Kartzone | FORM-TICKETS |
| 12 | 612 | Yas Links Golf | FORM-TICKETS |
| 13 | 613 | Yas Marina | FORM-TICKETS |
| 14 | 614 | Al Wathba Reserve | FORM-TICKETS |

---

### 5. Buggy без контента (3 блока)

| # | Block ID | Название | Проблема |
|---|----------|----------|----------|
| 1 | 810 | Buggy Dubai | Не заполнен |
| 2 | 811 | Buggy Sharjah | Не заполнен |
| 3 | 812 | Buggy RAK | Не заполнен |

**Шаблон контента:**
```yaml
message:
  text: |
    🏜 Багги-сафари [Локация]

    Захватывающая поездка по дюнам пустыни! Выбирайте
    транспорт и продолжительность по своему вкусу.

    Транспорт: Buggy 2/4-seat, Quad
    Модели: PRO Can-Am / Standard Polaris
    Время: Sunset/Morning/Day

    Цена: от [X] AED

buttons:
  - text: "🎫 Забронировать"
    screen: FORM-BUGGY
  - text: "⬅ Назад"
    screen: 800  # Activities Menu
```

---

### 6. Pools без кнопки бронирования (3 из 4)

| # | Block ID | Название | Проблема |
|---|----------|----------|----------|
| 1 | 821 | Cloud 22 | Нет кнопки |
| 2 | 822 | Address Sky View | Нет кнопки |
| 3 | 823 | FIVE Palm | Нет кнопки |

**Исправление (добавить кнопку):**
```yaml
buttons:
  - text: "🎫 Забронировать сессию"
    screen: FORM-POOL
    set: pool_venue_name = "[Название]"
  - text: "⬅ Назад"
    screen: 820  # Pools Menu
```

---

## Пошаговые инструкции

### Как добавить кнопку "Назад"

**Шаг 1:** Найти блок в конструкторе
```
ID блока → Найти в дереве навигации
```

**Шаг 2:** Определить родительский блок
```
Откуда пользователь пришел? → Это и есть цель кнопки "Назад"
```

**Шаг 3:** Добавить кнопку
```yaml
buttons:
  # ... существующие кнопки ...
  - text: "⬅ Назад"
    screen: [ID родительского блока]
```

**Шаг 4:** Протестировать
```
Пройти путь: Main Menu → Категория → Блок → Назад
Убедиться, что возврат работает
```

---

### Как заполнить пустой блок

**Шаг 1:** Определить категорию блока
```
850 = Beach Clubs
860 = Hotels
870 = Restaurants
880 = SPA
```

**Шаг 2:** Выбрать шаблон из `block-templates.md`

**Шаг 3:** Заполнить шаблон
```yaml
message:
  text: |
    [EMOJI] [Название]

    [Описание или placeholder]

buttons:
  - text: "[Действие]"
    screen: [FORM или контакт]
  - text: "⬅ Назад"
    screen: [ID меню эмирата]
```

**Шаг 4:** Добавить в конструктор

**Шаг 5:** Протестировать навигацию

---

### Как добавить форму бронирования

**Шаг 1:** Определить подходящую форму
```
Экскурсии → FORM-GT / FORM-PT
Парки → FORM-TICKETS
Водные → FORM-TICKETS
Яхты → FORM-YACHT
Круизы → FORM-CRUISE
Багги → FORM-BUGGY
Бассейны → FORM-POOL
Пляжи → FORM-BEACH
SPA → FORM-SPA
Рестораны → FORM-REST
Трансфер → FORM-TRANSFER
```

**Шаг 2:** Добавить кнопку с предустановкой переменной
```yaml
- text: "🎫 Забронировать"
  screen: FORM-TICKETS
  set: ticket_attraction = "Ferrari World"
```

**Шаг 3:** Убедиться, что форма существует и работает

---

### Как создать форму с нуля

**Шаг 1:** Определить поля (см. `block-templates.md`)

**Шаг 2:** Выбрать префикс переменных
```
Новая форма → новый префикс (например, cruise_)
```

**Шаг 3:** Создать цепочку блоков
```
START → DATE → GUESTS → NAME → PHONE → REVIEW → SUBMIT
```

**Шаг 4:** Добавить кнопки "Назад" на каждый шаг

**Шаг 5:** Настроить отправку админу

**Шаг 6:** Добавить переменные в документацию

---

## Чеклист проверки

### После исправления критического бага

- [ ] Блок содержит текст (не пустой)
- [ ] Есть кнопка "⬅ Назад"
- [ ] Кнопка "Назад" ведет на правильный родительский блок
- [ ] Протестирован путь туда и обратно
- [ ] Задокументировано исправление

### После добавления кнопки бронирования

- [ ] Кнопка присутствует
- [ ] Кнопка ведет на правильную форму
- [ ] Переменная предустановлена (если нужно)
- [ ] Форма принимает данные
- [ ] Уведомление уходит админу
- [ ] Пользователь получает подтверждение

### После заполнения пустого блока

- [ ] Текст соответствует категории
- [ ] Emoji соответствует контенту
- [ ] Есть кнопка действия (бронирование/контакт)
- [ ] Есть кнопка "Назад"
- [ ] Навигация работает

### Еженедельная проверка

- [ ] Все 16 пустых блоков эмиратов (850-880) исправлены
- [ ] FORM-CRUISE заполнена
- [ ] FORM-HOTEL доступна
- [ ] Все блоки имеют кнопку "Назад"
- [ ] Все услуги имеют кнопку бронирования

---

## Приоритеты исправления

### Неделя 1: Критические (20 багов)
1. Добавить "Назад" в 16 пустых блоков эмиратов
2. Заполнить FORM-CRUISE
3. Сделать FORM-HOTEL доступной
4. Исправить 600-PARKS-AD-FUJ
5. Исправить 201-JEEP-SAFARI

### Неделя 2: Water Activities (13 блоков)
1. Добавить FORM-TICKETS к 710-716 (Dubai)
2. Добавить FORM-TICKETS к 720-721 (Abu Dhabi)
3. Добавить FORM-TICKETS к 730-733 (Fujairah)

### Неделя 3: Parks (31 блок)
1. Dubai Parks (17 блоков) — добавить FORM-TICKETS
2. Abu Dhabi Parks (14 блоков) — добавить FORM-TICKETS

### Неделя 4: Остальное
1. Cruises & Yachts (10 блоков) — заполнить контент
2. Buggy (3 блока) — заполнить контент
3. Pools (3 блока) — добавить FORM-POOL

---

## Метрики успеха

| Метрика | До | После | Цель |
|---------|-----|-------|------|
| Критических багов | 20 | 0 | 0 |
| Блоков без "Назад" | 40+ | 0 | 0 |
| Услуг без бронирования | 60+ | 0 | 0 |
| Пустых форм | 1 | 0 | 0 |
| Недоступных форм | 1 | 0 | 0 |

---

**Связанные файлы:**
- `../SKILL.md` — Основная документация
- `block-templates.md` — Шаблоны блоков
- `troubleshooting.md` — Решение проблем
- `cheatsheet.md` — Быстрая справка
