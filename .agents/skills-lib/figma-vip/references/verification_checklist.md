# Post-Creation Verification Checklist

Run this checklist AFTER creating each slide. Every item must pass.

## Automated Checks (include in validate() at end of every script)

```javascript
// STANDARD VALIDATE — copy into every use_figma script
const issues = [];
function validate(root) {
  function check(n, depth) {
    // 1. h=100 trap (L-06)
    if (n.type === "FRAME" && n.height === 100 && n.layoutMode !== "NONE" && !n.name.startsWith("sp")) {
      issues.push({ node: n.name, issue: "h=100 stuck", fix: "resize + HUG" });
      n.resize(n.width, 10); n.layoutSizingVertical = "HUG";
    }
    // 2. w=100 + clip trap (L-06)
    if (n.type === "FRAME" && n.width === 100 && n.clipsContent && n.layoutSizingHorizontal === "FIXED") {
      issues.push({ node: n.name, issue: "w=100+clip" });
    }
    // 3. Text overflow (L-22) — text wider than parent
    if (n.type === "TEXT" && n.parent && n.parent.type === "FRAME" && n.parent.layoutMode !== "NONE") {
      const parentInner = n.parent.width - (n.parent.paddingLeft || 0) - (n.parent.paddingRight || 0);
      if (n.width > parentInner + 5) {
        issues.push({ node: n.name, issue: "text overflow", textW: Math.round(n.width), parentInner: Math.round(parentInner) });
      }
    }
    // 4. Placeholder icons still present
    if (n.type === "RECTANGLE" && (n.name.includes("placeholder") || (n.cornerRadius === 9 && n.width === 18 && n.height === 18))) {
      issues.push({ node: n.name, issue: "placeholder icon not replaced" });
    }
    if ("children" in n) n.children.forEach(c => check(c, depth + 1));
  }
  check(root, 0);
  return issues;
}
```

## Manual Checks (after get_screenshot)

- [ ] **All text readable** — no clipping, no overflow beyond frame
- [ ] **All icons are SVG** — no gray circles or rectangles as icons
- [ ] **Footer at bottom** — footer-banner pinned to bottom of slide
- [ ] **Meta bar** — "NN / 08" left, "@vip_dxb_rus" right
- [ ] **Chip** — has icon + uppercase text with letter-spacing
- [ ] **Watermark** — bottom-right, barely visible (opacity 0.045)
- [ ] **Inner border** — thin white border 24px inset, 42px radius
- [ ] **Card titles bold** — ExtraBold weight (not Regular or Medium)
- [ ] **Card text lighter** — opacity 0.66 (not 1.0)
- [ ] **Stat-card fits** — value and text don't overflow panel

## Width Verification Script

Run this after ALL slides are created to catch width errors:

```javascript
// Paste into use_figma to audit all text widths
const CORRECT_WIDTHS = {
  "page__title": 520,
  "page__subtitle": 520,
  "content-page__title": 560,
  "content-page__subtitle": 560,
  "pass-panel__value": 340,
  "pass-panel__copy": 340,
  "stat-card__value": 320,
  "stat-card__text": 320,
  "footer-banner__text": 718,
  "footer-banner__title": 170,
  "footer-note__text": 328,
  "cta-text": 620,
  "service": 720
};
// For split layouts, subtitle = 520 (not 560)
// For place-card text: FILL (auto from parent)
// For tip-card text: FILL (auto from parent)
```

## Slide Type Templates

Before creating a slide, confirm which template it follows:

| Type | Components | SVG count |
|------|-----------|-----------|
| cover | meta + chip + cover-grid(title+panel) + note-card + footer(save-chip+footer-note) | 4 (star, clock, arrow, bookmark) |
| content | meta + chip + title + subtitle + place-cards + footer-banner | 1(chip) + N(cards) |
| content-split | meta + chip + hero(title+stat-card) + place-cards + footer-banner | 1(chip) + N(cards) |
| tips | meta + chip + title + subtitle + tip-grid(2-col) + footer-banner | 1(chip) + N(tips) |
| cta | meta + cta-shell(badge+eyebrow+title+text+action-pills+service) | 1(badge) + N(pills) |
