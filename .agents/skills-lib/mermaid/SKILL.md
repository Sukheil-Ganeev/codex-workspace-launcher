---
name: mermaid
description: "Use when creating architecture diagrams, database ERD, flow charts, sequence diagrams, state machines, Gantt charts, or any visual diagram that should live in Markdown documentation"
license: Apache-2.0
---
# Mermaid Diagrams

## Overview

Mermaid — это библиотека диаграмм на JavaScript, которая позволяет создавать визуальные схемы прямо внутри Markdown-файлов с помощью простого текстового синтаксиса.

**Где рендерится нативно (без плагинов):**
- GitHub — в любом `.md` файле, PR description, Issue, Wiki
- GitLab — аналогично GitHub
- Notion — блок `/code` → язык `mermaid`
- VS Code — плагин "Markdown Preview Mermaid Support"
- VitePress, Docusaurus, Obsidian
- Онлайн редактор: https://mermaid.live

**Ключевой принцип:** диаграммы версионируются в Git вместе с кодом, проходят code review, не устаревают.

---

## When to Use / When NOT to Use

**Использовать Mermaid когда:**
- Документируешь архитектуру системы, микросервисов, ботов
- Описываешь FSM (конечный автомат) — состояния бронирования, авторизации
- Показываешь схему базы данных (ERD)
- Визуализируешь API / webhook flow (sequence diagram)
- Строишь roadmap или план спринта (Gantt)
- Рисуешь простые диаграммы распределения (pie chart)

**НЕ использовать когда:**
- Нужен красивый дизайн для презентации клиенту — используй Figma/draw.io
- Диаграмма сложнее 20-25 узлов — разбей на несколько
- Нужны кастомные иконки или бренд-цвета — лучше изображение

---

## Diagram Types

### flowchart — Процессы и архитектура

**Синтаксис:**
```
flowchart LR          (или TD — сверху вниз)
    A[Прямоугольник]
    B(Скругленный)
    C{Ромб — решение}
    D[(Цилиндр — БД)]
    E((Круг))

    A --> B
    B -->|да| C
    B -->|нет| D
    C --> E
```

**Направления:** `LR` (left→right), `TD` (top→down), `RL`, `BT`

**Формы узлов:**
- `[текст]` — прямоугольник
- `(текст)` — скругленный
- `{текст}` — ромб (решение)
- `[(текст)]` — цилиндр (база данных)
- `((текст))` — круг
- `>текст]` — флаг
- `/текст/` — параллелограмм

**Пример — Архитектура CatalogBot:**
```mermaid
flowchart LR
    subgraph Clients["Клиенты"]
        TG[Telegram]
        VK[VK]
        IG[Instagram DM]
        WA[WhatsApp]
        FB[Facebook]
        VB[Viber]
    end

    subgraph Core["core/"]
        CFG[config.py]
        I18N[i18n.py]
        FMT[formatter_base.py]
        FSM[fsm.py]
        AI[ai_adapter.py]
    end

    subgraph Data["data/"]
        DB[(PostgreSQL\nCatalogDB\n460 методов)]
        SEED[seed_data.json\n285 блоков]
    end

    subgraph Services["core/services/"]
        AIS[ai_assistant]
        GEO[geo]
        CUR[currency]
        REF[referral_logic]
    end

    TG --> Core
    VK --> Core
    IG --> Core
    WA --> Core
    FB --> Core
    VB --> Core

    Core --> Data
    Core --> Services
    Services --> AI
    AI -->|Gemini 2.5| EXT1[Google AI]
    AI -->|GPT-4o-mini| EXT2[OpenAI]
```

---

### sequenceDiagram — API и Webhook потоки

**Синтаксис:**
```
sequenceDiagram
    participant A as Клиент
    participant B as Сервер
    participant C as БД

    A->>B: POST /webhook
    B->>C: INSERT INTO bookings
    C-->>B: OK
    B-->>A: 200 {"status":"ok"}

    Note over A,B: Синхронный обмен
    activate B
    B->>C: SELECT ...
    deactivate B
```

**Стрелки:**
- `->>` — сплошная стрелка (синхронный вызов)
- `-->>` — пунктирная стрелка (ответ)
- `-x` — стрелка с крестом (ошибка/блокировка)
- `-)` — открытая стрелка (async)

