# FAQ - Частые вопросы

## Общие вопросы

### Почему AI меняет больше чем я прошу?

**Причина:** AI-модели обучены на "улучшенных" фото, где часто применялись beauty-фильтры. Без явных ограничений AI пытается сделать фото "красивее" по своему пониманию.

**Решение:** Всегда добавлять блок `DO NOT CHANGE` с конкретными ограничениями.

---

### Какую платформу лучше использовать?

| Платформа | Лучше для | Особенности |
|-----------|-----------|-------------|
| **Gemini** | Фото людей | Хорошо понимает ограничения, рекомендуется |
| **DALL-E** | Простые правки | Склонен к большим изменениям, нужны строгие ограничения |
| **Midjourney** | Художественная обработка | Менее подходит для естественного ретуша |

**Рекомендация:** Начни с Gemini для фото людей.

---

### Промт не работает, AI все равно меняет лицо

**Что попробовать:**

1. **Усилить защиту** - добавь "CRITICAL" и "ABSOLUTE" к ограничениям
2. **Упростить запрос** - попроси только одно изменение
3. **Использовать fallback** - добавь "If you cannot do this without changing face, make NO changes"
4. **Сменить платформу** - попробуй другой AI
5. **Минимальный промт** - используй ультра-безопасный промт только для яркости/контраста

---

### Как сохранить морщины при улучшении кожи?

Добавь в защитный блок:
```
PRESERVE AGE-APPROPRIATE FEATURES:
- Keep all wrinkles and expression lines
- Do NOT make the person look younger
- These are character features, not flaws
```

---

### Можно ли редактировать фото для паспорта?

**Осторожно!** Для официальных документов допустимы только:
- Коррекция яркости/контраста
- Баланс цвета
- Улучшение резкости

**Нельзя:**
- Менять черты лица
- Сглаживать кожу
- Убирать дефекты

Используй промт "Для паспорта/документов" из библиотеки.

---

## Этика и ограничения

### Можно ли редактировать детские фото?

**Ответ:** Только техническое улучшение без изменения внешности.

**Допустимо:**
- Коррекция освещения и экспозиции
- Баланс белого
- Удаление красных глаз от вспышки
- Кадрирование

**Категорически нельзя:**
- Любое изменение черт лица
- Сглаживание кожи (детская кожа и так гладкая)
- Изменение цвета глаз/волос
- Beauty-обработка

**Промт для детских фото:**
```
CHILD PHOTO - TECHNICAL CORRECTIONS ONLY:
- Adjust exposure and white balance
- Remove red-eye from flash
- Minor color correction

ABSOLUTE RESTRICTIONS:
- ZERO changes to any facial features
- NO skin smoothing of any kind
- NO beauty enhancements
- This is a child - appearance must remain completely untouched
```

---

### Как работать с фото пожилых людей?

**Главный принцип:** Морщины - это история жизни, не дефекты.

**Правильный подход:**
- Улучшай освещение, но сохраняй все морщины
- Можно слегка осветлить глубокие тени
- Не делай человека моложе

**Что добавить в промт:**
```
RESPECT AGE AND CHARACTER:
- ALL wrinkles must remain visible and unchanged
- Expression lines are character features, NOT flaws
- Do NOT make this person look younger
- Skin texture including age spots should remain natural
- This person has earned every line on their face - preserve them
```

**Типичная ошибка:** AI склонен автоматически "омолаживать" - всегда добавляй явную защиту возрастных особенностей.

---

### Можно ли "похудеть" человека на фото?

**Ответ:** Морфинг (изменение формы тела) - неэтично и не рекомендуется.

**Что допустимо:**
- Работа со светотенью для более выгодного освещения
- Небольшая коррекция позы через кадрирование
- Улучшение осанки через свет

**Что недопустимо:**
- Сужение талии, лица, рук
- Удаление "лишнего" веса
- Изменение пропорций тела

**Почему это важно:**
- Создает нереалистичные ожидания
- Может навредить самооценке человека
- Это уже не редактирование, а фальсификация

