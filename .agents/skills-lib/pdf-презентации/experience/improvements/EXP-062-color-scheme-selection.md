---
id: EXP-062
date: 2026-02-11
type: improvement
severity: high
category: design-system
projects: [Skill_Presentations (все 23 справочника), Калькулятор-Документация]
related: [EXP-026, EXP-040, EXP-029, EXP-033]
tags: [палитра, цвета, темы, css-переменные, дизайн]
status: verified
---

## Контекст

За 23 справочника + 3 презентации Калькулятора выработана система выбора цветовых палитр. Все темы строятся на одной CSS-структуре (`:root` переменные), уникальность -- через палитру и тема-специфичные компоненты. Правильный выбор цветов определяет восприятие всей презентации.

## Описание

### Таблица тем с hex-кодами

| Тема | Тип | bg-dark | accent-1 | accent-2 | accent-3 | Размер |
|------|-----|---------|----------|----------|----------|--------|
| GitHub Dark (Git) | Тёмная | #0d1117 | #58a6ff (blue) | #3fb950 (green) | #f85149 (red) | ~4 MB |
| Amber Terminal (JS/Node) | Тёмная | #0d1117 | #F59E0B (amber) | #68D391 (green) | #f85149 (red) | 3.5 MB |
| Aurora Warm (Instagram) | СВЕТЛАЯ | #FAFAF8 | IG gradient | #E1306C (pink) | #833AB4 (purple) | 4.4 MB |
| Steel Canvas (VK) | Тёмная | #0F172A | #5181B8 (VK blue) | #FF6347 (red) | #F59E0B (amber) | 7.6 MB |
| Red Blueprint (Yandex Cloud) | Тёмная | #0C1220 | #FC3F1D (red) | #007ACC (blue) | #FFD700 (gold) | 4.7 MB |
| Vault Command Center | Тёмная | #0D1117 | #00c853 (emerald) | #ffa000 (amber) | #ef5350 (red) | ~5 MB |
| Neon Wire (Threads) | Тёмная | #08081a | #e1306c (pink) | #8b5cf6 (violet) | #22d3ee (cyan) | ~4 MB |
| Video Stream (VK Video) | Тёмная | #06060e | #0077ff (blue) | #ff4444 (red) | #8b5cf6 (purple) | 7.4 MB |
| WhatsApp Encrypted | Тёмная | #0b141a | #25d366 (green) | #128c7e (teal) | #34b7f1 (blue) | 9.6 MB |
| WA Business | Тёмная | (green+gold) | #25d366 (green) | #d4af37 (gold) | -- | ~5 MB |
| Data Vault (Database-SQL) | Тёмная | #0a1a0f | #4ade80 (green) | #22d3ee (cyan) | #fbbf24 (amber) | 3.8 MB |
| FinTech Vault (Payment) | Тёмная | #0a0f1e | #d4af37 (gold) | #007acc (blue) | #ef5350 (red) | 3.9 MB |
| Search Radar (SEO) | Тёмная | #080e10 | #4caf50 (green) | #2196f3 (blue) | #ff9800 (orange) | 3.5 MB |
| YouTube Studio Dark | Тёмная | #0a0a0a | #ff0000 (red) | #3ea6ff (blue) | -- | 5.1 MB |
| Partnership Network | Тёмная | #0a1014 | #14b8a6 (teal) | #8b5cf6 (purple) | #f59e0b (amber) | 6.1 MB |
| Ad Engine (Рекламные) | Тёмная | #0f0a08 | #ff6b00 (orange) | #0077ff (blue) | #e74c3c (red) | 8.3 MB |
| Puzzle Blueprint (PuzzleBot) | Тёмная | #0C0E22 | #6C5CE7 (indigo) | #A8E06C (lime) | #FF7EB3 (rose) | 6.9 MB |
| Scenario Graph (Make.com) | Тёмная | #0A0920 | #B24BF3 (magenta) | #00D4FF (cyan) | #FF6B6B (coral) | 5.9 MB |
| Channel Pulse (SaleBot) | Тёмная | #080C1A | #1B6EF3 (blue) | #2DD4A8 (mint) | #FF8C42 (tangerine) | ~5 MB |
| Claude Editorial Light | СВЕТЛАЯ | #FAFAF7 | #D4714E (terracotta) | #6E4FE0 (purple) | #1D8A5A (green) | ~4 MB |
| Container Dock (Docker) | Тёмная | #0A0E1A | #2496ED (Docker blue) | #1B3A5C (navy) | #FFC107 (yellow) | 2.5 MB |
| Desert Minimal (reportlab) | Светлая | #FFFFFF | #C4956A (sand) | #2D2D2D (charcoal) | -- | ~1 MB |

