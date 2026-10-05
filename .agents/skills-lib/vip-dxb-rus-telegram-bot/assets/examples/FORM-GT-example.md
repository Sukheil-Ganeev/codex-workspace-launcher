# Пример: Заполненная форма групповой экскурсии (FORM-GT)

## Сценарий заполнения формы

Пользователь бронирует групповую экскурсию "Современный Дубай" (tour_id: 101) на 3 человека.

---

## ШАГ 1: Имя и фамилия

**Сообщение бота:**
```
🏙️ БРОНИРОВАНИЕ: Современный Дубай

Пожалуйста, укажите ваше имя и фамилию:
```

**Ответ пользователя:**
```
Анна Петрова
```

**Валидация:**
- ✅ Содержит минимум 2 слова
- ✅ Только буквы и пробелы
- ✅ Длина от 5 до 100 символов

**Сохранено в user_data:**
```python
user_data[user_id]["name"] = "Анна Петрова"
```

---

## ШАГ 2: Количество человек

**Сообщение бота:**
```
✅ Имя: Анна Петрова

Сколько человек поедет на экскурсию?
(максимум 6 человек в группе)
```

**Ответ пользователя:**
```
3
```

**Валидация:**
- ✅ Целое число
- ✅ От 1 до 6 (максимум для групповой экскурсии)
- ✅ Не пустое значение

**Сохранено в user_data:**
```python
user_data[user_id]["persons"] = 3
```

---

## ШАГ 3: Дата экскурсии

**Сообщение бота:**
```
✅ Количество: 3 человека

На какую дату вы хотите забронировать экскурсию?

Укажите дату в формате: ДД.ММ.ГГГГ
Например: 15.02.2026

⚠️ Минимум 24 часа до даты экскурсии
```

**Ответ пользователя:**
```
15.02.2026
```

**Валидация:**
- ✅ Формат DD.MM.YYYY
- ✅ Дата не в прошлом
- ✅ Минимум через 24 часа от текущего момента
- ✅ Дата существует (не 31 февраля)

**Сохранено в user_data:**
```python
user_data[user_id]["date"] = "15.02.2026"
user_data[user_id]["date_object"] = datetime(2026, 2, 15)
```

---

## ШАГ 4: Время экскурсии

**Сообщение бота:**
```
✅ Дата: 15 февраля 2026

Выберите удобное время:

⏰ ДОСТУПНОЕ ВРЕМЯ:
1️⃣ Утренний тур: 09:00 - 14:00
2️⃣ Вечерний тур: 16:00 - 21:00 (с шоу фонтанов) ⭐️

Отправьте номер варианта (1 или 2)
```

**Ответ пользователя:**
```
2
```

**Валидация:**
- ✅ Число 1 или 2
- ✅ Соответствует доступным вариантам

**Сохранено в user_data:**
```python
user_data[user_id]["time"] = "16:00 - 21:00"
user_data[user_id]["time_type"] = "evening"
```

---

## ШАГ 5: Отель и место встречи

**Сообщение бота:**
```
✅ Время: 16:00 - 21:00 (вечерний тур)

Укажите название вашего отеля или точный адрес для трансфера:

📍 Примеры:
• Jumeirah Beach Hotel
• Atlantis The Palm
• Downtown Dubai, Sheikh Mohammed bin Rashid Blvd

💡 Если не знаете точного названия, укажите район
```

**Ответ пользователя:**
```
Atlantis The Palm
```

**Валидация:**
- ✅ Минимум 5 символов
- ✅ Не только цифры
- ✅ Не пустое значение

**Сохранено в user_data:**
```python
user_data[user_id]["hotel"] = "Atlantis The Palm"
```

---

## ШАГ 6: Номер телефона

**Сообщение бота:**
```
✅ Отель: Atlantis The Palm

Укажите ваш номер телефона для связи:

📱 Формат: +971501234567 или +79161234567
(можно с пробелами или дефисами)

💡 Это нужно для координации встречи и экстренной связи
```

**Ответ пользователя:**
```
+971 50 123 4567
```

**Валидация:**
- ✅ Начинается с +
- ✅ Содержит от 11 до 15 цифр
- ✅ Допустимы пробелы, дефисы, скобки
- ✅ Корректный международный формат

**Обработка:**
```python
# Очистка номера от лишних символов
phone_clean = re.sub(r'[^\d+]', '', "+971 50 123 4567")
# Результат: "+971501234567"
```

**Сохранено в user_data:**
```python
user_data[user_id]["phone"] = "+971501234567"
user_data[user_id]["phone_display"] = "+971 50 123 4567"
```

---

