---
name: docs-optimizer
description: "Аудит и оптимизация проектной документации для Claude Code. Находит раздутые файлы, дублирование, устаревший контент, content drift. Триггеры - CLAUDE.md раздут, доки устарели, проверь документацию."
---
## Overview

Docs Optimizer — аудит, дедупликация и оптимизация проектной документации.
Комбинирует: анти-паттерны (docu-optimizer), question-driven трансформация (llm-docs-optimizer), tiered loading (token-optimizer) + опыт аудита проекта с 43K строк.

**Принцип:** CLAUDE.md = навигационный хаб, не энциклопедия. Свежесть > Полнота.

---

## When to Use

| Триггер | Режим |
|---------|-------|
| CLAUDE.md > 300 строк или > 2.5K токенов | `optimize` |
| Суммарно docs > 10K строк | `analyze` |
| Подозрение на дублирование | `audit` |
| Новый проект или рефакторинг docs/ | `tiered` |
| Быстрая проверка перед сессией | `analyze` |
| Применить готовый план | `apply` |

---

## Modes

### 1. `analyze` (по умолчанию)
1. Сканировать все MD файлы (корень + docs/ + .claude/)
2. Измерить: строки, ~токены (строк * 4), файлы, суммарный размер
3. Проверить 20 анти-паттернов + content drift detection
4. Найти дублирование между файлами
5. Классифицировать: `active` / `stale` / `dead`
6. Определить стадию: INIT / ACTIVE / STABLE / MAINTENANCE
7. Вывести отчёт с оценкой в формате `N/5`

### 2. `optimize`
Всё из `analyze` + оптимизированная CLAUDE.md, SSOT таблица, before/after метрики, .claudeignore

**Обязательный шаг перед генерацией оптимизированного CLAUDE.md:** создать tier-таблицу классификации контента:
```
| Tier | Контент | Что делать |
|------|---------|-----------|
| Essential | [секции которые остаются в CLAUDE.md] | Оставить, сократить |
| On-demand | [секции для выноса в docs/] | Переместить в docs/xxx.md |
| Archive | [устаревшее, в .claudeignore] | В docs/archive/ + .claudeignore |
```
Эта таблица **обязательна** — она обосновывает каждое решение оптимизации и показывает что остаётся (Essential), что выносится (On-demand), что архивируется (Archive).

### 3. `apply`
Всё из `optimize` + diff каждого изменения → подтверждение владельца → применить + бэкап в docs/archive/

### 4. `audit`
Полный аудит: .claude/ ecosystem, MEMORY↔CLAUDE дубли, ISSUES.md stale detection, roadmap freshness, валидность ссылок, карта дублирования

**Обязательные элементы вывода при `audit` режиме:**

**DUP-XX коды (обязательно при дублировании):**
Каждое найденное дублирование ОБЯЗАТЕЛЬНО кодировать как DUP-XX. Нельзя описывать дублирование без кода.
```
Формат: DUP-XX | [файл A] ↔ [файл B] | [что дублируется] | Severity: HIGH/MEDIUM/LOW
```
Примеры:
```
DUP-01 | CLAUDE.md ↔ docs/DEPLOY_GCP.md | GCP deployment params (IP, zone, VM type) | Severity: HIGH
DUP-02 | CLAUDE.md ↔ docs/ARCHITECTURE.md ↔ docs/ARCHITECTURE_v1.md | Архитектурное дерево файлов | Severity: HIGH
DUP-03 | CLAUDE.md ↔ docs/IMPROVEMENT_MASTER_PLAN.md | FORMATTING_GUIDE путь | Severity: MEDIUM
```

