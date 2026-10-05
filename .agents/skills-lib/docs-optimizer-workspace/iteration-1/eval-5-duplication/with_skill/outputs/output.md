# DOCS OPTIMIZER — SSOT DUPLICATION ANALYSIS
## TouristBotEcosystem

**Режим:** `audit` (SSOT / Cross-file duplication)
**Дата:** 2026-03-12
**Verification Score:** 2/5

---

## МЕТРИКИ ФАЙЛОВ

| Файл | Строк | ~Токенов | Тип |
|------|-------|---------|-----|
| CLAUDE.md | 557 | ~2,228 | CRITICAL (> 400 строк) |
| CHANGELOG.md | 1,088 | ~4,352 | active / журнал |
| MASTER_PLAN.md | 1,900 | ~7,600 | СТALE (исходный план) |
| ISSUES.md | 110 | ~440 | active |
| README.md | 351 | ~1,404 | active |
| docs/ARCHITECTURE.md | 424 | ~1,696 | active |
| docs/ARCHITECTURE_v1.md | 841 | ~3,364 | ДУБЛЬ → superseded |
| docs/IDEAL_MASTER_PLAN.md | 2,559 | ~10,236 | READ-ONLY |
| docs/IMPROVEMENT_MASTER_PLAN.md | 879 | ~3,516 | STALE (Batch 5) |
| docs/IMPROVEMENT_MASTER_PLAN_v2.md | 255 | ~1,020 | active |
| docs/DEPLOY.md | 798 | ~3,192 | ДУБЛЬ Oracle Cloud |
| docs/DEPLOY_GCP.md | 1,062 | ~4,248 | active |
| docs/PROJECT_ACCOMPLISHMENTS.md | 628 | ~2,512 | ДУБЛЬ CHANGELOG |
| docs/SERVER_RUNBOOK.md | 361 | ~1,444 | active |
| docs/UX_DESIGN_v1.md | 1,103 | ~4,412 | active |
| docs/BUTTON_DESIGN_GUIDE.md | 1,039 | ~4,156 | active |
| docs/audit_*.md (6 файлов) | ~948 | ~3,792 | STALE (Phase 0 аудиты) |
| docs/AUDIT_2026-03-03.md | 332 | ~1,328 | STALE |
| docs/USER_GUIDE_*.md (3 файла) | ~1,011 | ~4,044 | active |
| docs/CICD_SETUP.md | 105 | ~420 | active |
| docs/SENTRY_GUIDE.md | 187 | ~748 | active |
| docs/SERVER_HEALTH_REPORT_2026-03-04.md | 142 | ~568 | СТALE (snapshot) |
| docs/DEPLOY_LESSONS_2026-03-03.md | 166 | ~664 | archive |
| docs/COMMAND_AUDIT.md | 218 | ~872 | STALE |
| docs/COMMAND_AUDIT_ADMIN.md | 262 | ~1,048 | STALE |
| docs/DATABASE_COVERAGE_AUDIT.md | 337 | ~1,348 | STALE |
| docs/CODE_REVIEW_v1.md | 385 | ~1,540 | active |
| docs/MANUAL_TESTS.md | 321 | ~1,284 | active |
| docs/WHATSAPP_BOT_REDESIGN.md | 522 | ~2,088 | active |
| docs/ADMIN_BOT_REDESIGN.md | 278 | ~1,112 | active |
| deploy/README.md | (small) | ~200 | active |

**СУММАРНО:** ~40 MD файлов, **21,199 строк**, **~85,000 токенов**

> Порог WARNING: > 15K строк суммарно. Статус: **CRITICAL** (85K токенов)

---

## КАРТА ДУБЛИРОВАНИЯ

### DUP-01 — Деплой-параметры GCP (HIGH)

**Факт:** IP `34.107.127.155`, зона `europe-west3-b`, тип `e2-standard-2`

