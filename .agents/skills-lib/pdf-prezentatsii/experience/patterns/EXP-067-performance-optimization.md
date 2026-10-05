---
id: EXP-067
date: 2026-02-11
type: pattern
severity: high
category: performance
projects: [Skill_Presentations (все 23 справочника), Калькулятор-Документация]
related: [EXP-030, EXP-038, EXP-043, EXP-051]
tags: [размер-pdf, оптимизация, производительность, бенчмарки, изображения]
status: verified
---

## Контекст

Размер PDF напрямую влияет на удобство распространения (email, мессенджеры, облако). За 23 справочника выявлены конкретные факторы, которые раздувают PDF, и методы их контроля. Целевой диапазон: 3-8 MB на 18 слайдов 1920x1080.

## Описание

### Бенчмарки размеров реальных презентаций

| Презентация | Слайдов | Размер | Визуальная сложность | Примечание |
|-------------|---------|--------|---------------------|------------|
| Search Radar (SEO) | 18 | 3.5 MB | Средняя | Минимум декора, solid цвета |
| javascript-nodejs "Amber Terminal" | 18 | 3.5 MB | Средняя | Terminal mockups, code |
| Database-SQL "Data Vault" | 18 | 3.8 MB | Средняя | ERD SVG, SQL code |
| Payment "FinTech Vault" | 18 | 3.9 MB | Средняя | Flow diagrams, card mockup |
| Instagram "Aurora Warm" | 18 | 4.4 MB | Средняя | Светлая тема, IG gradient |
| yandex-cloud "Red Blueprint" | 18 | 4.7 MB | Средняя | Blueprint стиль |
| YouTube "Studio Dark v2" | 18 | 5.1 MB | Высокая | deco-grid + circles + code badges |
| Scenario Graph (Make.com) | 18 | 5.9 MB | Высокая | Module nodes, scenario flows |
| Partnership Network | 18 | 6.1 MB | Высокая | SVG диаграммы, funnel |
| Puzzle Blueprint (PuzzleBot) | 18 | 6.9 MB | Высокая | Builder flows, dot-grid |
| VK "Steel Canvas" | 18 | 7.6 MB | Высокая | Много визуальных слоёв |
| VK Video "Video Stream" | 18 | 7.4 MB | Высокая | Player mockups, gradient borders |
| Ad Engine (Рекламные) | 18 | 8.3 MB | Очень высокая | Donut SVG, pipeline, dot-grid |
| WhatsApp "Encrypted" v2 | 18 | 9.6 MB | Очень высокая | Glow blobs (filter:blur) x2 на слайд |
| Docker "Container Dock" ДО оптимизации | 18 | 52 MB | Критическая | filter:blur x54, glass, grid |
| Docker "Container Dock" ПОСЛЕ оптимизации | 18 | 2.5 MB | Средняя (7 фото) | Без filter:blur, solid bg |
| Threads "Neon Wire" ПОСЛЕ оптимизации | 18 | 0.9 MB | Низкая (убраны тени) | Минимум визуального шума |

### Факторы, раздувающие PDF (от большего к меньшему)

| Фактор | Impact | Пример | EXP |
|--------|--------|--------|-----|
| **filter:blur() на bg-glow (3/slide)** | **x20 (2.5 -> 52 MB)** | 54 blurred circles = Gaussian bitmap layers | **EXP-126** |
| **radial-gradient на ::after слайдов** | x4 (3.5 -> 14.5 MB) | mesh-эффект на full-slide pseudo | EXP-043 |
| **linear-gradient на карточках** | x3 (3.7 -> 11 MB) | gradient bg на .card и .code-block | EXP-038 |
| **SVG feTurbulence** | x2.5 (7 -> 17 MB) | noise-текстура на каждом слайде | EXP-030 |
| **Glow blobs (filter:blur, мало)** | +3-6 MB | 2 штуки на слайд, 120-160px blur | EXP-051 |
| **Встроенные HD фото** | +3-5 MB | Реальные фото из YD (яхты ~3.5 MB) | EXP-052 |
| **deco-grid + deco-circles** | +1-2 MB | Повторяющиеся SVG/CSS паттерны | EXP-037 |
| **gradient borders (mask-composite)** | +0.5-1 MB | ::before на каждой карточке | EXP-031 |
| **Solid цвета, border accents** | ~0 MB | border-top/left + solid bg | -- |
| **Gradient-divider (1px)** | ~0 MB | Тонкая линия, мизерный impact | -- |

