# figma-vip

Unified Figma super-skill for VIP-DXB-RUS Instagram design production.

## Canonical Source

- Source of truth: `D:/Downloads/InstaCovers/skills-source/figma-vip/`
- Published copies: `~/.claude/skills/figma-vip/` and `~/.codex/skills/figma-vip/`
- Publish command: `python3 scripts/publish_skill.py publish figma-vip`
- If a hotfix was made directly in Claude/Codex, backport it first with `python3 scripts/publish_skill.py pull figma-vip --from-env claude` (or `codex`)

## What It Does

Single entry point for ALL Figma work in the VIP tourism project. Combines:

- **Official Figma MCP skills** (6 skills: use, implement, generate-design, generate-library, design-system-rules, code-connect)
- **noemuch/bridge** (figma-console-mcp) for image uploads and fetch operations
- **VIP brand system** — colors, fonts, effects mapped from CSS to Figma API values
- **Night Cinema** photo processing pipeline
- **Batch production** workflow for creating multiple carousels

## When to Use

Load this skill FIRST before any Figma operation. Triggers:
- "figma", "use_figma", "html to figma", "carousel to figma"
- "bridge", "plugin api", "figma api", "Night Cinema figma"
- "import в figma", "photo placeholder", "design system figma"

## Key Components

| File | Purpose |
|------|---------|
| `SKILL.md` | Decision matrix, critical rules, brand system, quick reference |
| `references/plugin_api_rules.md` | WRONG/CORRECT code patterns for use_figma |
| `references/css_to_figma_mapping.md` | CSS property to Figma API conversion table |
| `references/etalon_structures.md` | 5 palette etalon layer structures |
| `references/brand_system.md` | Colors, fonts, effects for VIP brand |
| `references/bridge_guide.md` | figma-console-mcp setup and image upload |
| `references/night_cinema.md` | Photo color correction workflow |
| `references/workflows.md` | Three main production workflows (A/B/C) |
| `references/gotchas.md` | ALL known pitfalls by category |
| `references/batch_production.md` | Multi-carousel batch pipeline |

## Quick Start

1. Read `SKILL.md` for the decision matrix — pick the right workflow
2. Follow the Plugin API Critical Rules (Section 2) for every `use_figma` call
3. Load specific references on demand as needed

## Integration Points

- **Figma file:** `8B1Dfaq8XtBOXlJuS19UhK`
- **MCP servers:** Official Figma MCP + figma-console (bridge)
- **Project:** `D:/Downloads/InstaCovers/`
- **Photos:** `D:/Downloads/InstaCovers/photos/` + `D:/Downloads/Каталог турпродуктов ОАЭ/`
- **Scripts:** `D:/Downloads/InstaCovers/docs/figma-scripts/`

## Experience

Lessons learned are tracked in `experience/_index.md`. After each Figma session, new pitfalls go to `references/gotchas.md`, new patterns to `references/plugin_api_rules.md`.
