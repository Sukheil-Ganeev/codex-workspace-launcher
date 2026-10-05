# Серия справочников — Полная документация

> Вызывается из SKILL.md §13. Содержит: CSS-компоненты, метрики, палитры, критические правила, список проектов.
> Загружай этот файл ТОЛЬКО при работе с серией справочников в D:/Downloads/Skill_Presentations/

### Проект

**Путь:** `D:/Downloads/Skill_Presentations/`
**Конвертер:** `_shared/convert_to_pdf.py` — универсальный, принимает путь к папке
**Формат:** 1920x1080, 16-20 слайдов, zero-dependency, ~4-5 MB

### Структура проекта

```
D:/Downloads/Skill_Presentations/
├── _shared/
│   └── convert_to_pdf.py          # python convert_to_pdf.py "../папка/"
├── telegram-справочник/            # ✅ Прототип, тёмная тема
├── git-github-справочник/          # ✅ GitHub Dark (v2)
├── claude-agent-teams/             # ✅ Claude Editorial (светлая)
├── payment-integration-справочник/ # ✅ (v2)
├── max-справочник/                 # ✅
├── youtube-справочник/             # ✅ YouTube Studio Dark
├── threads-справочник/             # ✅ Neon Wire
├── vk-video-справочник/            # ✅ Video Stream
├── seo-справочник/                 # ✅ Search Radar
├── database-sql-справочник/        # ✅
├── монетизация-контента-справочник/# ✅
├── партнёрские-программы-справочник/# ✅
├── рекламные-платформы-справочник/ # ✅
├── html-css-справочник/            # ✅
├── javascript-nodejs-справочник/   # ✅ Amber Terminal
├── whatsapp-справочник/            # ✅ WhatsApp Encrypted
├── whatsapp-business-api-справочник/# ✅
├── instagram-справочник/           # ✅ Aurora Warm
├── vk-справочник/                  # ✅ Steel Canvas
├── yandex-cloud-справочник/        # ✅ Red Blueprint
├── puzzlebot-справочник/           # ✅ Puzzle Blueprint
├── make-com-справочник/            # ✅ Scenario Graph
├── salebot-справочник/             # ✅ Channel Pulse
├── 08_business/обмен-валюты/       # ✅ Cash Flow (бизнес)
```

### Порядок пачек

| Пачка | Справочники | Статус |
|-------|-------------|--------|
| Прототип | telegram | ✅ Готов |
| Спец | claude-agent-teams | ✅ Готов |
| Пачка 1 | git-github ✅, html-css ✅, javascript-nodejs ❌, payment-integration ✅ | 🔄 3/4 |
| Пачка 2 | whatsapp ✅, whatsapp-business ✅, instagram ❌, youtube ✅ | 🔄 3/4 |
| Пачка 3 | vk ❌, vk-video ✅, max ✅, threads ✅ | 🔄 3/4 |
| Пачка 4 | yandex-cloud ❌, seo ✅, database-sql ✅ | 🔄 2/3 |
| Пачка 5 | монетизация ✅, партнёрские ✅, рекламные ✅ | ✅ 3/3 |
| Пачка 6 | puzzlebot ✅, make-com ✅, salebot ✅ | ✅ 3/3 |
| Бизнес | обмен-валюты ✅ | ✅ 1/1 |
| **Итого** | **24/24 готово** | **100%** |

### Workflow создания нового справочника

1. **Прочитать SKILL.md справочника** — через `Skill(название-справочник)`
2. **Создать директорию** — `mkdir -p "D:/Downloads/Skill_Presentations/название/output"`
3. **Создать presentation.html** — копировать CSS-базу из готового, менять `:root` палитру
4. **Конвертировать** — `python _shared/convert_to_pdf.py "../название/"`
5. **Проверить PDF** — на обрезку контента, читаемость
6. **Бэкап перед правками** — `presentation_backup_v1.html`

### CSS дизайн-система (общая для всех)

**Базовые компоненты** (копируются из справочника в справочник):

| Компонент | CSS-класс | Описание |
|-----------|-----------|----------|
| Слайд | `.slide` | 1920x1080, flex column, page-break |
| Фон-свечение | `.bg-glow` | `filter: blur(150px)`, 3 варианта |
| Карточка | `.card` | border-radius: 16px, padding: 32px |
| Таблица | `.styled-table` | Чередующиеся строки, цветная шапка |
| Блок кода | `.code-block` | Тёмный фон #010409, подсветка |
| Список | `.feature-list` | Цветные маркеры |
| Тег | `.tag` | .tag-blue, .tag-green, .tag-yellow, .tag-red |
| Акцент-бокс | `.highlight-box` | Плашка внизу слайда |
| Timeline | `.timeline` | Горизонтальная цепочка шагов |
| Flow | `.flow-container` | Блоки со стрелками → |
| VS-layout | `.vs-layout` | Сравнение двух вариантов |
| Лейауты | `.two-columns`, `.three-columns`, `.four-grid` | Grid-лейауты |
| Скроллбар | `::-webkit-scrollbar` | 6px gradient thumb, per-element варианты |

