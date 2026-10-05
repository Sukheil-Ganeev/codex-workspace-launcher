---
id: EXP-034
date: 2026-02-10
type: pattern
severity: high
category: layout
projects: []
related: [EXP-006, EXP-036]
tags: [standalone, white-label, scroll-spy, checklist, progress-bar, SVG-icons]
status: verified
---

# White Label Standalone Presentation — Lessons Learned

**Дата:** 2026-02-10
**Проект:** `D:/Downloads/Codex_Results/White_Label_Negotiation/`
**Тип:** Standalone бизнес-презентация (НЕ из серии справочников)
**Результат:** 14 слайдов, тёмная navy-тема, Candara/Corbel шрифты, ~70 KB HTML

## Контекст

Презентация для переговоров по white-label партнёрству в VIP-туризме ОАЭ.
Исходная версия (v4) — 9 слайдов от Codex. Прокачена до v5 — 14 слайдов с полным визуальным апгрейдом.

## EXP-062: Smooth scroll + scroll spy конфликт (КРИТИЧНЫЙ БАГ!)

**Проблема:** При нажатии стрелок навигации на слайдах 8-9 (и любых соседних) происходит "bounce" — слайд прыгает туда-сюда.
**Причина:** `scrollIntoView({behavior: 'smooth'})` генерирует серию scroll-событий. Функция `activeSlideByScroll()` (scroll spy) ловит промежуточную позицию, сбрасывает `current` на предыдущий слайд, и следующее нажатие стрелки снова переходит на тот же.
**Решение:** Scroll lock — блокировка scroll spy на 800ms после keyboard-навигации:
```javascript
let scrollLock = false;
let scrollLockTimer = null;

function goTo(idx) {
  const safe = Math.max(0, Math.min(idx, slides.length - 1));
  if (safe === current) return;
  scrollLock = true;
  clearTimeout(scrollLockTimer);
  slides[safe].scrollIntoView({ behavior: 'smooth', block: 'start' });
  setHud(safe);
  scrollLockTimer = setTimeout(function() { scrollLock = false; }, 800);
}

function activeSlideByScroll() {
  if (scrollLock) return;  // ← ключевая строка
  // ... остальная логика
}
```
**Когда:** ВСЕГДА когда есть smooth scroll + scroll spy в HTML-презентациях.

## EXP-063: Интерактивный чек-лист с CSS-анимацией

**Контекст:** Слайд "Чек-лист: 10 пунктов до первой брони с новым гидом" — пользователь попросил кликабельные чекбоксы.
**Решение:**
```css
.check-box {
  cursor: pointer;
  transition: all 0.25s ease;
  user-select: none;
}
.check-box:hover { border-color: var(--cyan); background: rgba(92, 200, 255, 0.12); }
.check-box.checked { border-color: var(--mint); background: rgba(50, 211, 154, 0.2); }
.check-box.checked::after {
  content: "";
  width: 14px; height: 14px;
  background-image: url("data:image/svg+xml,...checkmark SVG...");
  animation: checkPop 0.3s ease;
}
.checklist li.is-checked span:last-child {
  text-decoration: line-through;
  text-decoration-color: rgba(50, 211, 154, 0.4);
  color: var(--text-dim);
}
@keyframes checkPop { 0% { scale(0) } 50% { scale(1.3) } 100% { scale(1) } }
```
JS: `.check-box` click → toggle `.checked` + parent `li.is-checked`
**ВАЖНО:** В PDF-версии это не работает (PDF статичный). Только для HTML-просмотра.

## EXP-064: Стоковые фото с overlay в тёмных презентациях

**Подход:** Unsplash фото встраиваются двумя способами:
1. **Фоновое фото на титульном слайде** — gradient overlay 85-95%:
```css
#slide-1 {
  background:
    linear-gradient(180deg, rgba(7,13,31,0.86) 0%, rgba(15,26,54,0.9) 50%, rgba(18,34,70,0.94) 100%),
    url('https://images.unsplash.com/photo-XXX?w=1920&q=80') center/cover no-repeat,
    /* остальные слои... */;
}
```
2. **Декоративные фото** (260x168px) — `mix-blend-mode: luminosity; opacity: 0.5`:
```css
.slide-photo {
  position: absolute; right: 74px; bottom: 56px;
  width: 260px; height: 168px;
  object-fit: cover; border-radius: 14px;
  opacity: 0.5; mix-blend-mode: luminosity;
  pointer-events: none;
}
```
**Проверенные Unsplash IDs для ОАЭ/бизнес-темы:**
- Dubai skyline: `photo-1512453979798-5ea266f8880c`
- Business handshake: `photo-1521791136064-7986c2920216`
- Contract signing: `photo-1450101499163-c8848c66ca85`
**ВАЖНО:** Фото загружаются по сети при открытии HTML. Для offline/PDF — скачивать и встраивать base64.

## EXP-065: Progress bar вместо статичного topline

