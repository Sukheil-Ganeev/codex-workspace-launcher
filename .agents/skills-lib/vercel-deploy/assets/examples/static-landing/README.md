# Static Landing - Простой статичный лендинг

Минималистичный одностраничный лендинг для деплоя на Vercel.

## Структура проекта

```
static-landing/
├── index.html       # Главная страница
├── vercel.json      # Конфигурация Vercel
└── README.md        # Документация
```

## Особенности

- Чистый HTML/CSS (без зависимостей)
- Responsive дизайн
- Gradient фон
- Быстрая загрузка

## Деплой на Vercel

### Вариант 1: Через CLI

```bash
# Перейти в папку проекта
cd path/to/static-landing

# Залогиниться в Vercel
vercel login

# Задеплоить
vercel

# Или сразу в production
vercel --prod
```

### Вариант 2: Через GitHub

1. Создать репозиторий на GitHub
2. Пушнуть код:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-repo-url
   git push -u origin main
   ```
3. Зайти на [vercel.com](https://vercel.com)
4. New Project → Import Git Repository
5. Выбрать репозиторий → Deploy

### Вариант 3: Drag & Drop

1. Зайти на [vercel.com](https://vercel.com)
2. Перетащить папку проекта в окно браузера
3. Дождаться деплоя

## Настройка

### Изменить текст

Отредактировать `index.html`:

```html
<h1>Ваш заголовок</h1>
<p>Ваше описание</p>
<a href="your-link" class="btn">Ваша кнопка</a>
```

### Изменить цвета градиента

В `<style>`:

```css
.hero {
    background: linear-gradient(135deg, #ваш-цвет-1 0%, #ваш-цвет-2 100%);
}
```

### Добавить больше страниц

1. Создать `about.html`, `contact.html` и т.д.
2. Vercel автоматически их подхватит

## Полезные ссылки

- [Vercel Static Builds](https://vercel.com/docs/concepts/deployments/build-step#static-builds)
- [HTML/CSS Best Practices](https://developer.mozilla.org/en-US/docs/Learn/HTML)

## Troubleshooting

**Проблема:** 404 ошибка после деплоя

**Решение:** Убедитесь, что `index.html` находится в корне проекта

---

**Проблема:** Стили не применяются

**Решение:** Проверьте синтаксис CSS в `<style>` теге

---

**Проблема:** Долгая загрузка

**Решение:** Оптимизируйте изображения (если добавляли) через [TinyPNG](https://tinypng.com)
