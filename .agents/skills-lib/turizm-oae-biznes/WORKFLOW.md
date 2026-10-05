# Workflow: Туризм ОАЭ — Бизнес

## Обзор процесса

```
Данные из парсера (contacts.json, messages.jsonl)
        |
  [Классификация]
        |
Клиенты, Агенты, Поставщики
        |
  [Построение профилей]
        |
profiles.json, operations.json
        |
  [Бизнес-аналитика]
        |
LTV, Средний чек, Воронка продаж, Жалобы
        |
  [CRM Интеграции]
        |
Bitrix24, amoCRM, Notion, Airtable
        |
  [Маркетинг]
        |
Рефералы, RFM сегментация, Программа лояльности
        |
  [Документы]
        |
Инвойсы, Контракты, Ваучеры
        |
  [Дашборды и отчёты]
        |
Daily Dashboard, Воронка, Финансы, KPI
        |
  [Гео-аналитика]
        |
Карты клиентов, Маршруты водителей
        |
  [Экспорт]
        |
Airtable CSV, Шаблоны, Индексы
```

---

## Этап 1: Классификация и профили

### scripts/business/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `classify_contacts.py` | contacts.json, all_messages.jsonl | contacts.json (обновленный) | Автоклассификация контактов по типам (клиенты, агенты, поставщики, сотрудники) на основе ключевых слов в сообщениях, паттернов JID и имен. Определяет подтипы (турист, VIP, турагент, водитель и др.) |
| `build_profiles.py` | contacts.json, all_messages.jsonl | profiles.json | Строит профили клиентов: стиль общения (formal/informal), чувствительность к цене, скорость принятия решений, предпочтительное время, типы туров, интересы, бюджетная категория. Извлекает биографию (город, профессия, семейное положение) |
| `detect_referrals.py` | contacts.json, all_messages.jsonl | referrals.json | Обнаруживает рефералов через VCF-контакты, упоминания ("от Марины", "по рекомендации"), прямые указания ("мой друг посоветовал"). Fuzzy matching имен с базой контактов |

### Зависимости этапа 1

```
whatsapp-парсер/contacts.json
whatsapp-парсер/all_messages.jsonl
    |
    +-- classify_contacts.py --> contacts.json (c type/subtype)
    |       |
    |       +-- build_profiles.py --> profiles.json
    |
    +-- detect_referrals.py --> referrals.json
```

---

## Этап 2: Бизнес-аналитика

### scripts/business/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `average_check.py` | operations.json, contacts.json, all_messages.jsonl | average_check_analysis.json, CSV, MD | Анализ среднего чека: по типу клиента (агенты vs прямые), по типу тура (сафари, яхты, трансферы), по сезонам, по источникам. Upsell анализ, тренды по месяцам, прогноз выручки, распределение чеков (гистограмма) |
| `calculate_ltv.py` | contacts.json, operations.json, profiles.json | ltv_analysis.json, MD, CSV | Расчет LTV: исторический (сумма покупок), средний чек, частота покупок, срок жизни клиента, прогнозный LTV. Сегментация (VIP/Regular/One-time/Churned), churn risk, когортный анализ |
| `calculate_response_time.py` | all_messages.jsonl, contacts.json | response_time.json | Расчет времени ответа на сообщения клиентов |
| `first_response_time.py` | all_messages.jsonl, contacts.json, sales_funnel.json | first_response_time.json, CSV, MD | FRT анализ: время первого ответа, SLA метрики (< 5 мин, < 1 час, < 24 часа), сегментация по типу клиента и времени суток, влияние на конверсию, сравнение с industry benchmarks |
| `build_sales_funnel.py` | all_messages.jsonl, contacts.json, operations.json | sales_funnel.json, MD | Построение воронки продаж: этапы (lead, qualified, proposal, negotiation, payment, completed), конверсия между этапами, средний чек по этапам, время в этапе |
| `dialog_duration.py` | all_messages.jsonl | dialog_duration.json, MD | Анализ длительности диалогов: определение сессий (gap > 4 часов = новая сессия), lifecycle контакта, паттерны (fast_dealer vs long_negotiator), реактивации |
| `extract_complaints.py` | all_messages.jsonl | complaints.json, MD | Извлечение жалоб по категориям: отмены, качество, цена, сервис, возвраты. Определение severity (high/medium/low), продукта, резолюции |
| `rejection_analysis.py` | all_messages.jsonl, contacts.json | rejections.json, CSV, MD | Анализ причин отказов: цена, конкуренты, timing, качество/сервис, личные обстоятельства. Тренды, сегментация по типу клиента |
| `repeat_customers.py` | contacts.json, operations.json, profiles.json | repeat_customers.json, CSV, MD | Анализ повторных клиентов: retention метрики, RFM сегментация, churn prediction, программа лояльности |
| `seasonal_analysis.py` | all_messages.jsonl, operations.json | seasonal_analysis.json, MD | Сезонный анализ: по месяцам, дням недели, часам. Учет праздников ОАЭ, РФ и исламских. Высокий сезон (окт-апр) vs низкий (май-сен) |
| `source_conversion.py` | contacts.json, all_messages.jsonl, operations.json, profiles.json | source_conversion.json, CSV, MD | Конверсия по источникам: Instagram, referral, advertising, Google, agent, direct, repeat. UTM-подобные метки, модели атрибуции, воронка по источникам |
| `manager_efficiency.py` | all_messages.jsonl, contacts.json, operations.json | manager_efficiency.json, CSV, PDF, MD | Эффективность менеджеров: время ответа, конверсия, средний чек, количество диалогов. Leaderboard, выявление слабых мест, рекомендации |

