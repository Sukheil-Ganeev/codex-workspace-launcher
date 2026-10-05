# P001: Составной ключ для уникальной идентификации

**Дата:** 2026-02-05
**Источник:** Проект Туризм-ОАЭ

---

## Проблема

Одно поле не гарантирует уникальность:

| Ключ | Проблема |
|------|----------|
| Только filename | Одинаковые имена в разных чатах |
| Только chat_folder | Много файлов в одном чате |
| Только path | Разные источники (Personal/Business) |

## Решение

Составной ключ из 3 полей:

```python
file_key = (chat_folder, filename, source_name)

# Примеры:
# ("Марсель_971507705321", "audio_001.opus", "whatsapp_personal")
# ("Марсель_971507705321", "audio_001.opus", "whatsapp_business")
# Это РАЗНЫЕ записи!
```

## Реализация

```python
processed_keys = set()

# Загрузка существующих
with open(output_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        key = (data['chat_folder'], data['media_path'], data.get('source', ''))
        processed_keys.add(key)

# При обработке
for audio_file in audio_files:
    key = (chat_folder, audio_file.name, source)
    if key in processed_keys:
        skipped += 1
        continue

    # Обработка...
    processed_keys.add(key)
```

---

**Теги:** #ключи #уникальность #идемпотентность
