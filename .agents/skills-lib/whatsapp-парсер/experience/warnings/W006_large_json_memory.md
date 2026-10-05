# W006: Не грузить contact_graph_full.json (151 MB) целиком

> Дата: 2026-02-12 | Severity: HIGH

---

## Проблема

`json.load()` для contact_graph_full.json (151 MB) занимает несколько секунд и потребляет ~500 MB RAM (3x размер файла из-за Python dict/list overhead).

Аналогично для любых JSON >50 MB:
- `contact_graph_full.json` — 151 MB
- `all_messages_enriched.jsonl` — 401 MB (но это JSONL, не JSON)

## Масштаб проблемы

| Файл | Размер | RAM при json.load() | Время загрузки |
|------|--------|---------------------|----------------|
| contact_graph_full.json | 151 MB | ~500 MB | 3-5 сек |
| all_messages_enriched.jsonl | 401 MB | ~1.5-2 GB | Нельзя json.load()! |

## Решение 1: Загрузить и сразу удалить

Если нужна только статистика:

```python
import json

with open("contact_graph_full.json", "r") as f:
    data = json.load(f)

stats = {
    "total_nodes": len(data["nodes"]),
    "total_edges": len(data["edges"]),
}

del data  # Освободить ~500 MB RAM немедленно
import gc; gc.collect()
```

## Решение 2: Записывать statistics отдельно при генерации

**Лучший подход** — при создании графа записывать лёгкий файл statistics:

```python
# При генерации графа:
stats = {
    "total_nodes": G.number_of_nodes(),
    "total_edges": G.number_of_edges(),
    "clusters": len(clusters),
    "generated_at": datetime.now().isoformat(),
}

with open("contact_graph_stats.json", "w") as f:
    json.dump(stats, f, indent=2)
```

Потом читать только stats (< 1 KB) вместо полного графа (151 MB).

## Решение 3: Потоковый парсинг (ijson)

Для извлечения отдельных ключей без загрузки всего файла:

```python
import ijson

with open("contact_graph_full.json", "rb") as f:
    for node in ijson.items(f, "nodes.item"):
        # Обработка по одному узлу
        process(node)
```

## Правило

**Для JSON >50 MB: всегда думать, нужен ли весь файл. Если нет — загружать только нужное или использовать отдельный файл статистики.**

---

## Теги

#память #json #оптимизация #большие-файлы
