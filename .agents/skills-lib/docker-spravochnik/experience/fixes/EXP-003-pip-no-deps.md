---
id: EXP-003
date: 2026-02-17
type: fix
severity: high
tags: [dockerfile, python, pip, dependencies]
---

## Проблема

Research предложил `pip install --no-deps` в Dockerfile для уменьшения размера образа.

## Контекст

`--no-deps` НЕ устанавливает транзитивные зависимости. Без lock-файла (pip-tools, poetry.lock) это ломает приложение в runtime -- модули импортируются, но их зависимости отсутствуют. Ошибка проявляется только при запуске контейнера, не при сборке.

## Решение

Правильные флаги для уменьшения размера:
- `--no-cache-dir` -- не кэшировать скачанные пакеты (уменьшение размера)
- `--no-compile` -- не создавать .pyc файлы
- `--no-deps` -- ТОЛЬКО в multi-stage с pre-built wheels из builder stage

```dockerfile
# Правильно:
RUN pip install --no-cache-dir -r requirements.txt

# Неправильно:
RUN pip install --no-deps -r requirements.txt
```

## Урок

Для обычного pip install в Dockerfile: `--no-cache-dir`, НЕ `--no-deps`. Флаг `--no-deps` безопасен только с полностью разрешёнными зависимостями (lock-файл или pre-built wheels).
