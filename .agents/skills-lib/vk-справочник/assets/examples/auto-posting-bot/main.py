#!/usr/bin/env python3
"""
VK Auto-Posting Bot
===================

Автоматическая публикация туров в VK-сообщество по расписанию.

"""

import vk_api
from vk_api.upload import VkUpload
import schedule
import time
import json
import logging
import requests
import os
from datetime import datetime
from config import *

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/autopost.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ========== VK ПОДКЛЮЧЕНИЕ ==========

try:
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    upload = VkUpload(vk_session)
    logger.info("✅ Подключено к VK API")
except Exception as e:
    logger.error(f"❌ Ошибка подключения к VK: {e}")
    exit(1)

# ========== ФУНКЦИИ ==========

def load_tours():
    """Загрузить данные туров из JSON"""
    try:
        with open(TOURS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['tours']
    except FileNotFoundError:
        logger.error(f"❌ Файл {TOURS_DATA_FILE} не найден!")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        return []


def download_photo(url, tour_name):
    """
    Скачать фото по URL

    Args:
        url (str): URL фотографии
        tour_name (str): Название тура (для имени файла)

    Returns:
        str: Путь к скачанному файлу или None
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Создать временную директорию
        os.makedirs('temp', exist_ok=True)

        # Сохранить файл
        filename = f"temp/{tour_name.replace(' ', '_')}_{int(time.time())}.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)

        logger.info(f"📥 Фото скачано: {filename}")
        return filename

    except Exception as e:
        logger.error(f"❌ Ошибка скачивания фото: {e}")
        return None


def upload_photo_to_vk(photo_path):
    """
    Загрузить фото в VK

    Args:
        photo_path (str): Путь к файлу

    Returns:
        str: Attachment строка или None
    """
    try:
        photo = upload.photo_wall(photo_path, group_id=GROUP_ID)[0]
        attachment = f"photo{photo['owner_id']}_{photo['id']}"
        logger.info(f"📤 Фото загружено в VK: {attachment}")

        # Удалить временный файл
        if os.path.exists(photo_path):
            os.remove(photo_path)

        return attachment

    except Exception as e:
        logger.error(f"❌ Ошибка загрузки фото в VK: {e}")
        return None


def format_tour_post(tour):
    """
    Форматировать текст поста

    Args:
        tour (dict): Данные тура

    Returns:
        str: Отформатированный текст
    """
    text = f"""🌴 {tour['name']}

{tour['description']}

💵 Цена: {tour['price']}"""

    # Добавить дополнительные поля, если есть
    if 'duration' in tour:
        text += f"\n⏱️ Длительность: {tour['duration']}"

    if 'included' in tour:
        text += f"\n\n✨ Включено:\n"
        for item in tour['included']:
            text += f"   • {item}\n"

    text += f"""
📲 Бронирование:
   • WhatsApp: +971-50-123-4567
   • Telegram: @dubaitours
   • VK: vk.me/dubaitours

#ДубайТуры #ОАЭ #Туризм #{tour['name'].replace(' ', '')}"""

    return text


def post_tour(tour, dry_run=False):
    """
    Опубликовать тур в VK

    Args:
        tour (dict): Данные тура
        dry_run (bool): Тестовый режим (без публикации)

    Returns:
        int: ID поста или None
    """
    logger.info(f"📝 Публикация тура: {tour['name']}")

    try:
        # Скачать и загрузить фото
        attachments = []
        if 'photo' in tour and tour['photo']:
            photo_path = download_photo(tour['photo'], tour['name'])
            if photo_path:
                attachment = upload_photo_to_vk(photo_path)
                if attachment:
                    attachments.append(attachment)

                # Пауза (rate limiting)
                time.sleep(RATE_LIMIT_DELAY)

        # Форматировать текст
        message = format_tour_post(tour)

        if dry_run:
            logger.info(f"🔍 [DRY RUN] Пост:\n{message}")
            logger.info(f"🔍 [DRY RUN] Attachments: {','.join(attachments)}")
            return None

        # Публикация
        post_id = vk.wall.post(
            owner_id=-GROUP_ID,
            from_group=1,
            message=message,
            attachments=','.join(attachments) if attachments else None
        )['post_id']

        post_url = f"https://vk.com/wall-{GROUP_ID}_{post_id}"
        logger.info(f"✅ Опубликован пост {post_id}: {tour['name']}")
        logger.info(f"🔗 URL: {post_url}")

        return post_id

    except vk_api.exceptions.ApiError as e:
        logger.error(f"❌ VK API Error: {e}")
        return None

    except Exception as e:
        logger.error(f"❌ Ошибка публикации: {e}")
        return None


def post_daily_tour():
    """Опубликовать ежедневный тур"""
    logger.info("🚀 Запуск ежедневной публикации...")

    tours = load_tours()
    if not tours:
        logger.warning("⚠️ Нет туров для публикации")
        return

    # Выбрать тур для публикации (по расписанию)
    current_time = datetime.now().strftime('%H:%M')

    for tour in tours:
        if tour.get('schedule') == current_time:
            post_tour(tour)
            time.sleep(RATE_LIMIT_DELAY)


def post_all_tours(dry_run=False):
    """
    Опубликовать все туры (для тестирования)

    Args:
        dry_run (bool): Тестовый режим
    """
    logger.info("🚀 Публикация всех туров...")

    tours = load_tours()
    if not tours:
        logger.warning("⚠️ Нет туров для публикации")
        return

    success_count = 0
    for tour in tours:
        result = post_tour(tour, dry_run=dry_run)
        if result:
            success_count += 1

        # Пауза (rate limiting)
        time.sleep(RATE_LIMIT_DELAY)

    logger.info(f"✅ Публикация завершена: {success_count}/{len(tours)} успешно")


# ========== РАСПИСАНИЕ ==========

def setup_schedule():
    """Настроить расписание публикаций"""
    tours = load_tours()

    for tour in tours:
        if 'schedule' in tour:
            schedule_time = tour['schedule']
            schedule.every().day.at(schedule_time).do(post_daily_tour)
            logger.info(f"⏰ Запланирована публикация '{tour['name']}' в {schedule_time}")


# ========== MAIN ==========

def main():
    """Основная функция"""
    import sys

    # Парсинг аргументов
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            # Опубликовать все туры
            post_all_tours()
            return

        elif sys.argv[1] == '--dry-run':
            # Тестовый режим
            logger.info("🔍 Тестовый режим (без публикации)")
            post_all_tours(dry_run=True)
            return

        elif sys.argv[1] == '--help':
            print("""
VK Auto-Posting Bot

Использование:
  python main.py              # Запуск по расписанию
  python main.py --all        # Опубликовать все туры сейчас
  python main.py --dry-run    # Тестовый режим (без публикации)
  python main.py --help       # Эта справка
            """)
            return

    # Запуск по расписанию
    logger.info("🤖 VK Auto-Posting Bot запущен")
    logger.info(f"📋 Группа ID: {GROUP_ID}")
    logger.info(f"⏰ Часовой пояс: {TIMEZONE}")

    setup_schedule()

    logger.info("⏳ Ожидание расписания...")
    logger.info("💡 Нажмите Ctrl+C для остановки\n")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверка каждую минуту


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Бот остановлен (Ctrl+C)")
    except Exception as e:
        logger.error(f"\n❌ Критическая ошибка: {e}")
