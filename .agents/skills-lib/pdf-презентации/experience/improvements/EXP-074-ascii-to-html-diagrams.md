# EXP-074: Замена ASCII-арт диаграмм на HTML/CSS

## Проблема
Слайды с техническими диаграммами использовали ASCII-арт в `<pre>` блоках:
```
┌──────────────────────────────┐
│  POST-FORM-HANDLER           │
│  1. Определить service_type  │
└──────────────────┬───────────┘
                   ▼
```
Это выглядит непрофессионально и не масштабируется.

## Решение: 3-слойная HTML-диаграмма

### Слой 1: Блок с тегами (Forms)
```html
<div class="card" style="border:2px solid rgba(245,158,11,0.35); padding:20px; text-align:center;">
  <h3 style="font-size:16px; margin-bottom:12px;">ФОРМЫ (11 шт)</h3>
  <div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:center;">
    <span class="tag tag-yellow">FORM-GT</span>
    <span class="tag tag-yellow">FORM-PT</span>
    <!-- ... -->
  </div>
</div>
```

### CSS-стрелка между слоями
```html
<div style="text-align:center; font-size:28px; color:var(--accent-1); margin:8px 0;">&#9660;</div>
```
Unicode &#9660; (▼) — простой, надёжный, масштабируемый.

### Слой 2: Обработчик (grid)
```html
<div class="card" style="border:2px solid rgba(52,211,153,0.35); padding:20px;">
  <h3>POST-FORM-HANDLER</h3>
  <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:12px;">
    <div class="card" style="padding:12px; text-align:center;">
      <div style="font-size:20px; font-weight:700; color:var(--accent-1);">1</div>
      <p>service_type</p>
    </div>
    <!-- шаги 2-4 -->
  </div>
</div>
```

### Слой 3: Flow статусов (горизонтальный)
```html
<div style="display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap;">
  <span class="tag tag-yellow">990 new</span>
  <span style="color:var(--text-muted);">&#10132;</span> <!-- → arrow -->
  <span class="tag tag-blue">991 processing</span>
  <span style="color:var(--text-muted);">&#10132;</span>
  <!-- ... -->
</div>
```

## Для ветвлений (fork)
```html
<div style="display:flex; gap:24px; justify-content:center; margin-top:8px;">
  <div><!-- ветка 1 --></div>
  <div><!-- ветка 2 --></div>
</div>
```

## Ключевые приёмы
1. `.card` + colored border = визуальный блок
2. `.tag` + color variants = статусные элементы
3. Unicode arrows (&#9660; &#10132; &#8595;) = коннекторы
4. CSS grid = равномерное распределение шагов
5. flex-wrap = адаптивность при большом количестве элементов
6. Inline styles для уникального позиционирования, CSS classes для общего вида

## Когда использовать
- Архитектурные диаграммы
- Flow-схемы процессов
- Статусные машины
- Любые блок-схемы

## Тэги
#improvement #diagrams #ascii-replacement #html #css #architecture
