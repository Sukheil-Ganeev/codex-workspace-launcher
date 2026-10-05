---
id: EXP-001
date: 2026-02-15
type: fix
severity: critical
tags: [puzzlebot, formatting, hotkeys, fallback]
source: experience/_index.md
---

## Проблема

Горячая клавиша `Ctrl+Shift+M` в PuzzleBot вместо моноширинного форматирования вводит символ `m` и может стирать выделенный текст.

## Решение

Использовать кнопку `</>` на плавающей панели форматирования через визуальный сценарий:
1. `screenshot`
2. визуальный поиск кнопки
3. `click`

## Урок

Для web-редакторов с нестабильными хоткеями всегда держать fallback-путь через screenshot + click.