**Уникальные компоненты по темам:**

| Тема | Компоненты |
|------|-----------|
| Telegram | `.chat-mockup`, `.chat-msg`, `.chat-btn` — имитация чата |
| Git/GitHub | `.terminal`, `.diff-block`, `.diff-add/.diff-del` — терминал + diff |
| WhatsApp | `.wa-chat`+`.wa-chat-header`+`.wa-chat-avatar` (чат-мокап), `.wa-bubble`+`.wa-bubble-in`/`.wa-bubble-out` (пузыри + `.wa-check` галочки), `.wa-bubble-btns` (inline кнопки), `.wa-template`+`.wa-tmpl-hdr`+`.wa-tmpl-body`+`.wa-tmpl-btns` (template preview), `.enc-hex` (hex-декорации opacity 0.07), `.title-badge` (lock icon), `.glow`+`.g-green`/`.g-teal`/`.g-blue` (ambient glow blobs), `.card-green`/`.card-teal`/`.card-blue`/`.card-warn` (семантические left-border варианты карточек), gradient text на h1/h2 `.accent`, `.section-label::before` (green bar), `.code-block::after` (teal accent strip), `.code-lang` (teal badge) |
| WA Business | `.verification-badge` + `.badge-text` (Gold verified badge), `.product-catalog` + `.product-card` (каталог 3col), `.shopping-cart` + `.cart-total` (корзина), `.quality-bar` (рейтинг шкала), green+gold палитра |
| Instagram | `.ig-post`, `.ig-story-ring` — посты и Stories |
| Threads | `.thread-decor` (SVG нити), `.threads-post` (пост-мокап), glassmorphism cards |
| VK Video | `.vplayer` (player mockup), `.play-lg` (play button), `.live` (LIVE badge) |
| YouTube | `.yt-thumb` (thumbnail 16:9), `.youtube-play-btn` (SVG play), `.yt-chart-bars` (analytics chart), `.q-bar` (quota bar), `.metric` (stat card + bottom accent), `.deco-grid` (subtle grid), `.deco-circle` (ring decoration), `.code-lang` (language badge on code blocks) |
| Database-SQL | SQL syntax (`.kw`,`.tbl`,`.col`,`.str`,`.type`), ERD SVG diagram, `.code-note` (описание перед code-block), `.slide-decor-grid` (кольца), `.slide-decor-corner` |
| Payment | `.payment-flow` + `.flow-step` (5 этапов платежа), `.currency-badge` (AED/USD/RUB/USDT), `.card-mockup` + `.card-chip` (банковская карта), `.status-indicator`, `.security-badge` |
| Max | `.max-chat` + `.max-chat-header` (чат-мокап), `.message`+`.message-bubble` (пузыри бот/юзер), `.bot-keyboard`+`.kb-btn` (клавиатура с цветами primary/secondary/positive/negative), `.miniapp-card`+`.miniapp-badge` (карточка Mini App), `.msg-decoration`+`.msg-bubble-deco` (декоративные пузыри фона) |
| PuzzleBot | `.puzzle-card` (карточка с цветным border-top), `.builder-flow`+`.builder-block`+`.builder-connector` (цепочка блоков конструктора со стрелками), `.kb-preview`+`.kb-header`+`.kb-btn` (превью Telegram-клавиатуры), `.block-badge` (бейдж типа блока: text/action/condition/api) |
| Make.com | `.scenario-module` (нода модуля со свечением), `.scenario-flow`+`.conn-line`+`.conn-arrow` (цепочка сценария с коннекторами), `.ops-panel` (панель операций/статистики), `.mapping-table` (маппинг данных между модулями) |
| SaleBot | `.channel-badges` (бейджи 8 мессенджеров с аутентичными цветами), `.crm-pipeline` (kanban воронка продаж), `.inbox-list`+`.inbox-item` (единое окно сообщений), `.funnel-bar` (воронка конверсий) |
| Cash Flow | `.danger-shake` (shake animation), `.bar-grow` (bar chart animation), `.anim` (trigger class), `scalePresentation()` (viewport zoom) |

### Метрики композиции (эталон)

