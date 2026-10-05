# GIF Recording Template

## Назначение

Шаблон для записи GIF-инструкций и демонстраций через Claude in Chrome. Подходит для создания визуальных гайдов для сотрудников, документирования workflow, обучающих материалов.

**Когда использовать:**
- Создание пошаговых инструкций для сотрудников (рассылка в WhatsApp/Telegram)
- Документирование процессов бронирования, заполнения форм
- Демонстрация новых фич или интерфейсов
- Запись для README, Confluence, Knowledge Base

## Шаги

### Шаг 1. Подготовка окна

```
tabs_context_mcp(createIfEmpty=true)
resize_window(width=1280, height=720, tabId=TAB_ID)
```

**Рекомендуемые размеры:**

| Назначение | Ширина | Высота |
|-----------|--------|--------|
| Стандартный гайд | 1280 | 720 |
| WhatsApp/Telegram | 800 | 600 |
| Мобильная демо | 375 | 812 |
| Full HD | 1920 | 1080 |

### Шаг 2. Навигация к начальной точке

```
navigate(url="https://САЙТ.com/страница")
computer(action="wait", duration=2, tabId=TAB_ID)    # дождаться загрузки
```

### Шаг 3. Начало записи

```
gif_creator(action="start_recording", tabId=TAB_ID)
```

### Шаг 4. ПЕРВЫЙ КАДР (обязательно!)

```
computer(action="screenshot", tabId=TAB_ID)
# GIF записывает только скриншоты — каждый screenshot = 1 кадр
```

### Шаг 5. Выполнение действий с промежуточными скриншотами

```
# Действие 1
form_input(selector="#guest_name", value="Иван Петров", tabId=TAB_ID)
computer(action="screenshot", tabId=TAB_ID)              # кадр после заполнения

# Действие 2
form_input(selector="#tour_type", value="Desert Safari", tabId=TAB_ID)
computer(action="screenshot", tabId=TAB_ID)              # кадр после выбора

# Действие 3
find(text="Submit", tabId=TAB_ID)
computer(action="left_click", ref=REF, tabId=TAB_ID)
computer(action="screenshot", tabId=TAB_ID)              # кадр после клика

# Действие 4 — результат
computer(action="wait", duration=2, tabId=TAB_ID)
computer(action="screenshot", tabId=TAB_ID)              # кадр с результатом
```

**Правило: после КАЖДОГО значимого действия -- screenshot!**

### Шаг 6. Дополнительные кадры на финальном экране

```
# Для "задержки" на важном кадре — повторные скриншоты
computer(action="screenshot", tabId=TAB_ID)   # +1 кадр
computer(action="screenshot", tabId=TAB_ID)   # +1 кадр
# Каждый дополнительный screenshot = +1 кадр паузы
```

### Шаг 7. Остановка записи

```
gif_creator(action="stop_recording", tabId=TAB_ID)
```

### Шаг 8. Экспорт GIF

```
gif_creator(action="export", tabId=TAB_ID,
  download=true,
  filename="НАЗВАНИЕ_ИНСТРУКЦИИ.gif",
  options={
    quality: 5,
    showClickIndicators: true,
    showActionLabels: true,
    showProgressBar: true,
    showWatermark: false
  }
)
```

## Пример промпта

```
Запиши GIF-инструкцию для сотрудников:
"Как заполнить форму бронирования на partnersite.com"

Шаги для записи:
1. Открой partnersite.com/new-booking
2. Установи размер окна 1280x720
3. Начни запись GIF
4. Покажи заполнение каждого поля: имя, email, тип тура, дата, кол-во гостей
5. Покажи нажатие кнопки Submit
6. Покажи экран подтверждения (задержка 3 кадра)
7. Сохрани как booking_instruction.gif

Настройки GIF: quality=5, показывать клики и подписи действий, БЕЗ watermark.
```

## Параметры для настройки

| Параметр | По умолчанию | Описание |
|----------|-------------|---------|
| `width` | 1280 | Ширина окна записи |
| `height` | 720 | Высота окна записи |
| `filename` | `recording.gif` | Имя файла GIF |
| `quality` | 10 | Качество GIF (1-30, ниже = лучше качество, больше файл) |
| `showClickIndicators` | true | Показывать круги в местах кликов |
| `showDragPaths` | true | Показывать пути перетаскивания |
| `showActionLabels` | true | Подписи к действиям |
| `showProgressBar` | true | Прогресс-бар внизу GIF |
| `showWatermark` | true | Водяной знак Claude |
| `Доп. кадры на финале` | 2-3 | Количество повторных screenshot для "паузы" |

## Частые ошибки

- **GIF пустой или 0 кадров** -- Не сделан ни один screenshot между start_recording и stop_recording. Решение: GIF записывает ТОЛЬКО скриншоты. Обязательно `computer(action="screenshot")` после каждого действия.

- **GIF слишком быстрый** -- Мало кадров. Решение: добавить дополнительные screenshots на важных моментах (повторный screenshot = дополнительный кадр задержки).

- **Файл не скачивается** -- Не указан `download: true`. Решение: `download: true` обязателен при export. Параметра `output_path` НЕ СУЩЕСТВУЕТ.

- **Записаны лишние действия** -- Забыли stop_recording вовремя. Решение: `gif_creator(action="clear")` для сброса и начало заново.

- **Окно слишком большое для мессенджера** -- Решение: `resize_window(width=800, height=600)` перед записью для компактного GIF.

- **Не видно курсор/клики** -- По умолчанию включены `showClickIndicators`. Проверить, что `options` содержит `showClickIndicators: true`.

## Советы по качественному GIF

1. **Планирование:** Определите точную последовательность действий ДО начала записи
2. **Чистота:** Закройте лишние уведомления, попапы, рекламу перед записью
3. **Пауза на результате:** 2-3 дополнительных screenshot на финальном кадре
4. **Размер файла:** quality=5 для WhatsApp (лучшее качество), quality=15 для экономии
5. **Именование:** Используйте понятные имена: `booking_form_guide.gif`, `crm_add_contact.gif`