### Зависимости этапа 2

```
contacts.json (classified)
profiles.json
operations.json
all_messages.jsonl
    |
    +-- average_check.py ----------> average_check_analysis.json
    +-- calculate_ltv.py ----------> ltv_analysis.json
    +-- first_response_time.py ----> first_response_time.json
    +-- build_sales_funnel.py -----> sales_funnel.json
    +-- dialog_duration.py --------> dialog_duration.json
    +-- extract_complaints.py -----> complaints.json
    +-- rejection_analysis.py -----> rejections.json
    +-- repeat_customers.py -------> repeat_customers.json
    +-- seasonal_analysis.py ------> seasonal_analysis.json
    +-- source_conversion.py ------> source_conversion.json
    +-- manager_efficiency.py -----> manager_efficiency.json
```

---

## Этап 3: CRM Интеграции

### scripts/integrations/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `bitrix24_integration.py` | contacts.json, profiles.json, operations.json | Bitrix24 API | Синхронизация с Битрикс24 CRM: создание контактов, сделок, лидов. Настройка воронок продаж и смарт-процессов. Rate limiting (2 req/sec), batch запросы |
| `bitrix24_products.py` | operations.json | Bitrix24 API | Синхронизация товаров/услуг с каталогом Битрикс24 |
| `bitrix24_timeline.py` | all_messages.jsonl | Bitrix24 API | Синхронизация таймлайна сделок с историей сообщений |
| `google_sheets_export.py` | contacts.json, operations.json, profiles.json, sales_funnel.json, ltv_analysis.json | Google Sheets | Экспорт данных в Google Sheets: контакты, операции, профили, воронка, LTV. Форматирование заголовков, автоширина колонок |
| `google_calendar_sync.py` | operations.json | Google Calendar API | Синхронизация операций (экскурсий, трансферов) с Google Calendar |
| `notion_sync.py` | contacts.json, profiles.json, operations.json | Notion API | Синхронизация с Notion: создание баз данных контактов и операций, маппинг типов, rate limiting (3 req/sec) |
| `email_sync.py` | contacts.json, operations.json | Email | Синхронизация с email: отправка подтверждений, напоминаний |

### Bitrix24 CRM

**Настройка:**
```bash
export BITRIX24_DOMAIN="your-domain.bitrix24.ru"
export BITRIX24_USER_ID="1"
export BITRIX24_WEBHOOK_KEY="your-webhook-key"
```

