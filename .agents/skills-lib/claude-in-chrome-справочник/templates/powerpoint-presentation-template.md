# PowerPoint Presentation Template (Claude Code + python-pptx)

## Назначение

Шаблон для программного создания PowerPoint-презентаций через Claude Code. Подходит для автоматической генерации слайдов с текстом, таблицами, графиками и брендированным дизайном.

**Когда использовать:**
- Создание коммерческих предложений для клиентов
- Генерация отчетных презентаций из данных
- Batch-создание презентаций для разных клиентов/проектов
- Презентации с корпоративным шаблоном

**Два подхода:**
| Подход | Когда | Инструмент |
|--------|-------|-----------|
| **Claude Code CLI** (этот шаблон) | Программная генерация, batch, автоматизация | python-pptx |
| **Claude in PowerPoint (add-in)** | Интерактивная работа в открытом файле | Sidebar в PowerPoint |

**Важно:** Claude in PowerPoint add-in доступен только на Max/Team/Enterprise (НЕ Pro!).

## Шаги

### Шаг 1. Описание контента и структуры

Укажите Claude:
- Тему и назначение презентации
- Количество и содержание слайдов
- Шаблон/бренд (если есть .pptx шаблон)
- Нужные визуальные элементы (таблицы, графики, изображения)

### Шаг 2. Создание презентации

Claude Code напишет Python-скрипт:

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData

# --- Инициализация ---
# С шаблоном:
# prs = Presentation("D:/Downloads/template.pptx")
# Без шаблона:
prs = Presentation()
prs.slide_width = Inches(13.333)   # Widescreen 16:9
prs.slide_height = Inches(7.5)
```

### Шаг 3. Титульный слайд

```python
slide_layout = prs.slide_layouts[0]  # Title Slide
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Экскурсии по ОАЭ"
title.text_frame.paragraphs[0].font.size = Pt(40)
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x2F, 0x54, 0x96)

subtitle = slide.placeholders[1]
subtitle.text = "Индивидуальные и групповые программы\nДубай | Абу-Даби | Шарджа"
```

### Шаг 4. Контентные слайды

```python
# --- Слайд с буллетами ---
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)
slide.shapes.title.text = "Наши услуги"

body = slide.placeholders[1]
tf = body.text_frame
tf.clear()

services = [
    ("Городские туры", "Обзорные экскурсии по Дубаю и Абу-Даби"),
    ("Джип-сафари", "Утреннее, вечернее, ночное сафари в пустыне"),
    ("Парки развлечений", "Билеты по ценам ниже кассы"),
    ("VIP-программы", "Индивидуальные маршруты под запрос"),
]

for i, (title_text, desc) in enumerate(services):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = f"{title_text} — {desc}"
    p.font.size = Pt(18)
    p.level = 0
```

### Шаг 5. Таблица

```python
# --- Слайд с таблицей ---
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank
slide.shapes.title.text = "Прайс-лист"

rows, cols = 5, 4
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.8), Inches(11), Inches(4)).table

# Заголовки
headers = ["Экскурсия", "Длительность", "Цена (AED)", "Цена (USD)"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.bold = True
        paragraph.font.size = Pt(14)
        paragraph.font.color.rgb = RGBColor(255, 255, 255)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x2F, 0x54, 0x96)

# Данные
pricing = [
    ["Desert Safari", "6 часов", "180", "49"],
    ["City Tour Dubai", "4 часа", "150", "41"],
    ["Abu Dhabi Full Day", "10 часов", "250", "68"],
    ["Yacht Cruise", "3 часа", "350", "95"],
]
for r, row_data in enumerate(pricing, 1):
    for c, val in enumerate(row_data):
        table.cell(r, c).text = val
```

### Шаг 6. График

```python
# --- Слайд с графиком ---
slide = prs.slides.add_slide(prs.slide_layouts[5])

