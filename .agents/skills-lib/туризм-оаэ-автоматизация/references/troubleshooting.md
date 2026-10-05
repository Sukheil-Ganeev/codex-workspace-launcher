# Troubleshooting - Решение проблем

## Claude API

### Claude API возвращает ошибку

#### Ошибка 401 Unauthorized

**Причина:** Неверный или отсутствующий API ключ.

**Решение:**
```python
# Проверьте, что ключ загружен
import os
key = os.getenv('ANTHROPIC_API_KEY')
print(f"Key loaded: {key[:10]}..." if key else "KEY NOT FOUND!")

# Убедитесь, что .env загружен
from dotenv import load_dotenv
load_dotenv()  # Вызовите ДО использования os.getenv
```

**В make.com:**
- Проверьте Header: `x-api-key` (не `Authorization`)
- Убедитесь, что нет лишних пробелов в ключе

---

#### Ошибка 429 Rate Limit

**Причина:** Превышен лимит запросов.

**Решение:**
```python
import time
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
def call_claude_with_retry(message: str):
    try:
        return client.messages.create(...)
    except anthropic.RateLimitError:
        time.sleep(60)  # Подождать минуту
        raise  # retry сработает
```

**Лимиты Claude API:**
- Tier 1: 60 RPM (requests per minute)
- Tier 2: 1000 RPM
- Tier 3: 4000 RPM

---

#### Ошибка 500 Internal Server Error

**Причина:** Временная проблема на стороне Anthropic.

**Решение:**
```python
# Добавьте retry с exponential backoff
import anthropic
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, max=60))
def safe_claude_call(messages):
    try:
        return client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=messages
        )
    except anthropic.InternalServerError:
        print("Claude API временно недоступен, повтор...")
        raise
```

---

#### Ошибка: Некорректный JSON в ответе

**Причина:** Claude не всегда возвращает чистый JSON.

**Решение:**
```python
import json
import re

def extract_json(text: str) -> dict:
    """Извлекает JSON из ответа Claude"""

    # Удаляем markdown блоки
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)

    # Ищем JSON объект
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")

    return {"error": "no_json_found", "raw_text": text}
```

---

## Whisper API

### Whisper не транскрибирует

#### Ошибка: File too large

**Причина:** Файл больше 25 MB.

**Решение:**
```python
from pydub import AudioSegment
import os

def split_audio(file_path: str, max_size_mb: int = 24) -> list[str]:
    """Разбивает большой аудиофайл на части"""

    audio = AudioSegment.from_file(file_path)
    file_size = os.path.getsize(file_path)

    if file_size <= max_size_mb * 1024 * 1024:
        return [file_path]

    # Разбиваем на 5-минутные части
    chunk_length = 5 * 60 * 1000  # 5 минут в миллисекундах
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_length)):
        chunk = audio[start:start + chunk_length]
        chunk_path = f"{file_path}_part{i}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)

    return chunks
```

---

#### Ошибка: Unsupported audio format

**Причина:** Формат не поддерживается Whisper.

**Поддерживаемые форматы:** mp3, mp4, mpeg, mpga, m4a, wav, webm

**Решение:**
```python
from pydub import AudioSegment

def convert_to_mp3(input_path: str) -> str:
    """Конвертирует любой аудиофайл в MP3"""

    output_path = input_path.rsplit('.', 1)[0] + '.mp3'

    # Определяем формат входного файла
    audio = AudioSegment.from_file(input_path)

    # Экспортируем в MP3
    audio.export(output_path, format="mp3", bitrate="128k")

    return output_path
```

---

#### Ошибка: Poor transcription quality

**Причина:** Шум, акцент, технические термины.

**Решение:**
```python
def transcribe_with_context(audio_path: str) -> str:
    """Транскрипция с контекстом для улучшения качества"""

    # Добавьте prompt с терминами вашего бизнеса
    tourism_terms = """
    Ferrari World, Burj Khalifa, Dubai Mall, Atlantis, Palm Jumeirah,
    Desert Safari, Abu Dhabi, Sharjah, Ajman, Ras Al Khaimah,
    трансфер, экскурсия, виза, дирхам, AED, пикап, дропофф,
    Марсель, Сокол, VIP, бизнес-класс
    """

    with open(audio_path, "rb") as f:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            prompt=tourism_terms,  # Подсказка для Whisper
            language="ru"  # Указываем язык явно
        )

    return transcription.text
```

---

## make.com

### make.com сценарий падает

#### Ошибка: Connection timeout

**Причина:** API не отвечает вовремя.

**Решение:**
1. В настройках HTTP модуля:
   - Timeout: 60000 (60 секунд)
   - Retry: 3
   - Retry interval: 5 секунд

2. Добавьте Error Handler:
   ```
   [HTTP Module] → [Error Handler] → [Slack Notification]
                                   → [Save to Error Log]
   ```

---

#### Ошибка: Webhook не срабатывает

**Причина:** Webhook URL неактивен или неправильно настроен.

**Диагностика:**
1. Проверьте статус webhook в make.com (должен быть "Listening")
2. Отправьте тестовый запрос:
   ```bash
   curl -X POST https://hook.eu2.make.com/xxx \
        -H "Content-Type: application/json" \
        -d '{"test": "message"}'
   ```
