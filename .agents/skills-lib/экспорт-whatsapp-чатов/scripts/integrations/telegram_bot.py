#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Telegram Bot для управления туристическим бизнесом в ОАЭ.

Функционал:
- Уведомления: новый контакт, бронирование, жалобы, крупные сделки, дайджест
- Команды: статистика, поиск, карточки контактов, операции, follow-up, выручка
- Inline кнопки: быстрые действия с контактами и бронированиями
- Отдельный бот для агентов: проверка наличия, цены, статус бронирования

Требует: pip install python-telegram-bot>=20.0
"""

import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Настройка путей
sys.path.insert(0, str(Path(__file__).parent))

try:
    from telegram import (
        Bot,
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        Update,
    )
    from telegram.ext import (
        Application,
        CallbackQueryHandler,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[!] python-telegram-bot не установлен. Установите: pip install python-telegram-bot>=20.0")

from config import (
    CHATS_DIR,
    CONTACT_TYPES,
    JSON_DIR,
    ANALYTICS_DIR,
    API_KEYS,
    check_api_key,
    get_api_key,
)

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Токены ботов
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_AGENT_BOT_TOKEN = os.getenv('TELEGRAM_AGENT_BOT_TOKEN', '')

# ID администраторов (список chat_id владельцев/менеджеров)
TELEGRAM_ADMIN_IDS = [
    int(x.strip()) for x in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',')
    if x.strip().isdigit()
]

# Порог для "крупной сделки" (AED)
BIG_DEAL_THRESHOLD = 5000

# Время дайджеста (часы по UTC)
DIGEST_MORNING_HOUR = 6  # 10:00 Dubai time (UTC+4)
DIGEST_EVENING_HOUR = 17  # 21:00 Dubai time (UTC+4)

# Webhook URL (если используется webhook вместо polling)
WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
WEBHOOK_PORT = int(os.getenv('TELEGRAM_WEBHOOK_PORT', '8443'))

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

def load_contacts_data() -> List[Dict]:
    """Загрузить данные контактов из JSON."""
    contacts_file = JSON_DIR / "contacts.json"
    if contacts_file.exists():
        try:
            with open(contacts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки contacts.json: {e}")
    return []


def load_operations_data() -> List[Dict]:
    """Загрузить данные операций из JSON."""
    operations_file = JSON_DIR / "operations.json"
    if operations_file.exists():
        try:
            with open(operations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки operations.json: {e}")
    return []


def load_bookings_data() -> List[Dict]:
    """Загрузить данные бронирований."""
    bookings_file = JSON_DIR / "bookings.json"
    if bookings_file.exists():
        try:
            with open(bookings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки bookings.json: {e}")
    return []


def load_followups_data() -> List[Dict]:
    """Загрузить данные follow-up задач."""
    # Пробуем разные источники
    sources = [
        JSON_DIR / "followups.json",
        JSON_DIR / "tasks.json",
        CHATS_DIR / "_задачи" / f"задачи_{datetime.now().strftime('%Y-%m-%d')}.json",
    ]

    for source in sources:
        if source.exists():
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                continue
    return []


def search_contacts(query: str) -> List[Dict]:
    """Поиск контактов по имени или телефону."""
    contacts = load_contacts_data()
    query_lower = query.lower()
    results = []

    for contact in contacts:
        name = contact.get('name', '').lower()
        phone = contact.get('phone', '')

        if query_lower in name or query in phone:
            results.append(contact)

    return results[:10]  # Лимит 10 результатов


def get_contact_by_id(contact_id: str) -> Optional[Dict]:
    """Получить контакт по ID."""
    contacts = load_contacts_data()

    for contact in contacts:
        if contact.get('id') == contact_id or contact.get('jid') == contact_id:
            return contact

    return None


def get_today_stats() -> Dict[str, Any]:
    """Статистика за сегодня."""
    today = datetime.now().strftime('%Y-%m-%d')
    operations = load_operations_data()
    contacts = load_contacts_data()
    bookings = load_bookings_data()

    today_ops = [op for op in operations if op.get('date', '').startswith(today)]

    revenue_aed = sum(
        float(op.get('amount', 0))
        for op in today_ops
        if op.get('currency') == 'AED'
    )
    revenue_rub = sum(
        float(op.get('amount', 0))
        for op in today_ops
        if op.get('currency') == 'RUB'
    )

    new_contacts = [c for c in contacts if c.get('created_at', '').startswith(today)]
    today_bookings = [b for b in bookings if b.get('date', '').startswith(today)]

    return {
        'operations_count': len(today_ops),
        'revenue_aed': revenue_aed,
        'revenue_rub': revenue_rub,
        'new_contacts': len(new_contacts),
        'bookings': len(today_bookings),
        'date': today,
    }


def get_period_stats(days: int) -> Dict[str, Any]:
    """Статистика за период."""
    start_date = datetime.now() - timedelta(days=days)
    operations = load_operations_data()
    contacts = load_contacts_data()
    bookings = load_bookings_data()

    period_ops = []
    for op in operations:
        try:
            op_date = datetime.strptime(op.get('date', ''), '%Y-%m-%d')
            if op_date >= start_date:
                period_ops.append(op)
        except:
            pass

    revenue_aed = sum(
        float(op.get('amount', 0))
        for op in period_ops
        if op.get('currency') == 'AED'
    )
    revenue_rub = sum(
        float(op.get('amount', 0))
        for op in period_ops
        if op.get('currency') == 'RUB'
    )

    return {
        'operations_count': len(period_ops),
        'revenue_aed': revenue_aed,
        'revenue_rub': revenue_rub,
        'days': days,
    }


# ═══════════════════════════════════════════════════════════════
# INLINE КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода статистики."""
    keyboard = [
        [
            InlineKeyboardButton("Сегодня", callback_data="stats_today"),
            InlineKeyboardButton("Неделя", callback_data="stats_week"),
            InlineKeyboardButton("Месяц", callback_data="stats_month"),
        ],
        [
            InlineKeyboardButton("Обновить", callback_data="stats_refresh"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_contact_keyboard(contact_id: str) -> InlineKeyboardMarkup:
    """Клавиатура действий с контактом."""
    keyboard = [
        [
            InlineKeyboardButton("История чата", callback_data=f"contact_history_{contact_id}"),
            InlineKeyboardButton("Операции", callback_data=f"contact_ops_{contact_id}"),
        ],
        [
            InlineKeyboardButton("Создать задачу", callback_data=f"contact_task_{contact_id}"),
            InlineKeyboardButton("Связаться", callback_data=f"contact_reach_{contact_id}"),
        ],
        [
            InlineKeyboardButton("Закрыть", callback_data="close"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_booking_keyboard(booking_id: str) -> InlineKeyboardMarkup:
    """Клавиатура действий с бронированием."""
    keyboard = [
        [
            InlineKeyboardButton("Подтвердить", callback_data=f"booking_confirm_{booking_id}"),
            InlineKeyboardButton("Отменить", callback_data=f"booking_cancel_{booking_id}"),
        ],
        [
            InlineKeyboardButton("Детали", callback_data=f"booking_details_{booking_id}"),
            InlineKeyboardButton("Контакт клиента", callback_data=f"booking_client_{booking_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_task_keyboard(task_id: str) -> InlineKeyboardMarkup:
    """Клавиатура действий с задачей."""
    keyboard = [
        [
            InlineKeyboardButton("Выполнено", callback_data=f"task_done_{task_id}"),
            InlineKeyboardButton("Отложить", callback_data=f"task_postpone_{task_id}"),
        ],
        [
            InlineKeyboardButton("Удалить", callback_data=f"task_delete_{task_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню."""
    keyboard = [
        [
            InlineKeyboardButton("Статистика", callback_data="menu_stats"),
            InlineKeyboardButton("Операции", callback_data="menu_operations"),
        ],
        [
            InlineKeyboardButton("Follow-up", callback_data="menu_followup"),
            InlineKeyboardButton("Выручка", callback_data="menu_revenue"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ═══════════════════════════════════════════════════════════════
# ФОРМАТИРОВАНИЕ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

def format_contact_card(contact: Dict) -> str:
    """Форматирование карточки контакта."""
    name = contact.get('name', 'Без имени')
    phone = contact.get('phone', 'Нет телефона')
    contact_type = contact.get('type', 'клиент')
    subtype = contact.get('subtype', '')

    card = f"""
*{name}*
Тип: {contact_type}{f' ({subtype})' if subtype else ''}
Телефон: `{phone}`
"""

    # Дополнительные поля
    if contact.get('email'):
        card += f"Email: {contact['email']}\n"

    if contact.get('company'):
        card += f"Компания: {contact['company']}\n"

    if contact.get('last_contact'):
        card += f"Последний контакт: {contact['last_contact']}\n"

    if contact.get('total_revenue'):
        card += f"Всего выручки: {contact['total_revenue']:,.0f} AED\n"

    if contact.get('notes'):
        card += f"\n_Заметки:_ {contact['notes'][:200]}\n"

    return card


def format_operation(op: Dict) -> str:
    """Форматирование операции."""
    date = op.get('date', 'Нет даты')
    amount = op.get('amount', 0)
    currency = op.get('currency', '')
    op_type = op.get('type', 'операция')
    contact = op.get('contact_name', '')
    status = op.get('status', '')

    status_emoji = {
        'completed': '',
        'pending': '',
        'cancelled': '',
    }.get(status.lower(), '')

    return f"{status_emoji} *{date}* | {amount:,.0f} {currency} | {op_type}" + \
           (f" | {contact}" if contact else "")


def format_stats(stats: Dict, title: str = "Статистика") -> str:
    """Форматирование статистики."""
    return f"""
*{title}*

Операций: {stats.get('operations_count', 0)}
Выручка AED: {stats.get('revenue_aed', 0):,.0f}
Выручка RUB: {stats.get('revenue_rub', 0):,.0f}
Новых контактов: {stats.get('new_contacts', 0)}
Бронирований: {stats.get('bookings', 0)}
"""


def format_followup_list(tasks: List[Dict]) -> str:
    """Форматирование списка follow-up задач."""
    if not tasks:
        return "*Нет задач на сегодня*"

    text = "*Follow-up на сегодня:*\n\n"

    for i, task in enumerate(tasks[:10], 1):
        contact = task.get('contact_name', 'Без контакта')
        description = task.get('description', task.get('text', 'Без описания'))[:100]
        priority = task.get('priority', 'normal')

        priority_emoji = {
            'high': '',
            'urgent': '',
            'normal': '',
            'low': '',
        }.get(priority, '')

        text += f"{i}. {priority_emoji} *{contact}*\n   {description}\n\n"

    if len(tasks) > 10:
        text += f"_...и ещё {len(tasks) - 10} задач_"

    return text


# ═══════════════════════════════════════════════════════════════
# УВЕДОМЛЕНИЯ
# ═══════════════════════════════════════════════════════════════

class NotificationService:
    """Сервис отправки уведомлений."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_to_admins(self, text: str, keyboard: InlineKeyboardMarkup = None):
        """Отправить сообщение всем администраторам."""
        for admin_id in TELEGRAM_ADMIN_IDS:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Ошибка отправки админу {admin_id}: {e}")

    async def notify_new_contact(self, contact: Dict):
        """Уведомление о новом контакте."""
        text = f"""
*Новый контакт*

{format_contact_card(contact)}
"""
        keyboard = get_contact_keyboard(contact.get('id', ''))
        await self.send_to_admins(text, keyboard)

    async def notify_new_booking(self, booking: Dict):
        """Уведомление о новом бронировании."""
        client = booking.get('client_name', 'Клиент')
        service = booking.get('service', 'Услуга')
        date = booking.get('date', 'Не указана')
        amount = booking.get('amount', 0)

        text = f"""
*Новое бронирование*

Клиент: {client}
Услуга: {service}
Дата: {date}
Сумма: {amount:,.0f} AED
"""
        keyboard = get_booking_keyboard(booking.get('id', ''))
        await self.send_to_admins(text, keyboard)

    async def notify_complaint(self, complaint: Dict):
        """URGENT: Уведомление о жалобе."""
        client = complaint.get('client_name', 'Клиент')
        description = complaint.get('description', 'Без описания')[:300]

        text = f"""
*ЖАЛОБА!*

Клиент: {client}
Суть: {description}

_Требуется срочное внимание!_
"""
        await self.send_to_admins(text)

    async def notify_big_deal(self, deal: Dict):
        """Уведомление о крупной сделке."""
        client = deal.get('client_name', 'Клиент')
        amount = deal.get('amount', 0)
        service = deal.get('service', 'Услуга')

        text = f"""
*Крупная сделка!*

Клиент: {client}
Сумма: {amount:,.0f} AED
Услуга: {service}
"""
        await self.send_to_admins(text)

    async def send_daily_digest(self, is_morning: bool = True):
        """Ежедневный дайджест."""
        stats = get_today_stats() if is_morning else get_period_stats(1)
        followups = load_followups_data()
        today_followups = [
            f for f in followups
            if f.get('due_date', '').startswith(datetime.now().strftime('%Y-%m-%d'))
        ]

        period = "Утренний" if is_morning else "Вечерний"

        text = f"""
*{period} дайджест*
_{datetime.now().strftime('%d.%m.%Y')}_

{format_stats(stats, 'За сегодня' if is_morning else 'Итоги дня')}

*Follow-up задачи: {len(today_followups)}*
"""

        if today_followups[:5]:
            for task in today_followups[:5]:
                contact = task.get('contact_name', '')
                desc = task.get('description', '')[:50]
                text += f"\n{contact}: {desc}"

        await self.send_to_admins(text, get_main_menu_keyboard())


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ КОМАНД (ВЛАДЕЛЕЦ/МЕНЕДЖЕРЫ)
# ═══════════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""
    user_id = update.effective_user.id

    if user_id not in TELEGRAM_ADMIN_IDS:
        await update.message.reply_text(
            "Доступ запрещён. Обратитесь к администратору."
        )
        return

    await update.message.reply_text(
        """
*Бот управления туристическим бизнесом*

*Доступные команды:*
/stats - Статистика за период
/search [имя/телефон] - Поиск контакта
/contact [id] - Карточка контакта
/operations - Последние операции
/followup - Задачи на сегодня
/revenue [period] - Выручка за период
/help - Справка

Также можете использовать кнопки ниже.
        """,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""
    await update.message.reply_text(
        """
*Справка по командам*

*/stats* - Статистика за сегодня/неделю/месяц
Выберите период кнопками

*/search [запрос]* - Поиск контакта
Пример: `/search Иван` или `/search +971`

*/contact [id]* - Карточка контакта
Пример: `/contact 12345`

*/operations* - Последние 10 операций
Можно указать количество: `/operations 20`

*/followup* - Follow-up задачи на сегодня
Показывает приоритетные задачи

*/revenue [период]* - Выручка
`/revenue today` - за сегодня
`/revenue week` - за неделю
`/revenue month` - за месяц

*Уведомления:*
- Новый контакт
- Новое бронирование
- Жалобы (срочные!)
- Крупные сделки (>5000 AED)
- Утренний и вечерний дайджест
        """,
        parse_mode='Markdown'
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats."""
    user_id = update.effective_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    stats = get_today_stats()
    text = format_stats(stats, "Статистика за сегодня")

    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_stats_keyboard()
    )


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search."""
    user_id = update.effective_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text(
            "Укажите имя или телефон для поиска.\nПример: `/search Иван`",
            parse_mode='Markdown'
        )
        return

    query = ' '.join(context.args)
    results = search_contacts(query)

    if not results:
        await update.message.reply_text(f"Контакты по запросу '{query}' не найдены.")
        return

    text = f"*Результаты поиска: {query}*\n\n"

    for contact in results:
        name = contact.get('name', 'Без имени')
        phone = contact.get('phone', '')
        contact_id = contact.get('id', contact.get('jid', ''))
        text += f"{name} | `{phone}`\n/contact\\_{contact_id[:8]}\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')


async def cmd_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /contact."""
    user_id = update.effective_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text(
            "Укажите ID контакта.\nПример: `/contact 12345`",
            parse_mode='Markdown'
        )
        return

    contact_id = context.args[0]
    contact = get_contact_by_id(contact_id)

    if not contact:
        # Поиск по частичному ID
        contacts = load_contacts_data()
        for c in contacts:
            if c.get('id', '').startswith(contact_id) or c.get('jid', '').startswith(contact_id):
                contact = c
                break

    if not contact:
        await update.message.reply_text(f"Контакт с ID '{contact_id}' не найден.")
        return

    text = format_contact_card(contact)
    keyboard = get_contact_keyboard(contact.get('id', contact.get('jid', '')))

    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)


async def cmd_operations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /operations."""
    user_id = update.effective_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    limit = 10
    if context.args and context.args[0].isdigit():
        limit = min(int(context.args[0]), 50)

    operations = load_operations_data()
    # Сортируем по дате (новые первые)
    operations.sort(key=lambda x: x.get('date', ''), reverse=True)
    recent_ops = operations[:limit]

    if not recent_ops:
        await update.message.reply_text("Операции не найдены.")
        return

    text = f"*Последние {len(recent_ops)} операций:*\n\n"

    for op in recent_ops:
        text += format_operation(op) + "\n"

    await update.message.reply_text(text, parse_mode='Markdown')


async def cmd_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /followup."""
    user_id = update.effective_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    followups = load_followups_data()
    today = datetime.now().strftime('%Y-%m-%d')

    # Фильтруем задачи на сегодня и просроченные
    today_tasks = []
    overdue_tasks = []

    for task in followups:
        due_date = task.get('due_date', task.get('date', ''))
        if due_date == today:
            today_tasks.append(task)
        elif due_date and due_date < today:
            overdue_tasks.append(task)

    text = "*Follow-up задачи*\n\n"

    if overdue_tasks:
        text += f"*Просроченные ({len(overdue_tasks)}):*\n"
        for task in overdue_tasks[:5]:
            contact = task.get('contact_name', '')
            desc = task.get('description', task.get('text', ''))[:80]
            text += f"- {contact}: {desc}\n"
        text += "\n"

    text += format_followup_list(today_tasks)

    await update.message.reply_text(text, parse_mode='Markdown')


async def cmd_revenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /revenue."""
    user_id = update.effective_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    period = 'today'
    if context.args:
        period = context.args[0].lower()

    period_days = {
        'today': 1,
        'week': 7,
        'month': 30,
        'quarter': 90,
        'year': 365,
    }

    days = period_days.get(period, 1)
    stats = get_period_stats(days)

    period_names = {
        'today': 'сегодня',
        'week': 'неделю',
        'month': 'месяц',
        'quarter': 'квартал',
        'year': 'год',
    }

    text = f"""
*Выручка за {period_names.get(period, period)}*

AED: {stats.get('revenue_aed', 0):,.0f}
RUB: {stats.get('revenue_rub', 0):,.0f}
Операций: {stats.get('operations_count', 0)}
"""

    await update.message.reply_text(text, parse_mode='Markdown')


# ═══════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ CALLBACK (INLINE КНОПКИ)
# ═══════════════════════════════════════════════════════════════

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline кнопок."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in TELEGRAM_ADMIN_IDS:
        return

    data = query.data

    # Статистика
    if data == "stats_today":
        stats = get_today_stats()
        text = format_stats(stats, "Статистика за сегодня")
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_stats_keyboard())

    elif data == "stats_week":
        stats = get_period_stats(7)
        text = format_stats(stats, "Статистика за неделю")
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_stats_keyboard())

    elif data == "stats_month":
        stats = get_period_stats(30)
        text = format_stats(stats, "Статистика за месяц")
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_stats_keyboard())

    elif data == "stats_refresh":
        stats = get_today_stats()
        text = format_stats(stats, f"Статистика (обновлено {datetime.now().strftime('%H:%M')})")
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_stats_keyboard())

    # Меню
    elif data == "menu_stats":
        stats = get_today_stats()
        text = format_stats(stats, "Статистика за сегодня")
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_stats_keyboard())

    elif data == "menu_operations":
        operations = load_operations_data()
        operations.sort(key=lambda x: x.get('date', ''), reverse=True)
        recent_ops = operations[:10]

        text = "*Последние операции:*\n\n"
        for op in recent_ops:
            text += format_operation(op) + "\n"

        await query.edit_message_text(text, parse_mode='Markdown')

    elif data == "menu_followup":
        followups = load_followups_data()
        today = datetime.now().strftime('%Y-%m-%d')
        today_tasks = [f for f in followups if f.get('due_date', '') == today]

        text = format_followup_list(today_tasks)
        await query.edit_message_text(text, parse_mode='Markdown')

    elif data == "menu_revenue":
        stats = get_period_stats(30)
        text = f"""
*Выручка за месяц*

AED: {stats.get('revenue_aed', 0):,.0f}
RUB: {stats.get('revenue_rub', 0):,.0f}
Операций: {stats.get('operations_count', 0)}
"""
        await query.edit_message_text(text, parse_mode='Markdown')

    # Действия с контактом
    elif data.startswith("contact_"):
        parts = data.split("_", 2)
        action = parts[1]
        contact_id = parts[2] if len(parts) > 2 else ''

        if action == "history":
            await query.edit_message_text(
                f"История чата для контакта {contact_id}...\n_(функция в разработке)_",
                parse_mode='Markdown'
            )
        elif action == "ops":
            operations = load_operations_data()
            contact_ops = [op for op in operations if contact_id in op.get('contact_id', '')]

            if contact_ops:
                text = f"*Операции контакта:*\n\n"
                for op in contact_ops[:10]:
                    text += format_operation(op) + "\n"
            else:
                text = "Операции контакта не найдены."

            await query.edit_message_text(text, parse_mode='Markdown')

        elif action == "task":
            await query.edit_message_text(
                f"Создание задачи для контакта {contact_id}...\n_(функция в разработке)_",
                parse_mode='Markdown'
            )

        elif action == "reach":
            contact = get_contact_by_id(contact_id)
            if contact and contact.get('phone'):
                phone = contact['phone'].replace('+', '')
                await query.edit_message_text(
                    f"Связаться с контактом:\n\n"
                    f"WhatsApp: https://wa.me/{phone}\n"
                    f"Телефон: {contact['phone']}",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("Контакт не найден.")

    # Действия с бронированием
    elif data.startswith("booking_"):
        parts = data.split("_", 2)
        action = parts[1]
        booking_id = parts[2] if len(parts) > 2 else ''

        if action == "confirm":
            await query.edit_message_text(
                f"Бронирование {booking_id} подтверждено!",
                parse_mode='Markdown'
            )
        elif action == "cancel":
            await query.edit_message_text(
                f"Бронирование {booking_id} отменено.",
                parse_mode='Markdown'
            )
        elif action == "details":
            await query.edit_message_text(
                f"Детали бронирования {booking_id}...\n_(функция в разработке)_",
                parse_mode='Markdown'
            )

    # Действия с задачей
    elif data.startswith("task_"):
        parts = data.split("_", 2)
        action = parts[1]
        task_id = parts[2] if len(parts) > 2 else ''

        if action == "done":
            await query.edit_message_text(f"Задача {task_id} выполнена!")
        elif action == "postpone":
            await query.edit_message_text(f"Задача {task_id} отложена на завтра.")
        elif action == "delete":
            await query.edit_message_text(f"Задача {task_id} удалена.")

    # Закрыть
    elif data == "close":
        await query.delete_message()


# ═══════════════════════════════════════════════════════════════
# БОТ ДЛЯ АГЕНТОВ
# ═══════════════════════════════════════════════════════════════

class AgentBot:
    """Отдельный бот для турагентов."""

    @staticmethod
    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start для агента."""
        await update.message.reply_text(
            """
*Бот для турагентов*

Доступные команды:
/check [тур] - Проверить наличие тура
/price [тур] - Узнать цену
/status [номер] - Статус бронирования
/help - Справка

Для получения доступа обратитесь к менеджеру.
            """,
            parse_mode='Markdown'
        )

    @staticmethod
    async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка наличия тура."""
        if not context.args:
            await update.message.reply_text(
                "Укажите название тура.\nПример: `/check Safari`",
                parse_mode='Markdown'
            )
            return

        tour_name = ' '.join(context.args)

        # Здесь должна быть логика проверки наличия
        # Пока заглушка
        await update.message.reply_text(
            f"Проверка наличия: *{tour_name}*\n\n"
            f"_Обработка запроса... Ожидайте ответа менеджера._",
            parse_mode='Markdown'
        )

    @staticmethod
    async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос цены."""
        if not context.args:
            await update.message.reply_text(
                "Укажите название тура.\nПример: `/price Desert Safari`",
                parse_mode='Markdown'
            )
            return

        tour_name = ' '.join(context.args)

        await update.message.reply_text(
            f"Запрос цены: *{tour_name}*\n\n"
            f"_Обработка запроса... Ожидайте ответа менеджера._",
            parse_mode='Markdown'
        )

    @staticmethod
    async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статус бронирования."""
        if not context.args:
            await update.message.reply_text(
                "Укажите номер бронирования.\nПример: `/status BK-12345`",
                parse_mode='Markdown'
            )
            return

        booking_number = context.args[0]

        # Здесь должна быть логика проверки статуса
        await update.message.reply_text(
            f"Статус бронирования *{booking_number}*:\n\n"
            f"_Загрузка данных..._",
            parse_mode='Markdown'
        )


# ═══════════════════════════════════════════════════════════════
# ЗАПУСК БОТА
# ═══════════════════════════════════════════════════════════════

def create_main_application() -> Optional[Application]:
    """Создать основное приложение бота."""
    if not TELEGRAM_AVAILABLE:
        print("[!] python-telegram-bot не установлен")
        return None

    if not TELEGRAM_BOT_TOKEN:
        print("[!] TELEGRAM_BOT_TOKEN не настроен")
        return None

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("contact", cmd_contact))
    app.add_handler(CommandHandler("operations", cmd_operations))
    app.add_handler(CommandHandler("followup", cmd_followup))
    app.add_handler(CommandHandler("revenue", cmd_revenue))

    # Inline кнопки
    app.add_handler(CallbackQueryHandler(handle_callback))

    return app


def create_agent_application() -> Optional[Application]:
    """Создать приложение бота для агентов."""
    if not TELEGRAM_AVAILABLE:
        return None

    if not TELEGRAM_AGENT_BOT_TOKEN:
        print("[!] TELEGRAM_AGENT_BOT_TOKEN не настроен (опционально)")
        return None

    app = Application.builder().token(TELEGRAM_AGENT_BOT_TOKEN).build()

    # Команды для агентов
    app.add_handler(CommandHandler("start", AgentBot.cmd_start))
    app.add_handler(CommandHandler("check", AgentBot.cmd_check))
    app.add_handler(CommandHandler("price", AgentBot.cmd_price))
    app.add_handler(CommandHandler("status", AgentBot.cmd_status))

    return app


async def run_polling():
    """Запуск в режиме polling."""
    main_app = create_main_application()
    if main_app:
        logger.info("Запуск основного бота в режиме polling...")
        await main_app.run_polling()


async def setup_webhook(app: Application, webhook_url: str):
    """Настройка webhook."""
    await app.bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")


# ═══════════════════════════════════════════════════════════════
# API ДЛЯ ВНЕШНИХ ВЫЗОВОВ
# ═══════════════════════════════════════════════════════════════

class TelegramNotifier:
    """
    API для отправки уведомлений из других скриптов.

    Использование:
        notifier = TelegramNotifier()
        await notifier.send_new_contact(contact_data)
        await notifier.send_big_deal(deal_data)
    """

    def __init__(self):
        self.bot = None
        self.notification_service = None

    async def connect(self):
        """Инициализация бота."""
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot не установлен")

        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не настроен")

        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.notification_service = NotificationService(self.bot)

    async def send_new_contact(self, contact: Dict):
        """Отправить уведомление о новом контакте."""
        if not self.notification_service:
            await self.connect()
        await self.notification_service.notify_new_contact(contact)

    async def send_new_booking(self, booking: Dict):
        """Отправить уведомление о новом бронировании."""
        if not self.notification_service:
            await self.connect()
        await self.notification_service.notify_new_booking(booking)

    async def send_complaint(self, complaint: Dict):
        """Отправить уведомление о жалобе (URGENT)."""
        if not self.notification_service:
            await self.connect()
        await self.notification_service.notify_complaint(complaint)

    async def send_big_deal(self, deal: Dict):
        """Отправить уведомление о крупной сделке."""
        if not self.notification_service:
            await self.connect()

        amount = deal.get('amount', 0)
        if amount >= BIG_DEAL_THRESHOLD:
            await self.notification_service.notify_big_deal(deal)

    async def send_daily_digest(self, is_morning: bool = True):
        """Отправить ежедневный дайджест."""
        if not self.notification_service:
            await self.connect()
        await self.notification_service.send_daily_digest(is_morning)

    async def send_message(self, text: str, keyboard: InlineKeyboardMarkup = None):
        """Отправить произвольное сообщение администраторам."""
        if not self.notification_service:
            await self.connect()
        await self.notification_service.send_to_admins(text, keyboard)


# Синхронные обёртки для удобства
def send_notification_sync(text: str):
    """Синхронная отправка уведомления."""
    async def _send():
        notifier = TelegramNotifier()
        await notifier.connect()
        await notifier.send_message(text)

    asyncio.run(_send())


def send_new_contact_sync(contact: Dict):
    """Синхронная отправка уведомления о новом контакте."""
    async def _send():
        notifier = TelegramNotifier()
        await notifier.send_new_contact(contact)

    asyncio.run(_send())


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Главная функция."""
    import argparse

    parser = argparse.ArgumentParser(description='Telegram бот для туристического бизнеса')
    parser.add_argument('--webhook', action='store_true', help='Использовать webhook вместо polling')
    parser.add_argument('--agent', action='store_true', help='Запустить бот для агентов')
    parser.add_argument('--test', action='store_true', help='Тестовый режим')

    args = parser.parse_args()

    if not TELEGRAM_AVAILABLE:
        print("[!] Установите python-telegram-bot:")
        print("    pip install python-telegram-bot>=20.0")
        return

    if not TELEGRAM_BOT_TOKEN:
        print("[!] Настройте TELEGRAM_BOT_TOKEN:")
        print("    1. Создайте бота через @BotFather")
        print("    2. Установите переменную окружения TELEGRAM_BOT_TOKEN")
        return

    if not TELEGRAM_ADMIN_IDS:
        print("[!] Настройте TELEGRAM_ADMIN_IDS:")
        print("    1. Узнайте свой chat_id через @userinfobot")
        print("    2. Установите переменную окружения TELEGRAM_ADMIN_IDS")
        print("    Пример: TELEGRAM_ADMIN_IDS=123456789,987654321")
        return

    if args.test:
        print("[OK] Конфигурация бота:")
        print(f"    Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"    Admin IDs: {TELEGRAM_ADMIN_IDS}")
        print(f"    Agent Bot: {'Да' if TELEGRAM_AGENT_BOT_TOKEN else 'Нет'}")
        print(f"    Webhook: {WEBHOOK_URL if WEBHOOK_URL else 'Не настроен (polling)'}")
        return

    print("[*] Запуск Telegram бота...")
    print(f"    Админы: {len(TELEGRAM_ADMIN_IDS)} пользователей")

    if args.agent and TELEGRAM_AGENT_BOT_TOKEN:
        app = create_agent_application()
        if app:
            asyncio.run(app.run_polling())
    else:
        app = create_main_application()
        if app:
            if args.webhook and WEBHOOK_URL:
                # Webhook режим
                asyncio.run(setup_webhook(app, WEBHOOK_URL))
                app.run_webhook(
                    listen="0.0.0.0",
                    port=WEBHOOK_PORT,
                    webhook_url=WEBHOOK_URL
                )
            else:
                # Polling режим
                asyncio.run(app.run_polling())


if __name__ == "__main__":
    main()
