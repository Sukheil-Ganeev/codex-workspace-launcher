---
id: EXP-027
date: 2026-02-04
type: pattern
severity: medium
category: images
projects: []
related: [EXP-004, EXP-026, EXP-043]
tags: [images, object-fit, css, playwright, loading]
status: verified
---

# Паттерн: Работа с изображениями в PDF-презентациях

## CSS для обложек книг / карточек

```css
.book-cover {
    width: 420px;
    height: 600px;
    border-radius: 4px;
    object-fit: cover;           /* заполняет область, обрезает края */
    object-position: center top; /* важная часть сверху */
}
```

## Когда какой object-fit

| Ситуация | object-fit | Результат |
|----------|------------|-----------|
| Все изображения одного формата | `contain` | Сохраняет пропорции, возможны поля |
| Разные форматы (квадратные, прямоугольные) | `cover` | Заполняет область, обрезает |
| Нужен точный размер без обрезки | `contain` + background: #f8fafc | Поля сливаются с фоном |

## Загрузка изображений в Playwright

```python
# 1. Дождаться загрузки сети
page.wait_for_load_state('networkidle')

# 2. Дождаться загрузки всех img
page.evaluate('''() => {
    return Promise.all(
        Array.from(document.images)
            .filter(img => !img.complete)
            .map(img => new Promise(resolve => {
                img.onload = img.onerror = resolve;
            }))
    );
}''')

# 3. Пауза для рендеринга
time.sleep(2)
```

## Чеклист перед генерацией PDF

- [ ] Проверить пути к изображениям: `ls covers/`
- [ ] Проверить размеры: `file covers/*.jpg`
- [ ] Квадратные изображения → `object-fit: cover`
- [ ] Белые края → светлый фон
