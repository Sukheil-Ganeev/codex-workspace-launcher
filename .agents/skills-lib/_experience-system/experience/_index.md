# Experience Index — _experience-system

> Актуально на: 2026-03-01

## Критические уроки (топ-5)

1. **Subagent-Driven Development** — 9 фич за сессию, каждая задача = отдельный субагент. Главное окно = диспетчер. [abaya-bot-waves6-7.md](../abaya-bot-waves6-7.md#1)
2. **Порядок задач критичен** — Prisma миграции первыми, затем сервисы, затем flows, затем frontend. [abaya-bot-waves6-7.md](../abaya-bot-waves6-7.md#2)
3. **API contract mismatches** — Backend/Frontend pagination и auth response форматы расходятся. Решение: fetchPaginated helper + unwrap. [abaya-bot-waves6-7.md](../abaya-bot-waves6-7.md#3)
4. **bcrypt rounds** — 12 в production, 4 в тестах (иначе таймауты Vitest). [abaya-bot-waves6-7.md](../abaya-bot-waves6-7.md#4)
5. **Channel Adapter Pattern** — MessageSender interface для омниканальности (WhatsApp + Instagram). FSM/flows без изменений. [abaya-bot-waves6-7.md](../abaya-bot-waves6-7.md#6)

## Записи

| ID | Файл | Проект | Дата | Severity |
|----|------|--------|------|----------|
| EXP-001 | [abaya-bot-waves6-7.md](../abaya-bot-waves6-7.md) | Abaya Bot | 2026-03-01 | high |

## Статистика
- Всего записей: 1
- Последнее обновление: 2026-03-01
