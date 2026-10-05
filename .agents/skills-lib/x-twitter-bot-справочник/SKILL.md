---
name: x-twitter-bot-справочник
description: "Production-ready руководство по X (Twitter) Bot API v2 для автоматизации и создания ботов. Filtered Stream, DM автоматизация, автопостинг, мониторинг. Используй когда нужно создать бота для X/Twitter."
---
# X (Twitter) Bot API v2 — Справочник

> Production-ready руководство по созданию ботов для X (Twitter). API v2, OAuth 2.0, Filtered Stream, автопостинг, DM-автоматизация, мониторинг упоминаний. Актуально на 2025-2026.

---

## 1. Quick Start — Первый пост за 10 минут

### Шаг 1: Регистрация Developer Account

1. Перейти на **developer.x.com** и войти в аккаунт X
2. Заполнить заявку на Developer Account (описание use case обязательно)
3. Принять Developer Agreement and Policy
4. Получить доступ к Developer Portal

### Шаг 2: Создание App

1. Developer Portal → Projects & Apps → Create Project
2. Указать имя проекта и описание (для туризма: "Tourism booking automation bot")
3. Выбрать Use Case: "Making a bot"
4. Внутри проекта создать App

### Шаг 3: Получение ключей

В настройках App → Keys and Tokens:
- **API Key** (Consumer Key) — идентификатор приложения
- **API Key Secret** (Consumer Secret) — секрет приложения
- **Bearer Token** — для App-only аутентификации (только чтение)
- **Access Token + Secret** — для действий от имени владельца App

### Шаг 4: Первый твит (Python + tweepy)

```python
import tweepy

client = tweepy.Client(
    consumer_key="YOUR_API_KEY",
    consumer_secret="YOUR_API_KEY_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
)

response = client.create_tweet(text="Hello from my X bot!")
print(f"Tweet ID: {response.data['id']}")
```

```bash
pip install tweepy
python bot.py
```

**Важно:** Free tier позволяет публиковать до 500 постов/месяц на App. Для полноценного бота нужен минимум Basic ($200/мес).

---

## 2. Архитектура API v2

### Структура API

X API v2 построен на REST-архитектуре с дополнительным Streaming-слоем:

| Компонент | Протокол | Назначение |
|-----------|----------|------------|
| REST endpoints | HTTPS (JSON) | CRUD операции: посты, лайки, пользователи |
| Filtered Stream | SSE (Server-Sent Events) | Реалтайм фильтрация публичных постов |
| Media Upload | Multipart/chunked | Загрузка изображений, видео, GIF |

**Base URL:** `https://api.x.com/2/`

### Тарифные планы (2025-2026)

| Параметр | Free | Basic ($200/мес) | Pro ($5,000/мес) | Enterprise |
|----------|------|-------------------|-------------------|------------|
| Посты (запись) | 500/мес на App, 1,500 на юзера | 50,000/мес | 300,000/мес | Без лимита |
| Посты (чтение) | Нет | 10,000/мес | 1,000,000/мес | Full firehose |
| Filtered Stream | Нет | 25 правил | 1,000 правил | 250,000 правил |
| Search API | Нет | Recent (7 дней) | Full-archive | Full-archive |
| DM API | Нет | Да | Да | Да |
| Media Upload | Да (только запись) | Да | Да | Да |
| Apps | 1 | 2 | 3 | Несколько |

**КРИТИЧНО:** Free tier крайне ограничен — только запись постов (500/мес), нет чтения, нет стриминга, нет DM. Для любого серьёзного бота нужен **минимум Basic** ($200/мес).

### Pay-Per-Use (пилот)

С декабря 2025 X тестирует модель оплаты по использованию на основе кредитов. Пока в закрытой бете — планировать на основе стандартных тарифов.

---

## 3. Аутентификация

### 3.1 OAuth 2.0 App-Only (Bearer Token)

Для операций чтения без привязки к пользователю.

```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")

# Поиск твитов (только чтение)
tweets = client.search_recent_tweets(query="#Dubai tourism", max_results=10)
```

**Применение:** поиск, чтение постов, получение информации о пользователях.
**Ограничение:** нельзя писать посты, лайкать, ретвитить — только чтение.

