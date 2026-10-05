# I002: SQLite FTS5 для полнотекстового поиска

**Impact:** HIGH
**Дата:** 2026-02-12
**Источник:** Фаза I-II аналитика — поиск по 880K сообщений

---

## Задача

Обеспечить мгновенный полнотекстовый поиск по всем данным: текстовые сообщения, транскрипции голосовых, OCR-тексты, PDF-тексты. Итого 773K записей.

## Сравнение

| Метод | Индексация | Поиск | RAM |
|-------|-----------|-------|-----|
| grep по JSONL (401 MB) | — | ~30-60 сек | ~500 MB |
| Python in-memory dict | ~120 сек | ~1-5 сек | ~2 GB |
| **SQLite FTS5** | **~120 сек** | **<0.1 сек** | **~50 MB** |
| Elasticsearch | ~300 сек | <0.1 сек | ~2 GB+ |

SQLite FTS5 — оптимальный выбор: скорость Elasticsearch, RAM grep'a, zero dependencies.

## Реализация

### Создание индекса

```python
import sqlite3
import json

conn = sqlite3.connect("search_index.db")
conn.execute("PRAGMA journal_mode=WAL")  # WAL mode для производительности

conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
        chat_folder,
        sender,
        datetime,
        text,
        source_type,  -- 'text' | 'voice' | 'ocr' | 'pdf'
        content=messages,
        tokenize='unicode61'
    )
""")

# Batch INSERT по 5000 строк
batch = []
with open("all_messages_enriched.jsonl", "r") as f:
    for line in f:
        msg = json.loads(line)
        batch.append((
            msg.get("chat_folder", ""),
            msg.get("sender", ""),
            msg.get("datetime", ""),
            msg.get("text", ""),
            "text",
        ))
        if len(batch) >= 5000:
            conn.executemany(
                "INSERT INTO messages_fts VALUES (?, ?, ?, ?, ?)",
                batch
            )
            batch.clear()

if batch:
    conn.executemany("INSERT INTO messages_fts VALUES (?, ?, ?, ?, ?)", batch)

conn.commit()
```

### Поиск

```python
def search(query, limit=50):
    conn = sqlite3.connect("search_index.db")
    cursor = conn.execute("""
        SELECT chat_folder, sender, datetime,
               snippet(messages_fts, 3, '>>>', '<<<', '...', 64) as snippet
        FROM messages_fts
        WHERE messages_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit))
    return cursor.fetchall()

# Использование:
results = search("сафари пустыня")  # <0.1 сек
```

## Метрики

| Метрика | Значение |
|---------|----------|
| Записей в индексе | 773,423 |
| Размер search_index.db | 322 MB |
| Время индексации | ~2 мин |
| Время поиска | <0.1 сек |
| Источники | text (880K) + voice (50K) + ocr (59K) + pdf (9.8K) |

## Ключевые настройки

- **WAL mode** — параллельное чтение/запись, 2-3x быстрее для записи
- **Batch INSERT по 5000** — оптимальный баланс RAM/скорость
- **unicode61 tokenizer** — корректная работа с русским и арабским текстом
- **snippet()** — выделение найденного фрагмента с контекстом

---

**Теги:** #sqlite #fts5 #поиск #производительность #индексация