chart_data = CategoryChartData()
chart_data.categories = ["Desert Safari", "City Tour", "Abu Dhabi", "Yacht"]
chart_data.add_series("Продажи (шт.)", (150, 200, 80, 45))
chart_data.add_series("Выручка (тыс. AED)", (27, 30, 20, 15.75))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(1), Inches(1.5), Inches(11), Inches(5.5),
    chart_data
).chart

chart.has_legend = True
chart.legend.include_in_layout = False
```

### Шаг 7. Сохранение

```python
output_path = "D:/Downloads/UAE_Tours_Presentation.pptx"
prs.save(output_path)
print(f"Презентация сохранена: {output_path}")
```

## Пример промпта

```
Создай 8-слайдовую презентацию для корпоративного клиента:

1. Титульный слайд: "Dubai Experience Package — [Company Name]"
2. О нас: семейный бизнес, 3 направления (экскурсии, яхты, авто)
3. Экскурсии: список с описаниями и ценами (таблица)
4. Яхты: Paramount Yachts, 300+ яхт, кейтеринг
5. VIP-трансферы: люкс и спорт-кары, аренда
6. График: сравнение наших цен vs конкуренты (bar chart)
7. Отзывы клиентов: 3-4 цитаты
8. Контакты: офис Tecom, телефон, WhatsApp, email

Цветовая схема: темно-синий (#2F5496) + золотой (#C4961A)
Формат: 16:9 Widescreen
Сохрани в D:/Downloads/corporate_proposal.pptx
```

## Параметры для настройки

| Параметр | По умолчанию | Описание |
|----------|-------------|---------|
| `Шаблон` | нет | Путь к .pptx шаблону с корпоративным дизайном |
| `Формат` | 16:9 | 16:9 (widescreen) или 4:3 (standard) |
| `Количество слайдов` | 8 | Сколько слайдов создать |
| `Цветовая схема` | синий/белый | Основной и акцентный цвета (HEX) |
| `Шрифт заголовков` | Calibri | Шрифт для заголовков |
| `Шрифт текста` | Calibri | Шрифт для основного текста |
| `Графики` | нет | Типы графиков: bar, line, pie |
| `Путь сохранения` | `D:/Downloads/` | Куда сохранить файл |

## Частые ошибки

- **python-pptx не установлен** -- Решение: Claude Code автоматически установит `pip install python-pptx`. Если нужны графики из pandas: `pip install python-pptx matplotlib pandas`.

- **Текст выходит за границы слайда** -- Решение: использовать `text_frame.word_wrap = True` и проверять длину текста. Уменьшить font.size при длинных строках.

- **Шаблон не применяется** -- Решение: `Presentation("path/to/template.pptx")` при инициализации. Шаблон должен иметь определенные slide_layouts. Проверить доступные: `for i, layout in enumerate(prs.slide_layouts): print(i, layout.name)`.

- **График не отображается в PowerPoint** -- Решение: python-pptx создает нативные PowerPoint-графики. Если данные пустые -- график будет пустым. Проверить, что CategoryChartData заполнен.

- **Кириллица в графиках отображается некорректно** -- Решение: python-pptx поддерживает UTF-8. Проблема может быть в шрифте. Явно указать шрифт: `chart.font.name = "Arial"`.

- **Нужны изображения на слайдах** -- Решение: `slide.shapes.add_picture("path/to/image.png", Inches(1), Inches(1), Inches(4), Inches(3))`. Изображение должно существовать локально.

## Add-in vs CLI: когда что выбрать

| Критерий | Claude in PowerPoint (add-in) | Claude Code CLI (этот шаблон) |
|----------|-------------------------------|------------------------------|
| Файл уже открыт | Да, интерактивный | Нет, программный |
| Template Intelligence | Да (читает slide master) | Ручное кодирование |
| Нативные графики | Да (редактируемые) | Да (python-pptx) |
| Batch (много файлов) | Нет | Да |
| Доступность | Max/Team/Enterprise | Любой план с Claude Code |
| Точечные правки | Да (без регенерации) | Весь файл пересоздается |
