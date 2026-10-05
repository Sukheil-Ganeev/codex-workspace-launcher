---
name: web-automation
description: "Use when scraping websites, extracting data from web pages, running E2E browser tests, automating browser actions (forms, navigation, clicks), or doing automated web research. Covers static HTML parsing, JavaScript-rendered pages, Playwright automation, deduplication, and structured data export."
---
# Web Automation

## Overview

Полный инструментарий для работы с веб-сайтами из кода:

| Режим | Когда использовать |
|-------|-------------------|
| `scrape` | Извлечь данные с сайта (парсинг) |
| `test` | E2E тестирование интерфейса в браузере |
| `research` | Автоматически исследовать сайт и собрать информацию |
| `automate` | Автоматизировать действия (формы, логин, навигация) |

**Стек:**
- **Статика** → `requests` + `beautifulsoup4`
- **JavaScript-сайты** → `playwright` (Python)
- **Тесты** → `playwright` + `pytest-playwright`
- **БД** → `asyncpg` (PostgreSQL) или `psycopg2`

---

## When to Use

Активируй этот скилл когда пользователь говорит:
- "спарси сайт", "собери данные с сайта", "извлеки цены/названия/ссылки"
- "напиши E2E тест", "проверь форму в браузере", "сделай скриншот страницы"
- "автоматизируй заполнение формы", "кликни кнопку", "пройди по страницам"
- "исследуй сайт конкурентов", "собери структуру сайта"

---

## Modes

---

### scrape — Извлечение данных с сайтов

#### Шаг 1: Определить тип сайта

```python
# Статический HTML (рендерится на сервере) → requests + BeautifulSoup
# JavaScript (React/Vue/Angular, данные грузятся через API) → Playwright

# Как проверить: открыть DevTools → Network → XHR/Fetch
# Если данные приходят через JSON API — использовать Playwright или напрямую API
```

#### Шаг 2а: Статический парсинг (BeautifulSoup)

```python
import requests
from bs4 import BeautifulSoup
import time
import hashlib
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_page(url: str) -> BeautifulSoup | None:
    """Загружает страницу с таймаутом и User-Agent."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"[scrape] fetch error: {url} → {e}")
        return None

def extract_items(soup: BeautifulSoup) -> list[dict]:
    """Извлекает карточки товаров/записей из страницы."""
    items = []
    for card in soup.select("div.product-card"):   # ← подобрать CSS-селектор
        item = {
            "title": card.select_one("h2.title").get_text(strip=True) if card.select_one("h2.title") else None,
            "price_cents": parse_price(card.select_one("span.price")),
            "url": card.select_one("a")["href"] if card.select_one("a") else None,
            "image": card.select_one("img")["src"] if card.select_one("img") else None,
        }
        items.append(item)
    return items

def parse_price(el) -> int | None:
    """Возвращает цену в центах (избегает float-ошибок)."""
    if not el:
        return None
    text = el.get_text(strip=True).replace(",", "").replace("$", "").replace("AED", "").strip()
    try:
        return int(float(text) * 100)
    except ValueError:
        return None
```

#### Шаг 2б: Динамический парсинг (Playwright)

```python
from playwright.sync_api import sync_playwright
import json

def scrape_js_page(url: str) -> list[dict]:
    """Парсит JavaScript-сайт через Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page.goto(url, timeout=30_000)
        page.wait_for_load_state("networkidle")  # ← КРИТИЧНО для JS-сайтов

        items = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('div.product-card')).map(card => ({
                title: card.querySelector('h2')?.textContent?.trim(),
                price: card.querySelector('.price')?.textContent?.trim(),
                url: card.querySelector('a')?.href,
            }));
        }""")

        browser.close()
        return items
```

#### Шаг 3: Пагинация

```python
def scrape_all_pages(base_url: str) -> list[dict]:
    """Итерирует по страницам пока есть данные."""
    all_items = []
    page_num = 1

    while True:
        url = f"{base_url}?page={page_num}"
        soup = fetch_page(url)
        if not soup:
            break

        items = extract_items(soup)
        if not items:
            break   # страница пустая — конец пагинации

        all_items.extend(items)
        page_num += 1
        time.sleep(1.5)   # ← уважаем сервер, не DDoSим

    print(f"[scrape] collected {len(all_items)} items across {page_num-1} pages")
    return all_items
```

