# Static Catalog - Статичный каталог туров

Простой HTML/CSS каталог туров без сборки.

## Описание

Минималистичный каталог туров, который можно быстро задеплоить без настройки сборки.

**Идеально для:** быстрого запуска, тестирования, простых каталогов.

## Структура проекта

```
static-catalog/
├── index.html                    # Главная страница
├── tours.html                    # Страница туров
├── contact.html                  # Контакты
├── style.css                     # Общие стили
├── netlify.toml                  # Конфигурация
└── images/                       # Изображения
    ├── safari.jpg
    ├── burj-khalifa.jpg
    └── abu-dhabi.jpg
```

## Шаг 1: Создайте файлы

### index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Туры в ОАЭ | Dubai Tours</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav class="navbar">
    <div class="container">
      <div class="logo">🏜️ Dubai Tours</div>
      <div class="nav-links">
        <a href="index.html">Главная</a>
        <a href="tours.html">Туры</a>
        <a href="contact.html">Контакты</a>
      </div>
    </div>
  </nav>

  <section class="hero">
    <div class="container">
      <h1>Незабываемые туры в ОАЭ</h1>
      <p>Экскурсии, сафари, билеты в парки по лучшим ценам</p>
      <a href="tours.html" class="btn">Смотреть туры</a>
    </div>
  </section>

  <section class="container">
    <h2 class="section-title">Популярные туры</h2>

    <div class="tours-grid">
      <div class="tour-card">
        <img src="images/safari.jpg" alt="Джип-сафари">
        <div class="tour-content">
          <h3>Джип-сафари в пустыне</h3>
          <p>Экстремальная езда по дюнам, катание на верблюдах, ужин BBQ и шоу</p>
          <div class="tour-price">От 250 AED</div>
          <a href="contact.html" class="btn btn-small">Забронировать</a>
        </div>
      </div>

      <div class="tour-card">
        <img src="images/burj-khalifa.jpg" alt="Бурдж Халифа">
        <div class="tour-content">
          <h3>Бурдж Халифа 124 этаж</h3>
          <p>Смотровая площадка самого высокого здания в мире</p>
          <div class="tour-price">От 149 AED</div>
          <a href="contact.html" class="btn btn-small">Забронировать</a>
        </div>
      </div>

      <div class="tour-card">
        <img src="images/abu-dhabi.jpg" alt="Абу-Даби">
        <div class="tour-content">
          <h3>Тур в Абу-Даби</h3>
          <p>Мечеть Шейха Зайда, Лувр Абу-Даби, набережная Корниш</p>
          <div class="tour-price">От 200 AED</div>
          <a href="contact.html" class="btn btn-small">Забронировать</a>
        </div>
      </div>
    </div>
  </section>

  <section class="cta">
    <div class="container">
      <h2>Готовы к приключению?</h2>
      <p>Свяжитесь с нами для бронирования</p>
      <a href="contact.html" class="btn">Связаться</a>
    </div>
  </section>

  <footer>
    <div class="container">
      <p>© 2024 Dubai Tours. Все права защищены.</p>
      <p>📱 +971 50 123 4567 | ✉️ info@dubaitours.com</p>
    </div>
  </footer>
</body>
</html>
```

### tours.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Все туры | Dubai Tours</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav class="navbar">
    <div class="container">
      <div class="logo">🏜️ Dubai Tours</div>
      <div class="nav-links">
        <a href="index.html">Главная</a>
        <a href="tours.html">Туры</a>
        <a href="contact.html">Контакты</a>
      </div>
    </div>
  </nav>

  <section class="container" style="padding-top: 100px;">
    <h1>Все туры</h1>

    <div class="tours-list">
      <div class="tour-item">
        <h3>🏜️ Джип-сафари в пустыне</h3>
        <p>Утреннее или вечернее сафари с ужином</p>
        <span class="price">250 AED</span>
      </div>

      <div class="tour-item">
        <h3>🏙️ Городской тур Дубай</h3>
        <p>Обзорная экскурсия по основным достопримечательностям</p>
        <span class="price">180 AED</span>
      </div>

      <div class="tour-item">
        <h3>🕌 Тур в Абу-Даби</h3>
        <p>Мечеть Шейха Зайда и Лувр</p>
        <span class="price">200 AED</span>
      </div>

      <div class="tour-item">
        <h3>🏢 Бурдж Халифа 124 этаж</h3>
        <p>Смотровая площадка</p>
        <span class="price">149 AED</span>
      </div>

      <div class="tour-item">
        <h3>🎢 Dubai Parks (Multi-Park)</h3>
        <p>Билеты на 2-3 парка</p>
        <span class="price">295 AED</span>
      </div>

      <div class="tour-item">
        <h3>🐠 Dubai Aquarium</h3>
        <p>Билеты в аквариум Dubai Mall</p>
        <span class="price">130 AED</span>
      </div>
    </div>
  </section>

  <footer>
    <div class="container">
      <p>© 2024 Dubai Tours. Все права защищены.</p>
    </div>
  </footer>
</body>
</html>
```