**Воронка продаж Bitrix24:**
```yaml
Туризм ОАЭ:
  1. NEW - Новый запрос
  2. PREPARATION - Уточнение деталей
  3. PREPAYMENT_INVOICE - Предложение отправлено
  4. EXECUTING - Ожидание оплаты
  5. PARTIAL_PAYMENT - Частичная оплата
  6. FINAL_INVOICE - Полная оплата
  7. IN_PROGRESS - В поездке
  8. WON - Успешно завершено
  9. LOSE - Отказ
```

**Кастомные поля:**
- `UF_CRM_WHATSAPP_ID` - ID чата WhatsApp
- `UF_CRM_TOUR_TYPE` - Тип тура (Экскурсия/Сафари/Яхта/Трансфер)
- `UF_CRM_ARRIVAL_DATE` - Дата приезда
- `UF_CRM_PAX` - Количество гостей

**Роботы и триггеры:**
- При создании сделки из WhatsApp → уведомление менеджеру + создание задачи
- Сделка в стадии "Предложение" > 24ч → автоматический follow-up
- За 3 дня до приезда → напоминание об оплате

### amoCRM

**Интеграция через API:**
```python
AMOCRM_CONFIG = {
    'subdomain': 'your-company',
    'client_id': 'xxx',
    'client_secret': 'xxx',
    'redirect_uri': 'https://your-server.com/amocrm/callback'
}

# Маппинг статусов воронки
PIPELINE_STAGES = {
    'new': 'Новая заявка',
    'qualified': 'Квалифицирован',
    'proposal': 'Предложение отправлено',
    'negotiation': 'Переговоры',
    'won': 'Успех',
    'lost': 'Отказ'
}
```

### Notion CRM

**Структура баз данных:**
```
Tourism CRM (Notion)
├── Клиенты - связь с телефоном/WhatsApp ID
├── Сделки - воронка продаж
├── Туры - каталог услуг
├── Оплаты - история платежей
└── Задачи - канбан по статусу
```

**Свойства базы "Клиенты":**
| Property | Type | Description |
|----------|------|-------------|
| Имя | Title | Имя клиента |
| Телефон | Phone | WhatsApp номер |
| Статус | Select | Новый/Активный/VIP/Архив |
| Менеджер | Person | Ответственный |
| Общая сумма | Rollup | Sum of Сделки.Сумма |
| WhatsApp ID | Text | ID чата |

### Airtable

**Схема базы:**
```
Tourism CRM (Airtable)
├── Contacts - связь WhatsApp ID → контакт
├── Deals - этапы воронки
├── Payments - оплаты
└── Tasks - задачи
```

**Автоматизации:**
- Новый контакт → уведомление в Slack
- Оплата → обновление статуса сделки
- Брошенная заявка (>2 дней) → задача менеджеру

### Зависимости этапа 3

```
contacts.json, profiles.json, operations.json
    |
    +-- bitrix24_integration.py ---> Bitrix24 CRM
    |       +-- bitrix24_products.py
    |       +-- bitrix24_timeline.py
    |
    +-- google_sheets_export.py ---> Google Sheets
    +-- google_calendar_sync.py ---> Google Calendar
    +-- notion_sync.py ------------> Notion Workspace
    +-- email_sync.py -------------> Email Server
```

**Переменные окружения для интеграций:**
- `BITRIX24_DOMAIN`, `BITRIX24_USER_ID`, `BITRIX24_WEBHOOK_KEY`
- `GOOGLE_SHEETS_CREDENTIALS`, `GOOGLE_SHEETS_SPREADSHEET_ID`
- `NOTION_API_KEY`, `NOTION_CONTACTS_DB`, `NOTION_OPERATIONS_DB`
- `AMOCRM_SUBDOMAIN`, `AMOCRM_CLIENT_ID`, `AMOCRM_CLIENT_SECRET`

---

## Этап 4: Маркетинг и рефералы

### Реферальная программа

**Обнаружение рефералов из чатов:**

| Паттерн | Пример | Действие |
|---------|--------|----------|
| "от [имя]" | "Я от Марины" | Связать с клиентом |
| "порекомендовал/а" | "Нас порекомендовала Анна" | Найти в базе |
| "по рекомендации" | "По рекомендации коллеги" | Уточнить имя |

**Regex для поиска:**
```regex
(?:от|по рекомендации|посоветовал[аи]?|рекомендовал[аи]?)\s+([А-Яа-яЁё]+)
```

