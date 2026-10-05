# Интеграция с make.com -- Webhook сценарии

Подробные инструкции и JSON-конфигурации для 4 основных webhook сценариев.

---

## Сценарий 1: Классификация входящего сообщения

```json
{
  "name": "WhatsApp Message Classification",
  "trigger": {
    "type": "webhook",
    "url": "https://hook.eu2.make.com/xxx/whatsapp-incoming"
  },
  "modules": [
    {
      "name": "Parse Webhook",
      "type": "json.parse",
      "input": "{{1.body}}"
    },
    {
      "name": "Check Media",
      "type": "router",
      "routes": [
        {
          "condition": "{{2.media_type}} == 'voice'",
          "target": "Whisper Transcription"
        },
        {
          "condition": "{{2.media_type}} == 'image'",
          "target": "OCR Processing"
        },
        {
          "condition": "true",
          "target": "Claude Classification"
        }
      ]
    },
    {
      "name": "Claude Classification",
      "type": "http.request",
      "config": {
        "url": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "headers": {
          "x-api-key": "{{env.ANTHROPIC_API_KEY}}",
          "anthropic-version": "2023-06-01",
          "content-type": "application/json"
        },
        "body": {
          "model": "claude-sonnet-4-20250514",
          "max_tokens": 1024,
          "system": "Ты классификатор сообщений туристического бизнеса...",
          "messages": [
            {
              "role": "user",
              "content": "Классифицируй сообщение:\n\n{{2.text}}"
            }
          ]
        }
      }
    },
    {
      "name": "Update Airtable",
      "type": "airtable.create_record",
      "config": {
        "base_id": "appXXX",
        "table": "Messages",
        "fields": {
          "Phone": "{{2.phone}}",
          "Text": "{{2.text}}",
          "Type": "{{4.classification.type}}",
          "Priority": "{{4.classification.priority}}",
          "Timestamp": "{{now}}"
        }
      }
    },
    {
      "name": "Route by Priority",
      "type": "router",
      "routes": [
        {
          "condition": "{{4.classification.priority}} == 'critical'",
          "target": "Alert Manager"
        },
        {
          "condition": "{{4.classification.type}} == 'inquiry'",
          "target": "Auto Response"
        }
      ]
    }
  ]
}
```

---

## Сценарий 2: Whisper транскрипция

```json
{
  "name": "Voice Message Transcription",
  "modules": [
    {
      "name": "Download Audio",
      "type": "http.download",
      "config": {
        "url": "{{input.media_url}}"
      }
    },
    {
      "name": "Whisper API",
      "type": "http.request",
      "config": {
        "url": "https://api.openai.com/v1/audio/transcriptions",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{env.OPENAI_API_KEY}}"
        },
        "body_type": "multipart/form-data",
        "body": {
          "file": "{{1.data}}",
          "model": "whisper-1",
          "language": "ru"
        }
      }
    },
    {
      "name": "Return Transcription",
      "type": "response",
      "config": {
        "body": {
          "transcription": "{{2.text}}",
          "duration": "{{2.duration}}"
        }
      }
    }
  ]
}
```

---

## Сценарий 3: Автоответ на запрос цены

```json
{
  "name": "Auto Price Response",
  "trigger": {
    "type": "webhook",
    "filter": {
      "classification.type": "inquiry",
      "classification.intent": "price_request"
    }
  },
  "modules": [
    {
      "name": "Get Product Info",
      "type": "airtable.search",
      "config": {
        "base_id": "appXXX",
        "table": "Products",
        "filter": "SEARCH('{{input.detected_product}}', {Name})"
      }
    },
    {
      "name": "Generate Response",
      "type": "http.request",
      "config": {
        "url": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "body": {
          "model": "claude-sonnet-4-20250514",
          "max_tokens": 500,
          "system": "Сгенерируй дружелюбный ответ с ценой...",
          "messages": [
            {
              "role": "user",
              "content": "Продукт: {{1.Name}}\nЦена: {{1.Price}}\nОписание: {{1.Description}}"
            }
          ]
        }
      }
    },
    {
      "name": "Send WhatsApp",
      "type": "whatsapp.send",
      "config": {
        "to": "{{input.phone}}",
        "message": "{{2.response}}"
      }
    }
  ]
}
```

