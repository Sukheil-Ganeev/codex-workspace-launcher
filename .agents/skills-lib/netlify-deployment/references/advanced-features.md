# Advanced Features: Расширенные возможности Netlify

Продвинутые функции Netlify для опытных пользователей.

---

## Split Testing (A/B Testing)

### Описание

Разделяйте трафик между разными версиями сайта для тестирования гипотез.

### Настройка через UI

```
Site Settings → Split Testing → Create split test
```

**Параметры:**
- Выберите деплои для сравнения
- Укажите процент трафика для каждого варианта
- Netlify автоматически распределяет пользователей

### Настройка через netlify.toml

```toml
[[split_tests]]
  path = "/*"
  branches = ["main", "new-design"]
  weights = [80, 20]  # 80% → main, 20% → new-design
```

### Пример использования

**Сценарий:** Тестирование нового дизайна главной страницы

```toml
# netlify.toml
[[split_tests]]
  path = "/"
  branches = ["production", "redesign"]
  weights = [90, 10]  # Показываем новый дизайн 10% пользователей
```

**Результат:**
- 90% трафика → текущий дизайн (безопасно)
- 10% трафика → новый дизайн (тестирование)
- Пользователи сохраняют свою версию в cookie

### Отслеживание результатов

```js
// Google Analytics
gtag('event', 'split_test', {
  'test_name': 'homepage_redesign',
  'variant': 'new_design'
});

// Netlify Analytics (платная функция)
// Автоматически отслеживает split tests
```

### Завершение теста

```
Split Testing → End test → Choose winning variant
```

Netlify переведёт 100% трафика на победившую версию.

---

## Deploy Previews

### Автоматические Preview для Pull Requests

**Как работает:**
1. Создаёте Pull Request в GitHub
2. Netlify автоматически создаёт preview deploy
3. Получаете уникальный URL: `deploy-preview-123--site.netlify.app`
4. Команда проверяет изменения ДО мержа
5. Каждый новый коммит → обновление preview

### Настройка

```toml
# netlify.toml
[context.deploy-preview]
  command = "npm run build:preview"
  publish = "build"

[context.deploy-preview.environment]
  REACT_APP_ENV = "preview"
  REACT_APP_API_URL = "https://staging-api.example.com"
```

### GitHub Checks интеграция

**Автоматически в PR:**
- ✅ Deploy Preview — успешно
- 🔗 Ссылка на preview deploy
- 📊 Lighthouse scores
- ⚠️ Build warnings

### Настройка через UI

```
Site Settings → Build & Deploy → Deploy contexts
```

**Опции:**
- Deploy Previews: All / None / Only on PRs from team
- Branch deploys: All / None / Specific branches
- Deploy notifications: Slack, GitHub, email

---

## Build Hooks

### Описание

Webhooks для триггера билдов из внешних систем.

### Создание Build Hook

```
Site Settings → Build & Deploy → Build hooks → Add build hook
```

**Параметры:**
- Имя hook (например, "Contentful publish")
- Ветка для билда (main, staging, etc)

**Получаете URL:**
```
https://api.netlify.com/build_hooks/abc123xyz
```

### Использование

**Простой POST запрос:**
```bash
curl -X POST -d {} https://api.netlify.com/build_hooks/abc123xyz
```

**С параметрами:**
```bash
curl -X POST -d '{"trigger_title":"Manual rebuild"}' \
  https://api.netlify.com/build_hooks/abc123xyz
```

### Интеграции

**Contentful (headless CMS):**
```
Contentful → Settings → Webhooks → Add webhook
URL: https://api.netlify.com/build_hooks/abc123xyz
Trigger: Publish entry
```

**Shopify:**
```
Shopify → Settings → Notifications → Webhooks
Event: Product update
URL: https://api.netlify.com/build_hooks/abc123xyz
```

**Sanity.io:**
```js
// sanity.json
{
  "hooks": {
    "afterPublish": [
      {
        "url": "https://api.netlify.com/build_hooks/abc123xyz",
        "method": "POST"
      }
    ]
  }
}
```

**Zapier/Make.com:**
```
Trigger: Google Sheets row added
Action: Webhook POST to Netlify build hook
```

### Scheduled builds (через Zapier)

```
Zapier → Schedule
Trigger: Every day at 3 AM
Action: POST to Netlify build hook
```

Полезно для:
- Обновления данных из API
- Ежедневный rebuild для fresh data
- Backup deploys

---

## Notifications

### Deploy Notifications

**Типы уведомлений:**
- Deploy started
- Deploy succeeded
- Deploy failed
- Deploy locked
- Form submissions

### Slack интеграция

```
Site Settings → Build & Deploy → Deploy notifications → Add notification → Slack
```

**Выберите события:**
- ✅ Deploy succeeded
- ✅ Deploy failed
- ⚠️ Deploy preview ready

