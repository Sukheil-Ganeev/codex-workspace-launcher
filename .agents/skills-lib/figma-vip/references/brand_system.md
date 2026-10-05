# VIP-DXB-RUS Brand System for Figma

> Complete brand reference with Figma-ready values.
> Canvas: 1080x1350px (Instagram 4:5). All colors in both CSS hex and Figma 0-1 range.

---

## Colors

### Brand Palette (CSS Hex + Figma RGB 0-1)

| Variable | Hex | Figma {r, g, b} | Usage |
|----------|-----|-----------------|-------|
| `--copper` | #C4896E | `{r:0.769, g:0.537, b:0.431}` | Primary brand |
| `--copper-light` | #d4a088 | `{r:0.831, g:0.627, b:0.533}` | Hover, accents |
| `--copper-dark` | #a06a50 | `{r:0.627, g:0.416, b:0.314}` | Active, emphasis |
| `--sand` | #DEB7A4 | `{r:0.871, g:0.718, b:0.643}` | Backgrounds, pills |
| `--peach` | #E7C6B4 | `{r:0.906, g:0.776, b:0.706}` | Soft tones |
| `--warm-clay` | #C4956A | `{r:0.769, g:0.584, b:0.416}` | Family, parks |
| `--mist-blue` | #C7D8E6 | `{r:0.780, g:0.847, b:0.902}` | Transport, water |
| `--warm-gray` | #A89B90 | `{r:0.659, g:0.608, b:0.565}` | Neutral utility |
| `--cream` | #F5EDE7 | `{r:0.961, g:0.929, b:0.906}` | Premium light blocks |
| `--black` | #1A1714 | `{r:0.102, g:0.090, b:0.078}` | Dark backgrounds |
| `--white` | #FEFCFA | `{r:0.996, g:0.988, b:0.980}` | Text on dark |

### Additional Colors Used in Etalons

| Color | Hex | Figma {r, g, b} | Where |
|-------|-----|-----------------|-------|
| Dark text | #1f2932 | `{r:0.122, g:0.161, b:0.196}` | Mist-blue palette text |
| Dark text alt | #2e2825 | `{r:0.180, g:0.157, b:0.145}` | Sand/warm-gray card text |
| Warm-clay dark | #A87D54 | `{r:0.659, g:0.490, b:0.329}` | Warm-clay gradient end |
| Warm-gray dark | #8F8378 | `{r:0.561, g:0.514, b:0.471}` | Warm-gray gradient end |
| Sand base | #C9C0B8 | `{r:0.788, g:0.753, b:0.722}` | Sand solid background |

---

## Typography

### Font Loading (loadFontAsync calls)

```js
// Headings
await figma.loadFontAsync({ family: "Tenor Sans", style: "Regular" });

// Body, pills, meta
await figma.loadFontAsync({ family: "Montserrat", style: "Medium" });

// Bold pills (sand/warm-gray section chips)
await figma.loadFontAsync({ family: "Montserrat", style: "Bold" });

// Taglines, small caps
await figma.loadFontAsync({ family: "Cormorant SC", style: "Regular" });
```

### Text Roles

| Role | Font | Size | Weight/Style | Extra |
|------|------|------|-------------|-------|
| Heading | Tenor Sans | 82-84px | Regular (400) | `textCase: "UPPER"`, `letterSpacing: {value:6, unit:"PIXELS"}` |
| Body/Description | Montserrat | 20-24px | Medium (500) | `letterSpacing: {value:0.3, unit:"PIXELS"}` |
| Pill label | Montserrat | 14-15px | Medium/Bold | `textCase: "UPPER"`, `letterSpacing: {value:1-2, unit:"PIXELS"}` |
| Tagline | Cormorant SC | 20px | Regular (400) | Small caps via font family |
| Handle | Montserrat | 18-20px | Medium (500) | `letterSpacing: {value:1, unit:"PIXELS"}` |
| Counter | Montserrat | 18px | Medium (500) | `letterSpacing: {value:1, unit:"PIXELS"}` |

