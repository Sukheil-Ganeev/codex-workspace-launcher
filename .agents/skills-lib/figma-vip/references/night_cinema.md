# Night Cinema Color Correction

The Night Cinema preset gives photos a warm cinematic look essential for VIP brand covers. Must be applied BEFORE importing photos to Figma because Figma lacks `hue-rotate`.

## CSS Filter Values (Source of Truth)

```css
filter: brightness(0.95) contrast(1.25) saturate(1.15) hue-rotate(5deg);
```

**Source of truth:** `templates/carousel/_boilerplate/cover_template.html`
**WARNING:** V2 speed boats had WRONG values (brightness 0.68-0.72, no hue-rotate) — do NOT copy from V2 carousels. Always verify against boilerplate.

## Color Overlay Gradient

Applied as a separate div in HTML, separate layer in Figma (not baked into the photo):

```css
/* mix-blend-mode: color */
background: linear-gradient(180deg,
  rgba(0,80,100,0.15) 0%,
  transparent 40%,
  rgba(196,137,110,0.12) 70%,
  rgba(26,23,20,0.30) 100%
);
```

## Why Figma Can't Replicate hue-rotate

Figma's image filters support exposure, contrast, saturation, temperature, tint, highlights, and shadows — but NOT hue rotation. The 5deg hue shift is subtle but creates the characteristic warm cinema tone. Without it, photos look slightly colder.

Solution: bake the full CSS filter into the photo file before import.

## Python Script

**Location:** `scripts/apply_night_cinema.py`

Applies brightness/contrast/saturation/hue-rotate equivalent using Pillow, producing `*_nc.png` files.

### Usage

```bash
cd D:/Downloads/InstaCovers
python scripts/apply_night_cinema.py
```

The script processes `photos/{carousel_name}/` originals and outputs corrected versions to `photos/{carousel_name}_nc/`.

## Photo Organization

```
photos/
  {topic}/          — source photos (originals, high-res JPG)
  {topic}_nc/       — Night Cinema corrected (*_nc.png, ready for Figma)
```

## Figma Workflow

1. Place original photos in `photos/{carousel_name}/`
2. Run `python scripts/apply_night_cinema.py` to produce `*_nc.png`
3. Import `*_nc.png` files into Figma (via bridge or manual drag-drop)
4. Add overlay layers in Figma separately:
   - Vignette (radial gradient, 5 stops for smooth falloff)
   - Gradient overlay (linear, top-to-bottom)
   - Color overlay (copper/blue at ~0.12 opacity)
   - Grain (noise texture, blendMode: OVERLAY)

## Photo Sources

Tourism product catalog: `D:/Downloads/Каталог турпродуктов ОАЭ/`
- Each product has `фото/` (originals) and `фото_для_сайта/` (web-optimized WebP)
- Prefer `фото/` originals for carousel production (higher quality)
- **Some folders are EMPTY** — always verify photos exist before planning slides
- When copying, rename to simple snake_case (e.g., `01_cover.jpg`)
