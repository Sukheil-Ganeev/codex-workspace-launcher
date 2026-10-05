# 11+ Use Cases с готовыми решениями

> Подробные руководства по сценариям использования с готовыми промтами.
> Краткий список use cases — в SKILL.md.

---

## USE CASE 1: CV/LinkedIn

**Цель:** Профессионально и располагающе, оставаясь собой.

**Допустимо:**
- Выровнять тон кожи, убрать временные дефекты
- Улучшить освещение и контраст
- Слегка осветлить тени под глазами
- Нейтральный фон

**Недопустимо:**
- Менять форму лица или черты
- Убирать все морщины (показывают опыт)
- Сильное сглаживание кожи
- Значительное омоложение

**Готовый промт для CV:**
```
Professional headshot enhancement for CV/LinkedIn.

APPLY:
- Professional lighting balance
- Subtle skin tone evening (keep all texture)
- Minor under-eye shadow reduction (30% max)
- Remove only temporary blemishes

PRESERVE:
- Exact facial structure and proportions
- Natural skin texture with visible pores
- Age-appropriate wrinkles and expression lines
- All identifying features

STANDARD: Must be recognizable at job interview.
STYLE: Professional, trustworthy, competent.
```

---

## USE CASE 2: ПАСПОРТ/ВИЗА

**СТРОГОЕ ОГРАНИЧЕНИЕ:** Только техническое улучшение качества изображения!

**Допустимо:**
- Баланс белого
- Коррекция экспозиции
- Шумоподавление
- Удаление красных глаз (артефакт вспышки)
- Коррекция фона

**КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:**
- Любые изменения лица
- Ретушь кожи
- Удаление родинок/шрамов
- Сглаживание
- Изменение цвета

**Риски:**
- Отказ в документе
- Проблемы на границе
- Юридические последствия

**Готовый промт:**
```
PASSPORT PHOTO - TECHNICAL ONLY

Allowed:
- White balance correction
- Exposure adjustment
- Noise reduction
- Background uniformity

ABSOLUTELY FORBIDDEN:
- ANY modification to face
- ANY skin changes
- ANY feature alterations

Person must look 100% identical.
Only image QUALITY improves, not appearance.
```

---

## USE CASE 3: Instagram/TikTok

**Тренд 2025-2026:** "Enhanced natural" - улучшено, но естественно.

**Что работает:**
- Здоровый glow
- Естественная текстура кожи (видимые поры - это тренд!)
- Тёплые тона
- "Clean girl" эстетика

**Что устарело:**
- Пластиковая кожа
- Сильное сглаживание
- Явные фильтры
- "Инста-лица"

**Готовый промт:**
```
Instagram photo - modern clean aesthetic.

APPLY:
- Healthy, subtle skin glow
- Natural-looking warmth
- Eye brightening (catchlight only)
- Soft flattering light

KEEP (trendy in 2025-2026):
- Visible skin texture and pores
- Freckles (enhance if present!)
- Natural skin undertones
- Authentic appearance

AVOID (dated):
- Poreless skin
- Over-bright eyes
- Uniform perfect complexion

MUST pass video call test - look same on Stories.
```

---

## USE CASE 4: Dating Apps

**Главное правило:** На свидании должны сказать "Ты выглядишь как на фото!"

**Статистика:**
- Сильная ретушь = -22% matches (подсознательно чувствуют)
- Честные фото = +35% конверсия в реальные даты
- 89% считают несоответствие фото "красным флагом"

**Допустимо:**
- Хорошее освещение
- Убрать то, что пройдёт к свиданию (прыщ)
- Лёгкое выравнивание тона

**Катастрофа:**
- Сужение лица
- Увеличение глаз/губ
- Изменение носа
- Значительное похудение

**Готовый промт:**
```
Dating app photo - authentically attractive.

GOAL: Look like myself on my BEST day.
Date should say "You look just like your photos!"

APPLY:
- Flattering warm lighting
- Remove temporary blemishes only
- Healthy even skin (keep texture!)
- Bright engaged eyes (no size change)

NEVER CHANGE:
- Face shape
- Any feature sizes
- Body proportions
- Permanent features (moles are unique!)

AUTHENTICITY > ATTRACTIVENESS
Must pass first date recognition test.
```

---

## USE CASE 5: E-commerce

**Принцип:** Модель не должна отвлекать от товара.

**Приоритеты:**
1. Товар - главный объект
2. Правдивость - покупатель получит то, что видит
3. Профессионализм без излишеств

**Допустимо:**
- Убрать временные дефекты на модели
- Профессиональное освещение
- Чистый фон

**Запрещено:**
- Изменять форму тела модели (вводит в заблуждение о посадке)
- Менять цвет товара
- Делать модель "слишком идеальной"

**Готовый промт:**
```
E-commerce catalog photo retouching.

MODEL:
- Clean professional appearance
- Remove temporary blemishes
- Natural skin (minimal smoothing)
- Neat hair

PRODUCT (PRIORITY):
- Color accurate - DO NOT alter
- Show real fit honestly
- Proper drape visible

BACKGROUND:
- Pure white (255,255,255) for marketplace
- Seamless edges

STRICTLY FORBIDDEN:
- Body shape modification
- Product color changes
- Heavy beauty retouching
```

