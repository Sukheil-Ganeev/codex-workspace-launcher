# Palette Registry — Multi-Palette Color System for Figma Production

> Copy-paste ready PALETTES object and createRoot() function for use_figma scripts.
> All colors in Figma 0-1 range. 5 palettes: copper, mist-blue, warm-clay, warm-gray, sand.

---

## Common Constants (Shared Across All Palettes)

```javascript
const COMMON = {
  white:      { r: 0.996, g: 0.988, b: 0.980 },  // #FEFCFA
  ink:        { r: 0.102, g: 0.090, b: 0.078 },  // #1A1714
  cream:      { r: 0.961, g: 0.929, b: 0.906 },  // #F5EDE7
  copperDark: { r: 0.627, g: 0.416, b: 0.314 },  // #a06a50
  canvas:     { w: 1080, h: 1350 },
  border:     { inset: 24, radius: 42 },
};
```

---

## PALETTES Object (Copy-Paste Ready)

```javascript
const PALETTES = {

  // ─────────────────────────────────────────────
  // COPPER (#C4896E) — Primary brand palette
  // ─────────────────────────────────────────────
  copper: {
    name: 'copper',
    base:    { r: 0.769, g: 0.537, b: 0.431 },  // #C4896E
    deep:    { r: 0.627, g: 0.416, b: 0.314 },  // #a06a50
    theme:   { r: 0.769, g: 0.537, b: 0.431 },  // same as base

    // Background gradient layers (bottom to top)
    gradient: [
      { type: 'SOLID', color: { r: 0.769, g: 0.537, b: 0.431 }, opacity: 1.0 },
      { type: 'GRADIENT_LINEAR', angle: 180, stops: [
        { color: { ...COMMON.white, a: 0.04 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.16, y: 0.18 }, stops: [
        { color: { ...COMMON.white, a: 0.08 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
    ],

    grid:    { size: 56, opacity: 0.20 },
    padding: 56,

    card: {
      bg:      { ...COMMON.white, a: 0.93 },
      border:  { ...COMMON.white, a: 0.24 },
      text:    { ...COMMON.ink,   a: 0.90 },
      soft:    { ...COMMON.ink,   a: 0.68 },
    },

    panel: {
      bg:      { ...COMMON.white, a: 0.14 },
    },

    // Text on background — WHITE (light text on mid-tone bg)
    textOnBg: { r: 0.996, g: 0.988, b: 0.980 },  // white
  },

  // ─────────────────────────────────────────────
  // MIST-BLUE (#C7D8E6) — Transport, water themes
  // UNIQUE: dark text on background!
  // ─────────────────────────────────────────────
  'mist-blue': {
    name: 'mist-blue',
    base:    { r: 0.780, g: 0.847, b: 0.902 },  // #C7D8E6
    deep:    { r: 0.780, g: 0.847, b: 0.902 },  // same as base (solid, no gradient)
    theme:   { r: 0.780, g: 0.847, b: 0.902 },  // same as base

    gradient: [
      { type: 'SOLID', color: { r: 0.780, g: 0.847, b: 0.902 }, opacity: 1.0 },
      { type: 'GRADIENT_LINEAR', angle: 180, stops: [
        { color: { ...COMMON.white, a: 0.04 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.12, y: 0.12 }, stops: [
        { color: { ...COMMON.white, a: 0.08 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
    ],

    grid:    { size: 56, opacity: 0.20 },
    padding: 56,

    card: {
      bg:      { ...COMMON.white, a: 0.93 },
      border:  { ...COMMON.white, a: 0.08 },
      text:    { ...COMMON.ink,   a: 0.90 },
      soft:    { ...COMMON.ink,   a: 0.62 },
    },

    panel: {
      bg:      { ...COMMON.white, a: 0.14 },
    },

    // TEXT ON BG IS DARK — unique among all palettes!
    textOnBg: { r: 0.122, g: 0.161, b: 0.196 },  // #1f2932
  },

  // ─────────────────────────────────────────────
  // WARM-CLAY (#C4956A) — Family, parks themes
  // Has 2 radial gradient spots
  // ─────────────────────────────────────────────
  'warm-clay': {
    name: 'warm-clay',
    base:    { r: 0.769, g: 0.584, b: 0.416 },  // #C4956A
    deep:    { r: 0.710, g: 0.541, b: 0.353 },  // #b58a5a
    theme:   { r: 0.769, g: 0.584, b: 0.416 },  // same as base

    gradient: [
      { type: 'SOLID', color: { r: 0.769, g: 0.584, b: 0.416 }, opacity: 1.0 },
      { type: 'GRADIENT_LINEAR', angle: 180, stops: [
        { color: { ...COMMON.white, a: 0.035 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00  }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.88, y: 0.04 }, stops: [
        { color: { ...COMMON.white, a: 0.07 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.14, y: 0.18 }, stops: [
        { color: { ...COMMON.white, a: 0.09 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
    ],

    grid:    { size: 64, opacity: 0.18 },
    padding: 64,

    card: {
      bg:      { ...COMMON.cream, a: 0.94 },
      border:  { r: 0.769, g: 0.584, b: 0.416, a: 0.10 },  // warmClay 0.10
      text:    { ...COMMON.ink,   a: 0.92 },
      soft:    { ...COMMON.ink,   a: 0.66 },
    },

    panel: {
      bg:      { ...COMMON.cream, a: 0.17 },  // 0.16-0.18 range
      border:  { ...COMMON.white, a: 0.14 },
    },

    textOnBg: { r: 0.996, g: 0.988, b: 0.980 },  // white
  },

  // ─────────────────────────────────────────────
  // WARM-GRAY (#A89B90) — Neutral utility
  // Has 2 radials + 2 linears (most complex gradient)
  // Panel bg is MUCH more opaque (cream 0.78)
  // ─────────────────────────────────────────────
  'warm-gray': {
    name: 'warm-gray',
    base:    { r: 0.659, g: 0.608, b: 0.565 },  // #A89B90
    deep:    { r: 0.561, g: 0.514, b: 0.471 },  // #8F8378
    theme:   { r: 0.659, g: 0.608, b: 0.565 },  // same as base

    gradient: [
      { type: 'GRADIENT_LINEAR', angle: 168, stops: [
        { color: { r: 0.659, g: 0.608, b: 0.565, a: 1.0 }, position: 0 },  // base
        { color: { r: 0.561, g: 0.514, b: 0.471, a: 1.0 }, position: 1 },  // deep
      ]},
      { type: 'GRADIENT_LINEAR', angle: 180, stops: [
        { color: { ...COMMON.white, a: 0.16 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.86, y: 0.14 }, stops: [
        { color: { ...COMMON.white, a: 0.18 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.12, y: 0.08 }, stops: [
        { color: { ...COMMON.white, a: 0.34 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
    ],

    grid:    { size: 62, opacity: 0.18 },
    padding: 62,

    card: {
      bg:      { ...COMMON.cream, a: 0.94 },
      border:  { r: 0.659, g: 0.608, b: 0.565, a: 0.10 },  // warmGray 0.10
      text:    { ...COMMON.ink,   a: 0.92 },
      soft:    { ...COMMON.ink,   a: 0.68 },
    },

    panel: {
      bg:      { ...COMMON.cream, a: 0.78 },  // MUCH more opaque than others!
    },

    textOnBg: { r: 0.996, g: 0.988, b: 0.980 },  // white
  },

  // ─────────────────────────────────────────────
  // SAND (#C9C0B8 display / #DEB7A4 theme)
  // Same gradient structure as warm-gray
  // Panel bg also cream 0.78
  // ─────────────────────────────────────────────
  sand: {
    name: 'sand',
    base:    { r: 0.788, g: 0.753, b: 0.722 },  // #C9C0B8 (display color)
    deep:    { r: 0.788, g: 0.753, b: 0.722 },  // same as base (solid)
    theme:   { r: 0.871, g: 0.718, b: 0.643 },  // #DEB7A4 (CSS --sand variable)

    gradient: [
      { type: 'GRADIENT_LINEAR', angle: 168, stops: [
        { color: { r: 0.788, g: 0.753, b: 0.722, a: 1.0 }, position: 0 },  // base
        { color: { r: 0.788, g: 0.753, b: 0.722, a: 1.0 }, position: 1 },  // same (solid)
      ]},
      { type: 'GRADIENT_LINEAR', angle: 180, stops: [
        { color: { ...COMMON.white, a: 0.16 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.86, y: 0.14 }, stops: [
        { color: { ...COMMON.white, a: 0.18 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
      { type: 'GRADIENT_RADIAL', center: { x: 0.12, y: 0.08 }, stops: [
        { color: { ...COMMON.white, a: 0.34 }, position: 0 },
        { color: { ...COMMON.white, a: 0.00 }, position: 1 },
      ]},
    ],

    grid:    { size: 62, opacity: 0.18 },
    padding: 62,

    card: {
      bg:      { ...COMMON.cream, a: 0.94 },
      border:  undefined,  // no explicit card border in sand
      text:    { ...COMMON.ink,   a: 0.92 },
      soft:    { ...COMMON.ink,   a: 0.68 },
    },

    panel: {
      bg:      { ...COMMON.cream, a: 0.78 },  // same as warm-gray
    },

    textOnBg: { r: 0.996, g: 0.988, b: 0.980 },  // white
  },

};
```

