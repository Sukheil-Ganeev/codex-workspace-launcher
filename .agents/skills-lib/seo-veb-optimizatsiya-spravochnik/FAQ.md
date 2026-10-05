# FAQ: SEO веб-оптимизация-справочник

## Часто задаваемые вопросы

### Общие вопросы

**Q: Для кого этот справочник?**
A: Для владельцев туристических сайтов, SEO специалистов, веб-разработчиков, контент-менеджеров. Требуется базовое понимание HTML.

**Q: Сколько времени нужно прочитать SKILL.md?**
A: 45-50 минут. Это comprehensive guide, но написан простым языком.

**Q: Это только для Дубая или для всего ОАЭ?**
A: Примеры сфокусированы на Дубай (большой рынок), но техники работают для Abu Dhabi, Sharjah, и всех emiratов.

---

### SEO вопросы

**Q: Как быстро видны результаты SEO?**
A: 
- Quick wins (meta tags): 2-4 недели
- Content ranking: 4-8 недель  
- Full results: 3-6 месяцев

Не ожидай instant results. SEO это долгосрочная инвестиция.

**Q: Какие keywords выбрать?**
A: Правило:
1. High volume + Low difficulty (quick wins)
2. Medium volume + Low difficulty (fast ranking)
3. Low volume + High intent (high conversion)

Используй `scripts/09-keyword-research.js` для анализа.

**Q: Нужны ли backlinks?**
A: Да, но quality >> quantity. 5 backlinks от DA50+ > 100 от DA10.

НИКОГДА не покупай backlinks (Google пенализирует).

**Q: Core Web Vitals важны?**
A: Да, это ranking signal. LCP < 2.5s критично.

Используй `scripts/12-performance-monitor.js` для отслеживания.

---

### Техническое

**Q: Нужен ли Node.js для использования справочника?**
A: Нет, SKILL.md и templates работают без Node.js.

Но scripts требуют Node.js 18+. Если не хочешь использовать scripts, можешь только читать и copy-paste templates.

**Q: Как настроить Google API credentials?**
A: 
1. Create Google Cloud Project
2. Enable Search Console API, Analytics API
3. Create Service Account
4. Download JSON credentials
5. Copy в `scripts/config/google-credentials.json`

Подробнее в `docs/API_INTEGRATION_GUIDE.md`.

**Q: Какой Node.js версии нужен?**
A: 18+. Проверь: `node --version`

**Q: Можно ли использовать на Windows?**
A: Да, все работает на Windows, Mac, Linux.

Git Bash рекомендуется на Windows.

---

### Local SEO

**Q: Что такое Local Pack?**
A: Топ-3 результаты в Google поиске с картой для локальных запросов.

Пример: "Restaurants near me" показывает Local Pack + organic results.

**Q: Как оптимизировать Google My Business?**
A: 
1. Заполни все поля (address, phone, website, hours)
2. Загрузи 20+ качественных фото
3. Добавь service areas (Dubai, Abu Dhabi)
4. Запроси reviews от клиентов
5. Отвечай на все reviews в течение 48 часов

**Q: Что такое NAP consistency?**
A: Name, Address, Phone одинаковы везде (GMB, website, citations).

Если "Your Tours LLC" в GMB но "Your Tours Ltd." на сайте — это ошибка.

---

### Schema & Structured Data

**Q: Зачем нужна schema?**
A: 
1. Помогает Google лучше understand контент
2. Rich snippets в поиске (ratings, price, availability)
3. CTR увеличивается на 15-30%

**Q: Какую schema использовать?**
A: Для туризма:
- Product (для туров с ценой)
- LocalBusiness (для офиса)
- Event (для специальных events)
- FAQ (для FAQ page)

Примеры в `assets/templates/`.

**Q: Как проверить что schema правильна?**
A: 
1. Используй Google Rich Results Test
2. Или `scripts/07-schema-validator.js`

**Q: Какой format лучше: JSON-LD или Microdata?**
A: JSON-LD. Это recommend Google и самый простой.

---

### Content & Keywords

**Q: Какой длины должен быть контент?**
A: 
- Product pages: 800-1500 слов
- Blog posts: 1500+ слов
- Supporting pages: 300-800 слов

Главное: качество > количество.

**Q: Что такое keyword density?**
A: % ключевого слова в тексте.

Пример: "Dubai desert safari" в 1500-словной статье = 1-3% (15-45 раз).

