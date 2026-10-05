---
id: EXP-007
date: 2026-02-17
type: pattern
severity: medium
tags: [compose, naming, convention]
---

## Паттерн

Каноническое имя файла: `compose.yaml` (предпочтительно) или `compose.yml`.

## Когда использовать

В ЛЮБОМ новом проекте. При рефакторинге старых проектов -- переименовать.

## Правильный способ

Приоритет поиска файла Docker Compose (по убыванию):
1. `compose.yaml` -- **каноническое имя** (рекомендуется)
2. `compose.yml`
3. `docker-compose.yaml`
4. `docker-compose.yml` -- **legacy**, только для backwards compatibility

```bash
# Правильно (новый проект):
docker compose -f compose.yaml up -d

# Legacy (старый проект, работает но не рекомендуется):
docker compose -f docker-compose.yml up -d
```

## Урок

`docker-compose.yml` -- legacy-имя из эпохи docker-compose v1 (Python). Современный Compose CLI (v2/v5) предпочитает `compose.yaml`. При создании нового проекта всегда используй каноническое имя.
