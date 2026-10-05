# CSS to Figma Plugin API Property Mapping

> Complete mapping table for converting HTML/CSS carousel designs to Figma Plugin API calls.
> Derived from analysis of 32+ elements across 5 palette etalons.

---

## Layout & Positioning

| CSS | Figma Plugin API | Notes |
|-----|-----------------|-------|
| `position: absolute` | `node.layoutPositioning = "ABSOLUTE"` or parent `layoutMode = "NONE"` | |
| `inset: 0` | `x=0, y=0, resize(parentW, parentH)` | |
| `bottom: 60px` | `y = parentH - 60 - nodeH` | Must calculate manually |
| `display: flex; flex-direction: column` | `layoutMode = "VERTICAL"` | |
| `display: flex; flex-direction: row` | `layoutMode = "HORIZONTAL"` | |
| `align-items: center` | `counterAxisAlignItems = "CENTER"` | |
| `justify-content: space-between` | `primaryAxisAlignItems = "SPACE_BETWEEN"` | |
| `gap: 12px` | `itemSpacing = 12` | Only with auto-layout |
| `padding: 54px 60px` | `paddingTop=54, paddingBottom=54, paddingLeft=60, paddingRight=60` | |
| `overflow: hidden` | `clipsContent = true` | |
| `z-index` | Child order in `frame.children` | Later child = higher z |
| `width: 100%` (in flex) | `layoutSizingHorizontal = "FILL"` | Parent must have layoutMode |
| `flex: 1` | `layoutGrow = 1` | Parent must be FIXED size |

## Colors & Fills

| CSS | Figma Plugin API | Notes |
|-----|-----------------|-------|
| `background: #C4896E` | `fills = [{type: "SOLID", color: {r: 0.769, g: 0.537, b: 0.431}}]` | RGB 0-1 range |
| `color: rgba(255,255,255,0.85)` | `fills = [{type: "SOLID", color: {r:1,g:1,b:1}}]; opacity = 0.85` | Alpha as separate opacity |
| `opacity: 0.04` | `node.opacity = 0.04` | |
| `mix-blend-mode: color` | `blendMode = "COLOR"` | |
| `mix-blend-mode: overlay` | `blendMode = "OVERLAY"` | Used for grain layer |
| `linear-gradient(180deg, ...)` | `type: "GRADIENT_LINEAR", gradientTransform: [[0,1,0],[-1,0,1]]` | Top-to-bottom |
| `linear-gradient(135deg, ...)` | `gradientTransform: [[0.707,0.707,-0.207],[-0.707,0.707,0.5]]` | cos/sin of angle |
| `linear-gradient(168deg, ...)` | `gradientTransform: [[cos,sin,tx],[-sin,cos,ty]]` | Calculate per angle |
| `radial-gradient(ellipse 80% 70% at 50% 45%)` | `type: "GRADIENT_RADIAL", gradientTransform: [[0.8,0,0.1],[0,0.7,0.15]]` | Scale + offset |
| Gradient stop `rgba(r,g,b,a)` | `{position: N, color: {r, g, b, a}}` | Alpha IN color for gradients |
| Solid fill `rgba(r,g,b,a)` | `color: {r,g,b}` + `opacity: a` | Alpha SEPARATE for solids |

## Effects

| CSS | Figma Plugin API | Notes |
|-----|-----------------|-------|
| `backdrop-filter: blur(20px)` | `effects: [{type: "BACKGROUND_BLUR", radius: 10}]` | **radius = CSS / 2** |
| `backdrop-filter: saturate(1.6)` | No equivalent | Figma cannot saturate backdrop |
| `filter: blur(10px)` | `effects: [{type: "LAYER_BLUR", radius: 5}]` | **radius = CSS / 2** |
| `text-shadow: 0 1px 2px rgba(0,0,0,0.2)` | `effects: [{type: "DROP_SHADOW", offset:{x:0,y:1}, radius:2, color:{r:0,g:0,b:0,a:0.2}, spread:0, visible:true, blendMode:"NORMAL"}]` | |
| `box-shadow: 0 4px 24px rgba(...)` | Same as DROP_SHADOW | Multiple = array of effects |
| `box-shadow: inset 0 1px 0 rgba(255,255,255,0.08)` | Separate child rect with `INNER_SHADOW` | Cannot coexist with BACKGROUND_BLUR on same node |
| `filter: brightness(...) contrast(...) saturate(...) hue-rotate(...)` | No Figma equivalent | Apply to photo BEFORE importing |

## Typography

| CSS | Figma Plugin API | Notes |
|-----|-----------------|-------|
| `font-family: 'Tenor Sans'` | `fontName = {family: "Tenor Sans", style: "Regular"}` | Must `loadFontAsync` first |
| `font-family: 'Montserrat'` | `fontName = {family: "Montserrat", style: "Medium"}` | weight 500 = "Medium" |
| `font-family: 'Cormorant SC'` | `fontName = {family: "Cormorant SC", style: "Regular"}` | Small caps font |
| `font-size: 84px` | `fontSize = 84` | |
| `font-weight: 500` | Style name in fontName: `"Medium"` | 400="Regular", 700="Bold" |
| `line-height: 1.08` | `lineHeight = {value: fontSize*1.08, unit: "PIXELS"}` | Calculate: 84*1.08=90.72 |
| `line-height: 36px` | `lineHeight = {value: 36, unit: "PIXELS"}` | |
| `letter-spacing: 6px` | `letterSpacing = {value: 6, unit: "PIXELS"}` | |
| `text-transform: uppercase` | `textCase = "UPPER"` | |
| `text-align: center` | `textAlignHorizontal = "CENTER"` | |
| `font-variant: small-caps` | Use "Cormorant SC" font family | Small caps is the font itself |
| `textAutoResize: "HEIGHT"` | Fixed width, auto height | For body/description text |
| `textAutoResize: "WIDTH_AND_HEIGHT"` | Auto both | For headings, then center manually |

## Borders & Strokes

| CSS | Figma Plugin API | Notes |
|-----|-----------------|-------|
| `border: 1px solid rgba(255,255,255,0.18)` | `strokes=[{type:"SOLID", color:{r:1,g:1,b:1}, opacity:0.18}]; strokeWeight=1; strokeAlign="INSIDE"` | opacity on paint object |
| `border: 1px solid rgba(31,41,50,0.08)` | `strokes=[{type:"SOLID", color:{r:0.122,g:0.161,b:0.196}, opacity:0.08}]` | Dark border (mist-blue) |
| `border-radius: 24px` | `cornerRadius = 24` | |
| `border-radius: 999px` | `cornerRadius = 999` | Full pill shape |
| `border-radius: 42px` | `cornerRadius = 42` | Inner decorative border |

## MCP Runtime Limitations

| API | Status | Workaround |
|-----|--------|-----------|
| `figma.createImageAsync(url)` | BLOCKED | User drag-drop photos manually |
| `fetch(url)` | BLOCKED | Cannot download anything |
| `XMLHttpRequest` | BLOCKED | Cannot download anything |
| `figma.createImage(bytes)` | Works but 50KB code limit | Only for tiny images (<30KB) |
| `figma.setCurrentPageAsync(page)` | Works | Heavy pages may timeout |
| `figma.currentPage = page` (sync) | BLOCKED | Use setCurrentPageAsync |
| `figma.notify()` | BLOCKED | Return string instead |
| `getPluginData/setPluginData` | BLOCKED | Use getSharedPluginData |
