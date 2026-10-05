#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Суммаризация диалогов WhatsApp через Claude API.

Функции:
1. Суммаризация через Claude API:
   - Краткое содержание (2-3 предложения)
   - Ключевые моменты
   - Исход диалога
2. Batch обработка
3. Кэширование результатов
4. Структурированный вывод:
   - Клиент хотел: ...
   - Предложено: ...
   - Итог: ...
5. Поиск по summary
6. Автообновление при новых сообщениях
7. Экспорт: JSON, Markdown

Конфигурация: ANTHROPIC_API_KEY

Входные данные: D:/Downloads/Chats/_база/raw/all_messages.jsonl
Выходные данные: D:/Downloads/Chats/_база/json/summaries.json
                 D:/Downloads/Chats/_аналитика/summaries.md
"""

import sys
import os
import json
import re
import argparse
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict, field

sys.stdout.reconfigure(encoding='utf-8')

# ===============================================================
# КОНФИГУРАЦИЯ
# ===============================================================

try:
    from config import RAW_DIR, JSON_DIR, ANALYTICS_DIR, CLAUDE_CONFIG
except ImportError:
    RAW_DIR = Path("D:/Downloads/Chats/_база/raw")
    JSON_DIR = Path("D:/Downloads/Chats/_база/json")
    ANALYTICS_DIR = Path("D:/Downloads/Chats/_аналитика")
    CLAUDE_CONFIG = {
        "api_key": os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("CLAUDE_API_KEY", ""),
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2048,
        "batch_size": 10,
        "max_retries": 3,
        "retry_delay": 2,
    }

# Claude API ключ
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '') or os.getenv('CLAUDE_API_KEY', '')

# Настройки
SUMMARY_MODEL = CLAUDE_CONFIG.get("model", "claude-sonnet-4-20250514")
SUMMARY_MAX_TOKENS = 2048
BATCH_SIZE = 5  # Диалогов в одном батче (диалоги длиннее, чем сообщения)
MAX_RETRIES = 3
RETRY_DELAY = 2

# Пути к файлам
CACHE_DIR = RAW_DIR / ".cache"
SUMMARY_CACHE_FILE = CACHE_DIR / "summary_cache.json"
SUMMARIES_JSON_FILE = JSON_DIR / "summaries.json"
SUMMARIES_MD_FILE = ANALYTICS_DIR / "summaries.md"


# ===============================================================
# ТИПЫ ДАННЫХ
# ===============================================================

@dataclass
class DialogSummary:
    """Результат суммаризации диалога."""
    jid: str
    contact_name: str

    # Краткое содержание
    short_summary: str  # 2-3 предложения

    # Структурированный вывод
    client_wanted: str      # Клиент хотел
    proposed: str           # Предложено
    outcome: str            # Итог

    # Ключевые моменты
    key_points: List[str]

    # Метаданные
    message_count: int
    date_range: str         # "01.01.2024 - 15.01.2024"
    last_message_date: str
    dialog_status: str      # active, pending, completed, cancelled

    # Извлечённые сущности
    products_mentioned: List[str]   # Туры, экскурсии
    amounts_mentioned: List[str]    # Суммы
    dates_mentioned: List[str]      # Даты

    # Служебные
    messages_hash: str      # Для отслеживания изменений
    summarized_at: str
    confidence: float

    def to_dict(self) -> Dict:
        return asdict(self)


# ===============================================================
# КЭШИРОВАНИЕ
# ===============================================================

class SummaryCache:
    """Кэш результатов суммаризации."""

    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        """Загрузить кэш из файла."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"Кэш суммаризации загружен: {len(self.cache)} записей")
            except (json.JSONDecodeError, IOError) as e:
                print(f"ВНИМАНИЕ: Не удалось загрузить кэш: {e}")
                self.cache = {}

    def _save(self):
        """Сохранить кэш в файл."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _compute_hash(self, messages: List[Dict]) -> str:
        """Вычислить хэш сообщений для отслеживания изменений."""
        # Берём последние 100 сообщений для хэша
        texts = [m.get('text', '')[:200] for m in messages[-100:]]
        content = json.dumps(texts, ensure_ascii=False)
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get(self, jid: str, messages: List[Dict]) -> Optional[Dict]:
        """Получить кэшированную суммаризацию если сообщения не изменились."""
        current_hash = self._compute_hash(messages)
        cached = self.cache.get(jid)

        if cached and cached.get('messages_hash') == current_hash:
            return cached

        return None

    def set(self, jid: str, summary: Dict):
        """Сохранить суммаризацию в кэш."""
        self.cache[jid] = summary

        # Сохраняем после каждых 10 новых записей
        if len(self.cache) % 10 == 0:
            self._save()

    def needs_update(self, jid: str, messages: List[Dict]) -> bool:
        """Проверить нужно ли обновить суммаризацию."""
        current_hash = self._compute_hash(messages)
        cached = self.cache.get(jid)

        if not cached:
            return True

        return cached.get('messages_hash') != current_hash

    def finalize(self):
        """Сохранить кэш при завершении."""
        self._save()
        print(f"Кэш суммаризации сохранён: {len(self.cache)} записей")


# ===============================================================
# СУММАРИЗАТОР
# ===============================================================

class DialogSummarizer:
    """Суммаризатор диалогов на основе Claude API."""

    def __init__(self, api_key: str, cache: SummaryCache):
        self.api_key = api_key
        self.cache = cache
        self.client = None
        self._init_client()

    def _init_client(self):
        """Инициализировать клиент Anthropic."""
        if not self.api_key:
            print("ВНИМАНИЕ: ANTHROPIC_API_KEY не установлен. Суммаризация недоступна.")
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("Claude API клиент для суммаризации инициализирован")
        except ImportError:
            print("ВНИМАНИЕ: anthropic SDK не установлен. Установите: pip install anthropic")
            self.client = None
        except Exception as e:
            print(f"ОШИБКА инициализации Claude API: {e}")
            self.client = None

    def summarize_dialog(
        self,
        jid: str,
        messages: List[Dict],
        contact_info: Dict,
        force: bool = False
    ) -> Optional[Dict]:
        """
        Суммаризировать один диалог.

        Args:
            jid: ID контакта (WhatsApp JID)
            messages: Список сообщений диалога
            contact_info: Информация о контакте
            force: Принудительная пересуммаризация

        Returns:
            Словарь с результатом суммаризации
        """
        if len(messages) < 3:
            return None

        # Проверяем кэш
        if not force:
            cached = self.cache.get(jid, messages)
            if cached:
                return cached

        # Если API недоступен
        if not self.client:
            return self._fallback_summary(jid, messages, contact_info)

        try:
            summary = self._call_claude_summarize(jid, messages, contact_info)
            self.cache.set(jid, summary)
            return summary
        except Exception as e:
            print(f"ОШИБКА суммаризации {jid}: {e}")
            return self._fallback_summary(jid, messages, contact_info)

    def _format_dialog_for_prompt(self, messages: List[Dict], max_messages: int = 50) -> str:
        """Форматировать диалог для промпта."""
        # Берём последние N сообщений
        recent = messages[-max_messages:]

        lines = []
        for msg in recent:
            sender = "Я" if msg.get('is_from_me') else msg.get('sender', 'Клиент')
            text = msg.get('text', '')[:500]  # Ограничиваем длину
            date = msg.get('date', '')

            if text:
                lines.append(f"[{date}] {sender}: {text}")

        return "\n".join(lines)

    def _get_date_range(self, messages: List[Dict]) -> Tuple[str, str]:
        """Получить диапазон дат диалога."""
        dates = [m.get('date', '') for m in messages if m.get('date')]
        if not dates:
            return ("", "")

        # Простой парсинг дат формата DD.MM.YYYY HH:MM:SS
        parsed = []
        for d in dates:
            try:
                # Попробуем несколько форматов
                for fmt in ['%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S']:
                    try:
                        parsed.append(datetime.strptime(d[:19], fmt))
                        break
                    except ValueError:
                        continue
            except:
                pass

        if not parsed:
            return (dates[0], dates[-1])

        min_date = min(parsed)
        max_date = max(parsed)

        return (
            min_date.strftime('%d.%m.%Y'),
            max_date.strftime('%d.%m.%Y')
        )

    def _call_claude_summarize(self, jid: str, messages: List[Dict], contact_info: Dict) -> Dict:
        """Вызвать Claude API для суммаризации."""

        dialog_text = self._format_dialog_for_prompt(messages)
        contact_name = contact_info.get('name', '') or contact_info.get('chat_name', '') or jid

        prompt = f"""Проанализируй переписку WhatsApp туристической компании в ОАЭ и создай структурированную суммаризацию.