---

## createRoot() — Palette-Agnostic Root Frame Builder

This function creates the root 1080x1350 frame with the correct background fills for any palette. Copy into your `use_figma` script alongside the PALETTES object above.

```javascript
/**
 * Build the background fills array for a given palette.
 * Returns an array of Figma-compatible fill objects (bottom to top).
 *
 * @param {string} paletteName - One of: 'copper', 'mist-blue', 'warm-clay', 'warm-gray', 'sand'
 * @returns {object[]} Array of fill objects for figma.createRectangle().fills
 */
function buildBackgroundFills(paletteName) {
  const P = PALETTES[paletteName];
  if (!P) throw new Error(`Unknown palette: ${paletteName}`);

  const fills = [];

  for (const layer of P.gradient) {
    if (layer.type === 'SOLID') {
      fills.push({
        type: 'SOLID',
        color: { r: layer.color.r, g: layer.color.g, b: layer.color.b },
        opacity: layer.opacity,
      });
    }
    else if (layer.type === 'GRADIENT_LINEAR') {
      // Convert angle to Figma gradient transform
      // (simplified: angle 180 = top-to-bottom, 168 = slight diagonal)
      const rad = (layer.angle * Math.PI) / 180;
      fills.push({
        type: 'GRADIENT_LINEAR',
        gradientStops: layer.stops.map(s => ({
          color: { r: s.color.r, g: s.color.g, b: s.color.b, a: s.color.a },
          position: s.position,
        })),
        gradientTransform: [
          [Math.cos(rad), Math.sin(rad), 0.5 - 0.5 * Math.cos(rad) - 0.5 * Math.sin(rad)],
          [-Math.sin(rad), Math.cos(rad), 0.5 + 0.5 * Math.sin(rad) - 0.5 * Math.cos(rad)],
        ],
      });
    }
    else if (layer.type === 'GRADIENT_RADIAL') {
      const cx = layer.center.x;
      const cy = layer.center.y;
      fills.push({
        type: 'GRADIENT_RADIAL',
        gradientStops: layer.stops.map(s => ({
          color: { r: s.color.r, g: s.color.g, b: s.color.b, a: s.color.a },
          position: s.position,
        })),
        gradientTransform: [
          [1, 0, cx],
          [0, 1, cy],
        ],
      });
    }
  }

  return fills;
}

/**
 * Create a root frame (1080x1350) with correct palette background.
 * Positions it at (x, y) on the Figma canvas.
 *
 * @param {string} paletteName - Palette key from PALETTES
 * @param {string} frameName   - Name for the frame (e.g., "Slide 1")
 * @param {number} x           - X position on canvas
 * @param {number} y           - Y position on canvas
 * @returns {string} Instructions string for use_figma
 */
function createRoot(paletteName, frameName, x = 0, y = 0) {
  const P = PALETTES[paletteName];
  const fills = buildBackgroundFills(paletteName);

  return `
    // Create root frame
    const root = figma.createFrame();
    root.name = "${frameName}";
    root.resize(1080, 1350);
    root.x = ${x};
    root.y = ${y};
    root.clipsContent = true;
    root.fills = ${JSON.stringify(fills, null, 2)};

    // Inner border (inset 24px, radius 42px)
    const border = figma.createRectangle();
    border.name = "inner-border";
    border.x = 24;
    border.y = 24;
    border.resize(1032, 1302);  // 1080-48, 1350-48
    border.cornerRadius = 42;
    border.fills = [];
    border.strokes = [{
      type: 'SOLID',
      color: { r: ${COMMON.white.r}, g: ${COMMON.white.g}, b: ${COMMON.white.b} },
    }];
    border.strokeWeight = 1.5;
    border.opacity = 0.25;
    root.appendChild(border);
  `;
}
```

