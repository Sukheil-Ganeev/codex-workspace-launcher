# Справочная карта Experience

> Последнее обновление: 2026-02-11
> Всего записей: 36

## Полный реестр

### FIXES (EXP-001..007)

| ID | Файл | Severity | Описание |
|----|------|----------|----------|
| EXP-001 | fixes/EXP-001-body-height-overflow.md | critical | Body height/overflow = видно только 1 слайд. Убрать height с body, page-break на .slide |
| EXP-002 | fixes/EXP-002-white-background.md | high | Белый фон в PDF. Решение: print_background=True в Playwright |
| EXP-003 | fixes/EXP-003-fonts-not-loading.md | high | Шрифты не загружаются. Решение: wait_for_load_state('networkidle') + preconnect |
| EXP-004 | fixes/EXP-004-image-scaling.md | high | min-width не масштабирует img. Решение: фиксированные width/height + object-fit |
| EXP-005 | fixes/EXP-005-fixed-nav-overlap.md | high | Fixed navigation перекрывает контент. Решение: padding-top: 180px на первой секции |
| EXP-006 | fixes/EXP-006-viewport-scaling-desktop.md | critical | Viewport meta игнорируется десктопными браузерами. Решение: JS transform: scale() |
| EXP-007 | fixes/EXP-007-каталог-книг-animated.md | high | 10 фиксов animated HTML: невидимый текст, !important каскад, click zones, light-theme |

### IMPROVEMENTS (EXP-011..012, EXP-062)

| ID | Файл | Severity | Описание |
|----|------|----------|----------|
| EXP-011 | improvements/EXP-011-font-size-scaling.md | high | Шрифты мелкие на 1920x1080. Систематическое +15%: h1 76px, body 17-19px, h2 44-46px |
| EXP-012 | improvements/EXP-012-visual-design-enhancements.md | medium | Мокап терминала на титульном, SVG иконки в заголовках, gradient border-left на code-box |
| EXP-062 | improvements/EXP-062-color-scheme-selection.md | high | Выбор палитры: 3 акцента оптимально, привязка к бренду, 21 тема с hex-кодами |

### PATTERNS (EXP-021..036, EXP-061, EXP-063, EXP-065..068)

| ID | Файл | Severity | Описание |
|----|------|----------|----------|
| EXP-021 | patterns/EXP-021-animated-html-presentation.md | high | Animated HTML: навигация goToSlide(), multi-theme, search overlay, toolbar-ы |
| EXP-022 | patterns/EXP-022-css-compactification.md | high | Контент не влезает: уменьшать padding/font/gap/line-height, НЕ удалять контент |
| EXP-023 | patterns/EXP-023-deanimate-html.md | high | Деанимация перед PDF: animation: none !important на *, ::before, ::after |
| EXP-024 | patterns/EXP-024-highlight-box-visual-upgrade.md | medium | Плоские hbox -> карточки с иконкой + gradient. Вариант A (с заголовком) / B (inline) |
| EXP-025 | patterns/EXP-025-image-download-api.md | medium | Скачивание фото через API стоков: Pexels 200 req/час, Unsplash 50 req/час |
| EXP-026 | patterns/EXP-026-image-normalization.md | high | Нормализация изображений: масштаб по высоте + обрезка/поля, object-fit: cover |
| EXP-027 | patterns/EXP-027-image-sizing.md | medium | object-fit: cover vs contain, ожидание загрузки img в Playwright |
| EXP-028 | patterns/EXP-028-interactive-elements.md | high | Клик по табам/аккордеонам/фильтрам для полного покрытия скриншотов |
| EXP-029 | patterns/EXP-029-landscape-pdf-orientation.md | critical | Landscape PDF: width='1920px' height='1080px', margin=0, НЕ format='A4' |
| EXP-030 | patterns/EXP-030-light-theme-terminals.md | medium | Тёплые light-терминалы: bg #FDFCF9, border rgba(0,0,0,0.13), text #1B1B1B |
| EXP-031 | patterns/EXP-031-pdf-from-screenshots.md | high | PDF из PNG скриншотов через Pillow вместо page.pdf() когда контент обрезается |
| EXP-032 | patterns/EXP-032-reportlab-vertical-documents.md | medium | Reportlab A4: таблицы разрываются, LeftBorderBlock overflow, минималистичные таблицы |
| EXP-033 | patterns/EXP-033-slide-renumbering.md | medium | Массовое обновление нумерации слайдов в обратном порядке (26->27, 25->26...) |
| EXP-034 | patterns/EXP-034-white-label-standalone.md | high | Standalone презентация: scroll lock 800ms, чек-лист, stocked photos, progress bar, SVG icons |
| EXP-035 | patterns/EXP-035-windows-unicode-encoding.md | medium | Windows UnicodeEncodeError: sys.stdout.reconfigure(encoding='utf-8') |
| EXP-036 | patterns/EXP-036-zero-dependency-presentation.md | high | Zero-dependency: системные шрифты, inline SVG, CSS-only декор, 0 сетевых запросов |
| EXP-061 | patterns/EXP-061-glassmorphism-utilities.md | medium | Glassmorphism: glass-value утилиты, inset shadows, backdrop-filter артефакты |
| EXP-063 | patterns/EXP-063-html-vs-pdf-tradeoffs.md | high | HTML vs PDF: таблица совместимости, конвертация Playwright, @media print, zero-dependency |
| EXP-065 | patterns/EXP-065-typography-at-scale.md | high | Типографика 1920x1080: hero 64-76px, h2 38-48px, body 17-19px, code 13px |
| EXP-066 | patterns/EXP-066-animation-for-pdf-vs-html.md | high | Анимации в PDF не работают; деанимация, @media print, "замораживание" кадров |
| EXP-067 | patterns/EXP-067-performance-optimization.md | high | Размер PDF: feTurbulence x2.5, radial-gradient x4, glow blob +0.3-0.5 MB; норма 3-5 MB/18 слайдов |
| EXP-068 | patterns/EXP-068-design-system-components.md | high | 13 компонентов: slide, card, styled-table, code-block, timeline, flow, bar-chart, chat-mockup... |

