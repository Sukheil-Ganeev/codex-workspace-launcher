# Figma VIP — Experience Index

## Sessions

| Date | Carousel | Slides | Key Lessons |
|------|----------|--------|-------------|
| 2026-03-28 | arab_traditions_v1 | 8/8 | L-01..L-13: source of truth, font weights, FILL/HUG ordering, wrapper defaults, SVG icons, auto-validation |
| 2026-03-28 | arabic_coffee_v1 | 8/8 | Stable production — 0 issues per slide |
| 2026-03-28 | avoid_queues_v1 | 8/8 (agent) | L-14..L-18: subagent quality gaps, batch fix workflow, scan→save→fix pattern |
| 2026-03-28 | banned_medicines_v1 | 8/8 (agent) | Wrong content (dress_code) — agent read wrong HTML folder |
| 2026-03-28 | cheap_food_dubai_v1 | 10/10 (agent) | Font weights unfixed — agent didn't read corrections before creating |
| 2026-03-28 | coffee_shops_v1 | 8/8 (agent) | Mostly correct, slide 1 font issue |

## Top Lessons (read first)

1. **L-01** CSS — источник правды, не эталон. Цвета, размеры, отступы — только из CSS.
2. **L-04** Font weight +1 ступень на цветном фоне (SemiBold/ExtraBold/Medium вместо Medium/Bold/Regular).
3. **L-05** `layoutSizing = "FILL"` только ПОСЛЕ `appendChild`.
4. **L-06** Wrapper-фреймы: `clipsContent = false`, sizing после append.
5. **L-08** `createNodeFromSvg()` работает — используй для иконок.
6. **L-09** Автопроверка в конце скрипта: сканировать h===100, w===100+clip.

## Full Reference

- `references/lessons-learned.md` — 13 уроков с Problem/Root Cause/Rule + checklist
- `references/gotchas.md` — технические ошибки Figma API (30+ pitfalls)
- `D:/Downloads/InstaCovers/docs/figma-data/font_weight_corrections.md` — таблица коррекций жирностей