**Q: Как найти keywords которые ищут потенциальные клиенты?**
A: 
1. Google Keyword Planner
2. Google Trends (seasonal)
3. Answer the Public (questions)
4. Competitor keywords analysis

Используй `scripts/09-keyword-research.js`.

---

### Analytics & Tracking

**Q: Как начать с Google Search Console?**
A: 
1. Create account на search.google.com
2. Add property (твой сайт)
3. Verify (через DNS или HTML file)
4. Enable API в Google Cloud Console
5. Start monitoring

**Q: Какие metrics смотреть?**
A: 
- Impressions: сколько раз показали в поиске
- Clicks: сколько нажали
- CTR: clicks / impressions
- Average Position: средняя позиция в выдаче

**Q: Как настроить Google Analytics 4?**
A: 
1. Create GA4 property
2. Add tracking ID на сайт
3. Configure goals/conversions (для bookings)
4. Link с Google Search Console

**Q: Что такое conversion в туризме?**
A: Booking tour, заполнение contact form, phone call.

Depends что считаешь success для своего бизнеса.

---

### Performance & Speed

**Q: Как улучшить LCP (Largest Contentful Paint)?**
A: 
1. Optimize hero image (WebP, smaller size)
2. Inline critical CSS
3. Defer non-critical JS
4. Use CDN для images

Подробнее в `references/03-technical-performance.md`.

**Q: Что делать если CLS (Cumulative Layout Shift) высокий?**
A: 
1. Add width/height для всех images
2. Reserve space для ads/embeds
3. Avoid inserting content выше existing content
4. Use CSS transform для animations (не margin)

**Q: Как проверить Core Web Vitals своего сайта?**
A: 
1. PageSpeed Insights (Google)
2. lighthouse CLI
3. `scripts/12-performance-monitor.js`

---

### Troubleshooting

**Q: Мой сайт в Google но low traffic. Почему?**
A: 
1. Low CTR? Улучши title/description
2. Low position? Улучши content quality + backlinks
3. High bounce rate? Улучши mobile UX + page speed
4. Low conversion? Улучши CTA + trust signals

Смотри раздел 9 в SKILL.md (Troubleshooting).

**Q: Я не вижу rich snippets в поиске**
A: 
1. Проверь schema валиден (Rich Results Test)
2. Дождись indexing (может быть 1-2 недели)
3. Убедись page is indexed (GSC → Coverage)

**Q: Мой ranking упал. Что делать?**
A: 
1. Check Google Search Console для errors
2. Check page speed (LCP, CLS)
3. Check competitors (может обогнали)
4. Check backlinks (может спам-ссылки?)

Разберись за день, не за месяц (используй alerts).

---

### Business Questions

**Q: Сколько стоит SEO?**
A: 
- DIY (самостоятельно): Time cost
- Agency: $1000-5000/month
- Hybrid: использовать tools + agency

Этот справочник + scripts помогают DIY подход.

**Q: За сколько времени окупится SEO?**
A: Зависит от:
- Начальный ranking (если не ранжируется, дольше)
- Конкуренция (более конкурентный niche = дольше)
- Бюджет контента (больше контента = быстрее)

Обычно: 3-6 месяцев до видимых results.

**Q: Что если я нанял SEO агентство?**
A: Все равно прочитай этот справочник. Тогда сможешь:
- Понимать что агентство делает
- Проверять их work
- Знать reasonable expectations

---

### Advanced Questions

**Q: Что такое pillar-cluster модель?**
A: Content organization:
- Pillar: большая page про broad topic (1500+ слов, все subtopics)
- Clusters: specific pages для каждого subtopic (800+ слов)
- Internal linking между ними

Пример: Pillar "Dubai Tours" → Clusters "Desert Safari", "Yacht Tours", "City Tours"

**Q: Зачем нужен hreflang tag?**
A: Для multi-language сайтов. Говорит Google какая версия для какого language/region.

Пример: English version для en-US, Russian для ru, Arabic для ar-AE.

**Q: Что такое canonical tag?**
A: Говорит Google что это duplicate page и вот canonical version которую ранжировать.

Пример: /tour/desert-safari и /tours/desert-safari — оба на canonical /tour/desert-safari.

---

## Не нашел ответ?

- Смотри `docs/TROUBLESHOOTING.md`
- Читай `experience/_index.md` для lessons learned
- Смотри примеры в `assets/examples/`

---

**Last updated:** 2026-02-04
