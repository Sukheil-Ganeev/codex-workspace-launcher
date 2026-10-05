# Claude in Chrome + Extensions: Справочник

**Версия:** 1.0 | **Создан:** 2026-02-16

## Описание

Production-ready справочник по экосистеме Claude для браузера и офисных приложений:
- **Claude in Chrome** — расширение для Chrome/Edge (side panel + Claude Code интеграция)
- **Chrome DevTools MCP** — альтернативный MCP-сервер от Google (26 инструментов)
- **Claude in Excel** — Office Add-in для работы с таблицами
- **Claude in PowerPoint** — Office Add-in для презентаций (Research Preview)
- **Office Skills CLI** — SKILL.md для программного создания PPTX/XLSX/DOCX/PDF

## Структура

```
claude-in-chrome-справочник/
├── SKILL.md                    # Основной справочник (~5000 слов, 14 разделов)
├── README.md                   # Этот файл
├── references/
│   ├── mcp-tools-catalog.md    # Полный каталог 18+26 MCP tools с параметрами
│   ├── cheatsheet.md           # Шпаргалка: инструменты, параметры, горячие клавиши
│   ├── office-addins.md        # Детальное руководство Excel + PowerPoint
│   ├── workflow-recipes.md     # Готовые рецепты автоматизации
│   ├── troubleshooting.md      # Подробная таблица ошибок и решений
│   └── faq.md                  # Часто задаваемые вопросы
└── experience/
    └── _index.md               # Критические уроки (читать при активации!)
```

## Разделы SKILL.md

| # | Раздел | Описание |
|---|--------|---------|
| 01 | Обзор экосистемы | 5 продуктов, планы, модели, хронология |
| 02 | MCP-инструменты Claude in Chrome | Каталог 18 tools, computer (13 actions), gif_creator (4 actions) |
| 03 | Chrome DevTools MCP | Каталог 26 tools, сравнительная таблица, установка |
| 04 | Навигация, вкладки и DOM | Tab groups, read_page, multi-tab workflows |
| 05 | Взаимодействие с элементами | form_input vs computer, загрузка файлов |
| 06 | JavaScript injection | javascript_tool, evaluate_script, innerHTML, Selection API |
| 07 | Шорткаты и планирование | 3 способа создания, scheduled tasks, MCP tools |
| 08 | Паттерны и рецепты | PuzzleBot (проверен), batch, coding+browser, GIF |
| 09 | Claude in Excel | Add-in, финансовые коннекторы, Agent Skills, CLI skill |
| 10 | Claude in PowerPoint | Add-in (Research Preview), Template Intelligence, CLI skill |
| 11 | Office Skills CLI | PPTX, XLSX, DOCX, PDF через Claude Code |
| 12 | Безопасность | Prompt injection, разрешения, admin-контроли |
| 13 | Troubleshooting | Таблица ошибок, диагностика, anti-rabbit-hole |
| 14 | Примеры для туризма ОАЭ | Мониторинг конкурентов, CRM, Excel, PPT, GIF |

## Источники данных

- **Tier 1:** Claude Code Docs, Claude Help Center, Anthropic Blog, ToolSearch (MCP-схемы)
- **Tier 2:** Chrome DevTools MCP GitHub, DataCamp tutorials, Zenity security research
- **Tier 3:** Community blogs, leaked system prompts (помечены как "может быть неактуально")
- **Tier 1 (Опыт):** PuzzleBot-кейс (проверен 2x, 2026-02-15)
