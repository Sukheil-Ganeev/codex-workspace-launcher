# Cheatsheet -- Instagram Competitor Analysis

## Instaloader -- быстрый старт

```bash
# Установка
pip install instaloader

# Скачать все посты профиля
instaloader profile competitor_name

# Скачать только последние 10 постов
instaloader --count 10 profile competitor_name

# С логином (больше данных, меньше блокировок)
instaloader --login YOUR_USERNAME profile competitor_name

# Скачать Stories
instaloader --login YOUR_USERNAME --stories profile competitor_name

# Скачать Highlights
instaloader --login YOUR_USERNAME --highlights profile competitor_name

# Только метаданные (без фото/видео)
instaloader --no-pictures --no-videos --no-video-thumbnails profile competitor_name

# С задержками (безопасный режим)
instaloader --request-timeout 300 profile competitor_name
```

## Python-скрипт -- базовый мониторинг

```python
import instaloader
import time
import random
import csv
from datetime import datetime

L = instaloader.Instaloader()
# L.login("your_username", "your_password")  # опционально

competitors = ["competitor1", "competitor2", "competitor3"]

results = []
for comp in competitors:
    profile = instaloader.Profile.from_username(L.context, comp)

    for post in profile.get_posts():
        results.append({
            "competitor": comp,
            "date": post.date_utc.isoformat(),
            "caption": post.caption[:200] if post.caption else "",
            "likes": post.likes,
            "comments": post.comments,
            "hashtags": ", ".join(post.caption_hashtags),
            "url": f"https://instagram.com/p/{post.shortcode}/"
        })
        if len([r for r in results if r["competitor"] == comp]) >= 10:
            break

    time.sleep(random.uniform(60, 120))  # пауза между профилями

# Сохранение в CSV
with open(f"competitors_{datetime.now():%Y%m%d}.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
```

## Выбор подхода -- быстрая таблица

| Вопрос | Approach 1 (Free) | Approach 2 (Cloud) | Approach 3 (AI) |
|--------|-------------------|---------------------|------------------|
| Бюджет | $0 | $49-149/мес | $85-110/мес |
| Конкуренты | 1-10 | 10-50 | 50+ |
| Частота | 1 раз/нед | Ежедневно | Real-time |
| Навыки | Python | Нет | Python + Make.com |
| Настройка | 1 час | 2-3 часа | 1-2 дня |

## Ключевые метрики для мониторинга

```
Engagement Rate = (likes + comments) / followers * 100

Posting Frequency = posts_count / days_period

Hashtag Overlap = common_hashtags / total_hashtags * 100

Price Position = your_price / competitor_avg_price * 100
```

## Безопасные лимиты скрейпинга

| Параметр | Безопасный лимит |
|----------|------------------|
| Постов за сессию | 20-30 |
| Пауза между постами | 60-120 сек |
| Пауза между профилями | 5-10 мин |
| Сессий в день | 1-2 |
| Профилей за сессию | 5-10 |

## Apify -- ключевые команды

```bash
# Установка CLI
npm install -g apify-cli

# Логин
apify login --token YOUR_TOKEN

# Запуск Instagram Scraper
apify call apify/instagram-scraper --input='{
  "directUrls": ["https://instagram.com/competitor1"],
  "resultsLimit": 50,
  "resultsType": "posts"
}'

# Получить результаты последнего запуска
apify datasets list
apify datasets get-items DATASET_ID --format csv
```

## Make.com (Approach 3) -- схема автоматизации

```
Trigger: Schedule (ежедневно 09:00)
    |
    v
Module 1: Apify -- запуск скрейпера
    |
    v
Module 2: Apify -- получить результаты
    |
    v
Module 3: Claude API -- анализ постов
    Prompt: "Извлеки цены, определи тип контента,
             оцени engagement. Формат JSON."
    |
    v
Module 4: Google Sheets -- записать данные
    |
    v
Module 5: Telegram Bot -- отправить сводку
    Формат: "Конкурент X: новая акция safari -20%"
```

## Существующий проект -- пути

```
D:/Downloads/instagram_competitor_analysis/
├── approach_1_instaloader/     # Готовые Python-скрипты
├── approach_2_cloud_services/  # Apify API клиенты, гайды
└── approach_3_full_automation/ # Claude API + Make.com workflows
```

Не пересоздавать код -- использовать готовые реализации из проекта.
