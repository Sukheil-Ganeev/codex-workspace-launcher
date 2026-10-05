# Excel Report Template (Claude Code + openpyxl)

## Назначение

Шаблон для программного создания Excel-отчетов через Claude Code с использованием библиотек Python. Подходит для автоматической генерации отчетов с данными, формулами, форматированием и графиками.

**Когда использовать:**
- Создание регулярных отчетов (ежедневных, еженедельных, месячных)
- Обработка и визуализация данных из CSV/JSON/API
- Расчет себестоимости, маржинальности, финансовых метрик
- Batch-генерация Excel для нескольких клиентов/периодов

**Два подхода:**
| Подход | Когда | Инструмент |
|--------|-------|-----------|
| **Claude Code CLI** (этот шаблон) | Программная генерация, batch, автоматизация | openpyxl, pandas |
| **Claude in Excel (add-in)** | Интерактивный анализ открытого файла | Sidebar в Excel |

## Шаги

### Шаг 1. Описание данных и структуры

Укажите Claude:
- Источник данных (CSV, JSON, вручную)
- Структуру листов (названия, столбцы)
- Нужные формулы и агрегации
- Форматирование (цвета, шрифты, ширина столбцов)

### Шаг 2. Создание Excel-файла

Claude Code напишет Python-скрипт с использованием openpyxl:

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Отчет"

# --- Заголовки ---
headers = ["Экскурсия", "Продажи", "Выручка (AED)", "Маржа %"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, size=12, color="FFFFFF")
    cell.fill = PatternFill(start_color="2F5496", fill_type="solid")
    cell.alignment = Alignment(horizontal="center")

# --- Данные ---
data = [
    ["Desert Safari", 150, 22500, 0.35],
    ["City Tour", 200, 18000, 0.42],
    ["Abu Dhabi Tour", 80, 16000, 0.28],
    # ...
]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        ws.cell(row=row_idx, column=col_idx, value=value)

# --- Формулы ---
last_row = len(data) + 1
ws.cell(row=last_row + 1, column=1, value="ИТОГО")
ws.cell(row=last_row + 1, column=2).value = f"=SUM(B2:B{last_row})"
ws.cell(row=last_row + 1, column=3).value = f"=SUM(C2:C{last_row})"
ws.cell(row=last_row + 1, column=4).value = f"=AVERAGE(D2:D{last_row})"
```

### Шаг 3. Форматирование

```python
# --- Conditional Formatting ---
from openpyxl.formatting.rule import CellIsRule

# Зеленый если маржа > 30%
green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
ws.conditional_formatting.add(
    f"D2:D{last_row}",
    CellIsRule(operator="greaterThan", formula=["0.30"], fill=green_fill)
)

# Красный если маржа < 15%
red_fill = PatternFill(start_color="FFC7CE", fill_type="solid")
ws.conditional_formatting.add(
    f"D2:D{last_row}",
    CellIsRule(operator="lessThan", formula=["0.15"], fill=red_fill)
)

# --- Форматы чисел ---
for row in ws.iter_rows(min_row=2, max_row=last_row, min_col=3, max_col=3):
    for cell in row:
        cell.number_format = '#,##0.00 "AED"'

for row in ws.iter_rows(min_row=2, max_row=last_row, min_col=4, max_col=4):
    for cell in row:
        cell.number_format = '0.0%'

# --- Ширина столбцов ---
ws.column_dimensions['A'].width = 25
ws.column_dimensions['B'].width = 15
ws.column_dimensions['C'].width = 20
ws.column_dimensions['D'].width = 15
```

### Шаг 4. Графики (опционально)

```python
# --- Bar Chart ---
chart = BarChart()
chart.title = "Выручка по экскурсиям"
chart.y_axis.title = "AED"
chart.x_axis.title = "Экскурсия"

data_ref = Reference(ws, min_col=3, min_row=1, max_row=last_row)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=last_row)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
chart.shape = 4
ws.add_chart(chart, "F2")
```

### Шаг 5. Сохранение

```python
output_path = "D:/Downloads/tour_report_2026_02.xlsx"
wb.save(output_path)
print(f"Отчет сохранен: {output_path}")
```

## Пример промпта

```
Создай Excel-отчет по продажам экскурсий за февраль 2026:

Данные (возьми из файла D:/Downloads/february_sales.csv):
- Название экскурсии
- Количество продаж
- Выручка (AED)
- Себестоимость
- Маржа (рассчитать формулой)

Требования:
1. Лист "Sales" — основная таблица с данными и формулами
2. Лист "Summary" — сводка: топ-5, итоги, средняя маржа
3. Conditional formatting: зеленый если маржа > 30%, красный если < 15%
4. Bar chart: выручка по экскурсиям
5. Pie chart: доля каждой экскурсии в общей выручке
6. Строка итогов: SUM, AVERAGE

Сохрани в D:/Downloads/sales_report_february_2026.xlsx
```

## Параметры для настройки

| Параметр | По умолчанию | Описание |
|----------|-------------|---------|
| `Источник данных` | CSV | CSV, JSON, ручной ввод, API |
| `Количество листов` | 1 | Сколько листов (tabs) в книге |
| `Формулы` | SUM, AVERAGE | Какие Excel-формулы использовать |
| `Conditional formatting` | нет | Правила цветового выделения |
| `Графики` | нет | BarChart, LineChart, PieChart |
| `Формат чисел` | `#,##0.00` | Формат для валют, процентов и т.д. |
| `Путь сохранения` | `D:/Downloads/` | Куда сохранить файл |
| `Библиотека` | openpyxl | openpyxl (гибкость) или pandas (быстрота) |

## Частые ошибки

- **openpyxl не установлен** -- Решение: Claude Code автоматически запустит `pip install openpyxl`. Если не получится: `pip install openpyxl pandas`.

- **Формулы не пересчитываются при открытии** -- Excel не пересчитывает формулы openpyxl автоматически. Решение: при открытии файла нажать Ctrl+Alt+F9 или добавить в скрипт `wb.calculation.calcMode = 'auto'`.

- **Русский текст отображается как кракозябры** -- Решение: openpyxl корректно поддерживает UTF-8 из коробки. Проблема обычно в исходных данных. Проверить encoding CSV: `encoding='utf-8-sig'`.

- **Conditional formatting не видно** -- Решение: убедиться, что диапазон формулы совпадает с диапазоном данных. Проверить формат ячеек (число, не текст).

- **График пустой** -- Решение: проверить, что Reference указывает на правильные строки/столбцы. `min_row=1` если заголовок используется как titles_from_data.

- **Файл слишком большой** -- Решение: для больших датасетов (>100k строк) использовать `openpyxl.Workbook(write_only=True)` для потокового режима.

## Add-in vs CLI: когда что выбрать

| Критерий | Claude in Excel (add-in) | Claude Code CLI (этот шаблон) |
|----------|--------------------------|------------------------------|
| Файл уже открыт | Да, интерактивный | Нет, программный |
| Batch (много файлов) | Нет | Да |
| Сложные формулы | Отличная отладка | Ручная проверка |
| Графики | Нативные Excel | openpyxl (ограничены) |
| Автоматизация | Нет | Да (скрипты, cron) |
| План | Pro+ | Любой с Claude Code |