---

## USE CASE 6: ДЕТСКИЕ ФОТО

**Главное правило:** Дети совершенны как есть. Минимальное вмешательство!

**Допустимо (только):**
- Техническая коррекция (свет, цвет, экспозиция)
- Удаление красных глаз от вспышки
- Убрать свежую царапину/укус комара

**КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:**
- Любое "улучшение" внешности
- Сглаживание кожи
- Отбеливание зубов
- Изменение глаз

**Готовый промт:**
```
CHILDREN'S PHOTO - PRESERVATION PRIORITY

Technical adjustments only:
- Lighting balance
- Color accuracy
- Exposure correction

ABSOLUTE PROTECTION:
- Child's appearance unchanged
- Natural imperfections preserved
- Authentic childhood documented

These "imperfections" become precious memories.
```

---

## USE CASE 7: ГРУППОВЫЕ ФОТО

**Принцип:** Консистентность важнее индивидуального совершенства.

**Допустимо:**
- Одинаковая обработка для всех
- Общая цветокоррекция
- Базовое улучшение освещения

**Недопустимо:**
- "Геройская" ретушь одного человека
- Разная интенсивность для разных людей
- Унификация тонов кожи

**Готовый промт:**
```
GROUP PHOTO - EQUAL TREATMENT

Apply to ALL equally:
- Lighting balance
- Basic blemish removal
- Skin tone evening (preserve individual tones!)

CONSISTENCY RULES:
- Same intensity for every person
- Respect different skin tones
- Age-appropriate for each
- No one stands out as "more edited"
```

---

## USE CASE 8: ПОЖИЛЫЕ ЛЮДИ

**Принцип:** Возраст - это опыт и мудрость, не проблема.

**Допустимо:**
- Уменьшить усталость (тени под глазами)
- Выровнять освещение
- Убрать временные покраснения

**Недопустимо:**
- Убирать морщины (они показывают жизненный опыт)
- Омолаживать
- Сглаживать характерные черты

**Готовый промт:**
```
SENIOR PORTRAIT - DIGNITY AND CHARACTER

Apply:
- Reduce fatigue indicators only
- Even, flattering lighting
- Healthy skin tone

PRESERVE (CRITICAL):
- ALL wrinkles and expression lines (wisdom!)
- Character features
- Natural age appearance
- Distinguished look

Goal: Well-rested for their age, not younger.
Experience is an ASSET, not a flaw.
```

---

## USE CASE 9: СВАДЕБНЫЕ ФОТО

**Принцип:** Вечная память, которая должна соответствовать видео и реальности.

**Допустимо:**
- Убрать усталость от долгого дня
- Выровнять освещение в сложных условиях
- Освежить макияж/внешний вид

**Недопустимо:**
- Сильная ретушь на фоне необработанных гостей
- Изменения, которые будут противоречить видео
- Датированные фильтры

**Готовый промт:**
```
WEDDING PHOTO - TIMELESS ELEGANCE

Apply:
- Remove event fatigue
- Balance challenging venue lighting
- Soft romantic glow (keep texture!)
- Refresh appearance naturally

CONSIDERATIONS:
- Video exists - must match
- Guests have phone photos - consistency
- Family will view for decades
- Printed in albums

STYLE: Timeless, not trendy. Real, not perfect.
```

---

## USE CASE 10: YOUTUBE/ВИДЕО THUMBNAILS

**Принцип:** Должен соответствовать тому, как человек выглядит в видео.

**Допустимо:**
- Улучшить освещение и контраст
- Сделать более "кликабельным"
- Убрать временные дефекты

**Недопустимо:**
- Сильная ретушь (видео покажет правду)
- Изменение пропорций лица
- Нереалистичные улучшения

**Готовый промт:**
```
YOUTUBE THUMBNAIL - VIDEO-CONSISTENT

Apply:
- Enhanced lighting and contrast
- Remove temporary blemishes
- Eye-catching but honest

CRITICAL:
- Must match how creator looks in video
- Viewers will compare immediately
- Authenticity builds trust

Style: Engaging but real.
```

---

## USE CASE 11: КОНФЕРЕНЦИИ/СПИКЕРЫ

**Принцип:** Авторитет и доверие, профессиональное качество.

**Допустимо:**
- Студийное качество освещения
- Профессиональная подача
- Чистый фон

**Недопустимо:**
- Чрезмерная ретушь (спикера увидят лично)
- Молодить (опыт = credibility)
- Гламурный вид

**Готовый промт:**
```
SPEAKER/CONFERENCE HEADSHOT

Apply:
- Professional studio lighting quality
- Clean, appropriate background
- Polished but authentic appearance

PRESERVE:
- All character and experience markers
- Professional credibility
- Age-appropriate appearance
- Recognition by attendees

Goal: Expert who looks camera-ready, not model.
```
