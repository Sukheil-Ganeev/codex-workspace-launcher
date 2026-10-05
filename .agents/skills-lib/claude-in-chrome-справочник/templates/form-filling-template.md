# Form Filling Template

## Назначение

Шаблон для автоматизации заполнения форм на веб-сайтах: CRM, системы бронирования, регистрационные формы, анкеты. Поддерживает как одиночное заполнение, так и batch-обработку из CSV.

**Когда использовать:**
- Массовый ввод данных в CRM (клиенты, бронирования)
- Заполнение регистрационных форм
- Автоматизация партнерских порталов бронирования
- Любые повторяющиеся формы с известными полями

## Шаги

### Шаг 1. Навигация к форме

```
tabs_context_mcp(createIfEmpty=true)
navigate(url="https://САЙТ.com/форма")
```

### Шаг 2. Идентификация полей

```
# Вариант A: через find (по тексту лейбла)
find(text="Имя", tabId=TAB_ID)
find(text="Email", tabId=TAB_ID)

# Вариант B: через read_page (полный список полей)
read_page(tabId=TAB_ID, format="accessibility_tree")

# Вариант C: через screenshot (для визуальной идентификации)
computer(action="screenshot", tabId=TAB_ID)
```

### Шаг 3. Заполнение полей

**Стандартные HTML-поля (input, select, textarea):**
```
form_input(selector="#name", value="Иван Петров", tabId=TAB_ID)
form_input(selector="#email", value="ivan@example.com", tabId=TAB_ID)
form_input(selector="#phone", value="+971-50-123-4567", tabId=TAB_ID)
```

**Dropdown (выпадающий список):**
```
form_input(selector="#country", value="UAE", action="select", tabId=TAB_ID)
```

**Чекбокс / радио-кнопка:**
```
form_input(selector="#agree_terms", value="true", tabId=TAB_ID)
```

**Custom UI (React, Vue — нестандартные компоненты):**
```
computer(action="left_click", coordinate=[X, Y], tabId=TAB_ID)
computer(action="type", text="Значение", tabId=TAB_ID)
```

**Дата-пикер:**
```
computer(action="left_click", coordinate=[X, Y], tabId=TAB_ID)  # открыть
computer(action="type", text="2026-03-15", tabId=TAB_ID)         # ввести дату
# или: навигация по календарю через клики
```

### Шаг 4. Верификация перед отправкой

```
computer(action="screenshot", tabId=TAB_ID)
# Визуальная проверка: все поля заполнены корректно
```

### Шаг 5. Отправка формы

```
find(text="Submit", tabId=TAB_ID)     # или "Отправить", "Save", "Сохранить"
computer(action="left_click", ref=НАЙДЕННЫЙ_REF, tabId=TAB_ID)
```

### Шаг 6. Подтверждение успеха

```
computer(action="screenshot", tabId=TAB_ID)
# Проверить: появилось ли сообщение об успехе
```

## Batch-режим (массовое заполнение из CSV)

```
# Claude Code читает CSV-файл
# Для каждой строки:
#   1. Навигация к форме (или клик "Add New")
#   2. Заполнение полей (Шаги 3-6)
#   3. Checkpoint каждые 25 записей
#   4. Финальный отчет: "Заполнено N из M форм"
```

## Пример промпта

```
Открой CRM на https://crm.example.com/contacts.
У меня есть файл contacts.csv в D:/Downloads/ со столбцами:
name, email, phone, tour_type, date, guests.

Для каждой строки:
1. Нажми "Add Contact"
2. Заполни все поля формы
3. Нажми "Save"
4. Каждые 25 контактов сообщай прогресс

В конце выведи: сколько успешно, сколько ошибок.
```

## Параметры для настройки

| Параметр | По умолчанию | Описание |
|----------|-------------|---------|
| `URL формы` | — | Адрес страницы с формой |
| `Поля` | — | Маппинг: CSS-селектор -> значение |
| `Кнопка отправки` | `"Submit"` | Текст кнопки отправки |
| `Batch CSV` | — | Путь к CSV для массового заполнения |
| `Checkpoint` | 25 | Каждые N записей сообщать прогресс |
| `Метод идентификации` | `form_input` | `form_input` (стандартные), `computer` (custom UI) |

## Частые ошибки

- **`form_input` не работает на custom dropdown** -- Элемент не является стандартным `<select>`. Решение: использовать `computer(left_click)` для открытия, затем `computer(type)` или `find` + `left_click` для выбора опции.

- **Форма сбрасывается после отправки** -- SPA перезагружает компонент. Решение: после отправки дождаться перезагрузки (`computer(wait, duration=2)`) и заново навигировать к чистой форме.

- **Дата-пикер не принимает текстовый ввод** -- Решение: `computer(triple_click)` для выделения текущего значения, затем `computer(type)` с нужной датой. Или кликать по дням в календаре.

- **Не видно кнопку Submit (за скроллом)** -- Решение: `computer(action="scroll", scroll_direction="down", scroll_amount=3)` перед кликом.

- **CAPTCHA на форме** -- Claude паузится. Решение: пользователь решает CAPTCHA, Claude продолжает автоматически.

- **Ошибка валидации не замечена** -- Решение: ВСЕГДА делать screenshot после отправки и проверять наличие error-сообщений.