```
Slide padding:        70px top/bottom, 100px left/right
Title h1:             48px, weight 700
Subtitle:             22px, weight 400, --text-secondary
Section label:        13px, uppercase, letter-spacing 3px
Card padding:         32px (28px если плотный слайд)
Card gap:             32px (16-20px если плотный)
Table font:           15-17px (13px для шпаргалок)
Code font:            13-15px (12-12.5px для плотных)
Feature list:         16-18px
Highlight-box:        20px 28px padding
Slide number:         15px, bottom-right
Top gradient:         4px height
Scrollbar width:      6px (WebKit), thin (Firefox)
Glass card bg:        rgba(255,255,255, 0.06), border-top: 0.15
```

### Тема-палитра (менять в :root)

```css
/* Пример: Git Terminal (GitHub Dark) */
:root {
  --bg-dark: #0d1117;
  --bg-slide: #0d1117;
  --bg-card: #161b22;
  --bg-card-elevated: #1c2128;
  --accent-1: #58a6ff;    /* GitHub blue */
  --accent-2: #3fb950;    /* GitHub green (diff add) */
  --accent-3: #f85149;    /* GitHub red (diff remove) */
  --accent-4: #d29922;    /* GitHub yellow (warning) */
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --text-code: #79c0ff;
  --border-subtle: rgba(240,246,252,0.06);
  --border-light: rgba(240,246,252,0.12);
  --gradient-top: linear-gradient(90deg, #58a6ff, #3fb950, #d29922);
}
```

### Светлая тема-палитра (Claude Editorial Light)

```css
/* Пример: Claude Agent Teams (Warm Light) */
:root {
  --bg-page: #F3F1EC;
  --bg-slide: #FAFAF7;
  --bg-card: #FFFFFF;
  --bg-card-alt: #F5F2ED;
  --bg-code: #FAF8F5;           /* ТЁПЛЫЙ light, НЕ тёмный! */
  --claude: #D4714E;             /* Terracotta акцент */
  --purple: #6E4FE0;
  --green: #1D8A5A;
  --blue: #2E6FD9;
  --amber: #C06E09;
  --text: #1B1B1B;
  --text-2: #4A4A4A;
  --text-3: #7A7A7A;
  --border: rgba(0,0,0,0.07);
  --grad-top: linear-gradient(90deg, #D4714E, #C8956F, #6E4FE0);
}
```

```css
/* Cash Flow (Обмен валюты) */
:root {
  --bg-dark: #0B1120;
  --bg-slide: #0B1120;
  --bg-card: #111D36;
  --bg-card-elevated: #152040;
  --accent-emerald: #10B981;    /* деньги, AED */
  --accent-gold: #F59E0B;       /* финансы, премиум */
  --accent-blue: #3B82F6;       /* крипто, технологии */
  --accent-red: #EF4444;        /* мошенники, штрафы */
  --text-primary: rgba(255,255,255,0.92);
  --text-secondary: rgba(255,255,255,0.65);
  --gradient-top: linear-gradient(90deg, #10B981, #F59E0B, #3B82F6);
}
```

**Дополнительные палитры** (Neon Wire, WhatsApp Encrypted, Video Stream, Search Radar, Puzzle Blueprint, Scenario Graph, Channel Pulse, Cash Flow) + правила для светлых тем:

→ Подробнее: `references/theme-palettes.md`

### Standalone бизнес-презентации (White Label и подобные)

| Компонент | CSS-класс | Описание |
|-----------|-----------|----------|
| Watermark числа | `.watermark` | 280px, opacity 0.04, фоновые якоря |
| Progress bar | `.topline::after` | Ширина per slide (1/N, 2/N...100%) |
| KPI ring | `.kpi-ring` svg | Круговой прогресс, stroke-dasharray/offset |
| Bar chart | `.bar-track` + `.bar-fill` | CSS-бары для финмоделей |
| Checklist | `.checklist` + `.check-box` | Кликабельные чекбоксы (только HTML) |
| Objection card | `.card .objection` + `.response` | Возражение/ответ с разделителем |
| Score box | `.score .box` | Скоринг с цветным border-top |
| Slide photo | `.slide-photo` | Декоративное фото, luminosity blend |

**Навигационный JS:** Smooth scroll + scroll spy → обязательно scrollLock на 800ms (EXP-062).
**Стоковые фото:** Unsplash URL + gradient overlay 85-95% / `mix-blend-mode: luminosity; opacity: 0.5` (EXP-064).
**SVG иконки:** 22x22 stroke-based, `fill="none" stroke="currentColor"`, наследуют цвет от `.card.warn/.danger/.violet` (EXP-068).
**Уникальные фоны:** Каждый slide-N → свои radial-gradient позиции/цвета из палитры (EXP-067).

