# Troubleshooting: AI фото-редактирование

## Проблемы с результатом

### 1. Лицо стало шире/уже

**Причина:** AI применил "идеальные" пропорции

**Решение:** Добавить в промт:
```
Keep EXACT same face width and proportions.
Do NOT reshape face in any way.
```

**Пример исправления:**
- Плохо: "Improve this photo"
- Хорошо: "Brighten eyes only. Keep EXACT face shape."

---

### 2. Кожа стала пластиковой

**Причина:** AI сгладил текстуру (beauty filter)

**Решение:**
```
Keep ALL natural pores visible.
Do NOT smooth or blur skin.
Do NOT apply beauty filter.
Keep skin looking REAL, not plastic.
```

---

### 3. Глаза неестественные

**Причина:** Слишком яркие, большие или глубокие

**Решение:**
```
ONLY add SUBTLE catchlight to eyes.
Do NOT change eye SIZE or SHAPE.
Do NOT change eye position or depth.
Keep pupil size natural.
```

---

### 4. AI изменил цвет глаз

**Причина:** AI "улучшил" цвет или сделал его более насыщенным

**Признаки:**
- Карие глаза стали зелёными/голубыми
- Цвет стал ярче оригинала
- Появился нереалистичный оттенок

**Решение:**
```
Keep EXACT original eye color.
Do NOT enhance, brighten, or change iris color.
Eye color must match the original photo EXACTLY.
```

**Защитный блок для глаз:**
```
EYES - DO NOT CHANGE:
- Iris color (keep original)
- Pupil size
- Eye shape and size
- Position of eyes
- Depth/shadowing around eyes
ONLY allowed: subtle catchlight reflection
```

---

### 4.1 ⚠️ ОГРАНИЧЕНИЕ: Тонкое изменение цвета глаз НЕ РАБОТАЕТ

**Практический опыт (2026-01-30):** AI consistently не справляется с задачей "сделать глаза чуть синее/зеленее".

**Что происходит при попытке:**
- Глаза становятся **плоскими** (теряют 3D глубину)
- Исчезает **текстура** радужки
- Теряется **сложность цвета** (сине-зелёные → однотонно-синие)
- Результат выглядит как **цветные линзы** или CGI

**Протестированные промты (НЕ РАБОТАЮТ):**
```
❌ "Increase blue saturation by 10-15%"
❌ "Add 5% more blue vibrancy"
❌ "Simulate daylight on blue-green eyes"
❌ "Make the SMALLEST possible adjustment"
→ Все дают перебор и потерю естественности
```

**Почему AI не справляется:**
1. AI не умеет делать изменения <10%
2. "Больше синего" = "заменить на синий" для AI
3. Теряется сложность цвета (3-5 оттенков → 1 оттенок)

**РЕКОМЕНДАЦИЯ:**
```
Для изменения оттенка цвета глаз используй:

✅ Photoshop: Hue/Saturation → Cyans/Blues → +5-10
✅ Lightroom: HSL → Blue/Aqua → Saturation +5-10
✅ Snapseed: Selective → точка на глаз → Saturation +10

AI подходит для глаз:
✅ Добавление catchlight
✅ Осветление белков (subtle)
✅ Уменьшение красноты
✅ Общее улучшение яркости

AI НЕ подходит для:
❌ Изменения оттенка (синее/зеленее)
❌ Тонкой цветокоррекции радужки
❌ "Усиления" существующего цвета
```

**Рекомендуемый workflow:**
```
1. AI: Общая ретушь (CV, LinkedIn пресет)
2. Photoshop/Lightroom: Точечная коррекция цвета глаз
3. Финал: Объединить результаты
```

---

### 5. AI удалил веснушки/родинки

**Причина:** AI воспринял их как "дефекты" для удаления

**Признаки:**
- Веснушки исчезли или побледнели
- Родинки удалены
- Кожа стала "чище" чем в оригинале

