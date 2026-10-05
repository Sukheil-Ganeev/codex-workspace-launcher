# FAQ - Часто задаваемые вопросы

## Как классифицировать контакт вручную?

**Ответ:** Откройте файл `D:/Downloads/Chats/_база/json/contacts.json` и измените поля `type` и `subtype` для нужного контакта:

```json
{
  "contact_id": "uuid-контакта",
  "type": "агенты",
  "subtype": "турагент",
  "tags": ["партнёр", "москва"],
  "notes": "Ручная классификация"
}
```

**Допустимые значения:**
| type | subtype |
|------|---------|
| клиенты | турист, VIP, корпоративный |
| агенты | турагент, туроператор, B2B |
| поставщики | обменник, водитель, гид, яхтсмен, кейтеринг |
| сотрудники | менеджер, водитель_штат, админ |

---

## Как добавить нового агента?

**Способ 1: Через JSON файл**

Добавьте запись в `contacts.json`:
```json
{
  "contact_id": "новый-uuid",
  "phone": "+79161234567",
  "name": "Название агентства",
  "type": "агенты",
  "subtype": "турагент",
  "source": "manual",
  "tags": ["комиссия_10%"],
  "notes": "Комиссия 10%, расчёт еженедельно"
}
```

**Способ 2: Через Bitrix24**

```bash
python scripts/integrations/bitrix24_integration.py --add-contact \
  --name "Название агентства" \
  --phone "+79161234567" \
  --type "агенты" \
  --subtype "турагент"
```

---

## Как рассчитать комиссию?

**Формула расчёта комиссии агента:**

```
Комиссия = Сумма заказов × Процент комиссии

Где:
- Сумма заказов = SUM(operations.amount) за период
- Процент комиссии = указан в tags контакта (например "комиссия_10%")
```

**Пример расчёта:**
```python
# Для агента с комиссией 10%
orders_sum = 15000  # AED
commission_rate = 0.10
commission = orders_sum * commission_rate  # 1500 AED
```

**Скрипт для расчёта:**
```bash
python scripts/business/calculate_agent_commission.py \
  --agent-phone "+79161234567" \
  --period "2026-01"
```

---

## Как экспортировать в Airtable?

**Шаг 1: Экспортируйте данные в CSV**
```bash
python scripts/export/export_for_airtable.py
```

**Шаг 2: В Airtable создайте новую базу**
1. Create a base > Start from scratch
2. Назовите "UAE Tourism CRM"

**Шаг 3: Импортируйте таблицы**
1. Для каждой таблицы: Add or import > CSV file
2. Порядок импорта:
   - `contacts.csv` (главная)
   - `profiles.csv`
   - `operations.csv`
   - `referrals.csv`

**Шаг 4: Настройте связи**
1. Откройте таблицу Operations
2. Измените тип поля Contact_Phone на "Link to another record"
3. Выберите таблицу Contacts
4. Повторите для Profiles и Referrals

**Подробная инструкция:** `D:/Downloads/Chats/_база/airtable/IMPORT_README.md`

---

## Как интегрировать с Bitrix24?

**Шаг 1: Создайте вебхук в Bitrix24**
1. Откройте CRM > Настройки > Интеграции > REST API
2. Создайте входящий вебхук
3. Выберите права: crm, im, disk

**Шаг 2: Настройте переменные окружения**
```bash
# Windows (PowerShell)
$env:BITRIX24_DOMAIN = "your-company.bitrix24.ru"
$env:BITRIX24_USER_ID = "1"
$env:BITRIX24_WEBHOOK_KEY = "your-webhook-key"

# Или добавьте в .env файл
```

**Шаг 3: Настройте структуру Bitrix24**
```bash
python scripts/integrations/bitrix24_integration.py --setup-all
```

Это создаст:
- Пользовательские поля для контактов
- Воронки продаж (Туры, Трансферы, Яхты, Билеты)
- Смарт-процессы (Бронирования, Рефералы)

**Шаг 4: Синхронизируйте данные**
```bash
# Тестовый режим
python scripts/integrations/bitrix24_integration.py --sync-all --dry-run

# Реальная синхронизация
python scripts/integrations/bitrix24_integration.py --sync-all
```

**Автоматическая синхронизация:**
Добавьте в планировщик Windows или cron:
```bash
# Каждый час
0 * * * * python scripts/integrations/bitrix24_integration.py --sync-incremental
```

---

## Дополнительные вопросы

### Как обновить классификацию после изменения правил?

```bash
python scripts/business/classify_contacts.py --force-reclassify
```

### Как найти все операции клиента?

```bash
python scripts/business/client_history.py --phone "+79161234567"
```

### Как экспортировать отчёт за месяц?

```bash
python scripts/documents/generate_report.py \
  --period "2026-01" \
  --format pdf \
  --output "D:/Downloads/reports/"
```