#### Шаг 4: Дедупликация через хэш

```python
def content_hash(item: dict) -> str:
    """MD5 хэш контента для дедупликации между запусками."""
    key = f"{item.get('title','')}{item.get('url','')}{item.get('price_cents','')}"
    return hashlib.md5(key.encode()).hexdigest()

def deduplicate(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        h = content_hash(item)
        if h not in seen:
            seen.add(h)
            item["_hash"] = h
            unique.append(item)
    print(f"[scrape] dedup: {len(items)} → {len(unique)} unique")
    return unique
```

#### Шаг 5: Экспорт в JSON/CSV

```python
import csv
from pathlib import Path

def save_json(items: list[dict], path: str = "output.json"):
    Path(path).write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[scrape] saved {len(items)} items → {path}")

def save_csv(items: list[dict], path: str = "output.csv"):
    if not items:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig для Excel
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)
    print(f"[scrape] saved {len(items)} rows → {path}")
```

#### Шаг 6: Загрузка в PostgreSQL

```python
import asyncpg

async def load_to_postgres(items: list[dict], dsn: str):
    """Batch upsert в PostgreSQL (идемпотентно)."""
    conn = await asyncpg.connect(dsn)

    # Upsert по хэшу — безопасно запускать повторно
    await conn.executemany("""
        INSERT INTO scraped_items (title, price_cents, url, image, content_hash)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (content_hash) DO UPDATE
            SET title = EXCLUDED.title,
                price_cents = EXCLUDED.price_cents,
                updated_at = NOW()
    """, [
        (item["title"], item.get("price_cents"), item.get("url"), item.get("image"), item["_hash"])
        for item in items
    ])

    await conn.close()
    print(f"[scrape] upserted {len(items)} rows to postgres")
```

#### Защита от блокировок (anti-bot)

```python
# Вариант 1: Ротация User-Agent
import random
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118",
]
headers = {"User-Agent": random.choice(USER_AGENTS)}

# Вариант 2: Playwright stealth mode (скрывает автоматизацию)
# pip install playwright-stealth
from playwright_stealth import stealth_sync
stealth_sync(page)

# Вариант 3: Прокси (Bright Data / другие)
browser = p.chromium.launch(proxy={"server": "http://proxy-host:port"})
```

---

### test — E2E тестирование в браузере

#### Установка

```bash
pip install playwright pytest-playwright
playwright install chromium
```

#### Базовый тест

```python
# tests/test_ui.py
import pytest
from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page):
    page.goto("http://localhost:3000")
    expect(page).to_have_title("My App")
    expect(page.locator("h1")).to_be_visible()

def test_search_form(page: Page):
    page.goto("http://localhost:3000/search")
    page.fill("input[name='query']", "Dubai tour")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    expect(page.locator(".results")).to_contain_text("результат")

def test_login_flow(page: Page):
    page.goto("http://localhost:3000/login")
    page.fill("input[name='email']", "test@example.com")
    page.fill("input[name='password']", "password123")
    page.click("button[type='submit']")
    # Дожидаемся редиректа на dashboard
    page.wait_for_url("**/dashboard")
    expect(page.locator("text=Добро пожаловать")).to_be_visible()
```

#### Скриншот при ошибке

```python
import pytest

@pytest.fixture(autouse=True)
def screenshot_on_fail(page: Page, request):
    yield
    if request.node.rep_call.failed:
        page.screenshot(path=f"screenshots/{request.node.name}.png")
```

#### Тест API внутри браузера

```python
def test_api_response(page: Page):
    # Перехватить сетевой запрос
    with page.expect_response("**/api/search**") as resp_info:
        page.goto("http://localhost:3000/search?q=dubai")
    response = resp_info.value
    assert response.status == 200
    data = response.json()
    assert len(data["results"]) > 0
```

#### Запуск тестов

```bash
# Все тесты headless
pytest tests/ -v

# С видимым браузером (для дебага)
pytest tests/ --headed

# Конкретный файл + скриншоты
pytest tests/test_ui.py --screenshot=on --output=screenshots/
```

