ДАННЫЕ АКТУАЛЬНЫ НА: 2026-02-16

# Claude in Excel и PowerPoint: Детальное руководство

## Claude in Excel

### Установка

**Индивидуальная:**
1. Открыть Excel (desktop или web)
2. Insert → Get Add-ins (Win) / Tools → Add-ins (Mac)
3. Найти "Claude by Anthropic" → Add
4. Войти с аккаунтом claude.ai
5. Горячая клавиша: Ctrl+Alt+C (Win) / Ctrl+Option+C (Mac)

**Организации (Admin):**
1. Microsoft 365 Admin Center → Settings → Integrated apps → Add-ins
2. "Claude by Anthropic for Excel" в AppSource
3. Deploy для организации или конкретных пользователей

### Возможности

| Категория | Возможности |
|-----------|------------|
| **Анализ** | Вопросы о workbook, cell-level цитаты (кликабельные), трассировка формул, навигация по листам |
| **Модификация** | Обновление данных с сохранением формул, подсветка изменений, отладка #REF!/#VALUE!/circular |
| **Нативные операции** | Sort, filter, pivot tables, графики, conditional formatting, data validation, gridlines |
| **Финансовое моделирование** | 3-statement models, DCF, SaaS metrics, LBO, real estate pro formas |
| **Работа с данными** | Категоризация, стандартизация, поиск дубликатов, парсинг |

### Финансовые коннекторы (7 штук)

| Коннектор | Данные |
|-----------|--------|
| Aiera | Транскрипты earnings calls, саммари |
| Third Bridge | Экспертные инсайты |
| Chronograph | PE-портфели |
| Egnyte | Data rooms, инвестиционные документы |
| LSEG | Live market data: акции, облигации, forex |
| Moody's | Кредитные рейтинги, 600M+ компаний |
| MT Newswires | Финансовые новости |

### Pre-built Agent Skills (6 штук)

1. **Comparable Company Analysis** — мультипликаторы оценки
2. **DCF Models** — прогнозы cash flow, WACC, sensitivity tables
3. **Due Diligence Data Packs** — обработка документов
4. **Company Teasers and Profiles** — обзоры для pitch books
5. **Earnings Analyses** — метрики из транскриптов
6. **Coverage Reports** — отраслевой анализ

### Новые функции (январь 2026)

- **Drag & Drop** нескольких файлов в sidebar
- **Auto-compaction** длинных бесед
- **Overwrite Protection** перед перезаписью данных

### Claude Log Tab

Опциональный лист "Claude Log" с записью всех действий Claude. Единственный audit trail, т.к. chat history НЕ сохраняется.

### Ограничения

| Ограничение | Детали |
|-------------|--------|
| Data tables | Не поддерживаются |
| VBA / Macros | Не поддерживаются |
| Chat history | Не сохраняется между сессиями |
| Audit logs | Не включен в Compliance API |
| Data retention | Enterprise настройки не наследуются |
| Форматы | Только .xlsx и .xlsm |

### Безопасность Excel

**Защищенные функции (pop-up подтверждения):**
- Web services: WEBSERVICE, STOCKHISTORY, TRANSLATE
- Import: IMPORTDATA, IMPORTXML, IMPORTHTML
- Dynamic references: INDIRECT
- Code execution: DDE, CALL, EVALUATE, FORMULA
- File system: IMAGE, FILES, DIRECTORY, FOPEN, FWRITE, FCLOSE
- System info: REGISTER.ID, RTD, INFO

### Примеры промптов

```
"Проанализируй, как изменение revenue growth rate на +2% повлияет на terminal value"
"Найди все ячейки с ошибками #REF! и объясни причины"
"Создай pivot table из данных на листе Sales, сгруппировав по региону и кварталу"
"Добавь conditional formatting: зеленый для >100%, красный для <50%"
"Стандартизируй формат дат во всем workbook в DD/MM/YYYY"
```

---

## Claude in PowerPoint

### Установка

1. [Microsoft Marketplace](https://marketplace.microsoft.com/en-us/product/office/wa200010001) → Get it now
2. Открыть PowerPoint → активировать add-in
3. Войти с аккаунтом Claude (Max/Team/Enterprise)

**ВНИМАНИЕ:** НЕ доступен для Pro плана.

### Template Intelligence

Ключевая особенность — Claude читает:
- Slide master
- Layouts
- Fonts
- Color schemes

И автоматически соблюдает корпоративный брендинг при генерации.

### Возможности

| Категория | Возможности |
|-----------|------------|
| **Создание** | Слайды из текста, deck-структуры, нативные графики (редактируемые!) |
| **Визуализация** | Конвертация буллетов в диаграммы, process flows, charts |
| **Редактирование** | Точечные правки без регенерации, сохранение форматирования |
| **Use cases** | Market sizing (TAM/SAM/SOM), competitive landscape, pitch decks, earnings |

### Ограничения

| Ограничение | Детали |
|-------------|--------|
| Pro план | НЕ включен |
| Chat history | Не сохраняется |
| Audit logs | Не включен в Compliance API |
| Файлы | Только активная презентация |
| Лимит пользователей | ~1000 с расширением (research preview) |

### Примеры промптов

```
"Create a market sizing section — 3 slides covering TAM, SAM, SOM with supporting visuals"
"Turn these bullets into a process flow diagram"
"Create a bar chart comparing Q1-Q4 performance"
"Restructure the deck: move conclusion before appendix, add agenda slide after title"
"Simplify the text on slide 3 and add a supporting chart"
```

---

## Excel → PowerPoint Pipeline

Рекомендуемый Anthropic workflow:
1. Обработать и структурировать данные в **Claude in Excel**
2. Визуализировать в **Claude in PowerPoint**

Пример: анализ финансовых данных в Excel → pitch deck в PowerPoint.

---

## CLI Skills (альтернатива add-in)

### Skill xlsx

**Библиотеки:** openpyxl (формулы), pandas (анализ), LibreOffice (пересчет)

**Color coding (финансовые модели):**

| Цвет текста | Значение |
|-------------|----------|
| Синий (0,0,255) | Хардкодированные inputs |
| Черный (0,0,0) | Формулы и вычисления |
| Зеленый (0,128,0) | Ссылки на другие листы |
| Красный (255,0,0) | Ссылки на внешние файлы |
| Желтый фон | Ключевые assumptions |

**Пересчет формул:**
```bash
python scripts/recalc.py output.xlsx [timeout_seconds]
```

### Skill pptx

**Три режима:**
- Чтение: `python -m markitdown presentation.pptx`
- Редактирование: Unpack XML → Edit → Repack
- Создание: pptxgenjs (Node.js)

**Скрипты:** thumbnail.py, unpack.py, soffice.py

### Сравнение: Add-in vs CLI

| Параметр | Add-in | CLI Skill |
|----------|--------|-----------|
| Интерфейс | Sidebar в Office | Терминал Claude Code |
| Файлы | Один открытый | Любое количество |
| Batch-обработка | Нет | Да |
| Шаблоны | Template Intelligence | XML editing / pptxgenjs |
| Зависимости | Office 2016+ | Python, Node.js, LibreOffice |
| Планы | Pro+ (Excel) / Max+ (PPT) | Любой с Claude Code |
