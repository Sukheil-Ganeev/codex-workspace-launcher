# DOCS OPTIMIZER — ОТЧЁТ (режим: optimize)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Проект: TouristBotEcosystem
Стадия: STABLE (все 6 Batch завершены, CI/CD настроен, деплой в production)
Verification Score: 3/5

---

## МЕТРИКИ (before)

| Файл | Строк | ~Токенов | Статус | Проблемы |
|------|-------|---------|--------|----------|
| CLAUDE.md | 557 | ~2,228 | active | AP-01, AP-04, AP-10, AP-16, AP-20 |
| CHANGELOG.md | 1,088 | ~4,352 | active | растёт — норма |
| ISSUES.md | 110 | ~440 | active | ok |
| docs/ARCHITECTURE_v1.md | ~250 | ~1,000 | stale | не связан с CLAUDE.md |
| docs/BUTTON_DESIGN_GUIDE.md | ? | — | active | linked |
| docs/IMPROVEMENT_MASTER_PLAN.md | ? | — | active | linked |
| docs/audit_*.md (6 файлов) | — | — | stale/archive | READ ONLY per CLAUDE.md |
| docs/DEPLOY_GCP.md | ? | — | active | дублирует GCP секцию |
| docs/CODE_REVIEW_v1.md | ? | — | stale | archive candidate |
| docs/MANUAL_TESTS.md | ? | — | stale | archive candidate |
| docs/COMMAND_AUDIT.md / COMMAND_AUDIT_ADMIN.md | — | — | stale | archive candidate |

**СУММАРНО (только CLAUDE.md):** 1 файл, 557 строк, ~2,228 токенов

---

## АНТИ-ПАТТЕРНЫ (найдены)

| ID | Паттерн | Severity | Детали |
|----|---------|----------|--------|
| AP-01 | Context Stuffing | HIGH | 557 строк, архитектурное дерево 315 строк подряд |
| AP-04 | Cache-Hostile Order | HIGH | "Статус проекта" стоит первым — это динамика. Должно быть внизу |
| AP-09 | Code-Doc Drift | MEDIUM | `telegram_voice` и `telegram_content` "отключены" по тексту, но подробно описаны в дереве |
| AP-10 | Monolithic Status | MEDIUM | Batch 4 описание занимает 1 строку длиной 400+ символов |
| AP-11 | Duplicate Commands | MEDIUM | Команды GCP деплоя дублируются: секция "Команды" + секция "Деплой" |
| AP-16 | Cross-File Duplication | HIGH | Полная таблица GCP деплоя есть в CLAUDE.md И в docs/DEPLOY_GCP.md |
| AP-20 | Protocol Sprawl | HIGH | Секция "Cloudflare Tunnel" (47 строк) — полное руководство по настройке. Уже настроен, смысл держать здесь = ZERO |
| AP-02 | Stale Docs | MEDIUM | Описаны 2 бота (`telegram_voice`, `telegram_content`) которые "отключены" |
| AP-13 | Flat Hierarchy | LOW | docs/ не разделён на audits/, archive/, active/ |

---

## ДУБЛИРОВАНИЕ (SSOT violations)

| Факт | Найден в | Источник правды (должен быть) |
|------|----------|-------------------------------|
| GCP деплой параметры (VM, IP, Docker и т.д.) | CLAUDE.md + docs/DEPLOY_GCP.md | docs/DEPLOY_GCP.md (или docs/DEPLOY.md) |
| Cloudflare Tunnel setup (47 строк) | CLAUDE.md | docs/DEPLOY_GCP.md — туннель уже настроен, инструкция не нужна в CLAUDE.md |
| Зависимости requirements.txt | CLAUDE.md (28 строк копия) + requirements.txt | requirements.txt — SSOT. В CLAUDE.md только ссылка |
| Статистика проекта (LOC, файлов и т.д.) | CLAUDE.md "Статистика" + "Архитектура" | CLAUDE.md "Статистика" — убрать дублирующие числа из дерева |
| AI backends таблица | CLAUDE.md + core/ai/models.py | core/ai/models.py — в CLAUDE.md достаточно 1 строки |
| Пути к FORMATTING_GUIDE | CLAUDE.md "Стандарты" + глобальный CLAUDE.md | Один источник |

