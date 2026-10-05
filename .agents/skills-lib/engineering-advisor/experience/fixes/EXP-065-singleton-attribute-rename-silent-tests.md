# EXP-065: Singleton + attribute rename breaks tests silently (MagicMock without spec)

**Тип:** fix
**Severity:** critical
**Проект:** Spy Bot v4 (MLCR Leads Bot)
**Дата:** 2026-02-28

## Проблема

При апгрейде Spy Bot v3 -> v4 (Wave 0D) в `AIClient.__init__` переименовали `_gemini_model` в `_gemini_client`. Все тесты остались зелёными. В production path — `AttributeError: 'AIClient' object has no attribute '_gemini_model'`.

## Корневая причина

1. `AIClient` — Singleton (один экземпляр, `__new__` + `_initialized` guard)
2. В `conftest.py` тесты использовали `MagicMock()` **без `spec=AIClient`**
3. MagicMock без spec возвращает новый MagicMock на ЛЮБОЙ атрибут — включая `_gemini_model` (уже не существующий)
4. Тесты обращались к `mock._gemini_model` → MagicMock молча создавал атрибут → тест зелёный
5. Реальный код обращался к `self._gemini_client` → работал корректно
6. Но другой код (не покрытый тестами с real instance) всё ещё использовал `_gemini_model` → `AttributeError`

## Почему это EXP-040 + EXP-041 одновременно

- **EXP-040** (dataclass attribute mismatch): переименование атрибута создаёт рассинхронизацию между определением и использованием
- **EXP-041** (MagicMock без spec): mock скрывает рассинхронизацию, тесты зелёные при битом коде

Singleton усугубляет проблему: один экземпляр шарится, и если mock создан первым — реальный `__init__` не вызывается повторно.

## Решение

```bash
# После ЛЮБОГО переименования атрибута:
grep -r "_gemini_model" tests/     # Найти ВСЕ упоминания старого имени
grep -r "_gemini_model" core/      # Найти ВСЕ упоминания в бизнес-коде
# Заменить все на новое имя
```

## Превентивные меры

1. **`MagicMock(spec=AIClient)`** — ловит обращение к несуществующему атрибуту сразу
2. **grep после rename** — `grep -r "old_attr" .` → fix ALL references
3. **Singleton reset в тестах** — `AIClient._instance = None` в teardown, чтобы каждый тест создавал fresh instance
4. **Интеграционный тест с реальным инстансом** — хотя бы один тест создаёт AIClient() без мока

## Чек-лист для будущих переименований

- [ ] `grep -r "old_name" .` по всему проекту
- [ ] Обновить ВСЕ тесты (не только те что упали)
- [ ] Проверить conftest.py на MagicMock без spec
- [ ] Для Singleton — проверить что `_initialized` guard не пропускает переименованные атрибуты

## Связанные уроки

- EXP-040: ВСЕГДА сверяй имена полей с определением
- EXP-041: MagicMock() без spec= скрывает баги
- EXP-042: Функции без тестов — баги живут неделями
