# P009: Параллельные агенты для аналитики

> Дата: 2026-02-12 | Контекст: Фаза I-II аналитика — 9 скриптов на 880K сообщений

---

## Задача

Запустить 9 аналитических скриптов максимально быстро. Некоторые независимы, некоторые зависят от результатов других.

## Граф зависимостей

```
Независимые (запускать параллельно):
  A1: analyze_quality_full.py
  A2: analyze_funnel.py
  A3: analyze_finance.py
  A4: search.py (FTS5 индексация)

Зависимые (после завершения зависимостей):
  B1: build_contact_graph_full.py  (независимый, но тяжёлый — лучше отдельно)
  B2: enrich_contacts.py           (после B1 для графовых метрик)
  B3: export_crm.py                (после B2 — нужен contacts_master_v2)
  B4: build_training_data.py       (после A1+A2 — нужны грейды и воронка)
  B5: update_summary.py            (после ВСЕХ — собирает итоги)
```

## Правила параллельных агентов

1. **4 независимых задачи (A1-A4) запускать одновременно** — каждый агент работает со своей копией данных
2. **Зависимые задачи запускать после завершения зависимостей** — B2 после B1, B3 после B2, B5 после всех
3. **Каждый агент: свой скрипт + свои выходные файлы** — нет конфликтов записи
4. **Не грузить большие файлы в память агента** — contact_graph_full.json (151 MB) передавать только путь

## Реализация

```python
# Агент 1 (A1-A4 параллельно):
import subprocess, concurrent.futures

independent = [
    ["python", "analyze_quality_full.py"],
    ["python", "analyze_funnel.py"],
    ["python", "analyze_finance.py"],
    ["python", "search.py"],
]

with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(subprocess.run, cmd): cmd for cmd in independent}
    for future in concurrent.futures.as_completed(futures):
        cmd = futures[future]
        print(f"Завершено: {cmd[1]}")

# Агент 2 (B1-B5 последовательно с зависимостями):
subprocess.run(["python", "build_contact_graph_full.py"])
subprocess.run(["python", "enrich_contacts.py"])
subprocess.run(["python", "export_crm.py"])
subprocess.run(["python", "build_training_data.py"])
subprocess.run(["python", "update_summary.py"])
```

## Результат

Общее время выполнения: ~15-20 мин (вместо ~40 мин последовательно).

---

## Связанные записи

- [P008](P008_streaming_jsonl.md) — потоковое чтение JSONL
- [W006](../warnings/W006_large_json_memory.md) — не грузить большие JSON целиком
