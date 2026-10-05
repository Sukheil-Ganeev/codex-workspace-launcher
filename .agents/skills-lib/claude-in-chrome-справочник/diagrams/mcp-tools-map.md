# Mind Map: Все MCP-инструменты по категориям

## Описание
Полная карта всех 18 инструментов Claude in Chrome и 26 инструментов Chrome DevTools MCP, сгруппированных по функциональным категориям. Позволяет быстро найти нужный инструмент по задаче и увидеть параллели между двумя MCP-серверами.

## Диаграмма

```mermaid
mindmap
  root((MCP Tools<br/>44 инструмента))
    **Claude in Chrome**<br/>18 tools
      Навигация и вкладки
        navigate<br/>url, action
        tabs_context_mcp<br/>createIfEmpty
        tabs_create_mcp<br/>url
        switch_browser<br/>browser_name
      Взаимодействие
        computer<br/>13 actions
          left_click
          right_click
          double_click
          triple_click
          type
          key
          scroll
          scroll_to
          left_click_drag
          hover
          zoom
          wait
          screenshot
        form_input<br/>selector, value
        find<br/>text, exact_match
      DOM и данные
        read_page<br/>accessibility_tree / html
        get_page_text<br/>текст страницы
        javascript_tool<br/>JS expression
      Медиа и UI
        gif_creator<br/>4 actions
          start_recording
          stop_recording
          export
          clear
        upload_image<br/>imageId
        resize_window<br/>width, height
      Отладка
        read_console_messages<br/>pattern, onlyErrors
        read_network_requests<br/>urlPattern
      Шорткаты и план
        shortcuts_list
        shortcuts_execute<br/>shortcut_name
        update_plan<br/>plan_text
    **Chrome DevTools MCP**<br/>26 tools
      Навигация и страницы
        navigate_page<br/>url, back, forward, reload
        new_page<br/>url
        close_page
        select_page<br/>pageId
        list_pages
      Взаимодействие
        click<br/>uid, dblClick
        fill<br/>uid, value
        fill_form<br/>fields array
        hover<br/>uid
        drag<br/>uid, target
        press_key<br/>key
      DOM и скрипты
        take_snapshot<br/>verbose, filePath
        evaluate_script<br/>function, args
        wait_for<br/>text, timeout
      Медиа и эмуляция
        take_screenshot<br/>fullPage, uid
        upload_file<br/>filePath
        resize_page<br/>width, height
        emulate<br/>viewport, geo, network, cpu
      Отладка
        list_console_messages<br/>20 типов
        get_console_message<br/>id
        list_network_requests<br/>20 resource types
        get_network_request<br/>id
        handle_dialog<br/>accept, dismiss, text
      Performance
        performance_start_trace
        performance_stop_trace
        performance_analyze_insight
```

## Таблица соответствий: Claude in Chrome vs Chrome DevTools MCP

| Категория | Claude in Chrome | Chrome DevTools MCP | Уникальное |
|-----------|-----------------|---------------------|------------|
| Навигация | `navigate` | `navigate_page` | DevTools: `list_pages`, `close_page` |
| Клик | `computer(left_click)` | `click(uid)` | Chrome: `right/double/triple_click`, drag |
| Формы | `form_input` | `fill`, `fill_form` | DevTools: batch `fill_form` |
| JS | `javascript_tool` | `evaluate_script` | DevTools: uid args |
| Скриншот | `computer(screenshot)` | `take_screenshot` | DevTools: fullPage, element screenshot |
| DOM | `read_page` | `take_snapshot` | Chrome: `get_page_text`, `find` |
| Консоль | `read_console_messages` | `list_console_messages` | DevTools: `get_console_message` |
| Сеть | `read_network_requests` | `list_network_requests` | DevTools: `get_network_request` |
| GIF | `gif_creator` | -- | Только Chrome! |
| Upload | `upload_image` (screenshot) | `upload_file` (disk) | Разная функциональность |
| Диалоги | -- | `handle_dialog` | Только DevTools! |
| Performance | -- | 3 инструмента | Только DevTools! |
| Эмуляция | -- | `emulate` | Только DevTools! |
| Шорткаты | `shortcuts_list/execute` | -- | Только Chrome! |
| План | `update_plan` | -- | Только Chrome! |

## Когда что использовать

- **Claude in Chrome** -- авторизованные сайты (cookies), GIF-запись, шорткаты, side panel
- **Chrome DevTools MCP** -- performance, headless, full-page screenshots, диалоги, эмуляция
- **Оба вместе** -- максимальный контроль: Chrome для UI, DevTools для отладки
