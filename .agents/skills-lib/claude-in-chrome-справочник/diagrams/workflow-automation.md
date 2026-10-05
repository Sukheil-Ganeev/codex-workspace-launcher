# Flowchart: Оптимальный паттерн автоматизации Web-редактора

## Описание
Пошаговая схема оптимального паттерна автоматизации web-редакторов (PuzzleBot и аналоги). Показывает конвейер: innerHTML injection -> Selection API -> горячие клавиши -> проверка -> скриншот. Основан на проверенном опыте (2x тестирование). Сокращает количество действий с 30+ до ~10, экономия 60-70%.

## Диаграмма

```mermaid
flowchart TD
    START(["Задача: автоматизация<br/>web-редактора"]) --> INIT

    subgraph INIT["1. Инициализация"]
        T1["tabs_context_mcp<br/>(createIfEmpty=true)"] --> T2["navigate(url)"]
        T2 --> T3["read_page<br/>(accessibility_tree)"]
        T3 --> T4["computer(screenshot)<br/><i>оценить состояние</i>"]
    end

    INIT --> FIND_EDITOR

    subgraph FIND_EDITOR["2. Найти редактор"]
        F1["find(text='...')<br/><i>поиск редактора</i>"] --> F2{"Найден<br/>contenteditable?"}
        F2 -->|"Да"| F3["Запомнить selector<br/><i>.editor, [contenteditable]</i>"]
        F2 -->|"Нет"| F4["javascript_tool:<br/>querySelector('[contenteditable]')"]
        F4 --> F3
    end

    FIND_EDITOR --> INJECT

    subgraph INJECT["3. innerHTML Injection"]
        I1["javascript_tool:<br/><b>editor.innerHTML = HTML</b>"] --> I2{"Контент содержит<br/>переменные {{...}}?"}
        I2 -->|"Да"| I3["Вставить через innerHTML!<br/><i>НЕ через ввод текста</i><br/>(переменные ломаются)"]
        I2 -->|"Нет"| I4["innerHTML =<br/>'&lt;p&gt;Текст&lt;/p&gt;'"]
        I3 --> I5["Проверка:<br/>innerHTML.includes(...)"]
        I4 --> I5
    end

    INJECT --> FORMAT_Q{"Нужно<br/>форматирование?"}

    FORMAT_Q -->|"Нет"| VERIFY
    FORMAT_Q -->|"Да"| FORMAT

    subgraph FORMAT["4. Форматирование (конвейер)"]
        direction TB
        FMT1["javascript_tool:<br/><b>Selection API</b><br/><i>range.setStart/setEnd</i>"] --> FMT2{"Тип<br/>форматирования?"}
        FMT2 -->|"Bold"| FMT3["computer(key: 'ctrl+b')"]
        FMT2 -->|"Italic"| FMT4["computer(key: 'ctrl+i')"]
        FMT2 -->|"Monospace"| FMT5{"Ctrl+Shift+M<br/>работает?"}
        FMT5 -->|"Да"| FMT6["computer(key:<br/>'ctrl+shift+m')"]
        FMT5 -->|"Нет (PuzzleBot!)"| FMT7["computer(screenshot)<br/>-> клик по кнопке<br/>&lt;/&gt; на панели"]
        FMT3 --> FMT8["Повторить для<br/>следующего фрагмента"]
        FMT4 --> FMT8
        FMT6 --> FMT8
        FMT7 --> FMT8
        FMT8 -->|"Есть еще"| FMT1
        FMT8 -->|"Все готово"| FMT9["Конвейер завершен"]
    end

    FORMAT --> VERIFY

    subgraph VERIFY["5. Проверка результата"]
        V1["javascript_tool:<br/>innerHTML.includes('&lt;strong&gt;')"] --> V2{"Форматирование<br/>применилось?"}
        V2 -->|"Да"| V3["computer(screenshot)<br/><i>финальный скриншот</i>"]
        V2 -->|"Нет"| V4["Повторить<br/>Selection + Key"]
        V4 --> V1
    end

    VERIFY --> BUTTONS_Q{"Нужны действия<br/>с кнопками<br/>(отправка и т.д.)?"}

    BUTTONS_Q -->|"Нет"| DONE
    BUTTONS_Q -->|"Да"| BUTTONS

    subgraph BUTTONS["6. Кнопочные действия"]
        B1["computer(screenshot)<br/><i>найти кнопку</i>"] --> B2["computer(left_click,<br/>coordinate)"]
        B2 --> B3["computer(screenshot)<br/><i>подтвердить результат</i>"]
    end

    BUTTONS --> DONE(["Готово!<br/>~10 действий вместо 30+"])

    style START fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style DONE fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style INIT fill:#e3f2fd,stroke:#1565c0,stroke-width:1px
    style FIND_EDITOR fill:#e3f2fd,stroke:#1565c0,stroke-width:1px
    style INJECT fill:#fff3e0,stroke:#e65100,stroke-width:1px
    style FORMAT fill:#fce4ec,stroke:#c62828,stroke-width:1px
    style VERIFY fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px
    style BUTTONS fill:#f3e5f5,stroke:#6a1b9a,stroke-width:1px
```

## Критические предупреждения (из опыта)

| Проблема | Решение |
|----------|---------|
| `{{переменные}}` ломаются при обычном вводе | ТОЛЬКО innerHTML injection |
| `Ctrl+Shift+M` вводит "m" в PuzzleBot | Кликать кнопку `</>` на панели |
| `alert()` блокирует все | НИКОГДА не вызывать alert/confirm/prompt |
| Selection не сработал | Проверить: textNode vs elementNode |
| Форматирование не видно | JS-проверка innerHTML перед скриншотом |

## Сравнение подходов

| Подход | Действий | Надежность | Скорость |
|--------|----------|-----------|----------|
| Наивный (клик-клик-клик) | 30+ | Низкая | Медленно |
| innerHTML + Selection API | ~10 | Высокая | Быстро |
| Экономия | **60-70%** | -- | -- |