### 3.2 OAuth 2.0 с PKCE (от имени пользователя)

Для действий от имени пользователя (посты, DM, лайки). Рекомендуемый метод для ботов.

```python
import tweepy

# Настройка OAuth 2.0 PKCE
oauth2_handler = tweepy.OAuth2UserHandler(
    client_id="YOUR_CLIENT_ID",
    redirect_uri="https://your-callback.com/callback",
    scope=["tweet.read", "tweet.write", "users.read", "dm.read", "dm.write"],
    client_secret="YOUR_CLIENT_SECRET"
)

# Получить URL для авторизации
auth_url = oauth2_handler.get_authorization_url()
# Пользователь авторизует -> получаем code -> обмениваем на токен
access_token = oauth2_handler.fetch_token(response_url)
```

**Токены:**
- Access Token — живёт **2 часа**
- Refresh Token — живёт **6 месяцев**
- Бот должен автоматически обновлять токены через refresh

**Скоупы (scope):**

| Scope | Описание |
|-------|----------|
| `tweet.read` | Чтение постов |
| `tweet.write` | Публикация постов |
| `users.read` | Чтение профилей |
| `dm.read` | Чтение DM |
| `dm.write` | Отправка DM |
| `follows.read` | Чтение подписок |
| `follows.write` | Подписка/отписка |
| `like.read` | Чтение лайков |
| `like.write` | Лайк/анлайк |
| `media.write` | Загрузка медиа |
| `offline.access` | Для refresh token |

### 3.3 OAuth 1.0a (устаревший, но рабочий)

Используется для некоторых v1.1 совместимых endpoints. Работает через API Key + Secret + Access Token + Secret (4 ключа).

```python
client = tweepy.Client(
    consumer_key="API_KEY",
    consumer_secret="API_KEY_SECRET",
    access_token="ACCESS_TOKEN",
    access_token_secret="ACCESS_TOKEN_SECRET"
)
```

### Хранение токенов для ботов

```python
import json
from pathlib import Path

TOKEN_FILE = "tokens.json"

def save_tokens(access_token, refresh_token):
    Path(TOKEN_FILE).write_text(json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token
    }))

def load_tokens():
    data = json.loads(Path(TOKEN_FILE).read_text())
    return data["access_token"], data["refresh_token"]

def refresh_access_token(client_id, client_secret, refresh_token):
    """Обновление access_token через refresh_token"""
    import requests
    resp = requests.post("https://api.x.com/2/oauth2/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }, auth=(client_id, client_secret))
    data = resp.json()
    save_tokens(data["access_token"], data["refresh_token"])
    return data["access_token"]
```

---

## 4. Автопостинг

### 4.1 Публикация текстового поста

```python
# POST /2/tweets
response = client.create_tweet(text="Экскурсии по Дубаю со скидкой 20%!")
tweet_id = response.data["id"]
```

### 4.2 Публикация с медиа

С января 2025 медиа загружается через v2 endpoint `POST /2/media/upload`.

```python
# Загрузка медиа (требуется OAuth 1.0a для tweepy или прямой запрос к v2)
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)
api = tweepy.API(auth)
media = api.media_upload(filename="dubai_tour.jpg")

# Публикация с медиа
client.create_tweet(text="Джип-сафари в пустыне!", media_ids=[media.media_id])
```

**Лимиты медиа:**
- Изображения: до 5 MB (JPEG, PNG, GIF, WEBP), до 4 штук на пост
- GIF: до 15 MB, 1 на пост
- Видео: до 512 MB, до 140 сек, 1 на пост

### 4.3 Треды (цепочки постов)

```python
# Первый пост
first = client.create_tweet(text="1/ Топ-5 экскурсий в Дубае на 2026 год:")

# Ответ на первый (тред)
second = client.create_tweet(
    text="2/ Burj Khalifa At The Top — лучший вид на город",
    in_reply_to_tweet_id=first.data["id"]
)

third = client.create_tweet(
    text="3/ Desert Safari — джип, верблюды, ужин в пустыне",
    in_reply_to_tweet_id=second.data["id"]
)
```

### 4.4 Планировщик постов