**Структура бонусов:**

| Уровень | Условие | Бонус рефереру | Бонус новому |
|---------|---------|----------------|--------------|
| Базовый | 1 реферал | 5% от заказа | Скидка 3% |
| Серебро | 3-5 рефералов | 7% от заказа | Скидка 5% |
| Золото | 6-10 рефералов | 10% от заказа | Скидка 7% |
| Платина | 11+ рефералов | 12% + VIP | Скидка 10% |

**Многоуровневая система:**
| Уровень цепочки | Бонус от заказа |
|-----------------|-----------------|
| Прямой реферал (1) | 100% бонуса |
| Уровень 2 | 30% бонуса |
| Уровень 3 | 10% бонуса |

### RFM сегментация

**R** - Recency (давность), **F** - Frequency (частота), **M** - Monetary (сумма)

| Сегмент | RFM | Стратегия |
|---------|-----|-----------|
| **VIP Чемпионы** | 555, 554 | Персональный менеджер, эксклюзивы |
| **Лояльные** | 444, 435 | Программа лояльности, upsell |
| **Перспективные** | 513, 514 | Вовлечение, скидка на 2й заказ |
| **Спящие** | 244, 144 | Реактивация "Мы скучаем" + скидка |
| **В зоне риска** | 154, 155 | Опрос причин + бонус возврата |

**Шкала RFM (1-5):**
| Показатель | 5 (лучший) | 4 | 3 | 2 | 1 (худший) |
|------------|------------|---|---|---|------------|
| **R** (дней с последнего заказа) | 0-30 | 31-90 | 91-180 | 181-365 | >365 |
| **F** (кол-во заказов) | 5+ | 4 | 3 | 2 | 1 |
| **M** (общая сумма, $) | >5000 | 3001-5000 | 1501-3000 | 501-1500 | <500 |

### Программа лояльности

**Система баллов:**
| Действие | Баллы |
|----------|-------|
| $1 потрачен | 1 балл |
| Отзыв Google | 50 баллов |
| Успешный реферал | 200 баллов |
| День рождения | 100 баллов |

**Конвертация:** 100 баллов = $1 скидка

**Уровни клиентов:**
| Уровень | Требование | Множитель | Привилегии |
|---------|------------|-----------|------------|
| Bronze | 0-999 баллов | x1.0 | Базовые скидки |
| Silver | 1000-2999 | x1.25 | Приоритетное бронирование |
| Gold | 3000-6999 | x1.5 | Бесплатные апгрейды |
| Platinum | 7000-14999 | x2.0 | Персональный менеджер |
| Diamond | 15000+ | x2.5 | Эксклюзивные туры + VIP трансфер |

### Источники трафика

| Источник | % | CAC | LTV | ROI |
|----------|---|-----|-----|-----|
| Рекомендации | 30% | $0 | $6000 | ∞ |
| Instagram | 40% | $300 | $4000 | 13x |
| Турагенты | 20% | $200 | $3500 | 17x |
| Google | 5% | $800 | $3000 | 3.75x |

---

## Этап 5: Дашборды и отчёты

### Ежедневный дашборд

```
┌─────────────────┬─────────────────┬─────────────────┬───────────────────┐
│ НОВЫЕ ЗАПРОСЫ   │  КОНВЕРСИЯ      │  ВЫРУЧКА ДНЯ    │ ПРОБЛЕМНЫЕ ЧАТЫ   │
│     47          │    12%          │   $8,450        │      3            │
│  (+8 vs вчера)  │ (+2% vs вчера)  │ (-$1.2K)        │ (требуют внимания)│
└─────────────────┴─────────────────┴─────────────────┴───────────────────┘
```

**Метрики:**
| Метрика | Формула | Источник данных |
|---------|---------|-----------------|
| Новые запросы | `COUNT(messages WHERE date = TODAY AND is_new_lead = true)` | WhatsApp/Telegram |
| Конверсия дня | `(Бронирования дня / Запросы дня) × 100%` | CRM |
| Выручка дня | `SUM(payments WHERE date = TODAY)` | Платёжная система |
| Проблемные чаты | `COUNT(chats WHERE last_reply_time > 4h OR sentiment = negative)` | Анализ чатов |