**Tier-таблица (обязательный формат вывода при полном аудите):**
В секции PHASE 3: SYNTHESIS ОБЯЗАТЕЛЬНО включать tier-таблицу для всех значимых файлов:
```
| Tier | File | Reason |
|------|------|--------|
| Essential | CLAUDE.md | Загружается каждую сессию, навигационный хаб |
| Essential | ISSUES.md | Актуальный список проблем |
| On-demand | docs/ARCHITECTURE.md | Читать при изменениях архитектуры |
| On-demand | docs/DEPLOY_GCP.md | Читать при деплое |
| Archive | docs/ARCHITECTURE_v1.md | Устарел, superseded by ARCHITECTURE.md |
| Archive | docs/DEPLOY.md | Oracle Cloud — заменён GCP деплоем |
```
Tier значения: `Essential` (всегда загружается), `On-demand` (по запросу), `Archive` (в .claudeignore)

### 5. `tiered`
Классификация по тирам: Essential (~800 токенов, всегда), On-demand (~500 каждый), Archive (0, .claudeignore). Реструктуризация + экономия токенов.

---

## Algorithm: 3 фазы

### Фаза 1: Discovery
1. Найти все MD файлы (корень, docs/, .claude/, подпроекты)
2. Считать метрики: строки, ~токены, дата изменения (git log)
3. Прочитать .claude/settings.json, .claudeignore
4. **Parent CLAUDE.md scan** — найти все CLAUDE.md вверх по дереву до ~/.claude/
5. Определить стадию: INIT (<5 коммитов) / ACTIVE (частые коммиты) / STABLE (2+ нед без изменений) / MAINTENANCE (редкие коммиты)

### Фаза 2: Parallel Analysis
Параллельно: A) Anti-pattern scan (20 паттернов), B) Cross-file duplication, C) Freshness check, D) SSOT violations, E) MEMORY↔CLAUDE diff, **F) Content drift detection**

### Фаза 3: Synthesis
Объединить → ранжировать по impact (HIGH/MEDIUM/LOW) → action plan → before/after projection

---

## Anti-Patterns (20 штук)

### Из docu-optimizer (15)

| ID | Паттерн | Плохо | Хорошо |
|----|---------|-------|--------|
| AP-01 | **Context Stuffing** | CLAUDE.md > 4K токенов, всё в одном файле | < 2.5K, ссылки на docs/ |
| AP-02 | **Stale Docs** | Инструкции для давно удалённых файлов | Актуальная структура |
| AP-03 | **Orphan Docs** | MD файлы без ссылок ниоткуда | Все файлы в навигации |
| AP-04 | **Cache-Hostile Order** | Динамический контент вверху CLAUDE.md | Статический → динамический |
| AP-05 | **Instruction Overload** | > 150 инструкций/правил | < 100, группировка по ролям |
| AP-06 | **Missing Modular Rules** | Все правила в CLAUDE.md | .claude/rules/ для переиспользуемых |
| AP-07 | **No Feedback Loop** | Нет experience/ или lessons learned | experience/_index.md |
| AP-08 | **Missing Emphasis** | Критические правила без выделения | `**КРИТИЧНО**`, CAPS для стоп-правил |
| AP-09 | **Code-Doc Drift** | Документация описывает код, которого нет | Верификация через grep/glob |
| AP-10 | **Monolithic Status** | Стена текста в "Текущий статус" | Структурированная таблица |
| AP-11 | **Duplicate Commands** | Одни и те же команды в 3+ файлах | Один файл + ссылки |
| AP-12 | **Missing Stage Markers** | Нет указания стадии проекта | INIT/ACTIVE/STABLE явно |
| AP-13 | **Flat Hierarchy** | Все docs в одной папке | docs/brand/, docs/plans/, docs/audits/ |
| AP-14 | **Missing Quick Start** | Нет "БЫСТРЫЙ СТАРТ" секции | 5-шаговый Quick Start вверху |
| AP-15 | **Changelog as Status** | CHANGELOG.md используется как текущий статус | CHANGELOG = история, CLAUDE.md = статус |

### Наши уникальные (5)

