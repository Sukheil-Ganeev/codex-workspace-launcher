"""
ПРИМЕР: Интеграция Claude API в VIP-DXB-RUS Telegram бота

Этот модуль демонстрирует как использовать Claude для:
1. Ответов на вопросы пользователей о турах и услугах
2. Обработки сложных запросов с контекстом базы знаний
3. Персонализированных рекомендаций экскурсий
4. Автоматической обработки бронирований

Требования:
pip install anthropic python-telegram-bot python-dotenv
"""

import os
import json
from anthropic import Anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация Claude API
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# База знаний бота (в реальности это будет отдельная БД)
KNOWLEDGE_BASE = {
    "tours": {
        "101": {
            "title": "Современный Дубай",
            "description": "Обзорная экскурсия по главным достопримечательностям",
            "price_group": 250,
            "price_private": 800,
            "duration": "4-5 часов",
            "highlights": ["Бурдж Халифа", "Дубай Молл", "Поющие фонтаны", "Дубай Марина", "Пальма Джумейра"],
            "best_for": ["семьи", "первый раз в Дубае", "фотографы"],
            "schedule": ["09:00-14:00", "16:00-21:00"]
        },
        "102": {
            "title": "Старый Дубай",
            "description": "Погружение в аутентичную культуру и историю эмирата",
            "price_group": 220,
            "price_private": 700,
            "duration": "3-4 часа",
            "highlights": ["Золотой рынок", "Рынок специй", "Музей Дубая", "Район Аль-Фахиди"],
            "best_for": ["ценители истории", "любители шопинга", "культурный туризм"],
            "schedule": ["09:00-13:00", "15:00-19:00"]
        },
        "201": {
            "title": "Сафари в пустыне",
            "description": "Экстремальная поездка по дюнам с ужином и шоу",
            "price_group": 280,
            "price_private": 950,
            "duration": "6 часов",
            "highlights": ["Дюн-бейшинг", "Катание на верблюдах", "Шоу танца живота", "Барбекю-ужин"],
            "best_for": ["любители приключений", "романтики", "семьи с детьми 7+"],
            "schedule": ["15:00-21:00"]
        }
    },
    "parks": {
        "511": {
            "title": "IMG Worlds of Adventure",
            "type": "Парк развлечений",
            "price_adult": 310,
            "price_child": 265,
            "features": ["крытый парк", "Marvel зона", "зона динозавров", "экстремальные горки"],
            "best_for": ["семьи с детьми 6+", "любители Marvel", "в жаркую погоду"]
        },
        "521": {
            "title": "Aquaventure Waterpark",
            "type": "Аквапарк",
            "price_adult": 370,
            "price_child": 325,
            "features": ["водные горки", "пляж", "аквариум", "зона для малышей"],
            "best_for": ["семьи с детьми", "любители водных развлечений", "жаркая погода"]
        }
    },
    "general_info": {
        "best_months": ["октябрь", "ноябрь", "декабрь", "январь", "февраль", "март", "апрель"],
        "hot_months": ["июнь", "июль", "август"],
        "currency": "AED (дирхам ОАЭ)",
        "language": "арабский (английский широко распространён)",
        "working_days": "Воскресенье-четверг (пятница-суббота - выходные)",
        "visa": "Для россиян - бесплатная по прилёту на 90 дней"
    }
}

