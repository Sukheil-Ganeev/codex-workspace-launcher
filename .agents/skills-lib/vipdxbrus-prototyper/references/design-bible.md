# VIP-DXB-RUS -- Design Bible for Prototypes

## 1. Brand

- **Name:** VIP-DXB-RUS (tourism)
- **Positioning:** Luxury minimalism, warm tones, personal approach
- **Audience:** CIS tourists (RU/EN), Dubai & Abu Dhabi
- **Logo in nav:** TEXT "VIP·DXB·RUS" (Tenor Sans), NEVER PNG

### Color Palette

| Name | HEX | CSS Variable | Role |
|------|------|-------------|------|
| Copper | `#C4896E` | `--color-copper` | Primary accent (CTA, hover, icons). 1-5% of page |
| Copper Hover | `#B07A5F` | `--color-copper-hover` | Hover state |
| Copper Light | `#D49D85` | `--color-copper-light` | Focus rings, pressed |
| Sand | `#DEB7A4` | `--color-sand` | Warm section backgrounds (opacity 0.3) |
| Peach | `#E7C6B4` | `--color-peach` | Card backgrounds, decorative |
| Warm White | `#FDFBF9` | `--color-bg-primary` | Main page bg (~60%) |
| Light Sand | `#F5EDE7` | `--color-bg-secondary` | Alternating sections (~20%) |
| Card BG | `#FAF6F2` | `--color-bg-card` | Card substrate |
| Warm Dark | `#1A1714` | `--color-bg-dark` | Hero, footer, premium (~15%) |
| Text Primary | `#1A1A1A` | `--color-text-primary` | Body text (NOT pure #000) |
| Text Secondary | `#6B6156` | `--color-text-secondary` | Captions, meta |
| Text Tertiary | `#9A8D80` | `--color-text-tertiary` | Muted, placeholder |
| Text on Dark | `#F5F0EB` | `--color-text-on-dark` | Body on dark bg |
| Border | `#E8DDD3` | `--color-border` | Cards, dividers |
| WhatsApp | `#25D366` | `--color-whatsapp` | ONLY for WhatsApp CTA |
| Rating | `#D69E2E` | `--color-rating` | Stars |
| Old Price | `#9A8D80` | `--color-price-old` | Strikethrough price |

**Pricelist uses different copper: `#B88D73`**

### Fonts

| Font | Weight | Purpose | Google Fonts |
|------|--------|---------|-------------|
| Tenor Sans | 400 | Headings (UPPERCASE H1-H2) | Yes (cyrillic) |
| Montserrat | 300-500 | Body, CTA, nav, meta | Yes (cyrillic) |
| Cormorant SC | 400-600 | Eyebrow labels, accent | Yes (cyrillic) |

```
Google Fonts URL:
https://fonts.googleapis.com/css2?family=Tenor+Sans&family=Montserrat:wght@300;400;500;600&family=Cormorant+SC:wght@400;600&display=swap
```

## 2. Prototype Style Rules

| Rule | Value |
|------|-------|
| border-radius | `0` on buttons and cards (luxury = sharp) |
| Border width | `0.8px` (thin, One&Only pattern) |
| Animations | 200-300ms `cubic-bezier(0.165, 0.84, 0.44, 1)` |
| Icons | SVG inline (Lucide style, 1.5px stroke), NOT emoji |
| Photos | Unsplash warm tones: sand, gold, beige, copper, desert, Dubai |
| Color ratio | 85-90% neutrals, 5-10% photos, 1-5% Copper |
| Uppercase | H1, H2, nav, CTA, labels. NOT body, NOT H3 |
| Font-weight | 400 for headings (luxury = light), max 500 for CTA |
| Min font | 12px (caption), body >= 16px |
| No pure black | Use `#1A1A1A`. No pure white -- use `#FDFBF9` |
| No orange | `#FE620D` = competitor color. Forbidden |
| Pills | ONLY for main CTA. Utility buttons = sharp corners |

## 3. Owner Preferences

**Likes:** Luxury minimalism, large text, whitespace, Copper as accent (not dominant), subtle animations.

**Dislikes:** PNG logo in nav (asked 3+ times), truncated text (ellipsis), mismatched nav/footer grouping, unequal card heights.

**Perfectionism rules:**
- ALL cards must show `oldPrice + price` (even demo)
- Equal card height within same row (flex, CTA pinned to bottom)
- Baseline alignment mandatory
- Footer = mirror of Nav (same category grouping)
- If 2 CTAs side-by-side -- equal width and visual weight

## 4. Spacing & Layout

### Spacing Scale (base 4px)

| Token | Value | Use |
|-------|-------|-----|
| `--space-1` | 4px | Icon-text gap |
| `--space-2` | 8px | Tag padding, inline |
| `--space-3` | 12px | Label-to-input |
| `--space-4` | 16px | Component padding (mobile) |
| `--space-5` | 20px | Card body padding |
| `--space-6` | 24px | Grid gap, card gap |
| `--space-8` | 32px | Section padding (mobile) |
| `--space-10` | 40px | Component gap (desktop) |
| `--space-12` | 48px | Nav padding |
| `--space-16` | 64px | Section padding (tablet) |
| `--space-20` | 80px | Between sections (mobile) |
| `--space-24` | 96px | Between sections (tablet) |
| `--space-28` | 112px | Between sections (desktop) |

### Semantic Spacing

| Token | Desktop | Tablet | Mobile |
|-------|---------|--------|--------|
| Section gap | 112px | 96px | 80px |
| Section padding-x | 48px | 32px | 24px |
| Card gap | 24px | 24px | 16px |
| Card padding | 20px | 20px | 16px |

### Z-Index

| Token | Value | Element |
|-------|-------|---------|
| `--z-base` | 1 | Base |
| `--z-dropdown` | 10 | Dropdowns |
| `--z-sticky` | 50 | Sticky CTA |
| `--z-nav` | 100 | Navigation |
| `--z-menu-overlay` | 200 | Mobile menu |
| `--z-modal` | 300 | Modals |
| `--z-whatsapp` | 1000 | WhatsApp, AI chat |

### Container

| Variant | max-width |
|---------|-----------|
| Default | 1200px |
| Wide | 1440px |
| Narrow | 680px |

## 5. Breakpoints

| Device | Width |
|--------|-------|
| iPhone SE | 375px |
| iPhone 14 | 390px |
| iPhone 14 Pro Max | 430px |
| Samsung S24 | 360px |
| Samsung S24 Ultra | 412px |
| Pixel 8 | 412px |
| iPad Mini | 744px |
| iPad Air/Pro | 820px |
| iPad Pro 12.9" | 1024px |
| Desktop | 1280px+ |

**Prototype breakpoints:**

| Name | Width | Tailwind |
|------|-------|----------|
| mobile | 375px | default |
| mobile-lg | 430px | -- |
| tablet | 768px | `md:` |
| tablet-lg | 1024px | `lg:` |
| desktop | 1280px | `xl:` |

## 6. Competitors -- What to Take

| Competitor | URL | Good | Bad |
|-----------|-----|------|-----|
| touristino.com | touristino.com | Clean design, whitespace, single accent color | No hero photo, no WhatsApp CTA |
| dubaitours.ru | dubaitours.ru | Fullscreen hero photos, poetic subtitles, "since 1994" | No prices on cards, no filters |
| imperiyaturizma24.com | imperiyaturizma24.com | 6-parameter filtering, icon categories | Basic visuals, stock photos |
| getyourguide.com | getyourguide.com | UX discipline: info density + minimalism, 69K reviews | Cold corporate, no warmth |
| bigbustours.com | bigbustours.com | Price near CTA, TripAdvisor integration | 14+ CTAs per page, utilitarian |
| platinumlist.net | platinumlist.net | Powerful categorization, AI search | Overloaded (12+ sections), cold |

## 7. Reference Sites -- Inspiration

| Site | Segment | Pattern We Took |
|------|---------|----------------|
| aman.com | Luxury hospitality | Letter-spacing 4px on uppercase headings |
| aesop.com | Luxury skincare | Whitespace as design element, font-weight 400 |
| apple.com | Tech luxury | Light/dark section alternation, storytelling |
| oneandonlyresorts.com | Luxury hospitality | Outline CTA 0.8px border, editorial flow |
| bang-olufsen.com | Premium audio | Single accent color for CTA, stagger animation |
| rolls-roycemotorcars.com | Ultra-luxury | Poetic copywriting, letter-spacing 15px hero |
| diptyqueparis.com | Luxury perfume | Ghost buttons, spacing system from CSS vars |
| fourseasons.com | Luxury hospitality | Sticky mobile CTA, progressive disclosure |

## 8. CSS Template

Copy this block into any prototype HTML file:

```css
/* === RESET === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
img { max-width: 100%; display: block; }
a { text-decoration: none; color: inherit; }
button { border: none; background: none; cursor: pointer; font: inherit; }

/* === CSS VARIABLES === */
:root {
  /* Brand Colors */
  --color-copper: #C4896E;
  --color-copper-hover: #B07A5F;
  --color-copper-light: #D49D85;
  --color-sand: #DEB7A4;
  --color-peach: #E7C6B4;

  /* Backgrounds */
  --color-bg-primary: #FDFBF9;
  --color-bg-secondary: #F5EDE7;
  --color-bg-card: #FAF6F2;
  --color-bg-dark: #1A1714;
  --color-bg-dark-secondary: #2A2520;

  /* Text */
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #6B6156;
  --color-text-tertiary: #9A8D80;
  --color-text-on-dark: #F5F0EB;
  --color-text-on-dark-secondary: #A09080;

  /* Borders */
  --color-border: #E8DDD3;
  --color-border-light: #F0E8E0;

  /* Semantic */
  --color-whatsapp: #25D366;
  --color-whatsapp-hover: #1EBE5A;
  --color-rating: #D69E2E;
  --color-price-old: #9A8D80;
  --color-error: #C53030;
  --color-success: #2F855A;

  /* Spacing (base 4px) */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;
  --space-4: 16px;  --space-5: 20px;  --space-6: 24px;
  --space-8: 32px;  --space-10: 40px; --space-12: 48px;
  --space-16: 64px; --space-20: 80px; --space-24: 96px;
  --space-28: 112px;

  /* Layout */
  --container-default: 1200px;
  --container-wide: 1440px;
  --container-narrow: 680px;
  --section-gap: 112px;
  --card-gap: 24px;
  --card-padding: 20px;

  /* Z-Index */
  --z-base: 1;
  --z-dropdown: 10;
  --z-sticky: 50;
  --z-nav: 100;
  --z-menu-overlay: 200;
  --z-modal: 300;
  --z-whatsapp: 1000;

  /* Shadows */
  --shadow-nav: 0 1px 0 rgba(0,0,0,0.05);
  --shadow-dropdown: 0 4px 20px rgba(0,0,0,0.08);
  --shadow-sticky: 0 -2px 10px rgba(0,0,0,0.1);

  /* Transitions */
  --ease-out: cubic-bezier(0.165, 0.84, 0.44, 1);
  --duration-fast: 200ms;
  --duration-base: 300ms;
  --duration-slow: 600ms;
}

/* === FONTS === */
body {
  font-family: 'Montserrat', sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.6;
  letter-spacing: 0.3px;
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
}

/* === TYPOGRAPHY === */
h1, h2 {
  font-family: 'Tenor Sans', serif;
  font-weight: 400;
  text-transform: uppercase;
  line-height: 1.1;
}
h1 { font-size: clamp(42px, 6vw + 1rem, 68px); letter-spacing: 6px; }
h2 { font-size: clamp(24px, 3vw + 0.5rem, 32px); letter-spacing: 4px; line-height: 1.2; }
h3 { font-family: 'Tenor Sans', serif; font-weight: 400; font-size: clamp(18px, 2vw + 0.25rem, 22px); letter-spacing: 2px; line-height: 1.3; }
.eyebrow { font-family: 'Cormorant SC', serif; font-size: 14px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--color-copper); }
.body-lg { font-size: 18px; font-weight: 300; }
.body-sm { font-size: 14px; font-weight: 300; }
.caption { font-size: 12px; font-weight: 300; letter-spacing: 0.5px; }
.label { font-size: 12px; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; }
.price { font-size: 18px; font-weight: 300; letter-spacing: 0.5px; }
.price-old { font-size: 14px; font-weight: 300; color: var(--color-price-old); text-decoration: line-through; }

/* === BUTTONS === */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);
  font-family: 'Montserrat', sans-serif; font-size: 15px; font-weight: 500;
  letter-spacing: 1.5px; text-transform: uppercase;
  padding: 14px 32px; border-radius: 0;
  transition: all var(--duration-base) var(--ease-out);
  cursor: pointer;
}
.btn-primary { background: var(--color-copper); color: #fff; border: none; }
.btn-primary:hover { background: var(--color-copper-hover); }
.btn-ghost { background: transparent; color: var(--color-copper); border: 0.8px solid var(--color-copper); }
.btn-ghost:hover { background: var(--color-copper); color: #fff; }
.btn-whatsapp { background: var(--color-whatsapp); color: #fff; border: none; }
.btn-whatsapp:hover { background: var(--color-whatsapp-hover); }

/* === CARD === */
.card {
  background: var(--color-bg-card);
  border: 0.8px solid var(--color-border);
  border-radius: 0;
  overflow: hidden;
  display: flex; flex-direction: column;
}
.card img { aspect-ratio: 3/2; object-fit: cover; width: 100%; transition: transform var(--duration-slow) var(--ease-out); }
.card:hover img { transform: scale(1.03); }
.card-body { padding: var(--card-padding); flex: 1; display: flex; flex-direction: column; }

/* === CONTAINER === */
.container { max-width: var(--container-default); margin: 0 auto; padding: 0 var(--space-6); }

/* === SECTION === */
.section { padding: var(--space-20) 0; }
@media (min-width: 768px) { .section { padding: var(--space-24) 0; } }
@media (min-width: 1024px) { .section { padding: var(--space-28) 0; } }

/* === DARK THEME === */
[data-theme="dark"] { background: var(--color-bg-dark); color: var(--color-text-on-dark); }
[data-theme="dark"] .eyebrow { color: var(--color-copper-light); }
[data-theme="dark"] .btn-ghost { color: var(--color-text-on-dark); border-color: var(--color-text-on-dark); }

/* === GRID === */
.grid-cards { display: grid; gap: var(--card-gap); grid-template-columns: 1fr; }
@media (min-width: 768px) { .grid-cards { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .grid-cards { grid-template-columns: repeat(3, 1fr); } }

/* === REDUCED MOTION === */
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }
```