**Если клиент настаивает:**
```
I can only work with lighting and shadows to create more flattering results.
I do not perform body morphing or reshaping.
```

---

### Этично ли отбеливать зубы на фото?

**Ответ:** Умеренно - да, "голливудская улыбка" - нет.

**Допустимо:**
- Убрать желтый/серый оттенок от освещения
- Выровнять цвет до естественного белого
- Коррекция на 10-20%

**Недопустимо:**
- Делать зубы ярче белого листа бумаги
- Неестественно белые зубы на фоне естественного лица
- "Голливудский" уровень отбеливания

**Промт для умеренного отбеливания:**
```
Teeth adjustment:
- Neutralize any yellow/gray color cast from lighting
- Result should look like naturally healthy teeth
- NOT bright white or artificial looking
- Subtle improvement, not dramatic change (max 15% brighter)
```

---

## Технические вопросы

### Какое разрешение нужно для AI-обработки?

**Минимум:** 1024x1024 пикселей

**Рекомендуется:** 2048x2048 или выше

**Почему это важно:**
- AI лучше понимает детали на крупных изображениях
- Меньше риск артефактов
- Точнее работают ограничения

**Таблица качества:**

| Разрешение | Качество результата | Рекомендация |
|------------|---------------------|--------------|
| < 512px | Плохое | Не использовать |
| 512-1024px | Приемлемое | Только для тестов |
| 1024-2048px | Хорошее | Рекомендуется |
| > 2048px | Отличное | Идеально |

**Совет:** Если фото маленькое, сначала увеличь его с помощью upscaling, потом редактируй.

---

### Какой формат лучше: JPEG или PNG?

**PNG - для качества:**
- Без потери качества при сохранении
- Поддерживает прозрачность
- Лучше для промежуточных этапов

**JPEG - для финального результата:**
- Меньший размер файла
- Достаточно для веба и соцсетей
- Используй качество 90%+

**Рекомендация:**
1. Исходник держи в PNG или RAW
2. Для AI-обработки загружай PNG
3. Финальный результат сохраняй в нужном формате для использования

**Избегай:**
- Многократного пересохранения в JPEG (каждый раз теряется качество)
- JPEG для фото с текстом или графикой
- Низкого качества сжатия (< 80%)

---

### Как увеличить маленькое фото для обработки?

**Инструменты для upscaling:**
- Topaz Gigapixel AI
- Real-ESRGAN (бесплатно)
- Waifu2x (для аниме-стиля)
- Встроенные инструменты в Photoshop

**Важные предупреждения:**
- Upscaling добавляет детали, которых нет в оригинале
- AI "додумывает" текстуры - это может изменить внешность
- Маленькое фото всегда даст худший результат, чем оригинал высокого разрешения

**Порядок действий:**
1. Увеличь фото в 2-4 раза
2. Проверь, не изменились ли черты лица
3. Только потом отправляй на AI-обработку
4. В промте укажи, что это upscaled изображение

**Промт для upscaled фото:**
```
Note: This is an upscaled image. Be extra careful to:
- Not add details that weren't in original
- Preserve the exact facial features
- Any texture should match original quality level
```

---

### Можно ли обработать несколько фото одинаково?

**Да, это называется batch processing.**

**Подход:**
1. Создай единый промт для серии
2. Добавь требование консистентности
3. Обрабатывай по одному, используя тот же промт

**Промт для серии:**
```
BATCH PROCESSING - CONSISTENCY REQUIRED:
This is part of a photo series. Apply IDENTICAL adjustments to all images:
- Same exposure correction value
- Same color temperature
- Same contrast settings
- Result should look like one photo session

DO NOT vary the editing style between images.
```

**Для корпоративных серий:**
```
CORPORATE PHOTO SERIES:
All photos must have:
- Identical background brightness
- Same skin tone rendering
- Consistent shadow depth
- Uniform overall style

This is for company website - consistency is critical.
```

---

## Платформы и инструменты