**Пример — WhatsApp Webhook Flow:**
```mermaid
sequenceDiagram
    participant U as Пользователь
    participant WA as WhatsApp Cloud API
    participant BOT as whatsapp_bot\n(FastAPI :8082)
    participant CORE as core/
    participant PG as PostgreSQL

    U->>WA: Отправляет сообщение
    WA->>BOT: POST /webhook\n(HMAC-SHA256)
    BOT->>BOT: verify_signature()
    BOT->>CORE: get_or_create_wa_user()
    CORE->>PG: UPSERT whatsapp_users
    PG-->>CORE: synthetic_user_id
    CORE-->>BOT: user context

    alt Текстовый поиск
        BOT->>CORE: search_blocks(query)
        CORE->>PG: SELECT blocks WHERE...
        PG-->>CORE: results[]
        CORE-->>BOT: formatted cards
        BOT->>WA: POST /messages (Interactive List)
    else Команда бронирования
        BOT->>CORE: FSMManager.set_state()
        BOT->>WA: POST /messages (текст с вопросом)
    end

    BOT-->>WA: 200 OK
    Note over BOT,CORE: Telegram notify → менеджер
```

---

### erDiagram — Схема базы данных

**Синтаксис:**
```
erDiagram
    TABLE1 {
        int id PK
        string name
        int fk_id FK
    }
    TABLE2 {
        int id PK
        string value
    }

    TABLE1 ||--o{ TABLE2 : "has"
```

**Типы связей:**
- `||--||` — один к одному
- `||--|{` — один ко многим (обязательно)
- `||--o{` — один ко многим (опционально)
- `}|--|{` — многие ко многим

**Пример — Основные таблицы CatalogBot:**
```mermaid
erDiagram
    blocks {
        bigserial id PK
        bigint parent_id FK
        varchar category
        varchar title
        text description
        numeric price
        varchar currency
        float lat
        float lng
        varchar bestseller_mode
        int bestseller_order
        bool is_active
    }

    bookings {
        bigserial id PK
        bigint user_id FK
        bigint block_id FK
        varchar form_type
        date tour_date
        int adults
        int children
        varchar status
        numeric total_price
        varchar currency
        bool voucher_sent
        bigint business_id FK
        timestamp created_at
    }

    loyalty {
        bigint user_id PK
        varchar user_name
        varchar language
        int total_bookings
        numeric total_spent
        int bonus_points
        varchar platform
        bool is_banned
        timestamp created_at
    }

    block_faq {
        bigserial id PK
        bigint block_id FK
        varchar question
        text answer
    }

    reviews {
        bigserial id PK
        bigint user_id FK
        bigint booking_id FK
        int rating
        text comment
        varchar status
        text owner_reply
        timestamp replied_at
        timestamp viewed_at
    }

    blocks ||--o{ bookings : "book"
    blocks ||--o{ block_faq : "has FAQ"
    blocks ||--o{ reviews : "reviewed in"
    loyalty ||--o{ bookings : "makes"
    loyalty ||--o{ reviews : "writes"
    blocks ||--o{ blocks : "parent_id (tree)"
```

---

### stateDiagram-v2 — FSM состояния

**Синтаксис:**
```
stateDiagram-v2
    [*] --> Начало
    Начало --> Шаг1 : событие
    Шаг1 --> Шаг2 : условие
    Шаг2 --> [*] : завершение

    state "Составное состояние" as CS {
        [*] --> Подсостояние1
        Подсостояние1 --> Подсостояние2
    }

    note right of Шаг1
        Подсказка
    end note
```

**Пример — FSM бронирования (Telegram/VK):**
```mermaid
stateDiagram-v2
    [*] --> idle : /start или главное меню

    idle --> waiting_date : нажал "Забронировать"\nbook:{block_id}
    waiting_date --> waiting_adults : ввёл дату\n(формат ДД.ММ.ГГГГ)
    waiting_adults --> waiting_children : ввёл кол-во взрослых
    waiting_children --> waiting_name : ввёл кол-во детей
    waiting_name --> waiting_phone : ввёл имя
    waiting_phone --> waiting_comment : ввёл телефон
    waiting_comment --> confirming : ввёл комментарий или /skip

    confirming --> booking_saved : нажал ✅ Подтвердить
    confirming --> idle : нажал ❌ Отмена

    booking_saved --> [*] : уведомление менеджеру\nваучер отправлен

    waiting_date --> idle : /cancel или Назад
    waiting_adults --> waiting_date : Назад
    waiting_children --> waiting_adults : Назад
    waiting_name --> waiting_children : Назад
    waiting_phone --> waiting_name : Назад
    waiting_comment --> waiting_phone : Назад

    note right of confirming
        Показывается карточка
        с итогом заказа
    end note
```

