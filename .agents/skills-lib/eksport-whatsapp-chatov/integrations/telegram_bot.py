#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Интеграция с Telegram Bot.
Отправка уведомлений и отчётов.
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from config import check_api_key, get_api_key, API_KEYS

class TelegramBotIntegration:
    """Интеграция с Telegram Bot API."""

    def __init__(self):
        self.token = None
        self.chat_id = None
        self.base_url = None

    def connect(self) -> bool:
        """Инициализировать бота."""
        if not check_api_key('telegram_bot'):
            print("[X] TELEGRAM_BOT_TOKEN не настроен")
            print("    Получите токен у @BotFather")
            return False

        if not API_KEYS.get('telegram_chat_id'):
            print("[X] TELEGRAM_CHAT_ID не настроен")
            print("    Узнайте через @userinfobot")
            return False

        self.token = get_api_key('telegram_bot')
        self.chat_id = API_KEYS['telegram_chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        return True

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Отправить сообщение.

        Args:
            text: Текст сообщения
            parse_mode: Markdown или HTML
        """
        if not self.token:
            if not self.connect():
                return False

        try:
            import requests
        except ImportError:
            print("[X] requests не установлен")
            return False

        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        response = requests.post(f"{self.base_url}/sendMessage", data=data)
        return response.status_code == 200

    def send_document(self, file_path: str, caption: str = "") -> bool:
        """Отправить файл."""
        if not self.token:
            if not self.connect():
                return False

        try:
            import requests
        except ImportError:
            return False

        with open(file_path, 'rb') as f:
            files = {"document": f}
            data = {
                "chat_id": self.chat_id,
                "caption": caption,
            }
            response = requests.post(f"{self.base_url}/sendDocument",
                                    data=data, files=files)

        return response.status_code == 200

    def notify_new_chat(self, contact_name: str, contact_type: str,
                        messages_count: int) -> bool:
        """Уведомить о новом обработанном чате."""
        text = f"""📱 *Новый чат обработан*

👤 Контакт: {contact_name}
📁 Тип: {contact_type}
💬 Сообщений: {messages_count}
"""
        return self.send_message(text)

    def notify_operations(self, operations_summary: dict) -> bool:
        """Уведомить о финансовых операциях."""
        text = "💰 *Сводка операций*\n\n"

        for currency, amount in operations_summary.items():
            text += f"• {currency}: {amount:,.2f}\n"

        return self.send_message(text)

    def send_daily_report(self, report_path: str) -> bool:
        """Отправить ежедневный отчёт."""
        return self.send_document(report_path, "📊 Ежедневный отчёт")


if __name__ == "__main__":
    bot = TelegramBotIntegration()
    if bot.connect():
        print("[OK] Telegram бот настроен")
        # bot.send_message("Тест интеграции! ✅")
    else:
        print("Настройте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")
