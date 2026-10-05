---
id: EXP-041
date: 2026-02-11
type: warning
severity: critical
category: colors
projects: []
related: [EXP-007]
tags: [backdrop-filter, blur, artifacts, chrome-bug, glassmorphism]
status: verified
---

# EXP-041: Артефакты backdrop-filter: blur() — НЕ ЧИНИТЬ

## Проблема
При использовании `backdrop-filter: blur()` + полупрозрачные border-ы на тёмном фоне Chrome рендерит светящиеся линии/полосы вдоль краёв элементов. Это subpixel rendering артефакт браузера.

## Что НЕ работает (проверено в 6 итерациях)
1. Удаление blob-ов / animated borders / glitch / shimmer / noise / shadows
2. Opus-диагностика: 15 источников, 12 фиксов — НЕ помогло
3. Замена border на outline
4. Удаление backdrop-filter (убивает дизайн)
5. Изменение border-radius
6. Добавление overflow: hidden

## Правильное решение
**НЕ ТРОГАТЬ.** Объяснить пользователю:
- Это баг рендеринга Chrome при определённых масштабах
- Попробовать Ctrl+0 (сброс масштаба) или другой браузер
- В PDF артефакт может не проявляться

## Критическое правило
НИКОГДА не удалять визуальные эффекты (glassmorphism, blur, glow) ради "фикса" артефактов рендеринга — это только ухудшает дизайн. После 6 итераций удалений презентацию пришлось пересобирать с нуля.

## Контекст
- Сессия: 2026-02-11
- Проект: Калькулятор-Документация, Презентация Владельца
- Тема: "Vault Command Center" (deep charcoal #0D1117)