---

### C4Context — Системная архитектура (C4 Model)

**Синтаксис:**
```
C4Context
    title System Context — Название системы

    Person(user, "Пользователь", "Описание")
    System(sys, "Система", "Описание")
    System_Ext(ext, "Внешняя система", "Описание")

    Rel(user, sys, "Использует", "HTTPS")
    Rel(sys, ext, "Интегрируется", "API")
```

**Пример — Контекст CatalogBot:**
```mermaid
C4Context
    title System Context — VIP DXB CatalogBot

    Person(client, "Клиент", "Турист из СНГ,\nищет экскурсии в ОАЭ")
    Person(owner, "Владелец / Менеджер", "Сухейль и команда,\nуправляют заказами")

    System(bot, "CatalogBot", "Мультиплатформенный бот:\nTelegram, VK, IG, WA, FB, Viber.\nКаталог, бронирование, CRM.")

    System_Ext(tg, "Telegram Bot API", "Long Poll")
    System_Ext(meta, "Meta APIs", "IG DM, WhatsApp,\nFacebook Messenger")
    System_Ext(vk, "VK API", "Long Poll")
    System_Ext(viber, "Viber REST API", "Webhook")
    System_Ext(ai, "Google AI / OpenAI", "Gemini + GPT-4o-mini")
    System_Ext(pg, "PostgreSQL (GCP)", "40+ таблиц, 460 методов")
    System_Ext(crm, "Tourism CRM", "Next.js на Vercel,\ncrm.vipdxbrus.com")

    Rel(client, bot, "Пишет", "Любая платформа")
    Rel(owner, bot, "Управляет", "Telegram owner panel")
    Rel(owner, crm, "Использует CRM", "HTTPS")

    Rel(bot, tg, "Long Poll")
    Rel(bot, meta, "Webhook HTTPS")
    Rel(bot, vk, "Long Poll")
    Rel(bot, viber, "Webhook HTTPS")
    Rel(bot, ai, "AI запросы", "HTTPS API")
    Rel(bot, pg, "asyncpg pool", "TCP")
    Rel(bot, crm, "CRM_MINIAPP_URL", "HTTPS")
```

---

### gantt — Дорожная карта и таймлайн

**Синтаксис:**
```
gantt
    title Название проекта
    dateFormat YYYY-MM-DD
    excludes weekends

    section Секция 1
    Задача завершена   :done,    t1, 2026-01-01, 2026-01-10
    Задача активная    :active,  t2, 2026-01-10, 7d
    Будущая задача     :         t3, after t2, 5d
    Критическая        :crit,    t4, 2026-01-20, 3d
```

**Пример — Roadmap Omni Inbox:**
```mermaid
gantt
    title Omni Inbox Rollout — VIP DXB CatalogBot
    dateFormat YYYY-MM-DD

    section P0 — Критично
    TelegramConnector в on_incoming_message    :done,    p0a, 2026-03-10, 2026-03-11
    InstagramConnector регистрация            :active,  p0b, 2026-03-11, 3d
    WhatsAppConnector создание                :         p0c, after p0b, 3d

    section P1 — Высокий приоритет
    FacebookConnector создание                :         p1a, after p0c, 2d
    ViberConnector создание                   :         p1b, after p1a, 2d
    Inbox UI — список диалогов                :         p1c, after p0c, 4d

    section P2 — Средний приоритет
    Поиск по диалогам                         :         p2a, after p1c, 3d
    Назначение диалогов менеджерам            :         p2b, after p2a, 3d
    Метрики и аналитика                       :         p2c, after p2b, 5d

    section P3 — Низкий приоритет
    Chatbot GPT auto-reply                    :         p3a, after p2c, 7d
    Cross-platform история клиента            :         p3b, after p3a, 5d
```

