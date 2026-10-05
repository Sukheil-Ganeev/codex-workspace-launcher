ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# Шпаргалка: Claude in Chrome + Extensions

## Запуск

| Действие | Команда |
|----------|---------|
| CLI с Chrome | `claude --chrome` |
| Внутри сессии | `/chrome` |
| По умолчанию | `/chrome` → "Enabled by default" |
| Переподключение | `/chrome` → "Reconnect extension" |
| Проверка MCP | `/mcp` → выбрать "claude-in-chrome" |
| Диагностика | `claude doctor --mcp-debug` |

## Обязательный первый вызов

```
tabs_context_mcp(createIfEmpty=true)
```

## Навигация

| Действие | Вызов |
|----------|-------|
| Перейти на URL | `navigate(url="https://...")` |
| Назад | `navigate(action="back")` |
| Вперед | `navigate(action="forward")` |
| Новая вкладка | `tabs_create_mcp(url="https://...")` |
| Переключить браузер | `switch_browser(browser_name="edge")` |

## Чтение страниц

| Действие | Вызов |
|----------|-------|
| DOM-структура | `read_page(tabId=T, format="accessibility_tree")` |
| HTML-код | `read_page(tabId=T, format="html")` |
| Чистый текст | `get_page_text(tabId=T)` |
| Поиск элемента | `find(text="Кнопка", tabId=T)` |

## Взаимодействие

| Действие | Вызов |
|----------|-------|
| Клик | `computer(action="left_click", tabId=T, coordinate=[x,y])` |
| Клик по ref | `computer(action="left_click", tabId=T, ref="uid_3_21")` |
| Ввод текста | `computer(action="type", tabId=T, text="Hello")` |
| Горячая клавиша | `computer(action="key", tabId=T, text="ctrl+b")` |
| Скролл вниз | `computer(action="scroll", tabId=T, coordinate=[500,400], scroll_direction="down")` |
| Скролл к элементу | `computer(action="scroll_to", tabId=T, ref="uid_3_50")` |
| Двойной клик | `computer(action="double_click", tabId=T, coordinate=[x,y])` |
| Перетаскивание | `computer(action="left_click_drag", tabId=T, start_coordinate=[x1,y1], coordinate=[x2,y2])` |
| Hover | `computer(action="hover", tabId=T, coordinate=[x,y])` |
| Форма | `form_input(selector="#email", value="test@mail.com", tabId=T)` |

## Визуальный контроль

| Действие | Вызов |
|----------|-------|
| Скриншот | `computer(action="screenshot", tabId=T)` |
| Zoom-область | `computer(action="zoom", tabId=T, region=[100,200,400,350])` |
| Размер окна | `resize_window(width=1280, height=720, tabId=T)` |
| Пауза | `computer(action="wait", tabId=T, duration=5)` |

## JavaScript

| Действие | Вызов |
|----------|-------|
| Выполнить JS | `javascript_tool(action="javascript_exec", text="document.title", tabId=T)` |
| innerHTML | `javascript_tool(..., text="document.querySelector('.ed').innerHTML='<p>HTML</p>'")` |
| Проверка | `javascript_tool(..., text="document.querySelector('.ed').innerHTML.includes('<strong>')")` |

## Консоль и сеть

| Действие | Вызов |
|----------|-------|
| Ошибки консоли | `read_console_messages(tabId=T, onlyErrors=true)` |
| Фильтр консоли | `read_console_messages(tabId=T, pattern="error\|CORS")` |
| API-запросы | `read_network_requests(tabId=T, urlPattern="/api/")` |

## GIF-запись

```
gif_creator(action="start_recording", tabId=T)
computer(action="screenshot", tabId=T)          # первый кадр!
... действия + screenshots ...
computer(action="screenshot", tabId=T)          # последний кадр!
gif_creator(action="stop_recording", tabId=T)
gif_creator(action="export", tabId=T, download=true, filename="demo.gif")
```

## Шорткаты

| Действие | Вызов |
|----------|-------|
| Список шорткатов | `shortcuts_list()` |
| Выполнить | `shortcuts_execute(shortcut_name="/competitor-scan")` |
| Обновить план | `update_plan(plan_text="Шаг 3 из 5: Заполняю форму...")` |

## Клавиатурные комбинации для web-редакторов

| Комбинация | Действие | Примечание |
|------------|----------|-----------|
| Ctrl+B | Жирный | Работает везде |
| Ctrl+I | Курсив | Работает везде |
| Ctrl+U | Подчеркнутый | Работает везде |
| Ctrl+K | Ссылка | Работает везде |
| Ctrl+Shift+S | Зачеркнутый | PuzzleBot |
| Ctrl+Shift+M | Моноширинный | **СЛОМАН в PuzzleBot!** Использовать кнопку </> |
| Ctrl+A | Выделить все | Универсальная |

## Паттерн для web-редакторов (проверен)

```
1. innerHTML injection (весь HTML разом)
2. JS Selection API (выделение фрагмента)
3. computer(key: "ctrl+b") (форматирование)
4. JS-проверка: innerHTML.includes('<strong>')
5. Один финальный screenshot
```

## Chrome DevTools MCP — уникальные инструменты

| Действие | Вызов |
|----------|-------|
| JS-функция | `evaluate_script(function="() => { return document.title }")` |
| Full-page screenshot | `take_screenshot(fullPage=true)` |
| Screenshot элемента | `take_screenshot(uid="3_21")` |
| Обработка диалога | `handle_dialog(accept=true)` |
| Performance trace | `performance_start_trace()` ... `performance_stop_trace()` |
| Эмуляция | `emulate(viewport={width:375, height:812})` |
| Ожидание текста | `wait_for(text="Success", timeout=10000)` |
| Клавиша | `press_key(key="Control+B")` |

## Excel add-in

| Действие | Горячая клавиша |
|----------|----------------|
| Открыть sidebar | Ctrl+Alt+C (Win) / Ctrl+Option+C (Mac) |
| Отменить действие | Ctrl+Z / Cmd+Z |

## Быстрая диагностика

| Проблема | Решение |
|----------|---------|
| Extension not connected | Перезапуск Chrome + Claude Code |
| Service worker заснул | `/chrome` → Reconnect |
| Named pipe conflict (Win) | Закрыть другие сессии Claude Code |
| Cowork конфликт | Отключить native host неиспользуемого |
| Alert заблокировал | Dismiss вручную, НЕ использовать alert() в JS |
| Tab ID невалиден | `tabs_context_mcp` для свежих ID |
