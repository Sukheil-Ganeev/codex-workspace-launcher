# Карта интеграций Taplink

Визуальная карта всех интеграций Taplink по категориям: мессенджеры, соцсети, аналитика, платежи, CRM, автоматизация, email-маркетинг.

```mermaid
graph TB
    TAPLINK(("TAPLINK<br/>Business<br/>$4.50/мес"))

    subgraph MESSENGERS["Мессенджеры (Pro+)"]
        WA["WhatsApp<br/>wa.me + автотекст"]
        TG["Telegram<br/>Профиль / Бот / Канал"]
        VB["Viber"]
        FB_MSG["Facebook Messenger"]
        LINE["Line"]
        WECHAT["WeChat"]
        SKYPE["Skype"]
    end

    subgraph SOCIAL["Соцсети (Pro+, 70+ сервисов)"]
        INST["Instagram"]
        VK["VKontakte"]
        FACEBOOK["Facebook"]
        TIKTOK["TikTok"]
        YOUTUBE["YouTube"]
        TWITTER["X (Twitter)"]
        LINKEDIN["LinkedIn"]
        PINTEREST["Pinterest"]
    end

    subgraph ANALYTICS_SYS["Аналитика (Pro+)"]
        GA4["Google Analytics 4<br/>Measurement ID"]
        YM["Яндекс.Метрика<br/>ID счетчика"]
        FB_PIXEL["Facebook/Meta Pixel<br/>Pixel ID + Access Token"]
        TT_PIXEL["TikTok Pixel<br/>через HTML-блок"]
        GTAG["Google Tag Manager<br/>через HTML"]
    end

    subgraph PAYMENTS["Платежи (Business, 60+ провайдеров)"]
        STRIPE["Stripe<br/>~2.9% + $0.30<br/>135+ валют"]
        PAYPAL["PayPal<br/>~3.4%<br/>25+ валют"]
        PADDLE["Paddle<br/>5% + $0.50<br/>MoR (налоги)"]
        FONDY["Fondy<br/>~2.5-3.5%<br/>Европа, Азия"]
        YUKASSA["ЮКасса<br/>3.5%<br/>Карты РФ"]
        ROBOKASSA["Робокасса<br/>3.9%"]
        CLOUDPAY["CloudPayments<br/>3.9%"]
        TINKOFF["Тинькофф<br/>3.1%"]
        MANUAL["Ручная оплата<br/>Сбер, Kaspi, USDT, наличные"]
    end

    subgraph CRM_SYS["CRM"]
        CRM_BUILT["Встроенная CRM Taplink<br/>(Business)"]
        NOTION["Notion<br/>через Zapier/Make"]
        AMOCRM["AmoCRM<br/>через Albato/ApiX-Drive"]
        BITRIX["Bitrix24<br/>через Albato/ApiX-Drive"]
        HUBSPOT["HubSpot<br/>через Zapier/Pabbly"]
        GSHEETS["Google Sheets<br/>через Zapier/Make/Albato"]
    end

    subgraph AUTOMATION["Автоматизация (через Webhooks)"]
        MAKE["Make.com<br/>Custom Webhook<br/>Бесплатно (огр.)"]
        ZAPIER["Zapier<br/>Catch Hook<br/>Бесплатно (огр.)"]
        ALBATO["Albato<br/>Нативное приложение<br/>~30% дешевле Zapier"]
        PABBLY["Pabbly Connect<br/>Нативное приложение<br/>$249+ разовая"]
        APIX["ApiX-Drive<br/>Через Webhook<br/>Ориентирован СНГ"]
    end

    subgraph EMAIL_MKT["Email-маркетинг (Business)"]
        MAILCHIMP["Mailchimp<br/>API-ключ"]
        GETRESPONSE["GetResponse<br/>API-ключ"]
        MAILERLITE["MailerLite<br/>API-ключ"]
        BREVO["Brevo (Sendinblue)<br/>API-ключ"]
        KLAVIYO["Klaviyo<br/>API-ключ"]
    end

    TAPLINK ==>|"Блок Messaging Apps"| MESSENGERS
    TAPLINK ==>|"Блок Social Networks"| SOCIAL
    TAPLINK ==>|"Модули настроек"| ANALYTICS_SYS
    TAPLINK ==>|"Прием платежей"| PAYMENTS
    TAPLINK ==>|"Встроенная + Webhooks"| CRM_SYS
    TAPLINK ==>|"Webhooks HTTP POST"| AUTOMATION
    TAPLINK ==>|"Интеграция по API-ключу"| EMAIL_MKT

    style TAPLINK fill:#FF9800,color:#fff,stroke:#E65100,stroke-width:3px
    style MESSENGERS fill:#c8e6c9,stroke:#2E7D32
    style SOCIAL fill:#bbdefb,stroke:#1565C0
    style ANALYTICS_SYS fill:#fff9c4,stroke:#F9A825
    style PAYMENTS fill:#e1bee7,stroke:#7B1FA2
    style CRM_SYS fill:#ffccbc,stroke:#BF360C
    style AUTOMATION fill:#b2dfdb,stroke:#00695C
    style EMAIL_MKT fill:#f8bbd0,stroke:#880E4F
```

## Типы интеграций

```mermaid
graph LR
    subgraph TYPES["Способы интеграции"]
        NATIVE["Нативная<br/>(встроена в Taplink)"]
        WEBHOOK["Через Webhooks<br/>(HTTP POST)"]
        API_KEY["По API-ключу<br/>(email-сервисы)"]
        HTML["Через HTML-блок<br/>(скрипты)"]
    end

    NATIVE --> N1["Мессенджеры"]
    NATIVE --> N2["Соцсети"]
    NATIVE --> N3["Платежные провайдеры"]
    NATIVE --> N4["GA4 / Метрика / Pixel"]

    WEBHOOK --> W1["Make.com"]
    WEBHOOK --> W2["Zapier"]
    WEBHOOK --> W3["Собственный сервер"]

    API_KEY --> A1["Mailchimp"]
    API_KEY --> A2["GetResponse"]
    API_KEY --> A3["Albato"]
    API_KEY --> A4["Pabbly Connect"]

    HTML --> H1["TikTok Pixel"]
    HTML --> H2["Google Tag Manager"]
    HTML --> H3["Кастомные виджеты"]
    HTML --> H4["Калькуляторы"]

    style NATIVE fill:#c8e6c9,stroke:#2E7D32
    style WEBHOOK fill:#bbdefb,stroke:#1565C0
    style API_KEY fill:#fff9c4,stroke:#F9A825
    style HTML fill:#e1bee7,stroke:#7B1FA2
```

## Легенда

| Цвет | Категория | Тариф |
|------|-----------|-------|
| Зеленый | Мессенджеры | Pro+ |
| Синий | Соцсети | Pro+ |
| Желтый | Аналитика | Pro+ (модули), Business (глобальный HTML) |
| Фиолетовый | Платежи | Business |
| Оранжевый | CRM | Business (встроенная + webhooks) |
| Бирюзовый | Автоматизация | Business (webhooks) |
| Розовый | Email-маркетинг | Business (API-ключ) |
