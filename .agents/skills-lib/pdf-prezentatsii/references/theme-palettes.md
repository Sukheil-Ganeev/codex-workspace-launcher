# Тема-палитры для серии справочников (Skill Presentations)

> Перенесено из SKILL.md. Базовые палитры (Git Terminal Dark, Claude Editorial Light) остались в SKILL.md.

---

## Neon Wire тема-палитра (Threads)

```css
/* Пример: Threads "Neon Wire" — тёмно-синий + glassmorphism + SVG нити */
:root {
  --bg-void: #05050a;
  --bg-slide: #08081a;
  --bg-glass: rgba(255,255,255,0.04);
  --neon-pink: #e1306c;
  --neon-violet: #8b5cf6;
  --neon-cyan: #22d3ee;
  --text-primary: #f0f0ff;
  --text-secondary: #b0b0cc;
  --text-muted: #6b6b8d;
  --border-glass: rgba(255,255,255,0.07);  /* Нейтральные, НЕ неоновые! */
  --gradient-wire: linear-gradient(90deg, #e1306c, #8b5cf6, #22d3ee);
  --gradient-pink-glow: radial-gradient(ellipse at 25% 40%, rgba(225,48,108,0.08) 0%, transparent 60%);
}
```

**ВАЖНО для Neon Wire темы:**
- Тени на тёмном фоне = "грязь" → убирать `box-shadow`, использовать тонкие нейтральные бордеры (EXP-033)
- Неоновые бордеры — только opt-in через `.card-accent`, не на каждой карточке
- gradient-mesh (radial-gradient) вместо круглых bg-glow — мягче и атмосфернее
- SVG `.thread-decor` — декоративные нити, визуальная метафора "threads"

---

## WhatsApp Encrypted тема-палитра

```css
/* Пример: WhatsApp "Encrypted" — настоящие цвета WA dark mode + шифрование */
:root {
  --bg: #0b141a;
  --surface: #111b21;
  --surface-2: #1a2730;
  --surface-3: #202c33;
  --wa-green: #25d366;
  --wa-teal: #128c7e;
  --wa-blue: #34b7f1;
  --wa-check: #53bdeb;
  --wa-out: #005c4b;          /* исходящие пузыри */
  --wa-in: #202c33;           /* входящие пузыри */
  --text: #e9edef;
  --text-2: #8696a0;
  --text-3: #667781;
  --code-bg: #0a1a12;         /* green-tinted по EXP-040 */
  --border: rgba(134,150,160,0.15);
  --grad-top: linear-gradient(90deg, #25d366, #128c7e, #34b7f1);
}
```

**ВАЖНО для WhatsApp Encrypted темы:**
- `.enc-hex` — декоративные hex-строки (opacity 0.07), визуальная метафора шифрования
- Пузыри с хвостиками: `border-radius: 10px 10px 10px 2px` (in), `10px 10px 2px 10px` (out)
- `.wa-check` голубые галочки `#53bdeb` — культовый элемент WA
- Template preview — `.wa-template` с header/body/footer/buttons секциями
- Code-block bg = `#0a1a12` (green-tinted), НЕ чёрный
- **Visual enrichment v2:** `.glow` ambient blobs (filter:blur 120px, 2 на слайд), `.card-green`/`.card-teal`/`.card-blue`/`.card-warn` (semantic left-border 3px), gradient text на `.accent` spans (green→blue), `.section-label::before` (green bar 4×18px), `.code-block::after` (teal strip 2px), `.code-lang` (teal badge вместо прозрачного), `.styled-table th` (tinted bg rgba(teal,0.12)), `.tag` borders (rgba 0.25)
- **PDF size:** 9.6 MB (v2 с glow blobs). Glow blobs с filter:blur добавляют ~6 MB. Не использовать linear-gradient на card-accent/highlight-box — solid rgba вместо (EXP-038)

---

## Video Stream тема-палитра (VK Video)

