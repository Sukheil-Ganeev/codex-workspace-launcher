# EXP-073: Bar Chart с уникальными цветами через nth-child

## Проблема
Все столбцы bar chart имели одинаковый gradient (accent-1 → accent-2). Визуально скучно и не информативно — цвет не помогает различать категории.

## Решение: nth-child цветовая палитра

```css
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 200px;
  padding: 20px 0 36px; /* 36px bottom для labels */
}

.bar-chart .bar {
  flex: 1;
  border-radius: 6px 6px 0 0;
  position: relative;
  min-width: 40px;
}

/* 6 уникальных цветов */
.bar-chart .bar:nth-child(1) { background: linear-gradient(to top, #F59E0B, #FBBF24); } /* amber */
.bar-chart .bar:nth-child(2) { background: linear-gradient(to top, #3B82F6, #60A5FA); } /* blue */
.bar-chart .bar:nth-child(3) { background: linear-gradient(to top, #8B5CF6, #A78BFA); } /* purple */
.bar-chart .bar:nth-child(4) { background: linear-gradient(to top, #10B981, #34D399); } /* green */
.bar-chart .bar:nth-child(5) { background: linear-gradient(to top, #EF4444, #F87171); } /* red */
.bar-chart .bar:nth-child(6) { background: linear-gradient(to top, #06B6D4, #22D3EE); } /* cyan */

.bar-chart .bar-value {
  position: absolute;
  top: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-2);
}

.bar-chart .bar-label {
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
}
```

## Важные детали
1. padding-bottom на .bar-chart должен быть >= 36px для размещения labels
2. bar-label позиционируется через bottom:-24px (НЕ через translateY(100%) — он ненадёжен)
3. Убирать конфликтующие inline styles из HTML (height, align-items, padding-bottom)
4. min-width:40px предотвращает слишком узкие бары
5. Цветовая палитра подобрана для тёмных тем (яркие, но не кислотные)

## Расширение на >6 баров
Добавить :nth-child(7), (8)... или использовать :nth-child(n+7) для дефолтного цвета.

## Тэги
#pattern #bar-chart #colors #nth-child #css
