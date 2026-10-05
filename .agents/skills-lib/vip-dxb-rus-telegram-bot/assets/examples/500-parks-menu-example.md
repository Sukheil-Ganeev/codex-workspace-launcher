# Пример: Меню "Парки в Дубае" (Блок 500)

## Основное меню категории

```
🎢 ПАРКИ В ДУБАЕ

Дубай предлагает невероятное разнообразие развлечений для всей семьи! От экстремальных аттракционов до спокойных зелёных зон - каждый найдёт что-то по душе.

🎯 ВЫБЕРИТЕ КАТЕГОРИЮ:

🎡 Парки развлечений - захватывающие аттракционы и шоу
🌊 Аквапарки - водные горки и бассейны
🐾 Зоопарки и сафари - встреча с дикой природой
🌳 Городские парки - отдых на природе в центре города
🏰 Тематические парки - уникальные развлекательные зоны
🎨 Образовательные парки - наука и творчество для детей

---

💡 ПОЛЕЗНАЯ ИНФОРМАЦИЯ:
• Лучшее время посещения: октябрь-апрель (прохладнее)
• Билеты выгоднее покупать онлайн заранее
• Многие парки работают до позднего вечера
• Детям до 3 лет часто вход бесплатный

📞 Нужна помощь в выборе? Напишите нам!
```

## Inline Keyboard структура

```python
keyboard_500 = [
    [
        {"text": "🎡 Парки развлечений", "callback_data": "cat_510"},
        {"text": "🌊 Аквапарки", "callback_data": "cat_520"}
    ],
    [
        {"text": "🐾 Зоопарки и сафари", "callback_data": "cat_530"},
        {"text": "🌳 Городские парки", "callback_data": "cat_540"}
    ],
    [
        {"text": "🏰 Тематические парки", "callback_data": "cat_550"},
        {"text": "🎨 Образовательные парки", "callback_data": "cat_560"}
    ],
    [
        {"text": "🎫 Комбо-билеты со скидкой", "callback_data": "combo_tickets_500"}
    ],
    [
        {"text": "🔙 Главное меню", "callback_data": "main_menu"}
    ]
]
```

---

## Подкатегория 510: Парки развлечений

```
🎡 ПАРКИ РАЗВЛЕЧЕНИЙ

Самые захватывающие парки развлечений в Дубае и окрестностях! Экстремальные аттракционы, семейные зоны и незабываемые впечатления.

🎢 ВЫБЕРИТЕ ПАРК:
```

**Кнопки:**
```python
keyboard_510 = [
    [
        {"text": "🎭 IMG Worlds of Adventure", "callback_data": "park_511"}
    ],
    [
        {"text": "🎪 Dubai Parks and Resorts", "callback_data": "park_512"}
    ],
    [
        {"text": "🏎️ Ferrari World Abu Dhabi", "callback_data": "park_513"}
    ],
    [
        {"text": "⚡ Warner Bros World Abu Dhabi", "callback_data": "park_514"}
    ],
    [
        {"text": "🎯 VR Park Dubai", "callback_data": "park_515"}
    ],
    [
        {"text": "🔙 К категориям парков", "callback_data": "cat_500"}
    ]
]
```

---

## Пример карточки парка: IMG Worlds of Adventure (511)