### Line Heights (calculated)

| Text | CSS | Figma |
|------|-----|-------|
| Heading 84px, lh 1.08 | `line-height: 1.08` | `lineHeight: {value: 90.72, unit: "PIXELS"}` |
| Heading 60px, lh 1.08 | `line-height: 1.08` | `lineHeight: {value: 64.8, unit: "PIXELS"}` |
| Body 24px, lh 36px | `line-height: 36px` | `lineHeight: {value: 36, unit: "PIXELS"}` |
| Meta 18px | auto | `lineHeight: {unit: "AUTO"}` |

---

## Standard Gradients

### Vignette (Photo Covers -- 5 Stops)

```js
{
  type: "GRADIENT_RADIAL",
  gradientTransform: [[0.8, 0, 0.1], [0, 0.7, 0.15]],  // ellipse 80%x70% at 50%,45%
  gradientStops: [
    { position: 0,    color: { r:0, g:0, b:0, a: 0 } },
    { position: 0.5,  color: { r:0, g:0, b:0, a: 0 } },
    { position: 0.75, color: { r:0, g:0, b:0, a: 0.08 } },
    { position: 0.9,  color: { r:0, g:0, b:0, a: 0.2 } },
    { position: 1.0,  color: { r:0, g:0, b:0, a: 0.35 } }
  ]
}
```

### Bottom Gradient (Photo Covers -- 5 Stops)

```js
{
  type: "GRADIENT_LINEAR",
  gradientTransform: [[0, 1, 0], [-1, 0, 1]],  // 180deg top-to-bottom
  gradientStops: [
    { position: 0,    color: { r:0, g:0, b:0, a: 0.25 } },
    { position: 0.2,  color: { r:0, g:0, b:0, a: 0 } },
    { position: 0.45, color: { r:0, g:0, b:0, a: 0 } },
    { position: 0.7,  color: { r:0, g:0, b:0, a: 0.4 } },
    { position: 1.0,  color: { r:0, g:0, b:0, a: 0.92 } }
  ]
}
```

### Color Overlay (Night Cinema -- 4 Stops)

```js
{
  type: "GRADIENT_LINEAR",
  gradientTransform: [[0, 1, 0], [-1, 0, 1]],  // 180deg
  blendMode: "COLOR",
  gradientStops: [
    { position: 0,    color: { r: 0, g: 0.314, b: 0.392, a: 0.15 } },      // teal top
    { position: 0.4,  color: { r: 0, g: 0.314, b: 0.392, a: 0 } },         // transparent
    { position: 0.7,  color: { r: 0.769, g: 0.537, b: 0.431, a: 0.12 } },  // copper warm
    { position: 1.0,  color: { r: 0.102, g: 0.090, b: 0.078, a: 0.30 } }   // black bottom
  ]
}
```

### Copper Divider (Horizontal -- 3 Stops)

```js
// 100x1px rectangle
{
  type: "GRADIENT_LINEAR",
  gradientTransform: [[1, 0, 0], [0, 1, 0]],  // left-to-right
  gradientStops: [
    { position: 0,   color: { r: 0.769, g: 0.537, b: 0.431, a: 0 } },
    { position: 0.5, color: { r: 0.769, g: 0.537, b: 0.431, a: 1 } },
    { position: 1,   color: { r: 0.769, g: 0.537, b: 0.431, a: 0 } }
  ]
}
```

---

## Standard Effects

### Text Shadows (Heading -- 4 Layers)

```js
effects: [
  { type: "DROP_SHADOW", offset: {x:0, y:1}, radius: 2,
    color: {r:0, g:0, b:0, a: 0.2}, spread: 0, visible: true, blendMode: "NORMAL" },
  { type: "DROP_SHADOW", offset: {x:0, y:4}, radius: 12,
    color: {r:0, g:0, b:0, a: 0.15}, spread: 0, visible: true, blendMode: "NORMAL" },
  { type: "DROP_SHADOW", offset: {x:0, y:12}, radius: 40,
    color: {r:0, g:0, b:0, a: 0.1}, spread: 0, visible: true, blendMode: "NORMAL" },
  { type: "DROP_SHADOW", offset: {x:0, y:24}, radius: 80,
    color: {r:0, g:0, b:0, a: 0.08}, spread: 0, visible: true, blendMode: "NORMAL" }
]
```

