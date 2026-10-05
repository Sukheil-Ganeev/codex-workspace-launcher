---
id: EXP-022
date: 2026-02-04
type: pattern
severity: high
category: layout
projects: []
related: [EXP-001, EXP-011]
tags: [css, padding, font-size, overflow, compactification]
status: verified
---

# Паттерн: Компактификация CSS при переполнении

**ID:** EXP-022
**Дата:** 2026-02-04
**Контекст:** Презентация Claude CLI

## Проблема

Контент слайда выходит за границы фиксированной высоты (1080px):
- Списки с множеством пунктов
- Code-блоки занимают много места
- Таблицы с данными
- Несколько секций на одном слайде

При рендеринге в PDF через Playwright контент обрезается.

## Решение: Компактификация CSS

### Шаг 1: Уменьшить padding контейнера

```css
/* Было: */
.slide {
    padding: 40px 50px;
}

/* Стало: */
.slide {
    padding: 22px 30px;
}
```

### Шаг 2: Уменьшить font-size основного текста

```css
/* Было: */
body { font-size: 36px; }
li { font-size: 28px; }

/* Стало: */
body { font-size: 26px; }
li { font-size: 22px; }
```

### Шаг 3: Уменьшить margin-top заголовков

```css
/* Было: */
.content-area { margin-top: 100px; }
h2 { margin-bottom: 40px; }

/* Стало: */
.content-area { margin-top: 70px; }
h2 { margin-bottom: 25px; }
```

### Шаг 4: Уменьшить line-height (осторожно!)

```css
/* Было: */
body { line-height: 1.6; }

/* Стало: */
body { line-height: 1.4; }
```

## Таблица компактификации

| Свойство | Стандарт | Компакт | Ультра-компакт |
|----------|----------|---------|----------------|
| padding | 40-50px | 22-30px | 15-20px |
| font-size body | 36px | 26px | 22px |
| font-size li | 28px | 22px | 18px |
| margin-top | 100px | 70px | 50px |
| line-height | 1.6 | 1.4 | 1.3 |
| gap в grid | 30px | 20px | 15px |

## Когда применять

1. **Много контента на слайде** - списки > 6 пунктов
2. **Code-блоки** - особенно многострочные
3. **Таблицы** - > 5 строк
4. **Комбинированные слайды** - несколько секций

## Проверка результата

```python
# В Playwright проверить высоту контента
content_height = page.evaluate('''() => {
    const slide = document.querySelector('.slide');
    return slide.scrollHeight;
}''')

if content_height > 1080:
    print(f"WARN: Контент переполнен на {content_height - 1080}px")
```

## Связанные файлы

- `_index.md` — урок #6
- `fixes/EXP-001-body-height-overflow.md` — исходная проблема overflow
