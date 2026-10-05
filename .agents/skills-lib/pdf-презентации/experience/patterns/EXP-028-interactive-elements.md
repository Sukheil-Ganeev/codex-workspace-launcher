---
id: EXP-028
date: 2026-02-05
type: pattern
severity: high
category: conversion
projects: []
related: [EXP-029, EXP-031]
tags: [interactive, tabs, screenshots, playwright, coverage]
status: verified
---

# Клик по интерактивным элементам для полного покрытия

**ID:** EXP-028
**Дата:** 2026-02-05
**Контекст:** MCP Presentation — каталог с 8 табами, но скриншот только первого

---

## Проблема

В презентации есть интерактивные элементы (табы, кнопки, фильтры, аккордеоны). При генерации PNG/PDF попадает только **видимое состояние**, остальной контент **теряется**.

**Пример из MCP Presentation:**
- Каталог серверов с 8 категориями (табы)
- По умолчанию видна только "Туризм"
- В PNG попало 6 слайдов вместо 13
- Потеряны: CRM, Формы, Коммуникации, Аналитика, Базы данных, Скрапинг, Google Workspace

**Исходная ошибка:**
```python
# НЕПРАВИЛЬНО — только видимый контент
section = page.query_selector('#catalog')
section.screenshot(path='slide_catalog.png')  # Только Туризм!
```

---

## Решение

Автоматический клик по всем интерактивным элементам + скриншот каждого состояния:

```python
# Категории каталога
catalog_categories = [
    ('tourism', 'Туризм'),
    ('crm', 'CRM'),
    ('forms', 'Формы'),
    ('comms', 'Коммуникации'),
    ('analytics', 'Аналитика'),
    ('database', 'Базы данных'),
    ('scraping', 'Скрапинг'),
    ('google', 'Google Workspace')
]

for cat_id, cat_name in catalog_categories:
    # Найти и кликнуть на кнопку категории
    button_selector = f'button.catalog-btn[onclick*="{cat_id}"]'
    page.click(button_selector)

    time.sleep(0.3)  # Подождать переключение/анимацию

    # Сделать скриншот этой категории
    section.screenshot(path=f'slide_catalog_{cat_id}.png')
    print(f'[OK] Каталог: {cat_name}')
```

---

## Универсальные паттерны

### 1. Табы (Bootstrap/Custom)

```python
# Bootstrap tabs
tabs = page.query_selector_all('.nav-tabs .nav-link')
for i, tab in enumerate(tabs):
    tab.click()
    time.sleep(0.2)
    content = page.query_selector('.tab-content .tab-pane.active')
    content.screenshot(path=f'tab_{i}.png')

# Custom tabs с onclick
tab_ids = ['tab1', 'tab2', 'tab3']
for tab_id in tab_ids:
    page.click(f'[data-tab="{tab_id}"]')
    time.sleep(0.2)
    page.screenshot(path=f'{tab_id}.png')
```

### 2. Аккордеоны

```python
# Раскрыть все аккордеоны
accordions = page.query_selector_all('.accordion-button')
for i, btn in enumerate(accordions):
    if 'collapsed' in btn.get_attribute('class'):
        btn.click()
        time.sleep(0.2)

# Скриншот с раскрытыми секциями
page.screenshot(path='accordion_expanded.png')
```

### 3. Фильтры/Dropdown

```python
# Все варианты фильтра
filter_options = ['all', 'active', 'completed', 'pending']
for option in filter_options:
    page.select_option('select.filter', value=option)
    time.sleep(0.3)
    page.screenshot(path=f'filter_{option}.png')
```

### 4. Модальные окна

```python
# Открыть и заскриншотить модалки
modal_triggers = page.query_selector_all('[data-bs-toggle="modal"]')
for i, trigger in enumerate(modal_triggers):
    trigger.click()
    time.sleep(0.3)
    modal = page.query_selector('.modal.show .modal-content')
    modal.screenshot(path=f'modal_{i}.png')
    page.click('.modal .btn-close')  # Закрыть
    time.sleep(0.2)
```

---

## Полный рабочий код (из MCP Presentation)

```python
def capture_all_catalog_categories(page, section, output_dir, slide_num):
    """Захватывает все категории каталога."""

    catalog_categories = [
        ('tourism', 'Туризм'),
        ('crm', 'CRM'),
        ('forms', 'Формы'),
        ('comms', 'Коммуникации'),
        ('analytics', 'Аналитика'),
        ('database', 'Базы данных'),
        ('scraping', 'Скрапинг'),
        ('google', 'Google Workspace')
    ]

    slides_created = []

    for cat_id, cat_name in catalog_categories:
        # Кликнуть на кнопку категории
        button_selector = f'button.catalog-btn[onclick*="{cat_id}"]'
        page.click(button_selector)

        time.sleep(0.3)  # Анимация переключения

        # Скриншот
        filename = f'slide_{slide_num:02d}_catalog_{cat_id}.png'
        filepath = os.path.join(output_dir, filename)
        section.screenshot(path=filepath)

        slides_created.append((filename, cat_name))
        slide_num += 1

        print(f'[OK] {filename} - {cat_name}')

    return slides_created, slide_num
```

---

## Диагностика

**Проверьте наличие интерактивных элементов:**

```python
# Поиск интерактивных элементов
tabs = page.query_selector_all('.nav-tabs, .tabs, [role="tablist"]')
buttons = page.query_selector_all('button[onclick], [data-toggle]')
accordions = page.query_selector_all('.accordion, [data-accordion]')

print(f'Tabs: {len(tabs)}')
print(f'Interactive buttons: {len(buttons)}')
print(f'Accordions: {len(accordions)}')
```

**Признаки проблемы:**
- PNG меньше чем ожидалось
- В презентации явно есть табы/категории
- Контент "скрыт" (opacity: 0, display: none)

---

## Когда применять

- Презентации с табами/категориями
- Каталоги продуктов с фильтрами
- FAQ с аккордеонами
- Dashboards с переключателями
- Любые страницы с `onclick`, `data-toggle`, `role="tablist"`

---

## Результат

**До:** 6 слайдов (только видимый контент)
**После:** 13 слайдов (все 8 категорий каталога + остальные секции)

---

## Связанные паттерны

- `landscape-pdf-orientation.md` — правильная ориентация PDF
- `deanimate-html.md` — деанимация перед конвертацией