---

### pie — Распределение и доли

**Синтаксис:**
```
pie title Заголовок
    "Категория 1" : 42
    "Категория 2" : 30
    "Категория 3" : 28
```

**Пример — Распределение бронирований по платформам:**
```mermaid
pie title Бронирования по платформам (2026)
    "Telegram" : 65
    "VK" : 18
    "WhatsApp" : 8
    "Instagram" : 5
    "Facebook" : 3
    "Viber" : 1
```

---

## Quick Reference

| Тип диаграммы | Когда использовать | Ключевое слово |
|---|---|---|
| `flowchart` | Архитектура, процессы, дерево решений | `flowchart LR` / `TD` |
| `sequenceDiagram` | API вызовы, webhook flow, взаимодействие сервисов | `sequenceDiagram` |
| `erDiagram` | Схема БД, связи между таблицами | `erDiagram` |
| `stateDiagram-v2` | FSM, состояния пользователя, lifecycle | `stateDiagram-v2` |
| `C4Context` | Системный контекст, внешние интеграции | `C4Context` |
| `gantt` | Roadmap, спринты, таймлайн задач | `gantt` |
| `pie` | Доли, распределения, статистика | `pie title` |
| `classDiagram` | ООП классы, иерархия наследования | `classDiagram` |
| `mindmap` | Брейншторм, структура знаний | `mindmap` |

---

## Rendering

### GitHub
Нативно в любом `.md` файле — просто оберни в блок кода с языком `mermaid`:
````
```mermaid
flowchart LR
    A --> B
```
````

### VS Code
Плагин: **"Markdown Preview Mermaid Support"** (Mamei Software).
После установки — стандартный preview (`Ctrl+Shift+V`) рендерит диаграммы.

### Notion
1. Напиши `/code`
2. Выбери язык `mermaid`
3. Вставь синтаксис диаграммы

### Онлайн редактор
https://mermaid.live — вставь код, получи SVG/PNG, поделись ссылкой.

### GitLab
Нативно, синтаксис идентичен GitHub.

---

## Common Mistakes

### 1. Пробелы и спецсимволы в именах узлов
```
# НЕВЕРНО — пробел сломает парсер
A[My Node] --> B[Another Node]

# ВЕРНО — если нет скобок, пробелы недопустимы в ID
myNode[My Node] --> anotherNode[Another Node]
```

### 2. Специальные символы требуют кавычек
```
# НЕВЕРНО
A --> B[Hello (World)]

# ВЕРНО — используй кавычки внутри скобок
A --> B["Hello (World)"]
```

### 3. Кириллица в ID узлов — лучше избегать
```
# РИСК — может работать, но нестабильно
Старт --> Конец

# НАДЁЖНО — латинские ID, кириллица только в метках
start_node[Старт] --> end_node[Конец]
```

### 4. Слишком длинные стрелки в sequenceDiagram
```
# НЕВЕРНО — лишние пробелы
A - - >> B: message

# ВЕРНО
A-->>B: message
```

### 5. ERD: FK должны явно описываться в relationships
```
# Просто добавить FK в поля недостаточно для линий связи
# НУЖНО явно написать:
TABLE1 ||--o{ TABLE2 : "описание связи"
```

### 6. Пустые диаграммы не рендерятся
Всегда должен быть хотя бы один узел или участник.

---

## Tips & Tricks

**Группировка узлов в flowchart:**
```
flowchart TD
    subgraph Backend["Backend Services"]
        API[FastAPI]
        DB[(PostgreSQL)]
    end
    Client --> API
    API --> DB
```

**Стили узлов:**
```
flowchart LR
    A[Нормальный]
    B[Ошибка]:::error
    C[Успех]:::success

    classDef error fill:#ff6b6b,color:#fff
    classDef success fill:#51cf66,color:#fff
```

**Ссылки на узлы (GitHub поддерживает):**
```
flowchart LR
    A[Документация] --> B[API]
    click A href "https://docs.example.com" "Открыть документацию"
```

---

## Sources

- Источник скилла: https://github.com/TerminalSkills/skills/tree/main/skills/mermaid
- Официальная документация: https://mermaid.js.org/intro/
- Онлайн редактор: https://mermaid.live
- Размер файла: ~7.5 KB