```
🎭 IMG WORLDS OF ADVENTURE

Крупнейший крытый парк развлечений в мире! 1.5 млн кв. футов развлечений с Marvel супергероями, динозаврами и экстремальными аттракционами.

📍 МЕСТОПОЛОЖЕНИЕ:
City of Arabia, Sheikh Mohammed Bin Zayed Road
🚗 30 минут от Downtown Dubai

⏰ ВРЕМЯ РАБОТЫ:
Понедельник - Воскресенье: 12:00 - 22:00
(часы могут меняться, уточняйте актуальное)

🎢 ТОП-АТТРАКЦИОНЫ:
• Avengers Battle of Ultron - 5D супергеройский экшн
• Velociraptor - экстремальные американские горки
• The Haunted Hotel - самый страшный дом ужасов в регионе
• Spider-Man Doc Ock's Revenge - гонка с злодеем
• Dinosaur Adventure - путешествие в юрский период

🏆 ЗОНЫ ПАРКА:
1️⃣ Marvel Zone - супергерои Marvel
2️⃣ Cartoon Network Zone - герои мультфильмов
3️⃣ Lost Valley - мир динозавров
4️⃣ IMG Boulevard - магазины и рестораны

👥 ДЛЯ КОГО:
✅ Семьи с детьми от 6 лет
✅ Любители экстрима
✅ Фанаты Marvel и CN
⚠️ Некоторые аттракционы с ограничениями по росту (120-140 см)

💰 СТОИМОСТЬ БИЛЕТОВ:
Взрослый (12+ лет): 345 AED
Детский (3-11 лет): 295 AED
До 3 лет: бесплатно

🎁 НАШИ ЦЕНЫ:
Взрослый: 310 AED (-10%)
Детский: 265 AED (-10%)
Семейный пакет (2+2): 1100 AED (экономия 280 AED!)

📦 ЧТО ВКЛЮЧЕНО:
✓ Безлимитный доступ ко всем аттракционам
✓ Все зоны и шоу
✓ Бесплатный Wi-Fi
✓ Парковка (оплачивается отдельно)

🍔 ПИТАНИЕ:
Рестораны и кафе в зоне IMG Boulevard
Средний чек: 50-100 AED/чел
(можно приносить свою воду)

📸 СОВЕТЫ:
• Приезжайте к открытию - меньше очередей
• Скачайте приложение IMG для актуальных времён ожидания
• Носите удобную обувь - много ходьбы
• Возьмите лёгкую куртку - внутри холодно от кондиционеров

🎫 КАК КУПИТЬ:
Онлайн через наш бот - получите е-билет на email
Оплата: карта, наличные, криптовалюта

---

Выберите действие ⤵️
```

**Кнопки карточки:**
```python
keyboard_park_511 = [
    [
        {"text": "🎫 Купить билеты", "callback_data": "buy_tickets_511"},
        {"text": "📅 Проверить расписание", "callback_data": "schedule_511"}
    ],
    [
        {"text": "🚗 Как добраться", "callback_data": "directions_511"},
        {"text": "📸 Фото парка", "callback_data": "photos_511"}
    ],
    [
        {"text": "❓ Часто задаваемые вопросы", "callback_data": "faq_511"}
    ],
    [
        {"text": "🔙 К паркам развлечений", "callback_data": "cat_510"}
    ]
]
```

---

## Подкатегория 520: Аквапарки

```
🌊 АКВАПАРКИ ДУБАЯ

Освежитесь в жаркую погоду! Экстремальные водные горки, ленивые реки и детские зоны - идеальный отдых для всей семьи.

🏄 ВЫБЕРИТЕ АКВАПАРК:
```

**Кнопки:**
```python
keyboard_520 = [
    [
        {"text": "🌴 Aquaventure Waterpark", "callback_data": "park_521"}
    ],
    [
        {"text": "🏝️ Wild Wadi Waterpark", "callback_data": "park_522"}
    ],
    [
        {"text": "💦 Laguna Waterpark", "callback_data": "park_523"}
    ],
    [
        {"text": "🌊 Legoland Water Park", "callback_data": "park_524"}
    ],
    [
        {"text": "🔙 К категориям парков", "callback_data": "cat_500"}
    ]
]
```

---

## Подкатегория 530: Зоопарки и сафари

```
🐾 ЗООПАРКИ И САФАРИ

Встретьтесь с удивительными животными! От африканской саванны до арктических пейзажей - настоящее путешествие по миру природы.

🦁 ВЫБЕРИТЕ ЛОКАЦИЮ:
```

**Кнопки:**
```python
keyboard_530 = [
    [
        {"text": "🦒 Dubai Safari Park", "callback_data": "park_531"}
    ],
    [
        {"text": "🐧 The Green Planet", "callback_data": "park_532"}
    ],
    [
        {"text": "🐪 Desert Safari Experience", "callback_data": "tour_533"}
    ],
    [
        {"text": "🐠 Dubai Aquarium", "callback_data": "park_534"}
    ],
    [
        {"text": "🦜 Ras Al Khor Wildlife", "callback_data": "park_535"}
    ],
    [
        {"text": "🔙 К категориям парков", "callback_data": "cat_500"}
    ]
]
```

