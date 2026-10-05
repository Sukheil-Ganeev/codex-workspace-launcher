#!/usr/bin/env python3
"""
VK Long Poll Bot Template
==========================

Шаблон бота для VK сообществ с использованием Long Poll API.

Возможности:
- Автоответы на сообщения
- Клавиатуры с кнопками
- Обработка payload
- Простая логика команд

Установка:
----------
pip install vk-api python-dotenv

Настройка:
----------
1. Создать .env файл:
   VK_TOKEN=your_community_token
   GROUP_ID=your_group_id

2. Включить сообщения сообщества в настройках VK группы
3. Запустить: python bot-longpoll-template.py

"""

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv
import os
import json

# Загрузить переменные окружения
load_dotenv()

# ========== НАСТРОЙКИ ==========
VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', 0))

if not VK_TOKEN:
    raise ValueError("❌ VK_TOKEN не найден в .env файле!")

# ========== ПОДКЛЮЧЕНИЕ ==========
print("🔌 Подключение к VK API...")
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
print("✅ Подключено!")

# ========== КЛАВИАТУРЫ ==========

def get_main_keyboard():
    """
    Главное меню с основными кнопками

    Returns:
        str: JSON клавиатуры
    """
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('📋 Услуги', VkKeyboardColor.PRIMARY)
    keyboard.add_button('💬 Поддержка', VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('ℹ️ О компании', VkKeyboardColor.SECONDARY)
    keyboard.add_button('📞 Контакты', VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def get_services_keyboard():
    """
    Меню услуг

    Returns:
        str: JSON клавиатуры
    """
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('🌴 Экскурсии', VkKeyboardColor.POSITIVE,
                       payload={'action': 'tours'})
    keyboard.add_button('🎫 Билеты', VkKeyboardColor.POSITIVE,
                       payload={'action': 'tickets'})
    keyboard.add_line()
    keyboard.add_button('🚗 Трансферы', VkKeyboardColor.POSITIVE,
                       payload={'action': 'transfers'})
    keyboard.add_button('🛥️ Яхты', VkKeyboardColor.POSITIVE,
                       payload={'action': 'yachts'})
    keyboard.add_line()
    keyboard.add_button('◀️ Назад', VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def get_back_keyboard():
    """
    Клавиатура с кнопкой "Назад"

    Returns:
        str: JSON клавиатуры
    """
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('◀️ Назад', VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

# ========== ФУНКЦИИ ОТПРАВКИ ==========

def send_message(user_id, message, keyboard=None):
    """
    Отправить сообщение пользователю

    Args:
        user_id (int): ID пользователя VK
        message (str): Текст сообщения
        keyboard (str, optional): JSON клавиатуры
    """
    try:
        vk.messages.send(
            user_id=user_id,
            message=message,
            keyboard=keyboard,
            random_id=0
        )
    except vk_api.exceptions.ApiError as e:
        print(f"❌ Ошибка отправки сообщения: {e}")


# ========== ОБРАБОТЧИКИ КОМАНД ==========

def handle_start(user_id):
    """Приветствие нового пользователя"""
    message = """👋 Добро пожаловать!

Я бот компании Dubai Tours. Помогу вам с:
• Бронированием экскурсий
• Покупкой билетов
• Заказом трансферов
• Арендой яхт

Выберите интересующий раздел:"""

    send_message(user_id, message, get_main_keyboard())
    print(f"👤 Новый пользователь: {user_id}")


def handle_services(user_id):
    """Показать меню услуг"""
    message = "📋 Выберите категорию услуг:"
    send_message(user_id, message, get_services_keyboard())


def handle_tours(user_id):
    """Информация об экскурсиях"""
    message = """🌴 Наши экскурсии:

1️⃣ Desert Safari - $80/чел
   Джип-сафари по пустыне с ужином BBQ

2️⃣ City Tour - $60/чел
   Обзорная экскурсия по Дубаю

3️⃣ Abu Dhabi Tour - $70/чел
   Поездка в столицу ОАЭ

4️⃣ Burj Khalifa - $45/чел
   Билеты на смотровую площадку

📲 Для бронирования напишите номер экскурсии или свяжитесь с менеджером."""

    send_message(user_id, message, get_back_keyboard())


def handle_tickets(user_id):
    """Информация о билетах"""
    message = """🎫 Билеты в парки и аттракционы:

🎢 IMG Worlds of Adventure - $75
🎪 Dubai Parks & Resorts - $85
🌊 Aquaventure Waterpark - $80
🎿 Ski Dubai - $70
🏰 Global Village - $20

📲 Укажите название парка для бронирования."""

    send_message(user_id, message, get_back_keyboard())


def handle_transfers(user_id):
    """Информация о трансферах"""
    message = """🚗 Трансферы по Дубаю:

✈️ Аэропорт → Отель - $35
🏨 Отель → Аэропорт - $35
🌆 Трансферы по городу - от $25/час

🚙 Доступны автомобили:
   • Economy (седан)
   • Business (премиум)
   • Luxury (представительский класс)

📲 Напишите откуда-куда нужен трансфер."""

    send_message(user_id, message, get_back_keyboard())


def handle_yachts(user_id):
    """Информация о яхтах"""
    message = """🛥️ Аренда яхт в Дубае:

⛵ Малая яхта (до 10 чел) - $150/2ч
🚤 Средняя яхта (до 20 чел) - $300/2ч
🛥️ Большая яхта (до 40 чел) - $600/2ч
🚢 Мега-яхта (до 100 чел) - $1200/2ч

✨ В стоимость входит:
   • Капитан и команда
   • Напитки и закуски
   • Музыкальная система

📲 Укажите количество гостей для подбора яхты."""

    send_message(user_id, message, get_back_keyboard())


def handle_about(user_id):
    """Информация о компании"""
    message = """ℹ️ О компании Dubai Tours

Мы - семейная компания, специализирующаяся на туристических услугах в ОАЭ.

🏆 Наши преимущества:
   • 5+ лет опыта
   • Русскоязычные гиды
   • Лучшие цены на рынке
   • 1000+ довольных клиентов

📍 Офис: Dubai, Tecom (Barsha Heights)
🚇 Метро: Dubai Internet City

👥 Команда:
   • Сухейль - экскурсии и билеты
   • Марсель - аренда авто и трансферы
   • Муфамад - аренда яхт

🌟 Ваш надёжный партнёр в ОАЭ!"""

    send_message(user_id, message, get_back_keyboard())


def handle_contacts(user_id):
    """Контактная информация"""
    message = """📞 Наши контакты:

📱 WhatsApp: +971-50-123-4567
📧 Email: info@dubaitours.com
🌐 Сайт: www.dubaitours.com

📲 Telegram: @dubaitours
📸 Instagram: @dubaitours

⏰ Работаем: 24/7
💬 Отвечаем: в течение 5 минут

Пишите по любым вопросам!"""

    send_message(user_id, message, get_back_keyboard())


def handle_support(user_id):
    """Поддержка клиентов"""
    message = """💬 Поддержка клиентов

Напишите ваш вопрос, и наш менеджер ответит в течение 5 минут.

Или свяжитесь напрямую:
📱 WhatsApp: +971-50-123-4567
📞 Звонок: +971-50-123-4567

⏰ Работаем 24/7"""

    send_message(user_id, message, get_back_keyboard())


def handle_unknown_command(user_id, message_text):
    """Обработка неизвестных команд"""
    message = f"""❓ Команда не распознана: "{message_text}"

Используйте кнопки меню для навигации или напишите:
• "начать" - главное меню
• "помощь" - список команд"""

    send_message(user_id, message, get_main_keyboard())


# ========== MAIN LOOP ==========

def main():
    """
    Основной цикл бота

    Прослушивает события Long Poll и обрабатывает входящие сообщения
    """
    print("🤖 VK Long Poll бот запущен!")
    print(f"📋 Группа ID: {GROUP_ID}")
    print("⏳ Ожидание сообщений...\n")

    for event in longpoll.listen():
        # Новое сообщение боту
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_text = event.text.strip().lower()

            print(f"📨 Сообщение от {user_id}: {message_text}")

            # Обработка команд
            if message_text in ['начать', 'start', 'привет', 'hello']:
                handle_start(user_id)

            elif message_text in ['услуги', '📋 услуги']:
                handle_services(user_id)

            elif message_text in ['о компании', 'ℹ️ о компании', 'о нас']:
                handle_about(user_id)

            elif message_text in ['контакты', '📞 контакты']:
                handle_contacts(user_id)

            elif message_text in ['поддержка', '💬 поддержка', 'помощь']:
                handle_support(user_id)

            elif message_text in ['назад', '◀️ назад']:
                handle_start(user_id)

            # Обработка payload (кнопки с данными)
            elif event.payload:
                try:
                    payload = json.loads(event.payload)
                    action = payload.get('action')

                    if action == 'tours':
                        handle_tours(user_id)
                    elif action == 'tickets':
                        handle_tickets(user_id)
                    elif action == 'transfers':
                        handle_transfers(user_id)
                    elif action == 'yachts':
                        handle_yachts(user_id)
                    else:
                        handle_unknown_command(user_id, message_text)

                except json.JSONDecodeError:
                    print(f"⚠️ Ошибка парсинга payload: {event.payload}")
                    handle_unknown_command(user_id, message_text)

            # Неизвестная команда
            else:
                handle_unknown_command(user_id, message_text)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
