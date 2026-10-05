---
id: EXP-112
date: 2026-02-18
type: warning
severity: medium
category: colors
projects: [debit-cards-research]
related: [EXP-092, EXP-093]
tags: [box-shadow, inset, artifacts, dark-theme, glassmorphism]
status: verified
---

# EXP-112: inset highlight создаёт светлые артефакты

## Проблема
`inset 0 1px 0 rgba(255,255,255,0.04)` в `box-shadow` даёт видимые светлые квадраты в углах карточек на тёмном фоне.

## Причина
Даже малый alpha у белого inset-слоя становится заметным на тёмных тонах из-за сложения с `border-radius` и другими тенями.

## Решение
Не использовать inset white highlight в тёмной теме. Если нужен верхний блик, делать его через `border-top`/`gradient` или псевдоэлемент.

## Связанные наблюдения
EXP-092 (rgba на тёмном часто невидим), EXP-093 (backdrop-filter на однородном фоне не работает).