## ШАГ 7: Email

**Сообщение бота:**
```
✅ Телефон: +971 50 123 4567

Укажите ваш email для отправки подтверждения:

📧 Формат: example@mail.com

На этот адрес придёт:
• Подтверждение бронирования
• Ваучер с деталями экскурсии
• Контакты гида
```

**Ответ пользователя:**
```
anna.petrova@gmail.com
```

**Валидация:**
- ✅ Содержит @
- ✅ Есть точка после @
- ✅ Корректный email-формат (regex проверка)
- ✅ Нет пробелов
- ✅ Длина от 5 до 100 символов

**Регулярное выражение:**
```python
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
is_valid = re.match(email_pattern, "anna.petrova@gmail.com")
```

**Сохранено в user_data:**
```python
user_data[user_id]["email"] = "anna.petrova@gmail.com"
```

---

## ШАГ 8: Комментарии и особые пожелания

**Сообщение бота:**
```
✅ Email: anna.petrova@gmail.com

Есть ли у вас особые пожелания или комментарии?

💬 Например:
• Едем с ребёнком 5 лет
• Нужно детское кресло в авто
• Интересует вегетарианская кухня
• Предпочитаем больше времени на фото

Если пожеланий нет, отправьте: нет
```

**Ответ пользователя:**
```
Едем с ребёнком 5 лет, нужно детское кресло. Очень хотим увидеть фонтаны!
```

**Валидация:**
- ✅ Опциональное поле
- ✅ Если указано - максимум 500 символов
- ✅ Если "нет" или "-" - сохраняется как пустое

**Сохранено в user_data:**
```python
user_data[user_id]["comments"] = "Едем с ребёнком 5 лет, нужно детское кресло. Очень хотим увидеть фонтаны!"
```

---

## ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ

**Сообщение бота:**
```
📋 ПРОВЕРЬТЕ ДАННЫЕ БРОНИРОВАНИЯ

🏙️ Экскурсия: Современный Дубай
👤 Имя: Анна Петрова
👥 Количество: 3 человека
📅 Дата: 15.02.2026
⏰ Время: 16:00 - 21:00 (вечерний тур)
🏨 Отель: Atlantis The Palm
📱 Телефон: +971 50 123 4567
📧 Email: anna.petrova@gmail.com
💬 Комментарии: Едем с ребёнком 5 лет, нужно детское кресло. Очень хотим увидеть фонтаны!

💰 СТОИМОСТЬ:
3 человека × 250 AED = 750 AED

📌 ВАЖНО:
• Трансфер включён в стоимость
• Билеты на Бурдж Халифа оплачиваются отдельно (от 149 AED)
• Детское кресло предоставим бесплатно

Всё верно?
```

**Кнопки:**
```python
keyboard = [
    [
        {"text": "✅ Всё верно, подтвердить", "callback_data": "confirm_booking_GT_101"},
        {"text": "✏️ Изменить данные", "callback_data": "edit_booking_GT_101"}
    ],
    [
        {"text": "❌ Отменить бронирование", "callback_data": "cancel_booking"}
    ]
]
```

---

## ОБРАБОТКА ПОДТВЕРЖДЕНИЯ

```python
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_booking_GT_"))
def confirm_group_tour_booking(call):
    """Финальное подтверждение бронирования"""

    user_id = call.from_user.id
    data = user_data.get(user_id, {})

    # Создание записи в базе данных
    booking_id = generate_booking_id()  # Например: "GT-101-20260215-001"

    booking_record = {
        "booking_id": booking_id,
        "user_id": user_id,
        "username": call.from_user.username,
        "booking_type": "GT",
        "tour_id": data["tour_id"],
        "tour_title": data["tour_title"],
        "customer_name": data["name"],
        "persons": data["persons"],
        "date": data["date"],
        "time": data["time"],
        "hotel": data["hotel"],
        "phone": data["phone"],
        "email": data["email"],
        "comments": data["comments"],
        "total_price": data["persons"] * 250,  # 3 × 250 = 750 AED
        "status": "pending",  # pending -> confirmed -> completed
        "created_at": datetime.now().isoformat(),
        "payment_status": "unpaid"
    }

    # Сохранение в БД
    save_booking(booking_record)

    # Отправка уведомления администратору
    notify_admin_new_booking(booking_record)

    # Отправка email клиенту
    send_confirmation_email(booking_record)

    # Ответ пользователю
    bot.edit_message_text(
        f"✅ БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО!\n\n"
        f"🎫 Номер бронирования: {booking_id}\n\n"
        f"📧 На ваш email отправлено подтверждение с деталями экскурсии.\n\n"
        f"📱 С вами свяжется наш менеджер в течение 2 часов для уточнения деталей.\n\n"
        f"💳 ОПЛАТА:\n"
        f"Вы можете оплатить:\n"
        f"• Наличными гиду перед экскурсией\n"
        f"• Онлайн по ссылке (придёт в письме)\n\n"
        f"Спасибо за выбор VIP-DXB-RUS! 🇦🇪",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=create_main_menu_keyboard()
    )

    # Очистка временных данных
    user_data.pop(user_id, None)
```

