# Сравнение: Office Add-ins vs CLI Skills

## Описание
Сравнительная диаграмма двух подходов к работе с Office-файлами: интерактивные Add-in (Claude in Excel, Claude in PowerPoint) и программные CLI Skills (xlsx, pptx, docx, pdf). Помогает выбрать правильный подход в зависимости от задачи, плана подписки и требований к автоматизации.

## Диаграмма

```mermaid
graph TB
    subgraph TASK["Задача: работа с Office-файлами"]
        Q1{"Какой формат?"}
    end

    Q1 -->|"Excel (.xlsx)"| EXCEL_Q{"Интерактивный<br/>или batch?"}
    Q1 -->|"PowerPoint (.pptx)"| PPT_Q{"Интерактивный<br/>или batch?"}
    Q1 -->|"Word (.docx)"| DOCX["CLI: docx skill<br/><i>python-docx</i>"]
    Q1 -->|"PDF"| PDF["CLI: pdf skill<br/><i>Poppler, Pandoc,<br/>LibreOffice</i>"]

    EXCEL_Q -->|"Интерактивный<br/>(1 файл, sidebar)"| EXCEL_ADDIN
    EXCEL_Q -->|"Batch / программный<br/>(много файлов)"| EXCEL_CLI

    PPT_Q -->|"Интерактивный<br/>(1 файл, sidebar)"| PPT_ADDIN
    PPT_Q -->|"Batch / программный<br/>(много файлов)"| PPT_CLI

    subgraph EXCEL_ADDIN["Claude in Excel (Add-in)"]
        EA1["<b>Статус:</b> Beta"]
        EA2["<b>Планы:</b> Pro, Max, Team, Enterprise"]
        EA3["<b>Модели:</b> Sonnet 4.5, Opus 4.6"]
        EA4["<b>Hotkey:</b> Ctrl+Alt+C"]
        EA5["<b>Фичи:</b><br/>- Cell-level цитаты<br/>- Трассировка формул<br/>- Отладка #REF!/#VALUE!<br/>- Pivot tables<br/>- Conditional formatting<br/>- Графики<br/>- 6 Agent Skills (DCF, LBO...)<br/>- 7 финансовых коннекторов<br/>- Drag & drop файлов<br/>- Claude Log Tab"]
        EA6["<b>Нет:</b> VBA/macros,<br/>Data tables, audit logs"]
    end

    subgraph EXCEL_CLI["xlsx CLI Skill"]
        EC1["<b>Статус:</b> Stable"]
        EC2["<b>Планы:</b> Любой с Claude Code"]
        EC3["<b>Библиотеки:</b><br/>openpyxl, pandas,<br/>LibreOffice"]
        EC4["<b>Фичи:</b><br/>- Формулы<br/>- Форматирование<br/>- Color coding<br/>- recalc.py<br/>- Batch-обработка<br/>- Программная генерация"]
    end

    subgraph PPT_ADDIN["Claude in PowerPoint (Add-in)"]
        PA1["<b>Статус:</b> Research Preview"]
        PA2["<b>Планы:</b> Max, Team, Enterprise<br/><i>(НЕ Pro!)</i>"]
        PA3["<b>Модели:</b> Opus 4.6, Sonnet 4.5"]
        PA4["<b>Лимит:</b> ~1000 пользователей"]
        PA5["<b>Фичи:</b><br/>- Template Intelligence<br/>&nbsp;&nbsp;(slide master, fonts, colors)<br/>- Нативные графики<br/>&nbsp;&nbsp;(НЕ статичные картинки!)<br/>- Буллеты -> диаграммы<br/>- Точечные правки<br/>&nbsp;&nbsp;(без регенерации)"]
        PA6["<b>Нет:</b> Pro план,<br/>chat history, audit logs"]
    end

    subgraph PPT_CLI["pptx CLI Skill"]
        PC1["<b>Статус:</b> Stable"]
        PC2["<b>Планы:</b> Любой с Claude Code"]
        PC3["<b>Библиотеки:</b><br/>python-pptx, pptxgenjs,<br/>markitdown"]
        PC4["<b>Фичи:</b><br/>- HTML -> PPTX<br/>- Шаблоны<br/>- Thumbnail генерация<br/>- XML editing<br/>- Batch-обработка<br/>- Программная генерация"]
    end

    style TASK fill:#e8eaf6,stroke:#283593,stroke-width:2px
    style EXCEL_ADDIN fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style EXCEL_CLI fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style PPT_ADDIN fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style PPT_CLI fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style DOCX fill:#fce4ec,stroke:#c62828,stroke-width:2px
    style PDF fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

## Сравнительная таблица

| Критерий | Add-in (Excel/PPT) | CLI Skill (xlsx/pptx/docx/pdf) |
|----------|--------------------|---------------------------------|
| **Подход** | Интерактивный (sidebar) | Программный (скрипт) |
| **Файлы за раз** | 1 открытый файл | Любое количество (batch) |
| **Нужен Office?** | Да (Excel/PowerPoint) | Нет (Python-библиотеки) |
| **Подписка (Excel)** | Pro, Max, Team, Enterprise | Любой с Claude Code |
| **Подписка (PPT)** | Max, Team, Enterprise (НЕ Pro!) | Любой с Claude Code |
| **Интеллект** | Высокий (cell-level, template intelligence) | Средний (программная логика) |
| **Batch** | Нет | Да |
| **Audit** | Claude Log Tab (только Excel) | Логи Claude Code |
| **VBA/Macros** | Нет | Нет |
| **Форматы** | .xlsx, .xlsm / .pptx | .xlsx, .pptx, .docx, .pdf |

## Pipeline: Excel -> PowerPoint

```
Claude in Excel                 Claude in PowerPoint
(анализ данных)       -->       (визуализация)
- Формулы                       - Template Intelligence
- Pivot tables                  - Нативные графики
- Conditional formatting        - Корпоративный брендинг
```

Или через CLI:
```
xlsx skill              -->       pptx skill
(openpyxl/pandas)                 (python-pptx/pptxgenjs)
- Batch обработка                 - HTML -> PPTX
- recalc.py                       - Batch генерация
```
