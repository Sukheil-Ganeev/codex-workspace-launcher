# Аудит документации — TouristBotEcosystem

**Дата аудита:** 2026-03-12
**Версия проекта (по CLAUDE.md):** v5.9.0
**Версия проекта (по ISSUES.md):** v5.8.0
**Ветка:** feat/admin-inline-action-callbacks

---

## Резюме

| Категория | Найдено |
|-----------|---------|
| Файлов .md в репозитории (без worktrees) | ~39 |
| Битых ссылок (файл не существует) | 2 |
| Устаревших данных (метрики, инфраструктура) | 8+ несоответствий |
| Дублирующихся документов | 6 пар/групп |
| Документов со статусом ACTIVE, но фактически закрытых | 1 |
| Опасных утечек (IP/SSH в MD) | 2 |

---

## 1. Битые ссылки (файл не существует)

### BL-01 — docs/DESIGN_DECISIONS_v1.md отсутствует

**Найдено в:**
- `README.md` строка 338: `| [docs/DESIGN_DECISIONS_v1.md](docs/DESIGN_DECISIONS_v1.md) | Architectural decisions |`
- `docs/ARCHITECTURE_v1.md` строка 37: `Источник: docs/DESIGN_DECISIONS_v1.md`
- `docs/ARCHITECTURE_v1.md` строка 841: `*Источники: DESIGN_DECISIONS_v1.md, ...`
- `MASTER_PLAN.md` строки 468, 559, 1690 — ссылки на создание и готовность файла

**Статус:** Файл значится как выполненный (`DONE` в MASTER_PLAN.md строка 1690), упомянут как источник в ARCHITECTURE_v1.md, но физически отсутствует в `docs/`.

**Серьёзность:** Средняя. README ссылается на несуществующий файл.

---

### BL-02 — ARCHITECTURE.md и ARCHITECTURE_v1.md в корне репо не существуют

`docs/ARCHITECTURE_v1.md` строка 841 ссылается на `DESIGN_DECISIONS_v1.md` как источник — это уже задокументировано выше. Отдельно: в `CLAUDE.md` (в дереве архитектуры) упомянуты `docs/DESIGN_DECISIONS_v1.md` косвенно через `docs/audit_*.md` — эти файлы существуют.

Файлы `ARCHITECTURE.md` и `ARCHITECTURE_v1.md` в **корне** репозитория (не в `docs/`) — **не существуют**. Они находятся только в `docs/ARCHITECTURE.md` и `docs/ARCHITECTURE_v1.md`. При этом `MASTER_PLAN.md` ссылается на `docs/ARCHITECTURE_v1.md` — это правильно.

---

## 2. Устаревший контент

### OC-01 — Количество тестов расходится в 4 документах

| Документ | Указанное число тестов |
|----------|----------------------|
| `CLAUDE.md` (актуальный) | 1263 |
| `README.md` (badge + таблица) | 1,042+ |
| `docs/ARCHITECTURE.md` | 970+ |
| `docs/IMPROVEMENT_MASTER_PLAN.md` строка 767 | 970+ |
| `docs/PROJECT_ACCOMPLISHMENTS.md` строка 348 | 970 → 1049+ |
| `ISSUES.md` (строка P9-11) | 970 |

**Вывод:** README.md и docs/ARCHITECTURE.md не обновились до 1263. README badge показывает `1042+`, CLAUDE.md (последний обновлённый) — 1263.

---

### OC-02 — Количество таблиц БД: 45 vs 47

| Документ | Указанное число |
|----------|----------------|
| `docs/ARCHITECTURE_v1.md` строки 21, 67 | 45 таблиц, 6 mixins |
| `docs/ARCHITECTURE.md` строки 57, 156 | 45 таблиц, 7 mixins |
| `docs/audit_ecosystem.md` строка 120 | 6 mixins |
| `README.md` строки 44, 132, 318 | 47 tables, 7 mixins |
| `CLAUDE.md` строка 365 | 45 таблиц, 7 mixins |
| `docs/DATABASE_COVERAGE_AUDIT.md` | 47 таблиц |