**Решение:**
```
PRESERVE all freckles, moles, birthmarks.
These are IDENTITY features, NOT imperfections.
Do NOT remove or fade any natural skin markings.
```

**Важно:** Веснушки — часть идентичности. Добавляй в любой промт:
```
Keep ALL freckles and moles in EXACT original positions.
```

---

### 6. AI "причесал" волосы

**Причина:** AI сгладил текстуру волос, сделал их "идеальными"

**Признаки:**
- Потеряна естественная текстура
- Выбившиеся пряди исчезли
- Волосы стали "глянцевыми"
- Кудри/локоны распрямились

**Решение:**
```
HAIR PROTECTION:
Keep ALL original hair texture.
Keep flyaway hairs and loose strands.
Do NOT smooth, straighten, or "perfect" hair.
Keep natural frizz if present.
Keep original curl pattern.
```

**Для кудрявых волос:**
```
Preserve EXACT curl pattern and volume.
Do NOT reduce frizz or smooth curls.
Curly/wavy hair must look NATURAL, not styled.
```

---

### 7. AI изменил форму бровей

**Причина:** AI применил "идеальную" форму бровей

**Признаки:**
- Брови стали симметричными
- Изменилась толщина
- Изменился изгиб
- Брови "почистились"

**Решение:**
```
EYEBROWS - KEEP EXACT:
- Original shape and arch
- Thickness and density
- Natural asymmetry
- Individual hair texture
Do NOT reshape, thin, or "perfect" eyebrows.
```

---

### 8. AI осветлил/затемнил кожу

**Причина:** AI применил "стандартную" обработку или colorism bias

**Признаки:**
- Тон кожи светлее оригинала
- Тон кожи темнее оригинала
- Потеряны естественные оттенки

**Решение (КРИТИЧНО):**
```
SKIN TONE PROTECTION (CRITICAL):
Keep EXACT original skin tone.
Do NOT lighten or darken skin.
Do NOT "even out" skin tone.
Preserve natural undertones (warm/cool/neutral).
This person's skin color is PERFECT as is.
```

**Анти-colorism блок:**
```
WARNING: Changing skin tone is discrimination.
Keep the EXACT natural skin color.
Any lightening or darkening = FAILURE.
```

---

### 9. Борода/усы стали "гладкими"

**Причина:** AI сгладил текстуру растительности на лице

**Признаки:**
- Потеряна текстура отдельных волосков
- Борода выглядит "нарисованной"
- Щетина стала размытой

**Решение:**
```
FACIAL HAIR PROTECTION:
Keep ALL individual hair strands visible.
Preserve natural texture of beard/mustache/stubble.
Do NOT smooth or blur facial hair.
Keep natural patchiness if present.
Keep shadow and depth of facial hair.
```

---

### 10. Очки исказились

**Причина:** AI неправильно обработал отражения и геометрию

**Признаки:**
- Линзы искажены или исчезли
- Оправа изменила форму
- Отражения в линзах неестественные
- Глаза за линзами "поплыли"

**Решение:**
```
GLASSES PROTECTION:
Keep EXACT frame shape and position.
Preserve lens transparency and reflections.
Keep eyes behind lenses in correct position.
Do NOT remove or modify glasses in any way.
Treat glasses as FIXED part of the face.
```

**Для сложных случаев:**
```
Glasses are CRITICAL identity element.
If you cannot preserve glasses perfectly,
make NO changes to the photo.
```

---

### 11. Результат слишком отличается от оригинала

**Причина:** Слишком много изменений в одном промте

**Решение:**
1. Один промт = одно изменение
2. Добавить: "Make the SMALLEST possible change"
3. Перечислить ВСЁ что нельзя менять

---

### 12. AI изменил то, что не просили

**Причина:** Нет явных ограничений

**Решение:** Добавить полный защитный блок:
```
DO NOT CHANGE (CRITICAL):
- Face shape or width
- Cheekbone structure
- Jaw line
- Skin texture
- Eye size, shape, position
- Hair
- Expression
- Background (unless asked)
```

