# Docs Optimizer Report — TouristBotEcosystem/CLAUDE.md
**Режим:** `optimize`
**Проект:** TouristBotEcosystem
**Стадия:** STABLE (деплой выполнен 2026-03-03, Batch 4 done)
**Score:** 3/5

---

## Фаза 1: Discovery — Анализ текущего CLAUDE.md

| Метрика | Значение | Статус |
|---------|----------|--------|
| Строк | 558 | 🔴 CRITICAL (>400) |
| ~Токенов | ~2,232 (~558×4) | 🟡 HIGH (>2,500 приближается) |
| Инструкций/правил | ~35 явных | ✅ OK |
| Дублирование | Высокое (команды, статус batch) | 🔴 |
| Content drift items | 3 | 🟡 MEDIUM |

**AP-01 (Context Stuffing):** CLAUDE.md 558 строк — вдвое больше цели 250 строк. Архитектурное дерево занимает ~315 строк из 558 (56% файла).

**AP-04 (Cache-Hostile Order):** Секция "Статус проекта" (динамическое) стоит вверху (строки 7-16), до статических секций команд и архитектуры.

**AP-10 (Monolithic Status):** Секция Batch-статусов содержит однострочные описания с 5-6 предложениями слитно, что затрудняет навигацию.

**AP-11 (Duplicate Commands):** Команды запуска ботов дублируются в секции "Команды" (строки 382-387) и в глобальном CLAUDE.md (D:/Downloads/CLAUDE.md).

**AP-20 (Protocol Sprawl):** Cloudflare Tunnel — полная инструкция развёртывания (строки 498-544, ~46 строк) не нужна ежесессионно. Это on-demand документация.

**Content Drift:**

| Файл | Упомянутое | Текущее | Severity |
|------|-----------|---------|----------|
| CLAUDE.md строка 362 | "Ботов: 3 (telegram_voice и telegram_content отключены)" | CLAUDE.md строка 214 описывает 4 бота включая telegram_voice | MEDIUM |
| CLAUDE.md строки 9-16 | Batch 1-6 DONE — статус описан в 6 длинных строках | STABLE — деплой давно выполнен | LOW |
| CLAUDE.md строка 557 | "Полный план: docs/plans/2026-03-02-merge-vtb-cf-plan.md" | Все batch завершены — план выполнен | LOW |

---

## Фаза 2: Tier-таблица классификации контента

| Tier | Контент | Секция (строки) | Что делать |
|------|---------|-----------------|-----------|
| **Essential** | Шапка проекта: название, git, стек | 1-5 | Оставить |
| **Essential** | Статус: краткая таблица batch (свёрнутая) | 7-16 | Сократить до 6-строчной таблицы |
| **Essential** | Стандарты дизайна (ссылки) | 18-26 | Оставить (только ссылки) |
| **Essential** | Команды: инфраструктура + запуск + тесты | 373-413 | Оставить, сократить |
| **Essential** | AI Backends таблица | 415-423 | Оставить (3 строки) |
| **Essential** | Деплой: ключевые параметры (таблица) | 460-481 | Оставить таблицу, убрать скрипты |
| **Essential** | Открытые проблемы → ссылка на ISSUES.md | 546-553 | Оставить (2 строки) |
| **Essential** | Статистика (таблица метрик) | 354-371 | Оставить, сократить |
| **On-demand** | Полное архитектурное дерево core/ | 38-211 | Переместить в docs/ARCHITECTURE.md |
| **On-demand** | Полное архитектурное дерево bots/ | 213-274 | Переместить в docs/ARCHITECTURE.md |
| **On-demand** | Полное архитектурное дерево config/data/tests/scripts/docs | 275-351 | Переместить в docs/ARCHITECTURE.md |
| **On-demand** | Зависимости (requirements.txt полный список) | 425-451 | Переместить в docs/DEPENDENCIES.md |
| **On-demand** | Источники (READ-ONLY) таблица | 28-33 | Переместить в docs/SOURCES.md |
| **On-demand** | Бизнес-контекст | 453-458 | Переместить в docs/BUSINESS_CONTEXT.md |
| **On-demand** | Cloudflare Tunnel — полная инструкция | 498-544 | Переместить в docs/CLOUDFLARE_SETUP.md |
| **On-demand** | Скрипты деплоя (описание) | 483-495 | Переместить в docs/DEPLOY.md |
| **Archive** | "Что нужно сделать (4 шага)" Cloudflare | 508-529 | Статус ✅ НАСТРОЕН — архивировать в docs/archive/cloudflare-setup-2026-03-04.md |
| **Archive** | "Старый туннель voicebot" — Oracle Cloud | 544 | Устаревшее примечание — в .claudeignore или удалить |
| **Archive** | "Альтернатива (через браузер)" Cloudflare | 536-541 | Уже настроено ✅ — архивировать |
| **Archive** | "План миграции" секция (строка 555-557) | 555-558 | Все batch DONE — архив docs/plans/ |

