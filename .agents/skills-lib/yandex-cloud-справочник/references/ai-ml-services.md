# AI/ML Services

## YandexGPT API

**Модели:**
- YandexGPT 5 Pro (128k context, лучшее качество)
- YandexGPT 4 Lite (быстрый, дешевый)

**Цены (2026):**
- Lite: 0.12₽/1k tokens
- Pro: 0.60₽/1k tokens

### Пример (Node.js)

```javascript
const axios = require('axios');

async function generateText(prompt) {
    const response = await axios.post(
        'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
        {
            modelUri: 'gpt://b1g.../yandexgpt/latest',
            completionOptions: {
                temperature: 0.7,
                maxTokens: 1000
            },
            messages: [
                { role: 'system', content: 'Ты ассистент туристического агентства в Дубае' },
                { role: 'user', content: prompt }
            ]
        },
        {
            headers: {
                'Authorization': `Bearer ${process.env.YC_IAM_TOKEN}`,
                'Content-Type': 'application/json'
            }
        }
    );

    return response.data.result.alternatives[0].message.content;
}

// Use
const answer = await generateText('Какие экскурсии есть в Дубае?');
```

### Streaming

```javascript
async function streamText(prompt) {
    const response = await axios.post(
        'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync',
        { /* params */ },
        { responseType: 'stream' }
    );

    response.data.on('data', chunk => {
        const text = JSON.parse(chunk).result.alternatives[0].message.content;
        process.stdout.write(text);
    });
}
```

---

## SpeechKit (Speech Recognition)

**Распознавание речи:**
- Языки: RU, EN, TR, AR и другие
- Форматы: WAV, MP3, OGG
- Streaming и batch режимы

**Цена:** 240₽/час аудио

### Пример (Python)

```python
import grpc
import yandex.cloud.ai.stt.v2.stt_service_pb2 as stt_service_pb2
import yandex.cloud.ai.stt.v2.stt_service_pb2_grpc as stt_service_pb2_grpc

def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    creds = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', creds)
    stub = stt_service_pb2_grpc.SttServiceStub(channel)

    request = stt_service_pb2.RecognizeRequest(
        config=stt_service_pb2.RecognitionConfig(
            specification=stt_service_pb2.RecognitionSpec(
                languageCode='ru-RU',
                profanityFilter=False,
                model='general',
                audioEncoding='LINEAR16_PCM',
                sampleRateHertz=8000
            )
        ),
        audio=stt_service_pb2.RecognitionAudio(content=audio_data)
    )

    metadata = [('authorization', f'Bearer {IAM_TOKEN}')]
    response = stub.Recognize(request, metadata=metadata)

    return ' '.join([alt.text for result in response.results for alt in result.alternatives])

# Use
text = transcribe_audio('voice_message.wav')
print(text)
```

### Telegram Bot integration

```javascript
// Обработка голосовых сообщений в Telegram
bot.on('voice', async (msg) => {
    const chatId = msg.chat.id;
    const fileId = msg.voice.file_id;

    // Download audio
    const fileUrl = await bot.getFileLink(fileId);
    const response = await axios.get(fileUrl, { responseType: 'arraybuffer' });

    // Transcribe
    const text = await transcribe(response.data);

    bot.sendMessage(chatId, `Вы сказали: ${text}`);
});
```

---

## Vision OCR

**Распознавание текста на изображениях:**
- Документы, чеки, паспорта
- 10+ языков
- Table detection

**Цена:** 120₽/1000 изображений

### Пример (Python)

```python
import boto3
import base64

def recognize_text(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response = requests.post(
        'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze',
        headers={'Authorization': f'Bearer {IAM_TOKEN}'},
        json={
            'folderId': FOLDER_ID,
            'analyze_specs': [{
                'content': image_data,
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'text_detection_config': {
                        'language_codes': ['en', 'ru']
                    }
                }]
            }]
        }
    )

    results = response.json()['results'][0]
    return results['results'][0]['textDetection']['pages'][0]['blocks']

# Use
text_blocks = recognize_text('passport.jpg')
for block in text_blocks:
    print(block['lines'][0]['words'][0]['text'])
```

---

## Translate API

**Перевод текста:**
- 90+ языков
- HTML поддержка

**Цена:** 480₽/1M символов

### Пример (Node.js)

```javascript
async function translate(text, targetLang) {
    const response = await axios.post(
        'https://translate.api.cloud.yandex.net/translate/v2/translate',
        {
            folderId: FOLDER_ID,
            texts: [text],
            targetLanguageCode: targetLang
        },
        {
            headers: {
                'Authorization': `Bearer ${IAM_TOKEN}`
            }
        }
    );

    return response.data.translations[0].text;
}

// Use
const translated = await translate('Hello, world!', 'ru');
// Привет, мир!
```

---

## Tourism Use Cases

### Кейс 1: AI Chatbot (Telegram)

```javascript
// Бот отвечает на вопросы о турах используя YandexGPT
bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const question = msg.text;

    // Context о турах из БД
    const tours = await getTours();
    const context = tours.map(t => `${t.name}: ${t.description}, цена ${t.price} AED`).join('\n');

    // YandexGPT
    const answer = await generateText(`
        Контекст: ${context}
        Вопрос клиента: ${question}
        Ответь как консультант туристического агентства.
    `);

    bot.sendMessage(chatId, answer);
});
```

### Кейс 2: Voice Message Transcription

```javascript
// Транскрипция голосовых сообщений клиентов
bot.on('voice', async (msg) => {
    const chatId = msg.chat.id;

    // Download & transcribe
    const audio = await downloadVoice(msg.voice.file_id);
    const text = await transcribe(audio);

    // YandexGPT для ответа
    const reply = await generateText(`Клиент спросил: ${text}. Ответь профессионально.`);

    bot.sendMessage(chatId, reply);
});
```

### Кейс 3: Document OCR

```python
# Автоматическое распознавание паспортов для бронирований
def process_passport(image_path):
    text_blocks = recognize_text(image_path)

    # Extract fields
    passport_data = {
        'name': extract_name(text_blocks),
        'passport_number': extract_passport_number(text_blocks),
        'nationality': extract_nationality(text_blocks)
    }

    # Save to DB
    save_customer(passport_data)
```

---

**См. также:**
- `assets/examples/ai-chatbot-telegram/` - полный Telegram бот
- `tourism-business-cases.md` - кейсы #2, #4, #9
