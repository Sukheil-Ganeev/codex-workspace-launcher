# Figma Production Workflows

Three main workflows for creating Instagram carousel designs in Figma.

---

## A) HTML to Figma — One-Off (html.to.design plugin)

**Best for:** First import of a new carousel, pixel-perfect accuracy, reference layers.

### Steps
1. Create standalone HTML with ALL CSS inlined (no external stylesheets, no local `@font-face`)
2. Open Figma Desktop > Plugins > html.to.design > Editor tab
3. Paste HTML code, set viewport to **1080px**
4. Click Create > Proceed
5. Result: pixel-perfect editable Figma layers with correct hierarchy

### Tips
- 12 free imports/month (resets monthly)
- Produces significantly better results than manual API for complex designs (glass effects, gradients)
- Use the imported layers as reference to analyze exact blur values, gradient stops, shadow params

### Pitfalls
- All CSS MUST be inlined — external files break the import
- Complex CSS filters may not translate perfectly — verify after import
- Cormorant SC must be loaded via Google Fonts `@import`, not local font files

---

## B) HTML to Figma — Batch/Programmatic (use_figma API)

**Best for:** Batch production of multiple carousels from established design system.

### Steps
1. Analyze an html.to.design import to understand the layer structure
2. Write a `use_figma` script using absolute positioning (`layoutMode: "NONE"`)
3. Key pattern: `resize(width, h)` > `textAutoResize = "HEIGHT"` > set `characters`
4. Place elements top-down with Y cursor; footer pinned to bottom (y = 1350 - footerHeight)
5. Run script via `use_figma`, verify with `get_screenshot`
6. Create photo placeholder rects named `"PHOTO: filename.jpg"` (user fills manually)

### Tips
- Use existing scripts as templates (e.g., `docs/figma-scripts/content_slides_3_7.js`)
- One `use_figma` call per slide or group of slides
- Always start with `setCurrentPageAsync` — page state does NOT persist between calls
- Return all created node IDs: `return { createdNodeIds: [root.id] }`

### Pitfalls
- `createImageAsync` and `fetch` are BLOCKED in MCP runtime — use bridge or manual import
- Scripts >50KB are rejected — keep code lean
- Heavy pages (>100MB images) cause timeout — keep photos on separate Figma page
- Each `use_figma` call = separate context — no variable persistence

---

## C) Photo Slides — Night Cinema Processing

**Best for:** Photo-heavy carousels with the VIP cinematic look.

### Steps
1. Collect source photos in `photos/{topic}/`
2. Run Night Cinema correction: `python scripts/apply_night_cinema.py`
3. Corrected files appear in `photos/{topic}_nc/` as `*_nc.png`
4. Upload to Figma via:
   - **Bridge** (`createImageAsync` through figma-console-mcp) — preferred
   - **Manual** drag-drop into Figma, fill placeholder rects
5. In Figma, add overlay layers (NOT baked into photo):
   - Photo layer with image fill
   - Vignette: radial gradient, 5 stops (see gotchas for stop values)
   - Gradient overlay: linear top-to-bottom
   - Color overlay: solid copper/blue at ~0.12 opacity
   - Grain: noise texture, blendMode OVERLAY

### Tips
- Keep photos on a separate Figma page ("фото постов инстаграм финал") to avoid timeout
- Night Cinema CSS filter cannot be applied in Figma — must pre-process (no `hue-rotate`)
- Use 5 gradient stops for vignette, not 2 (2 stops = harsh visible edge)

### Pitfalls
- NEVER copy filter values from V2 carousels — they have wrong values
- Source of truth for filter: `templates/carousel/_boilerplate/cover_template.html`
- Some photo catalog folders are EMPTY — always verify before planning slides

---

## End-to-End Workflow (New Carousel)

1. **Design in HTML** — build slides in `templates/carousel/{topic}/`
2. **Validate in browser** — check at 1080x1350 viewport, export test PNGs
3. **Import cover** — html.to.design for pixel-perfect reference
4. **Analyze layers** — note blur, gradient, shadow params from import
5. **Write Figma script** — create `docs/figma-scripts/{carousel}_figma.js`
6. **Prepare photos** — Night Cinema correction, organize in photos/
7. **Run scripts** — create all slides via `use_figma`
8. **Fill photos** — user drags photos and fills placeholder rects
9. **QA** — compare Figma output against browser rendering, adjust
