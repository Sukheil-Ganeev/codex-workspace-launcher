# Diagram Patterns — Feature Blueprint

Готовые Mermaid паттерны для VIP-DXB-CatalogBot. Скопируй и адаптируй под свою задачу.

---

## Pattern 1: Bot Webhook Flow (sequenceDiagram)

Универсальный шаблон для любой новой платформы с webhook архитектурой.

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant PLATFORM as [Platform] API
    participant BOT as [platform]_bot\n(FastAPI :PORT)
    participant VERIFY as webhook_verify.py
    participant HANDLER as handlers/
    participant CORE as core/
    participant PG as PostgreSQL
    participant TG as Telegram\n(notify manager)

    U->>PLATFORM: Отправляет сообщение
    PLATFORM->>BOT: POST /webhook\n(HMAC-SHA256 подпись)
    BOT->>VERIFY: verify_signature(request)

    alt Подпись невалидна
        VERIFY-->>BOT: False
        BOT-->>PLATFORM: 403 Forbidden
    else Подпись валидна
        VERIFY-->>BOT: True
        BOT->>CORE: get_or_create_[platform]_user(platform_id)
        CORE->>PG: UPSERT [platform]_users
        PG-->>CORE: synthetic_user_id
        CORE-->>BOT: user context

        alt Текстовое сообщение
            BOT->>HANDLER: handle_text(user, text)
            HANDLER->>CORE: search_blocks(query) или route_command(text)
            CORE->>PG: SELECT blocks WHERE...
            PG-->>CORE: результаты
            CORE-->>HANDLER: formatted response
            HANDLER->>PLATFORM: POST /send_message (карточки)
        else FSM: шаг бронирования
            BOT->>HANDLER: handle_booking_step(user, state, input)
            HANDLER->>CORE: FSMManager.set_state(user_id, next_state)
            HANDLER->>PLATFORM: POST /send_message (следующий вопрос)
        else FSM: финальное подтверждение
            HANDLER->>PG: INSERT INTO bookings
            PG-->>HANDLER: booking_id
            HANDLER->>TG: POST /sendMessage (notify manager)
            HANDLER->>PLATFORM: POST /send_message (подтверждение)
        end

        BOT-->>PLATFORM: 200 OK
    end
```

**Замени в шаблоне:**
- `[Platform]` → `Max Bot`, `Telegram`, `WhatsApp` и т.д.
- `PORT` → `8085`, `8082`, `8081` и т.д.
- `[platform]` → `max`, `whatsapp`, `instagram` и т.д.

---

## Pattern 2: FSM State Machine (stateDiagram-v2)

Шаблон 7-step booking FSM — используется в WhatsApp, Viber, Instagram, Facebook.

```mermaid
stateDiagram-v2
    [*] --> idle : /start или приветствие

    idle --> waiting_date : нажал "Забронировать"
    waiting_date --> waiting_adults : ввёл дату (ДД.ММ.ГГГГ)
    waiting_adults --> waiting_children : ввёл кол-во взрослых
    waiting_children --> waiting_name : ввёл кол-во детей
    waiting_name --> waiting_phone : ввёл имя
    waiting_phone --> waiting_comment : ввёл телефон
    waiting_comment --> confirming : ввёл комментарий или "пропустить"

    confirming --> booking_saved : подтвердил
    confirming --> idle : отменил

    booking_saved --> [*] : уведомление менеджеру\nваучер (если есть email)

    waiting_date --> idle : "отмена" или "назад"
    waiting_adults --> waiting_date : "назад"
    waiting_children --> waiting_adults : "назад"
    waiting_name --> waiting_children : "назад"
    waiting_phone --> waiting_name : "назад"
    waiting_comment --> waiting_phone : "назад"

    note right of confirming
        Показывается итоговая
        карточка заказа
    end note

    note right of booking_saved
        form_type = "[PLATFORM]_GT"
        INSERT INTO bookings
        Telegram notify → менеджер
    end note
```

**Telegram / VK (8-step, включает waiting_comment):**

```mermaid
stateDiagram-v2
    [*] --> idle

    idle --> w_date : book:{block_id} callback
    w_date --> w_adults : дата введена
    w_adults --> w_children : кол-во взрослых
    w_children --> w_name : кол-во детей
    w_name --> w_phone : имя
    w_phone --> w_comment : телефон
    w_comment --> confirming : комментарий или /skip
    confirming --> saved : ✅ Подтвердить
    confirming --> idle : ❌ Отмена

    saved --> [*]

    w_date --> idle : /cancel
    w_adults --> w_date : Назад
    w_children --> w_adults : Назад
    w_name --> w_children : Назад
    w_phone --> w_name : Назад
    w_comment --> w_phone : Назад