| Файл | Строки | Контекст |
|------|--------|---------|
| `CLAUDE.md` | 467 | Таблица деплоя |
| `CHANGELOG.md` | 381 | История |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | 243, 387 | История + таблица |
| `docs/SERVER_HEALTH_REPORT_2026-03-04.md` | 3, 33-35 | Отчёт |
| `docs/CICD_SETUP.md` | 15, 34, 56 | SSH команды |
| `docs/SENTRY_GUIDE.md` | 114 | SSH команда |
| `docs/SERVER_RUNBOOK.md` | 20, 26, 29 | SSH alias |
| `README.md` | 244, 251 | Таблица + SSH |

**Итого:** 8 файлов содержат один и тот же IP. Источник правды должен быть `CLAUDE.md` → деплой-таблица. Остальные — ссылаться.

---

### DUP-02 — Cloudflare Tunnel UUID и webhook URL (HIGH)

**Факт:** UUID `c4645c9f-c72a-4d8e-995f-9b1196184397`, URL `tourists-wa.vipdxbrus.com/webhook`

| Файл | Кол-во вхождений |
|------|-----------------|
| `CLAUDE.md` | 8+ вхождений |
| `CHANGELOG.md` | 3 |
| `deploy/README.md` | 1 |
| `docs/DEPLOY.md` | 10+ |
| `docs/DEPLOY_GCP.md` | 8+ |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | 3 |
| `docs/SERVER_RUNBOOK.md` | 5+ |
| `MASTER_PLAN.md` | 1 |
| `README.md` | 2 |

**Итого:** 9 файлов. CLAUDE.md содержит полный раздел "Cloudflare Tunnel" с пошаговыми инструкциями (строки 500-540) — это дублирует `docs/DEPLOY.md` Part 5 и `docs/DEPLOY_GCP.md` Part 9.

---

### DUP-03 — Инструкции по настройке Cloudflare Tunnel (HIGH)

**Шаги cloudflared tunnel login/create/route/dns** дублируются в трёх файлах с идентичным содержанием:

| Файл | Раздел |
|------|--------|
| `CLAUDE.md` | Строки 513-530 (4 шага) |
| `docs/DEPLOY.md` | Part 5, секции 5.1-5.8 |
| `docs/DEPLOY_GCP.md` | Part 9, секции 9.1-9.8 |

Плюс частичное дублирование в `deploy/README.md`.

---

### DUP-04 — Статистика проекта с расхождениями (HIGH — нарушение SSOT)

**Одни и те же метрики в разных файлах с разными значениями:**

| Метрика | CLAUDE.md | README.md | Расхождение |
|---------|-----------|-----------|-------------|
| Python файлов | ~248+ | 280 | +32 |
| Тестов | 1,263 | 1,042+ | +221 (устарел README) |
| LOC | ~60K | ~105K | Другой способ подсчёта |
| Env переменных | ~43 | 51 | +8 |

**Вывод:** README.md содержит устаревшие данные (состояние ~Batch 4), CLAUDE.md актуален (Batch 6).

---

### DUP-05 — Batch история и статус (MEDIUM)

**Таблица "Batch 1-6 + статус"** полностью дублируется:

| Файл | Форма |
|------|-------|
| `CLAUDE.md` | Таблица строки 11-17 |
| `CHANGELOG.md` | Детальные записи |
| `docs/PROJECT_ACCOMPLISHMENTS.md` | Нарративная история (628 строк) |
| `docs/ARCHITECTURE.md` | Краткое упоминание |
| `docs/audit_ecosystem.md` | Таблица batch-статуса |

`docs/PROJECT_ACCOMPLISHMENTS.md` (628 строк) полностью пересекается с CHANGELOG.md — оба описывают историю Batch 1-5. Это наиболее крупный дубль по объёму (~2,500 токенов).

---

### DUP-06 — Бизнес-контекст (MEDIUM)

**"Сухейль — экскурсии, Марсель — авто, Муфамад — яхты, Tecom"** найдено в 12 файлах:

`CLAUDE.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE_v1.md`, `docs/MANUAL_TESTS.md`, `docs/PROJECT_ACCOMPLISHMENTS.md`, `docs/USER_GUIDE_admin.md`, `docs/USER_GUIDE_owner.md`, `docs/USER_GUIDE_staff.md`, `docs/UX_DESIGN_v1.md`, `docs/WHATSAPP_BOT_REDESIGN.md`, `MASTER_PLAN.md`

