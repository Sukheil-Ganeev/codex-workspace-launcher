# W001: JSON теряет данные при падении

**Severity:** HIGH
**Дата:** 2026-02-05
**Источник:** Проект Туризм-ОАЭ

---

## Проблема

При использовании JSON для массового парсинга:

```python
# ОПАСНО
results = []
for item in items:
    results.append(process(item))
with open("out.json", "w") as f:
    json.dump(results, f)  # Если упадёт — потеря ВСЕГО!
```

## Решение

JSONL (JSON Lines) — каждая запись сразу на диск:

```python
# БЕЗОПАСНО
with open("out.jsonl", "a", encoding="utf-8") as f:
    for item in items:
        result = process(item)
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        # Каждая запись сразу сохранена!
```

## Сравнение

| Критерий | JSON | JSONL |
|----------|------|-------|
| При падении | Потеря ВСЕГО | Потеря 1 записи |
| Память | O(n) | O(1) |
| Добавление | Перезапись файла | Append |
| Чтение | Всё сразу | Построчно |

## Правило

> Для массовой обработки (>100 записей) — ТОЛЬКО JSONL

---

**Теги:** #jsonl #формат #надёжность
