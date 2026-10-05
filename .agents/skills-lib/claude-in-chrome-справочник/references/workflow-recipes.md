ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# Готовые рецепты автоматизации

## Рецепт 1: Форматирование текста в web-редакторе (PuzzleBot) — ПРОВЕРЕН 2x

**Статус:** Проверен на практике 2 раза (2026-02-15)
**Применимость:** PuzzleBot, Notion, Google Docs, CMS с contenteditable

### Пошаговый workflow

```
Шаг 1: Вставить весь HTML через JS injection
  javascript_tool(action="javascript_exec", text="
    document.querySelector('.ql-editor').innerHTML = '<p>Текст с <strong>жирным</strong></p>'
  ", tabId=T)

Шаг 2: Для каждого фрагмента, требующего форматирования:
  a) Выделить через JS Selection API:
     javascript_tool(action="javascript_exec", text="
       const range = document.createRange();
       const sel = window.getSelection();
       const node = document.querySelector('.ql-editor p').firstChild;
       range.setStart(node, 0);
       range.setEnd(node, 12);
       sel.removeAllRanges();
       sel.addRange(range);
     ", tabId=T)

  b) Применить горячую клавишу:
     computer(action="key", tabId=T, text="ctrl+b")

Шаг 3: Для формата без рабочего шортката (напр. <code> в PuzzleBot):
  a) Выделить через JS Selection API (как выше)
  b) computer(action="screenshot", tabId=T)         # найти кнопку
  c) computer(action="left_click", tabId=T, coordinate=[X, Y])  # клик по </>

Шаг 4: Проверка одним вызовом JS:
  javascript_tool(action="javascript_exec", text="
    const html = document.querySelector('.ql-editor').innerHTML;
    JSON.stringify({
      bold: html.includes('<strong>'),
      italic: html.includes('<em>'),
      code: html.includes('<code>')
    })
  ", tabId=T)

Шаг 5: Один финальный скриншот
  computer(action="screenshot", tabId=T)
```

### Критические предупреждения
- `Ctrl+Shift+M` в PuzzleBot **СЛОМАН** — вводит "m"
- `{{переменные}}` ломаются при `computer(type)` — только innerHTML
- Панель форматирования "плавает" — screenshot перед КАЖДЫМ кликом
- Emoji исключать из Selection range при форматировании

---

## Рецепт 2: Массовый ввод данных в CRM

**Статус:** Из официальной документации Claude Code

### Workflow

```
Промпт:
"I have customer contacts in contacts.csv. For each row,
go to crm.example.com, click 'Add Contact', and fill in
name, email, phone. Confirm progress after every 25 contacts."

Шаги Claude:
1. Прочитать contacts.csv (Claude Code)
2. tabs_context_mcp → navigate(url="https://crm.example.com")
3. Для каждой строки CSV:
   a) find(text="Add Contact") → computer(left_click, ref=...)
   b) form_input(selector="#name", value="John Doe")
   c) form_input(selector="#email", value="john@example.com")
   d) form_input(selector="#phone", value="+971-50-123-4567")
   e) find(text="Save") → computer(left_click, ref=...)
4. Checkpoint каждые 25 записей
5. Финальный отчет: "Введено 150 из 150 контактов"
```

---

## Рецепт 3: Мониторинг цен конкурентов (туризм ОАЭ)

### Workflow

```
Промпт:
"Открой GetYourGuide, Viator и Klook в отдельных вкладках.
Найди 'Desert Safari Dubai' на каждом. Собери: цену, рейтинг,
количество отзывов. Сохрани в CSV."

Шаги:
1. tabs_context_mcp(createIfEmpty=true)
2. tabs_create_mcp(url="https://www.getyourguide.com")
3. tabs_create_mcp(url="https://www.viator.com")
4. tabs_create_mcp(url="https://www.klook.com")
5. Для каждой вкладки:
   a) find(text="search") → computer(left_click)
   b) computer(type, text="Desert Safari Dubai")
   c) computer(key, text="Enter")
   d) get_page_text → извлечь данные
6. Сформировать CSV через Claude Code
```

**Шорткат:** `/competitor-scan` → Schedule: daily, 08:00

---

## Рецепт 4: GIF-инструкция для сотрудников

### Workflow

