#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Конфигурация для синхронизации Notion AI агентов.

Маппинг локальных папок агентов на Notion страницы.
"""

import os
from pathlib import Path
from typing import Dict, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# ПУТИ
# ═══════════════════════════════════════════════════════════════════════════════

# Базовая директория с папками агентов
AGENTS_BASE_DIR = Path("D:/Downloads")

# ═══════════════════════════════════════════════════════════════════════════════
# NOTION API
# ═══════════════════════════════════════════════════════════════════════════════

# API ключ из переменной окружения
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")

# Rate limiting (Notion limit: 3 requests/sec)
RATE_LIMIT_DELAY = 0.35  # секунды между запросами

# ═══════════════════════════════════════════════════════════════════════════════
# МАППИНГ АГЕНТОВ
# ═══════════════════════════════════════════════════════════════════════════════

# Структура: короткое_имя -> {folder, page_id, display_name}
AGENTS_CONFIG: Dict[str, Dict] = {
    "formatting": {
        "folder": "NOTION_AI_AGENT_FORMATTING",
        "page_id": "2f778820479f8039be03e5e97b990df3",
        "display_name": "Форматирование текстов",
        "enabled": True,
    },
    "bank": {
        "folder": "NOTION_AI_AGENT_BANK",
        "page_id": "2f778820479f80f490fbcfdb749fdc56",
        "display_name": "Банковские реквизиты",
        "enabled": True,
    },
    "bookings": {
        "folder": "NOTION_AI_AGENT_BOOKINGS",
        "page_id": "2f778820479f80e09b84c75c7938b997",
        "display_name": "Подтверждения бронирований",
        "enabled": True,
    },
    "routes": {
        "folder": "NOTION_AI_AGENT_ROUTES",
        "page_id": "",  # TODO: Найти или создать страницу
        "display_name": "Оптимизация маршрутов",
        "enabled": False,  # Отключён до получения page_id
    },
    "calculator": {
        "folder": "NOTION_AI_AGENT_CALCULATOR",
        "page_id": "",  # TODO: Найти или создать страницу
        "display_name": "Калькулятор валют",
        "enabled": False,
    },
    "requests": {
        "folder": "NOTION_AI_AGENT_REQUESTS",
        "page_id": "",  # TODO: Найти или создать страницу
        "display_name": "Обработка запросов",
        "enabled": False,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ФАЙЛЫ АГЕНТА
# ═══════════════════════════════════════════════════════════════════════════════

# Какие файлы синхронизировать и в какие секции Toggle
AGENT_FILES = {
    "INSTRUCTIONS.md": {
        "is_main": True,  # Основной контент (не в Toggle)
        "toggle_title": None,
    },
    "CHEATSHEET.md": {
        "is_main": False,
        "toggle_title": "📋 Шпаргалка",
    },
    "TEMPLATES.md": {
        "is_main": False,
        "toggle_title": "📝 Шаблоны",
    },
    "REFERENCE_TABLES.md": {
        "is_main": False,
        "toggle_title": "📊 Справочники",
    },
    "CHANGELOG.md": {
        "is_main": False,
        "toggle_title": "📜 История версий",
    },
}

# Секция которую НЕ ТРОГАТЬ при обновлении
PROTECTED_SECTION = "Воспоминания"

# ═══════════════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def get_agent_path(agent_name: str) -> Optional[Path]:
    """Получить путь к папке агента."""
    if agent_name not in AGENTS_CONFIG:
        return None
    folder = AGENTS_CONFIG[agent_name]["folder"]
    return AGENTS_BASE_DIR / folder


def get_enabled_agents() -> Dict[str, Dict]:
    """Получить только включённых агентов."""
    return {
        name: config
        for name, config in AGENTS_CONFIG.items()
        if config.get("enabled", False) and config.get("page_id")
    }


def get_all_agent_names() -> list:
    """Получить список всех имён агентов."""
    return list(AGENTS_CONFIG.keys())


def validate_config() -> list:
    """
    Проверить конфигурацию.

    Returns:
        Список ошибок (пустой если всё ОК)
    """
    errors = []

    if not NOTION_API_KEY:
        errors.append("NOTION_API_KEY не установлен")

    for name, config in AGENTS_CONFIG.items():
        agent_path = get_agent_path(name)
        if agent_path and not agent_path.exists():
            errors.append(f"Папка агента '{name}' не найдена: {agent_path}")

        if config.get("enabled") and not config.get("page_id"):
            errors.append(f"Агент '{name}' включён, но page_id не указан")

    return errors


if __name__ == "__main__":
    # Тест конфигурации
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 60)
    print("КОНФИГУРАЦИЯ SYNC-NOTION-AGENTS")
    print("=" * 60)

    print(f"\nБазовая директория: {AGENTS_BASE_DIR}")
    print(f"API Key установлен: {'Да' if NOTION_API_KEY else 'НЕТ'}")

    print("\n--- Агенты ---")
    for name, config in AGENTS_CONFIG.items():
        status = "[OK]" if config.get("enabled") else "[--]"
        page_id = config.get("page_id", "")[:12] + "..." if config.get("page_id") else "НЕТ"
        print(f"  {status} {name}: {config['display_name']}")
        print(f"      Папка: {config['folder']}")
        print(f"      Page ID: {page_id}")

    print("\n--- Валидация ---")
    errors = validate_config()
    if errors:
        for err in errors:
            print(f"  [!] {err}")
    else:
        print("  [OK] Конфигурация валидна")