### WARNINGS (EXP-041..043, EXP-064)

| ID | Файл | Severity | Описание |
|----|------|----------|----------|
| EXP-041 | warnings/EXP-041-backdrop-filter-artifacts.md | critical | backdrop-filter: blur() + border = светящиеся линии. Баг Chrome. НЕ ЧИНИТЬ |
| EXP-042 | warnings/EXP-042-css-variables-themes.md | critical | CSS-переменные меняют семантику между темами. var(--navy) = невидимый текст в light |
| EXP-043 | warnings/EXP-043-min-width-images.md | high | min-width на img НЕ масштабирует изображение. Использовать width/height + object-fit |
| EXP-064 | warnings/EXP-064-design-anti-patterns.md | high | 10 анти-паттернов: "детские анимации", emoji, accent-divider дисбаланс, переусердствие с фиксами |

---

## По проблемам

### Контент обрезается / не влезает
- **EXP-001** -- Body height/overflow обрезает все кроме первого слайда
- **EXP-022** -- Компактификация: font-size/padding/gap/line-height
- **EXP-011** -- Масштабирование шрифтов +15% (или уменьшение при переполнении)
- **EXP-065** -- Типографика: приоритет уменьшения (code -> padding -> line-height -> gap)
- **EXP-031** -- PDF из PNG скриншотов вместо page.pdf() если режет контент

### Изображения ломаются / неправильный размер
- **EXP-004** -- min-width не масштабирует img вверх
- **EXP-026** -- Нормализация: масштаб по высоте + обрезка, object-fit: cover
- **EXP-027** -- cover vs contain, ожидание загрузки img в Playwright
- **EXP-043** -- min-width на img -- НЕ работает для масштабирования
- **EXP-025** -- Скачивание фото через API стоков (Pexels, Unsplash)

### PDF слишком большой (>10 MB)
- **EXP-067** -- Бенчмарки, факторы роста, стратегии оптимизации
- **EXP-064** -- feTurbulence x2.5, gradients на карточках x3, radial-gradient x4

### Белый фон / шрифты не загружаются
- **EXP-002** -- print_background=True в Playwright
- **EXP-003** -- wait_for_load_state('networkidle') + preconnect

### Цвета / контрастность / невидимый текст
- **EXP-062** -- Выбор палитры: 3 акцента, text-primary не чистый #fff
- **EXP-042** -- CSS-переменные меняют семантику, хардкодить в light-theme
- **EXP-030** -- Тёплые light-терминалы вместо тёмных на светлом фоне
- **EXP-007** -- Невидимый текст content-slide, var(--navy) в light, roi-badge

