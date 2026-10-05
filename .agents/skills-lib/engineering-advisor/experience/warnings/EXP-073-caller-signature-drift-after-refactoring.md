# EXP-073: Caller-callee signature drift after DB method refactoring

- **Дата:** 2026-03-01
- **Severity:** critical
- **Тип:** warning
- **Проект:** VIP-DXB-CatalogBot (7 platforms, Python)

## Проблема
После рефакторинга методов `CatalogDB`:
- `get_bestsellers(days=30)` — изменилась сигнатура (параметры переименованы/удалены/добавлены)
- `get_card_cross_sell(block_id, categories, emirate, limit)` — аналогично

Callers в handlers продолжали вызывать с СТАРОЙ сигнатурой. Runtime crash:
```
TypeError: get_bestsellers() got an unexpected keyword argument 'days'
```

## Почему тесты не поймали
Unit-тесты мокировали DB:
```python
mock_db.get_bestsellers = AsyncMock(return_value=[...])
```
Mock принимает ЛЮБЫЕ аргументы без проверки сигнатуры. Тесты зелёные, production падает.

Это прямое следствие EXP-041 (MagicMock без spec) — но здесь проблема ещё коварнее: даже `MagicMock(spec=CatalogDB)` не поможет если spec создан ДО рефакторинга и не обновлён.

## Корневая причина
Рефакторинг метода без grep по всем call sites. Изменили `def get_bestsellers(self, limit=10)` но не обновили `await db.get_bestsellers(days=30)` в 3 handlers.

## Правило
После ЛЮБОГО изменения сигнатуры метода — обязательный checklist:

1. **Grep all callers:**
```bash
grep -rn "get_bestsellers" --include="*.py" .
grep -rn "get_card_cross_sell" --include="*.py" .
```

2. **Обновить ВСЕ call sites** — не только код, но и тесты

3. **Проверить mock specs:**
```python
# ПЛОХО — mock не проверяет сигнатуру
mock_db.get_bestsellers = AsyncMock(return_value=[...])

# ХОРОШО — spec привязан к РЕАЛЬНОМУ классу
mock_db = MagicMock(spec=CatalogDB)
# Теперь mock выбросит AttributeError на несуществующие методы
# и TypeError на неправильные аргументы (при вызове)
```

4. **Integration test** — хотя бы один тест должен вызывать метод с реальной DB (не mock), чтобы проверить сигнатуру end-to-end

## Связь с другими EXP
- **EXP-040:** Dataclass attribute mismatch — тот же класс проблем (имена не совпадают)
- **EXP-041:** MagicMock без spec скрывает баги — прямая причина
- **EXP-065:** Singleton + attribute rename + MagicMock = silent failure — тройная комбинация

## Мнемоника
**"Refactor method = grep callers"** — рефакторинг метода без grep по callers = гарантированный runtime crash.

## times_applied: 1