| ID | Паттерн | Плохо | Хорошо |
|----|---------|-------|--------|
| AP-16 | **Cross-File Duplication** | Один факт (версия, стек, URL) в 3-5 файлах | SSOT: один файл = источник правды |
| AP-17 | **MEMORY.md Bloat** | MEMORY.md дублирует 80% CLAUDE.md | MEMORY.md = только персистентные факты |
| AP-18 | **Stale Issues** | ISSUES.md: закрытые баги ещё OPEN | Обновлять статус при коммите |
| AP-19 | **Roadmap Rot** | Roadmap "Last updated: 3 месяца назад" | Дата обновления < 2 недель |
| AP-20 | **Protocol Sprawl** | Шаблоны отчётов (500+ строк) в CLAUDE.md | Вынести в docs/protocols.md |

**Детальное описание и примеры:** `See references/anti-patterns.md`

---

## Content Drift Detection

При анализе документов проверять семантическое устаревание:

1. **Найти упоминания версий** в тексте (v1.0, v2.3, Wave 3, Batch 2 и т.д.)
2. **Сравнить с текущей версией** проекта из CHANGELOG.md или CLAUDE.md
3. **Флагировать как OUTDATED** если расхождение > 1 мажорной версии
4. **Типичные признаки drift:** устаревшие деплой-таргеты, старые URL, ссылки на удалённые файлы, упоминания снятых зависимостей
5. **Выходной формат:**

| Файл | Упомянутая версия | Текущая версия | Severity |
|------|-------------------|----------------|----------|
| docs/arch.md | "Architecture v4.0" | v5.9 | HIGH |
| CLAUDE.md | "Wave 3 in progress" | Wave 5 complete | MEDIUM |

**Severity:**
- HIGH: расхождение > 1 мажорной версии или ссылки на несуществующее
- MEDIUM: расхождение в минорной версии или устаревший статус
- LOW: косметические несоответствия (старые имена, переименованные файлы)

### Freshness коды (AP-F0X)

При обнаружении freshness проблем — **обязательно использовать AP-F0X коды** (не описывать проблему просто текстом):

| Код | Проблема |
|-----|---------|
| AP-F01 | Файл не обновлялся более N дней (указать файл, дату последнего изменения, кол-во дней) |
| AP-F02 | Версия в документе расходится с текущей версией проекта |
| AP-F03 | Ссылки/URL в документе устарели или недоступны |
| AP-F04 | Описание функционала не соответствует текущему коду |

**Формат вывода для каждой freshness проблемы:**
```
AP-F0X | [файл] | [описание проблемы] | Severity: HIGH/MEDIUM/LOW
```

Пример:
```
AP-F01 | docs/arch.md | Не обновлялся 45 дней (последнее: 2026-01-25) | Severity: HIGH
AP-F02 | CLAUDE.md | Версия v4.0 в тексте, текущая v5.9 | Severity: HIGH
AP-F03 | docs/api.md | URL https://old.domain.com/api недоступен | Severity: MEDIUM
AP-F04 | docs/features.md | Описан модуль payments/, удалён в v5.0 | Severity: HIGH
```

---

## Metrics

### CLAUDE.md Size Thresholds (проверять ОБА независимо)

**По строкам:**
- **> 400 строк** → HIGH (обязательно флагировать)
- **> 300 строк** → MEDIUM

**По токенам:**
- **> 4,000 токенов** → CRITICAL (обязательно флагировать)
- **> 2,500 токенов** → HIGH

**Правило:** если ЛЮБОЙ порог превышен — флагировать по более высокому severity. Нельзя игнорировать строки если токены в норме, и наоборот.

### Общие метрики

| Метрика | Target | Warning | Critical |
|---------|--------|---------|----------|
| CLAUDE.md строк | < 250 | 250-400 | > 400 |
| CLAUDE.md ~токенов | < 2.5K | 2.5K-4K | > 4K |
| Кол-во инструкций | < 100 | 100-150 | > 150 |
| Cross-file дублей | 0 | 1-3 | > 3 |
| Stale files (>2 нед) | 0% | < 20% | > 20% |
| Orphan files | 0 | 1-2 | > 2 |
| ISSUES.md stale ratio | 0% | < 10% | > 10% |
| Verification score | 5/5 | 3-4/5 | < 3/5 |
| Суммарно docs строк | < 5K | 5K-15K | > 15K |
| Content drift items | 0 | 1-3 | > 3 |

