# Integrations — Интеграции с платформами

> Подключение Yandex SpeechKit к WhatsApp, Telegram, Make.com, n8n

---

## WhatsApp Business API

### Webhook обработка голосовых

```python
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    Webhook для обработки входящих сообщений WhatsApp.

    Получает голосовое → скачивает → транскрибирует → отвечает.
    """
    data = request.json

    # Извлекаем данные
    message = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0]

    if message.get("type") != "audio":
        return jsonify({"status": "ignored"}), 200

    # Данные голосового
    audio_id = message["audio"]["id"]
    from_number = message["from"]

    print(f"Получено голосовое от {from_number}, ID: {audio_id}")

    # 1. Скачать аудио
    audio_path = download_whatsapp_audio(audio_id)

    # 2. Транскрибировать
    text = transcribe_any_audio(audio_path, lang="ru-RU")

    # 3. Отправить ответ
    send_whatsapp_message(
        to=from_number,
        text=f"Вы сказали: {text}"
    )

    # Cleanup
    os.remove(audio_path)

    return jsonify({"status": "processed"}), 200


def download_whatsapp_audio(audio_id: str) -> str:
    """
    Скачивание аудио из WhatsApp Business API.

    Args:
        audio_id: ID медиафайла

    Returns:
        str: Путь к скачанному файлу
    """
    # 1. Получаем URL медиа
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    media_url_response = requests.get(
        f"https://graph.facebook.com/v18.0/{audio_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    media_url = media_url_response.json()["url"]

    # 2. Скачиваем файл
    audio_response = requests.get(
        media_url,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # 3. Сохраняем локально
    audio_path = f"/tmp/{audio_id}.ogg"
    with open(audio_path, "wb") as f:
        f.write(audio_response.content)

    return audio_path


def send_whatsapp_message(to: str, text: str):
    """Отправка текстового сообщения в WhatsApp."""
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    requests.post(
        f"https://graph.facebook.com/v18.0/{phone_number_id}/messages",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
    )


if __name__ == "__main__":
    app.run(port=5000)
```

### Настройка webhook

1. Запустить сервер:
   ```bash
   python whatsapp_webhook.py
   ```

2. Expose через ngrok (для разработки):
   ```bash
   ngrok http 5000
   ```

3. В Meta Developer Console:
   ```
   WhatsApp → Configuration → Webhook
   URL: https://your-domain.ngrok.io/webhook/whatsapp
   Verify Token: ваш_токен
   ```

4. Подписаться на события:
   ```
   ✓ messages
   ```

---

## Telegram Bot API

### Базовый бот для голосовых

```python
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка голосовых сообщений в Telegram.

    Args:
        update: Telegram Update
        context: Bot context
    """
    voice = update.message.voice

    # 1. Скачать файл
    file = await context.bot.get_file(voice.file_id)
    audio_path = f"/tmp/{voice.file_id}.ogg"
    await file.download_to_drive(audio_path)

    # 2. Отправить "печатает..."
    await update.message.chat.send_action("typing")

    # 3. Транскрибировать
    try:
        text = transcribe_any_audio(audio_path, lang="ru-RU")

        # 4. Отправить результат
        await update.message.reply_text(
            f"🎤 Вы сказали:\n\n{text}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка распознавания: {e}"
        )

    finally:
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)


def main():
    """Запуск бота."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    application = Application.builder().token(bot_token).build()

    # Обработчик голосовых
    application.add_handler(
        MessageHandler(filters.VOICE, handle_voice)
    )

    # Запуск
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
```

### Установка зависимостей

```bash
pip install python-telegram-bot requests python-dotenv
```

### Запуск бота

```bash
# .env
TELEGRAM_BOT_TOKEN=your_bot_token
YANDEX_CLOUD_API_KEY=PASTE_YANDEX_CLOUD_API_KEY_HERE
YANDEX_CLOUD_FOLDER_ID=b1gvu3q8k1kafqd3sk5f

# Запуск
python telegram_bot.py
```

---

## Make.com (Integromat)

### Сценарий: WhatsApp голосовое → транскрипция → сохранение в Google Sheets

#### Модуль 1: Webhook

```json
{
  "name": "WhatsApp Webhook",
  "type": "webhook",
  "config": {
    "url": "https://hook.eu1.make.com/ваш_webhook_id"
  }
}
```

#### Модуль 2: Download Audio

```json
{
  "name": "Download Audio",
  "type": "http",
  "action": "get",
  "config": {
    "url": "{{1.media_url}}",
    "headers": {
      "Authorization": "Bearer {{env.WHATSAPP_ACCESS_TOKEN}}"
    },
    "output": "binary"
  }
}
```

#### Модуль 3: SpeechKit Transcribe

**⚠️ Важно:** Make.com не имеет нативного модуля SpeechKit, используем HTTP Request.