### Воронка продаж

| Этап | Конверсия | Цель |
|------|-----------|------|
| Запрос → Интерес | 60% | 70% |
| Интерес → Бронь | 60% | 65% |
| Бронь → Оплата | 80% | 85% |
| Оплата → Выполнено | 95% | 98% |

### Метрики качества

| Метрика | Формула | Цель |
|---------|---------|------|
| Время первого ответа (FRT) | AVG(first_response_time) | < 5 мин |
| Время до бронирования (TTB) | AVG(inquiry_to_booking) | < 2 дня |
| NPS | Promoters% - Detractors% | > 50 |
| CSAT | Довольных (4-5) / Всего | > 85% |

### Финансовые отчёты

**Ключевые формулы:**
```python
Revenue = SUM(payments) - SUM(refunds)
Gross_Profit = Revenue - COGS
Gross_Margin = (Gross_Profit / Revenue) * 100
AOV = Revenue / Number_of_Orders
ROI = ((Revenue - Total_Costs) / Total_Costs) * 100
```

### Streamlit дашборд

```python
import streamlit as st
import plotly.express as px

def daily_dashboard():
    st.title("Ежедневный дашборд")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Новые запросы", 47, 8)
    col2.metric("Конверсия", "12%", "2%")
    col3.metric("Выручка", "$8,450", "-$1,200")
    col4.metric("Проблемные чаты", 3, 1, delta_color="inverse")
```

### Структура проекта дашборда

```
tourism-dashboard/
├── app.py                    # Главный файл
├── requirements.txt          # Зависимости
├── config.py                 # Настройки
├── data/
│   ├── connectors.py         # Подключение к БД
│   └── queries.py            # SQL запросы
├── pages/
│   ├── daily_dashboard.py
│   ├── sales_funnel.py
│   ├── quality_metrics.py
│   ├── financial.py
│   ├── team_activity.py
│   ├── customers.py
│   └── seasonality.py
└── components/
    ├── charts.py             # Переиспользуемые графики
    └── metrics.py            # Карточки метрик
```

---

## Этап 6: KPI и показатели

### Показатели по клиентам

| Показатель | Формула | Цель | Частота |
|------------|---------|------|---------|
| Всего клиентов | COUNT(type=client) | Рост 10%/мес | Ежедневно |
| Новые клиенты | COUNT(first_contact THIS_MONTH) | 50+/месяц | Еженедельно |
| Активные (90д) | COUNT(last_message < 90 days) | 200+ | Ежедневно |
| Повторные | COUNT(orders > 1) / COUNT(all) | 30%+ | Ежемесячно |
| Churn rate | COUNT(inactive 90+ days) / COUNT(all) | < 20% | Ежемесячно |

### Показатели по продажам

| Показатель | Формула | Цель |
|------------|---------|------|
| **Конверсия** | bookings / inquiries | 25%+ |
| **Средний чек (AOV)** | SUM(revenue) / COUNT(orders) | 1500 AED |
| **LTV клиента** | AVG(total_spent_per_client) | 5000 AED |
| **CAC** | Marketing spend / New customers | < 500 AED |
| **LTV/CAC** | LTV / CAC | > 3:1 |

### Формулы расчёта

**LTV (Lifetime Value):**
```
LTV = Средний чек × Частота заказов × Время жизни × Маржа
```

**CAC (Customer Acquisition Cost):**
```
CAC = Расходы на маркетинг / Количество новых клиентов
```

**Churn Rate:**
```
Churn = (Клиенты на начало - Клиенты на конец + Новые) / Клиенты на начало
```

**NPS (Net Promoter Score):**
```
NPS = % Промоутеров (9-10) - % Критиков (0-6)
```

### Юнит-экономика

| Метрика | Формула | Пример |
|---------|---------|--------|
| **CAC** | Marketing / New customers | 500 AED |
| **LTV** | Avg order × Avg orders/customer | 4500 AED |
| **LTV/CAC** | LTV / CAC | 9x |
| **Payback** | CAC / (Avg order × Margin) | 1.5 мес |
| **ARPU** | Revenue / Active users | 750 AED/мес |

