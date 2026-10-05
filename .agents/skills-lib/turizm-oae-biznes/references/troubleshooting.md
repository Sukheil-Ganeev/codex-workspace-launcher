# Troubleshooting - Решение проблем

## Ошибка синхронизации Bitrix24

### Симптомы
- `ConnectionError: Unable to connect to Bitrix24`
- `AuthenticationError: Invalid webhook key`
- `RateLimitError: Too many requests`

### Решения

**1. Проверьте переменные окружения:**
```bash
echo $BITRIX24_DOMAIN
echo $BITRIX24_WEBHOOK_KEY
```

**2. Проверьте доступность API:**
```bash
curl "https://$BITRIX24_DOMAIN/rest/$BITRIX24_USER_ID/$BITRIX24_WEBHOOK_KEY/crm.contact.list"
```

**3. Превышен лимит запросов (RateLimit):**
```bash
# Используйте батчевый режим
python scripts/integrations/bitrix24_integration.py --sync-all --batch

# Или увеличьте задержку между запросами
python scripts/integrations/bitrix24_integration.py --sync-all --delay 1000
```

**4. Истёк вебхук:**
- Создайте новый вебхук в Bitrix24
- Обновите `BITRIX24_WEBHOOK_KEY`

**5. Неправильные права доступа:**
- Убедитесь, что вебхук имеет права: `crm`, `im`, `disk`, `user`

---

## Дубликаты контактов

### Симптомы
- Один контакт появляется несколько раз в списке
- Разные записи для одного телефона
- Несовпадение данных между источниками

### Причины
- Один контакт в WhatsApp Personal и Business
- Номер с разными форматами (+7 и 8)
- Импорт из VCF с дубликатами

### Решения

**1. Запустите дедупликацию:**
```bash
python scripts/business/deduplicate_contacts.py
```

**2. Проверьте дубликаты вручную:**
```bash
python scripts/business/find_duplicates.py --output duplicates.json
```

**3. Объедините дубликаты:**
```bash
python scripts/business/merge_contacts.py \
  --primary "uuid-основного" \
  --duplicates "uuid-1,uuid-2"
```

**4. Нормализуйте телефоны перед импортом:**
```python
import re

def normalize_phone(phone):
    # Удаляем всё кроме цифр
    digits = re.sub(r'\D', '', phone)
    # Российский номер: 8 -> 7
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    return '+' + digits
```

---

## Неправильная конверсия валют

### Симптомы
- Суммы в отчётах не совпадают
- Неправильный курс AED/RUB
- Старые курсы валют

### Решения

**1. Обновите курсы валют:**
```bash
python scripts/business/update_exchange_rates.py
```

**2. Проверьте текущие курсы:**
```bash
cat D:/Downloads/Chats/_база/json/exchange_rates.json
```

**3. Установите курс вручную:**
```json
{
  "rates": {
    "AED_RUB": 24.5,
    "AED_USD": 0.27,
    "USD_RUB": 90.0
  },
  "updated_at": "2026-01-26T12:00:00"
}
```

**4. Пересчитайте операции с новыми курсами:**
```bash
python scripts/business/recalculate_amounts.py --use-current-rates
```

**5. Используйте фиксированные курсы для периода:**
```bash
python scripts/documents/generate_report.py \
  --period "2026-01" \
  --fixed-rate "AED_RUB=24.5"
```

---

## Проблемы с Google Sheets

### Симптомы
- `PermissionError: Insufficient permissions`
- `FileNotFoundError: credentials.json not found`
- `QuotaExceeded: Rate limit exceeded`

### Решения

**1. Проверьте credentials:**
```bash
ls -la $GOOGLE_SHEETS_CREDENTIALS
```

**2. Создайте новые credentials:**
1. Откройте [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services > Credentials
3. Create credentials > Service account
4. Скачайте JSON ключ
5. Укажите путь:
```bash
export GOOGLE_SHEETS_CREDENTIALS="/path/to/credentials.json"
```

**3. Дайте доступ сервисному аккаунту:**
1. Откройте таблицу Google Sheets
2. Share > Введите email сервисного аккаунта
3. Дайте права Editor

**4. Превышена квота:**
```bash
# Используйте экспоненциальный backoff
python scripts/integrations/google_sheets_export.py --retry-with-backoff

# Или разбейте на части
python scripts/integrations/google_sheets_export.py --batch-size 100
```

**5. Неправильный формат данных:**
```bash
# Валидируйте данные перед экспортом
python scripts/export/validate_for_sheets.py --input contacts.json
```

---

## Общие проблемы

### Скрипт зависает при обработке сообщений

**Причина:** Слишком много данных в памяти

**Решение:**
```bash
# Используйте потоковую обработку
python scripts/business/classify_contacts.py --streaming

# Или обрабатывайте частями
python scripts/business/classify_contacts.py --chunk-size 500
```

### Кодировка файлов (UTF-8)

**Симптом:** Кракозябры вместо русского текста

**Решение:**
```bash
# Проверьте кодировку
file -bi contacts.json

# Конвертируйте в UTF-8
iconv -f CP1251 -t UTF-8 contacts.json > contacts_utf8.json
```

### Нет данных в отчётах

**Проверьте:**
1. Существуют ли файлы данных:
```bash
ls -la D:/Downloads/Chats/_база/json/
```

2. Не пустые ли файлы:
```bash
wc -l D:/Downloads/Chats/_база/json/contacts.json
```

3. Правильный ли период:
```bash
python scripts/business/check_data_range.py
```

---

## Логирование для диагностики

Включите подробное логирование:
```bash
export LOG_LEVEL=DEBUG
python scripts/business/classify_contacts.py 2>&1 | tee debug.log
```

Отправьте `debug.log` для анализа проблемы.