---

### 13. Мультяшный эффект

**Причина:** Over-processing, слишком много улучшений

**Признаки:**
- Неестественно гладкая кожа
- Слишком яркие глаза
- Идеальная симметрия
- Отсутствие текстуры

**Решение:**
```
Style: NATURAL, REALISTIC retouching only.
NOT beauty filter. NOT cartoon. NOT AI-generated look.
Keep natural imperfections.
Person must look REAL, not rendered.
```

---

### 14. Потеря деталей (волосы, текстура)

**Причина:** AI перерисовал области

**Решение:**
```
Preserve ALL fine details:
- Hair texture and individual strands
- Skin pores and texture
- Fabric patterns
- Background details
```

---

## Технические проблемы

### AI отказывается редактировать

**Причины:**
- Content policy (nudity, violence, etc.)
- Face detection failed
- Image too low quality

**Решения:**
1. Проверить фото на соответствие policy
2. Переформулировать промт без триггерных слов
3. Использовать другую платформу
4. Улучшить качество исходного фото

---

### Качество результата низкое

**Причины:**
- Низкое разрешение исходника
- Сильное сжатие
- Плохое освещение оригинала

**Решения:**
1. Использовать фото минимум 1024x1024
2. Формат PNG или высококачественный JPEG
3. Сначала улучшить техническое качество, потом редактировать

---

### Артефакты на границах

**Причина:** Проблемы при замене фона или compositing

**Признаки:**
- Неровные края вокруг объекта
- "Рваные" границы
- Остатки старого фона

**Решение:**
```
Pay special attention to edge quality.
Ensure smooth, natural transitions between subject and background.
No jagged edges or artifacts at boundaries.
Feather edges naturally.
```

**Технические советы:**
1. Используй фото с контрастным фоном
2. Избегай мелких деталей на краях (развевающиеся волосы)
3. Добавь: "Seamless edge blending required"

---

### Ореол вокруг волос

**Причина:** Плохой edge detection на мелких деталях

**Признаки:**
- Светлый/тёмный контур вокруг волос
- "Вырезанный" вид
- Неестественная граница волос и фона

**Решение:**
```
HAIR EDGE QUALITY:
No halo or fringe around hair.
Preserve individual hair strands at edges.
Natural blending of hair with background.
No color bleeding from old background.
```

**Предотвращение:**
1. Исходник с простым однородным фоном
2. Хорошее освещение контура
3. Добавь: "Preserve wispy hair edges naturally"

---

### Потеря резкости

**Причина:** AI "размазал" изображение при обработке

**Признаки:**
- Фото менее чёткое чем оригинал
- Потеря мелких деталей
- "Мягкий" фокус

**Решение:**
```
Maintain ORIGINAL sharpness level.
Do NOT blur or soften the image.
Keep all details as crisp as original.
Output resolution must match input.
```

**Профилактика:**
1. Проверь разрешение выхода (должно = входу)
2. Избегай платформ с сильной компрессией
3. Добавь: "Preserve original image sharpness"

---

### Цветовые полосы (Banding)

**Причина:** Потеря цветовой глубины при обработке

**Признаки:**
- Полосы на градиентах (небо, кожа)
- "Ступеньки" цвета вместо плавных переходов
- Особенно заметно на однотонных областях

**Решение:**
```
Preserve smooth color gradients.
No banding or color stepping.
Maintain original color depth.
```

**Технические решения:**
1. Работай с 16-bit изображениями если возможно
2. Избегай сильных цветовых изменений
3. Финальный экспорт в высоком качестве

---

### Несогласованность серии (Batch проблемы)

**Причина:** Каждое фото обработано по-разному

**Признаки:**
- Разный цветовой баланс в серии
- Разная степень ретуши
- Несовместимые стили

**Решение:**
```
BATCH CONSISTENCY:
Apply IDENTICAL processing to all images in series.
Match color grading across all photos.
Same level of retouching for each image.
Consistent style throughout the set.
```

