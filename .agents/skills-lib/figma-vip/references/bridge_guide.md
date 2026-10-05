# Bridge Guide — figma-console-mcp + noemuch/bridge

## What It Is

WebSocket bridge from Claude Code to Figma Desktop Plugin API.
Unlike the standard MCP `use_figma` runtime, the bridge runs code inside the actual Figma plugin context — meaning `fetch()` and `createImageAsync()` WORK.

## Key Advantage

| Capability | MCP `use_figma` | Bridge (`figma-console`) |
|------------|-----------------|--------------------------|
| Create/edit nodes | Yes | Yes |
| `fetch()` | BLOCKED | Works |
| `createImageAsync()` | BLOCKED | Works |
| Upload photos | No (placeholder rects only) | Yes (direct image fill) |
| Code size limit | 50KB | No hard limit |
| Timeout | ~30s | Configurable |

## Setup

The MCP server is already registered as `figma-console` in Claude Code.

**Plugin manifest location:**
```
C:\Users\londo\.figma-console-mcp\plugin\manifest.json
```

### User Must Do (every session):
1. Open Figma Desktop (not browser)
2. Go to Plugins > Development > Import plugin from manifest
3. Point to `C:\Users\londo\.figma-console-mcp\plugin\manifest.json`
4. Run the plugin — keep it running in background
5. The bridge auto-connects via WebSocket

## When to Use

- Uploading photos to Figma (Night Cinema processed files)
- Loading images from URLs (`createImageAsync`)
- Any operation that needs `fetch()` (e.g., downloading from image-host)
- Heavy scripts that exceed 50KB or 30s timeout
- When MCP `use_figma` fails silently on image operations

## Image Upload Example

```javascript
// Via bridge — this WORKS (blocked in MCP runtime)
const imageUrl = "https://raw.githubusercontent.com/Sukheil-Ganeev/image-host/master/photo.jpg";
const image = await figma.createImageAsync(imageUrl);
const rect = figma.createRectangle();
rect.resize(1080, 1350);
rect.fills = [{ type: "IMAGE", imageHash: image.hash, scaleMode: "FILL" }];
```

## Fallback: Manual Photo Import

If bridge is unavailable, create named placeholder rects:
```javascript
const rect = figma.createRectangle();
rect.name = "PHOTO: 01_cover_nc.png";
rect.resize(1080, 1350);
rect.fills = [{ type: "SOLID", color: { r: 0.5, g: 0.5, b: 0.5 } }];
// User drags photo into Figma and fills the rect manually
```

## Public Image Host

For photos that need public URLs:
- Repo: `Sukheil-Ganeev/image-host` (PUBLIC, master branch)
- URL pattern: `https://raw.githubusercontent.com/Sukheil-Ganeev/image-host/master/{filename}`
- Only upload marketing photos — never credentials or internal docs
