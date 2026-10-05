# Form Fields Reference - Справка по полям форм

Детальная документация всех 110 полей форм VIP-DXB-RUS бота.

---

## Структура справки

Каждое поле описано по схеме:
- **Переменная** - имя переменной для хранения
- **Тип** - тип данных (text, number, date, phone, email)
- **Валидация** - правила проверки
- **Обязательное** - да/нет
- **Примеры** - корректные значения

---

## FORM-GT (Групповая экскурсия) - 7 полей

### GT-DATE - Дата экскурсии

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_date` |
| **Блок** | FORM-GT-DATE-350 |
| **Тип** | date |
| **Формат** | DD.MM.YYYY |
| **Валидация** | regex: `^\d{2}\.\d{2}\.\d{4}$` |
| **Диапазон** | от today до +6 месяцев |
| **Обязательное** | Да |
| **Примеры** | `25.12.2024`, `01.01.2025` |

**Правило:**
```yaml
validation:
  regex: "^\\d{2}\\.\\d{2}\\.\\d{4}$"
  min_date: "today"
  max_date: "+6 months"
  error: "Некорректная дата. Формат: ДД.ММ.ГГГГ"
```

---

### GT-TIME - Время экскурсии

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_time` |
| **Блок** | FORM-GT-TIME-360 |
| **Тип** | text (selection) |
| **Формат** | HH:MM или период дня |
| **Валидация** | один из: morning, afternoon, evening, custom |
| **Обязательное** | Да |
| **Примеры** | `morning` (08:00-12:00), `14:30`, `evening` (17:00-21:00) |

**Варианты выбора:**
```yaml
options:
  - value: "morning"
    label: "🌅 Утро (08:00-12:00)"
  - value: "afternoon"
    label: "☀️ День (12:00-17:00)"
  - value: "evening"
    label: "🌆 Вечер (17:00-21:00)"
  - value: "custom"
    label: "🕒 Свое время"
```

---

### GT-GUESTS - Количество гостей

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_guests` |
| **Блок** | FORM-GT-GUESTS-370 |
| **Тип** | number |
| **Валидация** | min: 1, max: 50 |
| **Обязательное** | Да |
| **Примеры** | `2`, `4`, `10`, `25` |

**Правило:**
```yaml
validation:
  type: number
  min: 1
  max: 50
  error: "Количество гостей: от 1 до 50"
```

---

### GT-NAME - Имя контактного лица

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_name` |
| **Блок** | FORM-GT-NAME-375 |
| **Тип** | text |
| **Валидация** | min_length: 2, max_length: 100 |
| **Обязательное** | Да |
| **Примеры** | `Иван`, `John Smith`, `محمد` |

**Правило:**
```yaml
validation:
  min_length: 2
  max_length: 100
  error: "Имя должно содержать от 2 до 100 символов"
```

---

### GT-PHONE - Номер телефона

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_phone` |
| **Блок** | FORM-GT-PHONE-380 |
| **Тип** | phone |
| **Формат** | +971XXXXXXXXX |
| **Валидация** | regex для ОАЭ номеров |
| **Обязательное** | Да |
| **Примеры** | `+971501234567`, `+971 50 123 4567`, `0501234567` |

**Правило:**
```yaml
validation:
  regex: "^(\\+971|00971|0)?[0-9\\s]{9,12}$"
  error: "Неверный формат. Используйте: +971XXXXXXXXX"
```

**Принимаемые форматы:**
- `+971501234567` - полный международный
- `+971 50 123 4567` - с пробелами
- `00971501234567` - альтернативный код
- `0501234567` - локальный
- `050 123 4567` - локальный с пробелами

---

### GT-HOTEL - Название отеля

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_hotel` |
| **Блок** | FORM-GT-HOTEL-385 |
| **Тип** | text |
| **Валидация** | optional, max_length: 200 |
| **Обязательное** | Нет |
| **Примеры** | `Burj Al Arab`, `Atlantis The Palm`, `JW Marriott Marquis` |

**Правило:**
```yaml
validation:
  optional: true
  max_length: 200
```

---

### GT-COMMENTS - Дополнительные пожелания

