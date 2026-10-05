# Engineering Advisor — Ответ на запрос N+1

## Активация скилла

Engineering Advisor активирован. Загружено 15+ уроков из опыта. Буду проверять код с учётом накопленных ошибок.

---

## Анализ кода

```python
tourists = db.query(Tourist).all()
for tourist in tourists:
    orders = db.query(Order).filter_by(user_id=tourist.id).all()
    print(f"{tourist.name}: {len(orders)} заказов")
```

---

## Engineering Advisor — Диагностика

```
=== Engineering Advisor ===
Триггер #12 (N+1 queries): SELECT в цикле
Уровень: Advisory (INFO)
INFO (1): Цикл по tourists делает 1 + N запросов к БД.
          100 туристов = 101 запрос. 1000 туристов = 1001 запрос.
          Это замедляет бота и создаёт нагрузку на БД.
Опыт: EXP-001 (Advisory first — не блокируй), триггер #12 применён.
===========================
```

---

## Что происходит в твоём коде

Представь что ты в офисе, и нужно узнать у каждого из 200 клиентов сколько заказов он сделал. Два варианта:

1. **Твой текущий код:** Позвони каждому клиенту по очереди — 200 звонков.
2. **Оптимальный:** Разошли один групповой запрос в базу — один ответ сразу со всеми данными.

Разница: при 200 туристах — 201 запрос к базе вместо 1. При 1000 — 1001 запрос.

---

## Исправленный код (SQLAlchemy — один запрос с JOIN)

```python
from sqlalchemy import func
from sqlalchemy.orm import joinedload

# Вариант 1: JOIN + GROUP BY (один запрос, быстро)
results = (
    db.query(Tourist.name, func.count(Order.id).label("order_count"))
    .outerjoin(Order, Order.user_id == Tourist.id)
    .group_by(Tourist.id, Tourist.name)
    .all()
)

for name, order_count in results:
    print(f"{name}: {order_count} заказов")
```

**Или через joinedload (если нужны сами объекты заказов):**

```python
# Вариант 2: eager loading — 2 запроса вместо N+1
tourists = (
    db.query(Tourist)
    .options(joinedload(Tourist.orders))
    .all()
)

for tourist in tourists:
    print(f"{tourist.name}: {len(tourist.orders)} заказов")
```

> Вариант 2 требует что в модели Tourist определена relationship: `orders = relationship("Order", back_populates="tourist")`

---

## Как красиво вывести в боте

```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import func

router = Router()

@router.message(Command("tourists"))
async def show_tourists(message: Message, db):
    # Один запрос вместо N+1
    results = (
        db.query(Tourist.name, func.count(Order.id).label("order_count"))
        .outerjoin(Order, Order.user_id == Tourist.id)
        .group_by(Tourist.id, Tourist.name)
        .order_by(Tourist.name)
        .all()
    )

    if not results:
        await message.answer("Туристов пока нет.")
        return

    lines = [f"<b>Туристы и заказы:</b>"]
    for name, order_count in results:
        lines.append(f"• {name}: {order_count} заказов")

    await message.answer("\n".join(lines), parse_mode="HTML")
```

**Пример вывода в боте:**
```
Туристы и заказы:
• Алексей Иванов: 3 заказа
• Мария Петрова: 1 заказ
• Сухейль Ганеев: 7 заказов
```

---

## Итог

| | До | После |
|---|---|---|
| Запросов к БД | 1 + N (на каждого туриста) | 1 (один JOIN) |
| 100 туристов | 101 запрос | 1 запрос |
| Скорость | Медленно при росте базы | Стабильно |

---

## Что ещё проверить

- Если используешь async SQLAlchemy (asyncpg) — замени `db.query()` на `await session.execute(select(...))`.
- Добавь индекс на `Order.user_id` в базе — ускорит JOIN в 5-10 раз на больших таблицах.

---

*Engineering Advisor — триггер #12 (N+1 queries). Advisory level.*
