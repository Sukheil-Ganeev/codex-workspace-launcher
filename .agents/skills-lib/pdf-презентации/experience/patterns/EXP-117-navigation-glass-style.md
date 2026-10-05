---
id: EXP-117
date: 2026-02-18
type: pattern
severity: low
category: layout
projects: [debit-cards-research]
related: [EXP-114, EXP-115]
tags: [navigation, glass, opacity, controls, hotkeys]
status: verified
---

# EXP-117: Навигационные элементы в glass-стиле

## База
`#nav-arrows` с `backdrop-filter: blur(16px) saturate(130%)` и полупрозрачным градиентным фоном.

## Критично
Не снижать `opacity` навкнопок до `0.5-0.6`: их перестают замечать.

## Практика
- кнопки: `opacity: 1`
- визуальная «тихость» через приглушённый accent (alpha ~0.6-0.7)
- подсказка hotkeys: `opacity: 0.4`