```

---

## Pattern 3: ERD для новой платформы

Стандартная структура таблицы маппинга платформы + связи с loyalty.

**Шаблон (заменить `[platform]` и `[prefix]`):**

```mermaid
erDiagram
    [platform]_users {
        varchar [prefix]_id PK
        varchar [prefix]_name
        bigint telegram_user_id
        bigint synthetic_user_id
        varchar language
        boolean is_subscribed
        varchar country
        timestamptz created_at
        timestamptz last_active
    }

    loyalty {
        bigint user_id PK
        varchar user_name
        varchar language
        int total_bookings
        numeric total_spent
        int bonus_points
        varchar platform
        boolean is_banned
        timestamptz created_at
    }

    bookings {
        bigserial id PK
        bigint user_id FK
        bigint block_id FK
        varchar form_type
        date tour_date
        int adults
        varchar status
        numeric total_price
        timestamptz created_at
    }

    [platform]_users ||--o| loyalty : "synthetic_user_id = user_id"
    loyalty ||--o{ bookings : "makes"
```

**Пример для Max Bot:**

```mermaid
erDiagram
    max_users {
        varchar max_id PK
        varchar max_name
        bigint telegram_user_id
        bigint synthetic_user_id
        varchar language
        boolean is_subscribed
        timestamptz created_at
        timestamptz last_active
    }

    loyalty {
        bigint user_id PK
        varchar user_name
        varchar platform
        int total_bookings
        boolean is_banned
    }

    bookings {
        bigserial id PK
        bigint user_id FK
        varchar form_type
        varchar status
        timestamptz created_at
    }

    max_users ||--o| loyalty : "synthetic_user_id → user_id"
    loyalty ||--o{ bookings : "makes"
```

---

## Pattern 4: C4 Context — Omni Inbox (все 7 платформ)

Актуальное состояние Omni Inbox (статус коннекторов на 2026-03-10):

```mermaid
C4Context
    title Omni Inbox — VIP DXB CatalogBot (статус: 2026-03-10)

    Person(client_cis, "Клиент из СНГ", "Турист, ищет\nэкскурсии в ОАЭ")
    Person(owner, "Владелец / Менеджер", "Сухейль и команда,\nуправляют через Telegram")

    System_Boundary(catalog_bot, "CatalogBot") {
        System(omni, "Omni Inbox", "bot/services/omni_inbox.py\nbot/handlers/omni.py\n4 таблицы, 28 методов")
        System(tg_bot, "Telegram Bot", "aiogram 3.25\nLong Poll")
        System(vk_bot, "VK Bot", "vkbottle 4.7\nLong Poll")
        System(ig_bot, "Instagram Bot", "FastAPI :8081\nWebhook")
        System(wa_bot, "WhatsApp Bot", "FastAPI :8082\nWebhook")
        System(fb_bot, "Facebook Bot", "FastAPI :8083\nWebhook")
        System(vb_bot, "Viber Bot", "FastAPI :8084\nWebhook")
    }

    System_Ext(pg, "PostgreSQL (GCP)", "40+ таблиц\n460 async методов")
    System_Ext(crm, "Tourism CRM", "crm.vipdxbrus.com\nNext.js + Neon PG")

    Rel(client_cis, tg_bot, "Пишет", "Telegram")
    Rel(client_cis, vk_bot, "Пишет", "VK")
    Rel(client_cis, ig_bot, "Пишет", "Instagram DM")
    Rel(client_cis, wa_bot, "Пишет", "WhatsApp")
    Rel(client_cis, fb_bot, "Пишет", "Facebook Messenger")
    Rel(client_cis, vb_bot, "Пишет", "Viber")

    Rel(tg_bot, omni, "on_incoming_message()", "✅ подключён")
    Rel(vk_bot, omni, "TODO P0", "⚠️ не зарегистрирован")
    Rel(ig_bot, omni, "TODO P0", "⚠️ не зарегистрирован")
    Rel(wa_bot, omni, "TODO P0", "❌ коннектор не создан")
    Rel(fb_bot, omni, "TODO P1", "❌ коннектор не создан")
    Rel(vb_bot, omni, "TODO P1", "❌ коннектор не создан")

    Rel(owner, tg_bot, "Owner Panel", "Telegram")
    Rel(owner, crm, "CRM", "HTTPS")

    Rel(omni, pg, "asyncpg pool", "TCP")
    Rel(tg_bot, pg, "asyncpg pool", "TCP")
```

**Шаблон для "после подключения всех коннекторов":**

```mermaid
C4Context
    title Omni Inbox — Target State

    Person(client, "Клиент", "Любая платформа")
    Person(manager, "Менеджер", "Работает в Telegram")

    System_Boundary(omni_system, "CatalogBot + Omni Inbox") {
        System(omni, "Omni Inbox", "Единый инбокс\nвсех платформ")
        System(tg, "Telegram Connector", "✅")
        System(vk, "VK Connector", "✅")
        System(ig, "Instagram Connector", "✅")
        System(wa, "WhatsApp Connector", "✅")
        System(fb, "Facebook Connector", "✅")
        System(vb, "Viber Connector", "✅")
    }

    System_Ext(pg, "PostgreSQL", "omni_conversations\nomni_messages\nomni_agents")

    Rel(client, tg, "Telegram")
    Rel(client, vk, "VK")
    Rel(client, ig, "Instagram DM")
    Rel(client, wa, "WhatsApp")
    Rel(client, fb, "Facebook")
    Rel(client, vb, "Viber")

    Rel(tg, omni, "on_incoming_message()")
    Rel(vk, omni, "on_incoming_message()")
    Rel(ig, omni, "on_incoming_message()")
    Rel(wa, omni, "on_incoming_message()")
    Rel(fb, omni, "on_incoming_message()")
    Rel(vb, omni, "on_incoming_message()")

    Rel(omni, pg, "asyncpg")
    Rel(manager, omni, "Отвечает через Telegram")
```

---

## Pattern 5: Deployment Diagram (flowchart)

Docker Compose + GCP production setup:

```mermaid
flowchart TD
    subgraph GCP["GCP VM: tourist-bot (europe-west3-b)"]
        subgraph Docker["Docker Compose (deploy/docker-compose.prod.yml)"]
            TG[telegram_bot\naiogram 3.25\nLong Poll]
            VK[vk_bot\nvkbottle 4.7\nLong Poll]
            IG[instagram_bot\nFastAPI :8081]
            WA[whatsapp_bot\nFastAPI :8082]
            FB[facebook_bot\nFastAPI :8083]
            VB[viber_bot\nFastAPI :8084]
            MA[miniapp\nFastAPI :8080]
            PG[(PostgreSQL\n:5432)]
        end
    end

    subgraph GitHub["GitHub Actions"]
        CI[deploy.yml\non push to main]
    end

    subgraph External["Внешние сервисы"]
        TG_API[Telegram Bot API]
        VK_API[VK API]
        META[Meta APIs\nIG + WA + FB]
        VIBER[Viber REST API]
        GAI[Google AI\nGemini 2.5]
        OAI[OpenAI\ngpt-4o-mini]
        CRM[Tourism CRM\nVercel + Neon]
    end

    DEV[Developer\ngit push] --> CI
    CI -->|SSH deploy| GCP

    TG -.->|Long Poll| TG_API
    VK -.->|Long Poll| VK_API
    IG -.->|Webhook| META
    WA -.->|Webhook| META
    FB -.->|Webhook| META
    VB -.->|Webhook| VIBER

    TG --> PG
    VK --> PG
    IG --> PG
    WA --> PG
    FB --> PG
    VB --> PG
    MA --> PG

    TG -.->|AI| GAI
    TG -.->|AI fallback| OAI
    MA -.->|CRM link| CRM
```

---

## Pattern 6: Component Diagram нового модуля (flowchart)

Шаблон для документирования структуры нового `[platform]_bot/`:

```mermaid
flowchart TD
    subgraph MODULE["max_bot/"]
        APP[app.py\nFastAPI :8085\nwebhook endpoint]
        CFG[config.py\nenv vars re-export]
        VERIFY[webhook_verify.py\nHMAC-SHA256]
        FSM[fsm.py\nMaxState enum\nFSMManager]
        FMT[formatters.py\nplain-text format]
        TPL[templates.py\nMax Bot карточки]

        subgraph HANDLERS["handlers/"]
            CMN[common.py\nevent router]
            CAT[catalog.py\nэмираты → блоки]
            BOOK[booking.py\n7-step FSM]
            SRCH[search.py\nтекстовый поиск]
        end
    end

    subgraph CORE["core/ (shared)"]
        CONFIG[config.py]
        I18N[i18n.py]
        FSMBASE[fsm.py\nFSMManager base]
        FMTBASE[formatter_base.py\nBaseFormatter ABC]
        UIDS[user_ids.py\nMAX_ID_OFFSET]
    end

    subgraph DATA["data/"]
        DB[(CatalogDB\nget_or_create_max_user\n_migrate_v22_max_bot)]
    end

    APP --> VERIFY
    APP --> CMN
    CMN --> CAT
    CMN --> BOOK
    CMN --> SRCH
    CMN --> FSM

    MODULE --> CORE
    BOOK --> DB
    SRCH --> DB
    CAT --> DB

    FMT -.->|inherits| FMTBASE
    FSM -.->|extends| FSMBASE
    CFG -.->|re-exports| CONFIG
```

---

## Mermaid Quick Rules

**Всегда соблюдай:**

1. **ID узлов — латиница:**
   ```
   # Плохо (нестабильно)
   Старт --> Конец

   # Хорошо
   start_node[Старт] --> end_node[Конец]
   ```

2. **Спецсимволы — в кавычки:**
   ```
   # Плохо
   A --> B[Hello (World)]

   # Хорошо
   A --> B["Hello (World)"]
   ```

3. **ERD — явные relationships:**
   ```
   # Только поле FK недостаточно для линии
   max_users ||--o| loyalty : "synthetic_user_id → user_id"
   ```

4. **Не больше 20-25 узлов** в одной диаграмме — разбивай на части

5. **sequenceDiagram стрелки без пробелов:**
   ```
   # Плохо
   A - ->> B: message

   # Хорошо
   A-->>B: message
   ```

6. **Рендеринг в GitHub** — просто оберни в блок кода с языком `mermaid`:
   ````
   ```mermaid
   flowchart LR
       A --> B
   ```
   ````