---

## ЧТО УБИРАТЬ / КУДА ПЕРЕНОСИТЬ

### Секции для полного удаления из CLAUDE.md (→ ссылки)

| Секция | Строк | Действие |
|--------|-------|----------|
| Архитектурное дерево (полное) | ~315 | → ссылка на `docs/ARCHITECTURE_v1.md` (уже существует!). Оставить только сводную таблицу подсистем ~15 строк |
| Cloudflare Tunnel setup (47 строк) | 47 | → полностью удалить (туннель уже настроен). Статус — одна строка |
| Зависимости requirements.txt (копия) | 30 | → удалить, оставить: "22 зависимости, см. requirements.txt" |
| GCP детальная таблица (13 строк) | 13 | → сократить до 4 строк (VM, IP, деплой URL, статус) |
| Скрипты деплоя буллиты | 5 | → оставить только bash-команду автодеплоя |
| Batch описания (длинные) | ~10 символов в каждой | → сократить Batch 4 и 5 до 1-2 слов статуса |

### Секции для переноса в docs/

| Секция | Куда |
|--------|------|
| Cloudflare Tunnel full setup | docs/DEPLOY_GCP.md (если нужна как reference) |
| Детальные описания подсистем | docs/ARCHITECTURE_v1.md (уже там) |

---

## ПРЕДЛОЖЕННАЯ СТРУКТУРА (cache-optimized ordering)

```
# TouristBotEcosystem                  ← СТАТИЧЕСКОЕ
Стек, Git, Деплой URL — одна строка каждое

## Quick Start                          ← СТАТИЧЕСКОЕ
5 шагов для начала работы в новой сессии

## Ключевые команды                     ← СТАТИЧЕСКОЕ
Только команды, которые нужны каждый день (8-10 строк)

## Архитектура (обзор)                  ← ПОЛУ-СТАТИЧЕСКОЕ
Таблица подсистем: имя | файлов | описание (~14 строк)
→ Детально: docs/ARCHITECTURE_v1.md

## Боты                                 ← ПОЛУ-СТАТИЧЕСКОЕ
Таблица: бот | порт | статус (~5 строк)

## Стандарты разработки                 ← ПОЛУ-СТАТИЧЕСКОЕ
Ссылки (не содержимое): formatting, buttons, i18n

## Навигация по документации            ← ПОЛУ-СТАТИЧЕСКОЕ
Таблица: файл | когда читать (~10 строк)

## Деплой                               ← ПОЛУ-СТАТИЧЕСКОЕ
4 строки: VM/IP/URL/команда git push

## Статус проекта                       ← ДИНАМИЧЕСКОЕ
Таблица Batch: только статус, без длинных описаний

## Статистика                           ← ДИНАМИЧЕСКОЕ
Таблица метрик (уже есть, оставить)

## Открытые проблемы                    ← ДИНАМИЧЕСКОЕ
→ ISSUES.md (ссылка)
```

---

## DRAFT: НОВЫЙ CLAUDE.md (~230 строк)