**Verification score:** 5=всё актуально, 4=мелкие неточности, 3=stale секции, 2=значительный drift, 1=вводит в заблуждение, 0=вредная документация

---

## Tiered Loading

### Parent CLAUDE.md Scanning

При анализе токенной нагрузки — учитывать ВСЕ CLAUDE.md которые автоматически загружаются:
1. Пройти вверх по дереву директорий от проекта до `~/.claude/`
2. Найти все CLAUDE.md на каждом уровне
3. Подсчитать суммарную токенную нагрузку при старте сессии
4. Если родительский CLAUDE.md > проектного → предупредить отдельно
5. Пример: `D:/Downloads/CLAUDE.md` (~9,647 токенов) загружается для ВСЕХ проектов в Downloads/

**Формат вывода:**
```
PARENT CLAUDE.md CHAIN:
| Уровень | Файл | Строк | ~Токенов |
|---------|------|-------|----------|
| ~/.claude/ | CLAUDE.md | 120 | ~480 |
| D:/Downloads/ | CLAUDE.md | 450 | ~9,647 |
| D:/Downloads/project/ | CLAUDE.md | 280 | ~1,120 |
| СУММАРНО при старте | | 850 | ~11,247 |
```

### Essential (загружается всегда, ~800 токенов)
CLAUDE.md (оптимизированный): Quick Start, стек/команды/деплой (таблицы), ссылки на docs/, статус (таблица), проблемы → ISSUES.md

### On-demand (по запросу, ~500 токенов каждый)
`docs/brand/`, `docs/roadmaps/`, `docs/plans/`, `docs/design/`, CHANGELOG.md, ISSUES.md, WHY-LOG.md

### Archive (0 токенов, в .claudeignore)
`docs/archive/`, `docs/audits/`, `docs/SESSION-LOG.md`, `backups/`, `*.bak`

**Правило AP-03 → Archive (ОБЯЗАТЕЛЬНО):** файлы, на которые нет ссылок ни из CLAUDE.md, ни из других навигационных документов (orphan docs), ВСЕГДА классифицировать в тир `Archive`. В tier-таблице такие файлы обязательно помечать `Archive` с пояснением "Orphan: нет ссылок".

---

## CLAUDE.md Optimal Structure (cache-optimized)

Порядок: **статическое вверху, динамическое внизу** (для кэш-оптимизации LLM).

| Секция | Тип | Содержимое |
|--------|-----|-----------|
| Project Name + стек/git/деплой | СТАТИЧЕСКОЕ | Шапка проекта |
| Quick Start (5 шагов) | СТАТИЧЕСКОЕ | Быстрый старт |
| Команды | СТАТИЧЕСКОЕ | Таблица команд |
| Структура проекта | ПОЛУ-СТАТ | Дерево, не >40 строк |
| Принципы и правила | ПОЛУ-СТАТ | Ссылки на docs/ |
| Навигация по docs | ПОЛУ-СТАТ | Файл → когда читать |
| Текущий статус | ДИНАМИЧЕСКОЕ | Таблица: фаза, прогресс |
| Открытые проблемы | ДИНАМИЧЕСКОЕ | Ссылка на ISSUES.md |
| Что дальше | ДИНАМИЧЕСКОЕ | Список приоритетов |

**Целевой размер:** 200-250 строк, ~1K-1.2K токенов.

---

## Cross-File Deduplication (SSOT)

**Принцип:** каждый факт живёт в ОДНОМ файле. Остальные файлы ссылаются.

