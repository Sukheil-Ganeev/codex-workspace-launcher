# Web-Editor Formatting Template (PuzzleBot Pattern)

## Назначение

Шаблон для форматирования текста в web-редакторах с contenteditable: PuzzleBot, Notion, Google Docs, CMS-системы. Использует проверенный паттерн: innerHTML injection + JS Selection API + горячие клавиши.

**Когда использовать:**
- Вставка и форматирование текста в PuzzleBot (Telegram-боты)
- Работа с Notion, Google Docs, любые WYSIWYG-редакторы
- Форматирование с переменными ({{user_name}}, {{date}} и т.д.)
- Массовое создание контента с HTML-разметкой

**Статус:** Проверен на практике 2 раза (PuzzleBot, 2026-02-15)

## Шаги

### Шаг 1. Навигация к редактору

```
tabs_context_mcp(createIfEmpty=true)
navigate(url="https://САЙТ.com/редактор")
computer(action="screenshot", tabId=TAB_ID)
```

### Шаг 2. Вставка всего HTML через innerHTML injection

```
javascript_tool(action="javascript_exec", text="
  document.querySelector('СЕЛЕКТОР_РЕДАКТОРА').innerHTML = `
    <p>Обычный текст</p>
    <p><strong>Жирный текст</strong> и <em>курсив</em></p>
    <p>Текст с {{переменной}} внутри</p>
    <p>Список:</p>
    <ul>
      <li>Пункт 1</li>
      <li>Пункт 2</li>
    </ul>
  `
", tabId=TAB_ID)
```

**Типичные селекторы редакторов:**
| Редактор | Селектор |
|----------|---------|
| PuzzleBot (Quill) | `.ql-editor` |
| Notion | `[contenteditable="true"]` |
| CKEditor | `.ck-editor__editable` |
| TinyMCE | `#tinymce` (внутри iframe!) |

### Шаг 3. Дополнительное форматирование через Selection API + горячие клавиши

Если innerHTML не поддерживает нужный формат (редактор использует свои классы), используйте конвейер:

```
# 3a. Выделить нужный фрагмент через JS Selection API
javascript_tool(action="javascript_exec", text="
  const range = document.createRange();
  const sel = window.getSelection();
  // Находим нужный текстовый узел
  const textNode = document.querySelector('СЕЛЕКТОР_РЕДАКТОРА p:nth-child(2)').firstChild;
  range.setStart(textNode, 0);    // начало выделения (символ)
  range.setEnd(textNode, 12);     // конец выделения (символ)
  sel.removeAllRanges();
  sel.addRange(range);
", tabId=TAB_ID)

# 3b. Применить форматирование горячей клавишей
computer(action="key", text="ctrl+b", tabId=TAB_ID)    # Жирный
# или
computer(action="key", text="ctrl+i", tabId=TAB_ID)    # Курсив
# или
computer(action="key", text="ctrl+u", tabId=TAB_ID)    # Подчеркнутый
```

### Шаг 4. Форматирование без горячей клавиши (кнопка на панели)

Если горячая клавиша сломана или формат не имеет шортката (например, `<code>` в PuzzleBot):

```
# 4a. Выделить текст через Selection API (как в Шаге 3a)

# 4b. Сделать скриншот — найти кнопку на панели форматирования
computer(action="screenshot", tabId=TAB_ID)

# 4c. Кликнуть по кнопке
computer(action="left_click", coordinate=[X, Y], tabId=TAB_ID)
```

### Шаг 5. Проверка результата (одним JS-вызовом)

```
javascript_tool(action="javascript_exec", text="
  const html = document.querySelector('СЕЛЕКТОР_РЕДАКТОРА').innerHTML;
  JSON.stringify({
    bold: html.includes('<strong>'),
    italic: html.includes('<em>'),
    code: html.includes('<code>'),
    variables: html.includes('{{'),
    totalLength: html.length
  })
", tabId=TAB_ID)
```

### Шаг 6. Финальный скриншот

```
computer(action="screenshot", tabId=TAB_ID)
```

## Пример промпта

```
Открой PuzzleBot, перейди к боту @my_tour_bot, найди сообщение приветствия.
Вставь следующий текст с форматированием:

Добро пожаловать, {{user_name}}!

Наши услуги:
- **Экскурсии** по Дубаю и Абу-Даби
- **Джип-сафари** в пустыне
- *Индивидуальные программы* по запросу

Для бронирования напишите /book

Убедись, что:
1. {{user_name}} осталась как переменная (не сломалась)
2. Жирный и курсив применены корректно
3. Сделай финальный скриншот
```

## Параметры для настройки

| Параметр | По умолчанию | Описание |
|----------|-------------|---------|
| `СЕЛЕКТОР_РЕДАКТОРА` | `.ql-editor` | CSS-селектор contenteditable элемента |
| `HTML-контент` | — | Полный HTML для вставки через innerHTML |
| `Форматы` | bold, italic | Какие форматы применить (bold, italic, code, underline) |
| `Переменные` | — | Список переменных в формате `{{name}}` |
| `Метод форматирования` | горячая клавиша | `key` (горячая клавиша) или `click` (кнопка панели) |

## Частые ошибки

- **`{{переменные}}` ломаются при `computer(type)`** -- Фигурные скобки интерпретируются некорректно. Решение: ТОЛЬКО innerHTML injection для текста с переменными. Никогда `computer(type)`.

- **`Ctrl+Shift+M` в PuzzleBot вводит букву "m"** -- Шорткат СЛОМАН в PuzzleBot. Решение: использовать кнопку `</>` на панели форматирования (screenshot + click).

- **Панель форматирования "плавает"** -- Координаты кнопок меняются. Решение: делать screenshot ПЕРЕД КАЖДЫМ кликом по панели.

- **Emoji попадают в Selection range** -- Ломают выделение (emoji = 2 символа в Unicode). Решение: исключить emoji из диапазона setStart/setEnd, считать символы без emoji.

- **innerHTML вставлен, но редактор не "видит" изменения** -- Некоторые редакторы используют свою модель данных. Решение: после innerHTML вызвать `dispatchEvent(new Event('input', {bubbles: true}))` чтобы триггернуть обновление.

- **TinyMCE: селектор не находится** -- TinyMCE рендерит внутри iframe. Решение: сначала `document.querySelector('iframe').contentDocument.querySelector('#tinymce')`.

## Оптимизация

Этот паттерн дает ~10 действий вместо 30+ при ручном вводе. Экономия: 60-70% токенов и времени.

**Порядок приоритета:**
1. innerHTML injection -- для вставки всего контента разом
2. Selection API + горячая клавиша -- для точечного форматирования
3. Screenshot + click по кнопке -- только если горячая клавиша сломана