---

## ПОЛНЫЙ ОБЪЕКТ user_data

```python
user_data[12345678] = {
    # Служебная информация
    "booking_type": "GT",
    "tour_id": "101",
    "tour_title": "Современный Дубай",
    "step": "comments",  # Текущий шаг формы

    # Данные формы
    "name": "Анна Петрова",
    "persons": 3,
    "date": "15.02.2026",
    "date_object": datetime(2026, 2, 15),
    "time": "16:00 - 21:00",
    "time_type": "evening",
    "hotel": "Atlantis The Palm",
    "phone": "+971501234567",
    "phone_display": "+971 50 123 4567",
    "email": "anna.petrova@gmail.com",
    "comments": "Едем с ребёнком 5 лет, нужно детское кресло. Очень хотим увидеть фонтаны!",

    # Расчётные данные
    "price_per_person": 250,
    "total_price": 750,
    "currency": "AED"
}
```

---

## ВАЛИДАЦИЯ: Все функции

```python
def validate_name(name):
    """Валидация имени и фамилии"""
    if not name or len(name.strip()) < 5:
        return False, "Имя слишком короткое. Укажите имя и фамилию."

    if len(name) > 100:
        return False, "Имя слишком длинное. Максимум 100 символов."

    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', name):
        return False, "Имя может содержать только буквы, пробелы и дефисы."

    words = name.strip().split()
    if len(words) < 2:
        return False, "Укажите имя и фамилию (минимум 2 слова)."

    return True, name.strip()


def validate_persons(persons_str, max_persons=6):
    """Валидация количества человек"""
    try:
        persons = int(persons_str)
    except ValueError:
        return False, "Укажите число. Например: 3"

    if persons < 1:
        return False, "Минимум 1 человек."

    if persons > max_persons:
        return False, f"Максимум {max_persons} человек в группе. Для большей группы выберите индивидуальную экскурсию."

    return True, persons


def validate_date(date_str):
    """Валидация даты экскурсии"""
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return False, "Неверный формат даты. Используйте ДД.ММ.ГГГГ (например: 15.02.2026)"

    # Проверка на прошедшую дату
    if date_obj.date() < datetime.now().date():
        return False, "Дата не может быть в прошлом."

    # Минимум 24 часа
    min_date = datetime.now() + timedelta(hours=24)
    if date_obj < min_date:
        return False, "Бронирование возможно минимум за 24 часа. Выберите более позднюю дату."

    # Максимум 6 месяцев вперёд
    max_date = datetime.now() + timedelta(days=180)
    if date_obj > max_date:
        return False, "Бронирование доступно максимум на 6 месяцев вперёд."

    return True, date_obj


def validate_phone(phone_str):
    """Валидация номера телефона"""
    # Очистка от лишних символов
    phone_clean = re.sub(r'[^\d+]', '', phone_str)

    if not phone_clean.startswith('+'):
        return False, "Номер должен начинаться с + и кода страны. Например: +971501234567"

    if len(phone_clean) < 11 or len(phone_clean) > 15:
        return False, "Проверьте номер телефона. Должно быть от 11 до 15 цифр с кодом страны."

    # Проверка на популярные коды
    valid_codes = ['+971', '+7', '+380', '+375', '+374', '+994']
    if not any(phone_clean.startswith(code) for code in valid_codes):
        return False, "Укажите номер с кодом страны: +971 (ОАЭ), +7 (Россия), +380 (Украина) и т.д."

    return True, phone_clean


def validate_email(email_str):
    """Валидация email"""
    email = email_str.strip().lower()

    if len(email) < 5 or len(email) > 100:
        return False, "Email должен быть от 5 до 100 символов."

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Неверный формат email. Пример: example@gmail.com"

    return True, email


def validate_comments(comments_str):
    """Валидация комментариев (опционально)"""
    if not comments_str or comments_str.strip().lower() in ['нет', 'no', '-', '—']:
        return True, ""

    if len(comments_str) > 500:
        return False, "Комментарий слишком длинный. Максимум 500 символов."

    return True, comments_str.strip()
```
