# P002: Мониторинг каждые 3-5 минут

**Дата:** 2026-02-05
**Источник:** Проект Туризм-ОАЭ

---

## Проблема

Долгие операции могут "зависнуть" незаметно:
- Падение без ошибки
- Бесконечное ожидание
- Исчерпание лимитов

## Решение

### Bash-проверки

```bash
# Количество готовых файлов
ls результаты/*.jsonl | wc -l

# Размеры (не пустые ли?)
ls -la результаты/*.jsonl | tail -5

# Общее количество записей
wc -l результаты/*.jsonl | tail -1
```

### Встроенный прогресс

```python
import time

start = time.time()
for i, item in enumerate(items, 1):
    # обработка...

    if i % 100 == 0:
        elapsed = time.time() - start
        rate = i / elapsed * 3600
        remaining = (total - i) / (i / elapsed) / 60
        print(f"[{i}/{total}] {rate:.0f}/час, ~{remaining:.0f} мин осталось")
```

### Telegram-уведомления

```python
if processed % 500 == 0:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": f"Прогресс: {processed}/{total}"}
    )
```

---

**Теги:** #мониторинг #прогресс #уведомления
