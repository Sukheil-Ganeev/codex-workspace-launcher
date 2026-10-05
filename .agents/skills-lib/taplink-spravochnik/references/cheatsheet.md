# Taplink -- Шпаргалка (Cheatsheet)

---

## Тарифы (Quick Reference)

| Тариф | 3 мес. | 12 мес. | /мес (год) | Ключевые возможности |
|-------|:------:|:-------:|:----------:|---------------------|
| **Basic** | $0 | $0 | **$0** | Текст, ссылки, FAQ, аватар |
| **Pro** | ~$12 | ~$6 | **~$2** | + мессенджеры, видео, карусель, карта, HTML, аналитика |
| **Business** | $27 | $54 | **$4.50** | + формы, платежи, CRM, домен, таймер, 512 страниц |

---

## Топ-15 блоков для туризма

| # | Блок | Тариф | Использование |
|---|------|-------|--------------|
| 1 | Link (Кнопка) | Basic | "Забронировать", "Купить билет" |
| 2 | Messaging Apps | Pro | WhatsApp + Telegram кнопки |
| 3 | Image Carousel | Pro | Фотогалерея экскурсий (до 15 фото) |
| 4 | Form and Payments | Business | Форма бронирования + оплата |
| 5 | Video | Pro | YouTube промо-ролики |
| 6 | Custom Block | Basic | Баннер акции, карточки услуг |
| 7 | Pricing Plans | Pro | Пакеты Standard/Premium/VIP |
| 8 | Timer | Business | "Акция заканчивается через..." |
| 9 | FAQ | Basic | "Что включено?", "Как добраться?" |
| 10 | Map | Pro | Офис в Tecom, точки встречи |
| 11 | Social Networks | Pro | Instagram, YouTube, TikTok |
| 12 | Media and Text | Pro | Преимущества с иконками |
| 13 | Avatar | Basic | Логотип компании |
| 14 | Text | Basic | Описания, приветствие |
| 15 | HTML Code | Pro | Виджеты, калькуляторы |

---

## Webhook формат

### Событие: leads.created (новая заявка)

```json
{
  "action": "leads.created",
  "data": {
    "profile_id": "56",
    "lead_id": "123",
    "lead_number": "45",
    "page_link": "https://taplink.cc/username",
    "ip": "192.168.1.1",
    "tms_created": "2026-02-14 12:00:00",
    "status_id": 1,
    "records": [
      { "value": "Jack", "type": "3", "title": "Name" },
      { "value": "+971501234567", "type": "1", "title": "Phone" },
      { "value": "jack@email.com", "type": "2", "title": "Email" }
    ]
  }
}
```

### Событие: payments.created (новый платеж)

```json
{
  "action": "payments.created",
  "data": {
    "order_id": "100",
    "order_number": "50",
    "budget": "250.00",
    "currency_code": "AED",
    "purpose": "Desert Safari VIP",
    "tms_modify": "2026-02-14 12:00:00",
    "records": [...]
  }
}
```

### Верификация подписи

```
Заголовок: taplink-signature
Алгоритм: HMAC-SHA1
Данные: raw body (JSON)
Ключ: SECRET PHRASE из настроек
```

### Retry Policy

8 попыток: 5мин -> 15мин -> 15мин -> 1ч -> 1ч -> 2ч -> 2ч -> 4ч (итого ~10.5ч)

---

## WhatsApp CTA-шаблоны

```
Экскурсии:
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Хочу%20забронировать%20экскурсию

Яхты:
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Интересует%20аренда%20яхты

Авто:
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Хочу%20арендовать%20автомобиль

Билеты:
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Хочу%20купить%20билеты

Трансфер:
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Нужен%20трансфер

МВУ:
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Хочу%20оформить%20МВУ
```

---

## CSS-хаки для Taplink