---

## Palette Comparison Table

| Property | Copper | Mist-Blue | Warm-Clay | Warm-Gray | Sand |
|----------|--------|-----------|-----------|-----------|------|
| **Base hex** | #C4896E | #C7D8E6 | #C4956A | #A89B90 | #C9C0B8 |
| **Deep hex** | #a06a50 | same as base | #b58a5a | #8F8378 | same as base |
| **Theme hex** | same as base | same as base | same as base | same as base | #DEB7A4 |
| **Gradient layers** | 3 (solid + 1 linear + 1 radial) | 3 (solid + 1 linear + 1 radial) | 4 (solid + 1 linear + 2 radials) | 4 (2 linears + 2 radials) | 4 (2 linears + 2 radials) |
| **Has base-to-deep gradient** | No | No | No | Yes (168deg) | No (solid both ends) |
| **Grid size** | 56px | 56px | 64px | 62px | 62px |
| **Grid opacity** | 0.20 | 0.20 | 0.18 | 0.18 | 0.18 |
| **Padding** | 56 | 56 | 64 | 62 | 62 |
| **Card bg** | white 0.93 | white 0.93 | cream 0.94 | cream 0.94 | cream 0.94 |
| **Card border** | white 0.24 | white 0.08 | warmClay 0.10 | warmGray 0.10 | none |
| **Card text** | ink 0.90 | ink 0.90 | ink 0.92 | ink 0.92 | ink 0.92 |
| **Card soft text** | ink 0.68 | ink 0.62 | ink 0.66 | ink 0.68 | ink 0.68 |
| **Panel bg** | white 0.14 | white 0.14 | cream 0.17 | cream 0.78 | cream 0.78 |
| **Text on bg** | WHITE | DARK (#1f2932) | WHITE | WHITE | WHITE |

---

## Key Differences to Watch

### 1. Mist-Blue Has DARK Text on Background

All other palettes use white text on the colored background. Mist-blue is the **only** palette where heading text, handle text, and taglines on the background must be dark `{r:0.122, g:0.161, b:0.196}` (#1f2932). Forgetting this will make text invisible.

### 2. Card Background: White vs Cream

- **Copper & Mist-Blue**: card bg uses `white` with 0.93 opacity
- **Warm-Clay, Warm-Gray & Sand**: card bg uses `cream` with 0.94 opacity

### 3. Panel Opacity Varies Dramatically

- **Copper & Mist-Blue**: panel bg = white 0.14 (very transparent)
- **Warm-Clay**: panel bg = cream 0.16-0.18 (slightly more opaque)
- **Warm-Gray & Sand**: panel bg = cream 0.78 (nearly solid!)

### 4. Gradient Complexity

- **Copper & Mist-Blue**: Simple (1 solid + 1 linear + 1 radial = 3 layers)
- **Warm-Clay**: Medium (1 solid + 1 linear + 2 radials = 4 layers)
- **Warm-Gray**: Complex (2 linears + 2 radials = 4 layers, includes base-to-deep transition)
- **Sand**: Same structure as warm-gray but both gradient ends are the same color (solid appearance)

### 5. Sand Has Separate Theme Color

Sand is unique: `base` (#C9C0B8) is the actual display background color, but `theme` (#DEB7A4) is the CSS `--sand` variable used for pills and accent elements. Other palettes have `theme === base`.

---

## Usage Examples

### Example 1: Create a Copper Slide

```javascript
// In your use_figma script:
const COMMON = { /* ... copy from above ... */ };
const PALETTES = { /* ... copy from above ... */ };

// Get palette data
const P = PALETTES['copper'];

// Create root frame with background
const root = figma.createFrame();
root.name = "Slide 1 — Copper";
root.resize(1080, 1350);
root.fills = buildBackgroundFills('copper');

// Create a card
const card = figma.createFrame();
card.name = "card";
card.resize(952, 400);  // 1080 - 2*64
card.x = 64;
card.y = 500;
card.cornerRadius = 32;
card.fills = [{
  type: 'SOLID',
  color: { r: P.card.bg.r, g: P.card.bg.g, b: P.card.bg.b },
  opacity: P.card.bg.a,
}];
if (P.card.border) {
  card.strokes = [{
    type: 'SOLID',
    color: { r: P.card.border.r, g: P.card.border.g, b: P.card.border.b },
  }];
  card.strokeWeight = 1;
  card.opacity = P.card.border.a;
}
root.appendChild(card);
```

### Example 2: Palette-Agnostic Text Color

```javascript
function getTextColor(paletteName, role) {
  const P = PALETTES[paletteName];
  switch (role) {
    case 'heading':   return P.textOnBg;       // White or dark depending on palette
    case 'card-body': return P.card.text;       // ink with palette-specific opacity
    case 'card-soft': return P.card.soft;       // ink with lower opacity
    case 'handle':    return P.textOnBg;        // Same as heading
    default:          return P.textOnBg;
  }
}

// Usage:
const color = getTextColor('mist-blue', 'heading');
// Returns { r: 0.122, g: 0.161, b: 0.196 } — dark, not white!
```

### Example 3: Quick Palette Lookup for Sub-Agent

```javascript
// Sub-agent receives paletteName from dispatcher.
// Minimal code to get started:

const paletteName = 'warm-clay';  // from task params
const P = PALETTES[paletteName];

// Background: use P.gradient array
// Card bg:    P.card.bg (color + .a for opacity)
// Card text:  P.card.text (color + .a for opacity)
// Headings:   P.textOnBg
// Grid:       P.grid.size, P.grid.opacity
// Padding:    P.padding
```

---

## Quick Reference: Flat Color Values

For sub-agents that need just the hex values without the full object:

| Palette | Base Hex | Deep Hex | Theme Hex | Text-on-Bg Hex | Card Bg Base | Panel Bg Base |
|---------|----------|----------|-----------|----------------|--------------|---------------|
| copper | #C4896E | #a06a50 | #C4896E | #FEFCFA (white) | #FEFCFA (white) | #FEFCFA (white) |
| mist-blue | #C7D8E6 | #C7D8E6 | #C7D8E6 | #1f2932 (dark) | #FEFCFA (white) | #FEFCFA (white) |
| warm-clay | #C4956A | #b58a5a | #C4956A | #FEFCFA (white) | #F5EDE7 (cream) | #F5EDE7 (cream) |
| warm-gray | #A89B90 | #8F8378 | #A89B90 | #FEFCFA (white) | #F5EDE7 (cream) | #F5EDE7 (cream) |
| sand | #C9C0B8 | #C9C0B8 | #DEB7A4 | #FEFCFA (white) | #F5EDE7 (cream) | #F5EDE7 (cream) |
