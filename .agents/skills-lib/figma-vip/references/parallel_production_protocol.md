# Parallel Production Protocol

Правила для запуска параллельных субагентов на Figma production без конфликтов.

---

## Current Safe Mode (2026-03-29)

- По умолчанию параллельная работа сейчас означает **1 main agent + 1 sidecar subagent**, а не два независимых live-writer агента.
- Главный агент владеет:
  - live `use_figma`
  - live audit через Figma
  - `ingest_live_audit.py`
  - обновлением `_progress.md`, `BUG_REGISTRY.md`, `GENERATOR_QA_CHANGELOG.md`
- Сайдкар-субагенту по умолчанию разрешена только локальная подготовка другой карусели на непересекающемся наборе файлов:
  - HTML/CSS review
  - `unified.js`
  - contracts
  - preflight QA
- Не считать старый 4-pass live-write шаблон безопасным по умолчанию: текущий production-процесс уже опирается на `unified + contracts + live audit + ingest`, и shared tracking надо обновлять централизованно.
- Если нужен именно параллельный live-write режим, это должно быть отдельным явным решением: с зарезервированным Y, выделенным диапазоном каруселей, обновлённым промптом и финальной проверкой главным агентом.

## Safe / Unsafe Operations

| Operation | Parallel by default? | Rule |
|---|---|---|
| HTML/CSS inspection | yes | safe on another carousel |
| Regenerate `slide_*_unified.js` | yes | only on disjoint carousel files |
| `build_slide_contracts.py` | yes | safe on another carousel, but keep `contracts -> live-audit` sequential inside that carousel |
| `figma_preflight_qa.py` | yes | safe on another carousel |
| `generate_live_audit.py` | no | only after final contracts, usually in main thread |
| live `use_figma` write | no | main agent owns it by default |
| `ingest_live_audit.py` | no | never parallel with another ingest |
| shared tracker docs | no | main agent only |

---

## 1. Y-Coordinate Registry

Каждая карусель занимает горизонтальную полосу на странице. Высота полосы = 1350 + 250 (gap) = **1600px**.

### Текущая карта (обновлять при каждом создании)

Файл: `docs/figma-analysis/production-log/_progress.md`

| Y | Карусель | Статус |
|---|----------|--------|
| 50 | arab_traditions + arabic_coffee + avoid_queues cover | legacy |
| 17600 | avoid_queues_v1 slides 2-8 | done |
| 19200 | banned_medicines_v1 (= dress_code) | wrong content |
| 20800 | cheap_food_dubai_v1 | font fixed |
| 22400 | coffee_shops_v1 | partial |
| 24000 | (зарезервировано для dress_code_dubai_v1) | — |
| 25600 | (зарезервировано для dubai_fines_v1) | — |
| 27200 | (зарезервировано) | — |
| 28800 | family_places_v1 | created |
| 30400 | fountains_dubai_v1 | — |
| 32000 | free_activities_dubai_v1 | — |
| 33600 | free_dubai_v1 | — |
| 35200 | tourist_mistakes_v1 | — |
| 36800 | which_excursions_v1 | — |
| 38400 | yas_island_v1 | — |

### Правила назначения Y

1. **Перед запуском агента** — прочитать _progress.md, найти свободный Y
2. **Записать "reserved by Agent X"** в файл ПЕРЕД началом работы
3. **Шаг Y = 1600px** (1350 slide + 250 gap)
4. **X-координата внутри ряда** = slideIndex * 1180 (1080 slide + 100 gap)
5. **Два агента НИКОГДА не работают на одном Y**

### Протокол резервирования

```
Агент A получает задачу: dress_code_dubai_v1
1. Читает _progress.md → Y=24000 свободен
2. Записывает в _progress.md: "| 24000 | dress_code_dubai_v1 | 🔒 Agent A working |"
3. Создаёт слайды
4. Обновляет: "| 24000 | dress_code_dubai_v1 | ✅ created |"
```

---

## 2. Conflict Prevention

### Что может конфликтовать

| Ресурс | Риск | Решение |
|--------|------|---------|
| Figma page | Два агента создают ноды одновременно | Разные Y-координаты |
| _progress.md | Одновременная запись | Агент записывает ТОЛЬКО свой ряд |
| Font loading | Два loadFontAsync одновременно | Безопасно — Figma кеширует |
| Node IDs | ID из Pass 1 нужен в Pass 2 | Передавать через return, не через файл |

### Что НЕ конфликтует (безопасно параллельно)

- Разные карусели на разных Y — полностью изолированы
- Чтение HTML/CSS файлов — read-only
- createNodeFromSvg — каждый вызов изолирован
- getNodeByIdAsync — читает конкретную ноду

---

## 3. Sub-Agent Task Format

Каждый субагент получает задачу в этом формате:

```
CAROUSEL: family_places_v1
SLIDES: 1-8
Y_POSITION: 28800
X_STEP: 1180

SLIDE DATA:
[slide_1]
type: cover
num: "01 / 08"
chip: "СЕМЕЙНЫЙ ГИД"
chip_svg: '<svg viewBox="0 0 24 24" ...>...</svg>'
title: "ДУБАЙ\nС ДЕТЬМИ\n10 МЕСТ"
title_size: 84
subtitle: "Парки с кондиционером..."
... (все поля)

[slide_2]
type: content
... и т.д.
```

### Что ОБЯЗАТЕЛЬНО включить в промпт субагента

1. **Boilerplate код** — полный блок из `references/boilerplate.md` (секции 1-8)
2. **CSS ширины** — таблица из `references/css_width_calculator.md` для нужного типа слайдов
3. **Font corrections** — таблица из `docs/figma-data/font_weight_corrections.md`
4. **Opacity table** — meta:0.84, subtitle:0.86, card-text:0.66, footer-title:0.95, footer-text:0.86, watermark:0.045, service:0.74, cta-eyebrow:0.78
5. **SVG строки** — все SVG пути извлечённые из HTML
6. **Slide data** — текстовый контент каждого слайда
7. **4-pass pipeline** — инструкция что делать в каждом pass
8. **Naming convention** — таблица из boilerplate секция 9
9. **Y-координата** — конкретная для этой карусели
10. **Figma file ID** — `8B1Dfaq8XtBOXlJuS19UhK`

### Что НЕ включать (экономия контекста)

- Историю сессии
- Уроки L-01..L-25 (они уже встроены в boilerplate и pipeline)
- Полный CSS файл (ширины уже рассчитаны)
- Другие карусели (только своя задача)

---

## 4. Error Recovery Protocol

### Таймаут (fetch failed / 30s limit)

```
Ситуация: Pass 1 или Pass 2 таймаутит
Действие:
1. НЕ паниковать — это нормально для сложных слайдов
2. Проверить: был ли root создан? (get_screenshot по координатам)
3. Если root создан но неполный → продолжить с Pass 2
4. Если root НЕ создан → retry тот же Pass
5. Максимум 2 retry → разбить Pass на 2 под-части
```

### 502 Bad Gateway (MCP server down)

```
Ситуация: Figma MCP возвращает 502
Действие:
1. Подождать 60 секунд
2. Отправить тестовый вызов: return { status: "ok" }
3. Если ок → продолжить
4. Если нет → подождать 2 минуты, retry
5. После 3 неудач → сообщить пользователю
```

### Неправильный контент (wrong data in slide)

```
Ситуация: текст или структура не соответствует HTML
Действие:
1. НЕ удалять и пересоздавать
2. Точечный fix через getNodeByIdAsync → изменить конкретную ноду
3. Пересоздание — только если >50% нод неправильные
```

---

## 5. Quality Gate — Определение "Done"

Слайд считается ГОТОВЫМ когда ВСЕ пункты выполнены:

### Автоматические (из validate())
- [ ] 0 нод с h=100 (кроме spacer)
- [ ] 0 нод с w=100+clip
- [ ] 0 текстовых нод с overflow (width > parent inner)
- [ ] 0 placeholder иконок (все заменены на SVG)

### Размерные (из css_width_calculator)
- [ ] Все текстовые ширины ±5px от значений калькулятора
- [ ] Root frame = 1080x1350
- [ ] Content padding = 56/64

### Визуальные (из get_screenshot)
- [ ] Все текста читаемы (нет обрезки)
- [ ] Footer прижат к низу
- [ ] Meta bar: counter слева, handle справа
- [ ] Chip с иконкой SVG
- [ ] Watermark едва виден внизу справа
- [ ] Inner border виден (тонкая белая рамка)

### Контентные
- [ ] Текст соответствует HTML оригиналу
- [ ] Количество карточек = количеству в HTML
- [ ] Номер слайда правильный (NN / MM)

**Когда все пункты ✅ → слайд "done". Обновить _progress.md.**

---

## 6. Parallel Agent Workflow

### Для 2 агентов (рекомендуемый максимум)

```
Agent A: карусели 1-4 (slides с меньшим количеством карточек)
Agent B: карусели 5-8 (или те же карусели, но другие slide ranges)

Координация:
- Каждый агент резервирует свои Y-координаты
- Каждый агент работает независимо (4-pass per slide)
- Финальная проверка — один проход по всем слайдам (get_screenshot loop)
```

### Для 3+ агентов

```
НЕ рекомендуется для одного Figma файла.
Причина: Figma API rate limits, node creation conflicts.
Максимум: 2 параллельных агента на 1 Figma файл.
```

### Timeline для 1 карусели (8 slides)

```
Pre-flight:         5 мин (read HTML, extract data, calc widths)
Pass 1 × 8 slides: 8 мин (shell + empty containers, 1 мин per slide)
Pass 2 × 8 slides: 8 мин (left column content)
Pass 3 × 8 slides: 8 мин (right column + footer)
Pass 4 × 8 slides: 8 мин (SVG icons + validate + width audit)
Post-flight:        5 мин (screenshots + visual check)
Total:             ~42 мин per carousel
```

С 2 параллельными агентами: **~42 мин на 2 карусели** (вместо 84 последовательно).
