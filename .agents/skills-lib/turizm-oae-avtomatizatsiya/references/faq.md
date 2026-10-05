# FAQ - Часто задаваемые вопросы

## Настройка и конфигурация

### Как настроить Claude API?

1. **Получите API ключ:**
   - Зарегистрируйтесь на https://console.anthropic.com
   - Перейдите в Settings -> API Keys
   - Создайте новый ключ

2. **Добавьте в .env файл:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-ваш-ключ
   ```

3. **Проверьте подключение:**
   ```python
   import anthropic
   client = anthropic.Anthropic()
   response = client.messages.create(
       model="claude-sonnet-4-20250514",
       max_tokens=100,
       messages=[{"role": "user", "content": "Привет!"}]
   )
   print(response.content[0].text)
   ```

4. **Для make.com:**
   - Создайте HTTP модуль
   - URL: `https://api.anthropic.com/v1/messages`
   - Headers:
     - `x-api-key`: ваш ключ
     - `anthropic-version`: `2023-06-01`
     - `content-type`: `application/json`

---

### Как добавить новую категорию классификации?

1. **Обновите системный промпт:**
   ```python
   CLASSIFIER_SYSTEM_PROMPT = """
   ...
   "type": "inquiry|booking|support|complaint|spam|other|НОВАЯ_КАТЕГОРИЯ",
   ...
   """
   ```

2. **Добавьте подтипы:**
   ```python
   "НОВАЯ_КАТЕГОРИЯ": [
       "subtype_1",
       "subtype_2",
       "subtype_3"
   ]
   ```

3. **Определите правила приоритета:**
   ```python
   # В секции ПРАВИЛА добавьте:
   # НОВАЯ_КАТЕГОРИЯ с условием X = priority: high
   ```

4. **Добавьте обработку в make.com:**
   - Новый route в Router модуле
   - Условие: `{{classification.type}} == 'НОВАЯ_КАТЕГОРИЯ'`
   - Целевой модуль для обработки

5. **Обновите Airtable:**
   - Добавьте новое значение в поле Type (Single Select)
   - Создайте View для фильтрации

---

### Как изменить промпт автоответа?

1. **Найдите функцию generate_auto_response:**
   ```python
   # scripts/ai/auto_responder.py
   ```

2. **Измените системный промпт:**
   ```python
   AUTORESPONSE_PROMPT = """
   Ты дружелюбный ассистент туристической компании в ОАЭ.

   ПРАВИЛА:
   - Отвечай на русском языке
   - Используй вежливую форму обращения
   - Не обещай то, что не можешь выполнить
   - Добавляй эмодзи для дружелюбности
   - Длина ответа: 2-4 предложения

   ШАБЛОНЫ:
   - Приветствие: "Здравствуйте! Спасибо за обращение."
   - Цена: "Стоимость составляет X AED / $Y."
   - Уточнение: "Подскажите, пожалуйста, ..."
   """
   ```

3. **Добавьте контекст:**
   ```python
   user_message = f"""
   Запрос клиента: {client_message}
   Тип: {classification['type']}
   Намерение: {classification['intent']}
   Продукт: {classification.get('entities', {}).get('product', 'не указан')}

   Сгенерируй ответ согласно правилам.
   """
   ```

4. **Тестируйте изменения:**
   ```python
   # Запустите несколько тестовых запросов
   test_messages = [
       "Сколько стоит экскурсия?",
       "Хочу забронировать на завтра",
       "Где мой водитель?"
   ]
   for msg in test_messages:
       response = generate_auto_response(msg)
       print(f"IN: {msg}\nOUT: {response}\n")
   ```

---

## Стоимость и биллинг

### Сколько стоит обработка 1000 сообщений?

**Базовый расчет (только классификация):**

| Компонент | Стоимость за 1 | За 1000 |
|-----------|---------------|---------|
| Классификация (Haiku) | $0.0003 | $0.30 |
| **Итого** | | **$0.30** |

**Полный расчет (с автоответами):**

| Компонент | % сообщений | Стоимость за 1 | За 1000 |
|-----------|-------------|----------------|---------|
| Классификация | 100% | $0.0003 | $0.30 |
| Автоответ (inquiry) | 40% | $0.003 | $1.20 |
| Транскрипция (voice) | 10% | $0.006/мин | $0.60 |
| OCR (images) | 5% | $0.01 | $0.50 |
| **Итого** | | | **$2.60** |

**Месячный бюджет (при 500 сообщений/день):**