```python
import schedule
import time

def post_daily_offer():
    offers = load_offers_from_db()  # Ваш источник данных
    offer = offers.pop(0)
    client.create_tweet(text=offer["text"], media_ids=offer.get("media_ids"))

schedule.every().day.at("09:00").do(post_daily_offer)
schedule.every().day.at("18:00").do(post_daily_offer)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 4.5 Удаление поста

```python
# DELETE /2/tweets/:id
client.delete_tweet(tweet_id)
```

---

## 5. Filtered Stream

Filtered Stream позволяет получать посты в реальном времени по заданным правилам.

### 5.1 Управление правилами

```python
# Добавление правил
rules = [
    tweepy.StreamRule(value="#Dubai tourism lang:en", tag="dubai_en"),
    tweepy.StreamRule(value="#Дубай экскурсии lang:ru", tag="dubai_ru"),
    tweepy.StreamRule(value="@your_bot_handle", tag="mentions"),
]
client_stream.add_rules(rules)

# Просмотр активных правил
current_rules = client_stream.get_rules()

# Удаление правил по ID
client_stream.delete_rules(rule_ids)
```

### 5.2 Операторы правил

| Оператор | Пример | Описание |
|----------|--------|----------|
| keyword | `Dubai tour` | Содержит оба слова |
| "exact" | `"desert safari"` | Точная фраза |
| #hashtag | `#DubaiTourism` | Хэштег |
| @mention | `@mybot` | Упоминание |
| from: | `from:visitdubai` | От конкретного юзера |
| to: | `to:mybot` | Адресовано юзеру |
| url: | `url:"booking.com"` | Содержит URL |
| has:media | `#Dubai has:media` | С медиа-вложением |
| has:images | `#Dubai has:images` | С изображением |
| has:links | `tourism has:links` | Со ссылкой |
| lang: | `Dubai lang:ru` | Язык поста |
| is:retweet | `-is:retweet` | Исключить ретвиты |
| is:reply | `-is:reply` | Исключить ответы |
| place_country: | `place_country:AE` | Геолокация ОАЭ |

**Лимиты правил:**
- Free: недоступно
- Basic: 25 правил, до 512 символов каждое
- Pro: 1,000 правил, до 1,024 символов
- Enterprise: 250,000 правил, до 2,048 символов

**Логические операторы:** `AND` (пробел), `OR`, `NOT` (-), группировка `()`

```
Пример: (#Dubai OR #AbuDhabi) (tour OR excursion OR safari) -is:retweet lang:en
```

### 5.3 Подключение к стриму

```python
import tweepy

class TourismStreamClient(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(f"[NEW] {tweet.text[:100]}")
        # Обработка: сохранение, уведомление, авто-ответ
        self.process_tourism_lead(tweet)

    def on_errors(self, errors):
        print(f"Error: {errors}")

    def on_disconnect(self):
        print("Disconnected, reconnecting...")
        return True  # Auto-reconnect

    def process_tourism_lead(self, tweet):
        # Ваша логика обработки
        pass

stream = TourismStreamClient(bearer_token="YOUR_BEARER")
stream.filter(
    tweet_fields=["author_id", "created_at", "lang", "geo"],
    expansions=["author_id"],
    user_fields=["name", "username", "location"]
)
```

### 5.4 Reconnect-стратегия

При обрыве соединения X рекомендует экспоненциальный backoff:

```python
import time

def connect_with_backoff(stream, max_retries=10):
    retries = 0
    while retries < max_retries:
        try:
            stream.filter(threaded=True)
            retries = 0  # Сброс при успешном подключении
        except Exception as e:
            wait = min(2 ** retries, 300)  # Max 5 минут
            print(f"Reconnecting in {wait}s... ({e})")
            time.sleep(wait)
            retries += 1
```

---

## 6. Search API

### 6.1 Recent Search (последние 7 дней)

```python
# GET /2/tweets/search/recent
tweets = client.search_recent_tweets(
    query='#Dubai excursion -is:retweet lang:en',
    max_results=100,
    tweet_fields=["created_at", "public_metrics", "author_id", "lang"],
    expansions=["author_id"],
    user_fields=["name", "username", "location", "public_metrics"]
)

for tweet in tweets.data:
    print(f"{tweet.created_at}: {tweet.text[:80]}")
```