3. Проверьте логи в make.com → Scenario → History

**Решение:**
- Пересоздайте webhook модуль
- Проверьте SSL сертификат (должен быть валидный)
- Убедитесь, что IP make.com не заблокирован

---

#### Ошибка: Data structure mismatch

**Причина:** Входные данные не соответствуют ожидаемой структуре.

**Решение:**
```json
// Добавьте модуль JSON Parse с fallback
{
  "name": "Safe Parse",
  "type": "json.parse",
  "config": {
    "input": "{{1.body}}",
    "fallback": {
      "error": true,
      "raw": "{{1.body}}"
    }
  }
}
```

---

#### Ошибка: Operations limit exceeded

**Причина:** Превышен лимит операций на тарифе.

**Решение:**
1. Оптимизируйте сценарии (меньше модулей)
2. Используйте фильтры ДО тяжелых операций
3. Batch обработка вместо поштучной
4. Апгрейд тарифа при необходимости

---

## Дашборд

### Дашборд не обновляется

#### Проблема: Данные устарели

**Причина:** Кэширование или проблемы с источником данных.

**Решение:**
```python
# Добавьте timestamp в данные
import time

def get_dashboard_data():
    data = fetch_from_airtable()
    data['_updated_at'] = time.time()
    data['_cache_valid_until'] = time.time() + 300  # 5 минут
    return data

# В HTML добавьте автообновление
# <script>
# setInterval(() => location.reload(), 300000);  // каждые 5 минут
# </script>
```

---

#### Проблема: Графики не отображаются

**Причина:** Ошибки JavaScript или отсутствие данных.

**Диагностика:**
1. Откройте DevTools (F12) → Console
2. Проверьте ошибки JavaScript
3. Проверьте Network tab на failed requests

**Решение:**
```python
# Добавьте проверку данных перед построением графика
def create_safe_chart(data):
    if not data or len(data) == 0:
        return create_empty_chart("Нет данных")

    try:
        return create_chart(data)
    except Exception as e:
        return create_error_chart(str(e))
```

---

#### Проблема: Медленная загрузка

**Причина:** Слишком много данных или неоптимизированные запросы.

**Решение:**
```python
# 1. Ограничьте объем данных
data = fetch_data(limit=1000, days=30)

# 2. Агрегируйте на сервере
aggregated = aggregate_by_day(data)

# 3. Используйте lazy loading
fig.update_layout(
    updatemenus=[{
        'type': 'dropdown',
        'buttons': [
            {'label': '7 дней', 'method': 'relayout', 'args': [{'xaxis.range': last_7_days}]},
            {'label': '30 дней', 'method': 'relayout', 'args': [{'xaxis.range': last_30_days}]}
        ]
    }]
)
```

---

## Airtable

### Airtable rate limit

**Причина:** Более 5 запросов в секунду.

**Решение:**
```python
import time
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=5, period=1)  # 5 запросов в секунду
def airtable_request(table, data):
    return table.create(data)

# Для batch операций
def batch_create(records: list):
    """Создает записи пачками по 10"""
    for i in range(0, len(records), 10):
        batch = records[i:i+10]
        table.batch_create(batch)
        time.sleep(0.2)  # Небольшая пауза между batch
```

---

### Airtable field type error

**Причина:** Тип данных не соответствует типу поля.

**Решение:**
```python
def sanitize_for_airtable(data: dict) -> dict:
    """Приводит данные к правильным типам для Airtable"""

    sanitized = {}

    for key, value in data.items():
        if value is None:
            continue  # Airtable не принимает None

        if isinstance(value, bool):
            sanitized[key] = value
        elif isinstance(value, (int, float)):
            sanitized[key] = value
        elif isinstance(value, list):
            # Для Linked Records или Multiple Select
            sanitized[key] = value
        else:
            # Все остальное в строку
            sanitized[key] = str(value)

    return sanitized
```

---

## Общие проблемы

### Encoding ошибки (Unicode)

**Причина:** Неправильная кодировка при работе с русским текстом.

**Решение:**
```python
# Всегда указывайте encoding при работе с файлами
with open(file_path, 'r', encoding='utf-8') as f:
    data = f.read()

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(data)

# Для JSON
json.dumps(data, ensure_ascii=False)  # Сохраняет кириллицу
```

---

### Memory ошибки при больших файлах

**Причина:** Загрузка всего файла в память.

**Решение:**
```python
# Потоковая обработка
def process_large_jsonl(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:  # Читаем построчно
            record = json.loads(line)
            yield process_record(record)

# Для pandas используйте chunks
for chunk in pd.read_json(file_path, lines=True, chunksize=1000):
    process_dataframe(chunk)
```

---

### Timezone проблемы

**Причина:** Несоответствие часовых поясов (UTC vs UAE).

**Решение:**
```python
from datetime import datetime
import pytz

UAE_TZ = pytz.timezone('Asia/Dubai')

def to_uae_time(utc_dt: datetime) -> datetime:
    """Конвертирует UTC в UAE время"""
    if utc_dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(utc_dt)
    return utc_dt.astimezone(UAE_TZ)

def now_uae() -> datetime:
    """Текущее время в ОАЭ"""
    return datetime.now(UAE_TZ)
```
