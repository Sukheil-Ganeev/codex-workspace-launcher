# Docker-справочник

Production-ready руководство по Docker для контейнеризации и деплоя приложений.

## Quick Start

1. Прочитай SKILL.md -- полный обзор Docker (3000+ слов, 10 модулей)
2. Скопируй шаблон из assets/templates/ для своего проекта
3. При проблемах: references/troubleshooting.md

## Prerequisites

- Docker Engine 29.x или Docker Desktop 4.60+
- Docker Compose v2.40+ (CLI v5.x)
- Git (для CI/CD примеров)

## Версии

- Docker Engine 29.x
- Docker Compose v2.40+ (CLI v5.x)
- Docker Desktop 4.60
- Февраль 2026

## Структура

```
docker-справочник/
├── SKILL.md                  # Основной справочник (~5000 слов, 10 модулей)
├── README.md                 # Этот файл
├── references/
│   ├── cheatsheet.md         # Шпаргалка: все команды Docker + Compose
│   ├── faq.md                # FAQ: 25+ вопросов-ответов
│   ├── troubleshooting.md    # Решение типичных проблем (17+)
│   ├── dockerfile-guide.md   # Полное руководство по Dockerfile
│   ├── compose-guide.md      # Полное руководство по Docker Compose
│   ├── security-production.md # Безопасность и production чеклист
│   ├── networking-volumes.md # Сети и хранилища подробно
│   └── registry-ci-cd.md    # Registry, CI/CD, деплой
├── assets/
│   ├── templates/
│   │   ├── Dockerfile.node           # Multi-stage Node.js 22
│   │   ├── Dockerfile.python         # Multi-stage Python 3.13
│   │   ├── docker-compose.dev.yml    # Dev-окружение (app+db+redis)
│   │   ├── docker-compose.prod.yml   # Production (app+db+redis+nginx)
│   │   ├── .dockerignore             # Стандартный для Node.js + Python
│   │   ├── daemon.json               # Конфиг Docker daemon
│   │   ├── nginx.conf                # Reverse proxy шаблон
│   │   └── .github/workflows/
│   │       └── docker-ci.yml         # GitHub Actions CI/CD
│   └── examples/
│       ├── 01-simple-node-api/       # Минимальный Node.js API
│       ├── 02-python-flask-app/      # Flask + gunicorn multi-stage
│       ├── 03-fullstack-compose/     # nginx + Node.js + PostgreSQL + Redis
│       ├── 04-booking-api-uae/       # Booking API туризм ОАЭ
│       └── 05-ci-cd-pipeline/        # Полный CI/CD pipeline
├── scripts/
│   ├── cleanup-docker.sh             # Очистка Docker-ресурсов
│   ├── backup-volumes.sh             # Бэкап named volumes
│   └── deploy-compose.sh             # Deploy с healthcheck и rollback
└── experience/
    ├── _index.md             # Критические уроки (10 записей)
    ├── fixes/
    │   ├── EXP-001-rate-limits.md      # Rate Limits противоречия [critical]
    │   ├── EXP-002-docker-pricing.md   # Docker pricing ошибка [critical]
    │   └── EXP-003-pip-no-deps.md      # pip --no-deps [high]
    ├── improvements/
    │   ├── EXP-004-model-runner.md     # Docker Model Runner [medium]
    │   ├── EXP-005-mcp-toolkit.md      # Docker MCP Toolkit [medium]
    │   └── EXP-006-registry-v3.md      # Registry v3 GA [medium]
    ├── patterns/
    │   ├── EXP-007-compose-yaml-name.md # compose.yaml имя [medium]
    │   └── EXP-008-docker-vs-podman.md  # Docker vs Podman [low]
    └── warnings/
        ├── EXP-009-watchtower-archived.md # Watchtower archived [critical]
        └── EXP-010-deprecated-3-params.md # Deprecated 3 параметра [high]
```

## Как использовать

1. **SKILL.md** -- основной файл, содержит все модули (0-9), типичные ошибки, ресурсы
2. **references/cheatsheet.md** -- быстрый поиск команд и Dockerfile инструкций
3. **references/faq.md** -- ответы на частые вопросы (лицензирование, альтернативы, AI-фичи)
4. **references/troubleshooting.md** -- диагностика и решение проблем
5. **assets/templates/** -- готовые шаблоны Dockerfile, Compose, CI/CD
6. **assets/examples/** -- рабочие примеры от простого к сложному
7. **scripts/** -- утилиты для очистки, бэкапа и деплоя

## Модули SKILL.md

| # | Модуль | Содержание |
|---|--------|-----------|
| 0 | Установка | Docker Desktop, Engine, daemon.json, лицензирование |
| 1 | Основы | Архитектура, образы vs контейнеры, ключевые команды |
| 2 | Образы | Base images, multi-platform, управление |
| 3 | Dockerfile | Инструкции, multi-stage, BuildKit, .dockerignore |
| 4 | Compose | Структура, Watch, Model Runner, profiles |
| 5 | Volumes | Named volumes, bind mounts, tmpfs, backup |
| 6 | Networking | Bridge, host, overlay, DNS, port binding |
| 7 | Registry | Docker Hub, GHCR, self-hosted, Scout |
| 8 | Security | Rootless, secrets, production чеклист |
| 9 | CI/CD | GitHub Actions, кэширование, ARM-деплой |

## Связанные скиллы

- `git-github-справочник` -- GitHub Actions, GHCR
- `javascript-nodejs-справочник` -- контейнеризация Node.js
- `yandex-cloud-справочник` -- Serverless Containers
- `database-sql-справочник` -- PostgreSQL/Redis в Compose

## Ключевые исправления (из верификации)

- Rate Limits: 100 pulls/час Personal (с 1 апреля 2025)
- Цены: Pro=$9, Team=$15, Business=$24 (annual, с декабря 2024)
- golang base image: 1.26 (Go 1.26 вышел 10 февраля 2026)
- BuildKit: дефолтный с Engine 23.0 (2023)
- Registry v3: стабильный GA (июнь 2025)
- pip: --no-cache-dir (НЕ --no-deps)
- Watchtower: заархивирован (декабрь 2025), альтернативы: WUD, DIUN
- Compose CLI: ренумерация на v5.x (пропущены v3/v4)
- VirtioFS: дефолтный (не экспериментальный) для macOS 12.5+
- Docker Desktop: 4.60 текущая (февраль 2026)