**Результат в Slack:**
```
[Netlify] Deploy succeeded ✅
Site: my-awesome-site
Branch: main
Deploy URL: https://my-site.netlify.app
Deploy time: 45s
```

### Email notifications

```
Add notification → Email
```

Введите email и выберите события.

### Discord/Teams

**Через Webhook URL:**
```
Add notification → Outgoing webhook
Webhook URL: https://discord.com/api/webhooks/...
Event: Deploy succeeded
```

### GitHub Commit Status

```
Add notification → GitHub commit status
```

**Добавляет в PR:**
- ✅ netlify/site-name/deploy-preview — Deploy succeeded
- 🔗 Preview URL

---

## Analytics

### Netlify Analytics (платная функция)

**Стоимость:** $9/месяц на сайт

**Возможности:**
- Server-side analytics (не блокируется ad blockers)
- Нет JavaScript трекеров
- 100% точность
- Privacy-friendly (GDPR compliant)

**Данные:**
- Page views
- Unique visitors
- Top pages
- Traffic sources
- Bandwidth usage
- 404 errors

### Включение

```
Site Settings → Analytics → Enable analytics
```

### Преимущества над Google Analytics

| Функция | Netlify Analytics | Google Analytics |
|---------|------------------|------------------|
| **Ad blocker proof** | ✅ | ❌ |
| **Privacy** | ✅ Минимум данных | ⚠️ Много данных |
| **JavaScript required** | ❌ | ✅ |
| **GDPR cookie banner** | ❌ | ✅ |
| **Real-time** | ❌ | ✅ |
| **Custom events** | ❌ | ✅ |

**Вывод:** Netlify Analytics для базовой статистики, Google Analytics для детального анализа.

---

## Forms

### Netlify Forms (встроенная обработка форм)

**Возможности:**
- Обработка форм без backend
- Спам защита (honeypot, reCAPTCHA)
- Email notifications
- Webhook интеграция
- 100 submissions/месяц на Free tier

### Базовая форма

```html
<form name="contact" method="POST" data-netlify="true">
  <input type="hidden" name="form-name" value="contact" />
  <input type="text" name="name" placeholder="Name" required />
  <input type="email" name="email" placeholder="Email" required />
  <textarea name="message" placeholder="Message"></textarea>
  <button type="submit">Send</button>
</form>
```

### Спам защита

**Honeypot (рекомендуется):**
```html
<form name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="contact" />

  <!-- Honeypot field (скрыт CSS) -->
  <p style="display:none">
    <label>Don't fill this: <input name="bot-field" /></label>
  </p>

  <input type="text" name="name" />
  <button type="submit">Send</button>
</form>
```

**reCAPTCHA:**
```html
<form name="contact" method="POST" data-netlify="true" data-netlify-recaptcha="true">
  <input type="hidden" name="form-name" value="contact" />
  <input type="text" name="name" />

  <!-- reCAPTCHA -->
  <div data-netlify-recaptcha="true"></div>

  <button type="submit">Send</button>
</form>
```

### Email notifications

```
Site Settings → Forms → Form notifications → Add notification → Email notification
```

**Настройка:**
- Email to notify: `your-email@example.com`
- Subject: `New form submission`
- Email template: Customize или default

### Webhook для форм

```
Form notifications → Add notification → Outgoing webhook
```

**Пример обработчика:**
```js
// netlify/functions/form-handler.js
exports.handler = async (event) => {
  const formData = JSON.parse(event.body);

  // Отправка в CRM, базу данных, etc
  await sendToCRM(formData);

  return {
    statusCode: 200,
    body: JSON.stringify({ message: 'Processed' })
  };
};
```

---

## Identity (User Management)

### Netlify Identity

Встроенная система управления пользователями.

**Возможности:**
- User registration/login
- Email confirmation
- Password reset
- OAuth providers (Google, GitHub, GitLab)
- JWT tokens
- Role-based access control

### Включение

```
Site Settings → Identity → Enable Identity
```

### Registration settings

```
Identity → Registration → Open / Invite only
```

**Open:** Любой может зарегистрироваться
**Invite only:** Только по приглашениям

### External providers

```
Identity → External providers → Add provider
```

**Доступные провайдеры:**
- Google
- GitHub
- GitLab
- Bitbucket

### Интеграция в код

```html
<!-- Add Identity widget -->
<script src="https://identity.netlify.com/v1/netlify-identity-widget.js"></script>
```

```js
// JavaScript
netlifyIdentity.on('init', user => {
  if (!user) {
    netlifyIdentity.open(); // Show login modal
  } else {
    console.log('Logged in as:', user.email);
  }
});

// Logout
netlifyIdentity.logout();
```

### Protected pages

