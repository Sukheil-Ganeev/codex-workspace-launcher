---
name: pdf-prezentatsii
description: "Конвертация HTML презентаций в PDF через Playwright"
---
# СОЗДАНИЕ PDF ПРЕЗЕНТАЦИЙ

## СВЯЗАННЫЕ СКИЛЛЫ

| Скилл | Когда использовать |
|-------|-------------------|
| `frontend-design` | Для создания HTML дизайна презентации |
| `EnterPlanMode` | Для сложных презентаций с многими слайдами |

**Интеграция с командными скиллами:**
Этот скилл автоматически активируется при Волне 4 (презентация) в проектах
скиллов `командная-работа` и `командная-работа-справочники`. Тиммейты
html-css-developer и presentation-finalizer ОБЯЗАНЫ загрузить этот скилл.

---

## РАБОЧИЙ ПРОЦЕСС

### Простая презентация (до 5 слайдов)
1. Создать HTML с `frontend-design`
2. Применить технические правила (этот скилл)
3. Конвертировать в PDF

### Сложная презентация (6+ слайдов)
1. **Планирование** — использовать `EnterPlanMode`
   - Определить структуру слайдов
   - Выбрать формат (16:9, A4)
   - Согласовать с пользователем
2. **Дизайн** — использовать `frontend-design`
   - Создать HTML презентацию
   - Дизайн под запрос пользователя
3. **Конвертация** — этот скилл
   - Применить технические правила
   - Конвертировать через Playwright

---

## БЫСТРЫЙ ПРОЦЕСС

1. **Создать HTML** — статичная презентация (через `frontend-design`)
2. **Применить технические правила** — размеры, page-break, без анимаций
3. **Конвертировать** — Playwright page.pdf()

---

## РАЗДЕЛ 1: РАЗМЕРЫ

### Стандартные форматы

| Формат | Пиксели | Применение |
|--------|---------|------------|
| 16:9 HD | 1920x1080px | Экраны, проекторы (по умолчанию) |
| 16:9 4K | 3840x2160px | Высокое разрешение |
| 4:3 | 1440x1080px | Старые проекторы |
| A4 Landscape | 297mm × 210mm | Печать |
| A4 Portrait | 210mm × 297mm | Документы |

### КРИТИЧЕСКОЕ ПРАВИЛО: Размеры слайдов

⚠️ **ВАЖНО: НЕ фиксировать height на body для многостраничных PDF!**

HTML:
```css
/* ✅ ПРАВИЛЬНО — body без фиксированной высоты */
html, body {
    width: 1920px;
    margin: 0;
    padding: 0;
    /* НЕ указывать height и overflow: hidden! */
}

/* Высоту фиксируем ТОЛЬКО на слайдах */
.slide {
    width: 1920px;
    height: 1080px;
    page-break-after: always;
    page-break-inside: avoid;
}
```

```css
/* ❌ НЕПРАВИЛЬНО — скроет все слайды кроме первого */
html, body {
    width: 1920px;
    height: 1080px;    /* ← УБРАТЬ! */
    overflow: hidden;  /* ← УБРАТЬ! */
}
```

Playwright:
```python
page.pdf(
    width='1920px',
    height='1080px',  # Это размер ОДНОЙ страницы PDF
    margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
)
```

**Логика:** Body должен растягиваться под все слайды, а page-break-after разбивает их на страницы.

---

## РАЗДЕЛ 2: РАЗБИВКА НА СЛАЙДЫ

### page-break правила

```css
.slide {
    width: 1920px;
    height: 1080px;
    page-break-after: always;
    page-break-inside: avoid;
}

.slide:last-child {
    page-break-after: auto;
}
```

### Структура HTML

```html
<body>
    <div class="slide"><!-- Слайд 1 --></div>
    <div class="slide"><!-- Слайд 2 --></div>
    <div class="slide"><!-- Слайд 3 --></div>
</body>
```

---

## РАЗДЕЛ 3: ЗАПРЕЩЕНО В CSS

### Не работает в PDF:

| Свойство | Почему |
|----------|--------|
| animation | PDF статичный |
| transition | PDF статичный |
| @keyframes | PDF статичный |
| :hover | Нет интерактивности |
| position: fixed | Ломает page-break |
| vh, vw | Непредсказуемо — использовать px |

