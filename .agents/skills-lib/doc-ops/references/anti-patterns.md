# Anti-Patterns: 20 паттернов плохой документации

Полный каталог анти-паттернов. Для каждого: описание, пример, исправление.

---

## Оригинальные (из исследований)

### AP-01: Context Stuffing
**Severity:** High
**Что:** Избыточные, "на всякий случай" инструкции, которые никогда не срабатывают. Раздувают контекст без пользы.
**Пример BAD:**
```
Никогда не используй jQuery. Не пиши на Python. Не удаляй package.json.
Не запускай rm -rf /. Не форматируй диск.
```
**Пример GOOD:**
```
Стек: Next.js 15 + TypeScript. Другие фреймворки не использовать.
```
**Fix:** Удалить инструкции, которые Claude и так не нарушит. Оставить только реально нужные ограничения.

---

### AP-02: Static Memory
**Severity:** Medium
**Что:** CLAUDE.md не обновляется между сессиями. Нет секции Learnings, нет датированных записей. Следующая сессия начинается с нуля.
**Пример BAD:**
```
# Project
Стек: Next.js
(и ничего больше, без дат, без истории)
```
**Пример GOOD:**
```
## Learnings
- 2026-03-10: Worktree на Windows требует core.longpaths = true
- 2026-03-11: SearchModal лучше через search-index.ts, не прямые импорты
```
**Fix:** Добавить секцию Learnings внизу CLAUDE.md. Датировать каждую запись.

---

### AP-03: Missing Plan Mode Guidance
**Severity:** Low
**Что:** Нет секции Workflow — Claude не знает как организовать работу (план → подтверждение → выполнение).
**Пример BAD:**
(Нет описания рабочего процесса)
**Пример GOOD:**
```
## Workflow
1. Показать план → ждать "ок"
2. Выполнить → отчёт
3. Обновить документацию
```
**Fix:** Добавить секцию Workflow с конкретными шагами.

---

### AP-04: Weak Verification Loop
**Severity:** High
**Что:** Нет конкретных команд проверки. "Проверь что всё работает" вместо конкретных `npm test`, `npm run typecheck`.
**Пример BAD:**
```
Убедись что код работает.
```
**Пример GOOD:**
```
## Verification
npm run typecheck        # Типы (0 ошибок)
npm run build            # Сборка (<3 мин)
npm test                 # Тесты (2374 pass)
```
**Fix:** Перечислить конкретные команды с ожидаемым результатом. Scoring 0-5 по полноте.

---

### AP-05: Permissions Not Documented
**Severity:** Low
**Что:** Для проектов с командами: непоследовательные пермишены (кто может деплоить, кто может мержить).
**Пример BAD:**
(Ничего про разрешения)
**Пример GOOD:**
```
Деплой: только после одобрения владельца
Коммит: по запросу, не автоматически
```
**Fix:** Документировать стоп-правила и разрешения.

---

### AP-06: No Format Standards
**Severity:** Medium
**Что:** Нет стандартов форматирования кода, нет хуков, нет линтера.
**Пример BAD:**
(Код без единого стиля, нет ESLint/Prettier)
**Пример GOOD:**
```
## Conventions
- Prettier: 2 spaces, single quotes, trailing comma
- ESLint: next/core-web-vitals
- Именование: camelCase (переменные), PascalCase (компоненты)
```
**Fix:** Добавить секцию Conventions с конкретными правилами.

---

### AP-07: Stale Documentation
**Severity:** Critical
**Что:** Файлы в docs/ не соответствуют текущему коду. API изменился, а документация — нет.
**Пример BAD:**
```
docs/API.md описывает endpoint /api/v1/users
Код использует /api/v2/users уже 3 месяца
```
**Пример GOOD:**
```
docs/API.md обновлён одновременно с кодом (один коммит)
```
**Fix:** Включить обновление docs/ в Definition of Done каждой задачи.

---

### AP-08: Missing Index
**Severity:** Medium
**Что:** Папка docs/ без README.md или индексного файла. Claude не знает что там и тратит токены на ls.
**Пример BAD:**
```
docs/
├── guide1.md
├── guide2.md
├── old-plan.md
└── some-notes.md
```
**Пример GOOD:**
```
docs/
├── README.md          # Индекс с описанием каждого файла
├── architecture.md
├── deployment.md
└── conventions.md
```
**Fix:** Создать docs/README.md с таблицей файлов и их назначением.

---

### AP-09: Orphan Docs
**Severity:** Medium
**Что:** Файлы в docs/, на которые ничего не ссылается. Никто их не читает, они только занимают место.
**Пример BAD:**
```
docs/old-migration-plan.md  — ни одной ссылки из CLAUDE.md или кода
```
**Пример GOOD:**
```
docs/old-migration-plan.md  → перенесён в docs/archive/ + добавлен в .claudeignore
```
**Fix:** Grep все ссылки на файлы docs/. Файлы без ссылок → archive или удалить.