Источник правды: `CLAUDE.md`. В USER_GUIDE файлах контекст обоснован (аудитория — сами сотрудники). В остальных — избыточен.

---

### DUP-07 — AI Backend каскад (MEDIUM)

**"Gemini → Claude → Groq"** и модели (`gemini-2.5-flash`, `claude-sonnet-4-6`, `llama-3.3-70b`):

| Файл | Контекст |
|------|---------|
| `CLAUDE.md` | Таблица AI Backends |
| `README.md` | Таблица AI Backends (идентична!) |
| `docs/ARCHITECTURE.md` | Раздел LLM Cascade |
| `docs/ARCHITECTURE_v1.md` | Раздел 2.4 |
| `docs/audit_ai_lessons.md` | Список моделей |
| `CHANGELOG.md` | Строка 804 |
| `MASTER_PLAN.md` | Строки 159, 600+ |

---

### DUP-08 — ARCHITECTURE.md vs ARCHITECTURE_v1.md (HIGH)

**Два файла описывают одну и ту же архитектуру:**

- `docs/ARCHITECTURE.md` (424 строки, обновлён 2026-03-03, v4.0) — текущая версия
- `docs/ARCHITECTURE_v1.md` (841 строки, 2026-03-03, v4.0) — "AS-IS после Batch 1-4"

ARCHITECTURE.md создан на основе ARCHITECTURE_v1.md (указано в шапке: "Источник: ARCHITECTURE_v1.md"). Оба описывают одно и то же состояние, с разной степенью детализации. v1 является архивом, но не помечен как таковой.

---

### DUP-09 — DEPLOY.md vs DEPLOY_GCP.md (HIGH)

Два файла деплоя для разных облаков:

- `docs/DEPLOY.md` (798 строк) — Oracle Cloud ARM + структура
- `docs/DEPLOY_GCP.md` (1,062 строки) — GCP x86 (текущая продакшн)

**Дублирующиеся секции:**
- Part 2/Часть 2: Server initial setup — идентичны
- Part 3/Часть 3: API keys configuration — идентичны (~50 env переменных)
- Part 5/Часть 9: Cloudflare Tunnel — идентичны (с поправкой arm64/amd64)
- Part 4/Часть 5: Database setup — идентичны

`DEPLOY.md` описывает Oracle Cloud (старая инфраструктура). Продакшн уже на GCP. DEPLOY.md устарел или должен быть архивирован.

---

### DUP-10 — IMPROVEMENT_MASTER_PLAN.md vs v2 (MEDIUM)

- `docs/IMPROVEMENT_MASTER_PLAN.md` (879 строк) — план Batch 5 (Sessions 1-12), **завершён**
- `docs/IMPROVEMENT_MASTER_PLAN_v2.md` (255 строк) — план Batch 7-9, **активен**

v1 уже выполнен (Batch 5 завершён ✅ согласно CLAUDE.md). Должен быть архивирован, не является текущим источником правды. Но CLAUDE.md ссылается на него: "docs/IMPROVEMENT_MASTER_PLAN.md (12 сессий — UX, тексты, кнопки, Admin/WA архитектура, DB аудит)".

---

### DUP-11 — Docker команды сервера (MEDIUM)

**`sudo docker compose --env-file .env.prod -f docker-compose.yml`** появляется в:

| Файл | Кол-во вхождений |
|------|-----------------|
| `CLAUDE.md` | 3 (строки 409-412, 533) |
| `docs/SERVER_RUNBOOK.md` | 10+ |
| `docs/DEPLOY.md` | 5+ |
| `docs/DEPLOY_GCP.md` | 8+ |
| `docs/CICD_SETUP.md` | 3 |

Источник правды: `docs/SERVER_RUNBOOK.md`. CLAUDE.md должен иметь только ссылку + критическую заметку (--force-recreate).

---

### DUP-12 — DESIGN_DECISIONS_v1.md — мёртвая ссылка (MEDIUM, AP-09)

Файл `docs/DESIGN_DECISIONS_v1.md` **не существует**, но на него ссылаются:

| Файл | Строка |
|------|--------|
| `CLAUDE.md` | 337 (в дереве файлов) |
| `docs/ARCHITECTURE_v1.md` | 37, 73, 841 |
| `MASTER_PLAN.md` | 468, 559, 574, 1690 |
| `README.md` | 338 |

**AP-09 Code-Doc Drift:** документация описывает файл, которого нет.

---

### DUP-13 — PROJECT_ACCOMPLISHMENTS.md vs CHANGELOG.md (HIGH)

`docs/PROJECT_ACCOMPLISHMENTS.md` (628 строк, "Полная история проекта и достижения") дублирует CHANGELOG.md:

- Раздел "История по батчам" (Batch 1-5) повторяет CHANGELOG записи v4.0-v5.6.0
- Раздел "Ключевые технические решения" повторяет ARCHITECTURE.md
- Раздел "Что сейчас работает" = CLAUDE.md статус проекта

Этот файл создан как "нарративная" версия трёх других документов. По SSOT принципу — избыточен.

---

### DUP-14 — Batch status table в audit_ecosystem.md (LOW)

`docs/audit_ecosystem.md` содержит таблицу Batch 1-4 статусов, идентичную CLAUDE.md. Файл создан в Phase 0 (2026-03-03) и не обновлялся (Batch 5-6 не отражены). Является STALE аудитом.

---

## SSOT ТАБЛИЦА — ЧТО ДОЛЖНО БЫТЬ ГДЕ

| Факт | Должен быть в | Сейчас дублируется в |
|------|--------------|---------------------|
| GCP IP, зона, тип VM | `CLAUDE.md` деплой-таблица | 8 файлах |
| Cloudflare Tunnel UUID | `docs/SERVER_RUNBOOK.md` | 4 файлах |
| Пошаговые инструкции tunnel | `docs/DEPLOY_GCP.md` Part 9 | + CLAUDE.md + DEPLOY.md |
| AI backends таблица | `CLAUDE.md` | README.md (идентична) |
| История batch | `CHANGELOG.md` | + PROJECT_ACCOMPLISHMENTS.md |
| Статистика (.py, тесты, LOC) | `CLAUDE.md` | README.md (устаревшие данные) |
| Docker команды сервера | `docs/SERVER_RUNBOOK.md` | CLAUDE.md + DEPLOY*.md |
| Бизнес-контекст (UAE) | `CLAUDE.md` | 11 файлах |
| Архитектура компонентов | `docs/ARCHITECTURE.md` | ARCHITECTURE_v1.md (дубль) |

---

## АНТИ-ПАТТЕРНЫ

| ID | Паттерн | Severity | Файл(ы) |
|----|---------|----------|---------|
| AP-01 | Context Stuffing | HIGH | CLAUDE.md (557 строк, ~2.2K токенов) |
| AP-02 | Stale Docs | HIGH | DEPLOY.md (Oracle, устарел), audit_*.md (Phase 0), PROJECT_ACCOMPLISHMENTS.md |
| AP-09 | Code-Doc Drift | HIGH | DESIGN_DECISIONS_v1.md — ссылки на несуществующий файл |
| AP-11 | Duplicate Commands | HIGH | Docker команды в 5 файлах |
| AP-15 | Changelog as Status | MEDIUM | PROJECT_ACCOMPLISHMENTS.md пересказывает CHANGELOG |
| AP-16 | Cross-File Duplication | CRITICAL | IP в 8 файлах, Tunnel в 9 файлах |
| AP-19 | Roadmap Rot | MEDIUM | IMPROVEMENT_MASTER_PLAN.md (Batch 5, завершён, не архивирован) |

---

## РЕКОМЕНДАЦИИ

### HIGH PRIORITY

1. **[HIGH] DUP-04 — Исправить расхождение статистики:** README.md содержит устаревшие данные (1,042 тестов вместо 1,263; 280 .py вместо 248+). Обновить README.md из CLAUDE.md.

2. **[HIGH] DUP-08 — Архивировать ARCHITECTURE_v1.md:** Переместить в `docs/archive/ARCHITECTURE_v1.md`. Текущий источник — `docs/ARCHITECTURE.md`. Обновить ссылки.