```json
{
  "name": "Yandex SpeechKit",
  "type": "http",
  "action": "post",
  "config": {
    "url": "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
    "method": "POST",
    "headers": {
      "Authorization": "Api-Key {{env.YANDEX_CLOUD_API_KEY}}"
    },
    "qs": {
      "folderId": "{{env.YANDEX_CLOUD_FOLDER_ID}}",
      "lang": "ru-RU",
      "format": "oggopus",
      "sampleRateHertz": "48000"
    },
    "body": "{{2.data}}",
    "bodyType": "raw"
  }
}
```

#### Модуль 4: Parse Response

```json
{
  "name": "Parse JSON",
  "type": "json",
  "action": "parse",
  "config": {
    "json": "{{3.body}}"
  }
}
```

#### Модуль 5: Save to Google Sheets

```json
{
  "name": "Add Row to Google Sheets",
  "type": "google-sheets",
  "action": "addRow",
  "config": {
    "spreadsheetId": "ваш_spreadsheet_id",
    "sheetName": "Transcriptions",
    "values": {
      "Timestamp": "{{now}}",
      "Phone": "{{1.from}}",
      "Text": "{{4.result}}",
      "Duration": "{{1.audio.duration}}"
    }
  }
}
```

### Полный сценарий Make.com

```
WhatsApp Webhook
    ↓
Download Audio
    ↓
Yandex SpeechKit (HTTP Request)
    ↓
Parse JSON Response
    ↓
Save to Google Sheets
    ↓
Send WhatsApp Reply (опционально)
```

---

## n8n Workflow

### Self-hosted автоматизация

```json
{
  "name": "Voice Transcription Workflow",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "whatsapp-voice",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Download Audio",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $json.media_url }}",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer {{ $env.WHATSAPP_TOKEN }}"
        },
        "responseFormat": "file"
      }
    },
    {
      "name": "Transcribe with SpeechKit",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
        "method": "POST",
        "headers": {
          "Authorization": "Api-Key {{ $env.YANDEX_CLOUD_API_KEY }}"
        },
        "queryParameters": {
          "folderId": "{{ $env.YANDEX_CLOUD_FOLDER_ID }}",
          "lang": "ru-RU",
          "format": "oggopus"
        },
        "bodyParameters": {
          "audio": "={{ $binary.data }}"
        }
      }
    },
    {
      "name": "Save to Database",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "insert",
        "table": "transcriptions",
        "columns": [
          "phone",
          "text",
          "created_at"
        ],
        "values": [
          "={{ $node['Webhook'].json.from }}",
          "={{ $json.result }}",
          "={{ $now }}"
        ]
      }
    }
  ]
}
```

---

## Python примеры для каждой интеграции

### 1. WhatsApp Business API (полный пример)

```python
"""
WhatsApp голосовые → SpeechKit → CRM
"""
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_handler():
    data = request.json

    # Извлекаем голосовое
    messages = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [])

    for message in messages:
        if message.get("type") == "audio":
            process_voice_message(
                audio_id=message["audio"]["id"],
                from_number=message["from"]
            )

    return jsonify({"status": "ok"}), 200


def process_voice_message(audio_id: str, from_number: str):
    """Полный цикл обработки голосового."""
    # 1. Скачать
    audio_path = download_whatsapp_audio(audio_id)

    # 2. Транскрибировать
    text = transcribe_any_audio(audio_path)

    # 3. Сохранить в CRM
    save_to_crm(phone=from_number, text=text, type="voice")

    # 4. Отправить ответ
    send_whatsapp_message(
        to=from_number,
        text=f"Спасибо за сообщение! Вы сказали: {text[:100]}..."
    )

    # Cleanup
    os.remove(audio_path)
```

### 2. Telegram Bot (с автоопределением языка)

```python
"""
Telegram бот с автоопределением языка
"""
from telegram.ext import Application, MessageHandler, filters

async def handle_voice_smart(update, context):
    """Обработка с автоопределением языка."""
    voice = update.message.voice

    # Скачать
    file = await context.bot.get_file(voice.file_id)
    audio_path = f"/tmp/{voice.file_id}.ogg"
    await file.download_to_drive(audio_path)

    try:
        # Определение языка по профилю (из username или предыдущих сообщений)
        user_lang = detect_user_language(update.message.from_user)

        # Транскрипция
        result = transcribe_with_profile(audio_path, client_country=user_lang)

        # Ответ
        await update.message.reply_text(
            f"🎤 ({result['language']}) {result['text']}"
        )

    finally:
        os.remove(audio_path)


def detect_user_language(user) -> str:
    """Определение языка пользователя."""
    # По language_code Telegram
    lang_map = {
        "ru": "RU",
        "en": "US",
        "ar": "AE",
        "tr": "TR"
    }
    return lang_map.get(user.language_code, "RU")
```

### 3. Make.com Custom Module (Python server)