**Доступность:** Basic и выше. Free — недоступен.

### 6.2 Full-Archive Search (весь архив)

```python
# GET /2/tweets/search/all (Pro и Enterprise)
tweets = client.search_all_tweets(
    query='#DubaiTourism',
    start_time="2024-01-01T00:00:00Z",
    end_time="2025-01-01T00:00:00Z",
    max_results=500
)
```

**Доступность:** только Pro ($5,000/мес) и Enterprise.

### 6.3 Tweet Counts

```python
# GET /2/tweets/counts/recent — количество твитов по запросу
counts = client.get_recent_tweets_count(query="#Dubai tourism")
for bucket in counts.data:
    print(f"{bucket['start']}: {bucket['tweet_count']} tweets")
```

---

## 7. DM-автоматизация

### 7.1 Отправка Direct Message

```python
# POST /2/dm_conversations/with/:participant_id/messages
import requests

headers = {"Authorization": f"Bearer {access_token}"}
data = {"text": "Спасибо за обращение! Чем могу помочь?"}

resp = requests.post(
    f"https://api.x.com/2/dm_conversations/with/{user_id}/messages",
    json=data,
    headers=headers
)
```

### 7.2 Получение DM-событий

```python
# GET /2/dm_events
resp = requests.get(
    "https://api.x.com/2/dm_events",
    params={
        "dm_event.fields": "id,text,created_at,sender_id,dm_conversation_id",
        "max_results": 100
    },
    headers=headers
)
```

### 7.3 DM-бот для туризма

```python
class TourismDMBot:
    """Простой DM-бот с FAQ по турам в ОАЭ"""

    RESPONSES = {
        "price": "Цены на экскурсии от 100 AED. Напишите название тура для точной цены.",
        "safari": "Desert Safari: от 150 AED/чел. Включает джип, ужин, шоу. Пишите для брони!",
        "burj": "Burj Khalifa At The Top: от 170 AED. At The Top SKY: от 380 AED.",
        "yacht": "Яхты от 500 AED/час. Более 300 яхт. Детали: @ParamountYachts",
        "transfer": "Трансферы из аэропорта: эконом от 150 AED, бизнес от 250 AED.",
        "help": "Доступные команды: price, safari, burj, yacht, transfer",
    }

    def handle_message(self, text, sender_id):
        text_lower = text.lower().strip()
        for keyword, response in self.RESPONSES.items():
            if keyword in text_lower:
                self.send_dm(sender_id, response)
                return
        self.send_dm(sender_id,
            "Здравствуйте! Я бот-помощник. Напишите 'help' для списка команд "
            "или опишите ваш вопрос — оператор ответит в ближайшее время.")

    def send_dm(self, user_id, text):
        requests.post(
            f"https://api.x.com/2/dm_conversations/with/{user_id}/messages",
            json={"text": text},
            headers=self.headers
        )
```

### 7.4 Welcome Message

Welcome Message — автоматическое приветствие при открытии DM-диалога. Настраивается через Account Activity API (Enterprise) или polling-механизм:

```python
def check_new_conversations(self):
    """Polling: проверка новых DM каждые 30 сек"""
    events = self.get_dm_events()
    for event in events:
        if event["sender_id"] != self.bot_user_id:
            if self.is_new_conversation(event["dm_conversation_id"]):
                self.send_welcome(event["sender_id"])
```

---

## 8. Мониторинг упоминаний

### 8.1 Mentions Timeline

```python
# GET /2/users/:id/mentions
mentions = client.get_users_mentions(
    id=bot_user_id,
    max_results=100,
    tweet_fields=["created_at", "author_id", "in_reply_to_user_id"],
    since_id=last_processed_id  # Только новые
)

for mention in mentions.data or []:
    print(f"@{mention.author_id} mentioned you: {mention.text[:80]}")
    process_mention(mention)
```

### 8.2 Keyword Tracking через Search

