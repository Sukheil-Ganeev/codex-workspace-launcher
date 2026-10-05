ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# Полный каталог MCP-инструментов

## Часть 1: Claude in Chrome MCP (18 инструментов)

Префикс: `mcp__claude-in-chrome__`

---

### 1. computer (13 actions)

**Назначение:** Универсальный инструмент взаимодействия — мышь, клавиатура, скриншоты, скролл.

| Action | Описание | Обязательные параметры | Опциональные |
|--------|----------|----------------------|-------------|
| `left_click` | Клик ЛКМ | tabId, coordinate [x,y] ИЛИ ref | modifiers |
| `right_click` | Правый клик | tabId, coordinate ИЛИ ref | modifiers |
| `double_click` | Двойной клик | tabId, coordinate ИЛИ ref | modifiers |
| `triple_click` | Тройной клик (выделение строки) | tabId, coordinate ИЛИ ref | modifiers |
| `type` | Ввод текста | tabId, text | — |
| `screenshot` | Скриншот viewport | tabId | — |
| `wait` | Пауза | tabId, duration (макс 30 сек) | — |
| `scroll` | Прокрутка | tabId, coordinate, scroll_direction (up/down/left/right) | scroll_amount (1-10, default 3) |
| `key` | Горячая клавиша | tabId, text (пробел-разделенные ключи) | repeat (1-100) |
| `left_click_drag` | Перетаскивание | tabId, start_coordinate, coordinate | — |
| `zoom` | Увеличение области | tabId, region [x0,y0,x1,y1] | — |
| `scroll_to` | Прокрутка к элементу | tabId, ref | — |
| `hover` | Наведение курсора | tabId, coordinate ИЛИ ref | — |

**Общие параметры:**
- `tabId` (number, required) — ID вкладки
- `modifiers` (string, optional) — "ctrl", "shift", "alt", "cmd"/"meta", "win"/"windows", комбинации через "+"

**Примеры:**
```
computer(action="left_click", tabId=123, coordinate=[500, 300])
computer(action="key", tabId=123, text="ctrl+b")
computer(action="screenshot", tabId=123)
computer(action="scroll", tabId=123, coordinate=[500, 400], scroll_direction="down", scroll_amount=5)
computer(action="zoom", tabId=123, region=[100, 200, 400, 350])
```

---

### 2. navigate

**Назначение:** Навигация по URL, управление историей.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| url | string | Да (для goto) | URL для перехода |
| action | string | Нет | "goto" (default), "back", "forward" |

```
navigate(url="https://example.com")
navigate(action="back")
```

---

### 3. tabs_context_mcp

**Назначение:** Получение контекста вкладок. **ВСЕГДА первый вызов в сессии!**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| createIfEmpty | boolean | Нет | Создать tab group если пуста |

---

### 4. tabs_create_mcp

**Назначение:** Создание новой вкладки.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| url | string | Да | URL для открытия |

---

### 5. read_page

**Назначение:** Чтение DOM-структуры страницы.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| tabId | number | Да | ID вкладки |
| format | string | Нет | "accessibility_tree" (default) или "html" |

---

### 6. get_page_text

**Назначение:** Извлечение видимого текста (без HTML-тегов).

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| tabId | number | Да | ID вкладки |

---

### 7. find

**Назначение:** Поиск элементов по тексту.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| text | string | Да | Текст для поиска |
| exact_match | boolean | Нет | Точное совпадение |
| tabId | number | Да | ID вкладки |

---

### 8. form_input

**Назначение:** Заполнение форм.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| selector | string | Да | CSS-селектор элемента |
| value | string | Да | Значение |
| action | string | Нет | Тип действия |
| tabId | number | Да | ID вкладки |

---

### 9. javascript_tool

**Назначение:** Выполнение JS в контексте страницы.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| action | string | Да | Всегда "javascript_exec" |
| text | string | Да | JS-код (без return! результат = последнее выражение) |
| tabId | number | Да | ID вкладки |

**НЕЛЬЗЯ:** alert(), confirm(), prompt() — блокируют ВСЕ события.

---

### 10. read_console_messages

**Назначение:** Чтение консоли браузера.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| tabId | number | Да | ID вкладки |
| pattern | string | Нет | Regex-паттерн фильтрации |
| onlyErrors | boolean | Нет | Только ошибки (default: false) |
| limit | number | Нет | Макс. сообщений (default: 100) |
| clear | boolean | Нет | Очистить после чтения (default: false) |

---

### 11. read_network_requests

**Назначение:** Чтение HTTP-запросов.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| tabId | number | Да | ID вкладки |
| urlPattern | string | Нет | Строковый фильтр по URL |
| limit | number | Нет | Макс. запросов (default: 100) |
| clear | boolean | Нет | Очистить после чтения (default: false) |

---

### 12. gif_creator (4 actions)

**Назначение:** Запись GIF-анимации взаимодействий.

