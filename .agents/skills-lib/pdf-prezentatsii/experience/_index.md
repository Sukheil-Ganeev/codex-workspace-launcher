# Критические уроки PDF-презентаций

> 115 записей | Обновлено: 2026-03-04 (+ EXP-148..155 performance fixes: gradient text, image paths, GPU overhead, will-change, setInterval, color-mix, dead CSS, gap specificity)
> Полная карта: [REFERENCE_MAP.md](REFERENCE_MAP.md)

## Топ-10 (читать при активации скилла!)

1. **EXP-126** -- filter:blur() на bg-glow = 20x раздутие PDF (52 MB -> 2.5 MB). Для PDF/static: убрать filter:blur с декоров, solid bg вместо glass, оставлять blur ТОЛЬКО в animated версии
2. **EXP-091** -- `.slide > *` ломает position:absolute у декоров -> :not() селектор для bg-glow, slide-decor-*, slide-number, glow, deco-grid, deco-circle
3. **EXP-093** -- backdrop-filter на однородном фоне = нулевой эффект -> gradient + border + inset shadow
4. **EXP-092** -- rgba(255,255,255,0.12) на тёмном фоне невидим -> gradient bg + яркие бордеры rgba(0.25) + inset glow
5. **EXP-094** -- transform:scale() на body ломает position:fixed -> переносить nav в documentElement
6. **EXP-096** -- flex:1 на grid-контейнерах растягивает карточки -> убрать flex:1 с grid-контейнеров
7. **EXP-022** -- Контент не влезает -> уменьшай font/padding/gap/line-height, НЕ удаляй контент
8. **EXP-064** -- Анти-паттерны: emoji вместо фото, "детские анимации" (pulse-ring), переусердствие с фиксами
9. **EXP-097** -- Уникальные декор-классы (.glow, .deco-grid, .thread-decor) ломают flex -> широкий :not() или общий класс .slide-decor
10. **EXP-098** -- Purple-on-purple невидимый текст -> принудительный rgba(255,255,255,0.88) + text-shadow + цветные labels
11. **EXP-142** -- Анимированные PDF НЕ существуют. PDF = статика (ISO 32000). HTML = анимации. Двойной формат: HTML для показа + PDF для отправки/печати

## Быстрая навигация

### По ситуации

