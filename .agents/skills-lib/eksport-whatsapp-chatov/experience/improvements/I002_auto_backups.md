# I002: Автоматические бэкапы каждые N файлов

**Severity:** MEDIUM
**Дата:** 2026-02-05
**Источник:** Чат 12321212.txt

---

## Проблема

Длительные операции (часы) могут прерваться:
- Сбой питания
- Ошибка API
- Системная ошибка
- Закрытие терминала

## Решение

Автобэкап каждые 100-200 файлов:

```python
import shutil
from datetime import datetime

BACKUP_INTERVAL = 100
processed_count = 0

def process_file(file_path):
    global processed_count

    # ... обработка ...

    processed_count += 1
    if processed_count % BACKUP_INTERVAL == 0:
        create_backup()

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"results_backup_{timestamp}.jsonl"
    shutil.copy2("results.jsonl", backup_name)
    print(f"[BACKUP] Создан: {backup_name}")
```

## Структура папки

```
output/
├── results.jsonl           # Основной файл
├── results_backup_20260205_103000.jsonl
├── results_backup_20260205_110000.jsonl
└── results_backup_20260205_120000.jsonl
```

## Очистка старых бэкапов

```python
def cleanup_old_backups(max_keep=5):
    backups = sorted(glob.glob("results_backup_*.jsonl"))
    for old in backups[:-max_keep]:
        os.remove(old)
```

---

**Теги:** #бэкап #надежность #recovery