```python
def monitor_keywords(keywords, interval=60):
    """Мониторинг ключевых слов через периодический поиск"""
    last_id = None
    while True:
        query = " OR ".join(keywords) + " -is:retweet"
        tweets = client.search_recent_tweets(
            query=query,
            max_results=10,
            since_id=last_id,
            tweet_fields=["created_at", "author_id", "public_metrics"]
        )
        if tweets.data:
            last_id = tweets.data[0].id
            for tweet in tweets.data:
                handle_lead(tweet)
        time.sleep(interval)

# Пример для туризма
monitor_keywords(["ищу экскурсию Дубай", "тур ОАЭ цена", "Dubai tour cheap"])
```

### 8.3 Реалтайм мониторинг через Filtered Stream

Для мгновенной реакции — используйте Filtered Stream (раздел 5) с правилами на упоминания и ключевые слова.

---

## 9. Likes, Retweets, Replies

### 9.1 Лайк

```python
# POST /2/users/:id/likes
client.like(tweet_id)

# DELETE /2/users/:id/likes/:tweet_id
client.unlike(tweet_id)
```

### 9.2 Ретвит

```python
# POST /2/users/:id/retweets
client.retweet(tweet_id)

# DELETE /2/users/:id/retweets/:source_tweet_id
client.unretweet(tweet_id)
```

### 9.3 Ответ на пост

```python
# POST /2/tweets с in_reply_to_tweet_id
client.create_tweet(
    text="@user Спасибо за интерес! Напишите в DM для бронирования.",
    in_reply_to_tweet_id=tweet_id
)
```

### 9.4 Автоматизация реакций

```python
def auto_engage(tweet):
    """Авто-лайк и ответ на посты с высоким потенциалом"""
    metrics = tweet.public_metrics
    # Лайк постов с >10 лайками (потенциально вирусный)
    if metrics["like_count"] > 10:
        client.like(tweet.id)
    # Ответ на вопросы
    if "?" in tweet.text and any(kw in tweet.text.lower()
        for kw in ["dubai", "uae", "дубай", "оаэ"]):
        client.create_tweet(
            text=f"@{tweet.author_id} We offer the best Dubai tours! DM for details.",
            in_reply_to_tweet_id=tweet.id
        )
```

**Осторожно:** агрессивная автоматизация реакций может привести к бану аккаунта. Соблюдайте лимиты и правила X Automation Rules.

---

## 10. Webhooks — Account Activity API

### 10.1 Обзор

Account Activity API (AAAPI) отправляет события (DM, упоминания, подписки) на ваш webhook в реальном времени. Доступен на **Enterprise** уровне.

### 10.2 CRC (Challenge-Response Check)

X периодически отправляет CRC-запрос для проверки вашего webhook:

```python
import hmac
import hashlib
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"

@app.route("/webhook", methods=["GET"])
def crc_check():
    crc_token = request.args.get("crc_token")
    sha256_hash = hmac.new(
        CONSUMER_SECRET.encode(),
        crc_token.encode(),
        hashlib.sha256
    ).digest()
    response_token = base64.b64encode(sha256_hash).decode()
    return jsonify({"response_token": f"sha256={response_token}"})

@app.route("/webhook", methods=["POST"])
def receive_event():
    # Верификация подписи
    signature = request.headers.get("x-twitter-webhooks-signature")
    body = request.get_data()
    expected = "sha256=" + base64.b64encode(
        hmac.new(CONSUMER_SECRET.encode(), body, hashlib.sha256).digest()
    ).decode()

    if not hmac.compare_digest(signature, expected):
        return "Invalid signature", 403

    event = request.json
    # Обработка событий
    if "direct_message_events" in event:
        handle_dm(event["direct_message_events"])
    if "tweet_create_events" in event:
        handle_mention(event["tweet_create_events"])
    return "", 200
```

### 10.3 Регистрация webhook

```bash
# Регистрация URL
curl -X POST "https://api.x.com/1.1/account_activity/all/prod/webhooks.json?url=https://your-domain.com/webhook" \
  -H "Authorization: OAuth ..."

# Подписка на события
curl -X POST "https://api.x.com/1.1/account_activity/all/prod/subscriptions.json" \
  -H "Authorization: OAuth ..."
```

### 10.4 Альтернатива без Enterprise

Для Basic/Pro тарифов используйте **polling** вместо webhooks:

```python
def polling_loop(interval=30):
    """Polling: проверка новых событий каждые N секунд"""
    while True:
        check_mentions()
        check_dm_events()
        check_new_followers()
        time.sleep(interval)
```