| Параметр | Значение |
|----------|----------|
| **Переменная** | `gt_comments` |
| **Блок** | FORM-GT-COMMENTS-390 |
| **Тип** | text (multiline) |
| **Валидация** | optional, max_length: 1000 |
| **Обязательное** | Нет |
| **Примеры** | `Нужны детские кресла`, `Vegetarian meals please` |

**Правило:**
```yaml
validation:
  optional: true
  max_length: 1000
  multiline: true
```

---

## FORM-PT (Приватная экскурсия) - 7 полей

### PT-DATE - Дата экскурсии

| Параметр | Значение |
|----------|----------|
| **Переменная** | `pt_date` |
| **Блок** | FORM-PT-DATE-450 |
| **Тип** | date |
| **Формат** | DD.MM.YYYY |
| **Валидация** | Аналогично GT-DATE |
| **Обязательное** | Да |
| **Примеры** | `25.12.2024` |

*(Все параметры идентичны GT-DATE)*

---

### PT-TIME - Время экскурсии

| Параметр | Значение |
|----------|----------|
| **Переменная** | `pt_time` |
| **Блок** | FORM-PT-TIME-460 |
| **Тип** | text |
| **Валидация** | Аналогично GT-TIME |
| **Обязательное** | Да |

*(Все параметры идентичны GT-TIME)*

---

### PT-GUESTS - Количество гостей

| Параметр | Значение |
|----------|----------|
| **Переменная** | `pt_guests` |
| **Блок** | FORM-PT-GUESTS-470 |
| **Тип** | number |
| **Валидация** | min: 1, max: 20 (меньше чем у GT) |
| **Обязательное** | Да |
| **Примеры** | `2`, `4`, `8` |

**Отличие от GT:**
```yaml
validation:
  max: 20  # Приватные туры - меньше участников
```

---

### PT-NAME, PT-PHONE, PT-HOTEL, PT-COMMENTS

Идентичны GT версиям (см. выше), используют префикс `pt_` вместо `gt_`.

---

## FORM-BUGGY (Багги тур) - 9 полей

### BUGGY-DATE - Дата багги тура

| Параметр | Значение |
|----------|----------|
| **Переменная** | `buggy_date` |
| **Блок** | FORM-BUGGY-DATE-530 |
| **Тип** | date |
| **Формат** | DD.MM.YYYY |
| **Валидация** | Стандартная для дат |
| **Обязательное** | Да |

---

### BUGGY-TIME - Время тура

| Параметр | Значение |
|----------|----------|
| **Переменная** | `buggy_time` |
| **Блок** | FORM-BUGGY-TIME-540 |
| **Тип** | text (selection) |
| **Варианты** | morning, afternoon, sunset |
| **Обязательное** | Да |
| **Примеры** | `morning` (06:00-10:00), `sunset` (16:00-19:00) |

**Особенность:**
```yaml
options:
  - value: "morning"
    label: "🌅 Утренний тур (06:00-10:00)"
    recommended: true  # Лучшее время
  - value: "afternoon"
    label: "☀️ Дневной (10:00-16:00)"
    warning: "Очень жарко летом"
  - value: "sunset"
    label: "🌆 На закате (16:00-19:00)"
    premium: true  # Более дорогой
```

---

### BUGGY-PARTICIPANTS - Количество участников

| Параметр | Значение |
|----------|----------|
| **Переменная** | `buggy_participants` |
| **Блок** | FORM-BUGGY-PARTICIPANTS-550 |
| **Тип** | number |
| **Валидация** | min: 1, max: 10 |
| **Обязательное** | Да |
| **Примеры** | `2`, `4`, `6` |

**Примечание:**
Обычно багги вмещает 2 человека, поэтому количество участников влияет на количество багги.

---

### BUGGY-EXPERIENCE - Уровень опыта

| Параметр | Значение |
|----------|----------|
| **Переменная** | `buggy_experience` |
| **Блок** | FORM-BUGGY-EXPERIENCE-560 |
| **Тип** | text (selection) |
| **Варианты** | beginner, intermediate, advanced |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "beginner"
    label: "🟢 Новичок (первый раз)"
  - value: "intermediate"
    label: "🟡 Есть опыт (несколько раз)"
  - value: "advanced"
    label: "🔴 Продвинутый (регулярно катаюсь)"