```python
"""
Кастомный API для Make.com
"""
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route("/api/transcribe", methods=["POST"])
def make_transcribe():
    """
    Endpoint для Make.com HTTP Request модуля.

    Input:
    {
      "audio_base64": "...",
      "lang": "ru-RU"
    }

    Output:
    {
      "text": "распознанный текст",
      "confidence": 0.85
    }
    """
    data = request.json

    # Декодировать base64 аудио
    audio_base64 = data.get("audio_base64")
    audio_bytes = base64.b64decode(audio_base64)

    # Сохранить временно
    audio_path = "/tmp/make_audio.ogg"
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    # Транскрибировать
    lang = data.get("lang", "ru-RU")
    result = transcribe_with_profile(audio_path, client_country=lang[:2])

    # Cleanup
    os.remove(audio_path)

    return jsonify({
        "text": result["text"],
        "language": result["language"],
        "confidence": result["confidence"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

Использование в Make.com:
```json
{
  "url": "https://your-server.com/api/transcribe",
  "method": "POST",
  "body": {
    "audio_base64": "{{base64(2.data)}}",
    "lang": "ru-RU"
  }
}
```

### 4. n8n Custom Node

```javascript
// n8n-nodes-yandex-speechkit.js
const { IExecuteFunctions } = require('n8n-workflow');
const axios = require('axios');

async function execute() {
  const items = this.getInputData();
  const returnData = [];

  for (let i = 0; i < items.length; i++) {
    const audioData = items[i].binary.data;
    const lang = this.getNodeParameter('language', i, 'ru-RU');

    // Вызов SpeechKit
    const response = await axios.post(
      'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
      audioData,
      {
        params: {
          folderId: process.env.YANDEX_CLOUD_FOLDER_ID,
          lang: lang,
          format: 'oggopus'
        },
        headers: {
          Authorization: `Api-Key ${process.env.YANDEX_CLOUD_API_KEY}`
        }
      }
    );

    returnData.push({
      json: {
        text: response.data.result,
        language: lang
      }
    });
  }

  return [returnData];
}

module.exports = { execute };
```

---

## API Gateway для интеграций

### Универсальный endpoint

```python
"""
Универсальный API для всех интеграций
"""
from flask import Flask, request, jsonify
from functools import wraps
import hashlib
import hmac

app = Flask(__name__)

def verify_signature(f):
    """Проверка подписи запроса."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Signature")
        secret = os.getenv("API_SECRET")

        # Вычисляем ожидаемую подпись
        body = request.get_data()
        expected = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        if signature != expected:
            return jsonify({"error": "Invalid signature"}), 403

        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/v1/transcribe", methods=["POST"])
@verify_signature
def transcribe_api():
    """
    Универсальный API транскрипции.

    POST /api/v1/transcribe
    Headers:
      X-Signature: hmac_sha256(body, secret)
      Content-Type: audio/ogg | application/json

    Body (audio):
      <binary audio data>

    Body (JSON):
      {
        "audio_url": "https://...",
        "lang": "ru-RU",
        "callback_url": "https://..."
      }

    Response:
      {
        "text": "распознанный текст",
        "language": "ru-RU",
        "confidence": 0.85,
        "duration": 45.2
      }
    """
    if request.content_type.startswith("audio/"):
        # Прямая загрузка аудио
        audio_path = "/tmp/uploaded_audio.ogg"
        with open(audio_path, "wb") as f:
            f.write(request.data)

        lang = request.args.get("lang", "ru-RU")

    elif request.content_type == "application/json":
        # JSON с URL
        data = request.json
        audio_url = data.get("audio_url")
        lang = data.get("lang", "ru-RU")

        # Скачать
        import requests
        audio_path = "/tmp/downloaded_audio.ogg"
        audio_response = requests.get(audio_url)
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)

    else:
        return jsonify({"error": "Invalid content type"}), 400

    # Транскрибировать
    try:
        result = transcribe_with_profile(audio_path, client_country=lang[:2])

        response = {
            "text": result["text"],
            "language": result["language"],
            "confidence": result["confidence"],
            "duration": get_audio_duration(audio_path)
        }

        # Callback (если указан)
        callback_url = request.json.get("callback_url") if request.json else None
        if callback_url:
            requests.post(callback_url, json=response)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

---

## Docker deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  transcription-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - YANDEX_CLOUD_API_KEY=${YANDEX_CLOUD_API_KEY}
      - YANDEX_CLOUD_FOLDER_ID=${YANDEX_CLOUD_FOLDER_ID}
      - API_SECRET=${API_SECRET}
    volumes:
      - /tmp:/tmp
    restart: unless-stopped
```

---

## Связанные материалы

| Документ | Описание |
|----------|----------|
| `references/speechkit-basics.md` | Основы API, аутентификация |
| `references/error-handling.md` | Обработка ошибок в production |
| `references/performance-optimization.md` | Оптимизация для высоких нагрузок |

---

## Официальная документация

- WhatsApp Business API: https://developers.facebook.com/docs/whatsapp
- Telegram Bot API: https://core.telegram.org/bots/api
- Make.com: https://www.make.com/en/api-documentation
- n8n: https://docs.n8n.io/integrations/custom-operations/
