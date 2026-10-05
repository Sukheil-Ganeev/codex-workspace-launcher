---
id: EXP-116
date: 2026-02-18
type: warning
severity: medium
category: colors
projects: [debit-cards-research]
related: [EXP-105, EXP-115, EXP-119]
tags: [glow, glassmorphism, text-shadow, box-shadow, ui]
status: verified
---

# EXP-116: «Убери свечения» не равно «убери glassmorphism»

## Что обычно значит «убери свечения»
- убрать `text-shadow` glow
- снизить opacity у декоративного `.glow`
- убрать цветной glow из `box-shadow` (оставить нейтральные тени)

## Что не нужно убирать
- `backdrop-filter` (blur/saturate)
- градиентные фоны карточек
- glass-бордеры
- inset top-line эффекты

## Правило
Свечения: text-shadow, цветные тени, radial glow overlays. Glassmorphism: blur/saturate/градиенты/тонкие световые линии.