```

**Влияет на:**
- Сложность маршрута
- Скорость движения
- Длительность инструктажа

---

### BUGGY-INSURANCE - Страховка

| Параметр | Значение |
|----------|----------|
| **Переменная** | `buggy_insurance` |
| **Блок** | FORM-BUGGY-INSURANCE-565 |
| **Тип** | boolean |
| **Варианты** | yes, no |
| **Обязательное** | Да |
| **Примеры** | `yes`, `no` |

**Дополнительная информация:**
```yaml
insurance_info:
  basic: "Включена в стоимость"
  premium:
    cost: "+100 AED"
    coverage: "Полное покрытие ущерба"
```

---

### BUGGY-NAME, BUGGY-PHONE, BUGGY-HOTEL, BUGGY-COMMENTS

Аналогичны GT/PT версиям с префиксом `buggy_`.

---

## FORM-RENT (Аренда авто) - 11 полей

### RENT-START-DATE - Дата начала аренды

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_start_date` |
| **Блок** | FORM-RENT-START-DATE-800 |
| **Тип** | date |
| **Формат** | DD.MM.YYYY |
| **Валидация** | min: today |
| **Обязательное** | Да |

---

### RENT-END-DATE - Дата окончания аренды

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_end_date` |
| **Блок** | FORM-RENT-END-DATE-810 |
| **Тип** | date |
| **Формат** | DD.MM.YYYY |
| **Валидация** | min: rent_start_date + 1 день |
| **Обязательное** | Да |

**Правило:**
```yaml
validation:
  min: "{{rent_start_date}} + 1 day"
  max: "{{rent_start_date}} + 30 days"
  error: "Минимум 1 день, максимум 30 дней"
```

---

### RENT-CAR-CLASS - Класс автомобиля

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_car_class` |
| **Блок** | FORM-RENT-CAR-CLASS-820 |
| **Тип** | text (selection) |
| **Варианты** | economy, comfort, business, luxury, suv, sports |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "economy"
    label: "🚗 Эконом (от 100 AED/день)"
    examples: "Toyota Yaris, Nissan Sunny"

  - value: "comfort"
    label: "🚙 Комфорт (от 150 AED/день)"
    examples: "Toyota Camry, Honda Accord"

  - value: "business"
    label: "💼 Бизнес (от 250 AED/день)"
    examples: "BMW 5 Series, Mercedes E-Class"

  - value: "luxury"
    label: "💎 Люкс (от 500 AED/день)"
    examples: "Mercedes S-Class, BMW 7 Series"

  - value: "suv"
    label: "🚙 SUV (от 200 AED/день)"
    examples: "Toyota Land Cruiser, Nissan Patrol"

  - value: "sports"
    label: "🏎️ Спорткар (от 1000 AED/день)"
    examples: "Ferrari, Lamborghini, Porsche"
```

---

### RENT-TRANSMISSION - Тип коробки передач

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_transmission` |
| **Блок** | FORM-RENT-TRANSMISSION-825 |
| **Тип** | text (selection) |
| **Варианты** | automatic, manual, any |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "automatic"
    label: "⚙️ Автомат"
  - value: "manual"
    label: "🔧 Механика"
  - value: "any"
    label: "❓ Любая"
```

---

### RENT-EMIRATE - Эмират назначения

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_emirate` |
| **Блок** | FORM-RENT-EMIRATES-840 |
| **Тип** | text (selection) |
| **Варианты** | dubai, abu_dhabi, sharjah, ajman, fujairah, ras_al_khaimah, umm_al_quwain |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "dubai"
    label: "🏙️ Дубай"
  - value: "abu_dhabi"
    label: "🕌 Абу-Даби"
  - value: "sharjah"
    label: "🏛️ Шарджа"
  - value: "ajman"
    label: "🏖️ Аджман"
  - value: "fujairah"
    label: "⛰️ Фуджейра"
  - value: "ras_al_khaimah"
    label: "🏔️ Рас-эль-Хайма"
  - value: "umm_al_quwain"
    label: "🌊 Умм-эль-Кайвайн"
```

---

### RENT-DRIVER - Нужен водитель

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_driver` |
| **Блок** | FORM-RENT-DRIVER-890 |
| **Тип** | boolean |
| **Варианты** | yes, no |
| **Обязательное** | Да |

**Дополнительная информация:**
```yaml
driver_options:
  with_driver:
    cost: "+300 AED/день"
    includes: "Водитель 10 часов/день"

  self_drive:
    requirements:
      - "Международные права"
      - "Возраст 21+"
      - "Опыт вождения 1+ год"
```

