# EXP-075: Трансформация текстовых слайдов в визуальные

## Проблема
Слайды с большим объёмом текста (Q&A, списки, описания) выглядят как "стена текста". Мелкий шрифт (13-14px), однообразная структура, пустое пространство.

## Паттерн трансформации

### Шаг 1: Анализ контента
Определить тип информации в тексте:
- **Числа/метрики** → metric-card
- **Да/Нет** → green/red banner
- **Сравнение** → side-by-side cards или styled-table
- **Список** → feature-list или icon-cards
- **Предупреждение** → highlight-box с цветной рамкой
- **Категории** → tag strip
- **Цены** → price rows с colored tags
- **Статусы** → status table с colored tags

### Шаг 2: Layout
- 1-2 элемента → full-width card
- 3-4 элемента → two-columns grid
- 5+ элементов → grid с compact cards
- Один крупный + несколько мелких → full-width top + two-columns bottom

### Шаг 3: Визуальное обогащение
```
Текст → Card с colored left-border
Число → Metric-card с gradient text
Список → Feature-list с checkmarks
Статус → Tag (green/yellow/red)
Предупреждение → Highlight-box с red border
Совет → Highlight-box с green border
Цена → Price row: label + tag
```

### Шаг 4: Увеличение размеров
- Questions: 17-18px, font-weight:600, accent color
- Answers: 15-16px (was 13-14px)
- Tags: 12-13px, uppercase, letter-spacing
- Labels: 11-12px, muted color

## Пример: Q&A слайд "Виза"

**До:**
```html
<div class="qa-item">
  <div class="qa-q">Нужна ли виза?</div>
  <div class="qa-a">Нет, для граждан РФ безвизовый въезд на 90 дней</div>
</div>
```

**После:**
```html
<div class="card" style="padding:20px; border-left:3px solid var(--accent-1);">
  <h3 style="font-size:17px; color:var(--accent-1); margin-bottom:12px;">Нужна ли виза?</h3>
  <div style="display:flex; gap:16px; margin-top:8px;">
    <div class="metric-card" style="padding:16px; flex:1;">
      <div class="metric-value" style="font-size:28px; color:#10B981;">90 дней</div>
      <div class="metric-label">РФ / BY</div>
    </div>
    <div class="metric-card" style="padding:16px; flex:1;">
      <div class="metric-value" style="font-size:28px; color:#3B82F6;">30 дней</div>
      <div class="metric-label">KZ / UZ</div>
    </div>
  </div>
</div>
```

## Цветовая кодировка
| Цвет | Значение | CSS |
|------|----------|-----|
| Green (#10B981) | Да / OK / Разрешено | .tag-green, border-left:3px solid |
| Red (#EF4444) | Нет / Запрещено / Опасно | .tag-red, background rgba |
| Yellow (#F59E0B) | Внимание / Ограничено | .tag-yellow |
| Blue (#3B82F6) | Информация / Нейтрально | .tag-blue |
| Purple (#8B5CF6) | Особые условия | .tag-purple |

## Устранение пустого пространства
1. Увеличить font-size на 2-4px
2. Добавить metric-cards с числами
3. Разбить на 2 колонки вместо 1
4. Добавить tag strip сверху слайда
5. Использовать icon-cards с крупными иконками

## Тэги
#pattern #text-to-visual #layout #transformation #design
