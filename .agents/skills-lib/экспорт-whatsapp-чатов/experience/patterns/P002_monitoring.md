# P002: Мониторинг каждые 3-5 минут

**Дата:** 2026-02-05
**Источник:** Чаты 12211221.txt, 121212.txt

---

## Проблема

Субагенты и скрипты могут "зависнуть" незаметно:
- Падение без сообщения об ошибке
- Бесконечное ожидание API
- Незаметное исчерпание лимитов

## Решение

### Для субагентов

Проверять статус каждые 3-5 минут:

```bash
# Сколько батчей готово
ls исправленные/batch_*.jsonl | wc -l

# Размеры файлов (не пустые ли)
ls -la исправленные/batch_*.jsonl | tail -10

# Общее количество записей
wc -l исправленные/batch_*.jsonl | tail -1
```

### Для скриптов

Встроенный прогресс-бар:

```python
import time

start_time = time.time()
for i, file in enumerate(files, 1):
    # ... обработка ...

    if i % 50 == 0:
        elapsed = time.time() - start_time
        rate = i / elapsed * 3600
        remaining = (total - i) / rate * 60
        print(f"[{i}/{total}] {rate:.0f}/час, осталось ~{remaining:.0f} мин")
```

### Автоматические уведомления

```python
def notify_progress(current, total, chat_id=TELEGRAM_CHAT_ID):
    if current % 500 == 0:
        msg = f"Прогресс: {current}/{total} ({current/total*100:.1f}%)"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": msg})
```

---

**Теги:** #мониторинг #прогресс #уведомления
