---
name: lightpanda
description: "Управление Lightpanda - сверхлегкий headless-браузер для AI и автоматизации. Docker на порту 9222, Playwright/Puppeteer через CDP."
user-invocable: true
allowed-tools: Bash(docker *), Bash(python *)
---
# Lightpanda — Headless Browser for AI

Lightpanda — браузер, написанный с нуля на Zig специально для машин (не форк Chrome).
10x быстрее, 9x меньше памяти чем Chrome headless. Работает через Docker на порту 9222.

## Команды

Аргумент после `/lightpanda` определяет действие:

| Команда | Что делает |
|---------|------------|
| `/lightpanda start` | Запустить контейнер (создать если нет) |
| `/lightpanda stop` | Остановить контейнер |
| `/lightpanda status` | Проверить статус контейнера |
| `/lightpanda test` | Тест подключения через Playwright |
| `/lightpanda restart` | Перезапустить контейнер |
| `/lightpanda` (без аргументов) | Показать статус + справку |

## Выполнение команд

### Шаг 1 — Определи команду

Прочитай аргумент пользователя. Если аргумента нет — покажи статус и краткую справку.

### Шаг 2 — Выполни

<command name="start">
```bash
# Проверить, существует ли контейнер
docker ps -a --filter name=lightpanda --format "{{.Status}}"
```

Если контейнер существует и остановлен:
```bash
docker start lightpanda
```

Если контейнера нет:
```bash
docker run -d --name lightpanda -p 9222:9222 lightpanda/browser:nightly
```

Если контейнер уже запущен — сообщить что уже работает.

После запуска — подождать 2 секунды и проверить логи:
```bash
docker logs lightpanda 2>&1 | tail -5
```

Ожидаемый вывод: `server running address=0.0.0.0:9222`
</command>

<command name="stop">
```bash
docker stop lightpanda
```
Сообщить: "Lightpanda остановлен. Для повторного запуска: `/lightpanda start`"
</command>

<command name="status">
```bash
docker ps -a --filter name=lightpanda --format "Name: {{.Names}} | Status: {{.Status}} | Ports: {{.Ports}}"
```
Если пусто — контейнер не создан. Предложить `/lightpanda start`.
</command>

<command name="test">
Запустить Python-тест подключения:
```bash
python -c "
import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        print('[OK] Connected to Lightpanda on port 9222')
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://example.com')
        title = await page.title()
        print(f'[OK] Page loaded: {title}')
        result = await page.evaluate('() => navigator.userAgent')
        print(f'[OK] User-Agent: {result}')
        await page.close()
        await context.close()
        await browser.close()
        print('[DONE] Lightpanda works!')

asyncio.run(test())
"
```
Если ошибка подключения — предложить `/lightpanda start`.
</command>

<command name="restart">
```bash
docker restart lightpanda
```
Подождать 2 секунды, проверить логи.
</command>

## Интеграция с Playwright (Python)

### Подключение (вместо запуска Chrome)

```python
# БЫЛО (Chrome):
browser = await playwright.chromium.launch(headless=True)

# СТАЛО (Lightpanda):
browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
```

Весь остальной код (page.goto, page.content, page.evaluate) — без изменений.

### Подключение (Puppeteer / Node.js)

```javascript
import puppeteer from 'puppeteer-core';
const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222',
});
```

## Что умеет и чего НЕ умеет

| Возможность | Статус |
|-------------|--------|
| Загрузка страниц | OK |
| JavaScript (V8) | OK |
| Извлечение текста/HTML | OK |
| CSS-селекторы | OK |
| Навигация, клики | OK |
| Скриншоты | НЕТ (используй Chrome) |
| PDF-генерация | НЕТ (используй Chrome) |
| Полный визуальный рендеринг | НЕТ |

**Правило:** для `export_png.py` и любых задач со скриншотами — оставляй Chrome.
Lightpanda — только для парсинга, извлечения данных, автоматизации без визуала.

## Важно

- Docker Desktop должен быть запущен
- Порт 9222 не должен быть занят другим процессом
- Контейнер переживает перезагрузку Docker, но после перезагрузки ПК нужен `docker start lightpanda`
- Образ `lightpanda/browser:nightly` — обновлять периодически: `docker pull lightpanda/browser:nightly && docker rm -f lightpanda` + `/lightpanda start`