```css
/* Пример: VK Video "Video Stream" — тёмный + красно-синий + фиолетовый */
:root {
  --bg-dark: #06060e;
  --bg-slide: #0a0a14;
  --bg-card: rgba(22, 22, 42, 0.85);
  --bg-card-solid: #16162a;
  --bg-card-elevated: #1e1e3a;
  --accent-1: #0077ff;      /* VK blue */
  --accent-1-light: #3399ff;
  --accent-2: #ff4444;      /* Play red */
  --accent-2-light: #ff6b6b;
  --accent-3: #8b5cf6;      /* Purple depth */
  --text-primary: #f1f5f9;
  --text-secondary: #a8b2c8;
  --text-muted: #5a6078;
  --text-code: #7dd3fc;
  --border-subtle: rgba(255,255,255,0.06);
  --border-light: rgba(255,255,255,0.10);
  --gradient-top: linear-gradient(90deg, #0077ff 0%, #8b5cf6 40%, #ff4444 70%, #ff8844 100%);
  --gradient-play: radial-gradient(circle, #ff5555, #cc0000);
  --gradient-blue: linear-gradient(135deg, #0055cc, #0088ff);
  --gradient-red: linear-gradient(135deg, #cc0022, #ff4444);
  --card-border: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.03));
}
```

**ВАЖНО для Video Stream темы:**
- Gradient borders через `mask-composite` (не `border-image`) — работает в PDF (EXP-031)
- Card top shine — тонкий блик `::after` вверху карточки (1px `linear-gradient`)
- 3-цветная палитра (blue + red + purple) — глубже чем 2 цвета
- Таблицы оборачивать в `.card` с `padding:0;overflow:hidden` для лучшего вида
- **НЕ** использовать SVG `feTurbulence` noise-текстуры — раздувает PDF x2.5 (EXP-030)

---

## Search Radar тема-палитра (SEO)

```css
/* Пример: SEO "Search Radar" — тёмный сине-зелёный + SERP mockups */
:root {
  --bg-dark: #080e10;
  --bg-slide: #0a1214;
  --bg-card: #1a272c;
  --bg-card-elevated: #1e2f35;
  --accent-1: #4caf50;      /* SEO green */
  --accent-2: #2196f3;      /* Google blue */
  --accent-3: #ff9800;      /* Warning orange */
  --text-primary: #e8eef1;
  --text-secondary: #8da0a8;
  --text-muted: #5c7580;
  --text-code: #8dd6a0;
  --border-subtle: rgba(255,255,255,0.06);
  --gradient-top: linear-gradient(90deg, #4caf50, #2196f3, #ff9800);
}
```

**ВАЖНО для Search Radar темы:**
- SERP mockup на титульном слайде — 3 результата + "People Also Ask" блок
- Google Maps Pack mockup на Local SEO слайде
- Code-block bg: `#111d22` (сине-зелёный тинт, НЕ чёрный — EXP-040/049)
- `.three-columns stretch` для равной высоты карточек — БЕЗ `card-fill` (EXP-049)
- flow-container для визуализации процессов (crawl flow, content pipeline, link building, SEO roadmap)
- Заполнение пустоты: flow-container, metric cards, highlight-box, timeline — полезный контент, не "заливка"

---

## Puzzle Blueprint тема-палитра (PuzzleBot)

```css
/* Пример: PuzzleBot "Puzzle Blueprint" — пазл-конструктор, blueprint dot-grid */
:root {
  --bg-dark: #0C0E22;
  --bg-slide: #10122A;
  --bg-card: #1A1D3D;
  --bg-card-elevated: #222550;
  --accent-1: #6C5CE7;      /* Indigo */
  --accent-2: #A8E06C;      /* Lime */
  --accent-3: #FF7EB3;      /* Soft Rose */
  --accent-4: #60A5FA;      /* Info blue */
  --text-primary: #E8E8F4;
  --text-secondary: #9B9BC0;
  --text-muted: #6B6B8D;
  --text-code: #C4B5FD;
  --border-subtle: rgba(108,92,231,0.10);
  --border-light: rgba(108,92,231,0.18);
  --gradient-top: linear-gradient(90deg, #6C5CE7, #A8E06C, #FF7EB3);
}
```

**ВАЖНО для Puzzle Blueprint темы:**
- `.builder-flow` — цепочка блоков конструктора. Стрелки через CSS border triangle на `::after`. Размеры стрелок: 5px border-left, 4px transparent — не больше, иначе грубо
- `.puzzle-card` — НЕ использовать `::before` для коннекторов-кружочков на four-grid (выглядит как мусор). Вместо этого `border-top: 2px solid` с цветом акцента
- Blueprint dot-grid: `radial-gradient(circle, rgba(108,92,231,0.04) 1px, transparent 1px)` 32px — тонкая текстура
- three-columns с вложенными div'ами создаёт лесенку → использовать плоский 3×N grid без вложенности
- Code bg: `#12143A` (indigo-tinted)