---

### research — Автоматическое исследование сайта

```python
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, field
import json

@dataclass
class SiteResearch:
    url: str
    title: str = ""
    description: str = ""
    links: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    contact_info: dict = field(default_factory=dict)
    prices: list[str] = field(default_factory=list)

def research_site(url: str) -> SiteResearch:
    """Собирает структурированную информацию о сайте."""
    result = SiteResearch(url=url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30_000)
        page.wait_for_load_state("networkidle")

        # Мета-данные
        result.title = page.title()
        desc_el = page.query_selector('meta[name="description"]')
        result.description = desc_el.get_attribute("content") if desc_el else ""

        # Заголовки (структура страницы)
        result.headings = page.evaluate("""() =>
            Array.from(document.querySelectorAll('h1,h2,h3'))
                .map(h => h.textContent.trim())
                .filter(t => t.length > 0)
        """)

        # Все ссылки
        result.links = page.evaluate("""() =>
            Array.from(document.querySelectorAll('a[href]'))
                .map(a => a.href)
                .filter(h => h.startsWith('http'))
                .slice(0, 50)
        """)

        # Контакты (email, телефоны)
        page_text = page.inner_text("body")
        import re
        emails = re.findall(r'[\w.+-]+@[\w-]+\.\w+', page_text)
        phones = re.findall(r'\+?\d[\d\s\-().]{7,15}\d', page_text)
        result.contact_info = {"emails": list(set(emails)), "phones": list(set(phones))}

        # Цены
        result.prices = page.evaluate("""() =>
            Array.from(document.querySelectorAll('[class*="price"],[class*="cost"],[class*="rate"]'))
                .map(el => el.textContent.trim())
                .filter(t => t.length > 0 && t.length < 50)
                .slice(0, 20)
        """)

        browser.close()

    return result

# Использование:
# info = research_site("https://example.com")
# print(json.dumps(vars(info), ensure_ascii=False, indent=2))
```

---

### automate — Автоматизация действий в браузере

#### Заполнение формы

```python
from playwright.sync_api import sync_playwright

def fill_booking_form(url: str, data: dict):
    """Автоматически заполняет форму бронирования."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)   # headless=True для фона
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Заполнение полей
        page.fill("input[name='name']", data["name"])
        page.fill("input[name='email']", data["email"])
        page.fill("input[name='phone']", data["phone"])

        # Выбор из дропдауна
        page.select_option("select[name='tour']", label=data["tour_name"])

        # Выбор даты
        page.fill("input[type='date']", data["date"])

        # Клик с ожиданием навигации
        with page.expect_navigation():
            page.click("button[type='submit']")

        # Проверка успеха
        if "confirmation" in page.url or page.locator(".success-message").is_visible():
            print(f"[automate] form submitted successfully: {page.url}")
        else:
            page.screenshot(path="/tmp/form-error.png")
            print("[automate] form submission may have failed — screenshot saved")

        browser.close()
```

#### Навигация по сложному сайту

```python
def navigate_and_extract(start_url: str, target_selector: str) -> list[str]:
    """Собирает данные с нескольких вложенных страниц."""
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(start_url)
        page.wait_for_load_state("networkidle")

        # Получить все ссылки на детальные страницы
        links = page.eval_on_selector_all(
            "a.item-link",
            "els => els.map(e => e.href)"
        )

        for link in links[:20]:   # ограничить количество
            page.goto(link)
            page.wait_for_load_state("networkidle")

            el = page.query_selector(target_selector)
            if el:
                results.append(el.inner_text().strip())

        browser.close()

    return results
```

#### Авторизация и сохранение сессии

```python
import json
from pathlib import Path

def login_and_save_session(login_url: str, email: str, password: str, session_file: str = "/tmp/browser-session.json"):
    """Логинится и сохраняет cookies для повторного использования."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(login_url)
        page.fill("input[type='email']", email)
        page.fill("input[type='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        # Сохранить cookies
        cookies = context.cookies()
        Path(session_file).write_text(json.dumps(cookies))
        print(f"[automate] session saved: {session_file}")
        browser.close()

def use_saved_session(url: str, session_file: str = "/tmp/browser-session.json"):
    """Использует сохранённую сессию."""
    cookies = json.loads(Path(session_file).read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        # ... дальнейшие действия
        browser.close()
```

