# EXP-070: 10 уникальных дизайнов TOC

## Контекст
Проект VIP-DXB: 9 индивидуальных + 1 Combined (208 слайдов) презентация. Каждая получила уникальный TOC-дизайн, тематически связанный с содержанием.

## Общая структура HTML (неизменна)
```html
<div class="toc-backdrop" id="tocBackdrop"></div>
<div class="toc-overlay" id="tocOverlay">
  <div class="toc-header">
    <span class="toc-title">Содержание</span>
    <div class="toc-close" id="tocClose"><!-- X SVG --></div>
  </div>
  <div class="toc-progress-section">...</div>
  <div class="toc-list" id="tocList"><!-- JS builds items --></div>
  <div class="toc-footer"><!-- kbd shortcuts --></div>
</div>
```

## 10 дизайнов

### 1. МАРКЕТИНГ — "Data Dashboard"
- Indicator bars справа от каждого item (::after pseudo, height:3px, gradient)
- Number badges: квадратные (6px radius), monospace
- Header: dot-grid pattern (radial-gradient circles)
- Progress: квадратный trailing dot

### 2. АВТОМАТИЗАЦИЯ — "Circuit Board"
- Vertical dotted line (::before на .toc-list, left:56px, border-left:2px dashed)
- Items — circuit nodes на линии
- Active node: glow circle (16px) с box-shadow
- Header: blueprint grid (linear-gradient grid 20x20px)
- Font: monospace (Consolas/Monaco)

### 3. FORM_TICKETS — "Form Wizard"
- Items стилизованы как input fields (border:1px solid, border-radius:10px)
- Active = "focused" input (accent border + box-shadow focus ring)
- Margin между items (4px) — стопка полей формы
- Progress: pill (border-radius:10px), height:6px

### 4. BANT — "Sales Pipeline"
- Gradient intensity увеличивается к active (funnel metaphor)
- Number badges: rounded-square (8px) pipeline markers
- Header: serif accent (Georgia) + "PIPELINE" watermark
- Progress: 6px thick, gradient rose→purple

### 5. НАПОМИНАНИЯ — "Timeline / Notification Center"
- Vertical timeline line (::before, left:63px)
- Node dots на линии, active — larger с glow halo
- Items: notification cards (rounded right: 0 12px 12px 0)
- Close: circular button (border-radius:50%)
- Search: pill shape (20px)

### 6. FAQ — "Chat / Q&A Bubbles"
- Items как chat bubbles (border-radius:16px 16px 16px 4px)
- Alternating: even items reversed tail (16px 16px 4px 16px)
- Active bubble: glow dot (8px) at tail corner
- Compact padding (9px 20px), 3px gaps

### 7. B2B — "Executive Briefing"
- Ultra-minimal, high-contrast
- Thin horizontal dividers (border-bottom)
- Number: serif font (Georgia), weight:200
- Active: sharp 2px left border, NO glow
- Header: uppercase, letter-spacing:2px, weight:300
- All corners: 0-2px (sharp corporate)

### 8. КВИЗ — "Game Progress / Level Select"
- Large number circles (42px), border:2px, weight:900
- Active: gradient with triple ring shadow
- CSS triangle "current level" arrow (left)
- XP progress bar: 10px height, gradient, "XP" label
- "LEVEL SELECT" header

### 9. КОНТРОЛЬ — "QA Audit Checklist"
- Number badges: rectangular tags (border-radius:3px), monospace
- Active: checkmark (✓) справа, teal left border
- Progress: 6px, solid border, percentage
- "QA AUDIT" header tag с рамкой
- Left-border:3px on all items (checklist indent)

### 10. COMBINED — "Command Center"
- Master design, gold theme (#D4A017)
- Search input: glass card, gold-tinted, focus triple-ring
- Compact items (7px padding) for 208 slides
- Squared number badges (8px, not 50%)
- "MASTER" watermark in header
- Gold scrollbar thumb

## Ключевые принципы
1. Тема TOC должна отражать содержание презентации
2. Уникальность через: shape(badge), connector(line/dots/none), accent(glow/border/color), font(serif/mono/sans), spacing
3. HTML structure неизменна — уникальность только через CSS
4. Pseudo-elements: ::before для accent lines и neon bars, ::after для glow и indicator bars

## Тэги
#pattern #toc #design #unique #glassmorphism #css
