# Batch Carousel Production in Figma

How to produce multiple carousels efficiently using worktree agents and the Plugin API.

## Pipeline Overview

1. **Plan** — Read `docs/plans/product-photo-posts.md` for slide plans
2. **Find photos** — Search `D:/Downloads/Каталог турпродуктов ОАЭ/` (verify folders are non-empty)
3. **Launch agents** — 1 agent per carousel in isolated worktree
4. **Each agent:** finds photos > copies to `photos/{topic}/` > creates cinema.css + slides + preview + blueprint > commits > creates PR
5. **Merge** — Sequential merge of PRs into main (check cinema.css conflicts)
6. **Preview** — Start dev server, open preview.html, get user approval BEFORE finalizing
7. **Fix** — Apply corrections (photos, CTA text, preview links)

## Script Template Pattern

Use an existing Figma script as template for new carousels:

```
docs/figma-scripts/content_slides_3_7.js   — content slides example
docs/figma-scripts/{carousel}_figma.js      — per-carousel script
docs/figma-blueprints/{carousel}.md         — per-carousel content plan
```

Each script follows the pattern:
1. Set page: `await figma.setCurrentPageAsync(...)`
2. Load fonts: `await Promise.all([figma.loadFontAsync(...), ...])`
3. Create root frame: `figma.createFrame()`, resize 1080x1350
4. Add layers bottom-to-top: background > overlays > content > footer
5. Return created IDs: `return { createdNodeIds: [...] }`

## Page Organization

| Page | Content | Notes |
|------|---------|-------|
| "Посты Инстаграм Финал" | All carousel slides (48+ frames) | Main working page |
| "фото постов инстаграм финал" | Uploaded photos | Separate to avoid timeout |
| "Page 1" | Original story designs | READ ONLY |

### Slide Layout Rules
- Each carousel = one horizontal row
- Slides left-to-right: Cover > Content 1-N > CTA
- Gap between slides: 80px
- Gap between rows: 200px
- Row label: copper-colored Inter Medium text above the row

### Naming Convention
`PALETTE . carousel_name . Slide Type` (e.g., "COPPER . la_perle_v1 . Cover")

## Photo Pipeline

1. Find photos in `D:/Downloads/Каталог турпродуктов ОАЭ/{category}/{product}/фото/`
2. Copy to `photos/{topic}/`, rename to snake_case (`01_cover.jpg`, `02_interior.jpg`)
3. Run Night Cinema: `python scripts/apply_night_cinema.py`
4. Output in `photos/{topic}_nc/` — ready for Figma import
5. Upload via bridge or create placeholder rects for manual fill

## QA Checklist

Before marking a batch complete:

- [ ] Each slide has correct palette colors (check against etalon)
- [ ] Blur values are CSS / 2 (not raw CSS values)
- [ ] Vignette uses 5 gradient stops (not 2)
- [ ] Each photo is unique across slides (no duplicates)
- [ ] Pills have 3-child glassmorphism structure
- [ ] CTA slide follows La Perle slide_7 template
- [ ] Footer has correct handle (@vip_dxb_rus) and tagline
- [ ] Text is readable on exported PNG (not just in Figma preview)
- [ ] No product prices shown on slides we sell (utility topics exempt)
- [ ] Figma output matches browser rendering of HTML templates

## Key Lessons

- 2 agents per carousel for large ones (split by slides), 1 for smaller
- Always show preview to user before merging PRs — Figma changes are hard to undo
- `cinema.css` is identical across all carousels — git handles duplicate file merges
- CTA slides need descriptive pill text, not generic "Learn More"
- Save extracted Figma data (node IDs, image hashes) to `docs/figma-data/` immediately