### КРИТИЧЕСКИЕ ПРАВИЛА ДЛЯ СПРАВОЧНИКОВ

1. **Контент обрезается на слайде** → уменьшить font-size кода (13→12.5px), padding (32→28px), gap (32→16px), line-height (1.6→1.45) — НЕ удалять контент
2. **Не переусердствуй с фиксами** — если пользователь просит "чуть подправить", менять 1 параметр (margin 16→20px), НЕ переписывать весь блок
3. **Бэкап перед правками** — всегда `presentation_backup_v1.html`
4. **Chat/terminal mockup** занимает много места — уменьшить padding/font при нехватке
5. **Шпаргалка-слайд** — самый плотный (font-size 12-13px, padding 20px, gap 12px)
6. **Светлая тема: highlight-box** → два варианта замены:
   - **Вариант A (полная карточка):** icon 52×52 + заголовок в цвет акцента + текст — для выводов с 2+ строками
   - **Вариант B (inline карточка):** icon 22px + `<strong>Label:</strong> текст` — для однострочных результатов/советов
   - Варианты: инсайт (🧠 purple), warning (⚠️ amber), tip (💡 green), результат (✅ green), процесс (🔄), выбор (grid ИЛИ)
   - **⚠️ ОБЯЗАТЕЛЬНО:** Перед заменой → `grep "hbox" file.html` → список ВСЕХ → заменить ВСЕ → grep после = 0. (EXP-028, 3 раунда фиксов!)
7. **Светлая тема: терминалы** → warm light (#FDFCF9), НЕ тёмные (#1E1E2E) — иначе visual shock (EXP-029)
8. **Тени на тёмном фоне = "грязь"** → убирать `box-shadow`, использовать тонкие нейтральные бордеры `rgba(255,255,255,0.06)`. Неоновые бордеры — только opt-in `.card-accent` (EXP-033)
9. **split-40-60 vs split-50-50** → если в правой колонке bar chart / инфографика — использовать `split-50-50`, иначе бары выпирают правее текста (EXP-034)
10. **four-grid align-items** → по умолчанию `stretch` (одинаковая высота карточек в ряду). Ставить `start` ТОЛЬКО если карточки не должны тянуться (EXP-035)
11. **Пустое пространство** → оборачивать контент в `.card` div'ы для лучшего заполнения. Добавлять highlight-box с советом для баланса колонок (EXP-036)
12. **code-note паттерн** → перед code-block добавлять `.code-note` div с кратким описанием что делает код. Повышает юзабилити для неразработчиков (EXP-039)
13. **Code-block bg тонирование** → НЕ использовать чёрный `#010409` — слишком контрастный. Тонировать под тему (Data Vault: `#081228`, FinTech: `#0a1628`, Search Radar: `#111d22`). Muted dots 7px, opacity 0.5 (EXP-040)
14. **card-fill + three-columns = некрасивые разрывы** → `.card-fill` (justify-content: space-between) на карточках в three-columns с разным количеством контента создаёт огромные пустоты между заголовком и содержимым. Использовать `.three-columns.stretch` (равная высота) БЕЗ card-fill — контент идёт естественным потоком сверху (EXP-049)
15. **Заполнение пустоты внизу слайдов** → для каждого слайда добавлять уникальный визуальный элемент: flow-container (pipeline), metric-карточки (4-5 в ряд), highlight-box с правилом, timeline (roadmap). Если highlight-box тесно — заменить на лёгкую текстовую строку под flow. Это полезный контент, НЕ "заливка пустоты" (EXP-049)
16. **Highlight-box слипание с карточками** → НЕ ставить `flex: 1` на grid-контейнер (`.two-columns`, `.three-columns`, `.four-grid`) если на том же уровне `.content` есть highlight-box. `flex: 1` на grid + `margin-top: auto` на highlight-box = 0px gap (слипание). Решение: убрать `flex: 1` с grid, в CSS highlight-box добавить `margin-top: 20px; flex-shrink: 0`. Добавлять `flex: 1` inline только на слайды БЕЗ highlight-box (EXP-053)
17. **Viewport scaling для десктопа** → `<meta name="viewport" content="width=1920">` НЕ работает на десктопе. Для HTML-просмотра добавлять JS: `transform: scale(window.innerWidth / 1920)` + ограничение `html.height`. Без этого правая часть обрезается на экранах < 1920px (EXP-090). **ВАЖНО:** Если навигация использует `position: fixed`, применять `zoom` вместо `transform: scale` (EXP-094/EXP-125). `zoom` не ломает fixed positioning. Защита PDF: `@media print { body { zoom: 1 !important; } }`