---

### AP-10: Code-Doc Drift
**Severity:** High
**Что:** API/интерфейсы в коде отличаются от описания в документации. Количество компонентов, название функций, параметры — расхождение.
**Пример BAD:**
```
CLAUDE.md: "Компоненты: 35 шт."
Реальность: src/components/ содержит 50 файлов
```
**Пример GOOD:**
```
CLAUDE.md: "Компоненты: 50 шт. (docs/COMPONENT-LIBRARY.md)"
```
**Fix:** Автоматизировать подсчёт или ссылаться на ls/grep вместо ручных чисел.

---

### AP-11: Cache-Hostile Ordering
**Severity:** High
**Что:** Динамический контент (Learnings, Status) размещён ВЫШЕ статического (Architecture, Commands). Prompt caching работает по prefix — статика сверху кэшируется, динамика ломает кэш.
**Пример BAD:**
```
# Project
## Learnings (меняется каждую сессию)  ← ломает кэш всего ниже
## Architecture (статика)
## Commands (статика)
```
**Пример GOOD:**
```
# Project
## Quick Reference (статика)           ← кэшируется
## Architecture (статика)              ← кэшируется
## Commands (статика)                  ← кэшируется
## Status (полудинамика)
## Learnings (динамика)                ← внизу, не ломает кэш
```
**Fix:** Переупорядочить секции: статика сверху, динамика внизу. См. templates.md.

---

### AP-12: Instruction Overload
**Severity:** Critical
**Что:** Более 150 инструкций суммарно (CLAUDE.md + .claude/rules/ + MEMORY.md). Claude надёжно следует ~150-200 инструкциям; сверх этого — начинает случайно игнорировать.
**Пример BAD:**
```
CLAUDE.md: 80 правил
.claude/rules/: 50 правил
MEMORY.md: 40 правил
Итого: 170 → часть игнорируется
```
**Пример GOOD:**
```
CLAUDE.md: 30 правил (ключевые)
.claude/rules/: 20 правил (модульные)
MEMORY.md: 15 правил (уникальные)
Итого: 65 → все соблюдаются
```
**Fix:** Подсчитать инструкции. Приоритизировать. Объединить похожие. Удалить очевидные.

---

