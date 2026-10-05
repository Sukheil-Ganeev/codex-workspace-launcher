# Troubleshooting - Решение проблем

## Ошибка кодировки UTF-8

**Симптомы:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
```

**Причина:** Файл chat.txt содержит символы в неправильной кодировке (эмодзи, арабский текст, специальные символы).

**Решение:**

```python
# Открывайте файлы с обработкой ошибок
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Или используйте chardet для определения кодировки
import chardet

with open(filepath, 'rb') as f:
    raw = f.read()
    detected = chardet.detect(raw)
    content = raw.decode(detected['encoding'] or 'utf-8', errors='replace')
```

**В конфиге:**
```python
# config.py
ENCODING = 'utf-8'
ENCODING_ERRORS = 'replace'  # или 'ignore'
```

---

## Не найден chat.txt

**Симптомы:**
```
FileNotFoundError: chat.txt not found in folder "Иван_79051234567"
```

**Причины:**
1. Экспорт был без текста (только медиа)
2. Файл называется иначе (Chat.txt, _chat.txt)
3. Файл повреждён или пустой

**Решение:**

```python
import os

def find_chat_file(folder_path):
    """Поиск файла чата с разными именами"""
    possible_names = ['chat.txt', 'Chat.txt', '_chat.txt', 'WhatsApp Chat.txt']

    for name in possible_names:
        filepath = os.path.join(folder_path, name)
        if os.path.exists(filepath):
            return filepath

    # Поиск по паттерну
    for file in os.listdir(folder_path):
        if file.lower().endswith('.txt') and 'chat' in file.lower():
            return os.path.join(folder_path, file)

    return None
```

**Логирование:**
```python
if not chat_file:
    logging.warning(f"Чат не найден: {folder_path}")
    # Записать в список проблемных папок
    with open('missing_chats.txt', 'a') as f:
        f.write(f"{folder_path}\n")
```

---

## Неправильный формат даты

**Симптомы:**
```
ValueError: time data '26/01/2026' does not match format '%d.%m.%Y'
```

**Причина:** WhatsApp использует разные форматы дат в зависимости от настроек телефона.

**Известные форматы:**
- `26.01.2026` — Россия
- `26/01/2026` — Европа
- `01/26/2026` — США
- `2026-01-26` — ISO

**Решение:**

```python
from datetime import datetime

DATE_FORMATS = [
    '%d.%m.%Y',      # 26.01.2026
    '%d/%m/%Y',      # 26/01/2026
    '%m/%d/%Y',      # 01/26/2026
    '%Y-%m-%d',      # 2026-01-26
    '%d.%m.%y',      # 26.01.26
]

def parse_date(date_str):
    """Парсинг даты с автоопределением формата"""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Неизвестный формат даты: {date_str}")
```

**Автоопределение формата для чата:**
```python
def detect_date_format(chat_content):
    """Определение формата даты по первому сообщению"""
    import re

    # Найти первую дату в чате
    match = re.search(r'\[(\d{1,2}[./]\d{1,2}[./]\d{2,4})', chat_content)
    if match:
        date_str = match.group(1)
        for fmt in DATE_FORMATS:
            try:
                datetime.strptime(date_str, fmt)
                return fmt
            except ValueError:
                continue
    return DATE_FORMATS[0]  # По умолчанию русский формат
```

---

## Медиа не сохранено

**Симптомы:**
- В chat.txt есть `[ФОТО] media/IMG_001.jpg`
- Но файла `media/IMG_001.jpg` не существует

**Причины:**
1. Экспорт был "без медиа"
2. Файлы удалены или перемещены
3. Имя файла содержит спецсимволы

**Решение:**

```python
import os

def validate_media(chat_folder, media_path):
    """Проверка существования медиафайла"""
    full_path = os.path.join(chat_folder, media_path)

    if os.path.exists(full_path):
        return full_path

    # Попробовать без спецсимволов
    clean_path = media_path.replace(' ', '_').replace('(', '').replace(')', '')
    full_clean = os.path.join(chat_folder, clean_path)

    if os.path.exists(full_clean):
        return full_clean

    # Поиск по частичному имени
    media_dir = os.path.join(chat_folder, 'media')
    if os.path.exists(media_dir):
        filename = os.path.basename(media_path)
        for file in os.listdir(media_dir):
            if filename.lower() in file.lower():
                return os.path.join(media_dir, file)

    return None  # Медиа не найдено
```

**Статистика отсутствующих медиа:**
```python
missing_media = []
for msg in messages:
    for media in msg.get('media', []):
        if not validate_media(msg['chat_folder'], media['path']):
            missing_media.append({
                'chat': msg['chat_folder'],
                'media': media['path'],
                'datetime': msg['datetime']
            })

print(f"Отсутствует медиа: {len(missing_media)} файлов")
```

---

## Дубликаты сообщений

**Симптомы:** Одно и то же сообщение появляется несколько раз в выводе.

**Причины:**
1. Повторный экспорт чата
2. Один чат в обоих источниках (personal + business)

**Решение:**

```python
def deduplicate_messages(messages):
    """Удаление дубликатов по уникальному ключу"""
    seen = set()
    unique = []

    for msg in messages:
        # Ключ: datetime + sender + первые 100 символов текста
        key = (
            msg['datetime'],
            msg['sender'],
            msg.get('text', '')[:100]
        )

        if key not in seen:
            seen.add(key)
            unique.append(msg)

    return unique
```

---

## Память заканчивается при парсинге

**Симптомы:**
```
MemoryError: Unable to allocate array
```

**Причина:** Попытка загрузить все сообщения в память одновременно.

**Решение — потоковая обработка:**

```python
import json

def stream_messages(jsonl_path):
    """Генератор для чтения JSONL построчно"""
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Использование
for msg in stream_messages('all_messages.jsonl'):
    # Обработка по одному сообщению
    process(msg)
```

**Батчевая обработка:**
```bash
python scripts/parsing/parse_all_chats.py --batch-size 100
```

---

## Контакты

Если проблема не решена, проверьте логи:
```
D:/Downloads/Туризм-ОАЭ-Проект/02-Данные/_парсинг/логи/parsing.log
```
