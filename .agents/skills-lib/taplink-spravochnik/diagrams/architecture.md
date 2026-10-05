# Архитектура интеграций Taplink

Полная схема потока данных от Taplink-страницы до конечных систем: CRM, мессенджеры, аналитика, платежи.

```mermaid
graph TB
    subgraph CLIENT["Клиент (турист)"]
        IG["Instagram Bio / TikTok / QR"]
        VISIT["Посещение Taplink-страницы"]
        ACTION["Действие клиента"]
    end

    subgraph TAPLINK["Taplink Page (Business)"]
        PAGE["taplink.cc/dubaitours<br/>или dubai-tours.ae"]
        BLOCKS["Блоки контента:<br/>Кнопки | Карусель | Видео | FAQ"]
        FORM["Форма бронирования:<br/>Имя, Телефон, Дата, Гости"]
        SHOP["Магазин / Витрина:<br/>Экскурсии, Билеты"]
        PAYMENT["Прием оплаты:<br/>Stripe / PayPal / Manual"]
        MSGS["Кнопки мессенджеров:<br/>WhatsApp | Telegram"]
    end

    subgraph WEBHOOK_LAYER["Webhook Layer"]
        WH["HTTP POST + HMAC-SHA1"]
        WH_LEADS["leads.created"]
        WH_PAY["payments.created"]
    end

    subgraph MIDDLEWARE["Сервер / Автоматизация"]
        NODE["Node.js сервер<br/>(Express + crypto)"]
        MAKE["Make.com<br/>(Custom Webhook)"]
        ALBATO["Albato<br/>(нативная интеграция)"]
        ZAPIER["Zapier<br/>(Catch Hook)"]
    end

    subgraph DESTINATIONS["Конечные системы"]
        TG_BOT["Telegram Bot<br/>Уведомление менеджеру"]
        NOTION["Notion CRM<br/>База заявок"]
        GSHEETS["Google Sheets<br/>Таблица заказов"]
        EMAIL["Email<br/>Автоответ клиенту"]
        AMOCRM["AmoCRM / Bitrix24"]
    end

    subgraph ANALYTICS["Аналитика"]
        GA4["Google Analytics 4"]
        YANDEX["Яндекс.Метрика"]
        PIXEL["Facebook/Meta Pixel"]
        TIKTOK_P["TikTok Pixel"]
    end

    IG --> VISIT
    VISIT --> PAGE
    PAGE --> BLOCKS
    PAGE --> FORM
    PAGE --> SHOP
    PAGE --> MSGS
    FORM --> PAYMENT
    SHOP --> PAYMENT

    FORM --> WH
    PAYMENT --> WH
    WH --> WH_LEADS
    WH --> WH_PAY

    WH_LEADS --> NODE
    WH_LEADS --> MAKE
    WH_LEADS --> ALBATO
    WH_LEADS --> ZAPIER
    WH_PAY --> NODE
    WH_PAY --> MAKE

    NODE --> TG_BOT
    NODE --> NOTION
    MAKE --> GSHEETS
    MAKE --> EMAIL
    ALBATO --> AMOCRM
    ZAPIER --> NOTION

    PAGE -.-> GA4
    PAGE -.-> YANDEX
    PAGE -.-> PIXEL
    PAGE -.-> TIKTOK_P

    MSGS -->|"wa.me / t.me"| CLIENT

    style CLIENT fill:#e8f4fd,stroke:#2196F3
    style TAPLINK fill:#fff3e0,stroke:#FF9800
    style WEBHOOK_LAYER fill:#fce4ec,stroke:#E91E63
    style MIDDLEWARE fill:#e8f5e9,stroke:#4CAF50
    style DESTINATIONS fill:#f3e5f5,stroke:#9C27B0
    style ANALYTICS fill:#fff9c4,stroke:#FFC107
```

## Легенда

| Элемент | Описание |
|---------|----------|
| Сплошные линии | Основной поток данных |
| Пунктирные линии | Аналитические трекеры (JS-скрипты) |
| CLIENT | Точки входа клиента |
| TAPLINK | Платформа Taplink (тариф Business) |
| WEBHOOK LAYER | Исходящие HTTP POST запросы |
| MIDDLEWARE | Серверы обработки / платформы автоматизации |
| DESTINATIONS | Конечные системы получения данных |
| ANALYTICS | Системы аналитики и отслеживания |
