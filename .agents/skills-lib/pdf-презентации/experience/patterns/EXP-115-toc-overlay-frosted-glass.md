---
id: EXP-115
date: 2026-02-18
type: pattern
severity: low
category: design-system
projects: [debit-cards-research]
related: [EXP-070, EXP-116, EXP-117]
tags: [toc, overlay, glassmorphism, backdrop-filter, noise]
status: verified
---

# EXP-115: TOC overlay в стиле frosted glass

## Overlay
Градиентный фон (не однородный `rgba`) + `backdrop-filter: blur(30px) saturate(120%)`.

## Panel
Многоточечный градиент (4 stop, opacity ~0.85-0.9) + `blur(40px) saturate(150%)` и лёгкий SVG noise (`opacity: 0.03`).

## UX-деталь
Вместо крестика лучше pill-кнопка `ESC` (JetBrains Mono). Для заголовка `h2` нужен `padding-right: 70px`, чтобы не конфликтовал с кнопкой.