---

## 11. Состояния диалога (FSM для DM-ботов)

### 11.1 Finite State Machine

```python
from enum import Enum

class State(Enum):
    START = "start"
    CHOOSING_SERVICE = "choosing_service"
    CHOOSING_DATE = "choosing_date"
    CHOOSING_PEOPLE = "choosing_people"
    CONFIRMATION = "confirmation"

class DialogFSM:
    def __init__(self):
        self.sessions = {}  # {user_id: {"state": State, "data": {}}}

    def handle(self, user_id, text):
        session = self.sessions.get(user_id, {"state": State.START, "data": {}})
        state = session["state"]

        if state == State.START:
            return self.on_start(user_id, session)
        elif state == State.CHOOSING_SERVICE:
            return self.on_choose_service(user_id, text, session)
        elif state == State.CHOOSING_DATE:
            return self.on_choose_date(user_id, text, session)
        elif state == State.CHOOSING_PEOPLE:
            return self.on_choose_people(user_id, text, session)
        elif state == State.CONFIRMATION:
            return self.on_confirm(user_id, text, session)

    def on_start(self, user_id, session):
        session["state"] = State.CHOOSING_SERVICE
        self.sessions[user_id] = session
        return ("Добро пожаловать! Выберите услугу:\n"
                "1 - Экскурсии\n2 - Трансфер\n3 - Яхта\n4 - Аренда авто")

    def on_choose_service(self, user_id, text, session):
        services = {"1": "excursion", "2": "transfer", "3": "yacht", "4": "car"}
        if text in services:
            session["data"]["service"] = services[text]
            session["state"] = State.CHOOSING_DATE
            self.sessions[user_id] = session
            return "Укажите дату (ДД.ММ.ГГГГ):"
        return "Выберите 1, 2, 3 или 4:"

    def on_choose_date(self, user_id, text, session):
        session["data"]["date"] = text
        session["state"] = State.CHOOSING_PEOPLE
        self.sessions[user_id] = session
        return "Сколько человек?"

    def on_choose_people(self, user_id, text, session):
        session["data"]["people"] = text
        session["state"] = State.CONFIRMATION
        self.sessions[user_id] = session
        d = session["data"]
        return (f"Подтвердите заказ:\n"
                f"Услуга: {d['service']}\n"
                f"Дата: {d['date']}\n"
                f"Человек: {d['people']}\n"
                f"Ответьте 'да' для подтверждения")

    def on_confirm(self, user_id, text, session):
        if text.lower() in ("да", "yes", "ок"):
            order = session["data"]
            self.sessions.pop(user_id, None)
            # Сохранить заказ в БД, уведомить оператора
            return "Заказ принят! Менеджер свяжется с вами в течение 15 минут."
        self.sessions.pop(user_id, None)
        return "Заказ отменён. Напишите снова для нового заказа."
```

---

## 12. Rate Limits

### 12.1 Таблица лимитов по endpoint

| Endpoint | Free | Basic | Pro |
|----------|------|-------|-----|
| POST /2/tweets | 17/24ч на юзера | 100/24ч на юзера | 100/24ч на юзера |
| DELETE /2/tweets | 50/15мин | 50/15мин | 50/15мин |
| GET /2/tweets/search/recent | Нет | 60/15мин | 300/15мин |
| GET /2/tweets/search/all | Нет | Нет | 1/1сек |
| GET /2/users/me | 25/24ч | 75/15мин | 75/15мин |
| GET /2/users/:id/mentions | Нет | 180/15мин | 180/15мин |
| POST /2/users/:id/likes | 5/24ч | 1000/24ч | 1000/24ч |
| POST /2/users/:id/retweets | Нет | 5/15мин | 5/15мин |
| Filtered Stream connect | Нет | 1 подключение | 1 подключение |
| DM events | Нет | 15/15мин | 15/15мин |

### 12.2 Monthly Post Cap (квота чтения)

| Tier | Месячная квота |
|------|---------------|
| Free | 0 постов |
| Basic | 10,000 постов |
| Pro | 1,000,000 постов |

Квота расходуется при: recent search, filtered stream, user timelines, mention timelines.