```
15,000 сообщений/месяц:
- Классификация: $4.50
- Автоответы (40%): $18.00
- Голосовые (10%): $9.00
- OCR (5%): $7.50
-----------------------
Итого: ~$39/месяц
```

**Оптимизация стоимости:**
1. Используйте Haiku для классификации (в 10 раз дешевле Sonnet)
2. Кэшируйте частые запросы (FAQ, прайсы)
3. Batch API для массовой обработки
4. Фильтруйте спам ДО отправки в Claude

---

### Как снизить расходы на API?

1. **Используйте правильные модели:**
   - Классификация: Claude Haiku ($0.00025/1K input)
   - Генерация: Claude Sonnet ($0.003/1K input)
   - Сложные задачи: Claude Opus (только при необходимости)

2. **Кэширование:**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def get_faq_response(question_hash: str) -> str:
       # Кэш на 1000 популярных вопросов
       return cached_response
   ```

3. **Batch обработка:**
   ```python
   # Вместо 100 отдельных запросов
   # Отправьте 1 batch запрос
   results = await classify_batch(messages[:100])
   ```

4. **Фильтрация на входе:**
   ```python
   # Отфильтруйте спам/дубли ДО Claude
   if is_spam(message) or is_duplicate(message):
       return {"type": "spam", "auto_response": False}
   ```

---

## Интеграции

### Как подключить Telegram бота?

1. **Создайте бота через @BotFather:**
   ```
   /newbot
   Название: Марсель Туры
   Username: marsel_tours_bot
   ```

2. **Получите токен и добавьте в .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   ```

3. **Настройте webhook в make.com:**
   ```
   URL: https://api.telegram.org/bot{TOKEN}/setWebhook
   Body: {"url": "https://hook.eu2.make.com/xxx"}
   ```

4. **Обработка входящих:**
   ```python
   # Telegram отправляет JSON:
   {
       "update_id": 123,
       "message": {
           "chat": {"id": 12345},
           "text": "Сколько стоит тур?"
       }
   }
   ```

---

### Как подключить WhatsApp Business API?

1. **Зарегистрируйтесь в Meta Business:**
   - https://business.facebook.com
   - Создайте Business Account
   - Подключите WhatsApp Business API

2. **Получите токен и Phone ID:**
   ```bash
   WHATSAPP_TOKEN=EAAxxxx
   WHATSAPP_PHONE_ID=123456789
   ```

3. **Настройте webhook:**
   - URL: ваш make.com webhook
   - Verify token: секретная строка
   - Подпишитесь на events: messages

4. **Отправка сообщений:**
   ```python
   import requests

   def send_whatsapp(phone: str, message: str):
       url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
       headers = {"Authorization": f"Bearer {TOKEN}"}
       data = {
           "messaging_product": "whatsapp",
           "to": phone,
           "text": {"body": message}
       }
       requests.post(url, headers=headers, json=data)
   ```

---

## Troubleshooting

### Что делать, если Claude возвращает некорректный JSON?

1. **Добавьте явную инструкцию:**
   ```python
   system_prompt += "\n\nОТВЕЧАЙ ТОЛЬКО ВАЛИДНЫМ JSON БЕЗ КОММЕНТАРИЕВ."
   ```

2. **Используйте structured output:**
   ```python
   response = client.messages.create(
       model="claude-sonnet-4-20250514",
       max_tokens=1024,
       system=system_prompt,
       messages=[...],
       # Добавьте пример ожидаемого формата
   )
   ```

3. **Парсинг с fallback:**
   ```python
   import json
   import re

   def parse_claude_json(text: str) -> dict:
       # Попытка 1: прямой парсинг
       try:
           return json.loads(text)
       except:
           pass

       # Попытка 2: извлечь JSON из текста
       match = re.search(r'\{.*\}', text, re.DOTALL)
       if match:
           try:
               return json.loads(match.group())
           except:
               pass

       # Fallback
       return {"error": "parse_failed", "raw": text}
   ```

---

### Как масштабировать систему?

1. **Горизонтальное масштабирование:**
   - Несколько make.com сценариев
   - Разные webhooks для разных каналов
   - Load balancer перед webhooks

2. **Очередь сообщений:**
   - Используйте AWS SQS / RabbitMQ
   - Буферизация пиковых нагрузок
   - Гарантированная доставка

3. **Кэширование:**
   - Redis для частых запросов
   - CDN для статического контента
   - Edge caching для API responses

4. **Мониторинг:**
   - Datadog / New Relic
   - Custom dashboards
   - Автоматические алерты