### Глоссарий KPI

| Термин | Определение |
|--------|-------------|
| **CAC** | Cost of Acquisition - стоимость привлечения |
| **LTV** | Lifetime Value - пожизненная ценность |
| **ARPU** | Average Revenue Per User |
| **Churn** | Отток клиентов |
| **NPS** | Net Promoter Score |
| **RFM** | Recency-Frequency-Monetary |
| **AOV** | Average Order Value |
| **CSAT** | Customer Satisfaction Score |
| **FRT** | First Response Time |
| **TTB** | Time to Booking |

---

## Этап 7: Генерация документов

### scripts/documents/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `invoice_generator.py` | operations.json, данные клиента | PDF, HTML, JSON | Генерация PDF инвойсов: автонумерация (INV-2026-0001), шаблоны (стандартный, проформа, квитанция, кредит-нота), брендинг (логотип, цвета, QR-код), отправка по email, интеграция с Bitrix24 |
| `contract_generator.py` | данные клиента | PDF, DOCX | Генерация договоров: тур/экскурсия, агентский договор, аренда авто, яхта. Автозаполнение из данных клиента, цифровая подпись (опционально), QR код с ID договора |
| `voucher_generator.py` | данные операции | PDF (A4 + мобильная) | Генерация ваучеров: туристический (экскурсии, туры), трансфер, билеты (парки, аттракционы), подарочный сертификат. Уникальные коды, QR для верификации |
| `generate_report.py` | MD файлы чатов | PDF, MD | Генерация аналитических отчетов: обороты за период, топ контактов, извлечение операций из таблиц в чатах |

### Зависимости этапа 7

```
operations.json
contacts.json
profiles.json
    |
    +-- invoice_generator.py -----> D:/Downloads/Chats/_инвойсы/
    +-- contract_generator.py ----> D:/Downloads/Chats/_договоры/
    +-- voucher_generator.py -----> D:/Downloads/Chats/_ваучеры/
    +-- generate_report.py -------> D:/Downloads/Chats/_база/md/
```

**Требуемые библиотеки:**
- `reportlab` - PDF генерация
- `python-docx` - DOCX генерация
- `qrcode` - QR коды
- `cryptography` (опционально) - цифровая подпись

---

## Этап 8: Гео-аналитика

### scripts/geo/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `client_heatmap.py` | contacts.json, profiles.json | HTML карта, PNG, JSON, CSV | Тепловая карта клиентов по географии: определение страны по номеру телефона (phonenumbers), статистика по странам (топ-10), интерактивная карта Folium |
| `driver_routes.py` | список точек | Google Maps deep links, WhatsApp сообщения | Маршруты для водителей: multi-stop оптимизация, deep links для Google Maps и Waze, форматирование для WhatsApp/Telegram, мониторинг ETA, отчеты по пробегу |
| `pickup_optimizer.py` | адреса из чатов | оптимизированный маршрут, карта | Оптимизация маршрутов пикапа: извлечение адресов из чатов, геокодинг через Google Maps API, решение TSP (ortools), визуализация карты (Folium), экспорт для водителей |

### Зависимости этапа 8

```
contacts.json
profiles.json
all_messages.jsonl (для адресов)
    |
    +-- client_heatmap.py --------> HTML карта, статистика по странам
    +-- driver_routes.py ---------> Маршруты для водителей (WhatsApp)
    +-- pickup_optimizer.py ------> Оптимизированные маршруты
```

**Требуемые библиотеки:**
- `phonenumbers` - определение страны по телефону
- `folium` - интерактивные карты
- `googlemaps` - геокодинг и маршруты
- `ortools` - оптимизация TSP

**API ключи:**
- `GOOGLE_MAPS_API_KEY`

---

## Этап 9: Экспорт

### scripts/export/