### Чем Flux отличается от других платформ?

**Flux** - относительно новая платформа с особенностями:

**Преимущества:**
- Хорошо следует инструкциям
- Меньше склонен к "улучшательству"
- Быстрая генерация

**Особенности:**
- Может иначе интерпретировать промты
- Требует адаптации стандартных промтов
- Активно развивается

**Адаптация промтов для Flux:**
- Будь более прямолинеен
- Меньше "поэтических" описаний
- Больше конкретных инструкций

**Пример адаптации:**
```
Стандартный: "Gently enhance the catchlights in eyes"
Для Flux: "Add small white reflection point in each eye pupil, size 2-3 pixels"
```

---

### Какая платформа лучше для групповых фото?

**Рекомендация: Gemini**

**Почему Gemini:**
- Лучше понимает контекст "несколько человек"
- Можно указать применить изменения ко всем
- Меньше риск, что изменит одного человека больше других

**Промт для группового фото:**
```
GROUP PHOTO - APPLY EQUALLY TO ALL PEOPLE:
- Adjust lighting for ALL faces equally
- Same level of enhancement for each person
- No one person should look more edited than others
- Preserve individual characteristics of each person

CRITICAL: Each person must remain completely recognizable.
```

**Что добавить:**
```
For each person in this photo:
- Preserve their unique skin tone
- Keep their individual facial features
- Apply same intensity of adjustment
```

---

### Какая платформа лучше для художественной обработки?

**Рекомендация: Midjourney**

**Midjourney сильна в:**
- Стилизации под живопись
- Создании художественных эффектов
- Атмосферной обработке

**Когда использовать:**
- Портреты в стиле fine art
- Стилизация под фильмы
- Креативные проекты

**Когда НЕ использовать:**
- Естественный ретуш
- Фото для документов
- Когда нужна точность

**Промт для Midjourney:**
```
Transform into fine art portrait style:
- Painterly quality
- Soft, dramatic lighting
- Artistic color grading

Note: This IS meant to be stylized, not realistic.
Still preserve: basic facial recognition and proportions.
```

---

## Специфические задачи

### Как убрать блики с очков?

**Честный ответ:** Это одна из самых сложных задач для AI.

**Проблема:**
- Под бликом AI не знает, что находится
- Часто "додумывает" глаза неправильно
- Высокий риск изменения лица

**Варианты решения:**

1. **Частичное удаление (лучший вариант):**
```
Reduce glare on glasses by 50%
Do NOT attempt to show what's behind the glare
Just soften the bright spots
If you cannot see the eye clearly, leave glare as is
```

2. **Использование другого фото:**
Если есть фото того же человека без бликов - лучше использовать его

3. **Переснять:**
Часто проще переснять с другим углом освещения

**Предупреждение:** Если AI предлагает "восстановить" глаза под бликами - откажись. Результат почти всегда неестественный.

---

### Как восстановить старое/поврежденное фото?

**Осторожно!** Высокий риск изменения внешности человека.

**Допустимые действия:**
- Удаление царапин и пятен
- Восстановление выцветших цветов
- Уменьшение зернистости

**Рискованные действия:**
- Восстановление поврежденных частей лица
- "Додумывание" размытых участков
- Улучшение детализации

**Промт для старых фото:**
```
VINTAGE PHOTO RESTORATION - CONSERVATIVE APPROACH:

Allowed:
- Remove dust, scratches, and stains
- Restore faded colors to natural levels
- Reduce excessive grain

NOT ALLOWED:
- Reconstruct damaged facial features
- Add details that are not clearly visible in original
- Sharpen beyond what original quality allows
- Make assumptions about unclear areas

If part of face is damaged/unclear:
- Leave it slightly soft rather than inventing details
- Inform me what cannot be restored
```

---

### Как обработать свадебное фото?

**Ключевой принцип:** Консистентность и умеренность.

**Особенности свадебных фото:**
- Часто много людей в кадре
- Важна естественность
- Фото на память - не глянцевый журнал
- Клиент должен узнать себя и гостей