---

### RENT-INSURANCE-TYPE - Тип страховки

| Параметр | Значение |
|----------|----------|
| **Переменная** | `rent_insurance_type` |
| **Блок** | FORM-RENT-INSURANCE-895 |
| **Тип** | text (selection) |
| **Варианты** | basic, standard, premium |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "basic"
    label: "🔵 Базовая (включена)"
    coverage: "ДТП с участием других авто"

  - value: "standard"
    label: "🟡 Стандартная (+50 AED/день)"
    coverage: "ДТП + угон + стихия"

  - value: "premium"
    label: "🟢 Премиум (+100 AED/день)"
    coverage: "Полное покрытие без франшизы"
```

---

### RENT-NAME, RENT-PHONE, RENT-HOTEL, RENT-COMMENTS

Аналогичны другим формам с префиксом `rent_`.

---

## FORM-QUAD (Квадроцикл) - 8 полей

### QUAD-DATE, QUAD-TIME, QUAD-PARTICIPANTS

Аналогичны BUGGY версиям с префиксом `quad_`.

---

### QUAD-DURATION - Длительность

| Параметр | Значение |
|----------|----------|
| **Переменная** | `quad_duration` |
| **Блок** | FORM-QUAD-DURATION-640 |
| **Тип** | text (selection) |
| **Варианты** | 1h, 2h, 4h, full_day |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "1h"
    label: "⏱️ 1 час (250 AED)"
  - value: "2h"
    label: "⏱️ 2 часа (400 AED)"
  - value: "4h"
    label: "⏱️ 4 часа (700 AED)"
  - value: "full_day"
    label: "☀️ Полный день (1200 AED)"
```

---

### QUAD-EXPERIENCE, QUAD-INSURANCE

Аналогичны BUGGY версиям с префиксом `quad_`.

---

### QUAD-NAME, QUAD-PHONE, QUAD-COMMENTS

Стандартные поля с префиксом `quad_`.

---

## FORM-JETSKI (Гидроцикл) - 8 полей

### JETSKI-DATE - Дата

| Параметр | Значение |
|----------|----------|
| **Переменная** | `jetski_date` |
| **Блок** | FORM-JETSKI-DATE-710 |
| **Тип** | date |
| **Валидация** | Стандартная + проверка погоды |
| **Обязательное** | Да |

**Особенность:**
```yaml
validation:
  weather_check: true  # Проверить прогноз погоды
  min_conditions:
    wind: "< 25 km/h"
    waves: "< 1.5m"
```

---

### JETSKI-TIME - Время

| Параметр | Значение |
|----------|----------|
| **Переменная** | `jetski_time` |
| **Блок** | FORM-JETSKI-TIME-720 |
| **Тип** | text (selection) |
| **Варианты** | morning, afternoon |
| **Обязательное** | Да |

**Примечание:**
Вечерние катания не доступны из-за ограничений безопасности.

---

### JETSKI-PARTICIPANTS - Участники

| Параметр | Значение |
|----------|----------|
| **Переменная** | `jetski_participants` |
| **Блок** | FORM-JETSKI-PARTICIPANTS-730 |
| **Тип** | number |
| **Валидация** | min: 1, max: 6 |
| **Обязательное** | Да |

**Примечание:**
На одном гидроцикле обычно 1-2 человека.

---

### JETSKI-DURATION - Длительность

| Параметр | Значение |
|----------|----------|
| **Переменная** | `jetski_duration` |
| **Блок** | FORM-JETSKI-DURATION-740 |
| **Тип** | text (selection) |
| **Варианты** | 30min, 1h, 2h |
| **Обязательное** | Да |

**Варианты:**
```yaml
options:
  - value: "30min"
    label: "⏱️ 30 минут (200 AED)"
  - value: "1h"
    label: "⏱️ 1 час (350 AED)"
  - value: "2h"
    label: "⏱️ 2 часа (600 AED)"
```

---

### JETSKI-EXPERIENCE - Опыт

| Параметр | Значение |
|----------|----------|
| **Переменная** | `jetski_experience` |
| **Блок** | FORM-JETSKI-EXPERIENCE-750 |
| **Тип** | text (selection) |
| **Варианты** | none, basic, advanced |
| **Обязательное** | Да |

