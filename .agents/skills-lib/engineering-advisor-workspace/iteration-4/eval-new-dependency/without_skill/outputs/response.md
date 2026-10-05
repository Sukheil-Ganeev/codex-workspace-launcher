# Переход с requests на httpx

## Что нужно сделать

`requests` — синхронная библиотека, она блокирует event loop в async-коде. `httpx` поддерживает async через `AsyncClient`, что правильно для asyncio-ботов.

## Установка

```bash
pip install httpx
```

## Переписанный код

```python
import httpx

async def get_exchange_rate():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com/rates')
        response.raise_for_status()
        return response.json()
```

## Что изменилось

| До | После |
|----|-------|
| `import requests` | `import httpx` |
| `requests.get(...)` | `await client.get(...)` |
| Синхронный вызов (блокирует loop) | Асинхронный вызов (не блокирует) |
| Нет явной обработки HTTP-ошибок | `raise_for_status()` — бросает исключение при 4xx/5xx |

## Важные детали

**AsyncClient как контекстный менеджер** — `async with httpx.AsyncClient() as client:` автоматически закрывает соединение. Это предпочтительный способ для одиночных запросов.

**Если делаешь много запросов** — лучше создать клиент один раз на уровне модуля или при старте бота, чтобы переиспользовать connection pool:

```python
import httpx

_client: httpx.AsyncClient | None = None

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient()
    return _client

async def get_exchange_rate():
    client = await get_client()
    response = await client.get('https://api.example.com/rates')
    response.raise_for_status()
    return response.json()

async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None
```

**Обработка ошибок** — httpx бросает `httpx.HTTPStatusError` при `raise_for_status()` и `httpx.RequestError` при сетевых проблемах:

```python
async def get_exchange_rate():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('https://api.example.com/rates')
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP ошибка: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            print(f"Сетевая ошибка: {e}")
            raise
```