**Вывод:** Правильное число — 47 (включая 2 таблицы Business: `calc_history`, `saved_routes`, добавленных в Batch 4). CLAUDE.md называет 45 таблиц при 7 mixins — внутреннее противоречие.

---

### OC-03 — Количество подсистем core/: 13 vs 14

| Документ | Указанное число |
|----------|----------------|
| `docs/ARCHITECTURE.md` строка 30 | 13 подсистем |
| `docs/ARCHITECTURE_v1.md` строки 29, 101, 754 | 13 подсистем |
| `docs/PROJECT_ACCOMPLISHMENTS.md` строка 97 | 13 подсистем |
| `README.md` строка 316 | 14 subsystems |
| `CLAUDE.md` строка 361 | 14 (добавлен i18n) |

**Вывод:** Правильное число — 14 (добавлен `core/i18n/` в Batch 6, v5.8.0). `docs/ARCHITECTURE.md` и `docs/ARCHITECTURE_v1.md` не обновлены.

---

### OC-04 — Инфраструктура: Oracle Cloud vs GCP

**Устаревшие документы, описывающие Oracle Cloud как целевую платформу:**
- `docs/DEPLOY.md` (798 строк) — полное руководство по Oracle Cloud ARM Ubuntu, порт 8081 для 5 ботов
- `docs/ARCHITECTURE_v1.md` строки 21-30, 83 — Oracle Cloud ARM Ubuntu
- `docs/ARCHITECTURE.md` строки 388, 790 — Oracle Cloud ARM (Ubuntu)
- `deploy/README.md` строка 20 — "On Oracle Cloud Ubuntu 22.04:"
- `MASTER_PLAN.md` строки 1598, 1613, 1626, 1671 — Oracle Cloud как цель деплоя

**Актуальная информация (CLAUDE.md, CHANGELOG.md):** Деплой на **GCP europe-west3-b Frankfurt**, VM `tourist-bot`, IP `34.107.127.155`, первый деплой 2026-03-03.

**Итого:** `docs/DEPLOY.md` целиком описывает Oracle Cloud. `docs/DEPLOY_GCP.md` — актуальное руководство, явно ссылается на Oracle Cloud как на **альтернативу**.

---

### OC-05 — Количество активных ботов: 3 vs 5

**Устаревшие документы, упоминающие 5 ботов:**
- `docs/DEPLOY.md` строка 9: "Running 5 bots"
- `docs/DEPLOY.md` таблица: `telegram_voice`, `telegram_content`, `whatsapp`, `admin`, `telegram_main`
- `docs/ARCHITECTURE.md` строки 30, 29: "5 ботов"
- `docs/ARCHITECTURE_v1.md` строки 28-29: "5 ботов"

**Актуально (CLAUDE.md строка 362):** "Ботов: 3 (telegram_main, whatsapp, admin) — telegram_voice и telegram_content отключены"

**CHANGELOG.md строка 260:** "Reduced to 3 bots: telegram_main, admin, whatsapp (removed telegram_voice, telegram_content)"

---

### OC-06 — `docs/IMPROVEMENT_MASTER_PLAN.md` — статус ACTIVE при закрытом плане

Файл `docs/IMPROVEMENT_MASTER_PLAN.md` имеет заголовок `**Status:** ACTIVE` (строка 6).

Однако `docs/IMPROVEMENT_MASTER_PLAN_v2.md` строка 3 явно говорит: "следует за v1.0 **который закрыт в v5.7.0**".

При этом CLAUDE.md строка 26 ссылается именно на v1 как актуальный мастер-план улучшений: `docs/IMPROVEMENT_MASTER_PLAN.md (12 сессий — UX, тексты, кнопки, Admin/WA архитектура, DB аудит)` — не v2.

