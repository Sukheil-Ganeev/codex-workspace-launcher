# Ответ без скилла: N+1 запрос и красивый вывод в боте

## Проблема в коде

Твой код делает **N+1 запросов к базе данных**:
- 1 запрос — получить всех туристов
- N запросов — для каждого туриста отдельный запрос за заказами

Если туристов 500 — будет 501 запрос. Это медленно.

## Правильный подход: один запрос

```python
from sqlalchemy.orm import joinedload

tourists = db.query(Tourist).options(joinedload(Tourist.orders)).all()
```

Теперь SQLAlchemy загрузит всё за 1-2 запроса, и `tourist.orders` уже доступен без дополнительных запросов.

## Красивый вывод в Telegram-боте

```python
async def show_tourists_orders(message: Message, db: Session):
    tourists = db.query(Tourist).options(joinedload(Tourist.orders)).all()

    if not tourists:
        await message.answer("Туристов не найдено.")
        return

    lines = []
    for tourist in tourists:
        order_count = len(tourist.orders)
        if order_count == 0:
            icon = "⬜"
        elif order_count < 3:
            icon = "🟡"
        else:
            icon = "🟢"
        lines.append(f"{icon} {tourist.name} — {order_count} заказ(ов)")

    text = "📋 <b>Туристы и их заказы:</b>\n\n" + "\n".join(lines)
    await message.answer(text, parse_mode="HTML")
```

## Вывод с постраничкой (если туристов много)

```python
PAGE_SIZE = 10

async def show_tourists_page(message: Message, db: Session, page: int = 0):
    tourists = db.query(Tourist).options(joinedload(Tourist.orders)).all()

    total = len(tourists)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_tourists = tourists[start:end]

    lines = []
    for i, tourist in enumerate(page_tourists, start=start + 1):
        order_count = len(tourist.orders)
        lines.append(f"{i}. {tourist.name} — {order_count} заказ(ов)")

    text = f"📋 <b>Туристы ({start+1}–{min(end, total)} из {total}):</b>\n\n" + "\n".join(lines)

    # Кнопки навигации
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(text="← Назад", callback_data=f"tourists_page:{page-1}")
    if end < total:
        builder.button(text="Вперёд →", callback_data=f"tourists_page:{page+1}")

    await message.answer(text, parse_mode="HTML", reply_markup=builder.as_markup())
```

## Итого

| Было | Стало |
|------|-------|
| N+1 запросов | 1-2 запроса (joinedload) |
| print() | await message.answer() |
| Нет пагинации | Постраничный вывод |
| Нет форматирования | HTML + иконки |
