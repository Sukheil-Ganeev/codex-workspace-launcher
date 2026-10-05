# Паттерн: Zero-Dependency презентация

**Дата:** 2026-02-05
**Контекст:** Презентация "Стратегия Океанов" — 14 слайдов, тёмная тема, 4.9 MB PDF
**Путь:** `D:/Downloads/Ocean_Strategy_Presentation/`

## Проблема

Предыдущие презентации часто ломались из-за:
- Google Fonts не загружаются → квадратики на Mac
- Внешние изображения не скачиваются → пустые места
- CDN иконки не доступны offline → отсутствующие элементы

## Решение: Полностью автономный HTML

### 1. Системные шрифты (без Google Fonts)

```css
font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif;
```

**Почему:** Segoe UI установлен на всех Windows, Helvetica Neue на Mac, Arial — fallback. Нет сетевых запросов, нет задержек, нет проблем с кодировкой.

**Когда Google Fonts нужны:** Только для брендированных презентаций, где шрифт критичен. В этом случае — встраивать через base64 (EXP-007).

### 2. Inline SVG иконки (без CDN)

```html
<!-- ✅ Inline SVG — работает всегда -->
<svg width="32" height="32" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="14" fill="none" stroke="#e74c3c" stroke-width="2"/>
  <path d="M10 16 L16 10 L22 16 L16 22 Z" fill="#e74c3c"/>
</svg>

<!-- ❌ Внешние иконки — могут не загрузиться -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/...font-awesome...">
<i class="fa fa-star"></i>
```

**Совет:** Создавать простые SVG иконки по смыслу (крестик, стрелка, круг с плюсом), а не искать готовые. 5-10 строк SVG для каждой иконки.

### 3. CSS-only декоративные эффекты

#### Ambient Glow (фоновые круги с blur)

```css
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.15;
  z-index: 0;
}
```

```html
<div class="bg-decoration" style="
  width: 600px; height: 600px;
  background: var(--red-ocean);
  top: -200px; left: -150px;
"></div>
```

**Результат:** Мягкое цветное свечение, создающее глубину. Работает в Chromium PDF.
**Важно:** `filter: blur()` на отдельных элементах работает в PDF (в отличие от `backdrop-filter`!).

#### Градиентный текст

```css
.gradient-text {
  background: linear-gradient(135deg, #e74c3c, #9b59b6, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Работает в Chromium PDF:** Да.
**Работает в Apple Preview:** Может быть проблемы — тестировать.

#### Волны SVG (декор низа/верха слайда)

```html
<svg style="position: absolute; bottom: 0; left: 0; width: 100%;" viewBox="0 0 1920 120" fill="none">
  <path d="M0 80 C320 20, 640 100, 960 60 C1280 20, 1600 100, 1920 60 L1920 120 L0 120 Z"
        fill="rgba(10, 14, 39, 0.5)"/>
  <path d="M0 90 C320 40, 640 110, 960 70 C1280 30, 1600 110, 1920 70"
        stroke="rgba(52, 152, 219, 0.3)" stroke-width="2" fill="none"/>
</svg>
```

### 4. CSS переменные как дизайн-система

```css
:root {
  --bg-dark: #0a0e27;
  --bg-slide: #0f1535;
  --bg-card: #161d45;
  --red-ocean: #e74c3c;
  --blue-ocean: #3498db;
  --purple-ocean: #9b59b6;
  --green-ocean: #27ae60;
  --text-primary: #ffffff;
  --text-secondary: #a0aec0;
  --text-muted: #6b7a99;
  --accent-gold: #f39c12;
  --border-subtle: rgba(255, 255, 255, 0.08);
}
```

**Преимущества:**
- Легко сменить тему (заменить 10 переменных)
- Консистентность цветов на всех слайдах
- Поддержка glow-эффектов: `--red-glow: rgba(231, 76, 60, 0.3)`

### 5. Flexbox для вертикального распределения контента

```css
.slide {
  display: flex;
  flex-direction: column;
  padding: 70px 100px;
}

.slide-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Элемент в конце слайда (highlight box) */
.highlight-box {
  margin-top: auto;  /* Прижать к низу */
}
```

**Почему:** Контент автоматически занимает доступное пространство. `margin-top: auto` прижимает элемент к низу без абсолютного позиционирования.

## Результат

| Метрика | Значение |
|---------|----------|
| Внешние зависимости | 0 |
| Сетевые запросы | 0 |
| Время конвертации | ~3 сек |
| Размер PDF | 4.9 MB (14 слайдов) |
| Проблемы | 0 |

## Когда применять

- Любая презентация, где кастомный шрифт не обязателен
- Тёмные темы (где CSS gradients и glow выглядят хорошо)
- Быстрое прототипирование (не тратить время на поиск иконок)
- Презентации, которые должны работать offline

## Реальный пример

**Проект:** Ocean Strategy Presentation
**Файлы:** `D:/Downloads/Ocean_Strategy_Presentation/`
- `presentation.html` — 14 слайдов, ~1400 строк HTML
- `convert_to_pdf.py` — конвертер с Windows encoding fix
- `output/ocean_strategy.pdf` — финальный PDF