**Влияет на:**
- Зона катания (новички - ближе к берегу)
- Инструктаж (новичкам - полный)
- Максимальная скорость

---

### JETSKI-INSURANCE, JETSKI-NAME, JETSKI-PHONE, JETSKI-COMMENTS

Стандартные поля с префиксом `jetski_`.

---

## FORM-CRUISE (Круиз) - 0 полей (ПУСТАЯ)

**Статус:** Форма не реализована

**Требуется создать следующие поля:**

1. **cruise_type** - Тип круиза
   - dinner (ужин)
   - night (ночной)
   - day (дневной)

2. **cruise_date** - Дата круиза

3. **cruise_guests** - Количество гостей

4. **cruise_cabin** - Каюта (опционально)
   - standard
   - vip
   - premium

5. **cruise_name, cruise_phone, cruise_comments** - Стандартные поля

**См. troubleshooting.md для решения.**

---

## Системные поля (используются везде)

### USER_ID - ID пользователя Telegram

| Параметр | Значение |
|----------|----------|
| **Переменная** | `user_id` |
| **Тип** | number (integer) |
| **Источник** | Telegram API |
| **Обязательное** | Автоматически |
| **Примеры** | `123456789` |

---

### USERNAME - Username пользователя

| Параметр | Значение |
|----------|----------|
| **Переменная** | `username` |
| **Тип** | text |
| **Источник** | Telegram API |
| **Обязательное** | Нет (не у всех есть) |
| **Примеры** | `@john_doe` |

---

### FIRST_NAME - Имя из профиля Telegram

| Параметр | Значение |
|----------|----------|
| **Переменная** | `first_name` |
| **Тип** | text |
| **Источник** | Telegram API |
| **Обязательное** | Автоматически |
| **Примеры** | `John`, `Иван` |

---

### LAST_NAME - Фамилия из профиля

| Параметр | Значение |
|----------|----------|
| **Переменная** | `last_name` |
| **Тип** | text |
| **Источник** | Telegram API |
| **Обязательное** | Нет |
| **Примеры** | `Smith`, `Иванов` |

---

### LANGUAGE - Язык пользователя

| Параметр | Значение |
|----------|----------|
| **Переменная** | `language` |
| **Тип** | text (ISO 639-1) |
| **Источник** | Telegram API или выбор пользователя |
| **Обязательное** | Да (по умолчанию ru) |
| **Примеры** | `ru`, `en`, `ar` |

---

### TIMESTAMP - Время заполнения

| Параметр | Значение |
|----------|----------|
| **Переменная** | `timestamp` |
| **Тип** | datetime (ISO 8601) |
| **Источник** | Автоматически |
| **Обязательное** | Да |
| **Примеры** | `2024-12-25T14:30:00Z` |

---

## Сводная таблица всех полей

| Форма | Количество полей | Обязательных | Опциональных |
|-------|------------------|--------------|--------------|
| FORM-GT | 7 | 5 | 2 |
| FORM-PT | 7 | 5 | 2 |
| FORM-BUGGY | 9 | 7 | 2 |
| FORM-RENT | 11 | 9 | 2 |
| FORM-QUAD | 8 | 6 | 2 |
| FORM-JETSKI | 8 | 6 | 2 |
| FORM-CRUISE | 0 | 0 | 0 |
| **ИТОГО** | **50** | **38** | **12** |

**+ Системные поля:** 6

**Всего уникальных переменных:** 56

---

## Типы данных - Детали валидации

### Тип: DATE

**Форматы:**
- DD.MM.YYYY (основной)
- YYYY-MM-DD (ISO альтернатива)

**Валидация:**
```yaml
type: date
format: "DD.MM.YYYY"
regex: "^\\d{2}\\.\\d{2}\\.\\d{4}$"

# Дополнительно:
min_date: "today"  # Не раньше сегодня
max_date: "+6 months"  # Не позже 6 месяцев

# Исключения:
exclude_dates:
  - "25.12.2024"  # Рождество
  - "01.01.2025"  # Новый год

# Только определенные дни недели:
allowed_weekdays: [1, 2, 3, 4, 5]  # Пн-Пт
```

---

### Тип: PHONE

