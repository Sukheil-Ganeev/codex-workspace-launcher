# Figma API Gotchas

ALL known Figma pitfalls organized by category. Each with Problem, Cause, Fix.

---

## Blur Effects

| Problem | Cause | Fix |
|---------|-------|-----|
| Blur looks weaker/stronger in Figma | CSS blur value used directly | **Divide CSS blur by 2.** CSS `blur(20px)` = Figma `radius: 10`. Applies to `backgroundBlur`, `layerBlur`, all blur effects. |
| Glass effect looks flat | Only using `backgroundBlur` without structure | Use 3-child pill structure: blur-bg rect + text node + inset-shadow rect. |

## Colors & Gradients

| Problem | Cause | Fix |
|---------|-------|-----|
| Gradient colors invisible/wrong | Using `opacity` field for gradient stops | Gradient stops use `{r, g, b, a}` with alpha in color. Solid fills use `{r, g, b}` + separate `opacity`. |
| Colors way off | Using 0-255 range | Figma uses 0-1 range. Divide by 255: `#C4896E` = `{r:0.769, g:0.537, b:0.431}`. |
| Vignette edge visible as harsh line | Only 2 gradient stops | Use **5 stops** for smooth falloff (0, 0.5, 0.75, 0.9, 1.0). |
| Color overlay looks wrong | Wrong blend mode or opacity | Use solid fill at ~0.12 opacity on a separate rect, not mixed into photo. |

## Layout & Positioning

| Problem | Cause | Fix |
|---------|-------|-----|
| `FILL`/`HUG` throws error | Setting layout sizing before `appendChild` | Set `layoutSizingHorizontal = "FILL"` AFTER adding node to auto-layout parent. |
| Wrapper frame stuck at 100px | Default Figma frame = 100x100, `clipsContent = true` | Set sizing AFTER append. Set `clipsContent = false` on wrapper frames. |
| `paddingTop` throws on Text | Text nodes don't have padding | Use wrapper Frame with `paddingTop` instead. Never set padding on Text. |
| Negative margins impossible | Auto-layout doesn't support negative margins | Accept as limitation or use absolute positioning. |
| Elements misaligned | Using auto-layout for pixel-perfect HTML reproduction | Use `layoutMode: "NONE"` with manual `x/y` for pixel-perfect designs. |
| Pill overlaps heading | Insufficient spacing for multi-line titles | Check pill position with longest possible heading: 380px for 3 lines, 320px for 2 lines, 280px for 1 line. |
| Footer not at bottom | Calculating Y wrong | Footer Y = `1350 - footerHeight`. Pin to bottom of 1080x1350 canvas. |

## Text & Fonts

| Problem | Cause | Fix |
|---------|-------|-----|
| Text garbled or zero-width | Setting `characters` before `loadFontAsync` | ALWAYS `await figma.loadFontAsync(...)` BEFORE any text operations. |
| Text overflows frame | Setting `textAutoResize` before `resize()` | Call `resize(width, h)` FIRST, then set `textAutoResize = "HEIGHT"`. |
| Heading not centered | Using fixed X position | Use auto-width, center with `x = (1080 - measuredWidth) / 2` after loading font and setting text. |
| Cormorant SC not loading | Font not available in Figma | Must be loaded via Google Fonts. Check it's installed or available in Figma file. |

## Images

| Problem | Cause | Fix |
|---------|-------|-----|
| Cannot load images | `createImageAsync`/`fetch` blocked in MCP | Use noemuch/bridge (figma-console-mcp) or manual drag-drop with placeholder rects. |
| SVG icons as gray boxes | Used `createRectangle()` as placeholder | Use `figma.createNodeFromSvg(svgString)`. Takes full SVG markup, returns editable FrameNode. Resize + recolor children after. |
| SVG icon wrong color | Default stroke from SVG | After `createNodeFromSvg()`, traverse children: set `strokes = sf(targetColor)` and `fills = []`. |
| createImageAsync domain blocked | `allowedDomains` in plugin manifest | Add domain to manifest. BUT manifest caches on Figma startup — need full app restart AND MCP server regenerates manifest on restart. Workaround: `figma.createImage(uint8Array)` with manual base64 decode. |
| Timeout on use_figma | Too many images on same page | Keep photos on separate Figma page ("фото постов инстаграм финал"). |
| Night Cinema looks wrong | Wrong filter values (e.g., from V2 carousels) | Always use boilerplate values: `brightness(0.95) contrast(1.25) saturate(1.15) hue-rotate(5deg)`. |
| hue-rotate not applied | Figma has no hue-rotate filter | Pre-process with `scripts/apply_night_cinema.py` BEFORE import. |
| Photo repeated across slides | Agent chose same photo twice | Explicitly assign unique photo to each slide in the plan. |

## Pills & Glassmorphism

| Problem | Cause | Fix |
|---------|-------|-----|
| Pills look flat / no glass | Missing child layers | Each pill frame needs exactly 3 children: blur-bg rect (backgroundBlur + semi-transparent fill), text node, inset-shadow rect (INNER_SHADOW at low opacity). |
| Pill border inconsistent | Wrong stroke alignment | Use `strokeAlign: "INSIDE"` for consistent pill borders. |
| Too many pills overload screen | Decorating every card | If block reads fine by heading alone, skip the icon. Less is more. |

## Page Context

| Problem | Cause | Fix |
|---------|-------|-----|
| "Node not found" error | Page resets between `use_figma` calls | ALWAYS call `setCurrentPageAsync` or set `figma.currentPage` at the START of every call. |
| Changes on wrong page | Previous call set page, new call starts fresh | Each call = isolated context. No variable/page persistence. |

## Shadows & Effects

| Problem | Cause | Fix |
|---------|-------|-----|
| DROP_SHADOW not visible | Missing required properties | Always include `blendMode: "NORMAL"`, `spread: 0`, `visible: true`. |
| Heavy glass shadows look dirty | Too strong blur/shadow on solid backgrounds | For solid copper backgrounds, use soft shadows, weak blur, nearly flat background. |

## Fills & Strokes

| Problem | Cause | Fix |
|---------|-------|-----|
| "Cannot assign to read-only property" | Mutating fills/strokes in place | Clone, modify, reassign: `node.fills = [{...newFill}]`. Never mutate existing array. |
| Dune patterns not rendering in PNG | Using `mask-image` CSS property | Use transparent PNG/SVG silhouettes as normal `<img>` layers instead. |
| Patterns invisible on dark background | Opacity too low | For dark backgrounds, pattern opacity should be 0.3+ (not 0.12). |

## Script Execution

| Problem | Cause | Fix |
|---------|-------|-----|
| Script rejected | Code exceeds 50KB | Keep scripts lean. Split into multiple `use_figma` calls if needed. |
| No output visible | Using `console.log` or `figma.notify` | Only `return {...}` produces output. No IIFE wrapper needed — code auto-wrapped. |
| Script silently fails | Missing `return` with created node IDs | Always `return { createdNodeIds: [root.id] }` at minimum. |
