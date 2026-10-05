# database-sql-справочник

**Статус:** Production Ready
**Версия:** 1.0.0
**Автор:** Claude Skills
**Язык:** Русский + English примеры

---

## Описание

Полный справочник по SQL и управлению базами данных, оптимизированный для туристического бизнеса. Включает готовые schemas, примеры запросов, паттерны и best practices для работы с PostgreSQL.

**Идеально для:**
- Backend-разработчиков туристических платформ
- DevOps инженеров, настраивающих БД
- Data Analysts, работающих с историческими данными
- Всех, кто хочет понять SQL на production-уровне

**Основной фокус:**
- Управление турами, бронированиями, клиентами
- Ценообразование и скидки
- Аналитика и отчётность
- Безопасность и производительность

---

## Структура файлов

```
database-sql-справочник/
├── SKILL.md                    # Основной справочник (2500+ слов)
├── README.md                   # Этот файл
├── marketplace.json            # Метаданные для интеграции
├── experience/
│   └── _index.md              # Накопленные уроки и опыт
├── references/                 # 8 детальных модулей (~1000 слов каждый)
│   ├── sql-fundamentals.md
│   ├── data-types-constraints.md
│   ├── indexes-performance.md
│   ├── transactions-locking.md
│   ├── advanced-queries.md
│   ├── orm-integration.md
│   ├── security-backup.md
│   └── migrations-schema.md
├── assets/
│   ├── templates/              # SQL шаблоны для копирования
│   │   ├── booking-system.sql
│   │   ├── pricing-engine.sql
│   │   └── analytics-dashboard.sql
│   └── examples/               # Готовые примеры с данными
│       ├── sample-tourism-db.sql
│       ├── complex-queries.sql
│       └── optimization-tips.sql
└── scripts/
    ├── init-database.sh        # Инициализация БД
    ├── backup-restore.sh       # Резервные копии
    └── performance-check.sql   # Проверка производительности
```

---

## Quick Links

### Основное содержание
- **[SKILL.md](./SKILL.md)** — Полный справочник
  - Overview
  - Quick Start (подключение)
  - 13 Schemas для туризма
  - SQL Fundamentals
  - Advanced Features
  - ORM Integration (Prisma)
  - Best Practices
  - Common Patterns
  - Troubleshooting

### Детальные модули

| Модуль | Описание | Ссылка |
|--------|---------|--------|
| SQL Fundamentals | SELECT, WHERE, JOIN, агрегация | [sql-fundamentals.md](./references/sql-fundamentals.md) |
| Data Types | SERIAL, VARCHAR, JSON, DECIMAL | [data-types-constraints.md](./references/data-types-constraints.md) |
| Indexes & Performance | Индексирование, VACUUM, анализ | [indexes-performance.md](./references/indexes-performance.md) |
| Transactions & Locking | ACID, сохранение точек, deadlocks | [transactions-locking.md](./references/transactions-locking.md) |
| Advanced Queries | Window Functions, CTE, Full-Text Search | [advanced-queries.md](./references/advanced-queries.md) |
| ORM Integration | Prisma, миграции, типизация | [orm-integration.md](./references/orm-integration.md) |
| Security & Backup | Роли, права, шифрование, восстановление | [security-backup.md](./references/security-backup.md) |
| Migrations & Schema | Контроль версий БД, инструменты | [migrations-schema.md](./references/migrations-schema.md) |

### Шаблоны и примеры

**SQL шаблоны** (`assets/templates/`):
- `booking-system.sql` — Полная система бронирования
- `pricing-engine.sql` — Динамическое ценообразование
- `analytics-dashboard.sql` — Отчёты и KPI

**Примеры** (`assets/examples/`):
- `sample-tourism-db.sql` — Тестовые данные
- `complex-queries.sql` — 20+ готовых запросов
- `optimization-tips.sql` — Оптимизация реальных кейсов

### Скрипты

```bash
# Инициализация
bash scripts/init-database.sh

# Резервная копия
bash scripts/backup-restore.sh --backup

# Проверка производительности
psql -d tourism_db -f scripts/performance-check.sql
```

---

## Начало работы

### 1. Прочитайте SKILL.md
Начните с [SKILL.md](./SKILL.md) для основного понимания:
- Overview (зачем это нужно)
- Quick Start (как подключиться)
- 13 Schemas (как организована БД)

### 2. Изучите references
Когда нужна глубина по теме:
- Работаете с индексами? → [indexes-performance.md](./references/indexes-performance.md)
- Настраиваете Prisma? → [orm-integration.md](./references/orm-integration.md)
- Нужна безопасность? → [security-backup.md](./references/security-backup.md)

### 3. Используйте шаблоны
Копируйте готовые SQL из `assets/templates/`:
```bash
cp assets/templates/booking-system.sql your-project/
# Адаптируйте под вашу БД
```

### 4. Протестируйте на примерах
```bash
# Загрузить тестовые данные
psql -d tourism_db -f assets/examples/sample-tourism-db.sql

# Запустить готовые запросы
psql -d tourism_db -f assets/examples/complex-queries.sql
```

---

## Используемые технологии

- **СУБД:** PostgreSQL 12+
- **ORM:** Prisma 4+
- **Языки:** SQL, TypeScript, Python, JavaScript
- **Инструменты:** pg_stat_statements, explain, pgAdmin

---

## Интеграция с другими скиллами

**Зависит от:**
- `postgresql-table-design` — Основные концепции дизайна таблиц

**Используется в:**
- `api-backend-patterns` — Примеры работы с БД
- `performance-optimization` — Оптимизация запросов

---

## Когда обновляется

- **Содержание:** При выходе PostgreSQL 13+, Prisma 5+
- **Примеры:** Если найдены лучшие паттерны
- **Опыт:** Постоянно добавляются уроки

---

## Опыт и lessons learned

Смотрите `experience/_index.md` для:
- Критических уроков (читайте при активации!)
- Исправленных ошибок
- Найденных улучшений
- Паттернов и предупреждений

При нахождении полезного урока:
> "Хотите записать это в опыт скилла?"

---

## Быстрые ответы

**Q: С чего начать?**
A: Прочитайте Quick Start в SKILL.md + посмотрите на 13 schemas

**Q: Как оптимизировать медленный запрос?**
A: EXPLAIN ANALYZE + индексирование (см. indexes-performance.md)

**Q: Как настроить Prisma?**
A: Используйте prisma schema из SKILL.md раздел 6

**Q: Как делать миграции?**
A: Смотрите migrations-schema.md и используйте prisma migrate

**Q: Как обеспечить безопасность?**
A: Prepared statements + роли + шифрование (security-backup.md)

---

## Версионирование

| Версия | Дата | Что изменилось |
|--------|------|-----------------|
| 1.0.0 | 2026-02-04 | Первый релиз: SKILL.md, 8 modules, шаблоны |

---

## Поддержка

При проблемах:
1. Проверьте `experience/_index.md` → может быть known issue
2. Смотрите Troubleshooting в SKILL.md
3. Проверьте соответствующий reference модуль

---

**Последнее обновление:** 2026-02-04
**Статус:** Production Ready ✓
