#!/usr/bin/env python3
"""
VK Community Post Template
Шаблон для публикации постов в VK-сообществе
"""

import vk_api
import os
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

TOKEN = os.getenv('VK_COMMUNITY_TOKEN')
GROUP_ID = int(os.getenv('VK_GROUP_ID'))

# Инициализация
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

def post_to_wall(message, attachments=None):
    """Публикация поста на стене сообщества"""
    try:
        response = vk.wall.post(
            owner_id=GROUP_ID,
            from_group=1,
            message=message,
            attachments=attachments
        )
        print(f"✅ Пост опубликован: post_id={response['post_id']}")
        return response
    except vk_api.exceptions.ApiError as e:
        print(f"❌ Ошибка API: {e}")
        return None

# Пример использования
if __name__ == '__main__':
    message = """
🏜️ Desert Safari в Дубае

Включено:
✅ Трансфер от отеля
✅ Катание на джипах по дюнам
✅ Ужин BBQ (шведский стол)
✅ Шоу (танец живота, танура)

💰 Цена: 250 AED/чел
⏱ Время: 15:00-21:00

📞 Бронирование: +971 50 123 4567
    """

    post_to_wall(message.strip())
