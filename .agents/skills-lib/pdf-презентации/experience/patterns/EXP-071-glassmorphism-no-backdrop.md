# EXP-071: Glassmorphism без backdrop-filter

## Проблема
backdrop-filter вызывает артефакты в Chrome при конвертации в PDF (EXP-041). Нужна имитация glassmorphism без него.

## Техники

### 1. Полупрозрачный фон с gradient layers
```css
background: linear-gradient(180deg,
  rgba(30,35,65,0.97) 0%,
  rgba(16,20,40,0.98) 25%,
  rgba(10,12,26,0.99) 100%);
```

### 2. Тонкая белая рамка + inset shadow
```css
border: 1px solid rgba(255,255,255,0.08);
box-shadow: 12px 0 80px rgba(0,0,0,0.95),
  inset -1px 0 0 rgba(255,255,255,0.05);
```

### 3. Glow blob через ::after
```css
.header::after {
  content: '';
  position: absolute;
  width: 160px; height: 50px;
  background: var(--accent-1);
  opacity: 0.08;
  border-radius: 50%;
  filter: blur(25px);
  pointer-events: none;
}
```

### 4. Glass card эффект (header/search)
```css
.toc-header {
  margin: 16px;
  border-radius: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
}
```

### 5. Gradient text
```css
background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

### 6. Ambient orbs (radial-gradient)
```css
.overlay::before {
  content: '';
  position: absolute;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(accent,0.15) 0%, transparent 70%);
  border-radius: 50%;
}
```

## Важно
- filter:blur() на pseudo-elements — OK (не на основном элементе)
- rgba(255,255,255, 0.03-0.08) — оптимальный диапазон прозрачности
- box-shadow с большим blur (40-80px) создаёт "дымку"
- НЕ использовать backdrop-filter даже "только для TOC" — qa_validator проверяет весь `<style>`

## Тэги
#pattern #glassmorphism #css #backdrop-filter-alternative
