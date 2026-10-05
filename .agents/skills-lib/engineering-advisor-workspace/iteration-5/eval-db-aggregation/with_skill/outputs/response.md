# Engineering Advisor — Анализ stats.service.ts

**Запрос:** Добавить подсчёт заказов по статусам (pending/confirmed/cancelled) в существующий сервис статистики.

---

## Шаг 1: Анализ кода (до внесения изменений)

Перед выполнением запроса — проверка триггеров Engineering Advisor.

---

## === Engineering Advisor ===

**WARN (1):** `stats.service.ts:7` — Триггер #25: `findMany + JS агрегация вместо DB`

```typescript
// Проблема: загрузка ВСЕХ заказов в память
const orders = await prisma.order.findMany();    // N строк из БД

// Проблема: фильтрация и агрегация в JavaScript, а не в БД
const paidOrders = orders.filter(o => o.status === 'paid');
const total = paidOrders.length;
const revenue = paidOrders.reduce((sum, o) => sum + o.amount, 0);
```

**Что происходит на самом деле:**
- При 10,000 заказов — в память грузится 10,000 объектов. При 100,000 — 100,000.
- Каждый объект Order содержит все поля: id, status, amount, customerId, createdAt, items...
- Сеть: сервер БД → Node.js передаёт мегабайты данных только чтобы посчитать одно число.
- БД умеет делать это за один запрос с индексом, в 10-100x быстрее.

**Аналогия:** "Перебирать все полки склада вручную, чтобы узнать сколько товаров — вместо запроса в инвентарной системе."

---

**WARN (2):** `stats.service.ts:13-17` — Та же проблема #25 для клиентов

```typescript
// Загружаем ВСЕХ клиентов
const customers = await prisma.customer.findMany();

// Фильтруем в JS по дате
const activeCustomers = customers.filter(c => c.lastOrderAt &&
  new Date(c.lastOrderAt) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
).length;
```

БД умеет сделать это через `count({ where: { lastOrderAt: { gte: ... } } })` — без загрузки объектов.

---

**INFO (1):** Запрос пользователя — добавить подсчёт по статусам (pending/confirmed/cancelled) — НЕЛЬЗЯ выполнять в текущей архитектуре. Иначе добавим ещё три `.filter()` поверх уже загруженного `findMany()`. Это усугубит проблему.

---

## Опыт: применено 1 урок (EXP из abaya-bot audit: "findMany + JS aggregation")

---

## Шаг 2: Правильное решение

Сначала исправить архитектуру, потом добавить подсчёт по статусам. Иначе каждое новое требование будет добавлять ещё один `.filter()`.

### Правильный код — через DB-level агрегацию:

```typescript
// stats.service.ts (исправленная версия)
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function getDashboardStats() {
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

  // Один запрос: COUNT + SUM по paid заказам (без загрузки данных)
  const paidStats = await prisma.order.aggregate({
    where: { status: 'paid' },
    _count: { id: true },
    _sum: { amount: true },
  });

  // Один запрос: активные клиенты за 30 дней
  const activeCustomers = await prisma.customer.count({
    where: {
      lastOrderAt: { gte: thirtyDaysAgo },
    },
  });

  // НОВЫЙ ФУНКЦИОНАЛ: подсчёт по статусам — тоже в БД
  const ordersByStatus = await prisma.order.groupBy({
    by: ['status'],
    where: {
      status: { in: ['pending', 'confirmed', 'cancelled'] },
    },
    _count: { id: true },
  });

  // Приводим к удобному формату
  const statusCounts = {
    pending: 0,
    confirmed: 0,
    cancelled: 0,
  };
  for (const row of ordersByStatus) {
    if (row.status in statusCounts) {
      statusCounts[row.status as keyof typeof statusCounts] = row._count.id;
    }
  }

  return {
    totalPaidOrders: paidStats._count.id ?? 0,
    totalRevenue: paidStats._sum.amount ?? 0,
    activeCustomers,
    ordersByStatus: statusCounts,
  };
}
```

### Что изменилось:

| Было | Стало |
|------|-------|
| `findMany()` — загрузка всех строк | `aggregate()` / `count()` — только число |
| 2 запроса × N строк в памяти | 3 легких запроса, без данных в памяти |
| JS `.filter()` + `.reduce()` | DB индекс + GROUP BY |
| Для 100K заказов: ~секунды | Для 100K заказов: ~миллисекунды |

---

## Шаг 3: Параллельное выполнение (бонус)

Если нужна максимальная скорость — все три запроса можно запустить параллельно:

```typescript
const [paidStats, activeCustomers, ordersByStatus] = await Promise.all([
  prisma.order.aggregate({ where: { status: 'paid' }, _count: { id: true }, _sum: { amount: true } }),
  prisma.customer.count({ where: { lastOrderAt: { gte: thirtyDaysAgo } } }),
  prisma.order.groupBy({ by: ['status'], where: { status: { in: ['pending', 'confirmed', 'cancelled'] } }, _count: { id: true } }),
]);
```

Вместо последовательного выполнения — все три идут одновременно. Общее время = самый медленный запрос, а не сумма всех.

---

## Итог

**Триггеры:** #25 (findMany + JS агрегация) — сработал дважды

**BLOCK:** 0
**WARN:** 2 (производительность — реальный риск при росте данных)
**INFO:** 1 (рекомендация по параллельному выполнению)

**Рекомендация:** Уровень WARN — исправить до добавления новых фич. Добавлять подсчёт по статусам поверх текущей архитектуры нельзя — это умножит проблему.

---

**Делегация:** Для анализа всех DB-запросов в проекте → `superpowers:systematic-debugging` ("Найди все findMany без where/select в проекте, замени на count/aggregate")

---

## === Engineering Advisor Summary ===
Файлы проанализированы: 1 (stats.service.ts)
Триггеры сработали: #25 (findMany + JS агрегация — 2 места)
BLOCK: 0
WARN: 2 — загрузка всех заказов и клиентов в память вместо DB-агрегации
INFO: 1 — параллельное выполнение через Promise.all
Опыт применён: abaya-bot audit (findMany + JS aggregation anti-pattern)
========================================