**Вывод:** v1 закрыт, v2 является актуальным, но CLAUDE.md ссылается на v1.

---

### OC-07 — docs/ADMIN_BOT_REDESIGN.md — устаревший план

Статус документа: "Ожидает одобрения → Сессия 5 (реализация)". Фактически Admin Bot полностью переделан (Batch 6, CLAUDE.md). Документ продолжает существовать как незакрытый план.

---

### OC-08 — docs/AUDIT_2026-03-03.md — не помечен как устаревший

По правилам проекта (ISSUES.md раздел "Протокол аудит-файлов") каждый аудит должен иметь статус `АКТУАЛЕН / ЧАСТИЧНО УСТАРЕЛ / УСТАРЕЛ`. Файл `docs/AUDIT_2026-03-03.md` строка 5 содержит `**Статус:** АКТУАЛЕН` — создан 2026-03-03, сейчас 2026-03-12, прошло 9 дней. По правилу 5 он должен быть помечен как `УСТАРЕЛ` (>7 дней).

---

## 3. Дублирующийся контент

### DUP-01 — Две архитектурные документации

| Файл | Строк | Версия/Статус |
|------|-------|---------------|
| `docs/ARCHITECTURE.md` | 424 | v4.0, обновлено 2026-03-03, Phase 0 + Batch 1-4 |
| `docs/ARCHITECTURE_v1.md` | 841 | v1, AS-IS после Batch 1-4 + Phase 0 |

Оба описывают одно и то же состояние (Phase 0 + Batch 1-4). `ARCHITECTURE.md` — сокращённая версия, `ARCHITECTURE_v1.md` — подробная. Ни один не отражает текущее состояние (Batch 5, 6 с i18n, expenses, report, inline callbacks).

---

### DUP-02 — Два плана деплоя

| Файл | Строк | Описывает |
|------|-------|-----------|
| `docs/DEPLOY.md` | 798 | Oracle Cloud ARM Ubuntu (устаревший) |
| `docs/DEPLOY_GCP.md` | 1062 | GCP (актуальный) |

Наличие обоих создаёт путаницу: какой использовать? `deploy/README.md` ссылается на Oracle. `CLAUDE.md` ссылается на GCP (актуальный деплой).

---

### DUP-03 — Два плана улучшений

| Файл | Строк | Статус |
|------|-------|--------|
| `docs/IMPROVEMENT_MASTER_PLAN.md` | 879 | v1.0, закрыт в v5.7.0, но помечен ACTIVE |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | 255 | v2.0, актуальный |

---

### DUP-04 — MASTER_PLAN.md vs docs/IDEAL_MASTER_PLAN.md

| Файл | Строк | Описание |
|------|-------|----------|
| `MASTER_PLAN.md` (корень) | 1900 | Рабочий план проекта, прогресс фич |
| `docs/IDEAL_MASTER_PLAN.md` | 2559 | Методология (READ ONLY) |

Содержательно разные назначения, но оба — огромные документы о "мастер-плане". Нет четкого указания в CLAUDE.md что один — оперативный, другой — методологический.

---

### DUP-05 — Метрики проекта в 4 местах

Одни и те же числа (файлов .py, LOC, тестов, таблиц) дублируются в:
1. `CLAUDE.md` — самое актуальное
2. `README.md` — устаревшее (1042 тестов, 5 ботов)
3. `docs/ARCHITECTURE.md` — устаревшее (970+ тестов, 13 подсистем, 5 ботов)
4. `docs/ARCHITECTURE_v1.md` — устаревшее (45 таблиц, 6 mixins, 5 ботов)
5. `docs/PROJECT_ACCOMPLISHMENTS.md` — зафиксировано на v5.6.0

---

### DUP-06 — Дизайн-редизайны без статуса "выполнено"

| Файл | Описание | Реальный статус |
|------|----------|-----------------|
| `docs/ADMIN_BOT_REDESIGN.md` | Plan для Admin Bot | Реализован в Batch 6 |
| `docs/WHATSAPP_BOT_REDESIGN.md` | "АРХИТЕКТУРНЫЙ ДОКУМЕНТ — не реализован" | Частично реализован в Batch 5 |

