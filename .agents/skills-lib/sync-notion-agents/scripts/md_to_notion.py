#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Конвертер Markdown в Notion Blocks.

Поддерживает:
- Заголовки (H1, H2, H3)
- Параграфы
- Списки (маркированные и нумерованные)
- Код (inline и блоки)
- Выделение (bold, italic, strikethrough)
- Горизонтальные линии
- Цитаты (blockquote)
- Таблицы (базовая поддержка)
"""

import re
from typing import List, Dict, Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# ТИПЫ NOTION BLOCKS
# ═══════════════════════════════════════════════════════════════════════════════

def create_heading_1(text: str) -> Dict:
    """Создать блок заголовка H1."""
    return {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": parse_rich_text(text)
        }
    }


def create_heading_2(text: str) -> Dict:
    """Создать блок заголовка H2."""
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": parse_rich_text(text)
        }
    }


def create_heading_3(text: str) -> Dict:
    """Создать блок заголовка H3."""
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": parse_rich_text(text)
        }
    }


def create_paragraph(text: str) -> Dict:
    """Создать блок параграфа."""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": parse_rich_text(text)
        }
    }


def create_bulleted_list_item(text: str, children: List[Dict] = None) -> Dict:
    """Создать элемент маркированного списка."""
    block = {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": parse_rich_text(text)
        }
    }
    if children:
        block["bulleted_list_item"]["children"] = children
    return block


def create_numbered_list_item(text: str, children: List[Dict] = None) -> Dict:
    """Создать элемент нумерованного списка."""
    block = {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": parse_rich_text(text)
        }
    }
    if children:
        block["numbered_list_item"]["children"] = children
    return block


def create_code_block(code: str, language: str = "plain text") -> Dict:
    """Создать блок кода."""
    # Notion поддерживает ограниченный набор языков
    supported_languages = {
        "python", "javascript", "typescript", "java", "c", "cpp", "csharp",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "sql",
        "html", "css", "json", "yaml", "xml", "markdown", "bash", "shell",
        "powershell", "dockerfile", "plain text"
    }

    # Нормализуем язык
    lang = language.lower().strip()
    if lang in ["py", "python3"]:
        lang = "python"
    elif lang in ["js", "node"]:
        lang = "javascript"
    elif lang in ["ts"]:
        lang = "typescript"
    elif lang in ["sh", "zsh"]:
        lang = "bash"
    elif lang not in supported_languages:
        lang = "plain text"

    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": code}}],
            "language": lang
        }
    }


def create_quote(text: str) -> Dict:
    """Создать блок цитаты."""
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": parse_rich_text(text)
        }
    }


def create_divider() -> Dict:
    """Создать горизонтальную линию."""
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }


def create_callout(text: str, emoji: str = "💡") -> Dict:
    """Создать callout блок."""
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": parse_rich_text(text),
            "icon": {"type": "emoji", "emoji": emoji}
        }
    }


def create_toggle(title: str, children: List[Dict] = None) -> Dict:
    """Создать toggle блок (сворачиваемый)."""
    block = {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": parse_rich_text(title)
        }
    }
    if children:
        block["toggle"]["children"] = children
    return block


def create_table(rows: List[List[str]], has_header: bool = True) -> Dict:
    """
    Создать таблицу.

    Args:
        rows: Список строк, каждая строка — список ячеек
        has_header: Первая строка — заголовок
    """
    if not rows:
        return create_paragraph("(пустая таблица)")

    table_width = max(len(row) for row in rows)

    table_rows = []
    for row in rows:
        # Дополняем строку до нужной ширины
        cells = row + [""] * (table_width - len(row))
        table_row = {
            "type": "table_row",
            "table_row": {
                "cells": [
                    [{"type": "text", "text": {"content": str(cell)}}]
                    for cell in cells
                ]
            }
        }
        table_rows.append(table_row)

    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": has_header,
            "has_row_header": False,
            "children": table_rows
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RICH TEXT PARSING
# ═══════════════════════════════════════════════════════════════════════════════

def parse_rich_text(text: str) -> List[Dict]:
    """
    Парсить текст с форматированием в Notion rich_text.

    Поддерживает:
    - **bold** или __bold__
    - *italic* или _italic_
    - ~~strikethrough~~
    - `code`
    - [link](url)
    """
    if not text:
        return []

    # Результирующий список rich_text объектов
    result = []

    # Паттерны форматирования (порядок важен!)
    patterns = [
        # Bold + Italic
        (r'\*\*\*(.*?)\*\*\*', {'bold': True, 'italic': True}),
        (r'___(.*?)___', {'bold': True, 'italic': True}),
        # Bold
        (r'\*\*(.*?)\*\*', {'bold': True}),
        (r'__(.*?)__', {'bold': True}),
        # Italic
        (r'\*(.*?)\*', {'italic': True}),
        (r'_(.*?)_', {'italic': True}),
        # Strikethrough
        (r'~~(.*?)~~', {'strikethrough': True}),
        # Code
        (r'`(.*?)`', {'code': True}),
        # Links
        (r'\[(.*?)\]\((.*?)\)', 'link'),
    ]

    # Простой подход: обрабатываем текст последовательно
    # Для сложного форматирования нужен более продвинутый парсер

    # Сначала обрабатываем ссылки
    link_pattern = r'\[(.*?)\]\((.*?)\)'

    def process_segment(segment: str, annotations: Dict = None) -> List[Dict]:
        """Обработать сегмент текста."""
        if annotations is None:
            annotations = {}

        parts = []
        last_end = 0

        for match in re.finditer(link_pattern, segment):
            # Текст до ссылки
            if match.start() > last_end:
                plain_text = segment[last_end:match.start()]
                if plain_text:
                    parts.append(create_text_object(plain_text, annotations))

            # Ссылка
            link_text = match.group(1)
            link_url = match.group(2)
            link_annotations = annotations.copy()
            parts.append(create_text_object(link_text, link_annotations, link_url))

            last_end = match.end()

        # Остаток текста
        if last_end < len(segment):
            remaining = segment[last_end:]
            if remaining:
                parts.append(create_text_object(remaining, annotations))

        # Если не было ссылок
        if not parts and segment:
            parts.append(create_text_object(segment, annotations))

        return parts

    # Обрабатываем форматирование
    # Упрощённый подход — заменяем маркеры
    processed_text = text
    segments = []

    # Bold
    bold_parts = re.split(r'(\*\*.*?\*\*|__.*?__)', processed_text)

    for part in bold_parts:
        if re.match(r'\*\*.*?\*\*', part):
            inner = part[2:-2]
            segments.extend(process_inner_formatting(inner, {'bold': True}))
        elif re.match(r'__.*?__', part):
            inner = part[2:-2]
            segments.extend(process_inner_formatting(inner, {'bold': True}))
        elif part:
            segments.extend(process_inner_formatting(part, {}))

    return segments if segments else [create_text_object(text)]


def process_inner_formatting(text: str, base_annotations: Dict) -> List[Dict]:
    """Обработать вложенное форматирование (italic, code, links)."""
    result = []

    # Паттерн для italic и code
    pattern = r'(\*[^*]+\*|_[^_]+_|`[^`]+`|\[[^\]]+\]\([^)]+\))'
    parts = re.split(pattern, text)

    for part in parts:
        if not part:
            continue

        annotations = base_annotations.copy()
        content = part
        link_url = None

        # Italic
        if re.match(r'^\*[^*]+\*$', part) or re.match(r'^_[^_]+_$', part):
            content = part[1:-1]
            annotations['italic'] = True
        # Code
        elif re.match(r'^`[^`]+`$', part):
            content = part[1:-1]
            annotations['code'] = True
        # Link
        elif re.match(r'^\[.*?\]\(.*?\)$', part):
            match = re.match(r'^\[(.*?)\]\((.*?)\)$', part)
            if match:
                content = match.group(1)
                link_url = match.group(2)

        result.append(create_text_object(content, annotations, link_url))

    return result if result else [create_text_object(text, base_annotations)]


def create_text_object(content: str, annotations: Dict = None, link: str = None) -> Dict:
    """Создать объект rich_text."""
    if annotations is None:
        annotations = {}

    text_obj = {
        "type": "text",
        "text": {
            "content": content[:2000]  # Notion limit
        },
        "annotations": {
            "bold": annotations.get('bold', False),
            "italic": annotations.get('italic', False),
            "strikethrough": annotations.get('strikethrough', False),
            "underline": annotations.get('underline', False),
            "code": annotations.get('code', False),
            "color": annotations.get('color', "default")
        }
    }

    if link:
        text_obj["text"]["link"] = {"url": link}

    return text_obj


# ═══════════════════════════════════════════════════════════════════════════════
# MARKDOWN PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_markdown(md_content: str) -> List[Dict]:
    """
    Парсить Markdown контент в список Notion блоков.

    Args:
        md_content: Markdown текст

    Returns:
        Список Notion block объектов
    """
    blocks = []
    lines = md_content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Пустая строка — пропускаем
        if not stripped:
            i += 1
            continue

        # Блок кода (```)
        if stripped.startswith('```'):
            language = stripped[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_content = '\n'.join(code_lines)
            blocks.append(create_code_block(code_content, language))
            i += 1  # Пропускаем закрывающие ```
            continue

        # Горизонтальная линия
        if stripped in ['---', '***', '___'] or re.match(r'^[-*_]{3,}$', stripped):
            blocks.append(create_divider())
            i += 1
            continue

        # Заголовки
        if stripped.startswith('# '):
            blocks.append(create_heading_1(stripped[2:]))
            i += 1
            continue
        if stripped.startswith('## '):
            blocks.append(create_heading_2(stripped[3:]))
            i += 1
            continue
        if stripped.startswith('### ') or stripped.startswith('#### ') or stripped.startswith('##### '):
            # H3 и ниже → H3 в Notion
            text = re.sub(r'^#{3,6}\s+', '', stripped)
            blocks.append(create_heading_3(text))
            i += 1
            continue

        # Цитата
        if stripped.startswith('> '):
            quote_lines = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('> '):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            blocks.append(create_quote('\n'.join(quote_lines)))
            continue

        # Маркированный список
        if re.match(r'^[-*+]\s+', stripped):
            list_items = []
            while i < len(lines):
                current = lines[i]
                match = re.match(r'^(\s*)([-*+])\s+(.*)$', current)
                if not match:
                    break
                indent = len(match.group(1))
                text = match.group(3)

                # Простой список без вложенности
                if indent == 0:
                    list_items.append(create_bulleted_list_item(text))
                i += 1
            blocks.extend(list_items)
            continue

        # Нумерованный список
        if re.match(r'^\d+\.\s+', stripped):
            list_items = []
            while i < len(lines):
                current = lines[i].strip()
                match = re.match(r'^(\d+)\.\s+(.*)$', current)
                if not match:
                    break
                text = match.group(2)
                list_items.append(create_numbered_list_item(text))
                i += 1
            blocks.extend(list_items)
            continue

        # Таблица
        if '|' in stripped and not stripped.startswith('|'):
            stripped = '|' + stripped + '|'

        if stripped.startswith('|') and stripped.endswith('|'):
            table_rows = []
            while i < len(lines):
                current = lines[i].strip()
                if not current.startswith('|'):
                    break

                # Пропускаем строку разделителя (|---|---|)
                if re.match(r'^\|[\s\-:|]+\|$', current):
                    i += 1
                    continue

                # Парсим ячейки
                cells = [cell.strip() for cell in current.split('|')[1:-1]]
                if cells:
                    table_rows.append(cells)
                i += 1

            if table_rows:
                blocks.append(create_table(table_rows))
            continue

        # Параграф (всё остальное)
        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            # Прерываем параграф на пустой строке или специальных элементах
            if (not next_line or
                next_line.startswith('#') or
                next_line.startswith('```') or
                next_line.startswith('>') or
                next_line.startswith('|') or
                re.match(r'^[-*+]\s+', next_line) or
                re.match(r'^\d+\.\s+', next_line) or
                next_line in ['---', '***', '___']):
                break
            paragraph_lines.append(next_line)
            i += 1

        blocks.append(create_paragraph(' '.join(paragraph_lines)))

    return blocks


def split_blocks_for_api(blocks: List[Dict], max_blocks: int = 100) -> List[List[Dict]]:
    """
    Разбить список блоков на части для API (лимит 100 блоков за запрос).

    Args:
        blocks: Список блоков
        max_blocks: Максимум блоков в одном запросе

    Returns:
        Список списков блоков
    """
    return [blocks[i:i + max_blocks] for i in range(0, len(blocks), max_blocks)]


# ═══════════════════════════════════════════════════════════════════════════════
# ТЕСТИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Тестовый Markdown
    test_md = """# Заголовок H1

## Заголовок H2

### Заголовок H3

Обычный параграф с **жирным** и *курсивом*, а также `кодом`.

- Пункт 1
- Пункт 2
- Пункт 3

1. Первый
2. Второй
3. Третий

> Цитата
> на несколько строк

```python
def hello():
    print("Hello, World!")
```

---

| Колонка 1 | Колонка 2 |
|-----------|-----------|
| Ячейка 1  | Ячейка 2  |
| Ячейка 3  | Ячейка 4  |

Ссылка: [Google](https://google.com)
"""

    import json

    blocks = parse_markdown(test_md)
    print(f"Создано блоков: {len(blocks)}")
    print("\n--- JSON ---")
    print(json.dumps(blocks[:3], indent=2, ensure_ascii=False))
