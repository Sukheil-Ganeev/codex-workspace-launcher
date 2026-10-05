# Процесс обработки вебхука Taplink

Детальная схема прохождения данных от момента отправки формы клиентом до получения уведомления менеджером, включая верификацию подписи и retry policy.

```mermaid
sequenceDiagram
    participant C as Клиент (турист)
    participant T as Taplink Page
    participant S as Сервер (Node.js)
    participant TG as Telegram Bot
    participant CRM as Notion CRM
    participant E as Email

    Note over C,T: 1. Клиент заполняет форму
    C->>T: Отправка формы:<br/>Имя, Телефон, Дата, Гости

    Note over T: Taplink сохраняет заявку<br/>во встроенную CRM

    Note over T,S: 2. Webhook отправка
    T->>S: HTTP POST /webhook<br/>Content-Type: application/json<br/>Header: taplink-signature

    Note over T: Формат JSON:<br/>action: "leads.created"<br/>data.lead_id, data.records[]

    Note over S: 3. Верификация подписи
    S->>S: HMAC-SHA1(body, SECRET)<br/>Сравнение с taplink-signature<br/>(crypto.timingSafeEqual)

    alt Подпись НЕ валидна
        S-->>T: HTTP 403 Forbidden
        Note over T: Retry Policy активируется
    end

    alt Подпись валидна
        S-->>T: HTTP 200 OK

        Note over S: 4. Обработка данных
        S->>S: Парсинг records[]:<br/>Name, Phone, Date, Guests

        par Параллельная отправка
            Note over S,TG: 5a. Уведомление менеджеру
            S->>TG: POST /sendMessage<br/>"Новая заявка #45<br/>Name: Ahmed<br/>Phone: +971..."
            TG-->>S: OK

            Note over S,CRM: 5b. Запись в CRM
            S->>CRM: Notion API<br/>Create page in database
            CRM-->>S: OK

            Note over S,E: 5c. Автоответ клиенту
            S->>E: Отправка email<br/>"Спасибо за заявку!"
            E-->>S: OK
        end
    end
```

## Retry Policy Taplink

Если сервер ответил кодом, отличным от 100-299, Taplink повторяет отправку.

```mermaid
graph LR
    subgraph RETRY["Retry Policy (8 попыток, до 10.5 часов)"]
        R1["Попытка 1<br/>+5 мин"] --> R2["Попытка 2<br/>+15 мин"]
        R2 --> R3["Попытка 3<br/>+15 мин"]
        R3 --> R4["Попытка 4<br/>+1 час"]
        R4 --> R5["Попытка 5<br/>+1 час"]
        R5 --> R6["Попытка 6<br/>+2 часа"]
        R6 --> R7["Попытка 7<br/>+2 часа"]
        R7 --> R8["Попытка 8<br/>+4 часа"]
    end

    FAIL["HTTP >= 300<br/>или timeout"] --> R1
    R8 --> STOP["Webhook<br/>отключается"]

    style FAIL fill:#ffcdd2,stroke:#E91E63
    style STOP fill:#ffcdd2,stroke:#E91E63
    style RETRY fill:#e8f5e9,stroke:#4CAF50
```

## Формат данных Webhook

```mermaid
graph TD
    subgraph JSON["HTTP POST Body (JSON)"]
        A["action: leads.created"] --> D["data"]
        D --> LID["lead_id: 123"]
        D --> LN["lead_number: 45"]
        D --> PL["page_link: taplink.cc/dubaitours"]
        D --> TS["tms_created: 2026-02-14 12:00:00"]
        D --> REC["records: Array"]
        REC --> R1F["[0] title: Name, value: Ahmed"]
        REC --> R2F["[1] title: Phone, value: +971..."]
        REC --> R3F["[2] title: Date, value: 2026-03-15"]
        REC --> R4F["[3] title: Guests, value: 4"]
    end

    style JSON fill:#e3f2fd,stroke:#1976D2
```

## Легенда

| Элемент | Описание |
|---------|----------|
| taplink-signature | HMAC-SHA1 подпись в заголовке запроса |
| SECRET | Секретный ключ, заданный в настройках Taplink |
| crypto.timingSafeEqual | Безопасное сравнение строк (защита от timing attack) |
| HTTP 100-299 | Коды успешного ответа для Taplink |
| Retry Policy | 8 попыток за 10.5 часов, затем webhook отключается |
