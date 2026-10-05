# Figma Plugin API Rules & Gotchas

> Self-contained reference for use_figma calls in InstaCovers production.
> Combines official Figma MCP gotchas with project-specific lessons.

---

## 1. Blur Radius = CSS / 2

CSS `blur(20px)` becomes Figma blur radius **10**. Applies to `BACKGROUND_BLUR`, `LAYER_BLUR`, and all blur effects.

```js
// WRONG -- raw CSS value, blur is 2x too strong
effects: [{ type: "BACKGROUND_BLUR", radius: 20 }]

// CORRECT -- divide CSS blur by 2
effects: [{ type: "BACKGROUND_BLUR", radius: 10 }]
```

## 2. Each use_figma Call = Isolated Context

Page state, variables, and node references do NOT persist between calls. Always set the page first.

```js
// WRONG -- assumes page from previous call
const slide = figma.currentPage.findOne(n => n.name === "MySlide");

// CORRECT -- always set page at start of every call
const page = figma.root.children.find(p => p.name === "Посты Инстаграм Финал");
await figma.setCurrentPageAsync(page);
const slide = figma.currentPage.findOne(n => n.name === "MySlide");
```

## 3. resize() Before textAutoResize

`resize()` resets BOTH sizing modes to FIXED. Call it BEFORE setting auto-resize properties.

```js
// WRONG -- resize after textAutoResize resets it to FIXED
text.textAutoResize = "HEIGHT";
text.resize(960, 100);  // BUG: resets textAutoResize to NONE

// CORRECT -- resize first, then set auto-resize
text.resize(960, 100);
text.textAutoResize = "HEIGHT";
```

Same rule for frames with layoutSizingVertical/Horizontal:

```js
// WRONG -- resize after HUG resets to FIXED
frame.layoutSizingVertical = 'HUG';
frame.resize(300, 1);  // BUG: height locked at 1px

// CORRECT -- resize first, then set sizing
frame.resize(300, 40);
frame.layoutSizingVertical = 'HUG';  // sticks
```

## 4. Absolute Positioning in Figma

For overlay layers (vignette, gradient, grain), use absolute positioning within the parent frame.

```js
// WRONG -- relying on auto-layout for overlay rects
parent.layoutMode = "VERTICAL";
vignette.layoutPositioning = "ABSOLUTE"; // won't work well in auto-layout

// CORRECT -- parent has no auto-layout, children placed manually
parent.layoutMode = "NONE";  // or omit entirely
const vignette = figma.createRectangle();
parent.appendChild(vignette);
vignette.x = 0; vignette.y = 0;
vignette.resize(1080, 1350);
```

## 5. Colors Are 0-1 Range

```js
// WRONG -- CSS 0-255 range
node.fills = [{ type: 'SOLID', color: { r: 196, g: 137, b: 110 } }]

// CORRECT -- Figma 0-1 range (divide by 255)
node.fills = [{ type: 'SOLID', color: { r: 0.769, g: 0.537, b: 0.431 } }]
```

## 6. Solid Fills vs Gradient Fills -- Different Alpha Handling

```js
// SOLID -- alpha via separate opacity property
node.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];
node.opacity = 0.85;

// GRADIENT -- alpha baked into each color stop
gradientStops: [
  { position: 0, color: { r: 0, g: 0, b: 0, a: 0 } },
  { position: 1, color: { r: 0, g: 0, b: 0, a: 0.35 } }
]
```

## 7. Fills/Strokes Are Immutable Arrays

```js
// WRONG -- modifying in place does nothing
node.fills[0].color = { r: 1, g: 0, b: 0 };

// CORRECT -- clone, modify, reassign
const fills = JSON.parse(JSON.stringify(node.fills));
fills[0].color = { r: 1, g: 0, b: 0 };
node.fills = fills;
```

## 8. DROP_SHADOW Requires All Properties

```js
// WRONG -- missing blendMode and spread
effects: [{ type: "DROP_SHADOW", offset: {x:0, y:1}, radius: 2,
  color: {r:0, g:0, b:0, a:0.2} }]

// CORRECT -- include blendMode, spread, visible
effects: [{ type: "DROP_SHADOW", offset: {x:0, y:1}, radius: 2,
  color: {r:0, g:0, b:0, a:0.2}, spread: 0, visible: true, blendMode: "NORMAL" }]
```

## 9. Pill Glassmorphism = 3 Children

Each pill frame needs exactly 3 child nodes to match browser rendering:

```js
// 1. Blur-bg rect (semi-transparent fill + backgroundBlur)
const blurBg = figma.createRectangle();
blurBg.fills = [{ type: 'SOLID', color: {r:0.769,g:0.537,b:0.431}, opacity: 0.18 }];
blurBg.effects = [{ type: 'BACKGROUND_BLUR', radius: 5, visible: true }]; // CSS 10px / 2

// 2. Text node (the label)
const label = figma.createText();

// 3. Inset-shadow rect (INNER_SHADOW effect)
const insetRect = figma.createRectangle();
insetRect.fills = [];
insetRect.effects = [{ type: 'INNER_SHADOW', offset: {x:0, y:1},
  radius: 0, color: {r:1, g:1, b:1, a:0.08}, spread: 0,
  visible: true, blendMode: "NORMAL" }];
```

## 10. Vignette = 5 Gradient Stops

Two stops create a harsh visible edge. Use 5 for smooth falloff:

```js
// WRONG -- harsh 2-stop vignette
gradientStops: [
  { position: 0, color: {r:0,g:0,b:0, a:0} },
  { position: 1, color: {r:0,g:0,b:0, a:0.35} }
]

// CORRECT -- smooth 5-stop vignette
gradientStops: [
  { position: 0,    color: {r:0,g:0,b:0, a:0} },
  { position: 0.5,  color: {r:0,g:0,b:0, a:0} },
  { position: 0.75, color: {r:0,g:0,b:0, a:0.08} },
  { position: 0.9,  color: {r:0,g:0,b:0, a:0.2} },
  { position: 1.0,  color: {r:0,g:0,b:0, a:0.35} }
]
```

## 11. Page Switching -- Async Only

```js
// WRONG -- throws in MCP runtime
figma.currentPage = targetPage;

// CORRECT -- async method
await figma.setCurrentPageAsync(targetPage);
```

## 12. createImageAsync and fetch Are BLOCKED

Cannot upload images in MCP runtime. Create named placeholders instead:

```js
// WRONG -- blocked in MCP
const img = await figma.createImageAsync("https://example.com/photo.jpg");

// CORRECT -- placeholder rect for manual photo fill
const placeholder = figma.createRectangle();
placeholder.name = "PHOTO: 01_cover_nc.png";
placeholder.resize(1080, 1350);
placeholder.fills = [{ type: 'SOLID', color: {r:0.5, g:0.5, b:0.5} }];
```

## 13. Font Loading Is Required Before Text Changes

```js
// WRONG -- setting text without loading font
text.characters = "HELLO";

// CORRECT -- load font first
await figma.loadFontAsync({ family: "Tenor Sans", style: "Regular" });
text.characters = "HELLO";
```

## 14. lineHeight and letterSpacing Must Be Objects

```js
// WRONG -- bare numbers
text.lineHeight = 64.8;
text.letterSpacing = 4;

// CORRECT -- objects with unit
text.lineHeight = { value: 64.8, unit: "PIXELS" };
text.letterSpacing = { value: 4, unit: "PIXELS" };
```

## 15. FILL Requires Auto-Layout Parent FIRST

```js
// WRONG -- FILL before appending to auto-layout parent
const child = figma.createFrame();
child.layoutSizingHorizontal = 'FILL';  // ERROR
parent.appendChild(child);

// CORRECT -- append first, then set FILL
parent.appendChild(child);
child.layoutSizingHorizontal = 'FILL';
```

## 16. Return All Created Node IDs

Every script must return IDs for subsequent calls to reference nodes.

```js
// WRONG -- no return
figma.createRectangle();

// CORRECT -- return structured result
const rect = figma.createRectangle();
return { createdNodeIds: [rect.id], rootNodeId: rect.id };
```

## 17. Never Use figma.notify()

```js
// WRONG -- throws "not implemented"
figma.notify("Done!");

// CORRECT -- return a value
return "Done!";
```

## 18. Stroke Align for Pill Borders

```js
// CORRECT -- inside stroke for consistent pill borders
pill.strokes = [{ type: "SOLID", color: {r:1,g:1,b:1}, opacity: 0.18 }];
pill.strokeWeight = 1;
pill.strokeAlign = "INSIDE";
```

## 19. Description/Body Text -- Fixed Width Pattern

```js
// Standard body text: 960px wide, auto-height, positioned at x=60
const desc = figma.createText();
desc.resize(960, 100);  // set width first
desc.textAutoResize = "HEIGHT";  // then auto-height
desc.x = 60;  // centered in 1080px canvas (60px margin each side)
```

## 20. Heading Text -- Auto-Width, Then Center

```js
await figma.loadFontAsync({ family: "Tenor Sans", style: "Regular" });
heading.textAutoResize = "WIDTH_AND_HEIGHT";
heading.characters = "ЗАГОЛОВОК";
// Center after text is set (width is now measured)
heading.x = (1080 - heading.width) / 2;
```
