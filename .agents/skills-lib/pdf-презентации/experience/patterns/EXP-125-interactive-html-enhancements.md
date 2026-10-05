# EXP-125: Интерактивные улучшения HTML-презентаций

**Дата:** 2026-02-18
**Контекст:** Добавление JS навигации + CSS анимаций в существующие презентации

## Урок 1: zoom вместо transform: scale() для viewport scaling
- **ПРОБЛЕМА:** `body { transform: scale(0.8) }` ломает ВСЕ `position: fixed` элементы
- TOC overlay, progress bar, nav controls -- все перестают быть fixed
- Overlay получает height = scrollHeight (15000+px), контент центрируется в середине
- **РЕШЕНИЕ:** `body { zoom: 0.8 }` -- масштабирует контент БЕЗ поломки fixed
- zoom поддерживается: Chrome, Edge, Safari, Firefox 126+

## Урок 2: e.code для keyboard shortcuts
- `e.key` зависит от раскладки клавиатуры (RU: T->Е, F->А)
- `e.code` возвращает физическую клавишу (KeyT, KeyF) -- работает ВСЕГДА
- Паттерн: e.code для букв, e.key для спецклавиш (Arrow, Escape, Home)

## Урок 3: TOC overlay -- правильная реализация
```css
/* ПРАВИЛЬНО */
position: fixed; top: 0; left: 0;
width: 100%; height: 100%;
justify-content: flex-start;  /* НЕ center -- чтобы не обрезало */
overflow-y: auto;              /* скролл если много слайдов */
padding: 32px 0;              /* отступы сверху/снизу */
background: rgba(X,X,X,0.95); /* почти непрозрачный */
z-index: 10000;
```

## Урок 4: Premium CSS анимации (безопасные для презентаций)
- `@keyframes fadeInUp` -- появление заголовков (translateY 30px -> 0)
- `@keyframes scaleIn` -- появление карточек (scale 0.9 -> 1)
- `@keyframes shimmer` -- мерцающий градиент на акцентном тексте
- `@keyframes breathe` -- пульсация glow-орбов (6s infinite)
- `@keyframes gradientSlide` -- анимированная линия сверху слайда
- Hover: translateY(-4px) + enhanced box-shadow + border-color
- Каскадные задержки: nth-child(N) { animation-delay: N*0.1s }

## Урок 5: Glass cards -- правильный рецепт
```css
.card {
  background: rgba(20, 27, 45, 0.65);  /* полупрозрачный */
  border: 1px solid rgba(accent, 0.1);
  box-shadow: 0 4px 24px rgba(0,0,0,0.2),
              inset 0 1px 0 rgba(255,255,255,0.04);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.3),
              0 0 30px rgba(accent, 0.1);
  border-color: rgba(accent, 0.2);
}
/* Gradient border через ::before */
.card-elevated::before {
  content: '';
  position: absolute;
  top: -1px; left: -1px; right: -1px; bottom: -1px;
  border-radius: 17px;
  background: linear-gradient(135deg, rgba(color1,0.2), transparent 40%, transparent 60%, rgba(color2,0.2));
  z-index: -1; opacity: 0;
  transition: opacity 0.3s;
}
.card-elevated:hover::before { opacity: 1; }
```

## ВНИМАНИЕ: PDF vs HTML
- Анимации, hover, transitions -- ТОЛЬКО для HTML просмотра
- При конвертации в PDF через Playwright -- анимации игнорируются
- НЕ ломают PDF, но и не видны в PDF
- zoom тоже не влияет на PDF (Playwright сам устанавливает viewport)
