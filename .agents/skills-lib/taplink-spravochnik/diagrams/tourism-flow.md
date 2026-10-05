# Бизнес-процесс туризма ОАЭ через Taplink

Полный путь клиента от первого контакта в Instagram до выполнения услуги и получения отзыва. Оптимизировано для туристического бизнеса семьи Сухейля.

```mermaid
graph TB
    subgraph DISCOVERY["1. Обнаружение"]
        IG["Турист видит<br/>Instagram / TikTok / YouTube"]
        QR["QR-код<br/>Отель / Флаер / Визитка"]
        WOM["Рекомендация<br/>от друзей / отзывы"]
        ADS["Таргетированная<br/>реклама"]
    end

    subgraph ENTRY["2. Переход"]
        BIO["Клик на ссылку в Bio<br/>taplink.cc/dubaitours"]
        UTM["UTM-метки для отслеживания<br/>utm_source / utm_medium"]
    end

    subgraph TAPLINK_PAGE["3. Taplink-страница"]
        MAIN["Главная мультиссылка"]
        TOURS["Экскурсии<br/>(Сухейль)"]
        TICKETS["Билеты в парки<br/>(Сухейль)"]
        YACHTS["Яхты 300+<br/>(Муфамад)"]
        CARS["Аренда авто<br/>(Марсель)"]
        TRANSFER["Трансферы + МВУ<br/>(Марсель)"]
    end

    subgraph CONVERSION["4. Конверсия"]
        FORM["Форма бронирования<br/>Имя, Телефон, Дата, Гости"]
        WA_CLICK["Клик WhatsApp<br/>wa.me + автотекст"]
        TG_CLICK["Клик Telegram<br/>t.me/username"]
        PHONE["Звонок по телефону"]
    end

    subgraph PAYMENT_FLOW["5. Оплата"]
        STRIPE_PAY["Stripe (карта)<br/>~2.9% комиссия"]
        PAYPAL_PAY["PayPal<br/>~3.4%"]
        MANUAL_PAY["Ручная оплата"]
        CASH["Наличные AED/USD"]
        KASPI["Kaspi (KZT)"]
        SBER["Сбер (RUB)"]
        USDT["USDT TRC-20<br/>~1 AED комиссия"]
    end

    subgraph PROCESSING["6. Обработка заявки"]
        WEBHOOK_SEND["Webhook<br/>leads.created / payments.created"]
        TG_NOTIFY["Telegram бот<br/>Уведомление менеджеру"]
        CRM_SAVE["CRM (Notion / Sheets)<br/>Запись заявки"]
        EMAIL_AUTO["Email автоответ<br/>Клиенту"]
    end

    subgraph MANAGER["7. Работа менеджера"]
        ASSIGN["Назначение менеджера:<br/>Сухейль / Марсель / Муфамад"]
        CONFIRM["Подтверждение бронирования<br/>WhatsApp клиенту"]
        DETAILS["Отправка деталей:<br/>Время, место встречи, что взять"]
    end

    subgraph SERVICE["8. Выполнение"]
        PICKUP["Встреча / Трансфер"]
        EXECUTE["Выполнение услуги"]
        PHOTOS["Фото / Видео для клиента"]
    end

    subgraph FOLLOWUP["9. После услуги"]
        REVIEW["Запрос отзыва<br/>Google / TripAdvisor"]
        REPEAT["Предложение<br/>других услуг"]
        REFERRAL["Реферальная скидка<br/>для друзей"]
    end

    IG --> BIO
    QR --> BIO
    WOM --> BIO
    ADS --> BIO
    BIO --> UTM
    UTM --> MAIN

    MAIN --> TOURS
    MAIN --> TICKETS
    MAIN --> YACHTS
    MAIN --> CARS
    MAIN --> TRANSFER

    TOURS --> FORM
    TOURS --> WA_CLICK
    TICKETS --> FORM
    YACHTS --> WA_CLICK
    CARS --> TG_CLICK
    TRANSFER --> PHONE

    FORM --> STRIPE_PAY
    FORM --> PAYPAL_PAY
    FORM --> MANUAL_PAY
    WA_CLICK --> MANUAL_PAY
    MANUAL_PAY --> CASH
    MANUAL_PAY --> KASPI
    MANUAL_PAY --> SBER
    MANUAL_PAY --> USDT

    STRIPE_PAY --> WEBHOOK_SEND
    PAYPAL_PAY --> WEBHOOK_SEND
    FORM --> WEBHOOK_SEND
    WEBHOOK_SEND --> TG_NOTIFY
    WEBHOOK_SEND --> CRM_SAVE
    WEBHOOK_SEND --> EMAIL_AUTO

    TG_NOTIFY --> ASSIGN
    ASSIGN --> CONFIRM
    CONFIRM --> DETAILS

    DETAILS --> PICKUP
    PICKUP --> EXECUTE
    EXECUTE --> PHOTOS

    PHOTOS --> REVIEW
    REVIEW --> REPEAT
    REPEAT --> REFERRAL
    REFERRAL -.->|"Новый клиент"| BIO

    style DISCOVERY fill:#e3f2fd,stroke:#1565C0
    style ENTRY fill:#e8f5e9,stroke:#2E7D32
    style TAPLINK_PAGE fill:#fff3e0,stroke:#E65100
    style CONVERSION fill:#fce4ec,stroke:#C62828
    style PAYMENT_FLOW fill:#f3e5f5,stroke:#7B1FA2
    style PROCESSING fill:#e0f2f1,stroke:#00695C
    style MANAGER fill:#fff9c4,stroke:#F9A825
    style SERVICE fill:#c8e6c9,stroke:#2E7D32
    style FOLLOWUP fill:#d1c4e9,stroke:#4527A0
```

