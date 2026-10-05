#!/usr/bin/env python3
"""
Telegram Bot для транскрипции голосовых сообщений
Production-ready version для туристического бизнеса ОАЭ
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from bot.handlers import (
    start_command,
    help_command,
    stats_command,
    language_command,
    admin_command,
    voice_handler,
    error_handler
)
from bot.database import Database

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Запуск бота"""

    # Проверка переменных окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_key = os.getenv('YANDEX_API_KEY')
    folder_id = os.getenv('YANDEX_FOLDER_ID')

    if not all([bot_token, api_key, folder_id]):
        logger.error("Missing required environment variables")
        logger.error("Required: TELEGRAM_BOT_TOKEN, YANDEX_API_KEY, YANDEX_FOLDER_ID")
        sys.exit(1)

    # Инициализация базы данных
    db = Database('data/bot.db')
    db.initialize()

    # Создание приложения
    application = Application.builder().token(bot_token).build()

    # Сохранение зависимостей в context
    application.bot_data['db'] = db
    application.bot_data['yandex_api_key'] = api_key
    application.bot_data['yandex_folder_id'] = folder_id
    application.bot_data['admin_ids'] = [
        int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()
    ]

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("admin", admin_command))

    # Обработчик голосовых сообщений
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Определение режима работы
    bot_mode = os.getenv('BOT_MODE', 'polling').lower()

    if bot_mode == 'webhook':
        webhook_url = os.getenv('WEBHOOK_URL')
        webhook_port = int(os.getenv('WEBHOOK_PORT', 8443))

        if not webhook_url:
            logger.error("WEBHOOK_URL is required for webhook mode")
            sys.exit(1)

        logger.info(f"Starting bot in webhook mode: {webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=webhook_port,
            url_path="webhook",
            webhook_url=f"{webhook_url}/webhook"
        )
    else:
        logger.info("Starting bot in polling mode")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    # Создание необходимых директорий
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    main()
