# Сравнение тарифов Taplink: Basic vs Pro vs Business

Детальное сравнение трех тарифных планов Taplink с рекомендациями для туристического бизнеса в ОАЭ.

```mermaid
graph TB
    subgraph BASIC["BASIC -- Бесплатно"]
        B_PRICE["$0 / навсегда"]
        B1["Avatar (Аватар)"]
        B2["Link (Кнопки-ссылки)"]
        B3["Text (Текст)"]
        B4["FAQ (Вопросы-ответы)"]
        B5["Separator (Разделитель)"]
        B6["Icon and Text"]
        B7["Custom Block (базовый)"]
        B_NO1["Нет мессенджеров"]
        B_NO2["Нет видео"]
        B_NO3["Нет форм"]
        B_NO4["Нет платежей"]
        B_NO5["Нет кастомного домена"]
    end

    subgraph PRO["PRO -- ~$2/мес (при оплате за год)"]
        P_PRICE["$6/3мес | $8.40/6мес | $12/12мес"]
        P1["Все блоки Basic +"]
        P2["Messaging Apps (WhatsApp, Telegram, Viber)"]
        P3["Social Networks (70+ сервисов)"]
        P4["Video (YouTube/Vimeo/TikTok)"]
        P5["Image Carousel (до 15 фото)"]
        P6["Map (Карта)"]
        P7["HTML Code (на странице)"]
        P8["Media and Text"]
        P9["Pricing Plans"]
        P10["Navigation Menu"]
        P11["Open Graph (соцсети)"]
        P12["GA4 / Метрика / Pixel"]
        P_NO1["Нет форм бронирования"]
        P_NO2["Нет платежей"]
        P_NO3["Нет таймера"]
        P_NO4["Нет подстраниц"]
    end

    subgraph BUSINESS["BUSINESS -- ~$4.50/мес (при оплате за год)"]
        BU_PRICE["$27/3мес | $37.80/6мес | $54/12мес"]
        BU1["Все блоки Pro +"]
        BU2["Form and Payments (формы + оплата)"]
        BU3["Timer (обратный отсчет)"]
        BU4["Digital Products (PDF, ваучеры)"]
        BU5["Pages (до 512 подстраниц)"]
        BU6["Глобальный HTML (в head)"]
        BU7["Встроенная CRM"]
        BU8["Webhooks (HMAC-SHA1)"]
        BU9["Кастомный домен + SSL"]
        BU10["Email-маркетинг (API)"]
        BU11["60+ платежных провайдеров"]
        BU12["Уведомления: Telegram/Email/Slack"]
        BU13["Магазин с корзиной"]
        BU14["Промо-коды и скидки"]
    end

    style BASIC fill:#f5f5f5,stroke:#9E9E9E
    style PRO fill:#e3f2fd,stroke:#1565C0
    style BUSINESS fill:#c8e6c9,stroke:#2E7D32,stroke-width:3px

    style B_NO1 fill:#ffcdd2,stroke:#C62828
    style B_NO2 fill:#ffcdd2,stroke:#C62828
    style B_NO3 fill:#ffcdd2,stroke:#C62828
    style B_NO4 fill:#ffcdd2,stroke:#C62828
    style B_NO5 fill:#ffcdd2,stroke:#C62828
    style P_NO1 fill:#ffcdd2,stroke:#C62828
    style P_NO2 fill:#ffcdd2,stroke:#C62828
    style P_NO3 fill:#ffcdd2,stroke:#C62828
    style P_NO4 fill:#ffcdd2,stroke:#C62828
```

## Стоимость по периодам

```mermaid
graph LR
    subgraph PRICING["Стоимость тарифов"]
        subgraph M3["3 месяца"]
            M3B["Basic: $0"]
            M3P["Pro: ~$12"]
            M3BU["Business: $27"]
        end

        subgraph M6["6 месяцев (-30%)"]
            M6B["Basic: $0"]
            M6P["Pro: ~$8.40"]
            M6BU["Business: $37.80"]
        end

        subgraph M12["12 месяцев (-50%)"]
            M12B["Basic: $0"]
            M12P["Pro: ~$6"]
            M12BU["Business: $54"]
        end

        subgraph MONTHLY["Эффективно в месяц (при годовой)"]
            MYB["Basic: $0/мес"]
            MYP["Pro: ~$2/мес"]
            MYBU["Business: $4.50/мес"]
        end
    end

    style M12 fill:#c8e6c9,stroke:#2E7D32
    style MONTHLY fill:#fff9c4,stroke:#F9A825
```

## Рекомендация по сценарию

```mermaid
graph TD
    START{"Какой у вас<br/>сценарий?"}

    START -->|"Только ссылки<br/>в соцсети"| REC_BASIC["Basic (бесплатно)<br/>Простая мультиссылка"]
    START -->|"Мессенджеры +<br/>фото + видео"| REC_PRO["Pro (~$2/мес)<br/>Визитка с контактами"]
    START -->|"Формы + платежи +<br/>автоматизация"| REC_BIZ["Business ($4.50/мес)<br/>РЕКОМЕНДУЕТСЯ для туризма"]

    REC_BIZ --> WHY{"Почему Business<br/>для туризма ОАЭ?"}
    WHY --> W1["Формы бронирования<br/>с кастомными полями"]
    WHY --> W2["60+ платежных провайдеров<br/>0% комиссия Taplink"]
    WHY --> W3["Webhooks для автоматизации<br/>Telegram + CRM"]
    WHY --> W4["Кастомный домен<br/>dubai-tours.ae"]
    WHY --> W5["До 512 подстраниц<br/>Каталог экскурсий"]
    WHY --> W6["Таймер для акций<br/>и промо-коды"]

    style REC_BASIC fill:#f5f5f5,stroke:#9E9E9E
    style REC_PRO fill:#e3f2fd,stroke:#1565C0
    style REC_BIZ fill:#c8e6c9,stroke:#2E7D32,stroke-width:3px
    style WHY fill:#fff3e0,stroke:#E65100
```

## Легенда

| Цвет | Значение |
|------|----------|
| Серый | Basic -- бесплатный, минимальный |
| Синий | Pro -- средний, подходит для визитки |
| Зеленый (жирная рамка) | Business -- рекомендуется для туризма ОАЭ |
| Красный | Функция отсутствует на данном тарифе |
| Желтый | Рекомендуемый вариант оплаты (годовой) |
