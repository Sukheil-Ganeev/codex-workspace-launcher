# Ответ: Добавление возврата ID заказа

## Исправленный код

```python
@app.post('/api/orders')
async def create_order(data: dict):
    order = Order(**data)
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"status": "ok", "id": order.id}
```

## Что изменилось

Добавлена одна строка — `db.refresh(order)`.

После `db.commit()` объект `order` в памяти Python теряет актуальные данные из базы (в том числе `id`, который генерирует БД). Метод `db.refresh(order)` повторно загружает объект из базы — после этого `order.id` содержит реальный ID созданной записи.

Затем в return добавлено поле `"id": order.id`.

## Дополнительные рекомендации

Если хотите сделать эндпоинт надёжнее, стоит также добавить обработку ошибок:

```python
@app.post('/api/orders')
async def create_order(data: dict):
    try:
        order = Order(**data)
        db.add(order)
        db.commit()
        db.refresh(order)
        return {"status": "ok", "id": order.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
```

Без `db.rollback()` при ошибке сессия базы данных остаётся в сломанном состоянии и последующие запросы тоже будут падать.
