---
name: claude-in-chrome-справочник
description: "Skill claude-in-chrome-справочник"
version: "1.0"
created: "2026-02-16"
---
# Claude in Chrome + Extensions: Production-Ready Справочник

> **Версия:** 1.0 | **Дата:** 2026-02-16 | **Статус:** Beta (Chrome), Beta (Excel), Research Preview (PowerPoint)

## Триггеры активации

Этот справочник активируется при любом из:
- Запросы про **Claude in Chrome**, side panel, расширение для браузера
- Работа с **`claude --chrome`**, **`/chrome`**, MCP-инструменты браузера
- Автоматизация браузера: клики, формы, навигация, скриншоты, GIF
- **Chrome DevTools MCP** — `evaluate_script`, `take_screenshot`, performance tracing
- **Claude in Excel** / **Claude in PowerPoint** — add-in, sidebar
- **Office Skills CLI** — `pptx`, `xlsx`, `docx`, `pdf` через Claude Code
- Web-редакторы: `innerHTML`, Selection API, contenteditable, PuzzleBot

---

## Быстрый старт

```bash
# 1. Установить расширение
# Chrome Web Store → "Claude" by Anthropic → Add to Chrome

# 2. Запуск через CLI
claude --chrome                    # с флагом
/chrome                            # внутри сессии Claude Code
/chrome → "Enabled by default"     # включить постоянно (осторожно: +19k токенов)

# 3. Первый вызов — ВСЕГДА:
tabs_context_mcp(createIfEmpty=true)  # получить свежие tab ID

# 4. Навигация:
navigate(url="https://example.com")
```

**Требования:** Chrome/Edge, расширение >= 1.0.36, Claude Code >= 2.0.73, платный план (Pro/Max/Team/Enterprise). НЕ работает: Brave, Arc, WSL, Bedrock/Vertex/Foundry.

**Что НЕ поддерживается в Chrome-расширении:** Projects, внешние MCP connections, cross-session memory, финансовые сервисы, adult/pirated контент.

---

## 01. Обзор экосистемы

Экосистема Claude + Browser/Office включает 5 продуктов:

| Продукт | Тип | Планы | Статус | Дата |
|---------|-----|-------|--------|------|
| **Claude in Chrome** (side panel) | Расширение | Pro, Max, Team, Enterprise | Beta | 18.12.2025 (все планы) |
| **Claude Code + Chrome** | CLI + MCP | Pro, Max, Team, Enterprise | Beta | 18.12.2025 |
| **Claude in Excel** | Office Add-in | Pro, Max, Team, Enterprise | Beta | 24.01.2026 (Pro) |
| **Claude in PowerPoint** | Office Add-in | Max, Team, Enterprise (НЕ Pro!) | Research Preview | 05.02.2026 |
| **Office Skills CLI** | SKILL.md + Python/Node | Любой с Claude Code | Stable | — |

**Модели по планам:**

| План | Chrome | Excel / PowerPoint |
|------|--------|-------------------|
| Pro ($17-20/мес) | Haiku 4.5 только | Sonnet 4.5, Opus 4.6 |
| Max (от $100/мес) | Opus 4.6, Sonnet 4.5, Haiku 4.5 | Opus 4.6, Sonnet 4.5 |
| Team / Enterprise | Opus 4.6, Sonnet 4.5, Haiku 4.5 | Opus 4.6, Sonnet 4.5 |

**Хронология Chrome:** 26.08.2025 (1000 Max) → 24.11.2025 (все Max) → 18.12.2025 (все платные).

**Два режима работы:**
1. **Side Panel** (расширение) — чат в боковой панели, шорткаты "/", scheduled tasks, запись workflow
2. **Claude Code + Chrome** (CLI) — `claude --chrome`, 18 MCP-инструментов, комбинирование код + браузер

**ВНИМАНИЕ:** Claude Desktop Cowork и Claude Code конфликтуют за один extension ID. Используйте только одно из двух одновременно (см. раздел 13).

---

## 02. MCP-инструменты Claude in Chrome (18 tools)

> Полный каталог с параметрами: `references/mcp-tools-catalog.md`

