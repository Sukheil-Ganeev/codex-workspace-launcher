# Make.com Webhook Integration

FastAPI сервер для интеграции Yandex SpeechKit с Make.com (ex-Integromat).

## Описание

Webhook endpoint для автоматизации транскрипции голосовых через Make.com сценарии.

### Кейс

**Ситуация:** WhatsApp бизнес → Make.com → транскрипция → Google Sheets → уведомление менеджеру

**Решение:** Этот webhook получает аудио URL от Make.com, транскрибирует и возвращает JSON.

## Установка

```bash
pip install -r requirements.txt
```

## Конфигурация

```env
YANDEX_API_KEY=your_key
YANDEX_FOLDER_ID=your_folder
PORT=8000
```

## Запуск

```bash
python main.py
```

Сервер запустится на `http://localhost:8000`

## API Endpoints

### POST /transcribe

Принимает JSON:
```json
{
  "audio_url": "https://example.com/voice.ogg",
  "language": "ru-RU"
}
```

Возвращает:
```json
{
  "success": true,
  "text": "транскрипция",
  "confidence": 0.95,
  "duration": 15.5
}
```

### GET /health

Проверка работоспособности.

## Make.com сценарий

1. Webhook → получить голосовое из WhatsApp/Telegram
2. HTTP Request → POST к этому серверу
3. Google Sheets → сохранить транскрипцию
4. Telegram → отправить уведомление

## Деплой

### Netlify Functions

См. `netlify/` папку для serverless версии.

### Railway.app

```bash
railway init
railway up
```
