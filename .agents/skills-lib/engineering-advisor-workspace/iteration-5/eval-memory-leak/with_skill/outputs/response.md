# Engineering Advisor — Анализ rate_limiter.py

**Запрос:** Добавить `check_ai_rate` — не более 3 запросов к AI в минуту на пользователя.

---

## Активация скилла

Engineering Advisor активирован. Файл `.py` с бизнес-логикой (триггеры #1, #3, #24).

---

## Анализ кода

```
=== Engineering Advisor ===

BLOCK (0): нет критических блокирующих проблем

WARN (1): rate_limiter.py — in-memory словари rate_limit_map и message_limit_map
          растут бесконечно. У бота 1000+ пользователей → через несколько дней
          накопятся тысячи мёртвых записей. Нет механизма очистки устаревших
          ключей. Триггер #24 — In-memory коллекции без cleanup.

INFO (2):
  [1] Три функции (message, voice, AI) используют одинаковый паттерн но с
      отдельными словарями. Дублирование кода — при следующем изменении логики
      придётся менять в трёх местах. Можно сделать одну универсальную функцию.

  [2] Новая функция check_ai_rate запрашивается добавить — код предоставлен ниже.

Опыт: применено 1 урок (триггер #24 — In-memory без cleanup)
===========================
```

---

## WARN: Утечка памяти — словари растут бесконечно

**Что происходит:** Каждый новый пользователь добавляет запись в `rate_limit_map` / `message_limit_map`. Записи никогда не удаляются. Через неделю работы бота словари могут содержать тысячи устаревших записей.

**Аналогия из скилла:** "Мусорка без вывоза — через месяц не войти."

**Решение — добавить periodic cleanup:**

```python
import threading

def _cleanup_maps():
    """Удаляет устаревшие записи из всех rate limit словарей"""
    now = datetime.now()
    for map_obj in [rate_limit_map, message_limit_map, ai_limit_map]:
        keys_to_delete = [k for k, v in map_obj.items() if now > v['reset_at']]
        for k in keys_to_delete:
            del map_obj[k]

def _start_cleanup_scheduler():
    """Запускает фоновую очистку каждые 5 минут"""
    _cleanup_maps()
    t = threading.Timer(300, _start_cleanup_scheduler)
    t.daemon = True
    t.start()

_start_cleanup_scheduler()
```

Вызвать `_start_cleanup_scheduler()` один раз при старте модуля — остальное происходит автоматически.

---

## INFO: Рекомендуемый рефакторинг (необязательно)

Три функции делают одно и то же. Можно вынести логику в одну:

```python
def _check_rate(map_obj: dict, user_id: int, limit: int) -> bool:
    """Универсальная проверка rate limit"""
    now = datetime.now()
    key = str(user_id)

    if key not in map_obj:
        map_obj[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    entry = map_obj[key]
    if now > entry['reset_at']:
        map_obj[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    if entry['count'] >= limit:
        return False

    entry['count'] += 1
    return True
```

Тогда все три функции становятся однострочными:
```python
def check_message_rate(user_id: int) -> bool:
    return _check_rate(message_limit_map, user_id, 10)

def check_voice_rate(user_id: int) -> bool:
    return _check_rate(rate_limit_map, user_id, 5)

def check_ai_rate(user_id: int) -> bool:
    return _check_rate(ai_limit_map, user_id, 3)
```

---

## Итоговый код — полный файл с исправлениями

```python
# rate_limiter.py
from datetime import datetime, timedelta
import threading

# Хранит счётчики запросов в памяти
rate_limit_map = {}       # voice (5/мин)
message_limit_map = {}    # сообщения (10/мин)
ai_limit_map = {}         # AI-запросы (3/мин)


def _check_rate(map_obj: dict, user_id: int, limit: int) -> bool:
    """Универсальная проверка rate limit: не более N запросов в минуту на пользователя"""
    now = datetime.now()
    key = str(user_id)

    if key not in map_obj:
        map_obj[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    entry = map_obj[key]
    if now > entry['reset_at']:
        map_obj[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    if entry['count'] >= limit:
        return False

    entry['count'] += 1
    return True


def check_message_rate(user_id: int) -> bool:
    """Проверяет: не более 10 сообщений в минуту на пользователя"""
    return _check_rate(message_limit_map, user_id, 10)


def check_voice_rate(user_id: int) -> bool:
    """Проверяет: не более 5 голосовых в минуту"""
    return _check_rate(rate_limit_map, user_id, 5)


def check_ai_rate(user_id: int) -> bool:
    """Проверяет: не более 3 запросов к AI в минуту на пользователя"""
    return _check_rate(ai_limit_map, user_id, 3)


# --- Периодическая очистка устаревших записей (каждые 5 минут) ---

def _cleanup_maps():
    """Удаляет устаревшие записи из всех rate limit словарей"""
    now = datetime.now()
    for map_obj in [rate_limit_map, message_limit_map, ai_limit_map]:
        keys_to_delete = [k for k, v in map_obj.items() if now > v['reset_at']]
        for k in keys_to_delete:
            del map_obj[k]


def _start_cleanup_scheduler():
    """Рекурсивный таймер: запускается раз в 5 минут, daemon-поток"""
    _cleanup_maps()
    t = threading.Timer(300, _start_cleanup_scheduler)
    t.daemon = True
    t.start()


_start_cleanup_scheduler()  # Запустить при импорте модуля
```

---

## Что изменено

| Изменение | Тип | Обязательно |
|-----------|-----|-------------|
| Добавлена `check_ai_rate` (3/мин) | Новая функция | Да (задача) |
| Добавлен `ai_limit_map` | Новый словарь | Да (нужен для функции) |
| Добавлен `_cleanup_maps` + scheduler | Исправление утечки памяти | Рекомендуется (WARN) |
| Вынесена `_check_rate` | Рефакторинг дублирования | Необязательно (INFO) |

---

## Что проверить вручную

- Вызов `check_ai_rate(user_id)` перед каждым обращением к AI в боте — добавить в соответствующий handler
- Убедиться что при `return False` бот отвечает пользователю понятным сообщением (напр. "Подождите минуту, вы превысили лимит")
- Если бот многопроцессорный (несколько воркеров) — in-memory лимиты не будут синхронизированы между процессами. Тогда нужен Redis

---

## Новый опыт для записи

Найден паттерн: при добавлении новой функции в класс rate-limiter без рефакторинга — каждый разработчик копирует паттерн вместе с багом (отсутствие cleanup). Задача стала поводом исправить накопленный долг.

Хотите записать это в опыт скилла Engineering Advisor?
(тип: warning, severity: medium, тег: memory-leak, in-memory-map)