---

## Scenario Graph тема-палитра (Make.com)

```css
/* Пример: Make.com "Scenario Graph" — граф сценариев, связанные модули */
:root {
  --bg-dark: #0A0920;
  --bg-slide: #110E20;
  --bg-card: #1C1838;
  --bg-card-elevated: #24204A;
  --accent-1: #B24BF3;      /* Magenta */
  --accent-2: #00D4FF;      /* Electric Cyan */
  --accent-3: #FF6B6B;      /* Warm Coral */
  --accent-4: #FFD93D;      /* Yellow */
  --text-primary: #F0EEFF;
  --text-secondary: #A8A0CC;
  --text-muted: #6B648D;
  --text-code: #D4B0FF;
  --border-subtle: rgba(178,75,243,0.10);
  --border-light: rgba(178,75,243,0.18);
  --gradient-top: linear-gradient(90deg, #B24BF3, #00D4FF, #FF6B6B);
}
```

**ВАЖНО для Scenario Graph темы:**
- `.scenario-module` — нода модуля с box-shadow (rgba(accent,0.15)) для свечения
- `.scenario-flow` + `.conn-line` + `.conn-arrow` — коннекторы сценария. Стрелки через CSS border triangle
- `.ops-panel` — панель с операциями/минутами/MB, border-left: 3px solid accent-1
- `.mapping-table` — слева исходные, справа целевые поля с → между колонками
- Node-grid: 48px (крупнее чем dot-grid, разреженнее) — `radial-gradient(circle, rgba(178,75,243,0.04) 1.5px, transparent 1.5px)`
- Code bg: `#13103A` (magenta-tinted)
- styled-table: `border-collapse: separate; border-spacing: 0; border-radius: 14px` — скруглённые углы на ВСЕХ таблицах

---

## Channel Pulse тема-палитра (SaleBot)

```css
/* Пример: SaleBot "Channel Pulse" — мультиканальный пульс, CRM воронка */
:root {
  --bg-dark: #080C1A;
  --bg-slide: #0C1024;
  --bg-card: #161C38;
  --bg-card-elevated: #1E254A;
  --accent-1: #1B6EF3;      /* Royal Blue */
  --accent-2: #2DD4A8;      /* Vivid Mint */
  --accent-3: #FF8C42;      /* Tangerine */
  --accent-4: #F471B5;      /* Pink */
  --text-primary: #E8ECF8;
  --text-secondary: #9BA4C0;
  --text-muted: #636B88;
  --text-code: #93C5FD;
  --border-subtle: rgba(27,110,243,0.10);
  --border-light: rgba(27,110,243,0.18);
  --gradient-top: linear-gradient(90deg, #1B6EF3, #2DD4A8, #FF8C42);
}
```

**ВАЖНО для Channel Pulse темы:**
- `.channel-badges` — 8 мессенджеров (Telegram=blue, WhatsApp=green, VK=blue-grey, Instagram=gradient-pink, Facebook=dark-blue, Viber=purple, Avito=green, OK=orange) — аутентичные цвета каждого
- `.crm-pipeline` — kanban с 4 колонками (Новые→Переговоры→Решение→Оплачено), карточки с цветными левыми бордерами
- `.inbox-list` + `.inbox-item` — имитация единого окна оператора с аватарами мессенджеров
- `.funnel-bar` — горизонтальная воронка конверсий (100%→68%→42%→28%) с цветовой градацией
- Pulse-wave: `radial-gradient(ellipse at center, rgba(27,110,243,0.06) 0%, transparent 60%)` — пульсирующий фон
- Code bg: `#0E1430` (blue-tinted)

---

## Общие правила для светлых тем

- Терминалы/code-блоки — **warm light** (#FDFCF9), НЕ тёмные! (EXP-029)
- Highlight boxes для выводов → **карточки с иконкой + gradient bg** (EXP-028)
- Шрифты на 20% крупнее чем на тёмной теме (меньше контраст = нужно больше размера)
