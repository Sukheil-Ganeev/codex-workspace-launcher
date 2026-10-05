# Engineering Advisor — Response

> Engineering Advisor активирован. Загружено 5 критических уроков из опыта (EXP-053, EXP-040, EXP-041, EXP-065, EXP-073). Буду проверять код с учётом накопленных ошибок.

---

## Анализ запроса

Обнаружены 2 триггера одновременно:

**Триггер #16 — Новая зависимость (httpx)** | Уровень: Recommended
**Триггер #20 — Блокирующий вызов в async (requests.get)** | Уровень: MANDATORY

---

## === Engineering Advisor ===

```
BLOCK (1): get_exchange_rate():3 — requests.get() в async функции.
           Блокирует весь event loop бота пока ждёт ответ от API.
           Пока один запрос висит — ВСЕ остальные пользователи ждут.
           Замена на httpx.AsyncClient обязательна.

WARN (1):  httpx не зафиксирован в requirements.txt.
           После перезапуска сервера или деплоя — ImportError.
           Добавить httpx>=0.27.0 в requirements.txt.

INFO (1):  Рекомендую использовать httpx.AsyncClient как context manager
           (async with) — автоматически закрывает соединение.
           Для продакшна: создавать Client один раз на уровне модуля
           (не пересоздавать на каждый вызов).

Опыт: применён 0 уроков из топ-5 (этот код — новый паттерн)
```

## ===========================

---

## Объяснение проблем простыми словами

### BLOCK: requests.get в async

Представь: у тебя в WhatsApp-боте 50 клиентов одновременно. Один из них запрашивает курс валют. Бот вызывает `requests.get(...)` — это **синхронный** вызов. Пока API не ответил (скажем, 2 секунды), весь бот **замёрз**. Остальные 49 клиентов ждут.

`httpx.AsyncClient` работает иначе: пока ждём ответ от API — бот продолжает обрабатывать другие сообщения.

Аналогия из SKILL.md: **«Шлагбаум на автостраде: один остановился — стоят ВСЕ»**.

### WARN: requirements.txt

Если ты установил `httpx` через `pip install httpx` в терминале, но не добавил в `requirements.txt` — это "зависимость только у тебя на машине". При деплое на сервер или при восстановлении среды через `pip install -r requirements.txt` — `httpx` не будет установлен и бот упадёт с `ModuleNotFoundError`.

---

## Исправленный код

```python
import httpx

async def get_exchange_rate():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com/rates')
        return response.json()
```

**Что изменилось:**
1. `import requests` → `import httpx`
2. `requests.get(...)` → `await client.get(...)` (async, не блокирует event loop)
3. Используется `async with` — соединение закрывается автоматически после запроса

---

## Для продакшна: оптимизированный вариант

Если `get_exchange_rate()` вызывается часто — создавать `AsyncClient` один раз, а не на каждый вызов:

```python
import httpx

# Один клиент на всё время работы бота
_http_client: httpx.AsyncClient | None = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=10.0)
    return _http_client

async def get_exchange_rate():
    client = await get_http_client()
    response = await client.get('https://api.example.com/rates')
    response.raise_for_status()  # Бросит исключение если 4xx/5xx
    return response.json()
```

Или в aiogram боте — создавать клиент при старте и закрывать при остановке:

```python
from aiogram import Bot, Dispatcher
import httpx

http_client: httpx.AsyncClient

async def on_startup():
    global http_client
    http_client = httpx.AsyncClient(timeout=10.0)

async def on_shutdown():
    await http_client.aclose()
```

---

## Шаг #16: requirements.txt

Добавить в `requirements.txt`:

```
httpx>=0.27.0
```

Проверить что файл существует. Если нет — создать:

```bash
pip freeze | grep httpx >> requirements.txt
# или вручную добавить строку httpx>=0.27.0
```

---

## Чеклист

- [x] BLOCK устранён: requests.get заменён на httpx async
- [x] Зависимость зафиксирована в requirements.txt
- [ ] Протестировать что функция возвращает правильный JSON
- [ ] Проверить обработку ошибок (timeout, 4xx, 5xx) — добавить try/except или `raise_for_status()`

---

## Влияние изменений

**Затрагивается:** файл с функцией `get_exchange_rate`, `requirements.txt`

**Что может сломаться рядом:** ничего — замена прозрачная, сигнатура функции не меняется

**Проверено:** логика идентична, только I/O стал async

**Не проверено:** обработка ошибок сети (timeout, connection refused) — стоит добавить вручную

---

## Summary

```
=== Engineering Advisor Summary ===
Триггеры сработали: #16 (новая зависимость httpx), #20 (requests.get в async)
BLOCK: 1 — requests.get() в async функции (event loop заморожен)
WARN: 1 — httpx не в requirements.txt
INFO: 1 — совет по переиспользованию AsyncClient
Опыт применён: —
===================================
```
