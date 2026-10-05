---
id: EXP-006
date: 2026-02-16
type: pattern
severity: high
tags: [puzzlebot, batch, pipeline, md-to-html]
source: experience/_index.md
---

## Паттерн: MD -> PuzzleBot

1. Офлайн-парсер читает MD и генерирует HTML-фрагменты + JSON-метаданные
2. Claude Code читает HTML с диска
3. `javascript_tool` вставляет HTML в `.ql-editor`
4. Выполняется обязательный Save workflow
5. Делается screenshot для верификации

## Зачем

Разделение офлайн-подготовки и онлайн-вставки даёт масштабируемость для batch-потока 100+ карточек.

## Урок

Для массовой загрузки контента лучший режим: Claude Code (файлы) + Chrome MCP (вставка и верификация в браузере).