### 12.3 Обработка 429 (Too Many Requests)

```python
import time

def api_call_with_retry(func, *args, max_retries=5, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except tweepy.TooManyRequests as e:
            reset_time = int(e.response.headers.get("x-rate-limit-reset", 0))
            wait = max(reset_time - time.time(), 15 * (attempt + 1))
            print(f"Rate limited. Waiting {wait:.0f}s...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### 12.4 Заголовки Rate Limit

Каждый ответ API содержит заголовки:

| Заголовок | Описание |
|-----------|----------|
| `x-rate-limit-limit` | Максимум запросов в окне |
| `x-rate-limit-remaining` | Осталось запросов |
| `x-rate-limit-reset` | Unix timestamp сброса окна |

---

## 13. Примеры для туризма ОАЭ

### 13.1 Бот автопостинга акций

```python
import tweepy
import schedule
from datetime import datetime

class TourismPostBot:
    def __init__(self, client):
        self.client = client
        self.offers = [
            {"text": "Desert Safari — всего 150 AED! Джип, BBQ-ужин, шоу. Бронь в DM!",
             "tags": "#Dubai #DesertSafari #UAE #Travel"},
            {"text": "Burj Khalifa At The Top — 170 AED вместо 224! Пишите в DM.",
             "tags": "#BurjKhalifa #Dubai #Экскурсии"},
            {"text": "Яхта на 2 часа от 500 AED. 300+ яхт на выбор!",
             "tags": "#DubaiYacht #Luxury #UAE"},
        ]

    def post_offer(self):
        offer = self.offers[datetime.now().day % len(self.offers)]
        text = f"{offer['text']}\n\n{offer['tags']}"
        self.client.create_tweet(text=text)

# Посты в 9:00 и 18:00 (прайм-тайм для СНГ аудитории)
schedule.every().day.at("09:00").do(bot.post_offer)
schedule.every().day.at("18:00").do(bot.post_offer)
```

### 13.2 Мониторинг #Dubai

```python
class DubaiMonitor(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        text = tweet.text.lower()
        tourism_keywords = ["tour", "excursion", "safari", "yacht",
                          "экскурсия", "тур", "яхта", "сафари"]
        if any(kw in text for kw in tourism_keywords):
            self.log_lead(tweet)
            if "?" in tweet.text:  # Вопрос = горячий лид
                self.notify_manager(tweet)

# Правила стрима
rules = [
    tweepy.StreamRule("(#Dubai OR #Дубай) (tour OR excursion OR safari OR yacht) -is:retweet"),
    tweepy.StreamRule("(looking for OR ищу) (Dubai OR Дубай) (tour OR guide OR экскурсию)"),
]
```

### 13.3 DM-бот FAQ

Реализация FSM-бота из раздела 11 с данными по турам:

```python
TOUR_CATALOG = {
    "safari": {"name": "Desert Safari", "price": "150 AED", "duration": "6 часов"},
    "burj": {"name": "Burj Khalifa", "price": "от 170 AED", "duration": "1.5 часа"},
    "marina": {"name": "Dubai Marina Cruise", "price": "от 120 AED", "duration": "2 часа"},
    "abudhabi": {"name": "Abu Dhabi City Tour", "price": "от 200 AED", "duration": "10 часов"},
    "aqua": {"name": "Aquaventure Waterpark", "price": "от 280 AED", "duration": "целый день"},
}
```

---

## 14. Деплой

### 14.1 Python (сервер)

```
requirements.txt:
tweepy>=4.14
requests>=2.31
schedule>=1.2
flask>=3.0       # Для webhooks
python-dotenv>=1.0
```

```bash
# Переменные окружения (.env)
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_secret
X_BEARER_TOKEN=your_bearer_token
```

```python
# bot.py
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

client = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)
```

### 14.2 Node.js

```javascript
// bot.js
const { TwitterApi } = require('twitter-api-v2');

const client = new TwitterApi({
    appKey: process.env.X_API_KEY,
    appSecret: process.env.X_API_SECRET,
    accessToken: process.env.X_ACCESS_TOKEN,
    accessSecret: process.env.X_ACCESS_SECRET,
});

// Публикация поста
await client.v2.tweet('Hello from Node.js bot!');