| # | Tool | Назначение | Ключевые параметры |
|---|------|-----------|-------------------|
| 1 | `computer` | Мышь, клавиатура, скриншоты (13 actions) | action, tabId, coordinate/ref, text, modifiers |
| 2 | `navigate` | Навигация по URL, назад/вперед | url, action (goto/back/forward) |
| 3 | `tabs_context_mcp` | Контекст вкладок (ВСЕГДА первый!) | createIfEmpty |
| 4 | `tabs_create_mcp` | Создание вкладки | url |
| 5 | `read_page` | Чтение DOM (accessibility_tree / html) | tabId, format |
| 6 | `get_page_text` | Извлечение текста страницы | tabId |
| 7 | `find` | Поиск элементов по тексту | text, exact_match, tabId |
| 8 | `form_input` | Заполнение форм | selector, value, action, tabId |
| 9 | `javascript_tool` | Выполнение JS на странице | action="javascript_exec", text, tabId |
| 10 | `read_console_messages` | Консоль (regex-фильтр) | pattern, onlyErrors, limit, clear, tabId |
| 11 | `read_network_requests` | Сетевые запросы (URL-фильтр) | urlPattern, limit, clear, tabId |
| 12 | `gif_creator` | Запись GIF (4 actions) | action, tabId, download, filename, options |
| 13 | `upload_image` | Загрузка изображения | imageId, tabId, ref/coordinate, filename |
| 14 | `resize_window` | Размер окна | width, height, tabId |
| 15 | `shortcuts_list` | Список шорткатов | (нет параметров) |
| 16 | `shortcuts_execute` | Выполнение шортката | shortcut_name |
| 17 | `update_plan` | Обновление плана | plan_text |
| 18 | `switch_browser` | Переключение браузера | browser_name |

### computer tool — 13 actions (ИСПРАВЛЕНО: НЕ 15!)

| Action | Описание | Обязательные |
|--------|----------|-------------|
| `left_click` | Клик ЛКМ | tabId, coordinate/ref |
| `right_click` | Правый клик | tabId, coordinate |
| `double_click` | Двойной клик | tabId, coordinate |
| `triple_click` | Тройной клик | tabId, coordinate |
| `type` | Ввод текста | tabId, text |
| `key` | Горячая клавиша | tabId, text (напр. "ctrl+b"), repeat(1-100) |
| `screenshot` | Скриншот viewport | tabId |
| `scroll` | Прокрутка | tabId, coordinate, scroll_direction, scroll_amount(1-10) |
| `scroll_to` | Прокрутка к элементу | tabId, ref |
| `left_click_drag` | Перетаскивание | tabId, start_coordinate, coordinate |
| `hover` | Наведение курсора | tabId, coordinate/ref |
| `zoom` | Увеличение области | tabId, region [x0,y0,x1,y1] |
| `wait` | Пауза | tabId, duration (макс. 30 сек) |

**Модификаторы кликов:** `modifiers: "ctrl"/"shift"/"alt"/"cmd"/"win"`, комбинации через `+`.

### gif_creator — 4 actions (ИСПРАВЛЕНО)

| Action | Описание | Параметры |
|--------|----------|-----------|
| `start_recording` | Начать запись | tabId |
| `stop_recording` | Остановить запись | tabId |
| `export` | Экспорт GIF | tabId, download=true, filename, options |
| `clear` | Сброс кадров | tabId |

**Options (export):** showClickIndicators, showDragPaths, showActionLabels, showProgressBar, showWatermark (все bool, default true), quality (1-30, default 10).

**Параметра `output_path` НЕ СУЩЕСТВУЕТ.** Используйте `download: true` + `filename`.

---

## 03. Chrome DevTools MCP (26 tools)

> Полный каталог: `references/mcp-tools-catalog.md` | Сравнительная таблица ниже

**Установка:**
```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest"]
  }
}
```

### Сравнительная таблица: Claude in Chrome vs Chrome DevTools MCP