**Идея:** `.topline` из статичного градиентного бара → индикатор позиции в деке.
```css
.topline {
  background: rgba(168, 196, 244, 0.15);  /* track */
  position: relative; overflow: hidden;
}
.topline::after {
  content: ""; position: absolute; left: 0; top: 0; height: 100%;
  background: linear-gradient(90deg, var(--mint), var(--cyan), var(--amber));
}
/* Ширина для каждого слайда: */
#slide-1 .topline::after { width: 7.1%; }   /* 1/14 */
#slide-7 .topline::after { width: 50%; }    /* 7/14 */
#slide-14 .topline::after { width: 100%; }  /* 14/14 */
```
**Эффект:** Зритель всегда видит где он в деке. Работает в PDF (статичная ширина).

## EXP-066: Watermark-числа как фоновые якоря

```css
.watermark {
  position: absolute; right: 60px; bottom: -20px;
  font-size: 280px; font-weight: 900;
  color: rgba(168, 196, 244, 0.04);
  pointer-events: none; z-index: 0;
}
```
HTML: `<div class="watermark">01</div>` в каждом слайде.
**Эффект:** Визуальная глубина + ритм + подсознательная нумерация.

## EXP-067: Уникальные gradient mesh на каждый слайд

**Проблема:** Все слайды с одинаковым фоном = визуальная монотонность.
**Решение:** Для каждого slide-N свои radial-gradient позиции/цвета:
```css
#slide-2 { background: radial-gradient(800px at 90% 80%, rgba(rose,0.1), transparent 60%), ...; }
#slide-3 { background: radial-gradient(800px at 50% 0%, rgba(violet,0.12), transparent 60%), ...; }
```
**Правило:** Использовать акцентные цвета темы (--mint, --cyan, --amber, --rose, --violet), чередуя позиции (углы, центр, стороны).

## EXP-068: SVG inline иконки вместо emoji

**Проблема:** Emoji (🔍, ⚡, 🎯) выглядят непрофессионально и рендерятся по-разному на разных ОС.
**Решение:** Stroke-based SVG 22x22:
```html
<span class="icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
</svg></span>
```
```css
.icon { display: inline-flex; margin-right: 8px; opacity: 0.7; color: var(--cyan); }
.card.warn .icon { color: var(--amber); }
.card.danger .icon { color: var(--rose); }
```
**Набор:** search, zap, target, handshake, file-text, shield, scale, clock, play, check-circle, x-circle.

## EXP-069: CSS bar charts для финансовой визуализации

```css
.bar-track { height: 32px; border-radius: 8px; background: rgba(168,196,244,0.1); }
.bar-fill { height: 100%; border-radius: 8px; padding-left: 12px; font-size: 15px; color: #fff; }
.bar-fill.mint { background: linear-gradient(90deg, var(--mint), rgba(50,211,154,0.6)); }
```
**Использование:** "Без протокола" vs "С протоколом" — retention 60% vs 90%, маржа 20% vs 35%.

## EXP-070: KPI ring SVG — круговые прогресс-индикаторы

```html
<svg class="kpi-ring" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(168,196,244,0.12)" stroke-width="8"/>
  <circle cx="50" cy="50" r="42" fill="none" stroke="var(--mint)" stroke-width="8"
    stroke-dasharray="264" stroke-dashoffset="26" stroke-linecap="round"
    transform="rotate(-90 50 50)"/>
  <text x="50" y="50" text-anchor="middle" dy="0.35em" fill="#f0f7ff" font-size="18">≤10м</text>
</svg>
```
**Формула:** `stroke-dasharray` = 2πr = 2×3.14×42 ≈ 264. `stroke-dashoffset` = 264 × (1 - процент).
- 90% fill: offset = 264 × 0.1 = 26
- 100% fill: offset = 0
- 94% fill: offset = 264 × 0.06 ≈ 16

## EXP-071: go-badge collision с topline

**Проблема:** Абсолютно позиционированная плашка `go-badge` с `top: 56px` совпадает с padding слайда, из-за чего визуально слипается с topline.
**Решение:** `top: 24px` — вынести в зону выше padding.
**Правило:** При изменении topline/header области всегда проверять absolute-positioned элементы в той же зоне.

## Workflow standalone презентаций

В отличие от серии справочников (Skill_Presentations), standalone презентации:
1. Не привязаны к SKILL.md-скиллу как источнику контента
2. Могут иметь произвольную тему (не из дизайн-системы серии)
3. Контент создаётся с нуля или адаптируется из бизнес-материалов
4. Допускают интерактивные элементы (чек-листы, hover) для HTML-версии

**Итоговая структура проекта:**
```
White_Label_Negotiation/
├── White_Label_Negotiation_v5.html            # Статика
├── White_Label_Negotiation_v5_Animated.html   # С анимациями
└── _archive/
    ├── v4_originals.zip
    └── White_Label_Negotiation_v4.pdf
```