```markdown
# TouristBotEcosystem

Unified monorepo — 3 активных бота для туристического бизнеса в ОАЭ.

**Git:** https://github.com/Sukheil-Ganeev/TouristBotEcosystem | ветка: master
**Стек:** Python 3.13 + aiogram 3.25 + asyncpg + Gemini/Claude/Groq AI
**Production:** GCP europe-west3-b (34.107.127.155) | WhatsApp: tourists-wa.vipdxbrus.com
**Деплой:** `git push` → GitHub Actions → сервер обновится за 2-3 мин

---

## Quick Start

1. Прочитать этот файл (статус, архитектура, команды)
2. Проверить `ISSUES.md` — открытые проблемы (сейчас: все закрыты ✅)
3. Запустить: `docker compose up -d` → `python -m bots.telegram_main.main`
4. Перед новым handler — читать стандарты (раздел ниже)
5. После изменений — обновить CHANGELOG.md + этот файл

---

## Статус проекта

| Batch | Статус | Версия |
|-------|--------|--------|
| Batch 1: Core Foundation | ✅ DONE | 121 файл, ~47K LOC |
| Batch 2: Bot Migration | ✅ DONE | 65 файлов, 35K LOC |
| Batch 3: Database Unification | ✅ DONE | 45 таблиц, 127 тестов |
| Batch 4: Integration + Deploy | ✅ DONE | GCP деплой 2026-03-03 |
| Batch 5: UX & Quality | ✅ DONE | v5.6.0, 1050 тестов |
| Batch 6: Admin Bot UX | ✅ DONE | v5.9.0, 1263 тестов |

**Текущая ветка:** feat/admin-inline-action-callbacks

---

## Архитектура (обзор)

| Подсистема | Файлов | Описание |
|-----------|--------|----------|
| core/ai/ | 6 | Gemini → Claude → Groq каскад, TaskType routing, Redis cache |
| core/db/ | 10+SQL | PostgreSQL, 45 таблиц, 7 mixins, ~165 методов |
| core/formatter/ | 9 | Форматирование: транскрипции, статистика, туры, admin |
| core/lessons/ | 12 | AI самообучение, 27 типов ошибок |
| core/business/ | 17 | Калькулятор, CRM, маршруты, расходы |
| core/voice/ | 12 | STT pipeline, Whisper/Groq, суммаризация |
| core/content/ | 32 | 5 платформ, multiformat, AI planner |
| core/analytics/ | 13 | Метрики, RSS, конкуренты, сезонность |
| core/export/ | 6 | PDF, XLSX, MD |
| core/integrations/ | 7 | Bitrix24, Notion, Google, R2 |
| core/security/ | 2 | DB integrity, log sanitizer |
| core/i18n/ | 3 | RU/EN/AR/ZH, 100+ ключей |
| core/infra/ | 10 | Health, scheduler, Sentry, logging |

→ Детальное дерево: `docs/ARCHITECTURE_v1.md`

---

## Боты

| Бот | Модуль | Порт | Статус |
|-----|--------|------|--------|
| telegram_main | bots/telegram_main/ | 8080 | ✅ активен (13 роутеров) |
| whatsapp | bots/whatsapp/ | 8000 | ✅ активен (FastAPI + Cloudflare Tunnel) |
| admin | bots/admin/ | webhook | ✅ активен (12 команд) |
| telegram_voice | bots/telegram_voice/ | 8081 | ⏸ отключён |
| telegram_content | bots/telegram_content/ | — | ⏸ отключён |

---

## Стандарты разработки

**ОБЯЗАТЕЛЬНО читать перед работой:**
- Форматирование текстов: `D:/Downloads/VoiceTranscriptionBot/docs/FORMATTING_GUIDE.md`
- Дизайн кнопок: `docs/BUTTON_DESIGN_GUIDE.md`
- i18n: все тексты через `t(key, lang)` из `core/i18n/`

**Мастер-план улучшений:** `docs/IMPROVEMENT_MASTER_PLAN.md` (12 сессий)

**Источники (READ-ONLY):**
- `D:/Downloads/VoiceTranscriptionBot/` — голосовой бот + WhatsApp + Admin
- `D:/Downloads/ContentFactory/` — контент-фабрика

---

## Навигация по документации

| Файл | Когда читать |
|------|-------------|
| `ISSUES.md` | Начало каждой сессии — открытые проблемы |
| `CHANGELOG.md` | История изменений |
| `docs/ARCHITECTURE_v1.md` | Детальное дерево файлов |
| `docs/BUTTON_DESIGN_GUIDE.md` | Создание кнопок |
| `docs/IMPROVEMENT_MASTER_PLAN.md` | Планирование UX работ |
| `docs/DEPLOY_GCP.md` | Деплой, Cloudflare Tunnel, server ops |
| `docs/MANUAL_TESTS.md` | 17 ручных сценариев |
| `docs/audit_*.md` | READ ONLY — Phase 0 аудиты |

---

## Ключевые команды

```bash
# Инфраструктура
docker compose up -d                   # PostgreSQL 17 (port 5432)
docker compose ps                      # Статус

