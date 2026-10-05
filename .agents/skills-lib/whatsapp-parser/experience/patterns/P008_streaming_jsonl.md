# P008: Потоковое чтение JSONL 401 MB

> Дата: 2026-02-12 | Контекст: Аналитика all_messages_enriched.jsonl (880K записей, 401 MB)

---

## Задача

Обработать all_messages_enriched.jsonl (880,257 записей, 401 MB) для построения индексов, графов и аналитики без исчерпания RAM.

## Правило

**НИКОГДА не грузить all_messages_enriched.jsonl целиком в память.**

Файл 401 MB в JSON-объектах занимает ~1.5-2 GB RAM после десериализации (dict overhead). На машине с 16 GB это приведёт к swap и замедлению в 10-100x.

## Решение: потоковое чтение

```python
import json
from collections import defaultdict

chats = defaultdict(list)

with open(jsonl_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        msg = json.loads(line)
        chat_folder = msg.get("chat_folder", "unknown")
        # Обработка на лету — НЕ копим все сообщения
        chats[chat_folder].append({
            "datetime": msg.get("datetime"),
            "sender": msg.get("sender"),
            "text": msg.get("text", "")[:200],  # Только нужные поля!
        })

        if (i + 1) % 50_000 == 0:
            print(f"  Прочитано {i + 1:,} записей, {len(chats):,} чатов")
```

## Batch INSERT для SQLite

При записи в SQLite — batch по 5000 строк:

```python
batch = []
for i, line in enumerate(f):
    msg = json.loads(line)
    batch.append((msg["chat_folder"], msg["datetime"], msg["text"]))

    if len(batch) >= 5000:
        cursor.executemany("INSERT INTO messages VALUES (?, ?, ?)", batch)
        batch.clear()

if batch:  # Остаток
    cursor.executemany("INSERT INTO messages VALUES (?, ?, ?)", batch)
conn.commit()
```

## Мониторинг

Progress каждые 50K записей:
```
  Прочитано 50,000 записей, 1,200 чатов
  Прочитано 100,000 записей, 1,850 чатов
  ...
  Прочитано 880,000 записей, 2,422 чатов
```

## Ключевые метрики

| Метрика | Значение |
|---------|----------|
| Размер файла | 401 MB |
| Записей | 880,257 |
| RAM при потоковом чтении | ~200-500 MB |
| RAM при json.load() | ~1.5-2 GB (недопустимо) |
| Скорость чтения | ~60 сек |

---

## Связанные записи

- [P009](P009_parallel_agents.md) — параллельные агенты для аналитики
- [W006](../warnings/W006_large_json_memory.md) — не грузить большие JSON целиком
