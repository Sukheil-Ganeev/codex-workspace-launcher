#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Синхронизация локальных файлов Notion AI агентов с Notion страницами.

Использование:
    python sync_agents.py formatting           # Один агент
    python sync_agents.py all                  # Все агенты
    python sync_agents.py all --dry-run        # Тестовый режим
    python sync_agents.py calculator --force   # Принудительно

Требования:
    pip install notion-client

Переменные окружения:
    NOTION_API_KEY - API ключ интеграции Notion
"""

import os
import sys
import re
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    AGENTS_CONFIG, AGENT_FILES, PROTECTED_SECTION,
    NOTION_API_KEY, RATE_LIMIT_DELAY,
    get_agent_path, get_enabled_agents, validate_config
)
from md_to_notion import (
    parse_markdown, create_toggle, create_divider,
    create_heading_2, create_paragraph, split_blocks_for_api
)

try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# NOTION AGENT SYNC CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class NotionAgentSync:
    """Синхронизатор агентов с Notion."""

    def __init__(self, dry_run: bool = False, force: bool = False):
        """
        Инициализация.

        Args:
            dry_run: Тестовый режим без реальных изменений
            force: Игнорировать проверку версий
        """
        self.dry_run = dry_run
        self.force = force
        self.client: Optional[Client] = None

        # Статистика
        self.stats = {
            "synced": 0,
            "skipped": 0,
            "errors": 0,
        }

    def connect(self) -> bool:
        """Подключиться к Notion API."""
        if not NOTION_AVAILABLE:
            logger.error("notion-client не установлен. Установите: pip install notion-client")
            return False

        if not NOTION_API_KEY:
            logger.error("NOTION_API_KEY не установлен")
            logger.info("Установите: export NOTION_API_KEY='secret_xxx...'")
            return False

        try:
            self.client = Client(auth=NOTION_API_KEY)
            self.client.users.me()
            logger.info("Подключено к Notion API")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Notion: {e}")
            return False

    def _rate_limit(self):
        """Задержка для соблюдения rate limit."""
        time.sleep(RATE_LIMIT_DELAY)

    # ───────────────────────────────────────────────────────────────────────────
    # РАБОТА С ВЕРСИЯМИ
    # ───────────────────────────────────────────────────────────────────────────

    def get_local_version(self, agent_name: str) -> Optional[str]:
        """
        Получить версию агента из локального CHANGELOG.md.

        Ищет паттерн: ## [X.Y.Z] - YYYY-MM-DD
        """
        agent_path = get_agent_path(agent_name)
        if not agent_path:
            return None

        changelog_path = agent_path / "CHANGELOG.md"
        if not changelog_path.exists():
            return None

        try:
            content = changelog_path.read_text(encoding='utf-8')
            # Ищем первую версию в формате ## [X.Y.Z]
            match = re.search(r'##\s*\[(\d+\.\d+\.\d+)\]', content)
            if match:
                return match.group(1)
        except Exception as e:
            logger.warning(f"Ошибка чтения CHANGELOG: {e}")

        return None

    def get_notion_version(self, page_id: str) -> Optional[str]:
        """
        Получить версию со страницы Notion.

        Ищет в блоках текст с паттерном версии.
        """
        if self.dry_run:
            return None

        try:
            self._rate_limit()
            blocks = self.client.blocks.children.list(block_id=page_id)

            for block in blocks.get("results", []):
                block_type = block.get("type")
                if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
                    rich_text = block.get(block_type, {}).get("rich_text", [])
                    text = "".join([t.get("plain_text", "") for t in rich_text])

                    # Ищем версию
                    match = re.search(r'[Vv]ersion[:\s]*(\d+\.\d+\.\d+)|v(\d+\.\d+\.\d+)', text)
                    if match:
                        return match.group(1) or match.group(2)

            return None

        except APIResponseError as e:
            logger.warning(f"Ошибка получения версии с Notion: {e}")
            return None

    # ───────────────────────────────────────────────────────────────────────────
    # РАБОТА С БЛОКАМИ
    # ───────────────────────────────────────────────────────────────────────────

    def get_page_blocks(self, page_id: str) -> List[Dict]:
        """Получить все блоки страницы."""
        if self.dry_run:
            return []

        all_blocks = []
        has_more = True
        start_cursor = None

        try:
            while has_more:
                self._rate_limit()
                params = {"block_id": page_id}
                if start_cursor:
                    params["start_cursor"] = start_cursor

                response = self.client.blocks.children.list(**params)
                all_blocks.extend(response.get("results", []))
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")

            return all_blocks

        except APIResponseError as e:
            logger.error(f"Ошибка получения блоков: {e}")
            return []

    def find_memories_section(self, blocks: List[Dict]) -> Tuple[Optional[int], Optional[Dict]]:
        """
        Найти секцию "Воспоминания" в блоках.

        Returns:
            (index, block) или (None, None)
        """
        for i, block in enumerate(blocks):
            block_type = block.get("type")

            # Ищем в toggle блоках
            if block_type == "toggle":
                rich_text = block.get("toggle", {}).get("rich_text", [])
                text = "".join([t.get("plain_text", "") for t in rich_text])
                if PROTECTED_SECTION.lower() in text.lower():
                    return i, block

            # Ищем в заголовках
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                rich_text = block.get(block_type, {}).get("rich_text", [])
                text = "".join([t.get("plain_text", "") for t in rich_text])
                if PROTECTED_SECTION.lower() in text.lower():
                    return i, block

        return None, None

    def archive_blocks(self, blocks: List[Dict], exclude_ids: List[str] = None) -> int:
        """
        Архивировать (удалить) блоки.

        Args:
            blocks: Список блоков для удаления
            exclude_ids: ID блоков которые НЕ удалять

        Returns:
            Количество удалённых блоков
        """
        if self.dry_run:
            count = len([b for b in blocks if b["id"] not in (exclude_ids or [])])
            logger.info(f"[DRY-RUN] Будет удалено {count} блоков")
            return count

        exclude_ids = exclude_ids or []
        deleted = 0

        for block in blocks:
            if block["id"] in exclude_ids:
                continue

            try:
                self._rate_limit()
                self.client.blocks.delete(block_id=block["id"])
                deleted += 1
            except APIResponseError as e:
                logger.warning(f"Ошибка удаления блока {block['id']}: {e}")

        return deleted

    def append_blocks(self, page_id: str, blocks: List[Dict]) -> int:
        """
        Добавить блоки на страницу.

        Returns:
            Количество добавленных блоков
        """
        if self.dry_run:
            logger.info(f"[DRY-RUN] Будет добавлено {len(blocks)} блоков")
            return len(blocks)

        added = 0

        # Разбиваем на части по 100 блоков (лимит API)
        chunks = split_blocks_for_api(blocks, max_blocks=100)

        for chunk in chunks:
            try:
                self._rate_limit()
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=chunk
                )
                added += len(chunk)
            except APIResponseError as e:
                logger.error(f"Ошибка добавления блоков: {e}")
                self.stats["errors"] += 1

        return added

    # ───────────────────────────────────────────────────────────────────────────
    # СИНХРОНИЗАЦИЯ АГЕНТА
    # ───────────────────────────────────────────────────────────────────────────

    def read_agent_files(self, agent_name: str) -> Dict[str, str]:
        """
        Прочитать все файлы агента.

        Returns:
            {filename: content}
        """
        agent_path = get_agent_path(agent_name)
        if not agent_path or not agent_path.exists():
            return {}

        files = {}
        for filename in AGENT_FILES.keys():
            file_path = agent_path / filename
            if file_path.exists():
                try:
                    files[filename] = file_path.read_text(encoding='utf-8')
                except Exception as e:
                    logger.warning(f"Ошибка чтения {filename}: {e}")

        return files

    def build_page_content(self, agent_files: Dict[str, str]) -> List[Dict]:
        """
        Построить контент страницы из файлов агента.

        Структура:
        1. INSTRUCTIONS.md — основной контент
        2. Toggle секции для остальных файлов
        3. Разделитель
        """
        blocks = []

        # 1. Основной контент (INSTRUCTIONS.md)
        if "INSTRUCTIONS.md" in agent_files:
            main_content = agent_files["INSTRUCTIONS.md"]
            main_blocks = parse_markdown(main_content)
            blocks.extend(main_blocks)

        # Разделитель перед Toggle секциями
        if len(agent_files) > 1:
            blocks.append(create_divider())

        # 2. Toggle секции для остальных файлов
        for filename, config in AGENT_FILES.items():
            if config.get("is_main"):
                continue  # INSTRUCTIONS.md уже добавлен

            if filename not in agent_files:
                continue

            toggle_title = config.get("toggle_title", filename)
            file_content = agent_files[filename]

            # Парсим контент файла в блоки
            inner_blocks = parse_markdown(file_content)

            # Создаём Toggle с вложенными блоками
            # Notion API не позволяет напрямую создавать вложенные блоки при append
            # Поэтому создаём toggle и добавляем children отдельно
            toggle_block = create_toggle(toggle_title, inner_blocks[:100])  # Лимит вложенных блоков
            blocks.append(toggle_block)

        return blocks

    def sync_agent(self, agent_name: str) -> bool:
        """
        Синхронизировать одного агента.

        Returns:
            True если успешно
        """
        config = AGENTS_CONFIG.get(agent_name)
        if not config:
            logger.error(f"Агент '{agent_name}' не найден в конфигурации")
            return False

        if not config.get("enabled"):
            logger.warning(f"Агент '{agent_name}' отключён")
            return False

        page_id = config.get("page_id")
        if not page_id:
            logger.error(f"Page ID не указан для агента '{agent_name}'")
            return False

        display_name = config.get("display_name", agent_name)
        logger.info(f"\n{'='*60}")
        logger.info(f"Синхронизация: {display_name}")
        logger.info(f"{'='*60}")

        # Проверка версий
        local_version = self.get_local_version(agent_name)
        notion_version = self.get_notion_version(page_id) if not self.dry_run else None

        logger.info(f"Локальная версия: {local_version or 'не найдена'}")
        logger.info(f"Notion версия: {notion_version or 'не найдена'}")

        if not self.force and local_version and notion_version:
            if local_version == notion_version:
                logger.info(f"Версии совпадают, пропускаем")
                self.stats["skipped"] += 1
                return True

        # Читаем файлы агента
        agent_files = self.read_agent_files(agent_name)
        if not agent_files:
            logger.error(f"Файлы агента не найдены")
            self.stats["errors"] += 1
            return False

        logger.info(f"Найдено файлов: {len(agent_files)} ({', '.join(agent_files.keys())})")

        # Получаем текущие блоки страницы
        current_blocks = self.get_page_blocks(page_id)
        logger.info(f"Текущих блоков на странице: {len(current_blocks)}")

        # Ищем секцию "Воспоминания"
        memories_idx, memories_block = self.find_memories_section(current_blocks)
        preserve_ids = []

        if memories_block:
            logger.info(f"Найдена секция '{PROTECTED_SECTION}' (индекс {memories_idx})")
            preserve_ids.append(memories_block["id"])
            # Также сохраняем все блоки после "Воспоминаний" (могут быть вложенные)
            for block in current_blocks[memories_idx:]:
                if block["id"] not in preserve_ids:
                    preserve_ids.append(block["id"])

        # Удаляем старые блоки (кроме "Воспоминаний")
        blocks_to_delete = [b for b in current_blocks if b["id"] not in preserve_ids]
        if blocks_to_delete:
            deleted = self.archive_blocks(blocks_to_delete)
            logger.info(f"Удалено блоков: {deleted}")

        # Строим новый контент
        new_blocks = self.build_page_content(agent_files)
        logger.info(f"Подготовлено новых блоков: {len(new_blocks)}")

        # Добавляем новые блоки
        added = self.append_blocks(page_id, new_blocks)
        logger.info(f"Добавлено блоков: {added}")

        self.stats["synced"] += 1
        logger.info(f"[OK] Агент '{display_name}' синхронизирован")

        return True

    def sync_all(self, agent_names: List[str] = None) -> Dict:
        """
        Синхронизировать несколько агентов.

        Args:
            agent_names: Список имён агентов или None для всех включённых

        Returns:
            Статистика синхронизации
        """
        if agent_names is None or "all" in agent_names:
            agents = get_enabled_agents()
            agent_names = list(agents.keys())

        logger.info(f"Синхронизация агентов: {', '.join(agent_names)}")

        for name in agent_names:
            try:
                self.sync_agent(name)
            except Exception as e:
                logger.error(f"Ошибка синхронизации '{name}': {e}")
                self.stats["errors"] += 1

        return self.stats


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description="Синхронизация Notion AI агентов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python sync_agents.py formatting           Синхронизировать одного агента
  python sync_agents.py all                  Все включённые агенты
  python sync_agents.py all --dry-run        Тестовый режим
  python sync_agents.py calculator --force   Игнорировать версию

Доступные агенты:
  formatting   - Форматирование текстов
  bank         - Банковские реквизиты
  bookings     - Подтверждения бронирований
  routes       - Оптимизация маршрутов (отключён)
  calculator   - Калькулятор валют (отключён)
  requests     - Обработка запросов (отключён)

Переменные окружения:
  NOTION_API_KEY   API ключ интеграции Notion
        """
    )

    parser.add_argument('agents', nargs='*', default=[],
                       help='Имена агентов для синхронизации (или "all")')
    parser.add_argument('--dry-run', action='store_true',
                       help='Тестовый режим без изменений')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Игнорировать проверку версий')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    parser.add_argument('--list', '-l', action='store_true',
                       help='Показать список агентов и выйти')

    args = parser.parse_args()

    # Показать список агентов
    if args.list or (not args.agents and not args.list):
        print("\n=== Доступные агенты ===\n")
        for name, config in AGENTS_CONFIG.items():
            status = "[OK]" if config.get("enabled") else "[--]"
            page_id = config.get("page_id", "")[:12] + "..." if config.get("page_id") else "НЕТ"
            print(f"  {status} {name}")
            print(f"      {config['display_name']}")
            print(f"      Page ID: {page_id}")
            print()
        return 0

    # Настройка логирования
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Проверка библиотеки
    if not NOTION_AVAILABLE:
        print("[!] Установите библиотеку: pip install notion-client")
        return 1

    # Валидация конфигурации
    errors = validate_config()
    if errors:
        print("\n[!] Ошибки конфигурации:")
        for err in errors:
            print(f"    - {err}")
        return 1

    # Создаём синхронизатор
    sync = NotionAgentSync(dry_run=args.dry_run, force=args.force)

    if args.dry_run:
        logger.info("=== ТЕСТОВЫЙ РЕЖИМ (dry-run) ===")

    # Подключаемся
    if not sync.connect():
        return 1

    # Запускаем синхронизацию
    stats = sync.sync_all(args.agents)

    # Итоговая статистика
    print("\n" + "=" * 60)
    print("ИТОГО:")
    print(f"  Синхронизировано: {stats['synced']}")
    print(f"  Пропущено:        {stats['skipped']}")
    print(f"  Ошибок:           {stats['errors']}")
    print("=" * 60)

    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
