# Brand Design Skill for Claude Code

A Claude Code slash command (`/brand-design`) that generates on-brand HTML designs for LinkedIn content — carousels, article images, banners, infographics, and social posts.

## What It Does

When invoked via `/brand-design` in Claude Code, this skill instructs Claude to produce **self-contained HTML files** with:

- Inline CSS with a complete brand token system (colors, typography, spacing)
- Google Fonts loaded via `<link>`
- SVG graphics (no external image dependencies)
- An `html2canvas` download button for PNG/PDF export
- Mobile-optimized layouts (tested at 350px viewport width)

## Supported Formats

| Format | Dimensions | Use Case |
|---|---|---|
| `carousel` | 1080 × 1080 px per slide | LinkedIn carousel posts |
| `article-image` | 1080 × 607 px | LinkedIn article headers |
| `banner` | 1584 × 396 px | Profile/company banners |
| `infographic` | 1080 × 1350 px | Tall-format data visuals |
| `social-post` | 1080 × 1080 px | Single-image LinkedIn posts |

## Brand System

The skill encodes a complete design system called **Cool Slate + Signal Accents v2**, including:

- **6 punch backgrounds** (dark slides) and a cloud breathe background (light slides)
- **4 signal accent colors** (Emerald, Amber, Blue, Red-Orange) with bright/muted variants
- **Typography scale** using Inter (sans) and JetBrains Mono (mono)
- **Glass-panel card system** with hollow border technique
- **Slide rhythm rules** for carousel pacing (punch/breathe alternation)
- **Readability principles** with minimum font size thresholds

## Installation

Copy the skill file into your project's Claude Code commands directory:

```bash
mkdir -p .claude/commands
cp .claude/commands/brand-design.md <your-project>/.claude/commands/
```

Then use it in Claude Code by typing `/brand-design` followed by your design request.

## Usage Examples

```
/brand-design Create a 7-slide LinkedIn carousel about product-market fit frameworks
```

```
/brand-design Design an article header image for a post about developer productivity
```

```
/brand-design Build a LinkedIn banner showcasing our SaaS metrics dashboard
```

## Author

**Victor Ugochukwu**

## License

MIT
