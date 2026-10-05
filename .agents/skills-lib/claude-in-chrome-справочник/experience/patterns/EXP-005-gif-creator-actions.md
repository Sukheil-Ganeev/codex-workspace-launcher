---
id: EXP-005
date: 2026-02-16
type: pattern
severity: high
tags: [gif-creator, recording, export]
source: experience/_index.md
---

## Паттерн

Для `gif_creator` использовать только корректные actions:
- `start_recording`
- `stop_recording`
- `export`
- `clear`

## Важно

- Параметра `output_path` нет
- Для выгрузки использовать `download=true` + `filename`

## Урок

Перед использованием новых action-параметров проверять актуальную схему инструмента.