# Запуск ботов
python -m bots.telegram_main.main      # Unified (port 8080)
python -m bots.whatsapp.app            # WhatsApp (port 8000)
python -m bots.admin.main              # Admin

# Тесты
pytest -q --tb=no 2>&1 | tail -5       # Быстрая проверка (1263 тестов)
pytest tests/core/ -v                  # Core DB тесты

# Деплой (GCP)
git push                               # Автодеплой через GitHub Actions
# Статус: https://github.com/Sukheil-Ganeev/TouristBotEcosystem/actions

# Если нужно пересоздать контейнеры (env vars изменились):
sudo docker compose --env-file .env.prod -f docker-compose.yml up -d --force-recreate
```

---

## Деплой (GCP)

| Параметр | Значение |
|----------|----------|
| VM | tourist-bot, europe-west3-b, e2-standard-2 |
| IP | 34.107.127.155 |
| WhatsApp webhook | https://tourists-wa.vipdxbrus.com/webhook |
| Cloudflare Tunnel | tourist-bot (UUID: c4645c9f-...) — ✅ настроен |
| CI/CD | GitHub Actions, secrets настроены |

→ Детали настройки сервера, Cloudflare Tunnel setup: `docs/DEPLOY_GCP.md`

---

## Статистика

| Метрика | Значение |
|---------|----------|
| Файлов .py | ~248+ |
| core/ подсистем | 14 |
| Активных ботов | 3 |
| Тесты | 1263 (все проходят) |
| Database | PostgreSQL, 45 таблиц, ~165 методов |
| AI бэкендов | 3 (Gemini → Claude → Groq) |
| i18n ключей | 100+ × 4 языка |
| Зависимости | 22, см. requirements.txt |
| Общий LOC | ~60K+ |

---

## AI Backends

| Backend | Модель | Роль |
|---------|--------|------|
| Gemini | gemini-2.5-flash | Primary |
| Claude | claude-sonnet-4-6 | Premium creative |
| Groq | llama-3.3-70b-versatile | Fallback |

Каскад: Gemini → Claude → Groq. Redis cache: TTL 24h (temp<0.3), TTL 1h иначе.

---

## Открытые проблемы

→ `ISSUES.md` (обновлён: 2026-03-04 19:57 Dubai) — все issues закрыты ✅

---

## Бизнес-контекст

Сухейль: экскурсии/парки ОАЭ. Марсель: аренда авто/трансферы. Муфамад: яхты.
Офис: Дубай Tecom. Клиенты: СНГ. Языки: RU/EN/AR.
```

---

## SSOT ТАБЛИЦА (где живёт каждый факт)

