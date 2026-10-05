# EXP-068: await call.answer() должен быть ПЕРВОЙ строкой callback handler

- **Дата:** 2026-02-28
- **Severity:** high
- **Тип:** fix
- **Проект:** rassilka-bot (aiogram 3.x)
- **Триггер:** #21 (Пропущенный callback.answer)

## Проблема
В 53 callback handlers `await call.answer()` стоял в КОНЦЕ функции или в mid-flow.
Это вызывает "spinning clock" в Telegram UI до 30 сек, пока handler обрабатывает логику.

## Правильно
`await call.answer()` — ПЕРВАЯ строка после `async def`, до любой логики:
```python
@router.callback_query(F.data == "something")
async def cb_handler(call: types.CallbackQuery):
    await call.answer()  # ← СРАЗУ
    # ... остальная логика
```

## Урок
При аудите aiogram-ботов — grep для callback_query handlers и проверять позицию call.answer().
Pattern: первые 3 строки handler должны содержать call.answer().

## times_applied: 1
