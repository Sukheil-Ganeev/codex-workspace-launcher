# I001: Async для API — 8x прирост скорости

**Impact:** HIGH
**Дата:** 2026-02-05
**Источник:** Проект Туризм-ОАЭ

---

## Сравнение

| Метод | Скорость | Время на 27k |
|-------|----------|--------------|
| Последовательно | ~650/час | ~42 часа |
| ThreadPool (8) | ~2,000/час | ~14 часов |
| **Async (16)** | ~5,000+/час | ~5-6 часов |

## Реализация

```python
import aiohttp
import asyncio

CONCURRENT = 16

async def process_one(session, file_path, semaphore):
    async with semaphore:
        async with session.post(API_URL, data=...) as resp:
            return await resp.json()

async def main():
    semaphore = asyncio.Semaphore(CONCURRENT)
    async with aiohttp.ClientSession() as session:
        tasks = [process_one(session, f, semaphore) for f in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
```

## Риски и решения

| Риск | Решение |
|------|---------|
| Rate limiting | Semaphore (16 concurrent) |
| Ошибки API | Exponential backoff |
| Потеря данных | JSONL + flush после каждой записи |

```python
async def with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
```

---

**Теги:** #async #производительность #api
