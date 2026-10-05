# Performance Optimization Reference

Практическое руководство по оптимизации производительности веб-сайтов для туристического бизнеса.

---

## 1. Minification & Bundling

### Минификация CSS

Уменьшение размера CSS файлов за счёт удаления пробелов, комментариев и оптимизации кода:

```bash
# Установка cssnano
npm install cssnano postcss-cli

# Минификация одного файла
npx postcss styles.css --use cssnano -o styles.min.css

# Пакетная обработка
npx postcss src/*.css --use cssnano --dir dist/
```

### Минификация JavaScript

```bash
# Установка Terser
npm install terser -g

# Базовая минификация
npx terser script.js -o script.min.js

# С удалением console.log и комментариев
npx terser script.js --compress drop_console=true --comments false -o script.min.js
```

### Bundling с современными инструментами

**Vite (рекомендуется для новых проектов):**
```bash
npm create vite@latest my-project
npm run build  # Автоматическая оптимизация
```

**Webpack:**
```javascript
// webpack.config.js
module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    splitChunks: {
      chunks: 'all'
    }
  }
};
```

**Результат:** Уменьшение размера файлов на 40-70%, быстрая загрузка на мобильных устройствах.

---

## 2. Image Optimization

### Выбор правильного формата

**JPEG** — фотографии достопримечательностей, яхт, пустыни:
- Качество 80-85% оптимально
- Размер на 30-50% меньше PNG

**PNG** — логотипы, иконки с прозрачностью:
- Для простых изображений (логотип компании)
- PNG-8 для иконок с ограниченными цветами

**WebP** — современный формат (поддержка 95%+ браузеров):
- На 25-35% меньше JPEG при том же качестве
- Поддержка прозрачности и анимации

**SVG** — иконки, логотипы, карты:
- Бесконечная масштабируемость
- Минимальный размер файла

### Инструменты оптимизации

**Онлайн:**
- TinyPNG (tinypng.com) — массовое сжатие
- Squoosh (squoosh.app) — Google инструмент
- ImageOptim (только macOS)

**CLI инструменты:**
```bash
# Sharp (Node.js)
npm install sharp
npx sharp input.jpg -o output.webp --webp quality=80

# ImageMagick
convert input.jpg -quality 85 output.jpg
```

### Lazy Loading

```html
<!-- Откладываемая загрузка изображений -->
<img src="yacht.jpg" alt="Yacht Dubai" loading="lazy">

<!-- Responsive изображения -->
<img
  srcset="dubai-320.jpg 320w,
          dubai-640.jpg 640w,
          dubai-1280.jpg 1280w"
  sizes="(max-width: 640px) 100vw, 50vw"
  src="dubai-640.jpg"
  alt="Dubai Tour"
  loading="lazy">
```

### Оптимальные размеры для туристического бизнеса

- **Карточки экскурсий:** 400×300px (WebP, 40-60 KB)
- **Галерея:** 800×600px (JPEG 85%, 80-120 KB)
- **Баннеры:** 1920×600px (JPEG 85%, 150-250 KB)
- **Миниатюры:** 150×150px (WebP, 10-15 KB)

---

## 3. Caching Strategies

### Browser Caching

Настройка заголовков кэширования для статических файлов:

```html
<!-- HTML meta-теги (ограниченная поддержка) -->
<meta http-equiv="cache-control" content="public, max-age=31536000">
```

**Лучше настроить на сервере (Apache):**
```apache
# .htaccess
<IfModule mod_expires.c>
  ExpiresActive On

  # Изображения кэшируются 1 год
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"

  # CSS и JS — 1 месяц
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"

  # HTML — 1 час
  ExpiresByType text/html "access plus 1 hour"
</IfModule>
```

**Nginx:**
```nginx
location ~* \.(jpg|jpeg|png|webp|svg)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

location ~* \.(css|js)$ {
  expires 1M;
  add_header Cache-Control "public";
}
```

### Service Workers для Offline работы

```javascript
// sw.js
const CACHE_NAME = 'tourism-site-v1';
const urlsToCache = [
  '/',
  '/styles.css',
  '/script.js',
  '/images/logo.svg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

### CDN для статических файлов

**Бесплатные CDN:**
- Cloudflare (рекомендуется)
- jsDelivr для библиотек
- Unpkg для npm пакетов

```html
<!-- Загрузка библиотек через CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
```

---

## 4. Performance Metrics

### Core Web Vitals (Google)

**LCP — Largest Contentful Paint:**
- **Цель:** < 2.5 секунд
- **Измеряет:** Время загрузки основного контента
- **Как улучшить:** Оптимизация изображений, серверный рендеринг, предзагрузка ресурсов

**FID — First Input Delay:**
- **Цель:** < 100 миллисекунд
- **Измеряет:** Время отклика на первое взаимодействие
- **Как улучшить:** Минимизация JavaScript, code splitting, использование Web Workers

**CLS — Cumulative Layout Shift:**
- **Цель:** < 0.1
- **Измеряет:** Визуальная стабильность (отсутствие "прыжков" контента)
- **Как улучшить:** Указывать размеры изображений, резервировать место для динамического контента

### Инструменты измерения

**Google Lighthouse:**
```bash
# Установка
npm install -g lighthouse

# Анализ сайта
lighthouse https://yoursite.com --view
```

**PageSpeed Insights:**
- Онлайн: [pagespeed.web.dev](https://pagespeed.web.dev)
- Анализирует мобильную и десктопную версии
- Даёт конкретные рекомендации

**WebPageTest:**
- [webpagetest.org](https://www.webpagetest.org)
- Детальный waterfall загрузки
- Тестирование из разных локаций (включая ОАЭ)

**Chrome DevTools:**
- Performance tab: запись загрузки страницы
- Network tab: анализ размера файлов
- Coverage tab: неиспользуемый CSS/JS

### Целевые показатели для туристического сайта

- **Общий размер страницы:** < 2 MB
- **Время загрузки (3G):** < 5 секунд
- **Lighthouse Score:** > 90
- **Количество запросов:** < 50

---

## Чек-лист быстрой оптимизации

- [ ] Минифицированы CSS и JS
- [ ] Изображения сжаты и в WebP/JPEG
- [ ] Включен lazy loading для изображений
- [ ] Настроено browser caching
- [ ] Используется CDN для статики
- [ ] Проверены Core Web Vitals в Lighthouse
- [ ] Удалён неиспользуемый CSS/JS
- [ ] Шрифты загружаются с `font-display: swap`

---

**Совет:** Оптимизация — это итеративный процесс. Начните с самых тяжёлых ресурсов (обычно изображения) и измеряйте результат после каждого изменения.