| Функция | Claude in Chrome | Chrome DevTools MCP |
|---------|-----------------|-------------------|
| Навигация | `navigate(url, action)` | `navigate_page(url, back/forward/reload)` |
| Клик | `computer(left_click, coordinate)` | `click(uid, dblClick)` |
| Заполнение форм | `form_input(selector, value)` | `fill(uid, value)` / `fill_form(fields)` |
| JS-выполнение | `javascript_tool` (выражение) | `evaluate_script` (функция + uid args) |
| Скриншот viewport | `computer(screenshot)` | `take_screenshot()` |
| Скриншот full-page | Нет | `take_screenshot(fullPage: true)` |
| Скриншот элемента | `zoom(region)` | `take_screenshot(uid)` |
| DOM snapshot | `read_page(accessibility_tree)` | `take_snapshot(verbose, filePath)` |
| Консоль | `read_console_messages` (regex) | `list_console_messages` (20 типов) |
| Сеть | `read_network_requests` (URL) | `list_network_requests` (19 resource types) |
| GIF-запись | `gif_creator` | Нет |
| Upload | `upload_image` (screenshot) | `upload_file(filePath)` |
| Диалоги | Нет (ручной dismiss) | `handle_dialog(accept/dismiss)` |
| Performance | Нет | `performance_start/stop_trace`, `performance_analyze_insight` |
| Эмуляция | Нет | `emulate(viewport, geolocation, network, cpuThrottling)` |
| Горячие клавиши | `computer(key)` | `press_key(key)` |
| Ожидание | `computer(wait, duration)` | `wait_for(text, timeout)` |

**Когда какой использовать:**
- **Claude in Chrome** — авторизованные сайты (cookies), шорткаты, GIF, формы, side panel
- **Chrome DevTools MCP** — performance tracing, network debugging, headless, full-page screenshots, handle_dialog, эмуляция

---

## 04. Навигация, вкладки и DOM

### Паттерн навигации
```
1. tabs_context_mcp(createIfEmpty=true)    → свежие tab IDs
2. navigate(url="https://...")             → перейти
3. read_page(format="accessibility_tree")  → прочитать DOM
4. find(text="Кнопка")                     → найти элемент
5. computer(left_click, ref=...)           → взаимодействовать
```

### Tab Groups
- **Side panel:** перетащить вкладки в группу Claude
- **Claude Code:** автоматически "Claude (MCP)" через `tabs_context_mcp`
- **Проблема:** Tab groups НЕ удаляются после сессии. Закрывайте вручную (правый клик → Close group)

### read_page: accessibility_tree vs html

| Критерий | accessibility_tree | html |
|----------|-------------------|------|
| Содержимое | Семантическая структура с UID | Полный HTML-код |
| Размер | Большой | Очень большой |
| Для взаимодействия | Лучший (UID для кликов) | Средний (CSS-селекторы) |
| Для парсинга данных | Средний | Лучший |

### Фоновая работа
Claude продолжает работу при переключении вкладок пользователем (пока Chrome открыт). CAPTCHA и логин — Claude паузится и просит пользователя.

---

## 05. Взаимодействие с элементами и формы

### form_input vs computer

| Сценарий | Инструмент |
|----------|-----------|
| Стандартные HTML-формы | `form_input` (быстрее, надежнее) |
| Custom UI (React, Vue) | `computer` (визуальный клик) |
| Dropdown с поиском | `computer` click + type |
| Web-редакторы (contenteditable) | JS injection (`javascript_tool`) |
| Чекбоксы/радио | `form_input` или `computer` |

### Загрузка файлов
`upload_image` работает ТОЛЬКО с ранее сделанными скриншотами (imageId). Для файлов с диска используйте Chrome DevTools MCP `upload_file(filePath)`.

### Координатная система
- Кликать в ЦЕНТР элемента
- Перед кликом ВСЕГДА screenshot для определения координат
- `ref` (из read_page/find) надежнее координат

---

## 06. JavaScript injection и DOM-манипуляции

### javascript_tool (Claude in Chrome)
```javascript
// Синтаксис: выражение без return, результат — последнее выражение
javascript_tool(action="javascript_exec", text="document.title", tabId=TAB)
```

### evaluate_script (Chrome DevTools MCP)
```javascript
// Синтаксис: функция с return, аргументы через uid
evaluate_script(function="(el) => { return el.innerText; }", args=[{uid: "3_21"}])
```

### Ключевые паттерны