| Факт | Источник правды | НЕ дублировать в |
|------|-----------------|------------------|
| Версия проекта | CLAUDE.md шапка | MEMORY.md, CHANGELOG.md (там своя) |
| Стек технологий | CLAUDE.md шапка | MEMORY.md, docs/*.md |
| Бренд (цвета, шрифты) | docs/brand/brand-identity.md | CLAUDE.md (только ссылка) |
| Персонализация | docs/personalization.md | CLAUDE.md (только ссылка) |
| Команды запуска | CLAUDE.md "Команды" | docs/*.md |
| Деплой параметры | CLAUDE.md "Деплой" | docs/*.md |
| История изменений | CHANGELOG.md | CLAUDE.md (НЕ пересказывать) |
| Открытые проблемы | ISSUES.md | CLAUDE.md (только ссылка) |
| Решения и обоснования | WHY-LOG.md | CLAUDE.md (только ссылка) |
| Roadmap фичи | docs/roadmaps/[фича].md | CLAUDE.md (только ссылка) |
| Компоненты | docs/COMPONENT-LIBRARY.md | CLAUDE.md (только число: "50 компонентов") |
| Сессии | docs/SESSION-LOG.md | MEMORY.md (только последние 3-5) |
| Предпочтения владельца | docs/personalization.md | CLAUDE.md, MEMORY.md |

**Правило проверки:** если одна и та же строка (>10 слов) встречается в 2+ файлах — это SSOT violation.

---

## Output Format

Отчёты содержат: шапку (проект, стадия, score), таблицу метрик по файлам, анти-паттерны с severity, дублирование, content drift items, parent CLAUDE.md chain, рекомендации (HIGH/MEDIUM/LOW), прогноз экономии.

**Обязательный формат score** — overall documentation quality score ВСЕГДА писать как `N/5` (например: `3/5`, `5/5`). Не "3 из 5", не "60%", не просто "3". Только `N/5`.

**Шаблоны:** `See references/templates.md`

---

## Common Mistakes

| Ошибка | Правильно |
|--------|-----------|
| Удалить dormant docs | Спросить владельца, пометить `// DORMANT` |
| Сжать CHANGELOG / WHY-LOG | Журналы растут всегда, архивировать старое в docs/archive/ |
| Вынести всё из MEMORY.md | Убрать только дубли с CLAUDE.md, оставить уникальное |
| Удалять закрытые issues | Только обновлять stale статусы, история нужна |

**Золотое правило:** Archive != Delete. Перемещать в docs/archive/, НЕ удалять.

---

## Критические правила

1. **CLAUDE.md = хаб** — ссылки вместо содержимого, SSOT для каждого факта
2. **Свежесть > Полнота** — 50 актуальных строк лучше 500 устаревших
3. **Архив != Удаление** — docs/archive/, не удалять; журналы (CHANGELOG, WHY-LOG, ISSUES) растут всегда
4. **Dormant:** спросить перед удалением, пометить `// DORMANT`
5. **Двойные пороги:** проверять И строки И токены CLAUDE.md независимо
6. **Parent chain:** учитывать все CLAUDE.md вверх по дереву
7. **Content drift:** проверять версии в тексте vs текущая версия проекта
8. **Cache-optimized:** статическое вверху, динамическое внизу
9. **НИКОГДА** не применять изменения без OK владельца

---

## Промпт для Claude (инструкция по режимам)

При активации скилла, определи режим по запросу пользователя:
- "проверь/анализируй доки" → `analyze`
- "оптимизируй" → `optimize`
- "примени" → `apply`
- "аудит" → `audit`
- "tiered/тиры/токены" → `tiered`
- Без уточнения → `analyze`

**Порядок работы:**
1. Объявить режим и что будешь делать
2. Фаза Discovery через субагента (сканирование файлов, метрики)
3. Фаза Analysis через субагента (паттерны, дубли, свежесть)
4. Фаза Synthesis в главном окне (отчёт, рекомендации)
5. Ждать подтверждения перед любыми изменениями

**Детальные руководства:** `See references/`
- `references/anti-patterns.md` — развёрнутые описания 20 паттернов с примерами
- `references/transformation-patterns.md` — 20 паттернов трансформации (before/after)
- `references/tiered-loading.md` — детальная инструкция по тирам
- `references/cheatsheet.md` — краткая шпаргалка