### AP-13: Missing Modular Rules
**Severity:** High
**Что:** CLAUDE.md > 3k токенов, но нет файлов .claude/rules/. Всё свалено в один файл.
**Пример BAD:**
```
CLAUDE.md (500 строк, 8000 токенов — всё в одном файле)
```
**Пример GOOD:**
```
CLAUDE.md (150 строк, 2500 токенов — ядро)
.claude/rules/git.md (правила коммитов)
.claude/rules/testing.md (правила тестирования)
.claude/rules/docs.md (правила документации)
```
**Fix:** Вынести тематические блоки из CLAUDE.md в .claude/rules/*.md.

---

### AP-14: No Feedback Loop
**Severity:** Medium
**Что:** Нет механизма "ошибка произошла → исправление → обновление CLAUDE.md". Одни и те же ошибки повторяются в каждой сессии.
**Пример BAD:**
(Баг с путями Windows повторяется 3 сессии подряд)
**Пример GOOD:**
```
## Learnings
- 2026-03-10: Windows пути: `D:\` → `/d/` в Git Bash. Использовать forward slashes ВСЕГДА.
```
**Fix:** После каждой нетривиальной ошибки — записывать в Learnings.

---

### AP-15: Missing Emphasis
**Severity:** Medium
**Что:** Критические правила без выделения (IMPORTANT, CRITICAL, **bold**). Claude может пропустить их среди обычного текста.
**Пример BAD:**
```
Не деплоить без одобрения.
Не удалять файлы.
```
**Пример GOOD:**
```
**КРИТИЧНО:** НЕ деплоить без явного одобрения владельца.
**КРИТИЧНО:** НЕ удалять файлы без спроса.
```
**Fix:** Выделить 5-10 самых критичных правил bold + caps.

---

## Собственные (из опыта)

### AP-16: Cross-File Duplication
**Severity:** Critical
**Что:** Одна и та же информация в 3+ файлах. Бренд в CLAUDE.md + brand-identity.md + design-system.md + moodboard.md. При обновлении одного — остальные устаревают.
**Пример BAD:**
```
CLAUDE.md: "Copper #C4896E, Sand #DEB7A4"
brand-identity.md: "Copper #C4896E, Sand #DEB7A4"
design-system.md: "Copper #C4896E, Sand #DEB7A4"
tailwind.config.ts: copper: '#C4896E'
```
**Пример GOOD:**
```
CLAUDE.md: "Бренд → docs/brand/brand-identity.md"
brand-identity.md: "Copper #C4896E, Sand #DEB7A4"  ← единственный источник
tailwind.config.ts: copper: '#C4896E'               ← код ссылается на brandbook
```
**Fix:** Single Source of Truth таблица. Один файл-владелец для каждого факта, остальные — ссылки.

---

### AP-17: Monolithic Status Block
**Severity:** High
**Что:** "Текущий статус" как сплошной абзац 2000+ символов. Невозможно быстро извлечь нужное.
**Пример BAD:**
```
**Статус:** Полноценный сайт с 65+ роутами, 50 компонентами, 25 файлами данных
(236 продуктов в каталоге + 20 авианаправлений + 52 отзыва + 13 бандлов,
14 категорий + flights + trip-planner + city pages + favorites)...
[ещё 1500 символов сплошного текста]
```
**Пример GOOD:**
```
| Метрика | Значение |
|---------|----------|
| Роуты | 65+ |
| Компоненты | 50 |
| Продукты | 236 |
| Категории | 14 |
```
**Fix:** Таблица метрик (ключ-значение) + 5-7 bullet points для контекста.

---

### AP-18: Dead Pointers
**Severity:** Medium
**Что:** Ссылки на перемещённые или удалённые файлы. CLAUDE.md говорит "см. GLOSSARY.md", а файл на самом деле в docs/GLOSSARY.md или удалён.
**Пример BAD:**
```
CLAUDE.md: "Словарь: GLOSSARY.md"
Реальность: файл перемещён в docs/GLOSSARY.md
```
**Пример GOOD:**
```
CLAUDE.md: "Словарь: docs/GLOSSARY.md"  ← проверенный путь
```
**Fix:** Grep все ссылки на файлы в CLAUDE.md. Проверить существование каждого. Исправить или удалить битые.

---

### AP-19: Stale Issues
**Severity:** High
**Что:** Решённые issues в ISSUES.md всё ещё со статусом OPEN. Claude тратит время на анализ уже закрытых проблем.
**Пример BAD:**
```
| I-42 | FilterPanel не закрывается | OPEN |
(Исправлено в v0.28.0, но статус не обновлён)
```
**Пример GOOD:**
```
| I-42 | FilterPanel не закрывается | CLOSED | v0.28.0, 2026-03-08 |
```
**Fix:** Cross-reference ISSUES.md с CHANGELOG.md и git log. Закрыть все решённые.

---

### AP-20: Memory-Doc Overlap
**Severity:** High
**Что:** MEMORY.md дублирует 50-70% информации из CLAUDE.md. Оба загружаются — двойной расход токенов.
**Пример BAD:**
```
MEMORY.md: "Стек: Next.js 15 + TypeScript + Tailwind CSS 4"
CLAUDE.md: "Стек: Next.js 15 + TypeScript + Tailwind CSS 4"
MEMORY.md: [полная архитектура, история сессий, бренд]
CLAUDE.md: [та же архитектура, история сессий, бренд]
```
**Пример GOOD:**
```
MEMORY.md: [только уникальное — credentials, личные уроки, стоп-правила]
CLAUDE.md: [архитектура, бренд, статус — единственный источник]
```
**Fix:** В MEMORY.md оставить только то, чего НЕТ в CLAUDE.md: credentials, уроки, правила. Убрать дублирующуюся архитектуру, бренд, историю.

---

## Сводная таблица

| ID | Паттерн | Severity | Категория |
|----|---------|----------|-----------|
| AP-01 | Context Stuffing | High | Содержание |
| AP-02 | Static Memory | Medium | Процесс |
| AP-03 | Missing Plan Mode Guidance | Low | Процесс |
| AP-04 | Weak Verification Loop | High | Качество |
| AP-05 | Permissions Not Documented | Low | Процесс |
| AP-06 | No Format Standards | Medium | Качество |
| AP-07 | Stale Documentation | Critical | Актуальность |
| AP-08 | Missing Index | Medium | Структура |
| AP-09 | Orphan Docs | Medium | Структура |
| AP-10 | Code-Doc Drift | High | Актуальность |
| AP-11 | Cache-Hostile Ordering | High | Производительность |
| AP-12 | Instruction Overload | Critical | Содержание |
| AP-13 | Missing Modular Rules | High | Структура |
| AP-14 | No Feedback Loop | Medium | Процесс |
| AP-15 | Missing Emphasis | Medium | Содержание |
| AP-16 | Cross-File Duplication | Critical | Дублирование |
| AP-17 | Monolithic Status Block | High | Содержание |
| AP-18 | Dead Pointers | Medium | Актуальность |
| AP-19 | Stale Issues | High | Актуальность |
| AP-20 | Memory-Doc Overlap | High | Дублирование |