---

## Подкатегория 540: Городские парки

```
🌳 ГОРОДСКИЕ ПАРКИ

Оазисы спокойствия в сердце мегаполиса. Зелёные лужайки, озёра, детские площадки и зоны для пикников.

🏞️ ВЫБЕРИТЕ ПАРК:
```

**Кнопки:**
```python
keyboard_540 = [
    [
        {"text": "🌺 Zabeel Park", "callback_data": "park_541"}
    ],
    [
        {"text": "🌸 Al Barsha Pond Park", "callback_data": "park_542"}
    ],
    [
        {"text": "🎋 Safa Park", "callback_data": "park_543"}
    ],
    [
        {"text": "🌼 Al Qudra Lakes", "callback_data": "park_544"}
    ],
    [
        {"text": "🌿 Creek Park", "callback_data": "park_545"}
    ],
    [
        {"text": "🔙 К категориям парков", "callback_data": "cat_500"}
    ]
]
```

---

## Подкатегория 550: Тематические парки

```
🏰 ТЕМАТИЧЕСКИЕ ПАРКИ

Уникальные концепции и невероятные миры! От LEGO до Болливуда - парки с особенной атмосферой.

🎪 ВЫБЕРИТЕ ТЕМАТИКУ:
```

**Кнопки:**
```python
keyboard_550 = [
    [
        {"text": "🧱 Legoland Dubai", "callback_data": "park_551"}
    ],
    [
        {"text": "🎬 Motiongate Dubai", "callback_data": "park_552"}
    ],
    [
        {"text": "💃 Bollywood Parks", "callback_data": "park_553"}
    ],
    [
        {"text": "🚁 Hub Zero Dubai", "callback_data": "park_554"}
    ],
    [
        {"text": "🔙 К категориям парков", "callback_data": "cat_500"}
    ]
]
```

---

## Подкатегория 560: Образовательные парки

```
🎨 ОБРАЗОВАТЕЛЬНЫЕ ПАРКИ

Учиться весело! Интерактивные музеи, научные центры и творческие пространства для детей и взрослых.

🔬 ВЫБЕРИТЕ АКТИВНОСТЬ:
```

**Кnопки:**
```python
keyboard_560 = [
    [
        {"text": "🚀 Children's City", "callback_data": "park_561"}
    ],
    [
        {"text": "🔭 Dubai Science Park", "callback_data": "park_562"}
    ],
    [
        {"text": "🎭 OliOli Children's Museum", "callback_data": "park_563"}
    ],
    [
        {"text": "🖼️ Infinity des Lumières", "callback_data": "park_564"}
    ],
    [
        {"text": "🔙 К категориям парков", "callback_data": "cat_500"}
    ]
]
```

---

## Функция обработки навигации по категориям

```python
# Основная навигационная структура
PARKS_NAVIGATION = {
    "500": {
        "title": "🎢 ПАРКИ В ДУБАЕ",
        "message": get_parks_main_message,
        "keyboard": keyboard_500,
        "subcategories": ["510", "520", "530", "540", "550", "560"]
    },
    "510": {
        "title": "🎡 Парки развлечений",
        "message": get_entertainment_parks_message,
        "keyboard": keyboard_510,
        "parent": "500",
        "items": ["511", "512", "513", "514", "515"]
    },
    "520": {
        "title": "🌊 Аквапарки",
        "message": get_waterparks_message,
        "keyboard": keyboard_520,
        "parent": "500",
        "items": ["521", "522", "523", "524"]
    },
    # ... остальные категории
}

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def handle_category_navigation(call):
    """Универсальный обработчик навигации по категориям"""

    category_id = call.data.replace("cat_", "")

    if category_id not in PARKS_NAVIGATION:
        bot.answer_callback_query(call.id, "❌ Категория не найдена")
        return

    category = PARKS_NAVIGATION[category_id]

    # Получаем текст сообщения
    message_text = category["message"]()

    # Создаём клавиатуру
    keyboard = InlineKeyboardMarkup()
    for row in category["keyboard"]:
        buttons = [InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"]) for btn in row]
        keyboard.row(*buttons)

    # Отправляем сообщение
    bot.edit_message_text(
        message_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    # Подтверждение
    bot.answer_callback_query(call.id)
```