Оба не обновлены — не закрыты явно.

---

## 4. Опасные данные в документации

### SEC-01 — Публичный IP адреса в документации

**Файлы:**
- `docs/SERVER_RUNBOOK.md` строка 20: `ssh -i ~/.ssh/google_compute_engine londo@34.107.127.155`
- `docs/CICD_SETUP.md`: тот же адрес
- `README.md` строки 251, 245: `34.107.127.155`
- `CLAUDE.md` строки 476-477: IP и деплой пользователь

IP-адрес сервера `34.107.127.155` упомянут в публичных MD файлах. Если репозиторий приватный — приемлемо, но стоит документально подтвердить что репо private.

**GitHub:** `Sukheil-Ganeev/TouristBotEcosystem` (private — указано в CLAUDE.md).

---

## 5. ISSUES.md — оценка актуальности

**Файл:** `D:/Downloads/TouristBotEcosystem/ISSUES.md`
**Последнее обновление:** 2026-03-04 19:57 (Dubai)
**Статус файла:** АКТУАЛЕН (самооценка)

### Открытые issues:

| ID | Проблема | Оценка актуальности |
|----|----------|---------------------|
| DB-01 | 20 CF-таблиц dormant (telegram_content отключён) | Актуален — бот не возвращён |
| SEN-01..05 | Sentry: 5 открытых issues | Неизвестно — 8 дней прошло с создания |

**Замечание по SEN-01..05:** Issues созданы 2026-03-04, сейчас 2026-03-12. Статус "🔴 ОТКРЫТ" — неизвестно были ли они изучены. Правило 5 протокола аудит-файлов (>7 дней) технически применимо и здесь.

---

## 6. Документы, отсутствующие в CLAUDE.md (документация без регистрации)

Следующие файлы существуют в `docs/`, но не упомянуты в дереве архитектуры CLAUDE.md:

| Файл | Строк | Содержание |
|------|-------|------------|
| `docs/ADMIN_BOT_REDESIGN.md` | 278 | Дизайн Admin Bot |
| `docs/COMMAND_AUDIT_ADMIN.md` | 262 | Аудит команд Admin бота |
| `docs/CICD_SETUP.md` | 105 | GitHub Actions настройка |
| `docs/DEPLOY.md` | 798 | Oracle Cloud деплой |
| `docs/DEPLOY_GCP.md` | 1062 | GCP деплой |
| `docs/DEPLOY_LESSONS_2026-03-03.md` | 166 | Уроки первого деплоя |
| `docs/IMPROVEMENT_MASTER_PLAN_v2.md` | 255 | Текущий план улучшений |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | 628 | История проекта |
| `docs/SENTRY_GUIDE.md` | 187 | Sentry руководство |
| `docs/SERVER_HEALTH_REPORT_2026-03-04.md` | 142 | Одноразовый health отчёт |
| `docs/SERVER_RUNBOOK.md` | 361 | Runbook по серверу |
| `docs/USER_GUIDE_admin.md` | 390 | Руководство для Admin |
| `docs/USER_GUIDE_owner.md` | 476 | Руководство для Owner |
| `docs/USER_GUIDE_staff.md` | 145 | Руководство для Staff |
| `docs/WHATSAPP_BOT_REDESIGN.md` | 522 | WhatsApp редизайн |

---

## 7. Сводная таблица проблем