### Анимации / интерактивность
- **EXP-021** -- Animated HTML: навигация, темы, поиск, toolbar-ы
- **EXP-023** -- Деанимация HTML перед PDF-генерацией
- **EXP-066** -- Что работает/не работает в PDF, @media print, "замораживание"
- **EXP-028** -- Клик по табам/аккордеонам для полного покрытия скриншотов
- **EXP-034** -- Standalone: scroll lock, чек-лист, progress bar

### Визуальные артефакты
- **EXP-041** -- backdrop-filter: blur() артефакты -- НЕ ЧИНИТЬ
- **EXP-042** -- !important из glassmorphism перебивает вариации
- **EXP-064** -- Пересборка > патчинг после 3+ итераций

### Ориентация / масштаб PDF
- **EXP-029** -- Landscape: width/height в px, НЕ format='A4'
- **EXP-006** -- Viewport scaling для десктопных браузеров (JS transform: scale)

### Glassmorphism / визуальное улучшение
- **EXP-061** -- Утилиты glass-value, inset shadows, безопасная альтернатива
- **EXP-024** -- Highlight box -> карточки с иконкой + gradient
- **EXP-012** -- Мокап терминала, SVG иконки, gradient border-left

### Windows / совместимость
- **EXP-035** -- UnicodeEncodeError на Windows: reconfigure(encoding='utf-8')
- **EXP-032** -- Reportlab A4: таблицы разрываются, LeftBorderBlock overflow

---

## По этапам разработки

### 1. Планирование (палитра, типографика, формат)
- **EXP-062** -- Выбор палитры: 21 тема, 3 акцента оптимально
- **EXP-065** -- Типографика: hero 64-76px, h2 38-48px, body 17-19px
- **EXP-063** -- HTML vs PDF: когда какой формат, ограничения
- **EXP-068** -- 13 компонентов дизайн-системы

### 2. Верстка (компоненты, лейаут)
- **EXP-068** -- slide, card, table, code-block, timeline, flow, bar-chart...
- **EXP-022** -- Компактификация при переполнении
- **EXP-034** -- Standalone: scroll spy, progress bar, SVG icons
- **EXP-036** -- Zero-dependency: системные шрифты, inline SVG
- **EXP-005** -- Fixed nav overlap: padding-top на первой секции

### 3. Контент (текст, изображения)
- **EXP-026** -- Нормализация изображений разных пропорций
- **EXP-027** -- object-fit: cover vs contain, загрузка в Playwright
- **EXP-025** -- API стоков для скачивания фото
- **EXP-011** -- Масштабирование шрифтов +15%
- **EXP-024** -- Highlight box -> визуально богатые карточки
- **EXP-033** -- Перенумерация слайдов (обратный порядок)

### 4. Анимации / интерактив
- **EXP-021** -- Animated HTML: навигация, темы, поиск
- **EXP-023** -- Деанимация перед PDF
- **EXP-028** -- Клик по интерактивным элементам для покрытия
- **EXP-066** -- Что работает/не работает в PDF, @media print

### 5. Конвертация в PDF
- **EXP-001** -- Body height: auto, page-break-after: always
- **EXP-002** -- print_background=True
- **EXP-003** -- wait_for_load_state('networkidle')
- **EXP-006** -- Viewport scaling для десктопных браузеров
- **EXP-029** -- Landscape: width/height в px, margin=0
- **EXP-031** -- PDF из PNG скриншотов (альтернатива page.pdf)
- **EXP-063** -- HTML vs PDF tradeoffs

### 6. Отладка / фиксы
- **EXP-041** -- backdrop-filter артефакты -- НЕ ЧИНИТЬ
- **EXP-042** -- CSS-переменные в multi-theme, !important каскад
- **EXP-043** -- min-width на img не масштабирует
- **EXP-064** -- 10 анти-паттернов, пересборка > патчинг
- **EXP-007** -- 10 фиксов animated HTML

### 7. Оптимизация
- **EXP-067** -- Размер PDF: бенчмарки, факторы, стратегии
- **EXP-011** -- Масштабирование шрифтов (обратная задача -- уменьшение)
- **EXP-061** -- Glassmorphism: backdrop-filter без артефактов
- **EXP-035** -- Windows Unicode encoding

---

## По проектам