---

## Комбо-билеты со скидкой

```python
@bot.callback_query_handler(func=lambda call: call.data == "combo_tickets_500")
def show_combo_tickets(call):
    """Показывает специальные комбо-предложения"""

    message = """
🎫 КОМБО-БИЛЕТЫ СО СКИДКОЙ

Посетите несколько парков по специальной цене! Экономьте до 40% при покупке комбо-пакетов.

💎 ПОПУЛЯРНЫЕ КОМБО:

1️⃣ MEGA COMBO (5 парков)
🎡 Motiongate + 🧱 Legoland + 💦 Legoland Water + 💃 Bollywood + 🌊 Laguna
💰 Цена: 895 AED (вместо 1495 AED)
💵 Экономия: 600 AED (40%)
⏰ Срок действия: 7 дней

2️⃣ AQUA ADVENTURE
🌴 Aquaventure + 🐠 Lost Chambers Aquarium
💰 Цена: 425 AED (вместо 520 AED)
💵 Экономия: 95 AED (18%)
⏰ Срок действия: 1 день

3️⃣ FAMILY FUN
🎭 IMG Worlds + 🌊 Wild Wadi
💰 Цена: 550 AED (вместо 690 AED)
💵 Экономия: 140 AED (20%)
⏰ Срок действия: 3 дня

4️⃣ DUBAI PARKS 2-DAY
Любые 2 парка в Dubai Parks and Resorts
💰 Цена: 395 AED
💵 Экономия: 200 AED
⏰ Срок действия: 2 дня (подряд)

5️⃣ ABU DHABI COMBO
🏎️ Ferrari World + ⚡ Warner Bros World
💰 Цена: 650 AED (вместо 790 AED)
💵 Экономия: 140 AED
⏰ Срок действия: 2 дня

📌 УСЛОВИЯ:
• Дети до 3 лет - бесплатно
• Билеты именные, передача запрещена
• Возврат возможен за 48 часов до визита
• Электронные билеты - моментальная доставка на email

🎁 БОНУС: При покупке комбо от 800 AED - трансфер в подарок!
"""

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🛒 Купить Mega Combo", callback_data="buy_combo_mega"),
        InlineKeyboardButton("🛒 Aqua Adventure", callback_data="buy_combo_aqua")
    )
    keyboard.row(
        InlineKeyboardButton("🛒 Family Fun", callback_data="buy_combo_family"),
        InlineKeyboardButton("🛒 Dubai Parks 2-Day", callback_data="buy_combo_dp2")
    )
    keyboard.row(
        InlineKeyboardButton("🛒 Abu Dhabi Combo", callback_data="buy_combo_abudhabi")
    )
    keyboard.row(
        InlineKeyboardButton("💬 Консультация по выбору", callback_data="consult_combo"),
        InlineKeyboardButton("🔙 К паркам", callback_data="cat_500")
    )

    bot.edit_message_text(
        message,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )
```

---

## Breadcrumbs (хлебные крошки) для навигации

```python
def get_breadcrumbs(category_id):
    """Создаёт цепочку навигации"""

    breadcrumbs = []
    current = category_id

    while current:
        category = PARKS_NAVIGATION.get(current)
        if not category:
            break

        breadcrumbs.insert(0, {
            "id": current,
            "title": category["title"]
        })

        current = category.get("parent")

    # Формируем строку
    crumb_text = " → ".join([crumb["title"] for crumb in breadcrumbs])
    return f"📍 {crumb_text}\n\n"

# Использование:
# 📍 🎢 ПАРКИ В ДУБАЕ → 🎡 Парки развлечений → 🎭 IMG Worlds of Adventure
```
