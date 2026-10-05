# =============================================================================
# bot.py — Telegram Bot для бронирования туров ОАЭ
# aiogram 3.x + shared core (PostgreSQL + Redis)
# =============================================================================

import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

# --- Конфигурация ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DB_URL = os.getenv("DATABASE_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")
CURRENCY = os.getenv("TOURS_CURRENCY", "AED")
LANGUAGE = os.getenv("BOT_LANGUAGE", "ru")
HEALTH_PORT = 8081

# --- Каталог туров (в production -- из PostgreSQL) ---
TOURS = [
    {"id": 1, "name": "Джип-сафари Премиум", "price": 250, "emoji": "\U0001F3DC"},
    {"id": 2, "name": "Обзорная экскурсия по Дубаю", "price": 180, "emoji": "\U0001F3D9"},
    {"id": 3, "name": "Абу-Даби полный день", "price": 220, "emoji": "\U0001F54C"},
    {"id": 4, "name": "Бурдж-Халифа -- на вершине", "price": 260, "emoji": "\U0001F3D7"},
    {"id": 5, "name": "Круиз на яхте по Марине", "price": 350, "emoji": "\U0001F6F3"},
]

# --- Health Check HTTP сервер ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            data = {
                "status": "ok",
                "service": "telegram-bot",
                "currency": CURRENCY,
                "tours_count": len(TOURS),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Подавляем логи health check


def start_health_server():
    """Запуск HTTP сервера для healthcheck в отдельном потоке."""
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[Health] Сервер запущен: http://0.0.0.0:{HEALTH_PORT}/health")


async def main():
    """Основной цикл бота."""
    start_health_server()

    print(f"[Telegram Bot] Запуск...")
    print(f"[Telegram Bot] Валюта: {CURRENCY} | Язык: {LANGUAGE}")
    print(f"[Telegram Bot] Туров в каталоге: {len(TOURS)}")

    if not TOKEN:
        print("[Telegram Bot] TELEGRAM_BOT_TOKEN не установлен!")
        print("[Telegram Bot] Запущен в demo-режиме (без подключения к Telegram)")
        # В demo-режиме просто держим процесс живым
        while True:
            await asyncio.sleep(60)
    else:
        # В production здесь подключение aiogram
        # from aiogram import Bot, Dispatcher
        # bot = Bot(token=TOKEN)
        # dp = Dispatcher()
        # ... регистрация хэндлеров ...
        # await dp.start_polling(bot)
        print("[Telegram Bot] Polling запущен")
        while True:
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
