# Variables Cheatsheet - Шпаргалка по переменным

Быстрая справка по всем 113 переменным VIP-DXB-RUS бота для копирования.

---

## Быстрый поиск

- [FORM-GT (Групповая экскурсия)](#form-gt-групповая-экскурсия---7-переменных)
- [FORM-PT (Приватная экскурсия)](#form-pt-приватная-экскурсия---7-переменных)
- [FORM-BUGGY (Багги)](#form-buggy-багги-тур---9-переменных)
- [FORM-RENT (Аренда авто)](#form-rent-аренда-авто---11-переменных)
- [FORM-QUAD (Квадроцикл)](#form-quad-квадроцикл---8-переменных)
- [FORM-JETSKI (Гидроцикл)](#form-jetski-гидроцикл---8-переменных)
- [FORM-CRUISE (Круиз)](#form-cruise-круиз---6-переменных-планируется)
- [Системные переменные](#системные-переменные---6-переменных)

---

## FORM-GT (Групповая экскурсия) - 7 переменных

```yaml
variables:
  - gt_date          # Дата экскурсии (DD.MM.YYYY)
  - gt_time          # Время (morning/afternoon/evening/HH:MM)
  - gt_guests        # Количество гостей (1-50)
  - gt_name          # Имя контактного лица
  - gt_phone         # Телефон (+971XXXXXXXXX)
  - gt_hotel         # Название отеля (опционально)
  - gt_comments      # Дополнительные пожелания (опционально)
```

### Примеры использования

```yaml
# В блоке ввода:
block: FORM-GT-DATE-350
  variable_name: gt_date

# В Review блоке:
message: text: |
  📅 Дата: {{gt_date}}
  🕒 Время: {{gt_time}}
  👥 Гостей: {{gt_guests}}
  👤 Имя: {{gt_name}}
  📱 Телефон: {{gt_phone}}
  🏨 Отель: {{gt_hotel}}
  💬 Комментарии: {{gt_comments}}

# В отправке админу:
actions:
  - type: send_to_admin
    message: |
      🆕 Групповая экскурсия
      {{gt_date}} в {{gt_time}}
      Гостей: {{gt_guests}}
      Контакт: {{gt_name}} ({{gt_phone}})
```

---

## FORM-PT (Приватная экскурсия) - 7 переменных

```yaml
variables:
  - pt_date          # Дата экскурсии
  - pt_time          # Время
  - pt_guests        # Количество гостей (1-20)
  - pt_name          # Имя
  - pt_phone         # Телефон
  - pt_hotel         # Отель (опционально)
  - pt_comments      # Комментарии (опционально)
```

### Примеры использования

```yaml
# Аналогично GT, замените префикс gt_ на pt_
message: text: |
  📅 Дата: {{pt_date}}
  🕒 Время: {{pt_time}}
  👥 Гостей: {{pt_guests}}
```

---

## FORM-BUGGY (Багги тур) - 9 переменных

```yaml
variables:
  - buggy_date           # Дата тура
  - buggy_time           # Время (morning/afternoon/sunset)
  - buggy_participants   # Количество участников (1-10)
  - buggy_experience     # Уровень опыта (beginner/intermediate/advanced)
  - buggy_insurance      # Страховка (yes/no)
  - buggy_name           # Имя
  - buggy_phone          # Телефон
  - buggy_hotel          # Отель (опционально)
  - buggy_comments       # Комментарии (опционально)
```

### Примеры использования

```yaml
# Review блок:
message: text: |
  🏜️ *Багги тур*

  📅 Дата: {{buggy_date}}
  🕒 Время: {{buggy_time}}
  👥 Участников: {{buggy_participants}}
  📊 Опыт: {{buggy_experience}}
  🛡️ Страховка: {{buggy_insurance}}

  📞 Контакты:
  👤 {{buggy_name}}
  📱 {{buggy_phone}}
  🏨 {{buggy_hotel}}

# Условная логика:
if: buggy_experience == "beginner"
message: text: |
  ℹ️ Для новичков предусмотрен расширенный инструктаж (30 мин)
```

---

## FORM-RENT (Аренда авто) - 11 переменных

```yaml
variables:
  - rent_start_date      # Дата начала аренды
  - rent_end_date        # Дата окончания
  - rent_car_class       # Класс авто (economy/comfort/business/luxury/suv/sports)
  - rent_transmission    # Коробка передач (automatic/manual/any)
  - rent_emirate         # Эмират (dubai/abu_dhabi/sharjah/ajman/fujairah/rak/uaq)
  - rent_driver          # Нужен водитель (yes/no)
  - rent_insurance_type  # Тип страховки (basic/standard/premium)
  - rent_name            # Имя
  - rent_phone           # Телефон
  - rent_hotel           # Отель (опционально)
  - rent_comments        # Комментарии (опционально)
```

### Примеры использования

```yaml
# Review с расчетом дней:
message: text: |
  🚗 *Аренда автомобиля*

  📅 Период: {{rent_start_date}} - {{rent_end_date}}
  📊 Дней: {{calculate_days(rent_start_date, rent_end_date)}}

  🚙 Класс: {{rent_car_class}}
  ⚙️ КПП: {{rent_transmission}}
  📍 Эмират: {{rent_emirate}}

  👨‍✈️ Водитель: {{rent_driver}}
  🛡️ Страховка: {{rent_insurance_type}}

# Условная цена:
if: rent_driver == "yes"
message: text: |
  💰 Стоимость водителя: +300 AED/день

# Проверка длительности:
validation:
  custom: |
    const days = daysBetween(rent_start_date, rent_end_date);
    if (days < 1) return "Минимум 1 день";
    if (days > 30) return "Максимум 30 дней";
    return true;
```

---

## FORM-QUAD (Квадроцикл) - 8 переменных

```yaml
variables:
  - quad_date           # Дата
  - quad_time           # Время
  - quad_participants   # Участники (1-10)
  - quad_duration       # Длительность (1h/2h/4h/full_day)
  - quad_experience     # Опыт (beginner/intermediate/advanced)
  - quad_insurance      # Страховка (yes/no)
  - quad_name           # Имя
  - quad_phone          # Телефон
  - quad_comments       # Комментарии (опционально)
```

### Примеры использования

```yaml
# Review с ценой:
message: text: |
  🏍️ *Квадроцикл*

  📅 {{quad_date}} в {{quad_time}}
  ⏱️ Длительность: {{quad_duration}}
  👥 Участников: {{quad_participants}}

  💰 Стоимость:
  {{calculate_quad_price(quad_duration, quad_participants)}}

# Функция расчета цены:
functions:
  calculate_quad_price: |
    const prices = {
      '1h': 250,
      '2h': 400,
      '4h': 700,
      'full_day': 1200
    };
    return prices[duration] * participants + ' AED';
```

---

## FORM-JETSKI (Гидроцикл) - 8 переменных

```yaml
variables:
  - jetski_date          # Дата
  - jetski_time          # Время (morning/afternoon)
  - jetski_participants  # Участники (1-6)
  - jetski_duration      # Длительность (30min/1h/2h)
  - jetski_experience    # Опыт (none/basic/advanced)
  - jetski_insurance     # Страховка (yes/no)
  - jetski_name          # Имя
  - jetski_phone         # Телефон
  - jetski_comments      # Комментарии (опционально)
```

### Примеры использования

```yaml
# Review:
message: text: |
  🌊 *Гидроцикл*

  📅 {{jetski_date}} {{jetski_time}}
  ⏱️ {{jetski_duration}}
  👥 Участников: {{jetski_participants}}
  📊 Опыт: {{jetski_experience}}

  🛡️ Страховка: {{jetski_insurance}}

# Предупреждение для новичков:
if: jetski_experience == "none"
message: text: |
  ⚠️ Обязательный инструктаж перед катанием (15 мин)
  Зона катания: ближняя (до 500м от берега)
```

---

## FORM-CRUISE (Круиз) - 6 переменных (планируется)

```yaml
# ФОРМА НЕ РЕАЛИЗОВАНА - ШАБЛОН

variables:
  - cruise_type      # Тип круиза (dinner/night/day)
  - cruise_date      # Дата
  - cruise_guests    # Количество гостей
  - cruise_cabin     # Каюта (standard/vip/premium) - опционально
  - cruise_name      # Имя
  - cruise_phone     # Телефон
  - cruise_comments  # Комментарии (опционально)
```

### Примеры использования (когда будет реализовано)

```yaml
message: text: |
  🛳️ *Круиз*

  🎭 Тип: {{cruise_type}}
  📅 Дата: {{cruise_date}}
  👥 Гостей: {{cruise_guests}}
  🚪 Каюта: {{cruise_cabin}}
```

---

## Системные переменные - 6 переменных

```yaml
variables:
  - user_id       # ID пользователя Telegram (integer)
  - username      # @username (если есть)
  - first_name    # Имя из профиля Telegram
  - last_name     # Фамилия (если есть)
  - language      # Язык (ru/en/ar)
  - timestamp     # Время заполнения (ISO 8601)
```

### Примеры использования

```yaml
# Персонализация приветствия:
message: text: |
  Привет, {{first_name}}! 👋

# В логах:
log: |
  User {{user_id}} (@{{username}}) submitted form at {{timestamp}}

# Отправка админу с инфо о пользователе:
actions:
  - type: send_to_admin
    message: |
      🆕 Новая заявка
      👤 От: {{first_name}} {{last_name}} (@{{username}})
      🆔 ID: {{user_id}}
      🌐 Язык: {{language}}
      ⏰ Время: {{timestamp}}

# Условие по языку:
if: language == "ru"
message: text: "Русский текст"

if: language == "en"
message: text: "English text"
```

---

## Дополнительные служебные переменные

### Вычисляемые переменные

```yaml
# Не хранятся, вычисляются на лету
computed_variables:
  - current_date           # Сегодняшняя дата
  - current_time           # Текущее время
  - current_datetime       # Дата и время
  - form_progress          # Прогресс заполнения (%)
  - form_completion_time   # Время заполнения формы (сек)
```

**Примеры:**
```yaml
# Показать сегодняшнюю дату:
message: text: |
  📅 Сегодня: {{current_date}}

# Прогресс заполнения:
message: text: |
  ✅ Прогресс: {{form_progress}}%
  ⏱️ Потрачено времени: {{form_completion_time}} сек
```

---

## Группировка по типам данных

### Даты (17 переменных)

```yaml
date_variables:
  - gt_date
  - pt_date
  - buggy_date
  - rent_start_date
  - rent_end_date
  - quad_date
  - jetski_date
  - cruise_date
  - current_date
  - current_datetime
  - timestamp
```

**Формат:** DD.MM.YYYY или ISO 8601

---

### Время (8 переменных)

```yaml
time_variables:
  - gt_time
  - pt_time
  - buggy_time
  - quad_time
  - jetski_time
  - current_time
```

**Формат:** HH:MM или период (morning/afternoon/evening/sunset)

---

### Числа (7 переменных)

```yaml
number_variables:
  - gt_guests          # 1-50
  - pt_guests          # 1-20
  - buggy_participants # 1-10
  - quad_participants  # 1-10
  - jetski_participants # 1-6
  - cruise_guests      # 1-50
  - user_id            # integer
```

---

### Телефоны (7 переменных)

```yaml
phone_variables:
  - gt_phone
  - pt_phone
  - buggy_phone
  - rent_phone
  - quad_phone
  - jetski_phone
  - cruise_phone
```

**Формат:** +971XXXXXXXXX

---

### Текстовые (42 переменные)

Все остальные: имена, отели, комментарии, селекты.

---

### Булевы (6 переменных)

```yaml
boolean_variables:
  - buggy_insurance     # yes/no
  - quad_insurance      # yes/no
  - jetski_insurance    # yes/no
  - rent_driver         # yes/no
```

---

## Префиксы форм

| Префикс | Форма | Количество |
|---------|-------|------------|
| `gt_` | Групповая экскурсия | 7 |
| `pt_` | Приватная экскурсия | 7 |
| `buggy_` | Багги тур | 9 |
| `rent_` | Аренда авто | 11 |
| `quad_` | Квадроцикл | 8 |
| `jetski_` | Гидроцикл | 8 |
| `cruise_` | Круиз | 6 |
| (нет) | Системные | 6 |

---

## Стандартный набор полей

Каждая форма содержит базовые поля:

```yaml
# Минимальный набор (5 полей):
standard_fields:
  - {prefix}_date       # Дата
  - {prefix}_time       # Время (если применимо)
  - {prefix}_participants / _guests  # Количество
  - {prefix}_name       # Имя
  - {prefix}_phone      # Телефон

# Опциональные (2 поля):
optional_fields:
  - {prefix}_hotel      # Отель
  - {prefix}_comments   # Комментарии
```

**Шаблон для новой формы:**
```yaml
# Замените {PREFIX} на имя формы (например, SAFARI)
variables:
  - safari_date
  - safari_time
  - safari_participants
  - safari_name
  - safari_phone
  - safari_hotel
  - safari_comments
```

---

## Копипаста для объявления переменных

### Все переменные разом (56 переменных)

```yaml
variables:
  # FORM-GT (7)
  - gt_date
  - gt_time
  - gt_guests
  - gt_name
  - gt_phone
  - gt_hotel
  - gt_comments

  # FORM-PT (7)
  - pt_date
  - pt_time
  - pt_guests
  - pt_name
  - pt_phone
  - pt_hotel
  - pt_comments

  # FORM-BUGGY (9)
  - buggy_date
  - buggy_time
  - buggy_participants
  - buggy_experience
  - buggy_insurance
  - buggy_name
  - buggy_phone
  - buggy_hotel
  - buggy_comments

  # FORM-RENT (11)
  - rent_start_date
  - rent_end_date
  - rent_car_class
  - rent_transmission
  - rent_emirate
  - rent_driver
  - rent_insurance_type
  - rent_name
  - rent_phone
  - rent_hotel
  - rent_comments

  # FORM-QUAD (8)
  - quad_date
  - quad_time
  - quad_participants
  - quad_duration
  - quad_experience
  - quad_insurance
  - quad_name
  - quad_phone
  - quad_comments

  # FORM-JETSKI (8)
  - jetski_date
  - jetski_time
  - jetski_participants
  - jetski_duration
  - jetski_experience
  - jetski_insurance
  - jetski_name
  - jetski_phone
  - jetski_comments

  # FORM-CRUISE (6) - НЕ РЕАЛИЗОВАНО
  # - cruise_type
  # - cruise_date
  # - cruise_guests
  # - cruise_cabin
  # - cruise_name
  # - cruise_phone
  # - cruise_comments

  # Системные (6)
  - user_id
  - username
  - first_name
  - last_name
  - language
  - timestamp
```

---

## Шаблоны использования

### Review блок (универсальный шаблон)

```yaml
block: FORM-{PREFIX}-REVIEW-XXX
  message:
    text: |
      ✅ *Проверьте вашу заявку:*

      📅 Дата: {{PREFIX_date}}
      🕒 Время: {{PREFIX_time}}
      👥 Участников: {{PREFIX_participants}}
      👤 Имя: {{PREFIX_name}}
      📱 Телефон: {{PREFIX_phone}}
      🏨 Отель: {{PREFIX_hotel}}

      💬 Комментарии:
      {{PREFIX_comments}}

      Все верно?

  buttons:
    - text: "✏️ Редактировать"
      screen: FORM-{PREFIX}-DATE-XXX
    - text: "✅ Подтвердить"
      screen: FORM-{PREFIX}-SUBMIT-XXX
```

---

### Отправка админу (универсальный шаблон)

```yaml
block: FORM-{PREFIX}-SUBMIT-XXX
  actions:
    - type: send_to_admin
      chat_id: "ADMIN_CHAT_ID"
      message: |
        🆕 *Новая заявка: {FORM_NAME}*

        📅 Дата: {{PREFIX_date}}
        🕒 Время: {{PREFIX_time}}
        👥 Участников: {{PREFIX_participants}}

        📞 *Контакты:*
        👤 Имя: {{PREFIX_name}}
        📱 Телефон: {{PREFIX_phone}}
        🏨 Отель: {{PREFIX_hotel}}

        💬 *Комментарии:*
        {{PREFIX_comments}}

        ---
        👤 От: {{first_name}} {{last_name}} (@{{username}})
        🆔 ID: {{user_id}}
        ⏰ Время: {{timestamp}}
```

---

### Сброс переменных формы

```yaml
# После отправки или отмены
actions:
  - type: reset_variables
    variables:
      - PREFIX_date
      - PREFIX_time
      - PREFIX_participants
      - PREFIX_name
      - PREFIX_phone
      - PREFIX_hotel
      - PREFIX_comments
      # ... все переменные формы
```

---

## Условная логика - Примеры

### Проверка заполненности

```yaml
# Показать блок только если отель указан
if: gt_hotel != null && gt_hotel != ""
message: text: |
  🏨 Трансфер из {{gt_hotel}}
```

---

### Множественные условия

```yaml
# VIP обслуживание для больших групп
if: gt_guests > 20 || pt_guests > 10
message: text: |
  💎 Доступно VIP обслуживание
```

---

### Вложенные условия

```yaml
if: rent_driver == "no"
  # Если без водителя - нужны права
  if: rent_car_class == "sports"
    message: text: |
      ⚠️ Для спорткаров требуется:
      • Возраст 25+
      • Опыт вождения 5+ лет
      • Депозит 10,000 AED
  else:
    message: text: |
      ℹ️ Требуются международные права
```

---

### Расчетные поля

```yaml
# Количество багги = участники / 2 (округление вверх)
computed:
  buggy_count: "Math.ceil(buggy_participants / 2)"

message: text: |
  🏍️ Количество багги: {{buggy_count}}
  💰 Стоимость: {{buggy_count * 500}} AED

# Дней аренды
computed:
  rent_days: "daysBetween(rent_start_date, rent_end_date)"

message: text: |
  📊 Период аренды: {{rent_days}} дней
```

---

## Валидация между переменными

### Дата окончания после начала

```yaml
block: FORM-RENT-END-DATE-810
  validation:
    custom: |
      if (rent_end_date <= rent_start_date) {
        return "Дата окончания должна быть позже даты начала";
      }
      return true;
```

---

### Зависимые поля

```yaml
# Если выбран водитель - права не нужны
block: FORM-RENT-LICENSE-892
  visible_if: rent_driver == "no"

  validation:
    required_if: rent_driver == "no"
```

---

### Комплексная валидация

```yaml
block: FORM-GT-SUBMIT-410
  validation:
    custom: |
      // Проверка всех обязательных полей
      const required = ['gt_date', 'gt_time', 'gt_guests', 'gt_name', 'gt_phone'];

      for (let field of required) {
        if (!variables[field]) {
          return `Поле ${field} обязательно`;
        }
      }

      // Проверка логики
      if (variables.gt_guests > 30 && variables.gt_time == 'evening') {
        return "Вечерние туры доступны только для групп до 30 человек";
      }

      return true;
```

---

## Форматирование вывода

### Даты

```yaml
# Преобразовать DD.MM.YYYY в текст
{{formatDate(gt_date, 'long')}}
# Выход: "25 декабря 2024 года"

{{formatDate(gt_date, 'short')}}
# Выход: "25.12.24"

{{formatDate(gt_date, 'weekday')}}
# Выход: "Среда"
```

---

### Телефоны

```yaml
# Форматировать телефон
{{formatPhone(gt_phone)}}
# Вход: +971501234567
# Выход: +971 50 123 4567

{{formatPhone(gt_phone, 'local')}}
# Выход: 050 123 4567
```

---

### Числа

```yaml
# Форматировать количество
{{gt_guests}} {{pluralize(gt_guests, 'гость', 'гостя', 'гостей')}}
# 1 гость
# 2 гостя
# 5 гостей

# Цена
{{formatPrice(1500)}}
# 1,500 AED
```

---

## Дополнительные ресурсы

- **FAQ:** `faq.md` - часто задаваемые вопросы
- **Troubleshooting:** `troubleshooting.md` - решение проблем
- **Form Fields:** `form-fields-reference.md` - детальная справка по полям
- **Основной SKILL:** `../SKILL.md` - полная документация