| Факт | Источник правды | НЕ дублировать в |
|------|-----------------|------------------|
| Дерево файлов проекта | docs/ARCHITECTURE_v1.md | CLAUDE.md (только таблица подсистем) |
| GCP деплой параметры (полные) | docs/DEPLOY_GCP.md | CLAUDE.md (только 4 строки) |
| Cloudflare Tunnel setup | docs/DEPLOY_GCP.md | CLAUDE.md (только статус: настроен ✅) |
| Зависимости | requirements.txt | CLAUDE.md (только число: 22) |
| AI модели детально | core/ai/models.py | CLAUDE.md (только 3-строчная таблица) |
| История изменений | CHANGELOG.md | CLAUDE.md (не пересказывать) |
| Открытые проблемы | ISSUES.md | CLAUDE.md (только ссылка) |
| Стандарты форматирования | FORMATTING_GUIDE.md (VTB) | CLAUDE.md (только ссылка) |
| Дизайн кнопок | docs/BUTTON_DESIGN_GUIDE.md | CLAUDE.md (только ссылка) |
| Batch прогресс (детали) | CHANGELOG.md | CLAUDE.md (только статус + версия) |
| Manual test сценарии | docs/MANUAL_TESTS.md | CLAUDE.md (только ссылка) |

---

## .claudeignore (предложение)

```
# Archive — не грузить автоматически
docs/audit_*.md
docs/AUDIT_2026-03-03.md
docs/CODE_REVIEW_v1.md
docs/COMMAND_AUDIT.md
docs/COMMAND_AUDIT_ADMIN.md
docs/DATABASE_COVERAGE_AUDIT.md
docs/DEPLOY_LESSONS_2026-03-03.md
docs/SERVER_HEALTH_REPORT_2026-03-04.md
docs/PROJECT_ACCOMPLISHMENTS.md
docs/plans/
.claude/worktrees/
*.bak
```

---

## BEFORE / AFTER МЕТРИКИ

| Метрика | До | После | Изменение |
|---------|-----|-------|-----------|
| CLAUDE.md строк | 557 | ~230 | -59% |
| CLAUDE.md ~токенов | ~2,228 | ~920 | -59% |
| Анти-паттернов | 9 | 1-2 | -78% |
| SSOT violations | 6 | 0 | -100% |
| Дублирующих секций | 3 (GCP дважды, Cloudflare туториал, deps) | 0 | -100% |
| Dormant контент (отключённые боты) | 120+ строк описания | ~2 строки в таблице | -95% |

**Projection:** автозагрузка CLAUDE.md при старте сессии сократится с ~2,228 токенов до ~920 токенов.
Это высвобождает ~1,300 токенов контекста за каждую сессию.

---

## РЕКОМЕНДАЦИИ (по приоритету)

### HIGH
1. Заменить полное дерево файлов (315 строк) на таблицу подсистем (13 строк) + ссылку на ARCHITECTURE_v1.md
2. Удалить секцию Cloudflare Tunnel (47 строк) — туннель уже настроен, инструкция не нужна в CLAUDE.md. Оставить: "настроен ✅ → `docs/DEPLOY_GCP.md`"
3. Удалить копию requirements.txt (30 строк) → "22 зависимости, см. `requirements.txt`"
4. Переставить секции: "Статус проекта" вниз (динамическое), "Команды" и "Архитектура" вверх (статическое)

### MEDIUM
5. Сократить Batch 4/5 описания с ~400 символов до 2-3 слов + версию
6. Объединить GCP деплой информацию: оставить 4 строки в CLAUDE.md, всё остальное → docs/DEPLOY_GCP.md
7. Добавить Quick Start секцию (5 шагов) — сейчас отсутствует
8. Отметить отключённые боты как ⏸ (не описывать подробно)

### LOW
9. Создать .claudeignore для audit_*.md и archive файлов
10. Добавить секцию "Навигация по документации" с таблицей "файл → когда читать"

---

## ВАЖНО: что НЕ трогать

- CHANGELOG.md — журнал, растёт, не сжимать
- ISSUES.md — трекер, оставить как есть
- docs/ARCHITECTURE_v1.md — ценный документ, увеличивается в важности при сжатии CLAUDE.md
- docs/BUTTON_DESIGN_GUIDE.md, docs/IMPROVEMENT_MASTER_PLAN.md — активно используются
- Dormant-описания отключённых ботов: НЕ удалять код/файлы, только убрать детальное описание из CLAUDE.md (оставить строку в таблице)