### Skill_Presentations (23 справочника)
- **EXP-062** -- Палитра: 21 тема для всех справочников
- **EXP-065** -- Типографика единая
- **EXP-068** -- 13 компонентов дизайн-системы
- **EXP-067** -- Бенчмарки размеров (3.5-9.6 MB)
- **EXP-066** -- Анимации в PDF (zero-dependency подход)
- **EXP-063** -- HTML vs PDF (convert_to_pdf.py)
- **EXP-064** -- 10 анти-паттернов

### Калькулятор-Документация
- **EXP-041** -- backdrop-filter артефакты, Vault Command Center
- **EXP-061** -- Glassmorphism утилиты, glass-value-green/amber/red
- **EXP-062** -- Vault Command Center палитра (emerald + amber + red)
- **EXP-064** -- Пересборка > патчинг
- **EXP-063** -- HTML vs PDF tradeoffs

### Каталог книг Дубай
- **EXP-004** -- min-width не масштабирует обложки
- **EXP-007** -- 10 фиксов animated HTML (темы, click zones, glassmorphism)
- **EXP-021** -- Animated HTML паттерн (52-56 слайдов)
- **EXP-026** -- Нормализация 27 обложек
- **EXP-042** -- CSS-переменные в multi-theme
- **EXP-043** -- min-width на img

### Telegram Stars
- **EXP-011** -- Масштабирование шрифтов +15%

### Ocean Strategy
- **EXP-036** -- Zero-dependency, 14 слайдов, 4.9 MB

### Islamic AI Presentation
- **EXP-033** -- Перенумерация 26->28 слайдов
- **EXP-035** -- Windows Unicode encoding

### White Label Negotiation
- **EXP-034** -- Standalone: scroll lock, progress bar, SVG icons, KPI rings

### Claude CLI / MCP Presentation
- **EXP-005** -- Fixed nav overlap
- **EXP-012** -- Мокап терминала, SVG иконки
- **EXP-022** -- Компактификация CSS
- **EXP-028** -- Клик по табам каталога
- **EXP-029** -- Landscape PDF
- **EXP-031** -- PDF из PNG скриншотов

### Claude Agent Teams
- **EXP-024** -- Highlight box upgrade (17 слайдов, светлая тема)

### Сафарист Дубай
- **EXP-032** -- Reportlab A4, Desert Minimal, 6 страниц

---

## Граф связей

```
EXP-001 <--> EXP-022 (обрезка контента / компактификация)
EXP-022 <--> EXP-011 (масштабирование шрифтов)
EXP-011 <--> EXP-065 (типографика 1920x1080)

EXP-004 <--> EXP-026 <--> EXP-027 <--> EXP-043 (изображения)
EXP-025 --> EXP-026 --> EXP-027 (download -> normalize -> CSS)

EXP-041 <--> EXP-061 (backdrop-filter / glassmorphism)
EXP-041 <--> EXP-007 (артефакты animated HTML)

EXP-042 <--> EXP-007 <--> EXP-021 (multi-theme / CSS-переменные)
EXP-042 <--> EXP-030 (light-theme)

EXP-021 <--> EXP-023 (animated HTML / деанимация)
EXP-023 <--> EXP-029 <--> EXP-031 (конвертация PDF)
EXP-028 <--> EXP-029 <--> EXP-031 (интерактив -> скриншоты -> PDF)

EXP-062 <--> EXP-065 <--> EXP-068 (палитра -> типографика -> компоненты)
EXP-026 <--> EXP-062 <--> EXP-068 (дизайн-система)

EXP-003 <--> EXP-036 (шрифты / zero-dependency)
EXP-012 <--> EXP-036 (визуальный дизайн / zero-dependency)
EXP-012 <--> EXP-024 (визуальные улучшения)

EXP-063 <--> EXP-066 (HTML vs PDF / анимации)
EXP-063 <--> EXP-023 (tradeoffs / деанимация)

EXP-064 <--> EXP-067 (анти-паттерны / оптимизация размера)
EXP-061 <--> EXP-067 (glassmorphism / performance)

EXP-006 <--> EXP-034 (viewport scaling / standalone)
EXP-034 <--> EXP-036 (standalone / zero-dependency)

EXP-005 <--> EXP-022 (nav overlap / компактификация)
EXP-002 <--> EXP-029 (print_background / landscape)
EXP-033 --> EXP-034 (перенумерация -> standalone workflow)
```
