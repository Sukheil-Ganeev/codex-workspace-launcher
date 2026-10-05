# EXP-009: Паттерн деанимации HTML для PDF рендеринга

**Дата:** 2026-02-05
**Категория:** Patterns
**Теги:** html, pdf, animations, rendering, puppeteer

---

## Проблема

При конвертации HTML в PDF через Puppeteer анимации и transitions могут вызывать:
- Неправильный рендеринг элементов
- Элементы "застревают" в промежуточном состоянии
- Некорректное позиционирование контента
- Артефакты на финальном PDF

---

## Решение: Деанимация HTML

Перед генерацией PDF необходимо удалить все CSS анимации и transitions из HTML.

### Метод 1: JavaScript в браузере

```javascript
await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
            animation-duration: 0s !important;
            transition-duration: 0s !important;
        }
    `;
    document.head.appendChild(style);
});
```

### Метод 2: CSS файл

Создать `deanimate.css`:

```css
*, *::before, *::after {
    animation: none !important;
    transition: none !important;
    animation-duration: 0s !important;
    transition-duration: 0s !important;
    animation-delay: 0s !important;
    transition-delay: 0s !important;
}
```

Добавить в HTML:
```javascript
await page.addStyleTag({ path: './deanimate.css' });
```

### Метод 3: Модификация HTML перед рендерингом

```javascript
function deanimateHTML(htmlContent) {
    // Добавить CSS в <head>
    const deanimateCSS = `
        <style>
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
        }
        </style>
    `;
    return htmlContent.replace('</head>', `${deanimateCSS}</head>`);
}
```

---

## Когда применять

1. **Всегда** при генерации PDF из HTML с анимациями
2. При использовании UI фреймворков (Vue, React) с transitions
3. Если видны артефакты или "незавершенные" состояния на PDF
4. При работе с reveal.js, impress.js и подобными библиотеками

---

## Полный workflow

```javascript
// 1. Загрузить страницу
await page.goto(url, { waitUntil: 'networkidle0' });

// 2. Деанимация
await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
        }
    `;
    document.head.appendChild(style);
});

// 3. Подождать применения стилей
await page.waitForTimeout(100);

// 4. Генерация PDF
await page.pdf({
    path: 'output.pdf',
    format: 'A4',
    printBackground: true
});
```

---

## Важные замечания

- Деанимацию нужно применять **после** загрузки страницы
- Добавить небольшую задержку (100-200ms) после деанимации
- `!important` обязателен для переопределения inline стилей
- Проверять все псевдоэлементы (`::before`, `::after`)

---

## Результаты применения

**До деанимации:**
- Элементы в промежуточных состояниях
- Артефакты позиционирования
- Непредсказуемый результат

**После деанимации:**
- Стабильный рендеринг
- Все элементы в финальном состоянии
- Чистый PDF без артефактов

---

## Связанные паттерны

- `EXP-001`: Загрузка шрифтов (ждать до рендеринга)
- `EXP-004`: Обработка изображений (те же принципы ожидания)

---

## Checklist

- [ ] Добавлен CSS для деанимации
- [ ] Код выполняется после загрузки страницы
- [ ] Добавлена задержка после деанимации
- [ ] Используется `!important`
- [ ] Проверены псевдоэлементы
- [ ] Протестирован финальный PDF