3. **[HIGH] DUP-09 — Пометить DEPLOY.md как устаревший:** Oracle Cloud больше не используется. Добавить в шапку `> ⚠️ УСТАРЕЛ: проект перенесён на GCP. Актуальный деплой: DEPLOY_GCP.md` или переместить в архив.

4. **[HIGH] DUP-13 — Архивировать PROJECT_ACCOMPLISHMENTS.md:** Файл дублирует CHANGELOG + ARCHITECTURE + CLAUDE.md. Переместить в `docs/archive/`.

5. **[HIGH] DUP-12 — Удалить ссылки на DESIGN_DECISIONS_v1.md:** Файл не существует. Убрать из дерева CLAUDE.md (строка 337), README.md (строка 338), или создать файл.

### MEDIUM PRIORITY

6. **[MEDIUM] DUP-03 — Убрать Cloudflare Tunnel инструкции из CLAUDE.md:** CLAUDE.md содержит 30+ строк пошаговых инструкций (513-540). Заменить ссылкой: `→ Инструкции: docs/DEPLOY_GCP.md Part 9`. CLAUDE.md должен содержать только статус + ссылку.

7. **[MEDIUM] DUP-11 — Убрать дублированные docker команды из CLAUDE.md:** Строки 409-412, 533 дублируют SERVER_RUNBOOK.md. Оставить одну критическую заметку, убрать полный список.

8. **[MEDIUM] DUP-10 — Архивировать IMPROVEMENT_MASTER_PLAN.md (v1):** Batch 5 завершён. Переместить в `docs/archive/`. Обновить ссылку в CLAUDE.md на v2.

9. **[MEDIUM] Архивировать Phase 0 аудиты:** `docs/audit_*.md` (6 файлов) и `docs/AUDIT_2026-03-03.md` — устаревшие аудиты Phase 0 (2026-03-03). Переместить в `docs/archive/audits/`.

### LOW PRIORITY

10. **[LOW] DUP-06 — Бизнес-контекст:** Допустимо в USER_GUIDE файлах (аудитория — сотрудники). В технических файлах (ARCHITECTURE*.md) достаточно одного абзаца.

11. **[LOW] DUP-14 — Обновить audit_ecosystem.md:** Добавить шапку `**Статус:** УСТАРЕЛ (Phase 0, 2026-03-03). Актуальный статус: CLAUDE.md`.

---

## ПРОГНОЗ ЭКОНОМИИ

| Действие | Строк убрать | ~Токенов убрать |
|---------|-------------|----------------|
| Архивировать PROJECT_ACCOMPLISHMENTS.md | 628 | ~2,512 |
| Архивировать ARCHITECTURE_v1.md | 841 | ~3,364 |
| Архивировать DEPLOY.md (Oracle) | 798 | ~3,192 |
| Архивировать IMPROVEMENT_MASTER_PLAN.md v1 | 879 | ~3,516 |
| Архивировать 7 Phase-0 audit файлов | ~1,280 | ~5,120 |
| Убрать tunnel инструкции из CLAUDE.md | ~80 | ~320 |
| Убрать дублированные docker команды | ~30 | ~120 |
| **ИТОГО** | **~4,536** | **~18,144** |

**До:** 21,199 строк, ~85K токенов
**После:** ~16,663 строк, ~67K токенов
**Сокращение:** ~21% строк, ~21% токенов (только архивирование, без переписывания)

---

## ВЫВОД

В проекте выявлено **14 дублей** (12 по содержанию + 2 по файлам-версиям). Наиболее критичные:

- Один IP адрес сервера встречается в **8 файлах**
- Cloudflare Tunnel URL/UUID — в **9 файлах**
- Два файла деплоя с идентичными секциями (DEPLOY.md устарел)
- CHANGELOG история пересказана в PROJECT_ACCOMPLISHMENTS.md (628 строк)
- README.md содержит устаревшую статистику с расхождениями от CLAUDE.md

Verification Score: **2/5** — значительный drift, SSOT нарушен в ключевых фактах.
