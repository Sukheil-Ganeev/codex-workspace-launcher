# Архитектура экосистемы Claude + Browser/Office

## Описание
Показывает взаимосвязь всех 5 продуктов экосистемы: Claude in Chrome (side panel), Claude Code + Chrome (CLI), Chrome DevTools MCP, Claude in Excel, Claude in PowerPoint и Office Skills CLI. Полезна для понимания общей картины: как компоненты связаны, какие протоколы используют и где находятся границы каждого продукта.

## Диаграмма

```mermaid
graph TB
    subgraph USER["Пользователь"]
        CLI["Claude Code CLI<br/><i>claude --chrome</i>"]
        SIDEPANEL["Side Panel<br/><i>Чат в боковой панели</i>"]
    end

    subgraph CHROME_EXT["Chrome Extension (Anthropic)"]
        direction TB
        SW["Service Worker<br/><i>Background script</i>"]
        CS["Content Scripts<br/><i>DOM access</i>"]
        NMH["Native Messaging Host<br/><i>stdio bridge</i>"]
    end

    subgraph MCP_CHROME["MCP: Claude in Chrome (18 tools)"]
        direction LR
        NAV["navigate<br/>tabs_context_mcp<br/>tabs_create_mcp"]
        INTERACT["computer (13 actions)<br/>form_input<br/>find"]
        DOM["read_page<br/>get_page_text<br/>javascript_tool"]
        MEDIA["gif_creator<br/>upload_image<br/>resize_window"]
        DEBUG["read_console_messages<br/>read_network_requests"]
        SHORTCUTS["shortcuts_list<br/>shortcuts_execute<br/>update_plan<br/>switch_browser"]
    end

    subgraph MCP_DEVTOOLS["MCP: Chrome DevTools (26 tools)"]
        direction LR
        DT_NAV["navigate_page<br/>new_page<br/>close_page<br/>select_page<br/>list_pages"]
        DT_INTERACT["click<br/>fill<br/>fill_form<br/>hover<br/>drag<br/>press_key"]
        DT_DOM["take_snapshot<br/>evaluate_script<br/>wait_for"]
        DT_MEDIA["take_screenshot<br/>upload_file<br/>resize_page<br/>emulate"]
        DT_DEBUG["list_console_messages<br/>get_console_message<br/>list_network_requests<br/>get_network_request<br/>handle_dialog"]
        DT_PERF["performance_start_trace<br/>performance_stop_trace<br/>performance_analyze_insight"]
    end

    subgraph BROWSER["Chrome / Edge"]
        TAB1["Tab 1: Web App"]
        TAB2["Tab 2: CRM"]
        TAB3["Tab 3: localhost"]
    end

    subgraph OFFICE["Microsoft Office"]
        EXCEL["Claude in Excel<br/><i>Add-in / Sidebar</i><br/>Beta"]
        PPT["Claude in PowerPoint<br/><i>Add-in / Sidebar</i><br/>Research Preview"]
    end

    subgraph OFFICE_CLI["Office Skills CLI"]
        PPTX_SKILL["pptx skill<br/><i>python-pptx, pptxgenjs</i>"]
        XLSX_SKILL["xlsx skill<br/><i>openpyxl, pandas</i>"]
        DOCX_SKILL["docx skill<br/><i>python-docx</i>"]
        PDF_SKILL["pdf skill<br/><i>Poppler, Pandoc</i>"]
    end

    CLI -->|"Named Pipe (Windows)<br/>Unix Socket (macOS/Linux)"| NMH
    NMH -->|"stdio"| SW
    SIDEPANEL --> SW
    SW --> CS
    CS --> BROWSER

    CLI -->|"MCP Protocol"| MCP_CHROME
    CLI -->|"MCP Protocol"| MCP_DEVTOOLS
    MCP_CHROME --> SW
    MCP_DEVTOOLS -->|"CDP<br/>(Chrome DevTools Protocol)"| BROWSER

    CLI -->|"SKILL.md + Python/Node"| OFFICE_CLI

    EXCEL -->|"Anthropic API"| EXCEL
    PPT -->|"Anthropic API"| PPT

    style USER fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style CHROME_EXT fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style MCP_CHROME fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style MCP_DEVTOOLS fill:#fce4ec,stroke:#c62828,stroke-width:2px
    style BROWSER fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style OFFICE fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    style OFFICE_CLI fill:#fff8e1,stroke:#f57f17,stroke-width:2px
```

## Ключевые связи

| Связь | Протокол | Описание |
|-------|----------|----------|
| Claude Code -> Extension | Named Pipe / Unix Socket | Native Messaging Host bridge |
| Extension -> Browser | Content Scripts | DOM-доступ через Chrome API |
| Claude Code -> Claude in Chrome MCP | MCP Protocol | 18 инструментов через расширение |
| Claude Code -> Chrome DevTools MCP | CDP (Chrome DevTools Protocol) | 26 инструментов напрямую |
| Claude Code -> Office Skills | SKILL.md + Python/Node | Программная генерация файлов |
| Excel/PPT Add-in -> Anthropic | Anthropic API | Прямое обращение к моделям |

## Конфликт: Desktop Cowork vs Claude Code

Оба используют один Extension ID. Одновременно работает только одно приложение. При конфликте -- отключить Native Messaging Host неиспользуемого.