**innerHTML injection** — мгновенная вставка HTML в редакторы:
```javascript
document.querySelector('.editor').innerHTML = '<p>Текст с <strong>жирным</strong></p>'
```

**Selection API** — программное выделение текста:
```javascript
const range = document.createRange();
const sel = window.getSelection();
range.setStart(textNode, 0);
range.setEnd(textNode, 12);
sel.removeAllRanges();
sel.addRange(range);
```

### Ограничения
- **НИКОГДА** не вызывать `alert()`, `confirm()`, `prompt()` — блокируют ВСЕ события
- `evaluate_script` не поддерживает early lifecycle injection (page load)
- HTTP-only cookies недоступны через JS injection
- Для отладки: `console.log()` + `read_console_messages`

---

## 07. Шорткаты, запись workflow и планирование

### 3 способа создания шорткатов
1. **Save Prompt** — наведение на сообщение → иконка сохранения
2. **Convert to Task** — в заголовке беседы после выполнения workflow
3. **Record Workflow** — иконка курсора → выполнить задачу → Claude генерирует шорткат (голосовые комментарии!)

### Вызов: "/" в чате → выбрать шорткат

### Scheduled Tasks
- Частоты: daily, weekly, monthly, annually
- Настройка: иконка часов при создании/редактировании шортката
- **Требование:** Chrome должен быть открыт

### MCP-инструменты
- `shortcuts_list` — список всех шорткатов (без параметров)
- `shortcuts_execute(shortcut_name)` — выполнить шорткат
- `update_plan(plan_text)` — обновить план в side panel

### Клавиатурные шорткаты через MCP
```
computer(action="key", text="ctrl+b", tabId=TAB)     # Claude in Chrome
press_key(key="Control+B")                             # Chrome DevTools MCP
```

---

## 08. Паттерны и рецепты

> Подробные пошаговые рецепты: `references/workflow-recipes.md`

### Паттерн: Web-редактор (PuzzleBot) — ПРОВЕРЕН 2x

```
1. innerHTML injection → весь HTML разом (с {{переменными}}, <p>, <br>)
2. Конвейер: JS Selection API → горячая клавиша (Ctrl+B/I) — подряд без пауз
3. Для кнопочных действий: screenshot → клик по кнопке на панели
4. Одна JS-проверка: innerHTML.includes('<strong>')
5. Один финальный screenshot
```
**Результат:** ~10 действий вместо 30+. Экономия 60-70%.

**Критические баги PuzzleBot:**
- `Ctrl+Shift+M` СЛОМАН — вводит "m". Решение: кнопка `</>` на панели
- `{{переменные}}` ломаются при обычном вводе. Решение: innerHTML injection

### Паттерн: Batch processing
```
CSV → navigate CRM → form_input для каждой строки → checkpoint каждые 25 записей
```

### Паттерн: Coding + Browser
```
Claude Code → правка кода → navigate localhost:3000 → read_console_messages → screenshot → fix → verify
```

### Паттерн: Excel → PowerPoint pipeline
Обработать данные в Claude in Excel → визуализировать в Claude in PowerPoint.

### Паттерн: GIF для документирования
```
gif_creator(start_recording) → screenshot (первый кадр!) → действия + screenshots →
screenshot (последний кадр!) → gif_creator(stop_recording) → gif_creator(export, download=true)
```

---

## 09. Claude in Excel (add-in)

> Подробное руководство: `references/office-addins.md`

| Параметр | Значение |
|----------|---------|
| Статус | Beta |
| Планы | Pro, Max, Team, Enterprise |
| Горячая клавиша | Ctrl+Alt+C (Win) / Ctrl+Option+C (Mac) |
| Форматы | .xlsx, .xlsm |

**Возможности:** Анализ с cell-level цитатами, трассировка формул, отладка #REF!/#VALUE!, pivot tables, conditional formatting, графики, финансовое моделирование (DCF, LBO, SaaS metrics), drag & drop файлов, auto-compaction, overwrite protection.

**7 финансовых коннекторов:** Aiera, Third Bridge, Chronograph, Egnyte, LSEG, Moody's, MT Newswires.

**6 Agent Skills:** Comparable Company, DCF, Due Diligence, Company Teasers, Earnings Analyses, Coverage Reports.