```css
/* Скругленные кнопки */
.link-block { border-radius: 50px !important; }

/* Кастомный шрифт (Google Fonts) */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');
body { font-family: 'Montserrat', sans-serif !important; }

/* Скрытие Taplink-логотипа (Business) */
.taplink-footer { display: none !important; }

/* Hover-эффект на кнопках */
.link-block:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
}

/* Градиентный фон текста */
.text-block h2 {
  background: linear-gradient(90deg, #2563eb, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## Аналитика -- подключение

| Сервис | Где настроить | Что вставить | Тариф |
|--------|-------------|-------------|-------|
| Google Analytics 4 | Модули > GA | Measurement ID (G-XXXXXXX) | Pro+ |
| Яндекс.Метрика | Модули > Метрика | ID счетчика (число) | Pro+ |
| Facebook Pixel | Модули > FB Pixel | Pixel ID + Access Token | Pro+ |
| TikTok Pixel | HTML-блок | `<script>` код пикселя | Pro+ |
| Google Tag Manager | HTML-блок (Business) | GTM `<script>` | Business |

### Автоматические события Facebook Pixel

| Событие | Описание |
|---------|----------|
| `taplink:link` | Клик на внешнюю ссылку |
| `taplink:email` | Клик на email |
| `taplink:phone` | Клик на телефон |
| `taplink:messengers:whatsapp` | Клик на WhatsApp |
| `taplink:messengers:telegram` | Клик на Telegram |
| `taplink:market:AddToCart` | Добавление в корзину |
| `taplink:market:Lead` | Новый лид |
| `taplink:market:Paid` | Оплата |

---

## Платежные провайдеры для ОАЭ

| Провайдер | Комиссия | AED | Подключение |
|-----------|----------|:---:|------------|
| Stripe | ~2.9% + $0.30 | Да | API ключи (sk_, pk_) |
| PayPal | ~3.4% + фикс | Частично | Client ID + Secret |
| Paddle | 5% + $0.50 | Да | MoR (налоги включены) |
| Ручная (Сбер) | 0% | -- | Инструкция клиенту |
| Ручная (Kaspi) | 0% | -- | Инструкция клиенту |
| Ручная (USDT) | ~$1 сеть | -- | Адрес кошелька TRC-20 |
| Ручная (наличные) | 0% | Да | Адрес офиса |

---

## UTM-метки по каналам

```
Instagram Bio:
?utm_source=instagram&utm_medium=bio&utm_campaign=main

Instagram Stories:
?utm_source=instagram&utm_medium=story&utm_campaign=promo

TikTok:
?utm_source=tiktok&utm_medium=bio&utm_campaign=main

YouTube:
?utm_source=youtube&utm_medium=description&utm_campaign=video

Telegram:
?utm_source=telegram&utm_medium=channel&utm_campaign=main

QR-код (офлайн):
?utm_source=qr&utm_medium=print&utm_campaign=flyer

WhatsApp рассылка:
?utm_source=whatsapp&utm_medium=broadcast&utm_campaign=promo
```

---

## Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Официальный сайт | https://taplink.at |
| Тарифы | https://taplink.at/en/pricing/ |
| Справочный центр | https://taplink.at/en/help/ |
| Документация Webhooks | https://taplink.at/en/dev/webhooks.html |
| Руководство по блокам | https://taplink.at/en/help/faq/page/blocks/ |
| Настройка платежей | https://taplink.at/en/guide/payments-configuration.html |
| Подключение домена | https://taplink.at/en/blog/custom-domain-support.html |
| Facebook Pixel | https://taplink.at/en/guide/facebook-pixel.html |
| Блог (инструкции) | https://taplink.at/en/blog/ |
| Albato (автоматизация) | https://albato.com/apps/taplink |
| Pabbly Connect | https://www.pabbly.com/connect/integrations/taplink/ |

---

## Кастомный домен -- DNS настройки

```
NS-серверы (менять у регистратора):
  ns1.taplink.cc
  ns2.taplink.cc

Время обновления: 1-48 часов
SSL: автоматический (бесплатный)
Тариф: Business

Рекомендуемые зоны: .com, .ae, .travel, .tours
```

---

## Статусы заявок (CRM)

| ID | Статус |
|----|--------|
| 1 | Новая |
| 2 | В работе |
| 3 | Завершена |
| 4 | Отклонена |

---

## Ключевые лимиты

| Параметр | Лимит |
|----------|-------|
| Страницы (Business) | до 512 |
| Фото в карусели | до 15 |
| Размер файла карусели | до 12 MB |
| Размер фона | до 5 MB |
| Цифровой товар | до 256 MB |
| Аватар | 1080x1080 px |
| Видео обложка | 1020x574 px (16:9) |
| Мессенджеры | WhatsApp, Telegram, Viber, FB Messenger, Skype, Discord, Line + др. |
| Соцсети | 70+ платформ |
| Платежные провайдеры | 60+ |
| Языки интерфейса | 11 (арабский НЕ поддерживается) |