# Few-shot примеры для Claude (учим бота правильным ответам)
FEW_SHOT_EXAMPLES = [
    {
        "user": "Какую экскурсию выбрать для первого визита в Дубай?",
        "assistant": """Для первого визита в Дубай я рекомендую экскурсию **"Современный Дубай"** (tour_id: 101).

Почему именно эта экскурсия:
• Вы увидите все знаковые достопримечательности: Бурдж Халифа, Дубай Молл, Поющие фонтаны, Дубай Марину и Пальму Джумейра
• Продолжительность 4-5 часов - оптимально, чтобы не устать
• Вечерний тур особенно хорош - увидите шоу фонтанов и город в огнях

Стоимость:
- Групповая: от 250 AED/чел
- Индивидуальная: от 800 AED (1-3 чел)

Хотите забронировать? [КНОПКА: book_GT_101]"""
    },
    {
        "user": "Куда сходить с ребёнком 5 лет в Дубае?",
        "assistant": """Отличный вопрос! Для ребёнка 5 лет в Дубае масса возможностей:

🎢 **Парки развлечений:**
• **IMG Worlds of Adventure** - крытый парк с зоной Cartoon Network (идеально для этого возраста)
• **Legoland Dubai** - специально для детей 2-12 лет

🌊 **Аквапарки:**
• **Aquaventure** - есть специальная детская зона Splashers
• **Legoland Water Park** - мягкие горки, безопасно для малышей

🎨 **Образовательные:**
• **OliOli Children's Museum** - интерактивный музей для детей
• **The Green Planet** - тропический лес с животными

🏙️ **Экскурсии:**
• "Современный Дубай" (вечерний тур с фонтанами - дети в восторге!)
• Океанариум в Дубай Молле

Что бы вы хотели посмотреть подробнее? [КНОПКИ: парки / экскурсии / океанариум]"""
    },
    {
        "user": "Сколько стоит подняться на Бурдж Халифа?",
        "assistant": """Стоимость билетов на Бурдж Халифа зависит от уровня и времени:

**At The Top (уровни 124-125):**
• Prime hours (15:00-18:00): от 244 AED
• Non-prime hours: от 149 AED

**At The Top SKY (уровень 148):**
• От 378 AED

**Важные детали:**
• Дети до 4 лет - бесплатно
• Билеты лучше покупать онлайн заранее (дешевле и без очередей)
• Рекомендуем заходить на закате - увидите город и днём, и в огнях

💡 **Совет:** Если берёте экскурсию "Современный Дубай", билеты на башню оплачиваются отдельно, но гид поможет с покупкой и расскажет всё об истории башни.

Хотите забронировать экскурсию с посещением Бурдж Халифа? [КНОПКА: book_GT_101]"""
    }
]


class ClaudeTourAssistant:
    """Ассистент на базе Claude для помощи туристам"""

    def __init__(self):
        self.client = anthropic
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 1024

    def create_system_prompt(self):
        """Создаёт системный промпт с базой знаний"""

        return f"""Ты - ассистент VIP-DXB-RUS, профессионального туристического агентства в Дубае.

ТВОЯ РОЛЬ:
- Помогать туристам выбирать экскурсии, парки и развлечения
- Отвечать на вопросы о Дубае, ОАЭ и наших услугах
- Давать персонализированные рекомендации
- Быть дружелюбным, профессиональным и информативным

БАЗА ЗНАНИЙ:
{json.dumps(KNOWLEDGE_BASE, ensure_ascii=False, indent=2)}

ПРАВИЛА ОТВЕТОВ:
1. Всегда отвечай на русском языке
2. Если знаешь tour_id или park_id - используй формат [КНОПКА: callback_data]
3. Цены указывай в AED (дирхамах ОАЭ)
4. Если не уверен в информации - честно скажи об этом
5. Предлагай альтернативы, если подходящего варианта нет
6. Будь кратким, но информативным (максимум 300 слов)
7. Используй emoji для визуальной привлекательности (умеренно)

СПЕЦИАЛЬНЫЕ ВОЗМОЖНОСТИ:
- Если пользователь хочет забронировать - используй [КНОПКА: book_TYPE_ID]
  где TYPE = GT (группа) или PT (индивидуальная)
- Для показа фото: [КНОПКА: photos_ID]
- Для отзывов: [КНОПКА: reviews_ID]

Помни: ты представляешь премиум-сервис, поэтому ответы должны быть профессиональными!"""

    def ask_claude(self, user_question: str, conversation_history: list = None):
        """Отправляет вопрос в Claude и получает ответ"""

        # Формируем историю разговора
        messages = []

        # Добавляем few-shot примеры
        for example in FEW_SHOT_EXAMPLES:
            messages.append({
                "role": "user",
                "content": example["user"]
            })
            messages.append({
                "role": "assistant",
                "content": example["assistant"]
            })

        # Добавляем историю текущего разговора (если есть)
        if conversation_history:
            messages.extend(conversation_history)

        # Добавляем текущий вопрос
        messages.append({
            "role": "user",
            "content": user_question
        })

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.create_system_prompt(),
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            print(f"Ошибка Claude API: {e}")
            return "Извините, временные технические проблемы. Попробуйте задать вопрос позже или напишите нам напрямую."

    def parse_response_for_buttons(self, claude_response: str):
        """Парсит ответ Claude и извлекает кнопки"""

        import re

        # Ищем паттерн [КНОПКА: callback_data]
        button_pattern = r'\[КНОПКА: ([^\]]+)\]'
        buttons = re.findall(button_pattern, claude_response)

        # Убираем маркеры кнопок из текста
        clean_text = re.sub(button_pattern, '', claude_response).strip()

        # Создаём кнопки
        keyboard = []
        for button_data in buttons:
            if button_data.startswith('book_GT_'):
                tour_id = button_data.replace('book_GT_', '')
                keyboard.append([InlineKeyboardButton(
                    "📅 Забронировать групповую",
                    callback_data=button_data
                )])
            elif button_data.startswith('book_PT_'):
                tour_id = button_data.replace('book_PT_', '')
                keyboard.append([InlineKeyboardButton(
                    "👤 Индивидуальная экскурсия",
                    callback_data=button_data
                )])
            elif button_data.startswith('photos_'):
                keyboard.append([InlineKeyboardButton(
                    "📸 Фото",
                    callback_data=button_data
                )])
            elif button_data.startswith('reviews_'):
                keyboard.append([InlineKeyboardButton(
                    "⭐️ Отзывы",
                    callback_data=button_data
                )])

        # Добавляем кнопку "Задать ещё вопрос"
        keyboard.append([InlineKeyboardButton(
            "❓ Задать ещё вопрос",
            callback_data="ask_claude"
        )])

        return clean_text, InlineKeyboardMarkup(keyboard) if keyboard else None