- **Начинаю новую презентацию** -> EXP-062 (палитра), EXP-065 (типографика), EXP-068 (компоненты), EXP-063 (HTML vs PDF), EXP-133 (AI Product Launch тема)
- **Контент не влезает** -> EXP-022 (компактификация), EXP-001 (body height), EXP-011 (шрифты +15%)
- **Проблемы с изображениями** -> EXP-004 (min-width не работает), EXP-026 (нормализация Pillow), EXP-027 (cover vs contain), EXP-025 (API стоков), EXP-099 (blur на img-контейнерах)
- **Конвертация в PDF** -> EXP-001 (page-break), EXP-002 (print_background), EXP-003 (networkidle), EXP-029 (landscape), EXP-006 (viewport scaling), EXP-126 (filter:blur 20x bloat), EXP-141 (backdrop-filter → solid rgba), EXP-143 (/simplify ревью перед PDF)
- **Glassmorphism → PDF** -> EXP-141 (backdrop-filter замена на solid rgba + opacity таблица)
- **Анимированный PDF?** -> EXP-142 (невозможно, PDF = статика, HTML = анимации, двойной формат)
- **PDF из скриншотов** -> EXP-031 (Pillow), EXP-028 (клик по табам для покрытия)
- **Визуальные артефакты** -> EXP-041 (backdrop-filter -- НЕ ЧИНИТЬ), EXP-042 (CSS-переменные multi-theme), EXP-043 (min-width img), EXP-092 (rgba невидим на тёмном), EXP-098 (purple-on-purple), EXP-105 (text-shadow glow overdone), EXP-112 (inset white highlight артефакты)
- **Декоративные элементы ломают layout** -> EXP-091 (.slide > * ломает absolute), EXP-097 (уникальные декор-классы), EXP-096 (flex:1 растягивает grid), EXP-101 (glassmorphism ломает специфические элементы), EXP-102 (margin-top:auto без flex)
- **Навигация и масштабирование** -> EXP-094 (transform:scale ломает fixed), EXP-078 (body transform + fixed), EXP-118 (documentElement + light-theme duplication), EXP-125 (zoom вместо scale -- НЕ ломает fixed, @media print zoom:1, e.code для клавиш, TOC overlay, glass cards), EXP-138 (комплексный navigation JS: arrows, F, T, progress bar, scroll spy)
- **Glass-эффекты на тёмном фоне** -> EXP-093 (backdrop-filter на однородном = 0), EXP-095 (bg-glow opacity 0.30+), EXP-071 (glassmorphism без backdrop), EXP-099 (blur на img-контейнерах), EXP-112 (inset white highlight артефакты), EXP-119 (glassmorphism на тёмном с текстурой), EXP-128 (glassmorphism карточки backdrop-filter + glass border)
- **"Убери свечения" от пользователя** -> EXP-116 ("убери свечения" != "убери glassmorphism", что трогать / что нет)
- **Нужна анимация** -> EXP-021 (animated HTML), EXP-023 (деанимация для PDF), EXP-066 (что работает/нет в PDF), EXP-028 (интерактивные элементы), EXP-103 (профессиональные принципы плавности), EXP-120 (анимации + PDF через @media print), EXP-121 (gradient text hero), EXP-125 (premium CSS анимации: fadeInUp, scaleIn, shimmer, breathe, gradientSlide), EXP-129 (gradient text + shimmer анимация)
- **Улучшить дизайн** -> EXP-061 (glassmorphism), EXP-024 (highlight box upgrade), EXP-012 (мокап, SVG, gradient border), EXP-122 (gradient border mask-composite), EXP-127 (mesh gradients вместо bg-glow), EXP-130 (pill tags), EXP-131 (gradient bar сверху карточки)
- **Tech comparison / benchmarks** -> EXP-124 (Neural Grid тема), EXP-123 (benchmark бары), EXP-073 (bar chart multicolor), EXP-119 (glassmorphism на тёмном), EXP-149 (двойная палитра RTX3090 cyan/amber)
- **Сравнительная презентация (два продукта/поколения)** -> EXP-149 (dual-color: каждой стороне свой цвет, применять на всех слайдах)
- **Минимальная навигация (≤20 слайдов, нет TOC)** -> EXP-148 (55 строк: arrows+F+IntersectionObserver, без progress bar)
- **PDF слишком большой** -> EXP-126 (filter:blur 20x bloat -- ГЛАВНЫЙ ФАКТОР), EXP-067 (бенчмарки, solid вместо gradient, контроль glow), EXP-127 (mesh gradients = 0 риск раздутия)
- **Светлая тема** -> EXP-030 (тёплые терминалы), EXP-042 (CSS-переменные), EXP-007 (content-slide всегда тёмный текст)
- **Standalone презентация** -> EXP-034 (scroll lock, progress bar, SVG icons), EXP-036 (zero-dependency), EXP-113 (slideshow mode для статических HTML), EXP-138 (navigation JS комплексный)
- **Slideshow mode (PDF -> интерактив)** -> EXP-113 (slideshow mode IIFE), EXP-114 (keyboard shortcuts стандарт), EXP-115 (TOC frosted glass overlay), EXP-117 (nav arrows glass style)
- **Reportlab (A4 документ)** -> EXP-032 (таблицы, LeftBorderBlock, Desert Minimal)
- **Windows проблемы** -> EXP-035 (UnicodeEncodeError: reconfigure utf-8), EXP-100 (HTML entities эмодзи = квадратики)
- **Per-slide фиксы** -> EXP-104 (изоляция через nth-child), EXP-106 (timeline ::before линии)
- **Перенумерация слайдов** -> EXP-033 (обратный порядок замены)
- **Dark mode проблемы** -> EXP-107 (контраст rgba плашек), EXP-092 (rgba невидим на тёмном), EXP-098 (purple-on-purple)
- **Переключение тем** -> EXP-108 (overlay fade, не CSS transition), EXP-042 (CSS-переменные multi-theme)
- **Чеклист новой презентации** -> Taplink-презентация секция (13 пунктов + тайминги)
- **TOC ломает навигацию** -> EXP-069 (scroll isolation 3 layers), EXP-078 (body transform + fixed), EXP-115 (TOC frosted glass overlay дизайн), EXP-134 (premium TOC overlay с категориями)
- **TOC не навигирует после стрелок** -> EXP-145 (scrollLock блокирует goToSlide, сброс при открытии TOC)
- **Мёртвый CSS после итераций дизайна** -> EXP-146 (grep для class usage, удалять в /simplify)
- **Усиление glassmorphism для PDF** -> EXP-144 (bg 0.06, border 0.10, border-top 0.15, section-slide::before glass panel)
- **Кастомный скроллбар с градиентом** -> EXP-147 (WebKit gradient thumb + Firefox merge + per-element TOC scrollbar)
- **Минимальная навигация** -> EXP-148 (≤20 слайдов без TOC: 55 строк JS, arrows+F, IntersectionObserver)
- **Сравнительная двойная палитра** -> EXP-149 (dual-color: Cyan=новое, Amber=зрелое, везде последовательно)
- **gradient text невидим с transform:scale** -> EXP-148-new (color:#fff + filter:drop-shadow вместо background-clip:text)
- **пути изображений сломались после mv файлов** -> EXP-149-new (проверять localPhotoMap, src=, url( в JS)
- **анимация на всех слайдах тормозит** -> EXP-150 (ambient-orb только на .slide.active::before)
- **will-change тормозит смену слайда** -> EXP-151 (только :hover, только transform+opacity)
- **setInterval для слежения за слайдом** -> EXP-152 (CustomEvent + dispatchEvent в goTo())
- **color-mix() не работает без класса** -> EXP-153 (:root --a1/--a2 fallback обязателен)
- **CSS !important война в multi-version** -> EXP-154 (grep дублированных ::before/theme-N, удалять ранние)
- **карточки слипаются в grid** -> EXP-155 (#deck .slide .container gap !important)
- **Уникальный дизайн для каждой презентации** -> EXP-070 (10 TOC дизайнов), EXP-072 (CSS компоненты)
- **Glassmorphism в PDF** -> EXP-071 (без backdrop-filter: rgba + border + shadow)
- **Текст -> визуал** -> EXP-075 (metric-cards, grids), EXP-076 (FAQ transformation), EXP-079 (test checklists)
- **Графики и диаграммы** -> EXP-073 (bar chart multicolor), EXP-074 (ASCII -> HTML)
- **Командная работа** -> EXP-077 (параллельный дизайн, broadcast briefs), EXP-132 (5 агентов pipeline: Content+CSS Architect → HTML Builder → Static+QA), EXP-136 (researcher → presenter pipeline для больших источников), EXP-139 (mass data update: parallel research → sequential update)
- **/simplify для презентаций** -> EXP-143 (@media print, inline→CSS-классы, phantom cells, неиспользуемые CSS)
- **Массовое обновление презентации** -> EXP-139 (parallel research 6 агентов → single MD update → single HTML update → PDF)
- **Много событий на одном слайде** -> EXP-140 (timeline grid 5x2, до 10 событий на 1920x1080)

### Все записи по типам

→ Полный каталог (FIXES / IMPROVEMENTS / PATTERNS / WARNINGS): **[REFERENCE_MAP.md](../REFERENCE_MAP.md)**

## VIP-DXB Презентации (EXP-069..079)

### Критические уроки
1. **body transform ломает position:fixed** -- переносить overlay в document.documentElement (EXP-078, EXP-069)
2. **Glassmorphism без backdrop-filter** -- rgba backgrounds + white border + inset shadow + pseudo glow (EXP-071)
3. **Текстовые слайды -> визуальные** -- metric-cards, colored tags, icon-cards, grids (EXP-075, EXP-076)
4. **Уникальный дизайн через CSS-only** -- shape + connector + accent + font + spacing (EXP-070)
5. **Параллельный дизайн командой** -- researcher + 3-4 designers + QA, broadcast briefs (EXP-077)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 069 | fix | TOC scroll isolation (3 layers) |
| 070 | pattern | 10 unique TOC designs |
| 071 | pattern | Glassmorphism без backdrop-filter |
| 072 | improvement | CSS component improvements |
| 073 | pattern | Bar chart multi-color (nth-child) |
| 074 | improvement | ASCII -> HTML diagrams |
| 075 | pattern | Text-heavy -> visual slides |
| 076 | improvement | FAQ visual transformation |
| 077 | pattern | Team parallel design |
| 078 | warning | body transform + position:fixed |
| 079 | pattern | Test checklist slides (фазовая группировка) |

## ПК-справочники — полировка (EXP-091..098)

### Критические уроки
1. **`.slide > *` ломает декоры** -- :not() селектор обязателен для bg-glow, slide-decor-*, slide-number, glow, deco-grid, deco-circle (EXP-091)
2. **Glass на тёмном фоне невидим** -- gradient bg + яркие бордеры rgba(0.25) + inset glow, НЕ backdrop-filter (EXP-092, EXP-093)
3. **transform:scale ломает fixed** -- переносить nav в documentElement (EXP-094)
4. **bg-glow opacity 0.30+** -- 0.12 невидим, нужно 0.30-0.35 (EXP-095)
5. **flex:1 + grid = растянутые пустоты** -- убрать flex:1 с grid-контейнеров (EXP-096)
6. **Уникальные декор-классы** -- широкий :not() или общий .slide-decor на все декоры (EXP-097)
7. **Purple-on-purple** -- принудительный rgba(255,255,255,0.88) + text-shadow + цветные labels (EXP-098)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 091 | fix | `.slide > *` ломает position:absolute декоров |
| 092 | pattern | rgba невидим на тёмном, gradient + border |
| 093 | warning | backdrop-filter на однородном = 0 |
| 094 | fix | transform:scale ломает position:fixed |
| 095 | pattern | bg-glow opacity 0.30+ для видимости |
| 096 | fix | flex:1 на grid растягивает карточки |
| 097 | warning | Уникальные декор-классы ломают flex |
| 098 | warning | Purple-on-purple невидимый текст |

### Контекст
- **14 ПК-справочников** полностью отполированы
- **fix_all_v5.py** -- массовый скрипт полировки всех 14 файлов
- Основные проблемы: декоративные элементы в flex-потоке, невидимый glass, сломанная навигация

## Бот-презентации (EXP-099..106)

### Критические уроки
1. **backdrop-filter blur на img-контейнерах** -- glassmorphism ставит blur поверх картинок, нужно backdrop-filter: none + crisp-edges (EXP-099)
2. **HTML entities эмодзи = квадратики** -- использовать UTF-8 эмодзи + emoji шрифты в font-family (EXP-100)
3. **Glassmorphism ломает gradient text, border-left, tags** -- исключения через :not() или восстановление после (EXP-101)
4. **margin-top:auto без flex = 0** -- родитель должен быть flex-column (EXP-102)
5. **Профессиональные анимации** -- duration 0.4-0.55s, scale max 1.015, НИКОГДА transition:all (EXP-103)
6. **Изоляция фиксов через nth-child** -- per-slide правки только через :nth-child(N) (EXP-104)
7. **Text-shadow glow overdone** -- alpha 0.12-0.15, blur 6-8px, none для чисел (EXP-105)
8. **Timeline ::before линии** -- первый кандидат на удаление при визуальной шумности (EXP-106)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 099 | fix | backdrop-filter blur на img-контейнерах |
| 100 | fix | HTML entities эмодзи = квадратики |
| 101 | warning | Glassmorphism ломает gradient text, border-left, tags |
| 102 | fix | margin-top:auto без flex = 0 |
| 103 | pattern | Профессиональные анимации: принципы плавности |
| 104 | pattern | Изоляция CSS-фиксов через nth-child |
| 105 | warning | Text-shadow glow overdone |
| 106 | pattern | Timeline ::before линии: убирать или оставлять |

### Контекст
- **Бот-презентации:** telegram-bot, whatsapp-bot, vk-bot
- Основные проблемы: glassmorphism конфликты, агрессивные анимации, битые эмодзи
- Решения: изоляция через :not() и nth-child, мягкие параметры анимаций

## Taplink-презентация (EXP-107..111)

### Критические уроки
1. **Dark Mode контраст** -- rgba opacity 8-10% нечитаем, увеличить до 20-25%. Все карточки #22223a. WCAG AA 4.5:1 минимум. Отдельный `[data-theme="dark"]` для КАЖДОГО типа элемента (EXP-107)
2. **Overlay Fade переключение тем** -- CSS transition на `*` = "лоскутный" эффект. Полноэкранный #theme-overlay (z-index:99999), fade in 150ms -> data-theme мгновенно -> fade out 150ms = 300ms crossfade. НИКОГДА transition на * (EXP-108)
3. **Кастомный scrollbar** -- стандартный 17px чужеродный. scrollbar-width:thin, 6px, thumb border-radius 3px (EXP-109)
4. **Inline HTML один файл** -- CSS в style, JS в script, шрифты CDN. Лимит 200-250KB (EXP-110)
5. **Fullscreen клавиша F** -- requestFullscreen/exitFullscreen, добавлять ВСЕГДА (EXP-111)

### Чеклист для КАЖДОЙ новой презентации
- Dark mode: все элементы проверены на контраст (WCAG AA 4.5:1)
- Переключение темы: overlay fade (не CSS transition)
- Scrollbar: кастомный, тонкий (6px), в цветах палитры
- Fullscreen: клавиша F
- Горячие клавиши: arrows навигация, D темы, T оглавление, H помощь, F fullscreen, Ctrl+F поиск
- Copy-to-clipboard на блоках кода
- Expand/collapse для длинных блоков кода (>5 строк)
- Оглавление (Table of Contents) с навигацией
- Progress bar внизу
- Touch swipe для мобильных
- localStorage для сохранения темы
- initTheme() БЕЗ transition при загрузке
- Размер файла <250KB

### Оптимальные тайминги анимаций
- Overlay fade: 150ms in + 150ms out = 300ms
- Slide transition: 300ms ease-out
- Stagger delay: 50ms per element
- Hover effects: 200ms
- Code expand: 400ms ease

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 107 | warning | Dark Mode контраст на rgba плашках |
| 108 | pattern | Overlay Fade для переключения тем |
| 109 | pattern | Кастомный scrollbar обязателен |
| 110 | pattern | Inline HTML один файл, лимит 250KB |
| 111 | pattern | Fullscreen клавиша F |

### Контекст
- **Taplink-презентация:** интерактивная HTML-презентация справочника Taplink
- Основные проблемы: dark mode контраст, переключение тем (лоскутный эффект), стандартный scrollbar
- Решения: overlay fade техника, WCAG AA 4.5:1 контраст, кастомный scrollbar, горячие клавиши

## Debit-Cards-Research (EXP-112..118)

> Оригинальные номера пользователя: EXP-102..108, перенумерованы на EXP-112..118 (EXP-102..111 уже заняты)

### Критические уроки
1. **inset white highlight = артефакты** -- `inset 0 1px 0 rgba(255,255,255,0.04)` на тёмном = светлые квадратики в углах. НЕ использовать (EXP-112)
2. **Slideshow mode из статического HTML** -- body.slideshow-mode + .slide.active, IIFE ~80 строк, print сохраняется через @media print (EXP-113)
3. **Keyboard shortcuts стандарт** -- arrows, T(TOC), F(fullscreen), Esc, Home/End, Space. При TOC: overflow:hidden на body (EXP-114)
4. **TOC frosted glass** -- gradient bg + blur(30px) + SVG noise. ESC pill-кнопка вместо крестика. h2 padding-right:70px (EXP-115)
5. **"Убери свечения" != "Убери glassmorphism"** -- text-shadow/glow = свечения. backdrop-filter/gradient bg/glass borders = НЕ свечения (EXP-116)
6. **Nav arrows: opacity:1** -- НЕ делать opacity:0.5-0.6, пользователь не видит. Приглушённые цвета (alpha 0.6-0.7) (EXP-117)
7. **Scrollbar стилизация** -- webkit 4px + Firefox thin + scrollbar-color. Gradient thumb для dual-theme (EXP-118)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 112 | warning | inset white highlight артефакты на тёмном |
| 113 | pattern | Slideshow mode для статических HTML |
| 114 | pattern | Keyboard shortcuts стандарт |
| 115 | pattern | TOC overlay frosted glass design |
| 116 | warning | "Убери свечения" != "Убери glassmorphism" |
| 117 | pattern | Nav arrows glass style (opacity:1) |
| 118 | pattern | Scrollbar стилизация (webkit + Firefox) |

### Контекст
- **Проект:** Debit-Cards-Research -- исследовательская презентация
- Основные проблемы: inset highlight артефакты, интерпретация "убери свечения", навигация слайдшоу
- Решения: slideshow mode поверх статического HTML, стандартизация hotkeys, frosted glass TOC
- Подробности: [fixes/EXP-112-118-debit-cards.md](fixes/EXP-112-118-debit-cards.md)

## AI Models Comparison -- Neural Grid v2 (EXP-119..124, 139..142)

### Критические уроки
1. **Glassmorphism на тёмном с текстурой** -- 3-слойный bg (dot grid + horizontal lines + radial-gradient) делает backdrop-filter видимым на #0A0E1A (EXP-119)
2. **Анимации + PDF = @media print** -- @keyframes в браузере, animation:none !important в print. НЕ использовать CSS transition на .slide (EXP-120)
3. **Gradient text hero** -- background-clip:text + shimmer 8s + @media print fallback (EXP-121)
4. **Gradient border без border-image** -- ::before + mask-composite: exclude для rounded corners (EXP-122)
5. **Benchmark бары** -- horizontal bars с provider-colored gradient, число внутри + снаружи, growBar через IntersectionObserver (EXP-123)
6. **Neural Grid тема** -- #0A0E1A + Space Grotesk + Inter + JetBrains Mono, 4 provider-цвета (EXP-124)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 119 | pattern | Glassmorphism на тёмном фоне с текстурой |
| 120 | pattern | Анимации + PDF совместимость (@media print) |
| 121 | pattern | Gradient text для hero заголовков |
| 122 | pattern | Gradient border через mask-composite |
| 123 | pattern | Benchmark бары (horizontal, provider-colored) |
| 124 | pattern | Neural Grid дизайн-система (sci-fi tech) |
| 139 | pattern | Mass data update workflow (parallel research → sequential update) |
| 140 | pattern | Timeline grid 5x2 для 10 событий на 1 слайде |
| 141 | fix | backdrop-filter → solid rgba для PDF (opacity таблица) |
| 142 | warning | Анимированные PDF невозможны (PDF = статика ISO 32000) |

### Контекст
- **Проект:** AI Models Comparison 2026, 16 слайдов, 92 KB HTML
- **Тема:** "Neural Grid" -- тёмная sci-fi тема для сравнения AI моделей
- **QA:** 38/38 PASS
- Основные находки: glassmorphism работает на текстурном фоне, gradient border через mask-composite, @media print для полной PDF-совместимости анимаций
- **Обновление 2026-02-28:** mass data update (9 агентов, parallel research → sequential update), timeline grid 5x2, backdrop-filter → solid rgba для PDF, анимированные PDF невозможны
- Подробности: [patterns/EXP-124-neural-grid-theme.md](patterns/EXP-124-neural-grid-theme.md)

### Новая тема (добавить в EXP-062)
- Neural Grid: тёмная #0A0E1A, accent Google #4285F4 / OpenAI #10A37F / Anthropic #D97706 / xAI #1DA1F2, Space Grotesk + Inter + JetBrains Mono

## Docker-справочник -- Container Dock (EXP-126)

### Критические уроки
1. **filter:blur() на bg-glow = 20x раздутие PDF** -- 3 bg-glow x 18 слайдов = 54 blurred circles. Каждый создаёт Gaussian composite bitmap layer в Playwright PDF renderer. 52 MB -> 2.5 MB после удаления filter:blur (EXP-126)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 126 | fix | filter:blur() на bg-glow = 20x раздутие PDF |

### Контекст
- **Docker-справочник:** "Container Dock" тема, 18 слайдов, 7 stock photos, glassmorphism v3.0
- **Тема:** Container Dock -- тёмная industrial #0A0E1A, Docker blue #2496ED + navy #1B3A5C + yellow #FFC107
- Основная находка: filter:blur -- САМЫЙ КРУПНЫЙ фактор раздутия PDF, превосходит все ранее известные (SVG feTurbulence x2.5, radial-gradient x4, linear-gradient x3)
- Подробности: [fixes/EXP-126-filter-blur-pdf-bloat.md](fixes/EXP-126-filter-blur-pdf-bloat.md)

### Новая тема (добавить в EXP-062)
- Container Dock: тёмная #0A0E1A, accent Docker #2496ED / navy #1B3A5C / yellow #FFC107, Inter + JetBrains Mono

## Belarus-Payment-Research -- Glassmorphism v2 (EXP-127..132)

> Пользователь запросил EXP-099..104, перенумерованы на EXP-127..132 (EXP-099..126 уже заняты)

### Критические уроки
1. **Mesh gradients вместо bg-glow** -- УДАЛИТЬ все .bg-glow div'ы, заменить на radial-gradient прямо на .slide. Каждый слайд -- уникальные позиции/цвета (7+ вариантов). 0 риск PDF-раздутия (EXP-127)
2. **Glassmorphism карточки v2** -- rgba(255,255,255,0.04) + backdrop-filter:blur(20px) + border rgba(0.08) + ::before light line сверху. Для static/PDF: убрать backdrop-filter, rgba(0.04)→rgba(0.06) (EXP-128)
3. **Gradient text + shimmer** -- background-clip:text + background-size:200% + animation shimmer 4s. Для PDF: заменить на обычный color (background-clip text ненадёжен) (EXP-129)
4. **Pill tags** -- border-radius:100px вместо 6px. font-size:12px, uppercase, letter-spacing:0.5px. Более яркие цвета (#34D399) для контраста на glass bg (EXP-130)
5. **Gradient bar сверху карточки** -- ::after gradient bar вместо border-left:3px. Выглядит премиальнее с glassmorphism (EXP-131)
6. **5 агентов pipeline** -- Content Architect + CSS Architect (параллельно) → HTML Builder → Static Converter + QA Reviewer (параллельно). 3 волны, QA 10/10 (EXP-132)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 127 | pattern | Mesh gradients вместо bg-glow (radial-gradient на .slide) |
| 128 | pattern | Glassmorphism карточки (backdrop-filter + glass border) |
| 129 | pattern | Gradient text + shimmer анимация |
| 130 | pattern | Pill tags (border-radius:100px, modern) |
| 131 | pattern | Semantic cards: gradient bar сверху |
| 132 | pattern | Presentation pipeline: 5 агентов, 3 волны |

### Контекст
- **Проект:** Belarus-Payment-Research (2026-02-19)
- **Тема:** Glassmorphism v2 -- mesh gradients, glass cards, premium typography
- Основные находки: mesh gradient на .slide = глубина без отдельных элементов и 0 риск PDF-раздутия; pill tags + gradient bar сверху = современный премиальный вид; 5-агентный pipeline обеспечивает QA 10/10

## Telegram Business Bot -- AI Product Launch (EXP-133..138)

### Критические уроки
1. **AI Product Launch палитра** -- #0a0c1a + Telegram #2AABEE + purple #7C5CFC + green #10B981 + gold #F59E0B. Gradient text: linear-gradient(135deg, #2AABEE, #7C5CFC) для hero (EXP-133)
2. **Premium TOC overlay** -- solid rgba(8,10,25,0.97) НЕ backdrop-filter, 3-column grid, цветные категории (HERO/BUSINESS/SOLUTION/TECH/AI), keyboard shortcuts pills, auto-scroll active card (EXP-134)
3. **Custom scrollbar с hover** -- WebKit 6px gradient thumb (#2AABEE->#7C5CFC), hover ярче (#3BBCFF->#8D6DFF), Firefox scrollbar-width:thin merge в html{} (EXP-135)
4. **Researcher -> Presenter pipeline** -- при источниках >200KB: researcher -> content_brief.md -> presenter -> HTML. Параллельные агенты для EN+RU (EXP-136)
5. **Horizontal scrollbar от glow** -- overflow-x:hidden на html,body + overflow:hidden на .slide в БАЗОВЫЙ CSS с самого начала (EXP-137)
6. **Navigation JS комплексный** -- arrows+scrollLock 800ms, F=fullscreen, T=TOC, progress bar gradient 3px, slide counter, IntersectionObserver threshold:0.5, @media print {display:none} (EXP-138)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 133 | pattern | "AI Product Launch" тёмная тема |
| 134 | pattern | Premium TOC overlay (3-column, categories, shortcuts pills) |
| 135 | pattern | Custom scrollbar matching theme (gradient + hover) |
| 136 | pattern | Researcher -> Presenter pipeline (2-агентный) |
| 137 | fix | Horizontal scrollbar от glow blobs (overflow-x: hidden) |
| 138 | improvement | Navigation JS комплексный (arrows, F, T, progress, scroll spy) |

### Контекст
- **Проект:** Telegram Business + Connected Bot v2.0 (2026-02-20)
- **Тема:** "AI Product Launch" -- тёмная #0a0c1a, Telegram blue #2AABEE + AI purple #7C5CFC
- **Формат:** 18 слайдов, zero-dependency, системные шрифты, inline SVG, CSS ambient glow
- **Элементы:** glassmorphism cards, gradient text, flow diagrams, chat mockup, KPI rings, CSS bar charts, timeline
- **Версии:** EN + RU (параллельные агенты)
- **Pipeline:** plan.md + sources -> researcher -> content_brief.md -> presenter -> HTML -> PDF (~9.5 MB)
- Подробности: [patterns/EXP-133-ai-product-launch-theme.md](patterns/EXP-133-ai-product-launch-theme.md)

### Новая тема (добавить в EXP-062)
- AI Product Launch: тёмная #0a0c1a, accent Telegram #2AABEE / AI purple #7C5CFC / green #10B981 / gold #F59E0B / red #EF4444, системные шрифты (Segoe UI, Inter, Helvetica Neue)

## GPU-презентация /simplify ревью (EXP-143)

### EXP-143: /simplify ревью HTML-презентаций перед PDF

**Дата:** 2026-03-02
**Контекст:** GPU-презентация 25 слайдов, 93KB HTML

**Проблемы найденные /simplify:**
1. Нет `@media print` правил -- JS scaling transform применялся при PDF-генерации
2. 330 inline style= атрибутов, ~160 дублируют паттерны -> нужны CSS-классы
3. Пустые phantom `<th>`/`<td>` в таблицах с разным кол-вом столбцов
4. 9 неиспользуемых CSS-правил (four-grid, vs-layout, vs-divider, card.elevated, mt-auto, tag-white, fs17, fs28)
5. 3 цвета (#5ec6ff, #f5a623, #c084fc) без CSS-переменных
6. Дублированные CSS-свойства (margin/padding reset, box-sizing, gap:0)
7. Базовый h3 font-size 22px но все inline переопределяют на 17px
8. 48 glow blobs с blur(150px) -- можно скрывать в @media print

**Решения применённые:**
- Добавить `@media print { transform: none !important; print-color-adjust: exact; }`
- JS: `window.matchMedia('print').matches` guard + beforeprint/afterprint listeners
- JS: `totalHeight = N * 1080` вместо `scrollHeight` (избегает circular dependency)
- Извлечь повторяющиеся inline паттерны в CSS-классы СРАЗУ при создании
- Проверять phantom cells когда несколько таблиц с разным числом колонок в одной плашке

**Правило:** Запускать /simplify ПОСЛЕ первой генерации HTML но ДО финального PDF. Три агента параллельно (reuse, quality, efficiency) дают полную картину за ~3 минуты.

**Вывод:** @media print + JS print guard = обязательный чеклист для КАЖДОЙ HTML-презентации. Добавить в базовый шаблон.

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 143 | pattern | /simplify ревью HTML-презентаций перед PDF |
| 144 | pattern | Enhanced glassmorphism rgba values (bg 0.06, border 0.10, border-top 0.15) |
| 145 | fix | scrollLock блокирует TOC goToSlide (сброс при открытии TOC) |
| 146 | fix | Dead CSS cleanup (неиспользуемые классы после итераций дизайна) |
| 147 | pattern | Gradient scrollbar + TOC overlay scrollbar (WebKit gradient + Firefox merge) |

### Контекст
- **Проект:** GPU-презентация (2026-03-02), 25 слайдов, 93KB HTML, 10.1 MB PDF
- Основные находки: @media print обязателен, inline styles -> CSS-классы, phantom table cells, неиспользуемые CSS-правила
- /simplify с тремя параллельными агентами (reuse, quality, efficiency) эффективен для HTML-презентаций
- **Glass redesign:** enhanced glassmorphism values (border-top highlight), gradient scrollbar, scrollLock vs TOC bug fix, dead CSS cleanup

## Changelog

### 2026-03-02 — GPU Presentation Glass Redesign + Fix
- **EXP-144**: Enhanced glassmorphism values — bg rgba 0.04→0.06, border 0.08→0.10, NEW border-top 0.15 (highlight), inset shadow 0.06→0.08. Brand variants: bg 0.06, border 0.15, border-top 0.25. Section-slides: ::before glass panel 700x300 centered (border-radius 32px, bg 0.03, border-top 0.10). PDF size unchanged (10.1 MB).
- **EXP-145**: scrollLock vs TOC interaction — goToSlide() checks scrollLock first → if user navigates with arrows, then opens TOC within 800ms and clicks item, goToSlide silently ignored but toggleTOC closes overlay. Fix: add `if (tocOpen) scrollLock = false;` in toggleTOC.
- **EXP-146**: Dead CSS after design iterations — new utility classes (.glass-card-accent, --space-* vars) defined but never used in HTML. Always grep for class usage after adding new CSS. Remove dead code in /simplify pass.
- **EXP-147**: Gradient scrollbar + TOC scrollbar — WebKit: 6px width, gradient thumb (NVIDIA green → Intel blue), hover brighter. Firefox: scrollbar-width:thin + scrollbar-color merged into existing html{} rule. TOC overlay: separate semi-transparent green scrollbar matching overlay bg rgba(10,14,23,0.97). Updates EXP-135 with gradient pattern.

- 2026-03-02: GPU-презентация /simplify ревью -- EXP-143 (1 запись): /simplify для HTML-презентаций перед PDF. @media print обязателен, inline styles → CSS-классы, phantom table cells, неиспользуемые CSS-правила, CSS-переменные для цветов. Три агента параллельно (reuse, quality, efficiency).
- 2026-02-28: AI Models Comparison update session -- EXP-139..142 (4 записи): mass data update workflow (parallel research 6 агентов → sequential MD/HTML/PDF update, 9 агентов ~30 мин), timeline grid 5x2 (до 10 событий на 1 слайде), backdrop-filter → solid rgba для PDF (opacity таблица замены, двойная версия HTML+PDF), анимированные PDF невозможны (PDF = статика ISO 32000, HTML = анимации, двойной формат).
- 2026-02-20: Telegram Business Bot "AI Product Launch" -- EXP-133..138 (6 записей): "AI Product Launch" тёмная тема (#0a0c1a + Telegram #2AABEE + purple #7C5CFC), premium TOC overlay (3-column grid, цветные категории, keyboard shortcuts pills), custom scrollbar с gradient hover, researcher->presenter pipeline (2-агентный для больших источников), horizontal scrollbar fix (overflow-x:hidden на html,body), navigation JS комплексный (arrows/F/T/progress/scroll spy). 18 слайдов, zero-dependency, EN+RU параллельные агенты, PDF ~9.5 MB.
- 2026-02-19: Belarus-Payment-Research "Glassmorphism v2" -- EXP-127..132 (6 записей): mesh gradients вместо bg-glow (radial-gradient на .slide, 0 PDF-раздутие), glassmorphism карточки v2 (backdrop-filter + glass border + ::before light line), gradient text + shimmer анимация, pill tags (border-radius:100px), semantic cards gradient bar сверху, presentation pipeline 5 агентов 3 волны (Content+CSS Architect → HTML Builder → Static+QA). Перенумерованы с EXP-099..104 на EXP-127..132 (конфликт).

> Более ранние записи (2026-02-18 и старше): [CHANGELOG_ARCHIVE.md](CHANGELOG_ARCHIVE.md)

## GPU-презентация — Performance Fixes (EXP-148..155)

### Критические уроки
1. **gradient text ненадёжен с transforms** -- `background-clip:text` + `-webkit-text-fill-color:transparent` делает текст невидимым в Chromium при `transform:scale()` на родителе. Решение: `color:#ffffff !important` + `filter:drop-shadow()` (EXP-148)
2. **пути к изображениям после реорганизации** -- при перемещении HTML-файла все относительные пути в JS (`photo-cache/filename.jpg`) становятся недействительными. Проверять `localPhotoMap`, `src =`, `url(` при mv (EXP-149)
3. **ambient-orb animation на всех слайдах** -- `animation: ambient-orb infinite` на `#deck .slide::before` запускает 30 GPU-слоёв с blur одновременно. Только `.slide.active::before` (EXP-150)
4. **will-change на статических элементах** -- `will-change: transform, box-shadow...` на `td`, `th`, `.chip`, `.tag` создаёт сотни GPU-слоёв. Только `:hover`, только `transform` и `opacity` (EXP-151)
5. **setInterval вместо events** -- `setInterval(fn, 220)` + `querySelectorAll` каждые 220мс. Решение: `CustomEvent('slide-changed')` + `dispatchEvent` в `goTo()` (EXP-152)
6. **color-mix() без :root fallback** -- `color-mix(in srgb, var(--a1) 30%, transparent)` возвращает invalid если `--a1` не определена. Добавлять `:root { --a1: var(--cyan); }` (EXP-153)
7. **dead CSS в multi-version файлах** -- `!important` война между версиями накапливает мёртвые блоки. Искать дублированные `::before`/`::after`, ранние `theme-N` блоки — удалять (EXP-154)
8. **карточки слипаются** -- низкая специфичность gap правил. Использовать `#deck .slide .branches { gap: 10px !important }` (EXP-155)

### Каталог
| EXP | Категория | Тема |
|-----|-----------|------|
| 148 | fix | gradient text ненадёжен с transforms → color+drop-shadow |
| 149 | fix | пути к изображениям после реорганизации папок |
| 150 | fix | ambient-orb animation только на .slide.active::before |
| 151 | fix | will-change только в :hover, только transform/opacity |
| 152 | fix | setInterval → CustomEvent 'slide-changed' + dispatchEvent |
| 153 | warning | color-mix() без :root fallback = silent invalid |
| 154 | fix | dead CSS в multi-version файлах (!important война) |
| 155 | fix | карточки слипаются = низкая специфичность gap |

### Детали

**EXP-148: gradient text ненадёжен в Chromium с transforms**
`background-clip: text` + `-webkit-text-fill-color: transparent` делает текст невидимым в Chromium когда родитель имеет `transform: scale()`. Симптом: заголовок выглядит тёмным/невидимым. Решение: использовать `color: #ffffff !important` + `filter: drop-shadow(0 2px 12px rgba(47,159,232,0.4))` — надёжнее и работает везде. Gradient text применять только как progressive enhancement через `@supports (background-clip: text)`.

**EXP-149: пути к изображениям ломаются после реорганизации папок**
Если HTML-файл перемещают относительно медиа-папок, все относительные пути в JS (`photo-cache/filename.jpg`) становятся недействительными. Симптом: photo-cards показывают fallback вместо изображений. При реорганизации директорий всегда проверять JS код на `localPhotoMap`, `src =`, `url(` паттерны и обновлять пути. Формула: `../../_MEDIA/photo-cache/` при структуре `_PRESENTATIONS/project/file.html` → `_MEDIA/photo-cache/`.

**EXP-150: ambient-orb animation на всех скрытых слайдах — GPU оверхед**
`animation: ambient-orb infinite` на `#deck .slide::before` запускает анимацию + `filter:blur(4px)` на ВСЕХ слайдах одновременно, включая скрытые. При 30 слайдах — 30 постоянных GPU слоёв с blur. Решение: убрать animation из базового `.slide::before`, добавить только для `.slide.active::before`. Убедиться что JS добавляет класс `.active` на текущий слайд.

**EXP-151: will-change на статических элементах — GPU memory pressure**
`will-change: transform, box-shadow, background, text-shadow` применённый постоянно к `td`, `th`, `.chip`, `.tag`, `.num` и другим часто встречающимся элементам создаёт сотни GPU-слоёв одновременно. Симптом: тормоза при смене слайда, высокое потребление GPU памяти. Решение: `will-change` только в `:hover` pseudo-class, только для `transform` и `opacity` (единственные свойства с реальным benefit от layer promotion).

**EXP-152: setInterval для отслеживания смены слайда — polling anti-pattern**
`setInterval(fn, 220)` который вызывает `document.querySelectorAll` каждые 220мс — неэффективная альтернатива событиям. Если в коде уже есть `goTo()` функция, добавить в неё `document.dispatchEvent(new CustomEvent('slide-changed', {detail:{index}}))` и слушать это событие. Убрать setInterval полностью.

**EXP-153: color-mix() без :root fallback — silent invalid color**
`color-mix(in srgb, var(--a1) 30%, transparent)` возвращает invalid если `--a1` не определена (например слайд без `.tone-*` класса). Браузер молча игнорирует всё свойство. Всегда добавлять в `:root { --a1: var(--cyan); --a2: var(--mint); }` как безопасный default. Также работает `var(--a1, #4DDFFF)` inline fallback.

**EXP-154: dead CSS blocks накапливаются в multi-version файлах**
Файлы с последовательными версиями CSS (V3→V5→V6→V8) накапливают мёртвые блоки: `theme-N::after` V4 полностью перекрывается V8 с `!important`. `::before` переопределяется 3 раза. При ревью multi-version CSS: искать дублированные `::before`/`::after` правила, `theme-N` блоки — удалять ранние версии. Симптом обнаружения: `!important` война где каждый следующий слой добавляет `!important` чтобы перебить предыдущий `!important`.

**EXP-155: карточки слипаются — низкая CSS-специфичность gap правил**
Если gap/margin для grid-контейнеров (`.decision`, `.proc`, `.cols2-4`) задан без высокоспецифичного селектора, другие стили могут его перекрыть. Симптом: карточки стоят вплотную. Решение: использовать `#deck .slide .branches { gap: 10px !important }` с полным путём селектора. Добавить `margin-bottom: 6px` на `.metric` как дополнительную защиту.