```toml
# netlify.toml
[[redirects]]
  from = "/admin/*"
  to = "/admin/:splat"
  status = 200
  conditions = {Role = ["admin"]}
  force = true
```

---

## Edge Functions (Beta)

### Описание

Функции, которые запускаются на edge (ближе к пользователю).

**Отличие от Netlify Functions:**
- Netlify Functions → AWS Lambda (региональные)
- Edge Functions → Deno Deploy (глобальные, быстрее)

### Создание

```js
// netlify/edge-functions/hello.js
export default async (request, context) => {
  return new Response("Hello from the edge!");
};

export const config = { path: "/hello" };
```

### Использование

**Персонализация:**
```js
export default async (request, context) => {
  const country = context.geo.country.code;

  return new Response(`Hello from ${country}!`);
};
```

**A/B testing:**
```js
export default async (request, context) => {
  const variant = Math.random() < 0.5 ? 'A' : 'B';

  return context.rewrite(`/variants/${variant}`);
};
```

---

## Large Media (Git LFS)

### Описание

Хранение больших файлов (изображения, видео) вне Git.

**Проблема:** Git плохо работает с большими файлами
**Решение:** Netlify Large Media через Git LFS

### Настройка

```bash
# Установка Git LFS
git lfs install

# Отслеживание типов файлов
git lfs track "*.jpg"
git lfs track "*.png"
git lfs track "*.mp4"

# Commit .gitattributes
git add .gitattributes
git commit -m "Setup Git LFS"
```

### Image transformation

```html
<!-- Оригинал -->
<img src="/images/photo.jpg" />

<!-- С трансформацией -->
<img src="/images/photo.jpg?nf_resize=fit&w=400&h=300" />
```

**Параметры:**
- `nf_resize=fit` / `smartcrop`
- `w=400` - ширина
- `h=300` - высота
- `q=80` - качество (1-100)

---

## Snippets (Code Injection)

### Описание

Вставка кода (analytics, chat widgets) без изменения исходников.

### Создание snippet

```
Site Settings → Build & Deploy → Post processing → Snippet injection
```

**Типы:**
- Before `</head>`
- Before `</body>`
- Custom position (с селектором)

### Примеры

**Google Analytics:**
```html
<!-- Before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

**Crisp Chat:**
```html
<!-- Before </body> -->
<script type="text/javascript">
  window.$crisp=[];
  window.CRISP_WEBSITE_ID="YOUR_WEBSITE_ID";
  (function(){
    d=document;s=d.createElement("script");
    s.src="https://client.crisp.chat/l.js";
    s.async=1;d.getElementsByTagName("head")[0].appendChild(s);
  })();
</script>
```

---

## Asset Optimization

### Автоматическая оптимизация (платная функция)

```
Site Settings → Build & Deploy → Post processing → Asset optimization
```

**Включает:**
- ✅ Pretty URLs (убирает .html)
- ✅ Bundle CSS
- ✅ Minify CSS
- ✅ Minify JS
- ✅ Compress images
- ✅ Lossless image compression

### Prerendering (для SPA)

```
Post processing → Prerendering
```

**Что делает:**
- Рендерит SPA страницы в статический HTML
- Улучшает SEO
- Ускоряет первую загрузку

**Работает с:**
- React
- Vue
- Angular
- Any SPA framework

---

## Build Plugins

### Описание

Расширения для кастомизации build процесса.

### Популярные плагины

**Next.js Essential:**
```toml
[[plugins]]
  package = "@netlify/plugin-nextjs"
```

**Lighthouse CI:**
```toml
[[plugins]]
  package = "@netlify/plugin-lighthouse"

[[plugins.inputs.audits]]
  path = "/"
```

**Gatsby Cache:**
```toml
[[plugins]]
  package = "netlify-plugin-gatsby-cache"
```

**Image Optimizer:**
```toml
[[plugins]]
  package = "netlify-plugin-image-optim"
```

### Создание custom plugin

```js
// netlify-plugin-custom/index.js
module.exports = {
  onPreBuild: async ({ utils }) => {
    console.log('Running before build...');
  },

  onBuild: async ({ utils }) => {
    console.log('Running during build...');
  },

  onPostBuild: async ({ utils }) => {
    console.log('Running after build...');
  },

  onSuccess: async ({ utils }) => {
    console.log('Build succeeded!');
  },

  onError: async ({ utils }) => {
    console.log('Build failed!');
  }
};
```

```toml
# netlify.toml
[[plugins]]
  package = "./netlify-plugin-custom"
```

---

## Полезные ссылки

- 📖 [SKILL.md](../SKILL.md) - Основной гайд
- ❓ [FAQ](faq.md) - Частые вопросы
- 🔧 [Troubleshooting](troubleshooting.md) - Решение проблем
- 🔒 [Security Guide](security-guide.md) - Безопасность