# Инициализация ассистента
claude_assistant = ClaudeTourAssistant()

# Хранилище для истории разговоров пользователей
user_conversations = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""

    welcome_text = """
👋 Добро пожаловать в VIP-DXB-RUS!

Я - ваш персональный AI-ассистент по Дубаю. Помогу:
• Выбрать экскурсии
• Подобрать парки развлечений
• Ответить на вопросы о Дубае
• Забронировать билеты

💬 Просто задайте вопрос, и я постараюсь помочь!

Примеры вопросов:
• "Какую экскурсию выбрать для первого визита?"
• "Куда сходить с детьми 7 и 10 лет?"
• "Сколько стоит сафари в пустыне?"
• "Когда лучше ехать в Дубай?"
"""

    keyboard = [
        [
            InlineKeyboardButton("🏙️ Экскурсии", callback_data="cat_100"),
            InlineKeyboardButton("🎢 Парки", callback_data="cat_500")
        ],
        [
            InlineKeyboardButton("❓ Задать вопрос AI", callback_data="ask_claude")
        ]
    ]

    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_claude_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для вопросов к Claude"""

    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat.id
        await context.bot.send_message(
            chat_id,
            "💬 Задайте ваш вопрос о Дубае, экскурсиях или развлечениях:"
        )

    # Помечаем, что следующее сообщение - вопрос к Claude
    context.user_data['waiting_for_claude_question'] = True


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""

    user_id = update.effective_user.id
    user_message = update.message.text

    # Проверяем, ждём ли мы вопрос к Claude
    if context.user_data.get('waiting_for_claude_question'):

        # Показываем индикатор печатания
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # Получаем историю разговора
        conversation_history = user_conversations.get(user_id, [])

        # Спрашиваем у Claude
        claude_response = claude_assistant.ask_claude(
            user_message,
            conversation_history
        )

        # Сохраняем в историю
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        conversation_history.append({
            "role": "assistant",
            "content": claude_response
        })

        # Ограничиваем историю последними 10 сообщениями
        user_conversations[user_id] = conversation_history[-10:]

        # Парсим ответ на предмет кнопок
        clean_text, keyboard = claude_assistant.parse_response_for_buttons(claude_response)

        # Отправляем ответ
        await update.message.reply_text(
            clean_text,
            reply_markup=keyboard,
            parse_mode=None
        )

        # Сбрасываем флаг
        context.user_data['waiting_for_claude_question'] = False

    else:
        # Обычное сообщение - предлагаем меню
        keyboard = [
            [
                InlineKeyboardButton("❓ Задать вопрос AI", callback_data="ask_claude")
            ],
            [
                InlineKeyboardButton("🏙️ Экскурсии", callback_data="cat_100"),
                InlineKeyboardButton("🎢 Парки", callback_data="cat_500")
            ]
        ]

        await update.message.reply_text(
            "Выберите раздел или задайте вопрос:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def smart_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Умные рекомендации на основе предпочтений"""

    query = update.callback_query
    await query.answer()

    # Получаем данные пользователя (в реальности из БД)
    user_data = {
        "previous_bookings": ["101"],  # Был на "Современный Дубай"
        "interests": ["семья", "фотография"],
        "budget": "medium"
    }

    # Формируем вопрос к Claude
    question = f"""Пользователь уже был на экскурсии: {user_data['previous_bookings']}
Интересы: {user_data['interests']}
Бюджет: {user_data['budget']}

Порекомендуй 3 лучших варианта для следующего визита."""

    claude_response = claude_assistant.ask_claude(question)
    clean_text, keyboard = claude_assistant.parse_response_for_buttons(claude_response)

    await query.edit_message_text(
        f"🎯 ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ\n\n{clean_text}",
        reply_markup=keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""

    help_text = """
📖 СПРАВКА ПО БОТУ

🤖 **Команды:**
/start - Главное меню
/help - Эта справка
/tours - Все экскурсии
/parks - Все парки
/clear - Очистить историю чата с AI

💬 **Как пользоваться AI-ассистентом:**
1. Нажмите "❓ Задать вопрос AI"
2. Напишите ваш вопрос
3. Получите персонализированный ответ

🎯 **Что умеет AI:**
• Рекомендовать экскурсии и парки
• Отвечать на вопросы о Дубае
• Помогать с выбором под ваш бюджет
• Учитывать возраст детей и интересы

📞 **Поддержка:**
@vipdxbrus_support
"""

    await update.message.reply_text(help_text)


async def clear_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка истории разговора с Claude"""

    user_id = update.effective_user.id
    if user_id in user_conversations:
        del user_conversations[user_id]

    await update.message.reply_text(
        "✅ История разговора очищена. Можете начать новый диалог с AI!"
    )


def main():
    """Запуск бота"""

    # Создаём приложение
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_history_command))

    app.add_handler(CallbackQueryHandler(ask_claude_handler, pattern="^ask_claude$"))
    app.add_handler(CallbackQueryHandler(smart_recommendations, pattern="^smart_recommend$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен с Claude API интеграцией!")

    # Запускаем polling
    app.run_polling()


if __name__ == "__main__":
    main()


"""
ПРИМЕР .env ФАЙЛА:

ANTHROPIC_API_KEY=sk-ant-api03-xxx
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Опционально
DATABASE_URL=postgresql://user:pass@localhost/vipdxbrus
REDIS_URL=redis://localhost:6379
"""


"""
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ В КОДЕ:

1. Простой вопрос к Claude:
---
response = claude_assistant.ask_claude("Какая погода в Дубае в июле?")
print(response)

2. С историей разговора:
---
history = [
    {"role": "user", "content": "Еду с семьёй"},
    {"role": "assistant", "content": "Сколько человек?"},
]
response = claude_assistant.ask_claude("3 взрослых и 2 детей", history)

3. Персонализированные рекомендации:
---
user_profile = {
    "budget": "high",
    "interests": ["экстрим", "водные развлечения"],
    "age_group": "25-35"
}

question = f"Порекомендуй активности для: {json.dumps(user_profile, ensure_ascii=False)}"
response = claude_assistant.ask_claude(question)
"""


"""
РАСШИРЕННЫЕ ВОЗМОЖНОСТИ:

1. Многоязычность:
---
Добавьте в системный промпт определение языка:
"Определи язык вопроса и отвечай на том же языке (русский/английский/арабский)"

2. Анализ настроения:
---
Используйте Claude для определения удовлетворённости клиента:
"Проанализируй настроение клиента в этом сообщении: [текст]"

3. Автоматическая категоризация:
---
"Определи категорию вопроса: экскурсии/парки/общая_информация/бронирование"

4. Генерация персональных маршрутов:
---
"Составь 3-дневный маршрут по Дубаю для семьи с детьми 5 и 8 лет, бюджет $1000"

5. Обработка жалоб:
---
"Клиент недоволен. Составь профессиональный ответ и предложи компенсацию"
"""