**Процесс для серий:**
1. Сначала обработай одно фото идеально
2. Сохрани точный промт
3. Применяй ИДЕНТИЧНЫЙ промт ко всем
4. Добавь: "Match style of reference image exactly"

---

## Платформо-специфичные проблемы

### Gemini
- **Проблема:** Слишком консервативен
- **Решение:** Быть более конкретным в запросе
- **Совет:** Детально описывай желаемый результат

### DALL-E
- **Проблема:** Перерисовывает слишком много
- **Решение:** Добавить "smallest possible change", усилить защиту
- **Параметры:** Не меняй настройки по умолчанию

### Midjourney
- **Проблема:** Склонен к стилизации
- **Решение:** Использовать `--style raw`, `--iw 2`
- **Совет:** `--iw 2` увеличивает вес исходного изображения

### Flux

**Проблема:** Склонен к художественной стилизации

**Признаки:**
- Фото становится "артовым"
- Добавляется нежелательный стиль
- Теряется фотореалистичность

**Решение:**
```
Style: PHOTOREALISTIC only.
This is a PHOTOGRAPH, not art.
No stylization, no artistic interpretation.
Output must look like an unedited photo.
```

**Рекомендуемые параметры:**
- Guidance scale: 3.5-4.0 (не выше!)
- Steps: 28-35
- Добавь: "raw photo, unprocessed look"

### Stable Diffusion

**Проблема:** Требует тонкой настройки CFG

**Признаки:**
- Слишком "креативный" результат (высокий CFG)
- Размытый результат (низкий CFG)
- Игнорирует защитные инструкции

**Решение:**
```
Follow prompt EXACTLY.
Do not interpret creatively.
Literal execution only.
```

**Рекомендуемые параметры:**
- CFG Scale: 5-7 (для ретуши)
- Denoising strength: 0.2-0.4 (минимальные изменения)
- Sampler: DPM++ 2M Karras
- Добавь negative prompt: "cartoon, painting, artistic, stylized"

### Leonardo.ai

**Проблема:** Агрессивное улучшение по умолчанию

**Решение:**
```
MINIMAL processing.
Do NOT auto-enhance.
Do NOT apply beauty filters.
Keep original photo aesthetic.
```

**Настройки:**
- Отключи "Photo Real" если не нужен
- Guidance: 5-6
- Используй "Raw Mode" если доступен

---

## Диагностика: Дерево решений

Используй эту схему для быстрой диагностики проблем:

```
Результат плохой?
│
├── Лицо изменилось?
│   ├── Да → Усилить защитный блок
│   │   ├── Добавь: "Keep EXACT facial proportions"
│   │   ├── Перечисли ВСЕ части лица для защиты
│   │   └── Используй: "If face changes, make NO edit"
│   └── Нет → Проверь другие проблемы
│
├── Кожа пластиковая?
│   ├── Да → Добавить текстурную защиту
│   │   ├── "Keep ALL visible pores"
│   │   ├── "Do NOT smooth skin"
│   │   └── "NATURAL skin texture required"
│   └── Нет → Проверь другие проблемы
│
├── Слишком ярко/насыщенно?
│   ├── Да → Уменьшить интенсивность
│   │   ├── "SUBTLE changes only"
│   │   ├── "Natural, not enhanced look"
│   │   └── Уменьши denoising/strength
│   └── Нет → Проверь другие проблемы
│
├── Артефакты/глитчи?
│   ├── Да → Упростить изменения
│   │   ├── Один промт = одна задача
│   │   ├── Уменьши параметры обработки
│   │   └── Попробуй другую платформу
│   └── Нет → Проверь качество исходника
│
├── Цвета изменились?
│   ├── Да → Добавить цветовую защиту
│   │   ├── "Keep EXACT original colors"
│   │   ├── "No color correction"
│   │   └── "Preserve original white balance"
│   └── Нет → Проверь другие проблемы
│
└── Всё ещё плохо?
    └── Смотри раздел "Экстренные решения"
```