| Action | Обязательные | Опциональные |
|--------|-------------|-------------|
| start_recording | tabId | — |
| stop_recording | tabId | — |
| export | tabId, download (=true) | filename, options |
| clear | tabId | — |

**Options (export):**

| Свойство | Тип | Default | Описание |
|----------|-----|---------|----------|
| showClickIndicators | bool | true | Оранжевые круги кликов |
| showDragPaths | bool | true | Красные стрелки drag |
| showActionLabels | bool | true | Подписи действий |
| showProgressBar | bool | true | Progress bar внизу |
| showWatermark | bool | true | Логотип Claude |
| quality | number | 10 | Сжатие (1-30, меньше = лучше) |

---

### 13. upload_image

**Назначение:** Загрузка скриншота/изображения на страницу.

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| imageId | string | Да | ID скриншота |
| tabId | number | Да | ID вкладки |
| ref | string | Нет | Reference ID элемента (ИЛИ coordinate) |
| coordinate | [x,y] | Нет | Координаты для drag & drop (ИЛИ ref) |
| filename | string | Нет | Имя файла (default: "image.png") |

---

### 14. resize_window

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| width | number | Да | Ширина в px |
| height | number | Да | Высота в px |
| tabId | number | Да | ID вкладки |

---

### 15. shortcuts_list

Без параметров. Возвращает список сохраненных шорткатов.

---

### 16. shortcuts_execute

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| shortcut_name | string | Да | Имя шортката |

---

### 17. update_plan

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| plan_text | string | Да | Текст плана |

---

### 18. switch_browser

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| browser_name | string | Да | Название браузера |

---

## Часть 2: Chrome DevTools MCP (26 инструментов)

Префикс: `mcp__plugin_chrome-devtools-mcp_chrome-devtools__`

**Установка:**
```json
{ "chrome-devtools": { "command": "npx", "args": ["-y", "chrome-devtools-mcp@latest"] } }
```

| # | Tool | Описание | Ключевые параметры |
|---|------|----------|-------------------|
| 1 | `click` | Клик по элементу | uid, dblClick |
| 2 | `close_page` | Закрыть страницу | pageId |
| 3 | `drag` | Перетащить элемент | from_uid, to_uid |
| 4 | `emulate` | Эмуляция устройства/сети | viewport, geolocation, network, colorScheme, cpuThrottling, userAgent |
| 5 | `evaluate_script` | Выполнить JS-функцию | function, args (uid элементов) |
| 6 | `fill` | Заполнить input/textarea/select | uid, value |
| 7 | `fill_form` | Заполнить несколько полей | fields (массив) |
| 8 | `get_console_message` | Получить сообщение консоли | msgid |
| 9 | `get_network_request` | Получить сетевой запрос | reqid, requestFilePath, responseFilePath |
| 10 | `handle_dialog` | Обработать browser dialog | accept/dismiss, promptText |
| 11 | `hover` | Наведение на элемент | uid |
| 12 | `list_console_messages` | Список консольных сообщений | types (20 enum), pageIdx, pageSize, includePreservedMessages |
| 13 | `list_network_requests` | Список сетевых запросов | resourceTypes (19 enum), pageIdx, pageSize, includePreservedRequests |
| 14 | `list_pages` | Список открытых страниц | — |
| 15 | `navigate_page` | Навигация | url, back/forward/reload, initScript, handleBeforeUnload, ignoreCache |
| 16 | `new_page` | Новая страница | url, background |
| 17 | `performance_analyze_insight` | Анализ Performance Insight | insightSetId, insightName |
| 18 | `performance_start_trace` | Начать performance trace | reload, autoStop, filePath |
| 19 | `performance_stop_trace` | Остановить trace | filePath |
| 20 | `press_key` | Нажать клавишу | key ("Control+A", "Enter"), includeSnapshot |
| 21 | `resize_page` | Размер страницы | width, height (макс 3840x2160) |
| 22 | `select_page` | Выбрать страницу | pageId, bringToFront |
| 23 | `take_screenshot` | Скриншот | format (png/jpeg/webp), fullPage, uid, quality, filePath |
| 24 | `take_snapshot` | A11y-tree snapshot | verbose, filePath |
| 25 | `upload_file` | Загрузить файл | uid, filePath |
| 26 | `wait_for` | Ожидание текста | text, timeout |

### Типы для list_console_messages
`log`, `debug`, `info`, `error`, `warn`, `dir`, `dirxml`, `table`, `trace`, `clear`, `startGroup`, `startGroupCollapsed`, `endGroup`, `assert`, `profile`, `profileEnd`, `count`, `timeEnd`, `verbose`, `issue`

### Типы ресурсов для list_network_requests
`document`, `stylesheet`, `image`, `media`, `font`, `script`, `texttrack`, `xhr`, `fetch`, `prefetch`, `eventsource`, `websocket`, `manifest`, `signedexchange`, `ping`, `cspviolationreport`, `preflight`, `fedcm`, `other`
