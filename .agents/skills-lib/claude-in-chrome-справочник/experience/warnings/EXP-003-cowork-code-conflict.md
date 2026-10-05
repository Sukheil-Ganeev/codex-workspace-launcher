---
id: EXP-003
date: 2026-02-16
type: warning
severity: critical
tags: [claude-desktop, claude-code, native-host, chrome-extension]
source: experience/_index.md
---

## Риск

Claude Desktop Cowork и Claude Code могут конфликтовать: оба регистрируют native messaging host для одного extension ID, но используют несовместимые сокет-форматы.

## Симптом

Ошибка `Browser extension is not connected` без очевидной причины.

## Что делать

- Отключить native host неиспользуемого приложения
- Полностью перезапустить Chrome

## Урок

При этой ошибке сначала проверять конфликт Cowork/Code, а уже потом всё остальное.