**Ограничения:** No VBA/macros, no Data tables, no persistent chat history, no audit logs, no Compliance API.

**Claude Log Tab:** Опциональный лист с записью всех действий Claude (единственный audit trail).

---

## 10. Claude in PowerPoint (add-in)

> Подробное руководство: `references/office-addins.md`

| Параметр | Значение |
|----------|---------|
| Статус | Research Preview |
| Планы | Max, Team, Enterprise (**НЕ Pro!**) |
| Лимит | ~1000 пользователей с расширением |
| Дата запуска | 05.02.2026 |

**Template Intelligence:** Чтение slide master (layouts, fonts, color schemes) → автоматическое соблюдение корпоративного брендинга.

**Возможности:** Генерация слайдов из текста, нативные редактируемые графики (НЕ статичные картинки), конвертация буллетов в диаграммы, точечные правки без регенерации.

**Ограничения:** No Pro, no chat history, no audit logs, no Compliance API.

---

## 11. Claude Code Office Skills (CLI)

Набор SKILL.md для Claude Code — программный подход к созданию/редактированию Office-файлов.

| Формат | Библиотеки | Ключевые возможности |
|--------|-----------|---------------------|
| **PPTX** | python-pptx, pptxgenjs, markitdown | HTML→PPTX, шаблоны, thumbnail, XML editing |
| **XLSX** | openpyxl, pandas, LibreOffice | Формулы, форматирование, color coding, recalc.py |
| **DOCX** | python-docx | Tracked changes, структурные модификации |
| **PDF** | Poppler, Pandoc, LibreOffice | Формы, слияние, конвертация, извлечение |

**Установка:**
```bash
/plugin marketplace add anthropics/skills
```

**Add-in vs CLI:**
- **Add-in** — интерактивный, sidebar, один файл, нужен план Max/Team/Enterprise (для PPT)
- **CLI** — программный, batch-обработка, любое количество файлов, любой план с Claude Code

---

## 12. Безопасность, разрешения и admin-контроль

### Модель разрешений
- **Ask before acting** — Claude создает план → пользователь утверждает → автономная работа в рамках плана
- **Act without asking** — автономно, но высокорисковые действия ВСЕГДА требуют подтверждения
- **Высокорисковые:** покупки, публикации, передача персональных данных

### Prompt injection
- **Chrome:** 123 тест-кейса, 29 сценариев. ASR: 23.6% → 11.2% после mitigations. Свежий бенчмарк: 1% ASR (Opus 4.5, Best-of-N, 100 попыток)
- **Excel:** Скрытые инструкции в ячейках/формулах/комментариях. Защищенные функции требуют pop-up подтверждения (WEBSERVICE, DDE, IMPORTDATA и др.)
- **PowerPoint:** Скрытые инструкции в файлах
- **Рекомендация:** Использовать ТОЛЬКО с доверенными файлами и сайтами

### Admin-контроли (Team/Enterprise)
- Allowlist/blocklist сайтов через настройки расширения
- Deployment через Microsoft 365 Admin Center (для Office add-ins)
- **НО:** Add-in'ы НЕ наследуют Enterprise data retention settings, НЕ включены в Compliance API/audit logs

### Блокируемые категории (Chrome)
Финансовые сервисы, банки, криптобиржи, adult-контент, пиратские материалы.

### Уязвимости Desktop Extensions (DXT)
Koi Security обнаружили zero-click RCE уязвимость в Claude Desktop Extensions (10,000+ пользователей). Не путать с Chrome-расширением.

---

## 13. Troubleshooting и отладка

> Полная таблица ошибок: `references/troubleshooting.md`

| Ошибка | Причина | Решение |
|--------|---------|---------|
| "Browser extension is not connected" | Native messaging host | Перезапуск Chrome + Claude Code, `/chrome` reconnect |
| "Extension not detected" | Не установлено/отключено | chrome://extensions, перезапуск Chrome |
| "No tab available" | Вкладка не готова | `tabs_create_mcp` |
| "Receiving end does not exist" | Service worker заснул (~30 сек) | `/chrome` → Reconnect |
| EADDRINUSE (Windows) | Named pipe конфликт | Закрыть другие сессии Claude Code |
| Cowork + Code конфликт | Два native host для 1 extension ID | Отключить host неиспользуемого приложения |
| Alert блокирует | JS-диалоги | Не использовать alert(); dismiss вручную; DevTools: `handle_dialog` |

