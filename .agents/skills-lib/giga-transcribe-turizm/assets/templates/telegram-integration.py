"""
Telegram бот с интеграцией Yandex SpeechKit

Функции:
- Распознавание голосовых сообщений
- Автоматическая транскрипция
- Поддержка команд
- Логирование

Требования:
    pip install python-telegram-bot requests python-dotenv

Использование:
    1. Создать бота через @BotFather
    2. Добавить TELEGRAM_BOT_TOKEN в .env
    3. python telegram-integration.py
"""

import os
import logging
import requests
import tempfile
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
SYNC_API_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY", "PASTE_YANDEX_CLOUD_API_KEY_HERE")
YANDEX_FOLDER_ID = os.getenv("YANDEX_CLOUD_FOLDER_ID", "b1gvu3q8k1kafqd3sk5f")


class SpeechKitTranscriber:
    """Транскрибер для Telegram голосовых сообщений"""

    def __init__(self, api_key: str, folder_id: str):
        """
        Инициализация транскрибера

        Args:
            api_key: API ключ Yandex Cloud
            folder_id: ID каталога Yandex Cloud
        """
        self.api_key = api_key
        self.folder_id = folder_id

    def transcribe_ogg(
        self,
        ogg_file_path: str,
        language: str = "ru-RU",
        model: str = "general"
    ) -> dict:
        """
        Транскрибирует OGG файл (формат Telegram)

        Args:
            ogg_file_path: Путь к OGG файлу
            language: Язык распознавания
            model: Модель SpeechKit

        Returns:
            Dict с результатом транскрипции
        """
        try:
            # Читаем файл
            with open(ogg_file_path, 'rb') as f:
                audio_data = f.read()

            # Параметры запроса
            params = {
                'folderId': self.folder_id,
                'lang': language,
                'model': model,
                'format': 'oggopus'
            }

            headers = {
                'Authorization': f'Api-Key {self.api_key}'
            }

            # Отправляем запрос
            response = requests.post(
                SYNC_API_URL,
                params=params,
                headers=headers,
                data=audio_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'text': result.get('result', ''),
                    'confidence': result.get('confidence', 0.0)
                }
            else:
                logger.error(f"Yandex API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API error: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Создаем экземпляр транскрибера
transcriber = SpeechKitTranscriber(YANDEX_API_KEY, YANDEX_FOLDER_ID)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🎙️ Привет! Я бот для распознавания голосовых сообщений.

Просто отправь мне голосовое сообщение, и я преобразую его в текст.

📋 Команды:
/start - Показать это сообщение
/help - Справка
/stats - Статистика

Powered by Yandex SpeechKit 🚀
    """
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
❓ Как использовать:

1. Запиши голосовое сообщение
2. Отправь его боту
3. Получи текст

⚙️ Поддержка:
• Язык: Русский, Английский
• Формат: OGG Opus (Telegram)
• Лимит: до 30 секунд

💡 Совет: Говори четко для лучшего распознавания!
    """
    await update.message.reply_text(help_text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    user_data = context.user_data

    total = user_data.get('total_transcriptions', 0)
    success = user_data.get('success_transcriptions', 0)

    stats_text = f"""
📊 Твоя статистика:

• Всего распознаваний: {total}
• Успешных: {success}
• Ошибок: {total - success}
    """

    await update.message.reply_text(stats_text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик голосовых сообщений

    1. Скачивает voice message
    2. Транскрибирует через Yandex SpeechKit
    3. Отправляет текст обратно
    """
    user = update.effective_user
    logger.info(f"Voice message from {user.username} ({user.id})")

    # Отправляем статус "печатает"
    await update.message.reply_chat_action("typing")

    # Получаем голосовое сообщение
    voice = update.message.voice

    # Проверяем длительность (лимит 30 сек для Sync API)
    if voice.duration > 30:
        await update.message.reply_text(
            "⚠️ Голосовое сообщение слишком длинное (больше 30 сек).\n"
            "Пожалуйста, отправь короче."
        )
        return

    try:
        # Скачиваем файл
        voice_file = await context.bot.get_file(voice.file_id)

        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
            temp_path = temp_file.name
            await voice_file.download_to_drive(temp_path)

        # Транскрибируем
        result = transcriber.transcribe_ogg(temp_path)

        # Удаляем временный файл
        Path(temp_path).unlink()

        # Обрабатываем результат
        if result['success']:
            text = result['text']
            confidence = result['confidence']

            # Обновляем статистику
            context.user_data['total_transcriptions'] = \
                context.user_data.get('total_transcriptions', 0) + 1
            context.user_data['success_transcriptions'] = \
                context.user_data.get('success_transcriptions', 0) + 1

            # Формируем ответ
            if text:
                response = f"🎙️ → 📝\n\n{text}"

                if confidence < 0.7:
                    response += f"\n\n⚠️ Низкая уверенность ({confidence:.0%}). Возможны ошибки."
            else:
                response = "🤷 Не удалось распознать речь. Попробуй говорить четче."

            await update.message.reply_text(response)

        else:
            # Обновляем статистику
            context.user_data['total_transcriptions'] = \
                context.user_data.get('total_transcriptions', 0) + 1

            await update.message.reply_text(
                f"❌ Ошибка распознавания: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке голосового сообщения."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(
        "📝 Я распознаю только голосовые сообщения.\n"
        "Отправь мне голосовое сообщение, и я преобразую его в текст!"
    )


def main():
    """Запуск бота"""

    # Проверка конфигурации
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        logger.error("Yandex Cloud credentials not set!")
        return

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Регистрируем обработчики сообщений
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    logger.info("🤖 Telegram bot started!")
    logger.info("Press Ctrl+C to stop")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
