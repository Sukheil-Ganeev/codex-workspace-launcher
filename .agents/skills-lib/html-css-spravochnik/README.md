# HTML & CSS Справочник

> Production-ready скилл для создания современных веб-страниц

## Структура

- **SKILL.md** — Основной справочник (~2500 слов)
- **references/** — 7 модульных гайдов
- **assets/templates/** — 10 готовых шаблонов
- **assets/examples/** — 9 полных примеров
- **scripts/** — 8 production скриптов
- **experience/** — Накопленный опыт и уроки

## Quick Links

| Что нужно | Куда идти |
|-----------|-----------|
| Создать лендинг за 15 минут | SKILL.md → Quick Start → Сценарий A |
| Справка по HTML5 | references/html5-reference.md |
| Справка по CSS Grid/Flexbox | references/css3-reference.md |
| Адаптивный дизайн (Mobile-First) | references/responsive-design.md |
| JavaScript интеграции | references/javascript-integration.md |
| Интеграция с Google Maps | references/api-integrations.md |
| Оптимизация производительности | references/performance-optimization.md |
| Интеграции с другими скиллами | references/skill-integrations.md |
| Деплой на Netlify | scripts/deploy-helper.js |

## Использование

### 1. Выбрать шаблон

```bash
cp assets/templates/landing-page.html my-page.html
```

Доступные шаблоны:
- `landing-page.html` — Полноценный лендинг для туров
- `tour-card.html` — Карточка одного тура
- `contact-form.html` — Форма обратной связи
- `price-calculator.html` — Калькулятор цены тура
- `booking-form.html` — Форма бронирования
- `gallery.html` — Фотогалерея
- `google-maps-integration.html` — Интеграция Google Maps
- `sheets-api-integration.html` — Интеграция Google Sheets
- `base-styles.css` — Базовые стили
- `responsive-grid.css` — Адаптивная сетка

### 2. Адаптировать

Заменить плейсхолдеры `[ТЕКСТ]` на реальный контент:
- `[ЗАГОЛОВОК]` — Название тура/услуги
- `[ОПИСАНИЕ]` — Описание
- `[ЦЕНА]` — Цена в AED
- `[КОНТАКТ]` — WhatsApp, email и т.д.

### 3. Использовать примеры

Полные рабочие примеры в `assets/examples/`:
- **tour-landing/** — Лендинг тура в Абу-Даби
- **price-list/** — Прайс-лист из Google Sheets
- **booking-system/** — Система бронирования
- **tour-cards/** — Галерея туров
- **gallery/** — Фотогалерея с лайтбоксом
- **calculator/** — Калькулятор стоимости
- **maps-route/** — Маршрут на Google Maps
- **contact-form/** — Форма с валидацией
- **integrated-workflow/** — Полный workflow

Каждый пример содержит:
- `index.html` — HTML разметка
- `styles.css` — CSS стили
- `script.js` — JavaScript логика
- `README.md` — Инструкция по использованию

### 4. Запустить локально

```bash
cd scripts
npm install
node dev-server.js ../assets/examples/tour-landing/
```

Откроется `http://localhost:3000` с live reload.

### 5. Деплой

```bash
node scripts/deploy-helper.js --platform netlify
```

Поддерживаемые платформы:
- `netlify` — Netlify
- `vercel` — Vercel
- `github-pages` — GitHub Pages

## Использование скриптов

Все скрипты находятся в папке `scripts/`:

### Валидация HTML/CSS/JS

```bash
node scripts/validate.js index.html
node scripts/validate.js --css styles.css
node scripts/validate.js --js script.js
```

### Минификация для production

```bash
node scripts/minify.js index.html --output dist/
```

Результат:
- HTML: комментарии удалены, пробелы сжаты
- CSS: минифицирован через cssnano
- JS: минифицирован через terser

### Генерация из шаблона

```bash
node scripts/template-gen.js tour-landing \
  --title "Тур в Абу-Даби" \
  --price 250 \
  --output my-tour.html
```

### Оптимизация изображений

```bash
node scripts/image-optimizer.js images/
```

Результат: JPEG сжат на 70-80%, PNG сжат на 40-60%, создаёт WebP версии.

### Автопрефиксер CSS

```bash
node scripts/autoprefixer.js styles.css
```

Добавляет `-webkit-`, `-moz-`, `-ms-` префиксы автоматически.

### Build для production

```bash
node scripts/build.js --input src/ --output dist/
```

Запускает: валидация → минификация → оптимизация изображений → автопрефиксер.

Подробная документация: `scripts/README.md`

## Интеграции

Этот скилл работает вместе с:

- **netlify-deployment** — Деплой на Netlify
- **vercel-деплой** — Деплой на Vercel
- **api-туризм-оаэ** — API интеграции для туризма
- **git-github-справочник** — Работа с Git/GitHub
- **форматирование-турпродуктов** — Контент для карточек туров
- **создание-карточек-каталога** — Генерация каталогов

См. `references/skill-integrations.md` для workflows.

## Experience система

Скилл накапливает опыт в папке `experience/`:

```
experience/
├── _index.md             # Критические уроки (топ-5)
├── fixes/                # Исправленные ошибки
├── improvements/         # Найденные улучшения
├── patterns/             # Повторяющиеся паттерны
└── warnings/             # Что НЕ делать
```

**При активации скилла:**
1. Прочитайте `experience/_index.md`
2. Применяйте уроки при работе

**При завершении работы:**
- Если был урок — запишите в `experience/`
- Команда: "запиши в опыт"

## Документация

### Основные файлы

- **SKILL.md** — Начните здесь (Quick Start, сценарии, FAQ)
- **references/html5-reference.md** — HTML5 справочник (семантика, формы, мета-теги)
- **references/css3-reference.md** — CSS3 справочник (Grid, Flexbox, анимации)
- **references/responsive-design.md** — Mobile-First подход, медиазапросы
- **references/javascript-integration.md** — Vanilla JS для форм, API
- **references/api-integrations.md** — Google Maps, Google Sheets API
- **references/performance-optimization.md** — Скорость загрузки, Core Web Vitals
- **references/skill-integrations.md** — Работа с другими скиллами

### Дополнительно

- **scripts/README.md** — Документация всех скриптов
- **assets/examples/*/README.md** — Инструкции к каждому примеру

## Типичные задачи

### Создать лендинг тура за 15 минут

```bash
# 1. Копируем шаблон
cp assets/templates/landing-page.html my-tour.html

# 2. Редактируем в VS Code
code my-tour.html

# 3. Запускаем локально
node scripts/dev-server.js .

# 4. Деплоим
node scripts/deploy-helper.js --platform netlify
```

### Интегрировать Google Maps

См. `references/api-integrations.md` → Google Maps API.

Готовый шаблон: `assets/templates/google-maps-integration.html`

Пример: `assets/examples/maps-route/`

### Получить данные из Google Sheets

См. `references/api-integrations.md` → Google Sheets API.

Готовый шаблон: `assets/templates/sheets-api-integration.html`

Пример: `assets/examples/price-list/`

### Создать форму бронирования

Шаблон: `assets/templates/booking-form.html`

Пример: `assets/examples/booking-system/`

Валидация + отправка в Google Sheets + уведомление в Telegram.

## Поддержка

- Открыть issue на GitHub
- Спросить в команде Tourism Tech
- Проверить `experience/_index.md` на похожую проблему

## Лицензия

MIT

## Автор

Tourism Tech Team (Suheil)
