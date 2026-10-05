# feature-blueprint

Прежде чем писать код — нарисуй и опиши.

## Quick Start

```
blueprint: plan     → Tech Spec (MoSCoW + архитектура + DB + задачи)
blueprint: adr      → Architecture Decision Record
blueprint: diagram  → Mermaid диаграмма (flowchart / sequence / ERD / C4)
blueprint: db-design→ PostgreSQL схема + идемпотентная миграция
blueprint: breakdown→ Декомпозиция спека на задачи по 15-60 минут
```

## Структура

```
feature-blueprint/
├── SKILL.md                          — главный файл скилла, все режимы и правила
├── README.md                         — этот файл
├── references/
│   ├── spec-templates.md             — шаблоны: Tech Spec, ADR, RFC, MoSCoW
│   └── diagram-patterns.md           — Mermaid паттерны: webhook flow, FSM, ERD, C4, deployment
└── assets/templates/
    ├── feature-spec.md               — пример: "Добавление Max Bot в Omni Inbox"
    └── adr-template.md               — пример: "ADR-001: Synthetic user_id для Max Bot"
```

## Объединяет скиллы

- `spec-driven-dev` v1.1.0 — planning, MoSCoW, ADR, RFC, breakdown
- `mermaid` v1.0 — все типы диаграмм, синтаксис, паттерны
- `database-schema-designer` — PostgreSQL best practices, индексы, миграции

## License

Apache-2.0
