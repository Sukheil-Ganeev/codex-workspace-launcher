# F002: Проверка дубликатов при массовой обработке

**Severity:** HIGH
**Дата:** 2026-02-05
**Источник:** Чат 12321212.txt

---

## Проблема

При повторном запуске скрипта файлы обрабатываются заново:
- Потеря времени и API квоты
- Дубликаты в результатах
- Некорректная статистика

## Решение

Использовать составной ключ для уникальной идентификации:

```python
# Загрузка уже обработанных
processed_files = set()
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            key = (data['chat_folder'], data['media_path'], data.get('source', ''))
            processed_files.add(key)

# При обработке
for audio_file in audio_files:
    file_key = (chat_folder, audio_file.name, source_name)
    if file_key in processed_files:
        skipped += 1
        continue  # ПРОПУСТИТЬ

    # Обработка...
    processed_files.add(file_key)
```

## Важно

| Одно поле | Проблема |
|-----------|----------|
| Только filename | Одинаковые имена в разных чатах |
| Только chat | Много файлов в одном чате |
| Только path | Разные источники (Personal/Business) |

**Правильный ключ:** `(chat_folder, filename, source)`

---

**Теги:** #дубликаты #ключи #идемпотентность
