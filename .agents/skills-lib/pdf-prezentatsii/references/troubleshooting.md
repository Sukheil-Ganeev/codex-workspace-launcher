# Проблемы конвертации HTML → PDF

## 1. Белый фон вместо цветного

**Причина:** `print_background` не True

**Решение:**
```python
page.pdf(print_background=True, ...)
```

---

## 2. Шрифты не загрузились (системные вместо кастомных)

**Причины:**
- Нет preconnect
- Конвертация до загрузки шрифтов

**Решение:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

```python
page.wait_for_load_state('networkidle')
```

---

## 3. Контент обрезается

**Причина:** Размеры body ≠ размеры PDF

**Решение:** Сверить:
- HTML: `width: 1920px; height: 1080px`
- PDF: `width='1920px', height='1080px'`

---

## 4. Все слайды на одной странице

**Причина:** Нет page-break

**Решение:**
```css
.slide {
    page-break-after: always;
    page-break-inside: avoid;
}
```

---

## 5. Анимации/переходы не работают

**Причина:** PDF статичный формат

**Решение:** Удалить animation, transition, @keyframes, :hover

---

## 6. Файл слишком большой

**Причина:** Высокое разрешение или много изображений

**Решение:**
- Использовать 1920x1080 вместо 4K
- Оптимизировать изображения

---

## 7. Playwright не установлен

**Решение:**
```bash
pip install playwright
playwright install chromium
```

---

## 8. Путь к файлу не работает (Windows)

**Причина:** Обратные слеши

**Решение:**
```python
# Прямые слеши
html_path = 'D:/Downloads/presentation.html'

# file:// протокол
page.goto(f'file:///{html_path}')
```

---

## 9. Градиенты не отображаются

**Причина:** print_background: false или устаревший синтаксис

**Решение:**
```python
page.pdf(print_background=True, ...)
```

```css
/* Современный синтаксис */
background: linear-gradient(135deg, #color1, #color2);
```

---

## 10. Эмодзи не отображаются

**Причина:** Нет шрифта с эмодзи

**Решение:**
```css
font-family: ..., 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
```

---

## 11. Изображения не загрузились

**Причина:** Локальные пути или CORS

**Решение:**
- Использовать абсолютные пути: `file:///D:/path/image.png`
- Или встроить base64: `data:image/png;base64,...`
- Или дождаться загрузки: `page.wait_for_load_state('networkidle')`

---

## 12. Текст выходит за границы слайда

**Причина:** overflow не hidden

**Решение:**
```css
.slide {
    overflow: hidden;
}
```

---

## 13. Разное отображение в браузере и PDF

**Причина:** @media print стили

**Решение:** Проверить, нет ли конфликтующих @media print правил:
```css
@media print {
    /* Убедиться, что стили совпадают */
}
```

---

## 14. Пустые страницы между слайдами

**Причина:** Лишние отступы или margin

**Решение:**
```css
html, body {
    margin: 0;
    padding: 0;
}

.slide {
    margin: 0;
    padding: 0; /* Внутренние отступы через внутренние элементы */
}
```