### Стратегии оптимизации

#### 1. Solid цвета вместо gradient-ов

```css
/* Тяжело (x3 размер): */
.card { background: linear-gradient(135deg, rgba(74,222,128,0.08), rgba(34,211,238,0.04)); }

/* Легко (0 impact): */
.card { background: var(--bg-card); border-top: 2px solid rgba(74,222,128,0.3); }
```

#### 2. Контроль glow blobs

```css
/* Каждый glow blob = ~0.3-0.5 MB */
.bg-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(150px);  /* Работает в PDF */
    opacity: 0.08;        /* Меньше opacity = меньше размер */
}
```

Правила:
- Максимум 2 glow blob на слайд
- opacity: 0.04-0.08 (не выше)
- Не на каждом слайде -- через 1-2 слайда

#### 3. Оптимизация изображений

```python
from PIL import Image

def optimize_image(path, max_width=800, quality=85):
    img = Image.open(path)
    # Уменьшить до максимальной ширины
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
    # Сохранить с оптимальным качеством
    img.save(path, 'JPEG', quality=quality, optimize=True)
```

Для презентации 1920x1080 фото шире 800px не нужны -- они отображаются в карточках ~300-400px.

#### 4. Декорации без impact на размер

Эти элементы добавляют визуальную глубину при ~0 MB impact:
- `border-left: 3px solid var(--accent)` на highlight-box и card
- `.gradient-divider` (1px height, `linear-gradient(90deg, transparent, accent, transparent)`)
- Тонкие `border: 1px solid rgba(255,255,255,0.06)` на карточках
- `border-top: 2px solid` с solid цветом на карточках
- SVG inline иконки (5-10 строк)

#### 5. Dot-grid текстура -- безопасно

Dot-grid через `radial-gradient` на `::after` с `background-size: 32px 32px` -- безопасный декоративный паттерн. Ad Engine (8.3 MB на 18 слайдов с dot-grid на каждом слайде) -- в пределах нормы. Это НЕ то же самое что full-slide radial-gradient mesh (EXP-043).

### Лимиты

| Метрика | Норма | Предупреждение | Критично |
|---------|-------|----------------|----------|
| PDF на 18 слайдов | 3-5 MB | 5-8 MB | >10 MB |
| Один glow blob | 0.3-0.5 MB | -- | -- |
| Фото (одно, HD) | 0.5-1 MB | 1-3 MB | >3 MB |
| Конвертация | 3-15 сек | 15-30 сек | >30 сек |

### Диагностика: если PDF > 10 MB

1. Проверить SVG filters: `grep "feTurbulence\|feDisplacementMap" file.html`
2. Проверить gradient на card/code-block: `grep "linear-gradient\|radial-gradient" file.html | grep -i "card\|code"`
3. Проверить glow blobs: `grep "filter.*blur" file.html | wc -l` (>36 = по 2 на слайд = много)
4. Проверить встроенные изображения: `ls -la images/` (файлы > 1 MB -- сжать)

## Когда применять

- При создании каждой новой презентации -- закладывать solid цвета и border-accents как базу
- После первой конвертации -- проверить размер PDF и сравнить с бенчмарками
- При запросе "визуально богаче" -- добавлять декорации по возрастанию impact (border -> glow -> gradient)
- При жалобе "тяжёлый файл" -- диагностика по чек-листу выше

## Связанные уроки

- **EXP-030** -- SVG feTurbulence noise = огромный PDF
- **EXP-038** -- CSS gradients на карточках раздувают PDF в 3x
- **EXP-043** -- radial-gradient на ::after раздувает PDF в 4x
- **EXP-051** -- Visual enrichment system, glow blobs -- основной источник роста
