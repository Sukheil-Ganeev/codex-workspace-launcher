# Lightpanda Cheatsheet

## Docker-команды

```bash
# Запустить (первый раз)
docker run -d --name lightpanda -p 9222:9222 lightpanda/browser:nightly

# Запустить (повторно, после перезагрузки)
docker start lightpanda

# Остановить
docker stop lightpanda

# Перезапустить
docker restart lightpanda

# Статус
docker ps --filter name=lightpanda

# Логи
docker logs lightpanda --tail 20

# Обновить образ
docker pull lightpanda/browser:nightly
docker rm -f lightpanda
docker run -d --name lightpanda -p 9222:9222 lightpanda/browser:nightly
```

## Python + Playwright

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    # Подключение к Lightpanda
    browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")

    context = await browser.new_context()
    page = await context.new_page()

    # Загрузить страницу
    await page.goto("https://example.com")

    # Получить HTML
    html = await page.content()

    # Выполнить JS
    result = await page.evaluate("() => document.title")

    # Извлечь текст
    text = await page.inner_text("h1")

    # Кликнуть
    await page.click("a.link")

    # Закрыть
    await page.close()
    await context.close()
    await browser.close()
```

## Node.js + Puppeteer

```javascript
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222',
});

const context = await browser.createBrowserContext();
const page = await context.newPage();

await page.goto('https://example.com');
const content = await page.content();

await page.close();
await context.close();
await browser.disconnect();
```

## Что работает / не работает

| Функция | Lightpanda | Chrome |
|---------|------------|--------|
| page.goto() | OK | OK |
| page.content() | OK | OK |
| page.evaluate() | OK | OK |
| page.click() | OK | OK |
| page.type() | OK | OK |
| page.screenshot() | НЕТ | OK |
| page.pdf() | НЕТ | OK |
| Полный рендеринг | НЕТ | OK |

## Порты

- Lightpanda CDP: `9222`
- InstaCovers dev server: `7777`
- InstaCovers backend: `8080`

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| Connection refused на 9222 | `docker start lightpanda` |
| Container not found | `docker run -d --name lightpanda -p 9222:9222 lightpanda/browser:nightly` |
| Port 9222 already in use | `docker rm -f lightpanda` и создать заново |
| Docker не запущен | Открыть Docker Desktop вручную |