### Структура CSS-переменных (единая для всех)

```css
:root {
  --bg-dark: #_;       /* Фон body */
  --bg-slide: #_;      /* Фон слайда (может = bg-dark) */
  --bg-card: #_;       /* Фон карточки */
  --accent-1: #_;      /* Основной акцент (бренд/тема) */
  --accent-2: #_;      /* Второй акцент (дополнительный) */
  --accent-3: #_;      /* Третий (ошибки/удаление/глубина) */
  --accent-4: #_;      /* Четвёртый (предупреждения, опционально) */
  --text-primary: #_;
  --text-secondary: #_;
  --text-muted: #_;
  --gradient-top: linear-gradient(90deg, accent-1, accent-2, accent-3);
}
```

### Правила выбора палитры

**Тёмная vs Светлая тема:**
- Тёмная (bg < #151515) -- по умолчанию для технических справочников, code-heavy слайдов, IT-продуктов
- Светлая (bg > #F0F0F0) -- для consumer-продуктов (Instagram), клиентских презентаций, бизнес-контента

**Привязка к бренду:**
- accent-1 = основной цвет бренда (VK blue #5181B8, YouTube red #ff0000, Telegram blue #229ED9)
- accent-2 = дополнительный функциональный цвет
- accent-3 = третий цвет для глубины палитры (часто фиолетовый #8b5cf6)

**2 цвета мало, 3 -- оптимально:**
- 2 цвета (accent-1 + accent-2) создают монотонность
- 3 цвета (+ accent-3) обеспечивают достаточную палитру для card variants, tags, highlights
- 4 цвета -- только для специфических тем (Git: blue/green/red/yellow)

**Контрастность:**
- Text-primary на тёмном фоне: #e6edf3 или #f0f0ff (НЕ чистый #ffffff -- слишком резко)
- Text-secondary: #8b949e (50-60% от primary)
- Text-muted: #6e7681 (30-40% от primary)

### Типичные ошибки

1. **Code-block bg = чистый чёрный #010409** -- слишком резкий контраст. Правильно: тонировать в цвет темы (EXP-040)
2. **gradient-top шире 3 цветов** -- выглядит пёстро. Оптимально 3 цвета
3. **Неоновые бордеры на каждой карточке тёмной темы** -- создают "грязь" (EXP-033). Использовать нейтральные rgba(255,255,255,0.06-0.07)
4. **Одинаковый bg-dark для slide и card** -- карточки сливаются. Card должен быть на 1-2 уровня светлее

## Когда применять

- При создании нового справочника -- первый шаг: определить палитру через `:root`
- При адаптации существующего справочника под другой бренд -- менять ТОЛЬКО `:root`, структура остаётся
- При запросе "другие цвета" / "смени тему" -- менять только CSS-переменные

## Связанные уроки

- **EXP-026** -- Серия справочников, единая дизайн-система с переключаемыми темами
- **EXP-029** -- Тёплые light-терминалы на светлой теме
- **EXP-033** -- Тени на тёмном фоне = "грязь"
- **EXP-040** -- Code-block bg = тема слайда, НЕ чёрный