КОНТАКТ: {contact_name}
СООБЩЕНИЙ: {len(messages)}

ПЕРЕПИСКА:
{dialog_text}

Создай суммаризацию в следующем формате (ответь ТОЛЬКО валидным JSON):

{{
  "short_summary": "Краткое содержание диалога в 2-3 предложениях",
  "client_wanted": "Что клиент хотел/запрашивал (одно предложение)",
  "proposed": "Что было предложено (одно предложение)",
  "outcome": "Итог диалога: забронировано/в процессе/отказ/ожидает ответа",
  "key_points": ["ключевой момент 1", "ключевой момент 2", "ключевой момент 3"],
  "dialog_status": "active|pending|completed|cancelled",
  "products_mentioned": ["тур/экскурсия 1", "тур/экскурсия 2"],
  "amounts_mentioned": ["1000 AED", "50000 RUB"],
  "dates_mentioned": ["15.01.2024", "20.01.2024"],
  "confidence": 0.9
}}

ВАЖНО:
- dialog_status: active (активное общение), pending (ожидает ответа), completed (успешно завершено), cancelled (отказ)
- Если что-то неизвестно, оставь пустую строку или пустой массив
- Суммаризируй на русском языке
"""

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    model=SUMMARY_MODEL,
                    max_tokens=SUMMARY_MAX_TOKENS,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                response_text = response.content[0].text.strip()

                # Убираем markdown-обёртки
                if response_text.startswith("```"):
                    response_text = re.sub(r'^```\w*\n?', '', response_text)
                    response_text = re.sub(r'\n?```$', '', response_text)

                result = json.loads(response_text)

                # Дополняем метаданными
                date_start, date_end = self._get_date_range(messages)

                summary = {
                    "jid": jid,
                    "contact_name": contact_name,
                    "short_summary": result.get("short_summary", ""),
                    "client_wanted": result.get("client_wanted", ""),
                    "proposed": result.get("proposed", ""),
                    "outcome": result.get("outcome", ""),
                    "key_points": result.get("key_points", []),
                    "message_count": len(messages),
                    "date_range": f"{date_start} - {date_end}" if date_start else "",
                    "last_message_date": date_end,
                    "dialog_status": result.get("dialog_status", "pending"),
                    "products_mentioned": result.get("products_mentioned", []),
                    "amounts_mentioned": result.get("amounts_mentioned", []),
                    "dates_mentioned": result.get("dates_mentioned", []),
                    "messages_hash": self.cache._compute_hash(messages),
                    "summarized_at": datetime.now().isoformat(),
                    "confidence": result.get("confidence", 0.8)
                }

                return summary

            except json.JSONDecodeError as e:
                print(f"  Попытка {attempt + 1}: Ошибка парсинга JSON: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"  Попытка {attempt + 1}: Ошибка API: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)

        # Fallback если все попытки неудачны
        return self._fallback_summary(jid, messages, contact_info)

    def _fallback_summary(self, jid: str, messages: List[Dict], contact_info: Dict) -> Dict:
        """Базовая суммаризация без API (на основе правил)."""

        contact_name = contact_info.get('name', '') or contact_info.get('chat_name', '') or jid
        all_text = ' '.join([m.get('text', '') for m in messages]).lower()

        # Определяем что клиент хотел
        client_wanted = "Не определено"
        if any(w in all_text for w in ['цена', 'сколько', 'стоимость']):
            client_wanted = "Узнать цену"
        elif any(w in all_text for w in ['бронь', 'забронир', 'заказ']):
            client_wanted = "Забронировать услугу"
        elif any(w in all_text for w in ['экскурсия', 'тур', 'сафари']):
            client_wanted = "Экскурсия/тур"

        # Определяем статус
        dialog_status = "pending"
        if any(w in all_text for w in ['подтвержд', 'оплач', 'готово', 'забронир']):
            dialog_status = "completed"
        elif any(w in all_text for w in ['отказ', 'отмен', 'не надо', 'передумал']):
            dialog_status = "cancelled"

        # Извлекаем суммы
        amounts = re.findall(r'\d+(?:\s*(?:aed|дирхам|руб|usd|долл|\$|₽))', all_text, re.IGNORECASE)

        # Извлекаем даты
        dates = re.findall(r'\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?', all_text)

        date_start, date_end = self._get_date_range(messages)

        return {
            "jid": jid,
            "contact_name": contact_name,
            "short_summary": f"Диалог с {contact_name}, {len(messages)} сообщений",
            "client_wanted": client_wanted,
            "proposed": "Требуется ручной анализ",
            "outcome": "Требуется ручной анализ",
            "key_points": ["Автоматическая суммаризация недоступна"],
            "message_count": len(messages),
            "date_range": f"{date_start} - {date_end}" if date_start else "",
            "last_message_date": date_end,
            "dialog_status": dialog_status,
            "products_mentioned": [],
            "amounts_mentioned": amounts[:5],
            "dates_mentioned": dates[:5],
            "messages_hash": self.cache._compute_hash(messages),
            "summarized_at": datetime.now().isoformat(),
            "confidence": 0.3
        }

    def summarize_batch(
        self,
        dialogs: List[Tuple[str, List[Dict], Dict]],
        force: bool = False,
        progress_callback: callable = None
    ) -> List[Dict]:
        """
        Суммаризировать батч диалогов.

        Args:
            dialogs: Список кортежей (jid, messages, contact_info)
            force: Принудительная пересуммаризация
            progress_callback: Функция для отслеживания прогресса

        Returns:
            Список суммаризаций
        """
        results = []

        for i, (jid, messages, contact_info) in enumerate(dialogs):
            if progress_callback:
                progress_callback(i + 1, len(dialogs), jid)

            summary = self.summarize_dialog(jid, messages, contact_info, force)
            if summary:
                results.append(summary)

            # Небольшая пауза между запросами к API
            if self.client and i < len(dialogs) - 1:
                time.sleep(0.5)

        return results


# ===============================================================
# ПОИСК ПО СУММАРИЗАЦИЯМ
# ===============================================================

class SummarySearcher:
    """Поиск по суммаризациям диалогов."""

    def __init__(self, summaries: List[Dict]):
        self.summaries = summaries
        self._build_index()

    def _build_index(self):
        """Построить индекс для поиска."""
        self.by_status = defaultdict(list)
        self.by_product = defaultdict(list)

        for s in self.summaries:
            # По статусу
            self.by_status[s.get('dialog_status', 'unknown')].append(s)

            # По продуктам
            for product in s.get('products_mentioned', []):
                self.by_product[product.lower()].append(s)

    def search(self, query: str) -> List[Dict]:
        """
        Поиск по тексту суммаризации.

        Args:
            query: Поисковый запрос

        Returns:
            Список найденных суммаризаций
        """
        query_lower = query.lower()
        results = []

        for s in self.summaries:
            # Поиск по всем текстовым полям
            searchable = ' '.join([
                s.get('short_summary', ''),
                s.get('client_wanted', ''),
                s.get('proposed', ''),
                s.get('outcome', ''),
                s.get('contact_name', ''),
                ' '.join(s.get('key_points', [])),
                ' '.join(s.get('products_mentioned', [])),
            ]).lower()

            if query_lower in searchable:
                results.append(s)

        return results

    def filter_by_status(self, status: str) -> List[Dict]:
        """Фильтр по статусу диалога."""
        return self.by_status.get(status, [])

    def filter_by_product(self, product: str) -> List[Dict]:
        """Фильтр по упомянутому продукту."""
        return self.by_product.get(product.lower(), [])

    def get_pending(self) -> List[Dict]:
        """Получить диалоги, ожидающие ответа."""
        return self.filter_by_status('pending')

    def get_active(self) -> List[Dict]:
        """Получить активные диалоги."""
        return self.filter_by_status('active')

    def get_statistics(self) -> Dict:
        """Получить статистику по суммаризациям."""
        stats = {
            "total": len(self.summaries),
            "by_status": {},
            "by_confidence": {
                "high": 0,    # > 0.8
                "medium": 0,  # 0.5-0.8
                "low": 0,     # < 0.5
            },
            "avg_confidence": 0,
            "products": defaultdict(int),
        }

        total_confidence = 0

        for s in self.summaries:
            # По статусу
            status = s.get('dialog_status', 'unknown')
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # По уверенности
            conf = s.get('confidence', 0)
            total_confidence += conf
            if conf > 0.8:
                stats["by_confidence"]["high"] += 1
            elif conf >= 0.5:
                stats["by_confidence"]["medium"] += 1
            else:
                stats["by_confidence"]["low"] += 1

            # По продуктам
            for product in s.get('products_mentioned', []):
                stats["products"][product] += 1

        if self.summaries:
            stats["avg_confidence"] = total_confidence / len(self.summaries)

        # Топ продукты
        stats["top_products"] = sorted(
            stats["products"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return stats


# ===============================================================
# ЭКСПОРТ
# ===============================================================

def export_to_json(summaries: List[Dict], output_path: Path):
    """Экспорт в JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "generated_at": datetime.now().isoformat(),
        "total_dialogs": len(summaries),
        "summaries": summaries
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"JSON экспортирован: {output_path}")