---

## Фаза 3: Before/After метрики

| Метрика | До | После | Экономия |
|---------|-----|-------|---------|
| Строк CLAUDE.md | 558 | ~220 | -338 строк (-61%) |
| ~Токенов CLAUDE.md | ~2,232 | ~880 | -1,352 токенов (-61%) |
| Архитектурное дерево | 315 строк в CLAUDE.md | docs/ARCHITECTURE.md | 0 в CLAUDE.md |
| Cloudflare инструкция | 46 строк | docs/CLOUDFLARE_SETUP.md | 0 в CLAUDE.md |
| Dependencies | 25 строк | docs/DEPENDENCIES.md | 0 в CLAUDE.md |

**Целевой диапазон:** 200-250 строк, ~800-1,000 токенов.

---

## Anti-Patterns адресуемые оптимизацией

- **AP-01 (Context Stuffing):** 558 → ~220 строк. Архитектурное дерево (315 строк) переносится в docs/ARCHITECTURE.md.
- **AP-04 (Cache-Hostile Order):** Статус переносится вниз; статические секции (шапка, команды) — вверх.
- **AP-09 (Code-Doc Drift):** Нотация "telegram_voice/telegram_content отключены" в строке 362 расходится с описанием архитектуры в строках 214-229 — требует верификации.
- **AP-11 (Duplicate Commands):** Команды старых ботов (telegram_voice, telegram_content) убираются из активных — они отключены согласно строке 362.
- **AP-20 (Protocol Sprawl):** Cloudflare Tunnel инструкция (46 строк) — полностью в docs/CLOUDFLARE_SETUP.md.

---

## Draft: Оптимизированный CLAUDE.md (структура ~220 строк)

```markdown
# TouristBotEcosystem
Unified monorepo — 5 ботов для туристического бизнеса в ОАЭ, общее ядро core/.

**Git:** https://github.com/Sukheil-Ganeev/TouristBotEcosystem | ветка: master
**Стек:** Python 3.13 + aiogram 3.25 + asyncpg + PostgreSQL 17 + FastAPI + Redis
**Стадия:** STABLE | **Деплой:** GCP europe-west3-b | 2026-03-03 ✅

## Quick Start
1. `docker compose up -d` — PostgreSQL 17
2. `cp .env.example .env` — заполнить токены
3. `pytest -q` — убедиться что 1263 тестов проходят
4. `python -m bots.telegram_main.main` — запустить unified бот
5. `git push` → автодеплой через GitHub Actions (~2-3 мин)

## Статус

| Batch | Статус | Краткое описание |
|-------|--------|-----------------|
| Batch 1: Core Foundation | ✅ DONE | 121 файл core/, ~47K LOC |
| Batch 2: Bot Migration | ✅ DONE | 4 бота в bots/, 65 файлов |
| Batch 3: Database Unification | ✅ DONE | 45 таблиц, 127 тестов |
| Batch 4: Integration + Deploy | ✅ DONE | GCP деплой, CI/CD, Sentry |
| Batch 5: UX & Quality | ✅ DONE | v5.6.0, 1050 тестов |
| Batch 6: Admin Bot UX | ✅ DONE | v5.9.0, i18n 4 языка, 1263 тестов |

## Статистика

| Метрика | Значение |
|---------|----------|
| .py файлов | ~248+ |
| Активных ботов | 3 (telegram_main, whatsapp, admin) |
| Тесты | 1263 (все проходят) |
| Database | PostgreSQL, 45 таблиц, 7 mixins |
| AI бэкендов | 3 (Gemini → Claude → Groq) + Redis |
| Общий LOC | ~60K+ |

## Архитектура (краткая)

```
core/          # ~141 .py — ai/, db/, formatter/, lessons/, business/, voice/, content/, analytics/, export/, integrations/, security/, i18n/, infra/
bots/          # telegram_main (13 handlers), whatsapp (FastAPI :8000), admin (7 handlers)
               # Legacy: telegram_voice, telegram_content (отключены)