**Промт для свадебных фото:**
```
WEDDING PHOTO - ELEGANT AND NATURAL:

Goals:
- Soft, flattering lighting
- Natural skin tones
- Romantic but realistic atmosphere

Apply to ALL people in frame:
- Same level of subtle enhancement
- Preserve individual appearances
- Keep genuine expressions

DO NOT:
- Make anyone look dramatically different
- Apply heavy beauty retouching
- Create magazine-style perfection
- Edit out natural skin texture

This is a memory - it should look real, just beautifully lit.
```

**Типичные ошибки:**
- Переборщить с отбеливанием платья (теряются детали)
- Разный уровень обработки невесты и гостей
- Слишком гладкая кожа на крупных планах

---

### Как сделать фото для LinkedIn?

**Используй пресет LinkedIn Professional**

**Требования LinkedIn:**
- Профессиональный вид
- Четкое лицо
- Нейтральный или размытый фон
- Хорошее освещение

**Промт для LinkedIn:**
```
LINKEDIN PROFESSIONAL HEADSHOT:

Lighting:
- Clean, professional lighting
- Reduce harsh shadows
- Add subtle catchlight in eyes

Skin:
- Even skin tone
- Natural texture preserved
- Professional but not over-processed

Background:
- If busy, slightly blur background
- Keep focus on face

Style:
- Corporate-appropriate
- Confident but approachable
- Should look like professional photography

DO NOT:
- Heavy beauty retouching
- Dramatic filters
- Artistic effects
- This is for professional networking, not Instagram
```

---

## Проблемы и решения

### AI отказывается редактировать фото

**Возможные причины:**

1. **Content policy violation:**
- Фото может нарушать правила платформы
- Некоторые типы контента запрещены

2. **Неправильная формулировка:**
- Некоторые слова триггерят фильтры
- Попробуй переформулировать

**Решения:**

**Для policy issues:**
- Убедись, что фото не нарушает правила
- Используй другую платформу
- Обрежь проблемные части

**Для проблем с формулировкой:**
```
Вместо: "Remove blemishes" (может триггерить)
Попробуй: "Even out lighting on skin"

Вместо: "Make more attractive"
Попробуй: "Improve lighting quality"
```

**Универсальный безопасный промт:**
```
Apply professional photography lighting adjustments only:
- Exposure correction
- White balance
- Contrast optimization
No content changes, only technical improvements.
```

---

### Результат отличается каждый раз

**Причина:** AI генерирует вариации, нет фиксированного seed.

**Решения:**

1. **Используй seed (если платформа поддерживает):**
```
Use seed: 12345 for consistent results
```

2. **Добавь требование консистентности:**
```
CONSISTENCY CRITICAL:
If you must regenerate, maintain:
- Same color temperature
- Same exposure level
- Same overall style
Result should be indistinguishable from previous attempts.
```

3. **Сохраняй хорошие результаты:**
- Как только получил хороший результат - сохрани
- Не пытайся "улучшить" дальше без необходимости

4. **Работай итеративно:**
- Один хороший результат -> сохрани
- Используй как базу для следующего шага

---

### AI добавляет артефакты на фото

**Типичные артефакты:**
- Размытые края
- Странные текстуры
- Повторяющиеся паттерны
- "Мыльный" эффект

**Решения:**

1. **Уменьши интенсивность:**
```
Apply MINIMAL changes:
- Very subtle adjustments only
- If in doubt, do less
- Intensity: 20-30% of what you would normally apply
```

2. **Укажи качество:**
```
QUALITY REQUIREMENTS:
- No artifacts or distortions
- No blur except intentional background blur
- Clean, sharp edges
- Professional quality output
```

3. **Проверяй по зонам:**
```
Check these areas for artifacts before returning:
- Hair edges
- Skin texture
- Eye details
- Background transitions
```

---

### Фото стало слишком контрастным

**Причина:** AI часто "перебарщивает" с контрастом для эффекта.