def export_to_markdown(summaries: List[Dict], output_path: Path):
    """Экспорт в Markdown."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Группируем по статусу
    by_status = defaultdict(list)
    for s in summaries:
        by_status[s.get('dialog_status', 'unknown')].append(s)

    # Порядок статусов
    status_order = ['pending', 'active', 'completed', 'cancelled', 'unknown']
    status_names = {
        'pending': 'Ожидают ответа',
        'active': 'Активные',
        'completed': 'Завершённые',
        'cancelled': 'Отменённые',
        'unknown': 'Прочие',
    }
    status_emoji = {
        'pending': '---',
        'active': '',
        'completed': '',
        'cancelled': 'x',
        'unknown': '?',
    }

    lines = [
        f"# Суммаризация диалогов",
        f"",
        f"*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*",
        f"*Всего диалогов: {len(summaries)}*",
        f"",
        "---",
        "",
    ]

    # Статистика
    lines.append("## Статистика")
    lines.append("")
    lines.append("| Статус | Количество |")
    lines.append("|--------|------------|")
    for status in status_order:
        if status in by_status:
            lines.append(f"| {status_names.get(status, status)} | {len(by_status[status])} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Диалоги по статусам
    for status in status_order:
        if status not in by_status:
            continue

        dialogs = by_status[status]
        emoji = status_emoji.get(status, '')

        lines.append(f"## {emoji} {status_names.get(status, status)} ({len(dialogs)})")
        lines.append("")

        for s in dialogs:
            lines.append(f"### {s.get('contact_name', s.get('jid', 'Unknown'))}")
            lines.append("")
            lines.append(f"**{s.get('short_summary', '')}**")
            lines.append("")
            lines.append(f"- **Клиент хотел:** {s.get('client_wanted', '-')}")
            lines.append(f"- **Предложено:** {s.get('proposed', '-')}")
            lines.append(f"- **Итог:** {s.get('outcome', '-')}")
            lines.append("")

            if s.get('key_points'):
                lines.append("**Ключевые моменты:**")
                for kp in s.get('key_points', []):
                    lines.append(f"- {kp}")
                lines.append("")

            # Метаданные
            lines.append(f"*Сообщений: {s.get('message_count', 0)} | "
                        f"Период: {s.get('date_range', '-')} | "
                        f"Уверенность: {s.get('confidence', 0):.0%}*")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Markdown экспортирован: {output_path}")


# ===============================================================
# ЗАГРУЗКА ДАННЫХ
# ===============================================================

def load_messages(messages_path: Path) -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """Загрузить все сообщения и сгруппировать по JID."""
    messages = []
    messages_by_jid = defaultdict(list)

    if not messages_path.exists():
        print(f"ОШИБКА: Файл не найден: {messages_path}")
        return messages, messages_by_jid

    print(f"Загрузка сообщений из: {messages_path}")

    with open(messages_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                messages.append(msg)

                jid = msg.get('jid', '')
                if jid:
                    messages_by_jid[jid].append(msg)
            except json.JSONDecodeError:
                if line_num <= 5:
                    print(f"  Строка {line_num}: ошибка JSON")

    print(f"Загружено: {len(messages)} сообщений, {len(messages_by_jid)} диалогов")
    return messages, dict(messages_by_jid)


def load_existing_summaries(summaries_path: Path) -> List[Dict]:
    """Загрузить существующие суммаризации."""
    if not summaries_path.exists():
        return []

    try:
        with open(summaries_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('summaries', [])
    except (json.JSONDecodeError, IOError):
        return []


# ===============================================================
# CLI
# ===============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Суммаризация диалогов WhatsApp через Claude API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python summarize_dialog.py                        # Суммаризация всех диалогов
  python summarize_dialog.py --force                # Принудительная пересуммаризация
  python summarize_dialog.py --limit 10             # Только первые 10 диалогов
  python summarize_dialog.py --search "яхта"        # Поиск по суммаризациям
  python summarize_dialog.py --status pending       # Фильтр по статусу
  python summarize_dialog.py --min-messages 10      # Только диалоги с 10+ сообщений
  python summarize_dialog.py --update-only          # Только новые/изменённые
        """
    )

    # Входные/выходные файлы
    parser.add_argument(
        "--input",
        default=str(RAW_DIR / "all_messages.jsonl"),
        help="Путь к all_messages.jsonl"
    )
    parser.add_argument(
        "--output-json",
        default=str(SUMMARIES_JSON_FILE),
        help="Путь для JSON вывода"
    )
    parser.add_argument(
        "--output-md",
        default=str(SUMMARIES_MD_FILE),
        help="Путь для Markdown вывода"
    )

    # Режимы работы
    parser.add_argument(
        "--force",
        action="store_true",
        help="Принудительная пересуммаризация (игнорировать кэш)"
    )
    parser.add_argument(
        "--update-only",
        action="store_true",
        help="Суммаризировать только новые/изменённые диалоги"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Не использовать кэш"
    )

    # Фильтры
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Ограничить количество диалогов (0 = все)"
    )
    parser.add_argument(
        "--min-messages",
        type=int,
        default=3,
        help="Минимальное количество сообщений в диалоге (по умолчанию: 3)"
    )

    # Поиск
    parser.add_argument(
        "--search",
        help="Поиск по существующим суммаризациям"
    )
    parser.add_argument(
        "--status",
        choices=['active', 'pending', 'completed', 'cancelled'],
        help="Фильтр по статусу диалога"
    )

    # Вывод
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Показать статистику по суммаризациям"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("СУММАРИЗАЦИЯ ДИАЛОГОВ ЧЕРЕЗ CLAUDE API")
    print("=" * 60)

    # Режим поиска по существующим суммаризациям
    if args.search or args.status or args.stats:
        summaries = load_existing_summaries(Path(args.output_json))

        if not summaries:
            print("Суммаризации не найдены. Сначала запустите суммаризацию.")
            sys.exit(1)

        searcher = SummarySearcher(summaries)

        if args.stats:
            stats = searcher.get_statistics()
            print("\nСТАТИСТИКА:")
            print(f"  Всего диалогов: {stats['total']}")
            print(f"  Средняя уверенность: {stats['avg_confidence']:.0%}")
            print("\n  По статусу:")
            for status, count in stats['by_status'].items():
                print(f"    {status}: {count}")
            print("\n  Топ продукты:")
            for product, count in stats.get('top_products', [])[:5]:
                print(f"    {product}: {count}")
            sys.exit(0)

        if args.status:
            results = searcher.filter_by_status(args.status)
        else:
            results = searcher.search(args.search)

        print(f"\nНайдено: {len(results)} диалогов\n")

        for s in results[:20]:  # Показываем первые 20
            print(f"[{s.get('dialog_status', '?')}] {s.get('contact_name', s.get('jid'))}")
            print(f"  {s.get('short_summary', '')}")
            print(f"  Клиент хотел: {s.get('client_wanted', '-')}")
            print(f"  Итог: {s.get('outcome', '-')}")
            print()

        sys.exit(0)

    # Основной режим - суммаризация
    print(f"\nВходной файл: {args.input}")
    print(f"Выходные файлы:")
    print(f"  - JSON: {args.output_json}")
    print(f"  - MD: {args.output_md}")
    print(f"API ключ: {'настроен' if ANTHROPIC_API_KEY else 'НЕ НАСТРОЕН'}")

    # Инициализация кэша
    if args.no_cache:
        cache = SummaryCache(Path("/dev/null"))
    else:
        cache = SummaryCache(SUMMARY_CACHE_FILE)

    # Инициализация суммаризатора
    summarizer = DialogSummarizer(ANTHROPIC_API_KEY, cache)

    # Загрузка данных
    messages, messages_by_jid = load_messages(Path(args.input))

    if not messages:
        print("ОШИБКА: Нет сообщений для обработки")
        sys.exit(1)

    # Подготовка диалогов для суммаризации
    dialogs_to_process = []

    for jid, jid_messages in messages_by_jid.items():
        # Фильтр по минимальному количеству сообщений
        if len(jid_messages) < args.min_messages:
            continue

        # Проверка на необходимость обновления
        if args.update_only and not cache.needs_update(jid, jid_messages):
            continue

        contact_info = {
            'name': jid_messages[0].get('chat_name', ''),
            'jid': jid
        }

        dialogs_to_process.append((jid, jid_messages, contact_info))

    # Ограничение количества
    if args.limit > 0:
        dialogs_to_process = dialogs_to_process[:args.limit]

    print(f"\nДиалогов для суммаризации: {len(dialogs_to_process)}")

    if not dialogs_to_process:
        print("Нет диалогов для суммаризации (возможно, все уже в кэше)")
        sys.exit(0)

    # Суммаризация
    def progress_callback(current, total, jid):
        if args.verbose:
            print(f"  [{current}/{total}] {jid}")
        elif current % 10 == 0:
            print(f"  Обработано: {current}/{total}")

    print("\nСуммаризация...")
    summaries = summarizer.summarize_batch(
        dialogs_to_process,
        force=args.force,
        progress_callback=progress_callback
    )

    # Добавляем существующие суммаризации (если update-only)
    if args.update_only:
        existing = load_existing_summaries(Path(args.output_json))
        existing_jids = {s['jid'] for s in summaries}

        for es in existing:
            if es['jid'] not in existing_jids:
                summaries.append(es)

    # Сохранение кэша
    cache.finalize()

    # Экспорт
    print("\nЭкспорт результатов...")
    export_to_json(summaries, Path(args.output_json))
    export_to_markdown(summaries, Path(args.output_md))

    # Статистика
    searcher = SummarySearcher(summaries)
    stats = searcher.get_statistics()

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"Суммаризировано диалогов: {len(summaries)}")
    print(f"Средняя уверенность: {stats['avg_confidence']:.0%}")
    print("\nПо статусу:")
    for status, count in stats['by_status'].items():
        print(f"  {status}: {count}")

    print("\nСуммаризация завершена!")


if __name__ == "__main__":
    main()
