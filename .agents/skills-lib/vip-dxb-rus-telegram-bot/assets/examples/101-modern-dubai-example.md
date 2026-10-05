# Пример: Экскурсия "Современный Дубай" (Блок 101)

## Основное сообщение экскурсии

```
🏙️ СОВРЕМЕННЫЙ ДУБАЙ

Погрузитесь в мир футуристической архитектуры и роскоши! Увидите знаковые достопримечательности, которые сделали Дубай символом инноваций XXI века.

📍 ЧТО УВИДИТЕ:
• Бурдж Халифа (828 м) - самое высокое здание в мире
• Дубай Молл - крупнейший торговый центр планеты
• Поющие фонтаны - грандиозное водное шоу
• Дубай Марина - престижный район небоскрёбов
• Пальма Джумейра - искусственный остров
• Отель Атлантис - символ роскоши
• Район JBR - пляжная набережная

⏱ ПРОДОЛЖИТЕЛЬНОСТЬ: 4-5 часов
🚗 ТРАНСПОРТ: Комфортабельный автомобиль с кондиционером
👥 ФОРМАТ: Групповая или индивидуальная экскурсия

💰 СТОИМОСТЬ:
Групповая (до 6 человек): от 250 AED/чел
Индивидуальная: от 800 AED (1-3 чел)

🎁 В СТОИМОСТЬ ВХОДИТ:
✓ Трансфер от отеля и обратно
✓ Русскоязычный гид-экскурсовод
✓ Остановки для фотосессий
✓ Бутилированная вода

❌ ДОПОЛНИТЕЛЬНО ОПЛАЧИВАЕТСЯ:
• Билет на Бурдж Халифа (от 149 AED)
• Обед в ресторане (по желанию)
• Личные расходы

📅 ВРЕМЯ ПРОВЕДЕНИЯ:
Утренний тур: 09:00 - 14:00
Вечерний тур: 16:00 - 21:00 (с шоу фонтанов)

---

Выберите действие ⤵️
```

## Кнопки (Inline Keyboard)

```python
keyboard = [
    [
        {"text": "📅 Забронировать групповую", "callback_data": "book_GT_101"},
        {"text": "👤 Индивидуальная экскурсия", "callback_data": "book_PT_101"}
    ],
    [
        {"text": "📸 Фото с экскурсии", "callback_data": "photos_101"},
        {"text": "⭐️ Отзывы (47)", "callback_data": "reviews_101"}
    ],
    [
        {"text": "❓ Задать вопрос гиду", "callback_data": "ask_guide_101"}
    ],
    [
        {"text": "🔙 К списку экскурсий", "callback_data": "cat_100"}
    ]
]
```

## Переменные для использования в коде

```python
TOUR_101 = {
    "id": "101",
    "title": "Современный Дубай",
    "category": "100",  # Обзорные экскурсии
    "emoji": "🏙️",
    "duration": "4-5 часов",
    "transport": "Комфортабельный автомобиль с кондиционером",
    "group_price": "от 250 AED/чел",
    "private_price": "от 800 AED (1-3 чел)",
    "max_group_size": 6,
    "schedules": [
        {"time": "09:00-14:00", "type": "morning"},
        {"time": "16:00-21:00", "type": "evening"}
    ],
    "highlights": [
        "Бурдж Халифа (828 м)",
        "Дубай Молл",
        "Поющие фонтаны",
        "Дубай Марина",
        "Пальма Джумейра",
        "Отель Атлантис",
        "Район JBR"
    ],
    "included": [
        "Трансфер от отеля и обратно",
        "Русскоязычный гид-экскурсовод",
        "Остановки для фотосессий",
        "Бутилированная вода"
    ],
    "extra_cost": [
        "Билет на Бурдж Халифа (от 149 AED)",
        "Обед в ресторане (по желанию)",
        "Личные расходы"
    ],
    "reviews_count": 47,
    "rating": 4.9,
    "photos_gallery": "gallery_101",
    "available": True
}
```

## Обработчик кнопки "Забронировать групповую"

```python
@bot.callback_query_handler(func=lambda call: call.data == "book_GT_101")
def handle_book_group_tour_101(call):
    """Запускает форму бронирования групповой экскурсии 101"""

    # Сохраняем контекст
    user_data[call.from_user.id] = {
        "booking_type": "GT",
        "tour_id": "101",
        "tour_title": "Современный Дубай",
        "step": "name"
    }

    # Запускаем форму
    msg = bot.send_message(
        call.message.chat.id,
        "🏙️ БРОНИРОВАНИЕ: Современный Дубай\n\n"
        "Пожалуйста, укажите ваше имя и фамилию:"
    )

    bot.register_next_step_handler(msg, process_booking_name)
```

## Пример сообщения с фотографиями