```
1. resize_window(width=1280, height=720, tabId=T)
2. gif_creator(action="start_recording", tabId=T)
3. computer(action="screenshot", tabId=T)               # первый кадр
4. navigate(url="https://partner-booking.com/new")
5. computer(action="screenshot", tabId=T)
6. form_input(selector="#guest_name", value="Пример Имени")
7. computer(action="screenshot", tabId=T)
8. form_input(selector="#tour_type", value="Desert Safari")
9. computer(action="screenshot", tabId=T)
10. find(text="Submit") → computer(left_click)
11. computer(action="screenshot", tabId=T)              # последний кадр
12. gif_creator(action="stop_recording", tabId=T)
13. gif_creator(action="export", tabId=T,
      download=true,
      filename="booking_instruction.gif",
      options={quality: 5, showClickIndicators: true, showActionLabels: true})
```

---

## Рецепт 5: Coding + Browser debugging

### Workflow

```
Промпт:
"I just updated the login form. Open localhost:3000/login,
try submitting with empty fields, and check if validation works."

Шаги:
1. tabs_context_mcp → tabs_create_mcp(url="http://localhost:3000/login")
2. computer(screenshot) — визуальная проверка
3. find(text="Submit") → computer(left_click)
4. read_console_messages(onlyErrors=true) — проверка JS-ошибок
5. computer(screenshot) — проверка error messages
6. Отчет: "Валидация работает: показаны ошибки для 3 полей"
```

---

## Рецепт 6: Email management (Gmail)

### Workflow

```
Промпт:
"Open Gmail. Archive all promotional emails from last week.
Flag emails with 'urgent' or 'deadline' in subject.
Draft replies to unanswered emails from clients."

Шаги:
1. navigate(url="https://mail.google.com")
2. read_page — получить список писем
3. Для промо-писем: computer(left_click) → archive
4. Для срочных: flag
5. Для клиентских без ответа: draft reply (без отправки!)
```

**Claude имеет встроенное понимание Gmail** — навигация оптимизирована.

---

## Рецепт 7: Data extraction (парсинг таблиц)

### Workflow

```
Промпт:
"Go to the product page and extract all items: name, price, availability.
Save as CSV."

Шаги:
1. navigate(url="https://shop.example.com/products")
2. javascript_tool(text="
     JSON.stringify(
       Array.from(document.querySelectorAll('.product-card')).map(el => ({
         name: el.querySelector('.name').textContent.trim(),
         price: el.querySelector('.price').textContent.trim(),
         available: el.querySelector('.stock').textContent.includes('In Stock')
       }))
     )
   ")
3. Claude Code сохраняет результат в CSV
```

**Совет:** `javascript_tool` для точечного парсинга экономит контекст (vs read_page → полный DOM).

---

## Рецепт 8: Performance audit (Chrome DevTools MCP)

### Workflow

```
1. navigate_page(url="https://example.com")
2. performance_start_trace(reload=true, autoStop=true)
3. ... ожидание загрузки ...
4. performance_stop_trace(filePath="/tmp/trace.json")
5. performance_analyze_insight(insightSetId="...", insightName="LargestContentfulPaint")
6. take_screenshot(fullPage=true, filePath="/tmp/full_page.png")
7. Отчет с метриками Core Web Vitals
```

---

## Рецепт 9: Excel → PowerPoint pipeline (финансовый отчет)

### Workflow

```
Шаг 1 — Excel Add-in:
"Проанализируй Sales_Q4.xlsx. Создай сводку: revenue по регионам,
top-5 продуктов, YoY рост. Добавь conditional formatting."

Шаг 2 — PowerPoint Add-in:
"Создай 8-слайдовую презентацию из данных Excel:
Title, Executive Summary, Revenue by Region (bar chart),
Top Products (table), YoY Growth (line chart), Recommendations,
Next Steps, Appendix."
```

---

## Рецепт 10: Автоматизация расписания шорткатов

### Workflow

```
1. Создать шорткат /daily-bookings-report вручную или записью workflow
2. Протестировать 2-3 раза
3. Настроить Schedule:
   - Частота: ежедневно
   - Время: 09:00
   - Модель: Haiku 4.5 (для экономии)
4. Включить уведомления
5. Claude каждое утро:
   a) Открывает CRM
   b) Собирает бронирования за вчера
   c) Формирует сводку
   d) Уведомляет о результате
```

**Требование:** Chrome ДОЛЖЕН быть открыт в 09:00.
