---
id: EXP-025
date: 2026-02-05
type: pattern
severity: medium
category: images
projects: []
related: [EXP-026, EXP-027]
tags: [images, api, pexels, unsplash, download]
status: verified
---

# Скачивание изображений через API стоков

## Проблема

Прямое скачивание изображений через `curl` или `wget` с популярных источников (Wikimedia, Unsplash, Pexels) часто блокируется:
- **Hotlinking protection** — сайты проверяют Referer и User-Agent
- Возвращается HTML страница (2-3 KB) вместо изображения
- Даже с правильными заголовками запросы блокируются

```bash
# ❌ НЕ РАБОТАЕТ
curl -L -A "Mozilla/5.0" -o bear.jpg "https://images.unsplash.com/..."
# Результат: 2145 байт HTML вместо изображения
```

## Решение

Использовать официальные API бесплатных стоков:

| Сервис | Лимит | API |
|--------|-------|-----|
| **Pexels** | 200 req/час | https://api.pexels.com/v1/search |
| **Unsplash** | 50 req/час | https://api.unsplash.com/search/photos |
| **Pixabay** | 100 req/мин | https://pixabay.com/api/ |
| **Freepik** | 100 req/день | https://api.freepik.com |

## Реализация

### Минимальный скрипт (Pexels)

```python
import requests

PEXELS_KEY = 'your_api_key'

def download_pexels(query: str, filename: str):
    # 1. Поиск
    r = requests.get(
        'https://api.pexels.com/v1/search',
        params={'query': query, 'per_page': 5},
        headers={'Authorization': PEXELS_KEY}
    )

    photos = r.json().get('photos', [])
    if not photos:
        return None

    # 2. Скачивание первого результата
    url = photos[0]['src']['large2x']  # 1880px качество
    img = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(img.content)

    return filename

# Использование
download_pexels('european badger wildlife', 'badger.jpg')
```

### Универсальная утилита

Полная утилита с поддержкой всех API:
`D:/Downloads/image-downloader/image_downloader.py`

```python
from image_downloader import ImageDownloader

dl = ImageDownloader(
    pexels_key='...',
    unsplash_key='...',
    pixabay_key='...'
)

# Поиск по всем источникам
results = dl.search_all('brown bear', per_page=5)

# Поиск и скачивание
dl.search_and_download('hibernating bat', 'bat.jpg', source='pexels')
```

## Получение API ключей

### Pexels (рекомендую — лучший лимит)
1. https://www.pexels.com/api/
2. Регистрация → "Your API Key"
3. Описание: `Educational presentations, non-commercial use`

### Unsplash (лучшее качество)
1. https://unsplash.com/developers
2. "New Application" → Accept terms
3. Описание: `Educational tool for school presentations`
4. Скопировать **Access Key** (не Secret Key!)

### Pixabay
1. https://pixabay.com/api/docs/
2. После логина ключ показан на странице документации

## Хранение ключей

Файл `.env`:
```bash
# D:/Downloads/image-downloader/.env
PEXELS_API_KEY=uCGmonzY7...
UNSPLASH_ACCESS_KEY=huj8QnVz...
PIXABAY_API_KEY=54518429-...
FREEPIK_API_KEY=FPSX1d93...
```

## Альтернативы (если API не подходит)

1. **DevTools MCP** — скачивание через браузер (обходит hotlinking)
   ```python
   # Открыть URL в браузере
   page.goto('https://upload.wikimedia.org/.../badger.jpg')
   # Сделать скриншот как JPEG
   page.screenshot(path='badger.jpg', type='jpeg', quality=95)
   ```

2. **curl с Referer** (иногда работает)
   ```bash
   curl -H "Referer: https://upload.wikimedia.org/" \
        -A "Mozilla/5.0" -o img.jpg "URL"
   ```

## Когда применять

- Презентации требуют качественные изображения животных/природы/объектов
- Нужно автоматизировать скачивание нескольких изображений
- Прямое скачивание через curl возвращает ошибку или HTML

## Связанные файлы

- `D:/Downloads/image-downloader/image_downloader.py` — универсальная утилита
- `D:/Downloads/image-downloader/.env` — API ключи
