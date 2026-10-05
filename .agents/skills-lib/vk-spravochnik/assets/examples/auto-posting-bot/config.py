"""
Конфигурация Auto-Posting Bot
==============================

Настройки для автоматической публикации в VK

"""

import os
from dotenv import load_dotenv

# Загрузить .env файл
load_dotenv()

# ========== VK API ==========

# VK Community Access Token
VK_TOKEN = os.getenv('VK_TOKEN')

# ID группы (без минуса)
GROUP_ID = int(os.getenv('GROUP_ID', 0))

# Версия API
API_VERSION = os.getenv('API_VERSION', '5.199')

# ========== ФАЙЛЫ ==========

# Путь к JSON с данными туров
TOURS_DATA_FILE = 'tours_data.json'

# Директория для логов
LOGS_DIR = 'logs'

# Директория для временных файлов (фото)
TEMP_DIR = 'temp'

# ========== РАСПИСАНИЕ ==========

# Часовой пояс (для логов)
TIMEZONE = 'Asia/Dubai'  # UTC+4

# Время публикаций (настраивается в tours_data.json для каждого тура)
# Пример: "10:00" - публикация в 10:00 утра

# ========== RATE LIMITING ==========

# Задержка между запросами (секунды)
# Community Token: 3 запроса/сек, рекомендуется 0.5 сек (безопасный запас)
RATE_LIMIT_DELAY = 0.5

# Задержка между публикациями разных туров (секунды)
POST_DELAY = 2

# ========== ФОРМАТИРОВАНИЕ ПОСТОВ ==========

# Хештеги (добавляются ко всем постам)
DEFAULT_HASHTAGS = [
    '#ДубайТуры',
    '#ОАЭ',
    '#Туризм',
    '#Dubai',
    '#UAE'
]

# Контактные данные (добавляются ко всем постам)
CONTACTS = {
    'whatsapp': '+971-50-123-4567',
    'telegram': '@dubaitours',
    'vk': 'vk.me/dubaitours',
    'email': 'info@dubaitours.com'
}

# ========== НАСТРОЙКИ ФОТО ==========

# Максимальный размер фото для загрузки (MB)
MAX_PHOTO_SIZE_MB = 10

# Timeout для скачивания фото (секунды)
PHOTO_DOWNLOAD_TIMEOUT = 10

# ========== УВЕДОМЛЕНИЯ (опционально) ==========

# Telegram Bot Token для уведомлений (если нужно)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Telegram Chat ID для уведомлений
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Отправлять ли уведомления в Telegram
SEND_TELEGRAM_NOTIFICATIONS = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# ========== ВАЛИДАЦИЯ ==========

if not VK_TOKEN:
    raise ValueError("❌ VK_TOKEN не установлен! Создайте .env файл.")

if not GROUP_ID:
    raise ValueError("❌ GROUP_ID не установлен! Создайте .env файл.")

# ========== ВЫВОД КОНФИГУРАЦИИ ==========

if __name__ == '__main__':
    print("📋 Конфигурация Auto-Posting Bot")
    print(f"✅ VK Token: {'*' * 20}{VK_TOKEN[-10:]}")
    print(f"✅ Group ID: {GROUP_ID}")
    print(f"✅ API Version: {API_VERSION}")
    print(f"✅ Rate Limit Delay: {RATE_LIMIT_DELAY} сек")
    print(f"✅ Timezone: {TIMEZONE}")
    print(f"✅ Telegram Notifications: {'Включены' if SEND_TELEGRAM_NOTIFICATIONS else 'Выключены'}")