**Решение - конкретные значения:**
```
CONTRAST ADJUSTMENT - SPECIFIC VALUES:
- Increase contrast by MAXIMUM 10%
- Shadow lift: +5 to +10 only
- Highlight reduction: -5 to -10 only
- Midtones: unchanged

Result should be subtle improvement, NOT dramatic.
If current image looks good, you may make NO changes.
```

**Для исправления:**
```
This image is too contrasty. Please:
- Reduce contrast by 15-20%
- Lift shadows slightly
- Bring back highlight detail
- Result should look naturally lit
```

---

### AI изменил цвет волос

**Это частая проблема при цветокоррекции.**

**Добавь защиту:**
```
HAIR COLOR PROTECTION:
- Hair color must remain EXACTLY the same hue
- Do not shift hair toward red/orange/cool tones
- Check hair color before and after - must match
- This includes: highlights, shadows, and mid-tones of hair

If color correction affects hair color, exclude hair from correction.
```

**Для разных цветов волос:**
```
Specific hair color: [brown/blonde/red/black]
This exact shade must be preserved.
Any warmth/coolness adjustments should NOT affect hair.
```

---

## Бизнес-вопросы

### Как обрабатывать корпоративные фото?

**Ключевое требование:** Консистентность серии.

**Что нужно:**
- Все фото в одном стиле
- Одинаковый фон/обработка фона
- Единый уровень ретуша
- Профессиональный, но не "глянцевый" вид

**Промт для корпоративной серии:**
```
CORPORATE PHOTO SERIES - CONSISTENCY IS KEY:

This is photo [X] of [Y] in a corporate headshot series.

Standards for ALL photos:
- Background: [solid gray / office blur / white]
- Lighting style: professional, even
- Color temperature: neutral (not warm, not cool)
- Skin: natural with minimal retouching
- Expression: professional, approachable

Apply IDENTICAL processing to this photo as others in series.
Employee should look professional but still like themselves.
```

**Чек-лист для серии:**
- [ ] Одинаковая яркость фона
- [ ] Одинаковый баланс белого
- [ ] Одинаковый уровень контраста
- [ ] Одинаковая обработка кожи
- [ ] Все люди узнаваемы

---

### Сколько брать за AI-ретушь?

**Зависит от:**
- Сложности задачи
- Количества фото
- Требуемого качества
- Времени на согласование

**Примерные категории:**

| Тип работы | Сложность | Время | Ценовой диапазон |
|------------|-----------|-------|------------------|
| Базовая коррекция | Низкая | 5-10 мин | $ |
| Стандартный ретуш | Средняя | 15-30 мин | $$ |
| Сложный ретуш | Высокая | 30-60 мин | $$$ |
| Восстановление | Очень высокая | 1-2 часа | $$$$ |
| Серия/batch | Зависит от объема | Договорная | По кол-ву |

**Что влияет на цену:**
- Количество итераций с клиентом
- Необходимость ручной доработки
- Срочность
- Коммерческое использование

**Совет:** Всегда показывай примеры до согласования цены, чтобы клиент понимал уровень работы.

---

## Глоссарий

| Термин | Значение |
|--------|----------|
| **Catchlight** | Блик/отражение в глазах от источника света |
| **Beauty filter** | Автоматический фильтр сглаживания кожи |
| **Fill light** | Дополнительный свет для заполнения теней |
| **Fallback** | Запасной вариант действий |
| **Smoothing** | Сглаживание текстуры кожи |
| **Retouching** | Профессиональная обработка фото |
| **Upscaling** | Увеличение разрешения изображения с помощью AI |
| **Batch processing** | Обработка серии фото с одинаковыми настройками |
| **Seed** | Числовое значение для воспроизводимости AI-генерации |
| **Morphing** | Изменение формы объектов на фото |
| **Artifact** | Нежелательный визуальный дефект от обработки |
| **Color cast** | Цветовой оттенок, искажающий естественные цвета |
| **Consistency** | Единообразие обработки в серии фото |