// Поиск
const { data } = await client.v2.search('#Dubai tourism', {
    max_results: 10,
    'tweet.fields': 'created_at,public_metrics',
});

// Filtered Stream
const stream = await client.v2.searchStream({
    'tweet.fields': 'created_at,author_id',
});
stream.on('data', (tweet) => console.log(tweet));
stream.on('error', (err) => console.error(err));
```

### 14.3 Serverless (AWS Lambda / Google Cloud Functions)

Идеально для планировщика постов — не нужен постоянно работающий сервер:

```python
# lambda_function.py
def lambda_handler(event, context):
    """AWS Lambda: вызывается по расписанию через EventBridge"""
    client = get_twitter_client()
    offer = get_daily_offer()
    client.create_tweet(text=offer)
    return {"statusCode": 200}
```

**Триггер:** AWS EventBridge (cron) или Google Cloud Scheduler.

**Ограничение:** Serverless не подходит для Filtered Stream (требует постоянное соединение). Для стриминга используйте VPS или контейнер.

### 14.4 Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

```bash
docker build -t x-bot .
docker run -d --env-file .env --name x-bot x-bot
```

---

## 15. Библиотеки

### 15.1 Python

| Библиотека | Тип | Описание |
|-----------|-----|----------|
| **tweepy** (4.14+) | Официальная обёртка | Полная поддержка v2 + v1.1, OAuth 2.0 PKCE, Stream |
| **python-twitter-v2** | Официальная обёртка | Альтернатива tweepy, типизация, async |
| **twikit** | Неофициальная | Без API ключей, через внутренний API X. Бесплатно, но нестабильно |
| **requests** | HTTP | Прямые запросы к API для кастомных решений |

### 15.2 Node.js

| Библиотека | Описание |
|-----------|----------|
| **twitter-api-v2** (npm) | Полная обёртка v2 + v1.1, TypeScript, streaming |
| **twit** | Устаревшая (v1.1 only), не рекомендуется |

### 15.3 Другие языки

| Язык | Библиотека |
|------|-----------|
| Go | **go-twitter** |
| Ruby | **twitter** gem |
| PHP | **abraham/twitteroauth** |
| Java | **twitter4j** |

### 15.4 О twikit (неофициальная)

```python
# Установка
pip install twikit

# Использование (без API ключей!)
from twikit import Client
client = Client('en-US')
await client.login(
    auth_info_1='your_username',
    auth_info_2='your_email',
    password='your_password'
)

# Поиск
tweets = await client.search_tweet('#Dubai', 'Latest')
# Публикация
await client.create_tweet('Hello world!')
```

**Преимущества:** бесплатно, не нужны API ключи, нет лимитов тарифа.
**Риски:** использует внутренний API X, может сломаться при обновлении. Нарушает ToS — аккаунт может быть заблокирован. Только для исследований и прототипов.

---

## Таблица ресурсов

| Ресурс | URL | Описание |
|--------|-----|----------|
| X Developer Portal | developer.x.com | Создание App, ключи, дашборд |
| API v2 Документация | docs.x.com/x-api | Полная документация endpoints |
| Tweepy Docs | docs.tweepy.org | Python-библиотека |
| twitter-api-v2 (npm) | github.com/PLhery/node-twitter-api-v2 | Node.js-библиотека |
| twikit | github.com/d60/twikit | Неофициальная Python-библиотека |
| OAuth 2.0 PKCE Guide | developer.x.com/en/docs/authentication/oauth-2-0 | Гайд по аутентификации |
| Filtered Stream Rules | docs.x.com/x-api/posts/filtered-stream/integrate/build-a-rule | Построение правил |
| Rate Limits | docs.x.com/x-api/fundamentals/rate-limits | Лимиты по endpoints |
| X Automation Rules | help.x.com/en/rules-and-policies/x-automation | Правила автоматизации |
| Account Activity API | developer.x.com/en/docs/twitter-api/enterprise/account-activity-api | Webhooks (Enterprise) |
| Postman Collection | developer.x.com/en/docs/tools-and-libraries | Готовые запросы для тестирования |
| X API Changelog | devcommunity.x.com/c/announcements | Анонсы изменений API |
