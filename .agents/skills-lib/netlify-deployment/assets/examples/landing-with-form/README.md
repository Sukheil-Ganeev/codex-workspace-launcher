# Landing with Form - Лендинг с формой заявки

Лендинг страница с формой бронирования и Telegram уведомлениями.

## Описание

Простой лендинг для туристических услуг с формой заявки, которая отправляет уведомления в Telegram.

**Идеально для:** рекламных кампаний, спецпредложений, лендинги конкретных туров.

## Структура проекта

```
landing-with-form/
├── index.html                    # Лендинг страница с формой
├── style.css                     # Стили
├── netlify.toml                  # Конфигурация Netlify
├── _redirects                    # Редиректы
└── netlify/functions/
    └── submit-form.js            # Обработчик формы
```

## Шаг 1: Создайте файлы

### index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Джип-сафари в ОАЭ | Бронирование</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="hero">
    <div class="container">
      <h1>🏜️ Джип-сафари в пустыне Дубая</h1>
      <p class="subtitle">Незабываемое приключение с катанием на багги, ужином и шоу</p>
      <div class="price">Всего 250 AED с человека</div>
    </div>
  </div>

  <div class="container">
    <section class="features">
      <div class="feature">
        <h3>🚙 Катание на джипах</h3>
        <p>Экстремальная езда по дюнам</p>
      </div>
      <div class="feature">
        <h3>🍽️ Ужин BBQ</h3>
        <p>Традиционный арабский ужин</p>
      </div>
      <div class="feature">
        <h3>💃 Шоу программа</h3>
        <p>Танец живота и файер-шоу</p>
      </div>
    </section>

    <section class="booking">
      <h2>Забронировать тур</h2>

      <form id="bookingForm">
        <input
          type="text"
          name="name"
          placeholder="Ваше имя"
          required
        >

        <input
          type="tel"
          name="phone"
          placeholder="Телефон (WhatsApp)"
          required
        >

        <input
          type="email"
          name="email"
          placeholder="Email (опционально)"
        >

        <input
          type="date"
          name="date"
          placeholder="Желаемая дата"
          required
        >

        <input
          type="number"
          name="people"
          placeholder="Количество человек"
          min="1"
          required
        >

        <textarea
          name="message"
          placeholder="Комментарий"
          rows="4"
        ></textarea>

        <!-- Honeypot для защиты от спама -->
        <input type="text" name="website" style="display:none;" tabindex="-1">

        <button type="submit">Отправить заявку</button>
      </form>

      <div id="formMessage"></div>
    </section>
  </div>

  <script>
    document.getElementById('bookingForm').addEventListener('submit', async (e) => {
      e.preventDefault();

      const button = e.target.querySelector('button');
      button.disabled = true;
      button.textContent = 'Отправка...';

      const formData = Object.fromEntries(new FormData(e.target));

      try {
        const response = await fetch('/.netlify/functions/submit-form', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
          showMessage('success', result.message);
          e.target.reset();
        } else {
          showMessage('error', result.error);
        }
      } catch (error) {
        showMessage('error', 'Ошибка отправки. Попробуйте позже.');
      } finally {
        button.disabled = false;
        button.textContent = 'Отправить заявку';
      }
    });

    function showMessage(type, text) {
      const div = document.getElementById('formMessage');
      div.className = type;
      div.textContent = text;
      setTimeout(() => div.textContent = '', 5000);
    }
  </script>
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.price {
  display: inline-block;
  background: rgba(255,255,255,0.2);
  padding: 15px 40px;
  border-radius: 50px;
  font-size: 24px;
  font-weight: bold;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin: 60px 0;
}

.feature {
  text-align: center;
  padding: 30px;
  background: #f8f9fa;
  border-radius: 12px;
}

.feature h3 {
  font-size: 24px;
  margin-bottom: 10px;
}

.booking {
  max-width: 600px;
  margin: 60px auto;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.booking h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #667eea;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

input, textarea {
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border 0.3s;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #667eea;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 18px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #5568d3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

#formMessage {
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
}

#formMessage.success {
  background: #d4edda;
  color: #155724;
}

#formMessage.error {
  background: #f8d7da;
  color: #721c24;
}

@media (max-width: 768px) {
  .hero h1 { font-size: 32px; }
  .subtitle { font-size: 16px; }
  .booking { padding: 20px; }
}
```

### netlify.toml

```toml
[build]
  publish = "."
  functions = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### netlify/functions/submit-form.js

Скопируйте содержимое из `templates/function-form-handler.js`

## Шаг 2: Настройка Telegram уведомлений

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Получите ваш Chat ID:
   - Отправьте боту любое сообщение
   - Откройте: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Найдите `"chat":{"id":123456789}`

## Шаг 3: Deploy

```bash
git init
git add .
git commit -m "Initial commit"
# Push на GitHub
```

В Netlify:
- Deploy from Git
- Добавьте Environment Variables:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`

## Шаг 4: Тестирование

1. Откройте ваш сайт
2. Заполните форму
3. Проверьте уведомление в Telegram

## Расширения

- Добавьте Google Analytics
- Интегрируйте с CRM
- Сохраняйте заявки в Google Sheets
- Добавьте Pixel Facebook
- Настройте email уведомления

## Troubleshooting

**Форма не отправляется:**
- Проверьте console в браузере
- Проверьте Netlify Functions logs

**Уведомления не приходят:**
- Проверьте BOT_TOKEN
- Проверьте CHAT_ID
- Убедитесь что бот может писать в чат
