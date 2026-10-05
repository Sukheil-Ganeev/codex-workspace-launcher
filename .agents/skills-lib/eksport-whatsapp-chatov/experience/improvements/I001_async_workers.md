# I001: Async вместо threads для API запросов

**Severity:** HIGH
**Дата:** 2026-02-05
**Источник:** Чат 12321212.txt

---

## Сравнение

| Подход | Скорость | Сложность | Подходит для |
|--------|----------|-----------|--------------|
| Последовательно | ~650/час | Простая | <1000 файлов |
| ThreadPool (8) | ~2,000/час | Средняя | 1,000-10,000 |
| Async (16) | ~5,000+/час | Высокая | 10,000+ |

## Реализация

```python
import aiohttp
import asyncio

CONCURRENT_REQUESTS = 16

async def process_file(session, file_path, semaphore):
    async with semaphore:
        async with session.post(API_URL, data=...) as response:
            return await response.json()

async def main():
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession() as session:
        tasks = [process_file(session, f, semaphore) for f in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
```

## Риски

- **Rate limiting:** API может блокировать при высокой нагрузке
- **Решение:** Semaphore + exponential backoff

```python
async def process_with_retry(session, file_path, semaphore, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with semaphore:
                # ...
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 1, 2, 4 сек
            else:
                raise
```

---

**Теги:** #async #производительность #api #параллелизм