config/        # settings.py — ~43 env-переменные
tests/         # 1263 тестов, 40 файлов
scripts/       # deploy.sh, setup_server.sh (idempotent), healthcheck.sh
```

Детальная архитектура: `docs/ARCHITECTURE.md`

## AI Backends

| Backend | Модель | Роль |
|---------|--------|------|
| Gemini | gemini-2.5-flash | Primary |
| Claude | claude-sonnet-4-6 | Premium creative |
| Groq | llama-3.3-70b-versatile | Fallback |

Каскад: Gemini → Claude → Groq. Redis cache: TTL 24h (temperature<0.3), 1h иначе.

## Команды

```bash
# Инфраструктура
docker compose up -d                   # PostgreSQL 17

# Запуск ботов
python -m bots.telegram_main.main      # Unified бот (port 8080)
python -m bots.whatsapp.app            # WhatsApp (FastAPI, port 8000)
python -m bots.admin.main              # Admin бот

# Тесты
pytest                                 # Все тесты (1263)
pytest -q --tb=no 2>&1 | tail -5       # Быстрая проверка

# Type check
python -m mypy core/ --ignore-missing-imports

# Деплой на GCP (пересоздать контейнеры с новым .env)
sudo docker compose --env-file .env.prod -f docker-compose.yml up -d --force-recreate
```

## Деплой (GCP)

| Параметр | Значение |
|----------|----------|
| VM | tourist-bot (e2-standard-2) |
| Зона | europe-west3-b (Франкфурт) |
| Внешний IP | 34.107.127.155 |
| WhatsApp webhook | https://tourists-wa.vipdxbrus.com/webhook |
| Cloudflare Tunnel | tourist-bot ✅ |
| Sentry | marsel-luxury-car-rental.sentry.io |
| CI/CD | GitHub Actions (deploy.yml) |

Автодеплой: `git push master` → сервер обновится через 2-3 мин.
Детали: `docs/DEPLOY.md` | Cloudflare setup: `docs/CLOUDFLARE_SETUP.md`

## Стандарты дизайна

- Форматирование текстов: `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md`
- Дизайн кнопок: `docs/BUTTON_DESIGN_GUIDE.md`
- Мастер-план улучшений: `docs/IMPROVEMENT_MASTER_PLAN.md`

## Навигация по docs/

| Файл | Когда читать |
|------|-------------|
| docs/ARCHITECTURE.md | При изменении структуры core/ или bots/ |
| docs/DEPLOY.md | При деплое или настройке сервера |
| docs/CLOUDFLARE_SETUP.md | При настройке WhatsApp webhook |
| docs/DEPENDENCIES.md | При добавлении/обновлении зависимостей |
| docs/BUTTON_DESIGN_GUIDE.md | При создании новых команд/кнопок |
| docs/IMPROVEMENT_MASTER_PLAN.md | При планировании новых фич (UX) |
| docs/MANUAL_TESTS.md | Перед релизом (17 сценариев) |
| ISSUES.md | Открытые проблемы (актуально: все закрыты) |
| CHANGELOG.md | История изменений |

## Открытые проблемы

Актуальный список: `ISSUES.md` (обновлён: 2026-03-04 19:57 Dubai)
Все issues закрыты: LOG-01, LOG-02, LOG-03, CF-01, U-01 — все ✅
```

---

## .claudeignore предложения

```gitignore
# Archive — устаревшее, не нужно в каждой сессии
docs/archive/
docs/plans/2026-03-02-merge-vtb-cf-plan.md
docs/ARCHITECTURE_v1.md
docs/CODE_REVIEW_v1.md
docs/DESIGN_DECISIONS_v1.md
docs/audit_*.md

# Тяжёлые данные
data/lessons.json
data/pending_approvals.json

# Бэкапы
*.bak
backups/
```

---

## Итог

Оптимизация CLAUDE.md с **558 строк → ~220 строк** (-61%) за счёт:
1. Вынос полного архитектурного дерева (315 строк) в `docs/ARCHITECTURE.md`
2. Вынос Cloudflare Tunnel инструкции (46 строк) в `docs/CLOUDFLARE_SETUP.md`
3. Вынос dependencies (25 строк) в `docs/DEPENDENCIES.md`
4. Сжатие Batch-статусов: 6 однострочных строк вместо 6 многострочных абзацев
5. Добавление Quick Start (5 шагов) и навигационной таблицы docs/
6. Исправление Cache-Hostile порядка (AP-04): Quick Start + статика вверху

AP-коды адресованные: **AP-01, AP-04, AP-09, AP-11, AP-20**