| Скрипт | Вход | Выход | Что делает |
|--------|------|-------|------------|
| `export_for_airtable.py` | contacts.json, profiles.json, referrals.json, operations.json | CSV файлы, IMPORT_README.md, base_schema.json | Экспорт в CSV для Airtable: contacts.csv, profiles.csv, referrals.csv, operations.csv. UTF-8 BOM для Excel, README с инструкциями импорта |
| `build_index.py` | MD файлы чатов | index.md | Создание индекса всех чатов: метаданные (период, кол-во сообщений, медиа), подсчет сумм (RUB, AED), теги |
| `build_document.py` | txt чаты, расшифровки голосовых, анализ изображений, анализ PDF | MD документ | Сборка полного MD документа: парсинг WhatsApp сообщений, замена вложений расшифровками голосовых, описаниями изображений |
| `generate_templates.py` | MD файлы чатов | templates.json | Генерация шаблонов сообщений: поиск часто используемых фраз, категоризация (приветствия, цены, подтверждения) |

### Зависимости этапа 9

```
contacts.json, profiles.json, referrals.json, operations.json
    |
    +-- export_for_airtable.py ---> Airtable CSV + README

MD файлы чатов
    |
    +-- build_index.py -----------> index.md
    +-- build_document.py --------> полный MD документ
    +-- generate_templates.py ----> templates.json
```

---

## Примеры запуска

### Полный пайплайн бизнес-аналитики

```bash
# Этап 1: Классификация и профили
python scripts/business/classify_contacts.py
python scripts/business/build_profiles.py
python scripts/business/detect_referrals.py

# Этап 2: Бизнес-аналитика
python scripts/business/average_check.py
python scripts/business/calculate_ltv.py --update-contacts
python scripts/business/build_sales_funnel.py
python scripts/business/first_response_time.py
python scripts/business/seasonal_analysis.py
python scripts/business/extract_complaints.py

# Этап 3: Интеграции (требуют настройки API)
python scripts/integrations/bitrix24_integration.py --sync-all --dry-run
python scripts/integrations/google_sheets_export.py --all
python scripts/integrations/notion_sync.py --sync-all

# Этап 4: Документы
python scripts/documents/invoice_generator.py --operation-id OP-001
python scripts/documents/contract_generator.py --type tour

# Этап 5: Гео-аналитика
python scripts/geo/client_heatmap.py
python scripts/geo/pickup_optimizer.py --date 2026-01-27

# Этап 6: Экспорт
python scripts/export/export_for_airtable.py
python scripts/export/build_index.py
```

### Только LTV анализ

```bash
python scripts/business/calculate_ltv.py --top 20 --export-csv
python scripts/business/calculate_ltv.py --segment VIP
python scripts/business/calculate_ltv.py --churn-risk high
```

### Только интеграция с Bitrix24

```bash
# Тестовый режим
python scripts/integrations/bitrix24_integration.py --sync-all --dry-run

# Синхронизация контактов
python scripts/integrations/bitrix24_integration.py --contacts

# Синхронизация сделок
python scripts/integrations/bitrix24_integration.py --deals

# Настройка структуры CRM
python scripts/integrations/bitrix24_integration.py --setup-all
```

### Генерация документов

```bash
# Инвойс
python scripts/documents/invoice_generator.py --client-phone "+79123456789" --amount 5000 --currency AED --description "Safari Tour"

# Ваучер
python scripts/documents/voucher_generator.py --type tour --client-name "Иван Иванов" --date "2026-01-27"

# Договор
python scripts/documents/contract_generator.py --type agency --client-name "Travel Agency LLC"
```

---

## Структура выходных файлов