## Воронка конверсии

```mermaid
graph TD
    subgraph FUNNEL["Воронка продаж туризм ОАЭ"]
        F1["Визит на Taplink<br/>100%"]
        F2["Клик на услугу<br/>30-50%"]
        F3["Заполнение формы / WhatsApp<br/>10-20%"]
        F4["Подтверждение менеджером<br/>70-80% от заявок"]
        F5["Оплата<br/>60-70% от подтвержденных"]
        F6["Выполнение услуги<br/>95%+"]
        F7["Отзыв<br/>20-30%"]
    end

    F1 --> F2 --> F3 --> F4 --> F5 --> F6 --> F7

    style F1 fill:#1565C0,color:#fff
    style F2 fill:#1976D2,color:#fff
    style F3 fill:#1E88E5,color:#fff
    style F4 fill:#42A5F5,color:#fff
    style F5 fill:#64B5F6,color:#fff
    style F6 fill:#90CAF9
    style F7 fill:#BBDEFB
```

## Распределение по менеджерам

```mermaid
graph LR
    subgraph TEAM["Семейная команда"]
        S["Сухейль<br/>Экскурсии + Билеты"]
        MU["Муфамад<br/>Paramount Yachts"]
        MA["Марсель<br/>Авто + Трансферы + МВУ"]
    end

    LEAD["Новая заявка"] --> ROUTE{"Тип услуги?"}

    ROUTE -->|"Экскурсия / Билет"| S
    ROUTE -->|"Яхта / Водные развлечения"| MU
    ROUTE -->|"Авто / Трансфер / МВУ"| MA

    style S fill:#c8e6c9,stroke:#2E7D32
    style MU fill:#bbdefb,stroke:#1565C0
    style MA fill:#fff9c4,stroke:#F9A825
```

## Легенда

| Этап | Ключевое действие | Инструмент |
|------|-------------------|------------|
| Обнаружение | Турист находит бизнес | Instagram, TikTok, QR-код |
| Переход | Клик на ссылку | Bio link + UTM |
| Taplink | Просмотр услуг | Мультиссылка, подстраницы |
| Конверсия | Заявка или сообщение | Форма, WhatsApp, Telegram |
| Оплата | Платеж | Stripe, ручная, крипто |
| Обработка | Автоматизация | Webhook, Telegram бот, CRM |
| Менеджер | Подтверждение | WhatsApp переписка |
| Выполнение | Услуга | Офлайн |
| После | Отзыв и повторные продажи | Google Reviews, рефералы |