---

## Сценарий 4: Уведомление о жалобе

```json
{
  "name": "Complaint Alert",
  "trigger": {
    "type": "webhook",
    "filter": {
      "classification.type": "complaint"
    }
  },
  "modules": [
    {
      "name": "Get Client History",
      "type": "airtable.search",
      "config": {
        "base_id": "appXXX",
        "table": "Clients",
        "filter": "{Phone} = '{{input.phone}}'"
      }
    },
    {
      "name": "Create Summary",
      "type": "http.request",
      "config": {
        "url": "https://api.anthropic.com/v1/messages",
        "body": {
          "system": "Создай краткое саммари жалобы для менеджера...",
          "messages": [{"role": "user", "content": "{{input.text}}"}]
        }
      }
    },
    {
      "name": "Send Telegram Alert",
      "type": "telegram.send",
      "config": {
        "chat_id": "@managers_alerts",
        "text": "ЖАЛОБА\n\nКлиент: {{1.Name}}\nVIP: {{1.VIP}}\nИстория: {{1.TotalOrders}} заказов\n\nСуть: {{2.summary}}\n\nОригинал: {{input.text}}"
      }
    },
    {
      "name": "Create Task",
      "type": "airtable.create_record",
      "config": {
        "table": "Tasks",
        "fields": {
          "Title": "Жалоба от {{1.Name}}",
          "Priority": "High",
          "Status": "New",
          "AssignedTo": "{{1.Manager}}"
        }
      }
    }
  ]
}
```

---

## Обработка ошибок в make.com

### 1. Timeout API
**Симптомы:** Сценарий падает с ошибкой timeout после 40 секунд.

**Решения:**
- Увеличить timeout до 60 секунд в настройках HTTP модуля
- Добавить retry с exponential backoff: Retry 3 раза, интервалы 1s, 2s, 4s
- Разбить большие запросы на chunks

### 2. Rate limit Claude API
**Симптомы:** Ошибка 429 Too Many Requests.

**Решения:**
- Использовать batch API для массовых операций
- Добавить очередь сообщений (Queue module в make.com)
- Установить rate limiter: max 50 запросов/минуту
- Кэшировать повторяющиеся запросы

### 3. Webhook не отвечает
**Симптомы:** WhatsApp/Telegram не получают ответы.

**Решения:**
- Проверить SSL сертификат (должен быть валидный)
- Добавить healthcheck endpoint для мониторинга
- Проверить firewall/CORS настройки
- Увеличить timeout на стороне отправителя

### 4. Airtable rate limit
**Симптомы:** Ошибка 422 при частых запросах.

**Решения:**
- Batch записи (до 10 за запрос)
- Добавить delay между запросами (200ms)
- Использовать bulk update вместо single

---

## Дашборд метрик (make.com)

```json
{
  "scenario": "Metrics Collector",
  "schedule": "every 5 minutes",
  "modules": [
    {
      "name": "Collect Metrics",
      "type": "http.request",
      "urls": [
        "https://api.anthropic.com/v1/usage",
        "https://api.openai.com/v1/usage"
      ]
    },
    {
      "name": "Store in Airtable",
      "type": "airtable.create_record",
      "table": "Metrics",
      "fields": {
        "timestamp": "{{now}}",
        "api_calls": "{{metrics.calls}}",
        "cost": "{{metrics.cost}}",
        "errors": "{{metrics.errors}}"
      }
    },
    {
      "name": "Check Thresholds",
      "type": "router",
      "routes": [
        {
          "condition": "{{metrics.cost}} > 100",
          "target": "Send Alert"
        }
      ]
    }
  ]
}
```
