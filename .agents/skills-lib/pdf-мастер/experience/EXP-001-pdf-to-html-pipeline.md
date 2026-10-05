# EXP-001: PDF → HTML конвертация каталогов (115 страниц)

**Дата:** 2026-03-16/17
**Проект:** 4 каталога VIP DXB RUS (билеты 61стр, групповые 24, индивидуальные 16, аренда 14)

## Рабочий пайплайн (ПРОВЕРЕННЫЙ)

```
PDF → PyMuPDF метрики (JSON) → абсолютное позиционирование (pt) → HTML
     ↑                          ↑                                    ↑
  print PDF → HD фото      line breaks из bbox              @font-face TTF
```

## Что работает

1. **Извлечение метрик** — `page.get_text("dict")` даёт bbox каждого span/line/block
2. **Координаты в pt** — 1 CSS pt = 1 PDF pt, никакой конвертации
3. **line-height: 14.4pt** — стабильное значение для body текста Montserrat 12pt
4. **Параллельные агенты** — по 15 страниц на агента, метрики + фото + HTML
5. **Высококачественные фото** — из print PDF (4x разрешение vs web PDF)
6. **Принудительные `<br>`** — строки из JSON = строки в HTML

## Критические ошибки (НЕ ПОВТОРЯТЬ)

### 1. Массовые замены CSS
**Проблема:** `css.replace('font-weight: 600', 'font-weight: 500')` меняет ВСЁ включая @font-face
**Решение:** Точечные правки конкретных классов, НИКОГДА replace all

### 2. Шрифтовые метания (7 итераций!)
**Проблема:** 600→700→500→550→600→500→700→600 — каждая итерация ломала другое
**Решение:** Один раз проанализировать через fontTools, принять решение, больше не трогать
**Правильный ответ:** font-weight: 600 для SemiBold (confirmed by fontTools usWeightClass=600)

### 3. letter-spacing/text-stroke ломает layout
**Проблема:** Добавление letter-spacing:-0.2pt сдвигало текст и ломало позиции
**Решение:** НИКОГДА не добавлять letter-spacing/text-stroke для исправления толщины шрифта

### 4. Двойной фон на CTA блоках
**Проблема:** И copper-bar div И CTA-text div имели background — двойной медный блок
**Решение:** Фон только на одном элементе

### 5. "На глаз" вместо метрик
**Проблема:** Высота фото 375pt (вычислена) вместо 355.29pt (из PDF bbox)
**Решение:** ВСЕГДА page.get_image_rects(xref) для изображений

### 6. PyMuPDF flags=20 НЕ означает faux bold
**Проблема:** flags=20 (bold bit) — это интерпретация PyMuPDF названия "SemiBold", НЕ инструкция PDF рендереру
**Правда:** PDF FontDescriptor /Flags=4 (Symbolic), Text Rendering Mode=0 (fill), никакого faux bold
**Решение:** Не доверять span["flags"] для принятия решений о font-weight

## Архитектура файлов

```
catalog-html/           # Билеты (61 стр)
catalog-html-group/     # Групповые (24 стр)
catalog-html-individual/ # Индивидуальные (16 стр)
catalog-html-rental/    # Аренда (14 стр)

Каждая папка:
├── index.html
├── styles.css
├── fonts/ (TTF)
├── images/ (JPG + reference PNG)
└── metrics.json
```

## Дизайн-система каталогов

| Токен | Значение |
|-------|----------|
| Страница | 595.28 x 841.89 pt (A4) |
| Шрифт заголовков | Tenor Sans Regular |
| Шрифт текста | Montserrat Regular 400 / SemiBold 600 |
| Медный акцент | #c48d70 (заголовки), #c48c6f (полоски/CTA) |
| line-height body | 14.4pt |
| Левая колонка | x≈36-47pt |
| Правая колонка | x≈304-316pt |
| Ширина колонки | ≈244pt |

## Медная полоска (copper bar)

- Это drawing rectangle из PDF, НЕ border и НЕ hr
- Ширина: 3 варианта — 243.64pt, 376.96pt, 444.28pt (зависит от страницы)
- Высота: 7pt
- Позиция: ПОД заголовком (не на фото, не на всю ширину)
- Цвет fill: #c48c6f, stroke: #c48c6f, width: 1pt

## Разница рендеринга PDF vs браузер

Браузер (ClearType/DirectWrite) рендерит Montserrat-SemiBold ЖИРНЕЕ чем PDF (Adobe engine).
Это аппаратная разница, НЕ ошибка CSS. Принять как есть.
Не пытаться компенсировать через text-stroke, letter-spacing — это ломает layout.