### Удалить перед конвертацией:

```css
/* ❌ УДАЛИТЬ */
animation: fadeIn 0.5s ease;
transition: all 0.3s ease;
@keyframes fadeIn { ... }
.button:hover { ... }
```

---

## РАЗДЕЛ 4: PLAYWRIGHT КОНВЕРТАЦИЯ

### Базовый скрипт

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Загрузка HTML
    page.goto(f'file:///{html_path}')

    # Ждать загрузки ресурсов (шрифты, изображения)
    page.wait_for_load_state('networkidle')

    # Конвертация
    page.pdf(
        path='output.pdf',
        width='1920px',
        height='1080px',
        print_background=True,  # КРИТИЧНО для фона!
        margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
    )

    browser.close()
```

### Параметры page.pdf()

| Параметр | Тип | Описание | ВАЖНО |
|----------|-----|----------|-------|
| path | str | Путь сохранения | |
| width | str | Ширина | Должна = body width |
| height | str | Высота | Должна = body height |
| print_background | bool | Печатать фон | **True — иначе белый фон!** |
| margin | dict | Отступы | {'top': '0', ...} |
| format | str | Формат бумаги | 'A4', 'Letter' |
| landscape | bool | Альбомная | True/False |

### Размеры для форматов

```python
# 16:9 Full HD
page.pdf(width='1920px', height='1080px', ...)

# 16:9 4K
page.pdf(width='3840px', height='2160px', ...)

# 4:3
page.pdf(width='1440px', height='1080px', ...)

# A4 Landscape
page.pdf(format='A4', landscape=True, ...)

# A4 Portrait
page.pdf(format='A4', landscape=False, ...)
```

---

## РАЗДЕЛ 5: ЧЕК-ЛИСТ

### Перед конвертацией проверить:

- [ ] **Размеры body** совпадают с параметрами PDF
- [ ] **print_background: True** — иначе фон белый
- [ ] **margin: 0** — и в CSS, и в page.pdf()
- [ ] **page-break-after: always** на каждом слайде
- [ ] **Нет animation/transition/@keyframes**
- [ ] **Нет :hover эффектов**
- [ ] **wait_for_load_state('networkidle')** — ждать загрузки шрифтов

### Если шрифты Google Fonts:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

---

## РАЗДЕЛ 6: СОВМЕСТИМОСТЬ С APPLE (Mac/iOS)

### ⚠️ КРИТИЧНО: Apple Preview не поддерживает часть CSS!

PDF отображается через Preview.app (не Chrome), поэтому многие CSS свойства ломаются.

### Что НЕ работает в Apple Preview:

| CSS свойство | Проблема | Решение |
|--------------|----------|---------|
| `conic-gradient()` | Серый круг без цветов | Заменить на SVG секторы |
| `backdrop-filter: blur()` | Белые квадраты | Заменить на rgba() с opacity |
| Сложные SVG с gradients | Артефакты | Упростить или убрать |
| `box-shadow` с blur > 20px | Квадраты | Уменьшить blur до 12px |

### Решение: SVG вместо conic-gradient

```css
/* ❌ НЕ РАБОТАЕТ на Apple */
.season-ring {
    background: conic-gradient(green 0deg 90deg, orange 90deg 180deg, ...);
}
```

```html
<!-- ✅ РАБОТАЕТ везде — SVG секторы -->
<svg viewBox="0 0 500 500">
    <path d="M250,250 L250,0 A250,250 0 0,1 500,250 Z" fill="#8bc34a" opacity="0.3"/>
    <path d="M250,250 L500,250 A250,250 0 0,1 250,500 Z" fill="#4a7c23" opacity="0.3"/>
    <path d="M250,250 L250,500 A250,250 0 0,1 0,250 Z" fill="#d4762c" opacity="0.3"/>
    <path d="M250,250 L0,250 A250,250 0 0,1 250,0 Z" fill="#6b8fa3" opacity="0.3"/>
</svg>
```

### Решение: Убрать backdrop-filter

```css
/* ❌ НЕ РАБОТАЕТ — белые квадраты */
.card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
}

