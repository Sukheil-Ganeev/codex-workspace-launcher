---
id: EXP-033
date: 2026-02-05
type: pattern
severity: medium
category: layout
projects: []
related: []
tags: [slide-numbering, renumbering, reverse-order, html-structure]
status: verified
---

# Массовое обновление нумерации слайдов

## Проблема

При добавлении нового слайда в середину HTML-презентации нужно сдвинуть номера всех последующих слайдов:
- id="slide-3" → id="slide-4"
- slide-num "03 / 26" → "04 / 27"
- комментарии `<!-- SLIDE 3:` → `<!-- SLIDE 4:`

**Ловушка:** Прямой порядок замены (3→4, 4→5, 5→6) создаёт конфликты — slide-4 перезаписывается дважды и содержимое теряется.

## Решение: Обратный порядок

Сдвигать номера от большего к меньшему:

```python
import re

def add_slide_after(html_content, after_slide_num, new_slide_html, total_slides):
    """
    Добавляет новый слайд после указанного номера.

    Args:
        html_content: исходный HTML
        after_slide_num: после какого слайда вставить (например, 2)
        new_slide_html: HTML нового слайда
        total_slides: текущее количество слайдов (например, 26)

    Returns:
        HTML с новым слайдом и обновлённой нумерацией
    """
    content = html_content
    new_total = total_slides + 1
    new_slide_num = after_slide_num + 1

    # ШАГ 1: Обновить общее количество слайдов
    content = content.replace(f'/ {total_slides}<', f'/ {new_total}<')
    content = content.replace(f'/ {total_slides}</span>', f'/ {new_total}</span>')

    # ШАГ 2: Сдвинуть номера в ОБРАТНОМ порядке
    for old_num in range(total_slides, after_slide_num, -1):
        new_num = old_num + 1

        # ID слайда
        content = content.replace(
            f'id="slide-{old_num}"',
            f'id="slide-{new_num}"'
        )

        # Номер в углу слайда (формат 0X для < 10)
        if old_num < 10:
            old_display = f'0{old_num}'
        else:
            old_display = str(old_num)

        if new_num < 10:
            new_display = f'0{new_num}'
        else:
            new_display = str(new_num)

        content = content.replace(
            f'>{old_display} / {new_total}<',
            f'>{new_display} / {new_total}<'
        )

        # Футер слайда
        content = content.replace(
            f'<span>{old_display} / {new_total}</span>',
            f'<span>{new_display} / {new_total}</span>'
        )

        # HTML-комментарии
        content = content.replace(
            f'<!-- SLIDE {old_num}:',
            f'<!-- SLIDE {new_num}:'
        )

    # ШАГ 3: Найти место для вставки (после слайда after_slide_num)
    pattern = rf'(</div>\s*\n\s*<!-- =+\s*-->\s*\n\s*<!-- SLIDE {after_slide_num + 2}:)'
    match = re.search(pattern, content)

    if match:
        insert_pos = match.start()
        content = content[:insert_pos] + '\n</div>\n\n' + new_slide_html + '\n\n' + content[insert_pos + 7:]

    return content
```

## Порядок действий

1. **Сначала** обновить общее количество (/ 26 → / 27)
2. **Затем** сдвинуть в обратном порядке: 26→27, 25→26, ..., 3→4
3. **Потом** вставить новый слайд с номером 3

## Пример использования

```python
# Добавляем слайд методологии после содержания (слайд 2)
new_methodology_slide = '''
<!-- SLIDE 3: METHODOLOGY -->
<div class="slide" id="slide-3">
  <span class="slide-num">03 / 27</span>
  <div class="slide-title">Методология исследования</div>
  ...
</div>
'''

updated_html = add_slide_after(
    html_content=original_html,
    after_slide_num=2,
    new_slide_html=new_methodology_slide,
    total_slides=26
)
```

## Альтернатива: Ручное обновление через Python

Если нужен контроль над каждым шагом:

```python
# Step 1: 26 → 27 слайдов
content = content.replace('/ 26<', '/ 27<')
content = content.replace('/ 26</span>', '/ 27</span>')

# Step 2: Сдвиг (обратный порядок!)
for old_num in range(26, 2, -1):
    new_num = old_num + 1
    content = content.replace(f'id="slide-{old_num}"', f'id="slide-{new_num}"')
    # ... остальные замены
```

## Когда применять

- Добавление слайда "Методология" после содержания
- Добавление слайда "Об авторе" перед финальным
- Вставка нового раздела в существующую презентацию
- Любые модификации структуры презентации

## Реальный пример

Презентация "Islamic AI Assistants":
- v3 → v4: добавлен слайд методологии (26 → 27 слайдов)
- v4 → v5: добавлен слайд "Об авторе" (27 → 28 слайдов)

Путь: `D:/Downloads/Islamic_AI_Presentation_Project/versions/`
