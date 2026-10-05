# Decision Tree: Выбор инструмента взаимодействия

## Описание
Дерево решений для выбора правильного инструмента при взаимодействии с элементами веб-страницы. Помогает быстро определить: использовать form_input, computer, javascript_tool или Chrome DevTools MCP в зависимости от типа элемента и задачи.

## Диаграмма

```mermaid
flowchart TD
    START(["Нужно взаимодействовать<br/>с элементом на странице"]) --> Q1{"Какой тип<br/>элемента?"}

    Q1 -->|"input, select,<br/>textarea, checkbox"| Q2{"Стандартный<br/>HTML-элемент?"}
    Q1 -->|"contenteditable,<br/>web-редактор"| Q3{"Нужно вставить<br/>HTML-разметку?"}
    Q1 -->|"Кнопка, ссылка,<br/>меню, custom UI"| Q4{"Есть ref/UID<br/>из read_page?"}
    Q1 -->|"Диалог alert/<br/>confirm/prompt"| DIALOG["Chrome DevTools MCP:<br/><b>handle_dialog</b><br/>(accept/dismiss)"]

    Q2 -->|"Да"| FORMINPUT["Claude in Chrome:<br/><b>form_input</b><br/>(selector, value, action)"]
    Q2 -->|"Нет (React/Vue<br/>custom component)"| Q5{"Виден визуально<br/>на скриншоте?"}

    Q3 -->|"Да (HTML с тегами)"| INNERHTML["Claude in Chrome:<br/><b>javascript_tool</b><br/>innerHTML injection"]
    Q3 -->|"Нет (только текст)"| Q6{"Нужно<br/>форматирование?"}

    Q6 -->|"Да (bold, italic)"| SELECTION["Конвейер:<br/>1. <b>javascript_tool</b> (Selection API)<br/>2. <b>computer</b> (key: ctrl+b/i)"]
    Q6 -->|"Нет"| INNERHTML

    Q4 -->|"Да"| CLICK_REF["Claude in Chrome:<br/><b>computer</b><br/>(left_click, ref=UID)"]
    Q4 -->|"Нет"| Q5

    Q5 -->|"Да"| CLICK_COORD["Claude in Chrome:<br/><b>computer</b><br/>(left_click, coordinate)<br/><i>screenshot -> координаты</i>"]
    Q5 -->|"Нет (скрыто,<br/>offscreen)"| Q7{"Нужен<br/>программный доступ?"}

    Q7 -->|"Да"| JS_TOOL["Claude in Chrome:<br/><b>javascript_tool</b><br/>querySelector + click()"]
    Q7 -->|"Нужен UID<br/>элемента"| DT_CLICK["Chrome DevTools MCP:<br/><b>click</b>(uid)<br/><i>из take_snapshot</i>"]

    FORMINPUT --> CHECK{"Проверить<br/>результат?"}
    INNERHTML --> CHECK
    SELECTION --> CHECK
    CLICK_REF --> CHECK
    CLICK_COORD --> CHECK
    JS_TOOL --> CHECK
    DT_CLICK --> CHECK
    DIALOG --> DONE

    CHECK -->|"Визуально"| SCREENSHOT["<b>computer</b>(screenshot)<br/>или <b>take_screenshot</b>"]
    CHECK -->|"Программно"| JS_CHECK["<b>javascript_tool</b><br/>innerHTML.includes(...)"]
    CHECK -->|"Консоль"| CONSOLE["<b>read_console_messages</b><br/>pattern, onlyErrors"]

    SCREENSHOT --> DONE(["Готово"])
    JS_CHECK --> DONE
    CONSOLE --> DONE

    style START fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style DONE fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style FORMINPUT fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style INNERHTML fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style SELECTION fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    style CLICK_REF fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style CLICK_COORD fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style JS_TOOL fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style DT_CLICK fill:#f8bbd0,stroke:#c62828,stroke-width:2px
    style DIALOG fill:#f8bbd0,stroke:#c62828,stroke-width:2px
```

## Быстрая таблица

| Сценарий | Инструмент | Почему |
|----------|-----------|--------|
| Стандартная HTML-форма | `form_input` | Быстрее, надежнее, не нужны координаты |
| Custom UI (React/Vue) | `computer` (клик) | Визуальный клик обходит виртуальный DOM |
| Web-редактор (contenteditable) | `javascript_tool` (innerHTML) | Прямая вставка HTML-разметки |
| Форматирование текста | Selection API + `computer(key)` | Программное выделение + горячая клавиша |
| Dropdown с поиском | `computer` (click + type) | Имитация пользовательского ввода |
| Скрытый элемент | `javascript_tool` (querySelector) | Программный доступ к невидимым элементам |
| Диалоговое окно (alert) | DevTools `handle_dialog` | Claude in Chrome НЕ поддерживает диалоги |