### Text Shadows (Description -- 2 Layers)

```js
effects: [
  { type: "DROP_SHADOW", offset: {x:0, y:1}, radius: 3,
    color: {r:0, g:0, b:0, a: 0.3}, spread: 0, visible: true, blendMode: "NORMAL" },
  { type: "DROP_SHADOW", offset: {x:0, y:4}, radius: 12,
    color: {r:0, g:0, b:0, a: 0.15}, spread: 0, visible: true, blendMode: "NORMAL" }
]
```

### Pill Glassmorphism (3-Child Structure)

Each pill frame contains exactly 3 children:

**Child 1 -- Blur background rect (absolute, fills entire pill):**
```js
fills: [{ type: "GRADIENT_LINEAR",
  gradientTransform: [[0.707, 0.707, -0.207], [-0.707, 0.707, 0.5]],  // 134deg
  gradientStops: [
    { position: 0, color: { r: 0.769, g: 0.537, b: 0.431, a: 0.18 } },
    { position: 1, color: { r: 0.769, g: 0.537, b: 0.431, a: 0.06 } }
  ]
}]
effects: [{ type: "BACKGROUND_BLUR", radius: 5, visible: true }]  // CSS 10px / 2
```

**Child 2 -- Text node:**
```js
fontName: { family: "Montserrat", style: "Medium" }
fontSize: 15
textCase: "UPPER"
letterSpacing: { value: 2, unit: "PIXELS" }
fills: [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }]
opacity: 0.92
```

**Child 3 -- Inset shadow rect (absolute, fills entire pill):**
```js
fills: []  // transparent
effects: [{ type: "INNER_SHADOW", offset: {x:0, y:1}, radius: 0,
  color: {r:1, g:1, b:1, a:0.08}, spread: 0, visible: true, blendMode: "NORMAL" }]
```

**Pill frame itself:**
```js
cornerRadius: 999  // full pill
strokes: [{ type: "SOLID", color: {r:1, g:1, b:1}, opacity: 0.18 }]
strokeWeight: 1
strokeAlign: "INSIDE"
effects: [
  { type: "DROP_SHADOW", offset: {x:0, y:4}, radius: 24,
    color: {r:0, g:0, b:0, a: 0.12}, spread: 0, visible: true, blendMode: "NORMAL" },
  { type: "DROP_SHADOW", offset: {x:0, y:1}, radius: 2,
    color: {r:0, g:0, b:0, a: 0.06}, spread: 0, visible: true, blendMode: "NORMAL" }
]
```

### Grain Layer

```js
// Full-size rectangle (1080x1350), absolute position
const grain = figma.createRectangle();
grain.name = "grain";
grain.resize(1080, 1350);
grain.opacity = 0.04;
grain.blendMode = "OVERLAY";
// Fill: noise texture image hash (must be imported manually)
// Placeholder: solid gray until user fills with noise texture
grain.fills = [{ type: "SOLID", color: {r:0.5, g:0.5, b:0.5} }];
```

---

## Photo Cover Layer Stack (Bottom to Top)

Standard order for Night Cinema photo covers:

1. **photo-layer** -- Rectangle with image fill + exposure/contrast/saturation filters
2. **vignette** -- Rectangle with radial gradient (5 stops)
3. **gradient-overlay** -- Rectangle with linear gradient top-to-bottom (5 stops)
4. **color-overlay** -- Rectangle with linear gradient, blendMode: COLOR (4 stops)
5. **grain** -- Rectangle with noise image, opacity 4%, blendMode: OVERLAY
6. **content-group** -- Frame with heading, description, pills, decorative elements
7. **footer-bar** -- Frame with tagline (Cormorant SC) + handle (Montserrat)
8. **logo** -- Component instance or image