### contact.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Контакты | Dubai Tours</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav class="navbar">
    <div class="container">
      <div class="logo">🏜️ Dubai Tours</div>
      <div class="nav-links">
        <a href="index.html">Главная</a>
        <a href="tours.html">Туры</a>
        <a href="contact.html">Контакты</a>
      </div>
    </div>
  </nav>

  <section class="container" style="padding-top: 100px;">
    <h1>Контакты</h1>

    <div class="contact-info">
      <div class="contact-card">
        <h3>📱 Телефон / WhatsApp</h3>
        <p><a href="tel:+971501234567">+971 50 123 4567</a></p>
      </div>

      <div class="contact-card">
        <h3>✉️ Email</h3>
        <p><a href="mailto:info@dubaitours.com">info@dubaitours.com</a></p>
      </div>

      <div class="contact-card">
        <h3>📍 Офис</h3>
        <p>Dubai, Tecom (Barsha Heights)</p>
        <p>Ближайшее метро: Dubai Internet City</p>
      </div>

      <div class="contact-card">
        <h3>⏰ Режим работы</h3>
        <p>Ежедневно: 9:00 - 21:00</p>
      </div>
    </div>
  </section>

  <footer>
    <div class="container">
      <p>© 2024 Dubai Tours. Все права защищены.</p>
    </div>
  </footer>
</body>
</html>
```

### style.css

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Navbar */
.navbar {
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.navbar .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
}

.logo {
  font-size: 24px;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 30px;
}

.nav-links a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: #667eea;
}

/* Hero */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 150px 20px 100px;
  text-align: center;
  margin-top: 60px;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.hero p {
  font-size: 20px;
  margin-bottom: 30px;
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 15px 40px;
  background: white;
  color: #667eea;
  text-decoration: none;
  border-radius: 50px;
  font-weight: bold;
  transition: transform 0.3s;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn-small {
  padding: 10px 20px;
  font-size: 14px;
}

/* Tours Grid */
.section-title {
  text-align: center;
  font-size: 36px;
  margin: 60px 0 40px;
}

.tours-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 60px;
}

.tour-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.tour-card:hover {
  transform: translateY(-5px);
}

.tour-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.tour-content {
  padding: 20px;
}

.tour-content h3 {
  margin-bottom: 10px;
  color: #667eea;
}

.tour-price {
  font-size: 24px;
  font-weight: bold;
  color: #4caf50;
  margin: 15px 0;
}

/* Tours List */
.tours-list {
  display: grid;
  gap: 20px;
  margin-bottom: 60px;
}

.tour-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tour-item .price {
  font-size: 20px;
  font-weight: bold;
  color: #4caf50;
}

/* Contact */
.contact-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 60px;
}

.contact-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.contact-card h3 {
  margin-bottom: 15px;
  color: #667eea;
}

.contact-card a {
  color: #667eea;
  text-decoration: none;
}

/* CTA */
.cta {
  background: #667eea;
  color: white;
  padding: 80px 20px;
  text-align: center;
  margin: 60px 0;
}

.cta h2 {
  font-size: 36px;
  margin-bottom: 20px;
}

/* Footer */
footer {
  background: #333;
  color: white;
  padding: 40px 20px;
  text-align: center;
}

footer p {
  margin: 5px 0;
}

/* Responsive */
@media (max-width: 768px) {
  .hero h1 { font-size: 32px; }
  .nav-links { gap: 15px; }
  .tours-grid { grid-template-columns: 1fr; }
}
```

### netlify.toml

```toml
[build]
  publish = "."

[[redirects]]
  from = "/404"
  to = "/404.html"
  status = 404

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
```

## Шаг 2: Добавьте изображения

Создайте папку `images/` и добавьте:
- `safari.jpg`
- `burj-khalifa.jpg`
- `abu-dhabi.jpg`

Или используйте placeholder изображения:
```
https://via.placeholder.com/400x200
```

## Шаг 3: Deploy

### Через Netlify Drop

1. Откройте [https://app.netlify.com/drop](https://app.netlify.com/drop)
2. Перетащите папку проекта
3. Готово!

### Через CLI

```bash
netlify deploy --prod --dir=.
```

### Через Git

```bash
git init
git add .
git commit -m "Initial commit"
# Push на GitHub и deploy через Netlify UI
```

## Расширения

- Добавьте Google Analytics
- Интегрируйте форму заявки
- Добавьте больше страниц
- Подключите CMS (Netlify CMS, Forestry)
- Добавьте мультиязычность

## Преимущества

- Нет сборки - быстрый деплой
- Минимальная настройка
- Легко редактировать
- Подходит для начинающих