```python
@bot.callback_query_handler(func=lambda call: call.data == "photos_101")
def show_photos_101(call):
    """Показывает галерею фотографий экскурсии"""

    photos = [
        "https://example.com/burj-khalifa-sunset.jpg",
        "https://example.com/dubai-fountain-show.jpg",
        "https://example.com/palm-jumeirah-aerial.jpg",
        "https://example.com/dubai-marina-night.jpg"
    ]

    # Отправляем медиа-группу
    media_group = [
        InputMediaPhoto(photos[0], caption="🏙️ Фото с экскурсии 'Современный Дубай'"),
        InputMediaPhoto(photos[1]),
        InputMediaPhoto(photos[2]),
        InputMediaPhoto(photos[3])
    ]

    bot.send_media_group(call.message.chat.id, media_group)

    # Добавляем кнопку возврата
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Назад к экскурсии", callback_data="tour_101"))

    bot.send_message(
        call.message.chat.id,
        "📸 Больше фото в нашем Instagram: @vipdxbrus",
        reply_markup=keyboard
    )
```

## Пример сообщения с отзывами

```python
@bot.callback_query_handler(func=lambda call: call.data == "reviews_101")
def show_reviews_101(call):
    """Показывает отзывы об экскурсии"""

    reviews_text = """
⭐️⭐️⭐️⭐️⭐️ ОТЗЫВЫ (47)

🏙️ Современный Дубай

👤 Анна М. | 15 января 2026
⭐️⭐️⭐️⭐️⭐️
"Потрясающая экскурсия! Гид Мария рассказала столько интересного о Дубае.
Фонтаны просто волшебные, а виды с Пальмы - незабываемые. Всем рекомендую!"

👤 Дмитрий К. | 10 января 2026
⭐️⭐️⭐️⭐️⭐️
"Отличная организация, пунктуальность, комфортный автомобиль.
Увидели все главные достопримечательности за один день. Спасибо!"

👤 Елена П. | 5 января 2026
⭐️⭐️⭐️⭐️⭐️
"Брали вечерний тур с шоу фонтанов - это нечто! Детям очень понравилось.
Гид отлично работает с детьми, много интересных фактов."

📊 Средняя оценка: 4.9/5.0
✅ Рекомендуют: 96%
"""

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("📝 Оставить отзыв", callback_data="write_review_101"),
        InlineKeyboardButton("🔙 К экскурсии", callback_data="tour_101")
    )

    bot.edit_message_text(
        reviews_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )
```

## Интеграция с Claude API для вопросов

```python
@bot.callback_query_handler(func=lambda call: call.data == "ask_guide_101")
def ask_guide_101(call):
    """Позволяет задать вопрос о экскурсии через Claude"""

    msg = bot.send_message(
        call.message.chat.id,
        "💬 ЗАДАТЬ ВОПРОС О ЭКСКУРСИИ\n\n"
        "🏙️ Современный Дубай\n\n"
        "Напишите ваш вопрос, и я постараюсь ответить максимально подробно.\n\n"
        "Примеры вопросов:\n"
        "• Можно ли подняться на Бурдж Халифа?\n"
        "• Подходит ли экскурсия для детей 5 лет?\n"
        "• Во сколько лучше ехать - утром или вечером?"
    )

    # Сохраняем контекст
    user_data[call.from_user.id] = {
        "action": "ask_about_tour",
        "tour_id": "101",
        "tour_title": "Современный Дубай"
    }

    bot.register_next_step_handler(msg, process_question_about_tour)
```

## Формат данных для базы знаний Claude

```json
{
  "tour_id": "101",
  "knowledge_base": {
    "general": {
      "best_time": "Вечерний тур предпочтительнее - увидите шоу фонтанов и город в огнях",
      "for_kids": "Подходит для детей от 3 лет. Предусмотрены остановки, есть возможность перекуса",
      "accessibility": "Доступно для людей с ограниченной мобильностью (кроме подъёма на Бурдж Халифа)"
    },
    "burj_khalifa": {
      "tickets": "Билеты покупаются отдельно, от 149 AED. Рекомендуем бронировать заранее",
      "waiting_time": "С билетами At The Top - около 30-45 минут",
      "best_level": "Уровень 124-125 оптимален. Уровень 148 - для VIP опыта"
    },
    "fountain_show": {
      "schedule": "Каждые 30 минут с 18:00 до 23:00",
      "best_view": "Смотровая площадка у Дубай Молла или набережная",
      "duration": "5 минут, разные музыкальные композиции"
    },
    "food": {
      "lunch_options": "Дубай Молл - огромный фудкорт и рестораны на любой вкус и бюджет",
      "recommendations": "Советуем Cheesecake Factory с видом на фонтаны"
    },
    "photography": {
      "best_spots": "Бурдж Халифа с газона, Пальма с The Pointe, Марина с променада",
      "equipment": "Достаточно смартфона, но приветствуется камера для вечерней съёмки"
    }
  }
}
```