```
D:/Downloads/Chats/_база/
    |
    +-- raw/
    |   +-- all_messages.jsonl      # Сырые сообщения
    |
    +-- json/
    |   +-- contacts.json           # Контакты (classified)
    |   +-- profiles.json           # Профили клиентов
    |   +-- referrals.json          # Рефералы
    |   +-- operations.json         # Операции
    |   +-- ltv_analysis.json       # LTV анализ
    |   +-- average_check_analysis.json
    |   +-- sales_funnel.json       # Воронка продаж
    |   +-- first_response_time.json
    |   +-- complaints.json         # Жалобы
    |   +-- rejections.json         # Отказы
    |   +-- seasonal_analysis.json
    |   +-- source_conversion.json
    |   +-- manager_efficiency.json
    |
    +-- csv/
    |   +-- contacts.csv            # Для Airtable
    |   +-- profiles.csv
    |   +-- operations.csv
    |   +-- ltv_export.csv
    |   +-- first_response_time.csv
    |
    +-- md/
    |   +-- ltv_клиентов.md
    |   +-- средний_чек.md
    |   +-- время_первого_ответа.md
    |   +-- жалобы_и_отмены.md
    |   +-- сезонный_анализ.md
    |   +-- эффективность_менеджеров.md
    |
    +-- reports/
        +-- *.pdf                   # PDF отчеты

D:/Downloads/Chats/_инвойсы/
    +-- INV-2026-0001.pdf
    +-- invoice_registry.json

D:/Downloads/Chats/_договоры/
    +-- CONTRACT-2026-0001.pdf
    +-- contract_registry.json

D:/Downloads/Chats/_ваучеры/
    +-- VOUCHER-2026-0001.pdf
    +-- voucher_codes.json
```

---

## Требования

### Python библиотеки

```bash
pip install reportlab python-docx qrcode phonenumbers folium googlemaps ortools gspread google-auth notion-client pandas requests streamlit plotly
```

### Переменные окружения

```bash
# Bitrix24
export BITRIX24_DOMAIN="your-domain.bitrix24.ru"
export BITRIX24_USER_ID="1"
export BITRIX24_WEBHOOK_KEY="your-webhook-key"

# amoCRM
export AMOCRM_SUBDOMAIN="your-company"
export AMOCRM_CLIENT_ID="xxx"
export AMOCRM_CLIENT_SECRET="xxx"

# Google
export GOOGLE_SHEETS_CREDENTIALS="/path/to/credentials.json"
export GOOGLE_MAPS_API_KEY="your-api-key"

# Notion
export NOTION_API_KEY="your-notion-api-key"
export NOTION_CONTACTS_DB="database-id"
export NOTION_OPERATIONS_DB="database-id"

# Email
export SMTP_SERVER="smtp.gmail.com"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

---

## Чек-лист внедрения

### Фаза 1: Базовая аналитика (1-2 недели)
- [ ] Настроить сбор данных из WhatsApp
- [ ] Классификация контактов
- [ ] Построение профилей
- [ ] Базовый экспорт в Airtable

### Фаза 2: CRM интеграция (2-3 недели)
- [ ] Выбор CRM (Bitrix24/amoCRM/Notion)
- [ ] Настройка синхронизации контактов
- [ ] Настройка воронки продаж
- [ ] Автоматизации и триггеры

### Фаза 3: Маркетинг и рефералы (2-3 недели)
- [ ] Обнаружение рефералов из чатов
- [ ] RFM сегментация клиентов
- [ ] Программа лояльности
- [ ] Анализ источников трафика

### Фаза 4: Дашборды и отчёты (3-4 недели)
- [ ] Ежедневный дашборд (Streamlit)
- [ ] Воронка продаж
- [ ] Финансовые отчёты
- [ ] Метрики качества

### Фаза 5: Автоматизация (ongoing)
- [ ] Алерты на проблемные метрики
- [ ] Автоматические отчёты в Telegram
- [ ] A/B тестирование
- [ ] Предиктивная аналитика

---

## Дополнительные ресурсы

Файлы с расширенными идеями и детальной документацией:

| Файл | Путь | Описание |
|------|------|----------|
| **CRM интеграции** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_CRM_ИНТЕГРАЦИИ.md` | Детальные схемы Airtable, Bitrix24, Notion, amoCRM с кодом интеграций |
| **Маркетинг и рефералы** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_МАРКЕТИНГ_РЕФЕРАЛЫ.md` | RFM-анализ, реферальная программа, email-маркетинг, ретаргетинг |
| **Дашборды и отчёты** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_ДАШБОРДЫ_ОТЧЁТЫ.md` | Streamlit код, Plotly графики, SQL запросы, макеты дашбордов |
| **KPI и показатели** | `D:/Downloads/Идеи-туризм-бизнес/ИДЕИ_И_ПОКАЗАТЕЛИ.md` | Полный набор KPI, формулы, чек-листы внедрения, глоссарий |