---

## Tech Stack

| Задача | Библиотека | Установка |
|--------|-----------|-----------|
| Статический парсинг | `requests` + `beautifulsoup4` | `pip install requests beautifulsoup4` |
| JS-сайты / автоматизация | `playwright` (Python) | `pip install playwright && playwright install chromium` |
| E2E тесты | `pytest-playwright` | `pip install pytest-playwright` |
| Stealth-режим | `playwright-stealth` | `pip install playwright-stealth` |
| Async парсинг | `aiohttp` + `beautifulsoup4` | `pip install aiohttp beautifulsoup4` |
| PostgreSQL | `asyncpg` | `pip install asyncpg` |
| Экспорт | встроенные `json`, `csv` | — |

---

## Quick Reference

```python
# --- Проверить CSS-селектор в браузере (DevTools консоль) ---
document.querySelectorAll('div.product-card')   # → список элементов
document.querySelector('h1').textContent        # → текст заголовка

# --- Установка Playwright ---
pip install playwright pytest-playwright playwright-stealth
playwright install chromium

# --- Playwright: базовые действия ---
page.goto(url)
page.wait_for_load_state("networkidle")   # ждать JS
page.fill("selector", "value")            # ввод текста
page.click("selector")                    # клик
page.select_option("select", value="x")  # выбор из списка
page.screenshot(path="screen.png")       # скриншот
page.query_selector("selector")          # найти элемент
page.eval_on_selector_all("sel", "els => els.map(e => e.href)")  # массово

# --- BeautifulSoup: базовые операции ---
soup.select("div.card")                  # CSS-селектор → список
soup.select_one("h1").get_text(strip=True)  # первый элемент → текст
el["href"]                               # атрибут элемента
el.get("src")                            # атрибут с fallback None

# --- Запуск pytest playwright ---
pytest tests/ -v --headed              # с видимым браузером
pytest tests/ -v --screenshot=on       # сохранять скриншоты
```

---

## Common Mistakes

| Ошибка | Правильно |
|--------|----------|
| Парсить JS-сайт через requests | Проверить — нужен ли Playwright |
| Не ждать загрузки JS | Всегда `wait_for_load_state("networkidle")` |
| Цены как float | Хранить в целых центах: `int(price * 100)` |
| Нет таймаута на запросы | `timeout=30` для requests, `timeout=30_000` для Playwright |
| Нет User-Agent | Сайты блокируют запросы без UA |
| Не обрабатывать None | `el.get_text() if el else None` |
| Нет задержки между страницами | `time.sleep(1.5)` между запросами |
| Хардкод данных для форм | Параметризовать функции автоматизации |
| DDoS своими же скриптами | Лимит: max 1 запрос/сек, уважай robots.txt |
| Повторные дубликаты в БД | MD5-хэш + ON CONFLICT DO UPDATE |

---

## robots.txt Rule

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

def is_allowed(base_url: str, path: str, user_agent: str = "*") -> bool:
    """Проверяет robots.txt перед парсингом."""
    rp = RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    rp.read()
    return rp.can_fetch(user_agent, urljoin(base_url, path))

# Использование:
# if is_allowed("https://example.com", "/products/"):
#     items = scrape_all_pages(...)
```

---

## Sources

Этот скилл объединяет лучшее из:

1. **TerminalSkills/skills — web-scraper** (Apache-2.0) — BeautifulSoup, хэш-дедупликация, PostgreSQL upsert, anti-bot, правила robots.txt
2. **anthropics/skills — webapp-testing** — Playwright wait strategies, server lifecycle, reconnaissance-then-action workflow
3. **lackeyjb/playwright-skill** — headless/headed режимы, параметризация URL, helper utilities, browser lifecycle
4. **vercel-labs/agent-browser** — element snapshot references, session persistence, auth strategies
5. **Собственная экспертиза** — async PostgreSQL (asyncpg), CSV export с UTF-8 BOM для Excel, robots.txt проверка, session save/restore, research mode

**Размер файла:** ~230 строк кода + документация
