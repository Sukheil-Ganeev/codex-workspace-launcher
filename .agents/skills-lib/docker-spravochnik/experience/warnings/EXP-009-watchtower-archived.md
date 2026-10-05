---
id: EXP-009
date: 2026-02-17
type: warning
severity: critical
tags: [watchtower, deprecated, archived, auto-update]
---

## Что НЕ делать

НЕ использовать Watchtower для автообновления контейнеров.

## Почему

Проект официально заархивирован (декабрь 2025). Несовместим с Docker 28+/29+:
- Watchtower использует Docker API 1.25
- Docker Engine 29 требует API >= 1.44
- Результат: Watchtower НЕ может подключиться к Docker daemon

## Правильный способ

Альтернативы:
- **WUD (What's Up Docker):** мониторинг + автообновление + web dashboard
  - `docker run -d -v /var/run/docker.sock:/var/run/docker.sock whatsupDocker/whats-up-docker`
- **DIUN (Docker Image Update Notifier):** только нотификации (Telegram, Slack, email), НЕ обновляет контейнеры
  - `docker run -d -v /var/run/docker.sock:/var/run/docker.sock crazymax/diun`

## Урок

Deprecated инструменты быстро становятся опасными, а не просто "старыми". Watchtower не просто "не обновляется" -- он ЛОМАЕТ деплой при обновлении Docker Engine.