| ID | Тип | Серьёзность | Проблема | Действие |
|----|-----|-------------|----------|----------|
| BL-01 | Битая ссылка | Средняя | `docs/DESIGN_DECISIONS_v1.md` отсутствует, на него ссылаются README и ARCHITECTURE_v1 | Создать файл или убрать ссылки |
| OC-01 | Устарело | Средняя | Тесты: README показывает 1042+, актуально 1263 | Обновить README badge и таблицу |
| OC-02 | Устарело | Средняя | Таблицы БД: CLAUDE.md=45, актуально=47, docs/ARCHITECTURE=45 | Стандартизировать на 47 |
| OC-03 | Устарело | Низкая | Подсистемы: docs/ARCHITECTURE=13, актуально=14 | Обновить docs/ARCHITECTURE |
| OC-04 | Устарело | Высокая | docs/DEPLOY.md описывает Oracle Cloud — деплой давно на GCP | Добавить заголовок "УСТАРЕЛО" или переписать |
| OC-05 | Устарело | Высокая | docs/ARCHITECTURE, DEPLOY описывают 5 ботов — активных 3 | Обновить или добавить примечание |
| OC-06 | Неверный статус | Низкая | docs/IMPROVEMENT_MASTER_PLAN.md помечен ACTIVE, хотя закрыт в v5.7.0 | Изменить статус на CLOSED/АРХИВ |
| OC-07 | Устарело | Низкая | docs/ADMIN_BOT_REDESIGN.md — нереализованный план, но Admin Bot уже переделан | Обновить статус |
| OC-08 | Устарело | Низкая | docs/AUDIT_2026-03-03.md помечен АКТУАЛЕН, но >7 дней | Изменить на УСТАРЕЛ |
| DUP-01 | Дубль | Низкая | ARCHITECTURE.md и ARCHITECTURE_v1.md описывают одно состояние | Консолидировать или разграничить |
| DUP-02 | Дубль | Средняя | DEPLOY.md (Oracle) и DEPLOY_GCP.md — неясно какой основной | Пометить Oracle как архив |
| DUP-03 | Дубль | Низкая | IMPROVEMENT_MASTER_PLAN v1 и v2 оба существуют | v1 → пометить АРХИВ |
| DUP-04 | Дубль | Низкая | MASTER_PLAN.md и IDEAL_MASTER_PLAN.md — разные цели, но запутывают | Добавить пояснение в CLAUDE.md |
| DUP-05 | Дубль | Средняя | Метрики в 4 документах не синхронизированы | README и docs/ARCHITECTURE обновить |
| DUP-06 | Дубль | Низкая | Редизайн-документы не закрыты явно | Добавить статус РЕАЛИЗОВАН/АРХИВ |
| SEC-01 | Данные | Инфо | IP сервера в публичных MD файлах | Приемлемо если репо приватный (✅) |

---

## 8. Рекомендации по приоритету

### Срочно (блокируют новых разработчиков):

1. **OC-04 + OC-05** — Добавить в начало `docs/DEPLOY.md` блок:
   ```
   > ⚠️ УСТАРЕЛО: Этот документ описывает Oracle Cloud.
   > Актуальный деплой: GCP. Руководство: docs/DEPLOY_GCP.md
   ```

2. **OC-01** — Обновить `README.md` badge с 1042 → 1263 тестов

3. **BL-01** — Убрать ссылку на `docs/DESIGN_DECISIONS_v1.md` из `README.md` или создать файл

### В следующей сессии:

4. **OC-02** — Стандартизировать "47 таблиц" во всех docs/

5. **OC-06** — Изменить статус `IMPROVEMENT_MASTER_PLAN.md` на CLOSED; обновить ссылку в `CLAUDE.md` на v2

6. **DUP-02** — Пометить `docs/DEPLOY.md` как архив Oracle Cloud

### Когда будет время:

7. **OC-03** — Обновить "14 подсистем" в `docs/ARCHITECTURE.md` и `ARCHITECTURE_v1.md`

8. **DUP-01** — Решить судьбу двух архитектурных документов (слить в один актуальный)

9. **OC-07, OC-08** — Закрыть устаревшие планы и аудиты

---

*Аудит проведён: 2026-03-12*
*Охват: все .md файлы в корне и docs/ репозитория (без .claude/worktrees/ и .pytest_cache/)*