### Anti-rabbit-hole
Правило 2-3 попытки: после 3 неудач Claude останавливается и спрашивает пользователя. Не допускать бесконечные retry.

### Диагностика
```bash
claude doctor              # общая проверка
claude doctor --verbose    # детальные логи
claude doctor --mcp-debug  # диагностика MCP
claude mcp list            # подключенные серверы
```

---

## 14. Примеры для туризма ОАЭ

### Мониторинг цен конкурентов
```
Промпт: "Открой GetYourGuide, Viator и Klook. Найди Desert Safari Dubai
на каждом сайте. Собери цены, рейтинги и количество отзывов в CSV."
```
Шорткат: `/competitor-scan` → scheduled: ежедневно, 08:00

### Автоматизация CRM
```
Промпт: "Открой CRM. Для каждого клиента из bookings.csv заполни форму
бронирования: имя, email, тип экскурсии, дата, количество гостей."
```
Batch processing: checkpoint каждые 25 записей.

### Excel: Расчет себестоимости туров
```
Промпт: "Проанализируй лист Cost_Analysis. Рассчитай маржинальность
каждой экскурсии с учетом: транспорт, гид, билеты, комиссия.
Добавь conditional formatting: зеленый >30%, красный <15%."
```

### PowerPoint: Презентация для корпоративного клиента
```
Промпт: "Создай 10-слайдовую презентацию для corporate event:
overview Дубая, опции экскурсий, пакеты яхт, VIP-трансферы,
pricing table, testimonials. Используй шаблон Paramount."
```

### GIF-инструкции для сотрудников
```
Промпт: "Запиши GIF-инструкцию: как заполнить форму бронирования
на partnersite.com. Покажи каждое поле и кнопку Submit."
```
→ `gif_creator` → файл для WhatsApp-рассылки сотрудникам.

### Комбинация Claude in Chrome + WhatsApp
Мониторинг бронирований через Chrome → формирование отчета → отправка через WhatsApp-справочник.

---

## Routing-таблица: какой инструмент для задачи

| Задача | Инструмент |
|--------|-----------|
| Заполнить форму на сайте | `form_input` (стандартная) / `computer` (custom UI) |
| Вставить текст в web-редактор | `javascript_tool` (innerHTML) |
| Отформатировать текст в редакторе | JS Selection API + `computer(key: "ctrl+b")` |
| Скриншот для проверки | `computer(screenshot)` / DevTools `take_screenshot` |
| Записать демо-GIF | `gif_creator(start_recording → stop_recording → export)` |
| Мониторинг API-вызовов | `read_network_requests(urlPattern)` |
| Performance profiling | DevTools `performance_start/stop_trace` |
| Отладка консоли | `read_console_messages(pattern, onlyErrors)` |
| Обработка alert/confirm | DevTools `handle_dialog` |
| Тестирование responsive | `resize_window` + `computer(screenshot)` |
| Создание Excel с формулами | CLI `xlsx` skill (openpyxl) |
| Создание презентации | CLI `pptx` skill (pptxgenjs) / PowerPoint add-in |

---

## Связанные справочники

- `whatsapp-справочник` — для комбинации browser + messaging (WhatsApp платформа)
- `whatsapp-bot-справочник` — для WhatsApp Bot / Business API
- `puzzlebot-справочник-unified` — для web-редакторов и Telegram-ботов (PuzzleBot)

## References

| Файл | Содержание |
|------|-----------|
| `references/mcp-tools-catalog.md` | Полный каталог 18 + 26 MCP tools с параметрами |
| `references/cheatsheet.md` | Шпаргалка: все инструменты, параметры, горячие клавиши |
| `references/office-addins.md` | Детальное руководство Excel + PowerPoint |
| `references/workflow-recipes.md` | Готовые рецепты автоматизации |
| `references/troubleshooting.md` | Таблица ошибок и решений |
| `references/faq.md` | Часто задаваемые вопросы |
| `experience/_index.md` | Критические уроки из реального опыта |
