# EXP-072: CSS Component Improvements (VIP-DXB)

## Контекст
Массовое улучшение CSS-компонентов в 10 презентациях VIP-DXB. Каждый компонент получил более профессиональный вид с использованием современных CSS-техник.

## Компоненты и улучшения

### 1. Карточки (.card)
**До:** Плоский фон, простая рамка
**После:**
```css
.card {
  background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-elevated, var(--bg-card)) 100%);
  border-radius: 14-18px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 10px 20px rgba(0,0,0,0.15);
}
/* Top accent glow line */
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 20%; right: 20%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-1), var(--accent-2), transparent);
}
```

### 2. Таблицы (.styled-table)
**До:** Простые линии, одинаковый фон
**После:**
```css
.styled-table {
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 12-16px;
  overflow: hidden;
}
.styled-table thead th {
  background: linear-gradient(135deg, rgba(accent,0.15), rgba(accent,0.08));
  text-transform: uppercase;
  letter-spacing: 0.5-1.5px;
  font-size: 12-13px;
  border-bottom: 2px solid rgba(accent,0.4);
}
.styled-table tbody tr:nth-child(even) {
  background: rgba(255,255,255,0.02);
}
```
**Rounded corners техника:** border-collapse:separate + border-spacing:0 + border-radius + overflow:hidden

### 3. Code Blocks (.code-block)
**До:** Простой тёмный фон
**После:**
```css
.code-block {
  border-radius: 14px;
  border-left: 3px solid var(--accent-1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}
```

### 4. Metric Cards (.metric-card)
**До:** Простое число + текст
**После:**
```css
.metric-card {
  background: linear-gradient(135deg, var(--bg-card), var(--bg-slide));
  border-top: 3px solid transparent;
  border-image: linear-gradient(90deg, var(--accent-1), var(--accent-2)) 1;
}
.metric-value {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.metric-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
```

### 5. Section Labels (.section-label)
**До:** Обычный текст
**После:**
```css
.section-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 3.5px;
  text-transform: uppercase;
}
.section-label::before {
  content: '';
  width: 4px; height: 20px;
  background: linear-gradient(180deg, var(--accent-1), var(--accent-2));
  border-radius: 2px;
}
```

### 6. Highlight Boxes (.highlight-box)
```css
.highlight-box {
  background: linear-gradient(135deg, rgba(accent,0.06), rgba(accent,0.02));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}
```

### 7. Типографика
```css
h1 { font-weight: 800; letter-spacing: -0.5px; }
h2 { font-weight: 700; letter-spacing: -0.3px; }
h3 { font-weight: 600; letter-spacing: -0.2px; }
.slide-number { font-size: 13px; opacity: 0.5; letter-spacing: 0.5px; font-variant-numeric: tabular-nums; }
.gradient-top { opacity: 0.9; }
```

## Ключевые принципы
1. Gradient backgrounds вместо flat colors
2. Multi-layer box-shadow для глубины (3 слоя)
3. Top accent lines через ::before
4. Gradient text через background-clip для чисел/заголовков
5. Uppercase + letter-spacing для labels/headers
6. border-collapse:separate для rounded tables
7. Left accent border для code blocks
8. tabular-nums для чисел (одинаковая ширина цифр)

## Тэги
#improvement #css #components #cards #tables #typography