**Форматы для ОАЭ:**
```yaml
type: phone
country: "AE"  # ОАЭ
regex: "^(\\+971|00971|0)?[0-9\\s]{9,12}$"

# Автонормализация:
normalize: true  # +971501234567

# Проверка оператора:
validate_operator: true
allowed_operators:
  - "50"  # Etisalat
  - "52"  # Du
  - "54"  # Etisalat
  - "55"  # Du
  - "56"  # Etisalat
  - "58"  # Du
```

---

### Тип: NUMBER

**Валидация:**
```yaml
type: number
subtype: integer  # или float

# Диапазон:
min: 1
max: 50

# Кратность:
step: 1  # Только целые числа
# или
step: 0.5  # С шагом 0.5

# Специальные значения:
allow_zero: false
positive_only: true
```

---

### Тип: TEXT

**Валидация:**
```yaml
type: text
min_length: 2
max_length: 100

# Паттерн:
regex: "^[А-Яа-яA-Za-z\\s]+$"  # Только буквы

# Запрещенные символы:
forbidden_chars: ["<", ">", "&", "\""]

# Тримминг:
trim: true  # Убрать пробелы по краям
```

---

### Тип: SELECTION

**Варианты выбора:**
```yaml
type: selection
multiple: false  # Одиночный выбор

options:
  - value: "option1"
    label: "Опция 1"
    enabled: true

  - value: "option2"
    label: "Опция 2"
    enabled: false  # Недоступна
    reason: "Временно недоступно"

# Или динамические:
options_source: "api/get-available-times"
```

---

### Тип: BOOLEAN

**Представление:**
```yaml
type: boolean

# Варианты отображения:
display: buttons  # Кнопки "Да" / "Нет"
# или
display: toggle  # Переключатель
# или
display: checkbox  # Чекбокс

# Значения:
true_value: "yes"
false_value: "no"
default: false
```

---

## Правила валидации - Приоритеты

1. **Обязательность** - проверяется первой
2. **Тип данных** - соответствие типу
3. **Формат** - regex паттерн
4. **Диапазон** - min/max значения
5. **Бизнес-правила** - специфичные проверки

**Пример каскадной валидации:**
```yaml
# 1. Обязательно ли поле?
required: true

# 2. Правильный ли тип?
type: number

# 3. Соответствует ли формату?
regex: "^[0-9]+$"

# 4. В допустимом диапазоне?
min: 1
max: 50

# 5. Бизнес-правило
custom_validation: |
  if (value > 10) {
    require_field("group_name")  # Если больше 10 - нужно имя группы
  }
```

---

## Условная валидация

**Зависимость полей:**
```yaml
# Поле "Водитель" влияет на "Права"
block: FORM-RENT-DRIVER-LICENSE-892
  visible_if: "rent_driver == 'no'"  # Показать только если без водителя

  message:
    input: true
    text: "Номер водительских прав:"

  variable_name: rent_driver_license

  validation:
    required: true  # Обязательно если visible
    regex: "^[A-Z0-9]{6,15}$"
```

**Динамические правила:**
```yaml
# Максимум гостей зависит от типа тура
block: FORM-GT-GUESTS-370
  validation:
    max: |
      if (tour_type == 'vip') return 10;
      if (tour_type == 'standard') return 20;
      return 50;
```

---

## Error Messages - Лучшие практики

**Плохие сообщения об ошибках:**
- ❌ "Ошибка"
- ❌ "Неверный ввод"
- ❌ "Validation failed"

**Хорошие сообщения:**
- ✅ "Номер телефона должен начинаться с +971"
- ✅ "Дата должна быть в формате ДД.ММ.ГГГГ (например: 25.12.2024)"
- ✅ "Количество гостей: от 1 до 50"

**Структура:**
```yaml
error: |
  ❌ [Что не так]

  [Требование]
  [Пример]
```

**Пример:**
```yaml
error: |
  ❌ Некорректный номер телефона

  Требования:
  • Начинается с +971 или 0
  • Содержит 9-12 цифр

  Примеры:
  • +971501234567
  • 050 123 4567
```

---

## Дополнительные ресурсы

- **FAQ:** `faq.md`
- **Troubleshooting:** `troubleshooting.md`
- **Шпаргалка переменных:** `variables-cheatsheet.md`
- **Основной SKILL:** `../SKILL.md`
