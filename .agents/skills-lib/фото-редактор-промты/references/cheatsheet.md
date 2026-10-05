# Шпаргалка: AI фото-редактирование

## Быстрый выбор пресета

| Цель | Команда | Интенсивность |
|------|---------|---------------|
| CV | `/фото cv` | 3/10 |
| LinkedIn | `/фото linkedin` | 2/10 |
| Паспорт | `/фото паспорт` | 1/10 |
| Instagram | `/фото instagram` | 4/10 |
| Dating | `/фото dating` | 3/10 |
| Быстро | `/фото быстро` | 2/10 |

---

## Структура промта

```
ONLY DO:
- {что менять}

DO NOT CHANGE (CRITICAL):
- Face shape
- Skin texture
- Eye size/shape

Style: Natural, not beauty filter.

If cannot without changing face, make NO changes.
```

---

## Защитные фразы (копировать)

**Форма лица:**
```
Face shape - keep exactly the same width and proportions
```

**Текстура кожи:**
```
Skin texture - keep ALL natural pores visible, do NOT smooth
```

**Глаза:**
```
Eye size, shape, position - do NOT change
```

**Универсальный блок:**
```
DO NOT CHANGE (CRITICAL):
- Face shape or width
- Skin texture - keep natural pores
- Eye size or shape
- Bone structure
- Any identifying features
```

---

## Платформы

| Платформа | Когда | Добавить в промт |
|-----------|-------|------------------|
| **Gemini** | CV, профессиональные | — |
| **DALL-E** | Креатив | "smallest possible change" |
| **Midjourney** | Художественные | `--style raw` |
| **SD** | Приватность | denoise 0.3-0.5 |

---

## Что нельзя писать

| Плохо | Почему |
|-------|--------|
| "Make prettier" | Субъективно |
| "Improve" | Слишком широко |
| "Fix" | AI меняет всё |
| Без DO NOT | Нет защиты |

---

## Если результат плохой

1. **Лицо шире** → добавить "exact same face width"
2. **Пластик** → добавить "keep ALL pores visible"
3. **Мультяшно** → уменьшить scope, один change
4. **Не то** → явно перечислить DO NOT CHANGE

---

## База знаний

`D:/Downloads/NanaBananaPro_Скилл_Проект/`

- 150+ промтов
- 10 пресетов
- 4 платформы
- 52 файла документации