### Быстрая диагностика по симптомам

| Симптом | Вероятная причина | Быстрое решение |
|---------|-------------------|-----------------|
| Мыльная кожа | Beauty filter | "Keep pores visible" |
| Большие глаза | Face reshape | "EXACT eye size" |
| Светлая кожа | Colorism bias | "EXACT skin tone" |
| Гладкие волосы | Texture loss | "Keep hair texture" |
| Нет веснушек | Blemish removal | "Keep all freckles" |
| Ровные брови | Symmetry bias | "Keep brow asymmetry" |
| Ореол | Edge detection | "No halo around edges" |
| Размытие | Over-processing | "Keep original sharpness" |
| Плоские/неестественные глаза при изменении цвета | AI ограничение | **Используй Photoshop/Lightroom** |

---

## Экстренные решения

### Когда ничего не работает

**Уровень 1: Минимальный промт**

Убери всё лишнее, оставь только одно изменение:
```
ONLY adjust brightness by +10%.
Change NOTHING else.
If ANY other change would occur, make NO edit.
```

**Уровень 2: Другая платформа**

Каждая платформа имеет свои сильные стороны:

| Задача | Лучшая платформа |
|--------|------------------|
| Сохранение лица | Gemini (консервативен) |
| Точечные правки | DALL-E (с защитой) |
| Фотореализм | Flux (низкий guidance) |
| Контроль | Stable Diffusion (настраиваемый) |

**Уровень 3: Традиционные инструменты**

Иногда AI — не лучший выбор:

| Задача | Лучший инструмент |
|--------|-------------------|
| Точечная ретушь | Photoshop, Snapseed |
| Цветокоррекция | Lightroom |
| Удаление фона | remove.bg |
| Upscaling | Topaz Gigapixel, Remini |
| Удаление объектов | Photoshop Content-Aware |
| Коррекция освещения | Lightroom, Capture One |

**Уровень 4: Переснять фото**

Когда исходник слишком проблемный:

- Плохое освещение → Лучше переснять
- Размытый фокус → AI не исправит
- Слишком низкое разрешение → Ограничения качества
- Сложный фон для замены → Снять на чистом фоне

---

## Универсальный фикс

Если ничего не помогает, используй этот блок:
```
Make the SMALLEST possible change.
Keep this person looking EXACTLY like themselves.
Preserve EXACT facial proportions.
Keep ALL natural skin texture with visible pores.
Do NOT smooth, reshape, or beautify.
If you cannot do this without altering their appearance,
make NO changes at all.
```

---

## Чеклист перед отправкой промта

Проверь свой промт:

- [ ] Указана ОДНА конкретная задача
- [ ] Есть защитный блок DO NOT CHANGE
- [ ] Перечислены критические элементы для защиты
- [ ] Указан желаемый стиль (NATURAL, REALISTIC)
- [ ] Есть fallback: "If cannot preserve, make no changes"
- [ ] Нет конфликтующих инструкций
- [ ] Параметры платформы настроены правильно

---

## Когда отказаться от AI

Иногда лучше использовать традиционные инструменты:

| Задача | Лучший инструмент |
|--------|-------------------|
| Точечная ретушь | Photoshop, Snapseed |
| Цветокоррекция | Lightroom |
| Удаление фона | remove.bg |
| Upscaling | Topaz, Remini |

### Признаки что AI не подходит:

1. **Нужна 100% точность** — AI всегда вносит небольшие изменения
2. **Юридические/документальные фото** — Никаких изменений лица
3. **Серия из 50+ фото** — Сложно обеспечить консистентность
4. **Клиент очень требователен** — Ручная ретушь надёжнее
5. **Исходник плохого качества** — AI усилит проблемы

---

## Полезные ресурсы

- **cheatsheet.md** — Быстрые шаблоны промтов
- **faq.md** — Ответы на частые вопросы
- **SKILL.md** — Полное руководство по промтам