/* ✅ РАБОТАЕТ — просто увеличить opacity */
.card {
    background: rgba(255, 255, 255, 0.25);
    /* backdrop-filter убрать */
}
```

---

## РАЗДЕЛ 7: ВСТРАИВАНИЕ ШРИФТОВ (кросс-платформенность)

### Проблема: Квадратики вместо текста на Mac

Google Fonts загружаются по ссылке, но **не встраиваются** в PDF. На Windows шрифты могут быть локально, на Mac — нет.

### Решение: Base64 embedded fonts

```python
import base64

def load_font_base64(font_path):
    with open(font_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Скачать шрифты
# curl "https://fonts.gstatic.com/s/nunito/v32/..." -o fonts/nunito-400.ttf

font_data = load_font_base64('fonts/nunito-400.ttf')

font_css = f"""
@font-face {{
    font-family: 'Nunito';
    font-weight: 400;
    src: url(data:font/truetype;base64,{font_data}) format('truetype');
}}
"""
```

### Получение URL шрифтов Google Fonts

```bash
# Запросить CSS с User-Agent браузера
curl -s "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700" \
  -H "User-Agent: Mozilla/5.0"

# Вывод содержит URL .ttf файлов — скачать их
```

### Структура шрифтов в проекте

```
project/
├── fonts/
│   ├── nunito-400.ttf
│   ├── nunito-700.ttf
│   ├── merriweather-700.ttf
│   └── merriweather-900.ttf
├── presentation.html
└── convert_to_pdf.py
```

---

## РАЗДЕЛ 8: ТИПИЧНЫЕ ОШИБКИ

| Проблема | Причина | Решение |
|----------|---------|---------|
| Белый фон | print_background: false | `print_background=True` |
| Шрифты системные | Не дождались загрузки | `wait_for_load_state('networkidle')` |
| Контент обрезается | Размеры body ≠ PDF | Сверить width/height |
| Всё на одной странице | Нет page-break | `page-break-after: always` |
| **Только 1 слайд виден** | `height` и `overflow:hidden` на body | **Убрать height/overflow с body!** |
| Анимации не работают | PDF статичный | Удалить animation/transition |
| **Квадратики на Mac** | Шрифты не встроены | Встроить через base64 |
| **Диаграмма серая на Mac** | conic-gradient | Заменить на SVG |
| **Белые квадраты за элементами** | backdrop-filter | Убрать, использовать rgba |

### ⚠️ Самая частая ошибка: только первый слайд

```css
/* ❌ ТАК НЕЛЬЗЯ — скроет слайды 2, 3, 4... */
body {
    height: 1080px;
    overflow: hidden;
}

/* ✅ ТАК ПРАВИЛЬНО */
body {
    width: 1920px;
    margin: 0;
    /* height и overflow НЕ указываем! */
}

.slide {
    height: 1080px;  /* Высота только на слайдах */
    page-break-after: always;
}
```

---

## РАЗДЕЛ 9: ВЫБОР ФОРМАТА

| Сценарий | Формат | Размер |
|----------|--------|--------|
| Показ на экране/проекторе | 16:9 | 1920x1080px |
| Печать | A4 Landscape | 297mm × 210mm |
| Старое оборудование | 4:3 | 1440x1080px |
| Высокое качество | 16:9 4K | 3840x2160px |

**По умолчанию:** 16:9 (1920x1080) — универсальный формат.

---

## РАЗДЕЛ 10: ПРИМЕР РАБОЧЕГО ПРОЦЕССА

### Пользователь: "Создай PDF презентацию про MCP серверы"

**Шаг 1: Оценка сложности**
- Сколько слайдов? → Много, значит план
- Нужен ли особый дизайн? → Да → `frontend-design`

**Шаг 2: Планирование (EnterPlanMode)**
```
Слайды:
1. Титульный — название, автор
2. Что такое MCP — определение
3. Архитектура — диаграмма
4. Категории серверов — таблица
5. Примеры конфигов — код
6. Финальный — контакты
```

**Шаг 3: Создание HTML (frontend-design)**
- Дизайн под запрос (темная/светлая/цветная тема)
- Шрифты по желанию
- Визуальные элементы

**Шаг 4: Применение технических правил (этот скилл)**
- Удалить анимации
- Добавить page-break-after
- Проверить размеры body = PDF

**Шаг 5: Конвертация**
```python
page.pdf(width='1920px', height='1080px', print_background=True, ...)
```

---

## РАЗДЕЛ 11: РАБОТА С ИЗОБРАЖЕНИЯМИ

### Проблема

Прямое скачивание (`curl`, `wget`) блокируется hotlinking protection.

### Решение: Бесплатные API стоков

| Сервис | Лимит | Ключ |
|--------|-------|------|
| **Pexels** | 200/час | pexels.com/api/ |
| **Unsplash** | 50/час | unsplash.com/developers |
| **Pixabay** | 100/мин | pixabay.com/api/docs/ |

```python
import requests
r = requests.get('https://api.pexels.com/v1/search',
    params={'query': 'topic', 'per_page': 3},
    headers={'Authorization': 'YOUR_KEY'})
url = r.json()['photos'][0]['src']['large2x']
```

Полный скрипт: `scripts/image_downloader.py`

### Zero-dependency альтернатива (рекомендуется)

CSS gradients + `filter: blur()` на div'ах — 0 проблем, 0 API ключей. → EXP-019

---

## РАЗДЕЛ 12: ZERO-DEPENDENCY ПОДХОД (рекомендуемый)

### Принцип: 0 сетевых запросов = 0 проблем

Вместо внешних зависимостей использовать встроенные ресурсы:

| Вместо | Использовать |
|--------|-------------|
| Google Fonts | Системные: `'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif` |
| Font Awesome / иконки | Inline SVG (5-10 строк на иконку) |
| Фоновые изображения | CSS gradients + `filter: blur()` на div'ах |
| JS-библиотеки графиков | CSS-only диаграммы (flexbox + width%) |

### CSS Ambient Glow (замена фоновых изображений)

```css
.bg-decoration {
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);  /* Работает в PDF! (не backdrop-filter) */
    opacity: 0.15;
    z-index: 0;
}
```

```html
<div class="bg-decoration" style="width: 600px; height: 600px;
     background: #e74c3c; top: -200px; left: -150px;"></div>
```

### Flexbox для вертикального распределения

```css
.slide { display: flex; flex-direction: column; padding: 70px 100px; }
.slide-content { flex: 1; display: flex; flex-direction: column; }
.highlight-box { margin-top: auto; }  /* Прижать к низу слайда */
```

### CSS переменные как дизайн-система

```css
:root {
    --bg-slide: #0f1535;
    --red-ocean: #e74c3c;
    --red-glow: rgba(231, 76, 60, 0.3);  /* Для фонов/теней */
    --text-primary: #ffffff;
    --text-secondary: #a0aec0;
}
```

**Когда применять:** По умолчанию для любой презентации, если нет строгих требований к брендовому шрифту.
**Детали:** `experience/patterns/zero-dependency-presentation.md`

---

## РАЗДЕЛ 13: СЕРИЯ СПРАВОЧНИКОВ

> Полная документация серии (CSS-компоненты, метрики, палитры, 28 правил, 24 проекта):
> **→ [references/handbook-series.md](references/handbook-series.md)**

### Чеклист нового справочника (быстрый старт)

1. Читать SKILL.md справочника → `Skill(название-справочник)`
2. Создать директорию: `mkdir -p "D:/Downloads/Skill_Presentations/название/output"`
3. Скопировать CSS-базу из готового справочника → поменять `:root` палитру
4. Конвертировать: `python _shared/convert_to_pdf.py "../название/"`
5. Проверить PDF: обрезка контента, читаемость, размер файла

### Конвертер серии

```python
# D:/Downloads/Skill_Presentations/_shared/convert_to_pdf.py
# Запуск: python convert_to_pdf.py "../название-справочника/"
```

**Формат:** 1920×1080, 16-20 слайдов, zero-dependency, ~4-5 MB
**Путь серии:** `D:/Downloads/Skill_Presentations/`

---

## ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- `references/troubleshooting.md` — проблемы конвертации
- `references/cheatsheet.md` — быстрая справка
- `references/theme-palettes.md` — все тема-палитры (Neon Wire, WhatsApp Encrypted, Video Stream, Search Radar, Puzzle Blueprint, Scenario Graph, Channel Pulse, Cash Flow)
- `scripts/convert-to-pdf.py` — CLI скрипт конвертации
- `scripts/image_downloader.py` — скачивание изображений через API

---

## КОГДА КАКОЙ СКИЛЛ

| Задача | Скилл |
|--------|-------|
| Создать красивый HTML | `frontend-design` |
| Спланировать сложную презентацию | `EnterPlanMode` |
| Конвертировать HTML → PDF | `pdf-презентации` (этот) |
| Редактировать существующий PDF | `document-skills:pdf` |

---

## НАКОПЛЕННЫЙ ОПЫТ

**Перед началом работы прочитай:** `experience/_index.md`

Содержит критические уроки:
- EXP-001: Проблема "только первый слайд" — решение про body height
- EXP-002: Белый фон — print_background=True
- EXP-003: Шрифты не загружаются — networkidle
- **EXP-004: Квадратики на Mac** — встроить шрифты через base64
- **EXP-005: conic-gradient на Apple** — заменить на SVG секторы
- **EXP-006: backdrop-filter** — убрать, использовать solid rgba
- **EXP-019: Zero-Dependency** — системные шрифты + inline SVG + CSS ambient glow = 0 проблем
- **EXP-025: Масштабирование шрифтов** — для 1920x1080 начинать с увеличенных размеров
- **EXP-026: Серия справочников** — единая дизайн-система, тема через CSS-переменные
- **EXP-030: SVG feTurbulence** — noise-текстура раздувает PDF x2.5, не использовать
- **EXP-031: Gradient borders** — mask-composite + таблицы в карточках, card top shine
- **EXP-032: VK Video тема** — player mockup, play button с ripple, LIVE badge, 3-цветная палитра
- **EXP-033: Тени на тёмном фоне** — убирать box-shadow, нейтральные бордеры, opt-in неон
- **EXP-034: split-40-60 vs split-50-50** — bar chart выпирает в широкой колонке
- **EXP-035: four-grid align-items** — stretch (одинаковая высота) vs start (разная)
- **EXP-036: Пустое пространство** — обёртка в .card + highlight-box для баланса колонок
- **EXP-037: YouTube Premium Design v2** — deco layers, code badges, section icons, gradient text
- **EXP-038: CSS gradients на card/code-block** — раздувают PDF в 3x! Solid borders вместо gradient
- **EXP-039: code-note** — описание перед code-block для контекста (юзабилити)
- **EXP-040: Code-block bg** — тонировать под тему (не чёрный #010409), + muted dots
- **EXP-041: Data Vault тема** — SQL syntax, ERD SVG, 3.8 MB
- **EXP-042: FinTech Vault тема** — payment-flow, currency-badge, card-mockup, status-indicator
- **EXP-048: WhatsApp Encrypted тема** — enc-hex декорации, doodle-bg wallpaper, wa-bubble + wa-check, wa-template preview, 2.8 MB
- **EXP-051: Visual enrichment system** — glow blobs (filter:blur 120px, 2/slide), semantic card variants (card-green/teal/blue/warn с left-border 3px), gradient text на accent spans, section-label::before bar, code-block::after teal strip, code-lang teal badge. PDF 3→9.6 MB. НЕ использовать linear-gradient на card/highlight-box backgrounds (EXP-038)
- **EXP-053: Highlight-box слипание** — `flex: 1` на grid + `margin-top: auto` на highlight-box = 0px gap. Решение: убрать `flex: 1` с grid в CSS-классах, добавить inline только на слайдах без highlight-box. CSS highlight-box: `margin-top: 20px; flex-shrink: 0`
- **EXP-054: Amber Terminal тема (JS/Node.js)** — amber #F59E0B + Node green #68D391 на charcoal #111111. Уникальные: `.repl-terminal`, Event Loop SVG, `.npm-card`, `.async-flow`, `.perf-meter`. Code bg `#1a1700` (amber-tinted). 3.5 MB
- **EXP-055: Aurora Warm тема (Instagram, СВЕТЛАЯ!)** — warm white #FEFBF6 + IG gradient (pink→orange→purple). Уникальные: `.ig-post`, `.ig-story-circle`, `.ig-insights`. Code blocks ТЁМНЫЕ #2C2C2C на светлом фоне. Cards: white + shadow. 4.4 MB
- **EXP-056: Steel Canvas тема (VK API)** — steel navy #0F172A + VK sky blue #5181B8 + indigo #4338CA + emerald #10B981. Уникальные: `.vk-post`, `.vk-keyboard`, `.vk-miniapp`, `.community-card`, `.token-flow`. 7.6 MB
- **EXP-057: Red Blueprint тема (Yandex Cloud)** — blueprint navy #0C1220 + Yandex red #FC3F1D + blueprint blue #93C5FD. Уникальные: `.arch-diagram`, `.service-card`, `.pricing-calc`, `.compliance-badge`, `.blueprint-grid`, `.deploy-flow`. 4.7 MB
- **EXP-062: Smooth scroll + scroll spy scrollLock** — `scrollIntoView` + scroll spy = bounce между слайдами. Решение: `scrollLock = true` на 800ms, `if (scrollLock) return` в scroll handler.
- **EXP-063: Интерактивный чек-лист** — `.check-box` кликабельный, `checkPop` анимация, strikethrough текст. Только HTML (не PDF).
- **EXP-064: Стоковые фото с overlay** — Unsplash + gradient overlay 85-95% для фона, `mix-blend-mode: luminosity; opacity: 0.5` для декоративных.
- **EXP-065: Progress bar topline** — `.topline::after` с динамической шириной (1/N per slide). Заменяет статичный градиентный бар.
- **EXP-066: Watermark slide numbers** — `.watermark` 280px, opacity 0.04. Фоновые якоря + визуальная глубина.
- **EXP-067: Unique gradient mesh per slide** — каждый `#slide-N` свои radial-gradient позиции/цвета.
- **EXP-068: SVG inline icons vs emoji** — 22x22 stroke-based SVG, `currentColor`, наследуют цвет от `.card` типа.
- **EXP-069: CSS bar charts** — `.bar-track` + `.bar-fill` для финмоделей (retention, маржа, объём).
- **EXP-070: KPI ring SVG** — stroke-dasharray=2πr, dashoffset=264×(1−%), circular progress.
- **EXP-071: go-badge collision** — абсолютное позиционирование `top: 24px` вместо `56px` при изменённой topline.
- **EXP-079: Animated HTML: content-slide ВСЕГДА светлый** — `var(--white)` = `#f0f2f5` даже в тёмной теме. Текст хардкод тёмный, НЕ var(--white).
- **EXP-080: Glassmorphism !important** — перебивает highlight/featured. Добавлять `!important` ко ВСЕМ вариациям.
- **EXP-081: var(--navy) в light-теме = бежевый** — хардкодные цвета в `body.light-theme`, не CSS-переменные.
- **EXP-083: Navigation click zones** — перехватывают UI клики. Трёхуровневая защита: closest() + getBoundingClientRect() + capture-phase флаг.
- **EXP-084: Wheel event при search overlay** — проверка `display !== 'none'` перед `preventDefault()`.
- **EXP-088: Рендер animated HTML в PNG** — Playwright + `goToSlide(i)` + `wait 300ms` + HTTP server (не file://).
- **EXP-089: Chrome DevTools MCP** — `evaluate_script` для переключения тем/слайдов + `take_screenshot`.
- **EXP-090: Viewport Scaling для десктопа** — `<meta viewport width=1920>` ИГНОРИРУЕТСЯ десктопными браузерами. Слайды 1920px обрезаются на ноутбуках (1366-1536px). Решение: JS `transform: scale(screenWidth/1920)` + `html.height = totalHeight × scale` (ограничение прокрутки). **ВАЖНО:** При `position: fixed` навигации использовать `body.style.zoom = sw / 1920` вместо transform:scale (EXP-125). Добавлять в каждую HTML-презентацию с интерактивным просмотром.
- **EXP-133: "AI Product Launch" тёмная тема** — #0a0c1a + Telegram #2AABEE + AI purple #7C5CFC + green #10B981 + gold #F59E0B. Gradient text: linear-gradient(135deg, #2AABEE, #7C5CFC). Для tech/AI product презентаций.
- **EXP-134: Premium TOC overlay** — solid rgba(8,10,25,0.97) без backdrop-filter, 3-column grid карточек с цветными категориями (HERO/BUSINESS/SOLUTION/TECH/AI), keyboard shortcuts pills, auto-scroll active card, close button 40x40, pointer-events toggle.
- **EXP-135: Custom scrollbar matching theme** — WebKit 6px width, gradient thumb (#2AABEE->#7C5CFC), hover ярче (#3BBCFF->#8D6DFF). Firefox: scrollbar-width:thin + scrollbar-color merge в СУЩЕСТВУЮЩИЙ html{}.
- **EXP-136: Researcher -> Presenter pipeline** — при источниках >200KB: researcher agent -> content_brief.md -> presenter agent -> HTML. Параллельные background субагенты для EN+RU. Облегчённый 2-агентный pipeline (vs EXP-132 5-агентный).
- **EXP-137: Horizontal scrollbar от glow blobs** — ambient glow (position:absolute, filter:blur(150px)) выходят за viewport. Решение: overflow-x:hidden на html,body + overflow:hidden на .slide. Ставить В БАЗОВЫЙ CSS с самого начала.
- **EXP-138: Navigation JS комплексный** — arrows + scrollLock 800ms (EXP-062), F=fullscreen, T=TOC toggle, progress bar 3px gradient fixed top, slide counter fixed bottom-left, IntersectionObserver threshold:0.5 для scroll spy. ВСЁ hidden в @media print. Использовать e.code (не e.key).
- **EXP-144: Enhanced glassmorphism** — bg 0.06, border 0.10, border-top 0.15, section-slide::before glass panel, PDF size unchanged
- **EXP-145: scrollLock vs TOC** — goToSlide молча игнорируется при scrollLock, fix: clear lock on TOC open
- **EXP-146: Dead CSS cleanup** — всегда grep class usage после добавления CSS, удалять неиспользуемое
- **EXP-147: Gradient scrollbar** — WebKit 6px gradient thumb + Firefox merge into html{} + per-element TOC scrollbar
- **EXP-148: gradient text ненадёжен с transforms** — заменять на color:#fff + filter:drop-shadow
- **EXP-149: пути к изображениям после реорганизации** — обновлять JS photo paths при mv файлов
- **EXP-150: ambient-orb на всех слайдах** — animation только на .slide.active::before
- **EXP-151: will-change на статических элементах** — только в :hover, только transform/opacity
- **EXP-152: setInterval вместо events** — CustomEvent 'slide-changed' + dispatchEvent в goTo()
- **EXP-153: color-mix() без :root fallback** — добавлять --a1/--a2 в :root как default
- **EXP-154: dead CSS в multi-version файлах** — удалять ранние ::before/theme-N блоки
- **EXP-155: карточки слипаются** — gap с #deck .slide .container !important селектором
- **EXP-156: Inject-скрипт для улучшения существующей презентации** — вместо переписывания 150KB+ HTML целиком создавать Python inject-скрипт с 3 anchor-точками: `</style>` (CSS), `<body>\n` (nav UI), `</body>` (TOC + JS). `content.replace(anchor, new_code + anchor, 1)` — надёжнее и быстрее агент-перезаписи. При добавлении слайдов — ищи `.slide-num` дивы (`12 / 40`) как точные якоря вставки.
- **EXP-157: innerHTML security hook** — PreToolUse:Write хук блокирует файлы с `innerHTML` + template literals → XSS warning. Решение для динамических DOM: `createElement()` + `textContent` + `appendChild()`. Статичный HTML-строки (не user input) — хук не срабатывает. TOC-карточки строить через createElement.
- **EXP-158: Agent prompt size limit** — промпт агента >2000 слов с per-слайд спецификациями завершается "Prompt is too long". Держи промпт ≤1500 слов: numbered list + краткое описание слайдов, без детальных layout-спецификаций на каждый слайд.
- **EXP-159: Обновление нумерации при добавлении слайдов** — при вставке N новых слайдов обновить: (1) slide-num в новых слайдах, (2) slide-num сдвинутых слайдов, (3) TOC JS массив (новые записи), (4) initial counter `01 / N`, (5) все хардкодные `/ 40` → `/ 47`. `slides.length` в JS пересчитывается автоматически.
- **EXP-160: Dual-purpose HTML (браузер + PDF)** — HTML-презентация работает как интерактивный браузер И источник для PDF. Весь UI (progress bar, TOC overlay, nav arrows, счётчик, JS) — в `@media print { display:none !important }`. PDF конвертируется без изменений в convert_to_pdf.py. Тема "GPU Thermal Dark": bg #0C1230, cyan #00D4FF, amber #FF8C1A, green #00E676, red #FF3D00, purple #7B61FF.

При завершении — скажи "запиши это в опыт" если был полезный урок.
