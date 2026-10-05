---
name: bot-builder-workflow
description: "Use when building a new bot from scratch, setting up bot architecture, choosing a bot framework, structuring handlers/commands/FSM state machines, or deciding between webhooks and polling for Telegram, WhatsApp, or Slack bots"
---
# Bot Builder Workflow

## Overview

Structured workflow for building production-ready bots across Telegram, WhatsApp (Meta Cloud API), and Slack. This skill covers architecture decisions, project structure, handler patterns, FSM for multi-step dialogs, deployment checklist, and minimal working templates for each platform. It is about HOW TO BUILD, not an API reference.

---

## When to Use

Use this skill when:
- Starting a new bot project from zero
- Choosing a framework or architecture approach
- Structuring handlers, commands, callbacks, or FSM
- Deciding between webhooks and long-polling
- Setting up middleware, error handling, rate limiting
- Preparing a bot for production deployment

Do NOT use this skill for:
- Looking up specific API endpoints or payload fields → use platform-specific справочники (telegram-bot-справочник, whatsapp-bot-справочник, etc.)
- Debugging a running bot → use error-handling-patterns skill
- CI/CD pipeline details → use cicd-pipeline skill

---

## Universal Bot Architecture

Every production bot, regardless of platform, shares the same logical layers:

```
Entry Point (polling loop OR webhook endpoint)
    ↓
Middleware layer (auth check, rate limit, logging, i18n)
    ↓
Router / Dispatcher (match incoming event to handler)
    ↓
Handler (business logic)
    ↓
FSM State Machine (if multi-step dialog)
    ↓
Service layer (DB, external APIs, notifications)
    ↓
Response formatter → Platform API
```

### Project Structure (universal)

```
my-bot/
├── bot/
│   ├── main.py            # entry point
│   ├── config.py          # env vars, settings
│   ├── handlers/          # one file per feature area
│   │   ├── start.py
│   │   ├── catalog.py
│   │   ├── booking.py
│   │   └── admin.py
│   ├── fsm/               # state definitions
│   │   └── states.py
│   ├── services/          # business logic, DB calls
│   │   ├── database.py
│   │   └── notifications.py
│   ├── middlewares.py     # throttle, auth, logging
│   └── keyboards.py       # reusable UI components
├── tests/
├── .env
├── requirements.txt
└── Dockerfile
```

### Webhooks vs Long-Polling

| Mode | When to use | Pros | Cons |
|------|-------------|------|------|
| Long-polling | Development, small bots, no public URL | Zero infra setup | Higher latency, not production-ideal |
| Webhooks | Production, high traffic, microservices | Low latency, event-driven | Needs HTTPS + public URL |

**Rule of thumb:** Start with polling locally, switch to webhooks before production.

### Config Pattern (all platforms)

```python
# config.py — load all secrets from environment, never hardcode
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x]
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
DEBUG = os.getenv("DEBUG", "0") == "1"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
```

---

## Platform Guides

### Telegram

**Recommended frameworks:**
- Python: **aiogram 3.x** (async, type-safe, best FSM) — production choice
- Python alternative: python-telegram-bot 21+ (sync/async, beginner-friendly)
- Node.js: grammY (modern, plugin ecosystem)

**Core concepts:**
- `Update` = any incoming event (message, callback_query, inline_query, etc.)
- `Router` = group of handlers, composable like blueprints
- `FSMContext` = per-user state storage for multi-step dialogs
- `InlineKeyboard` = buttons attached to a message
- `ReplyKeyboard` = persistent bottom keyboard

**Minimal production-ready bot (aiogram 3.x):**

```python
# bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.handlers import start, catalog, booking
from bot.middlewares import ThrottleMiddleware

logging.basicConfig(level=logging.INFO, format="[%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware (order matters: outer → inner)
    dp.message.middleware(ThrottleMiddleware(rate_limit=1.0))

    # Routers
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(booking.router)

    logger.info("Bot starting...")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
```

```python
# bot/handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>!\n\n"
        "Use /catalog to browse or /help for commands."
    )
```

```python
# bot/handlers/booking.py — FSM multi-step dialog
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

router = Router()


class BookingFSM(StatesGroup):
    waiting_name = State()
    waiting_date = State()
    waiting_guests = State()
    confirm = State()


@router.callback_query(F.data.startswith("book:"))
async def start_booking(callback: CallbackQuery, state: FSMContext):
    block_id = callback.data.split(":")[1]
    await state.update_data(block_id=block_id)
    await state.set_state(BookingFSM.waiting_name)
    await callback.message.answer("Enter your full name:")
    await callback.answer()


@router.message(BookingFSM.waiting_name)
async def got_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookingFSM.waiting_date)
    await message.answer("Enter date (DD.MM.YYYY):")


@router.message(BookingFSM.waiting_date)
async def got_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(BookingFSM.waiting_guests)
    await message.answer("Number of guests:")


@router.message(BookingFSM.waiting_guests)
async def got_guests(message: Message, state: FSMContext):
    data = await state.update_data(guests=message.text)
    await state.set_state(BookingFSM.confirm)
    await message.answer(
        f"Confirm booking:\n"
        f"Name: {data['name']}\n"
        f"Date: {data['date']}\n"
        f"Guests: {data['guests']}\n\n"
        "Reply 'yes' to confirm or 'no' to cancel."
    )


@router.message(BookingFSM.confirm, F.text.lower() == "yes")
async def confirmed(message: Message, state: FSMContext):
    data = await state.get_data()
    # await db.create_booking(data)
    await state.clear()
    await message.answer("Booking confirmed! We will contact you shortly.")


@router.message(BookingFSM.confirm, F.text.lower() == "no")
async def cancelled(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Booking cancelled.")
```

```python
# bot/middlewares.py — throttle middleware
import time
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self._last_call: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
            now = time.monotonic()
            last = self._last_call.get(uid, 0)
            if now - last < self.rate_limit:
                await event.answer("Too fast! Please slow down.")
                return
            self._last_call[uid] = now
        return await handler(event, data)
```

**Webhook setup (production):**

```python
# bot/main_webhook.py
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

WEBHOOK_PATH = "/webhook/telegram"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def on_startup(bot):
    await bot.set_webhook(WEBHOOK_URL)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)
app.on_startup.append(on_startup)
web.run_app(app, host="0.0.0.0", port=8080)
```

---

### WhatsApp (Meta Cloud API)

**Approach:** No official Python bot framework. Use FastAPI + httpx to handle webhooks and call the Graph API directly. Do NOT use unofficial libraries (they violate ToS and break on API updates).

**Core concepts:**
- Webhooks only (no long-polling)
- Every incoming message must be acknowledged with `200 OK` immediately
- Messages: text, interactive (buttons/lists), template, media
- `mark_as_read` should be called for each incoming message
- 24-hour customer-initiated window; outside it: use approved templates
- Phone number ID is NOT the phone number — it's an account identifier

**Minimal production-ready bot:**

```python
# whatsapp_bot/app.py
import hashlib, hmac, json, os
from fastapi import FastAPI, Request, Response
from whatsapp_bot.handlers import common, catalog, booking

app = FastAPI()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
APP_SECRET = os.getenv("META_APP_SECRET", "")


@app.get("/webhook")
async def verify(request: Request):
    """Meta webhook verification handshake."""
    params = dict(request.query_params)
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return Response(content=params["hub.challenge"])
    return Response(status_code=403)


@app.post("/webhook")
async def receive(request: Request):
    """Receive and route WhatsApp messages."""
    # Verify HMAC signature
    body_bytes = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), body_bytes, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return Response(status_code=403)

    payload = json.loads(body_bytes)
    await route_message(payload)
    return Response(status_code=200)  # ALWAYS return 200 immediately


async def route_message(payload: dict):
    try:
        entry = payload["entry"][0]
        changes = entry["changes"][0]["value"]

        # Statuses (read receipts, delivery) — ignore or log
        if "statuses" in changes:
            return

        messages = changes.get("messages", [])
        for msg in messages:
            wa_id = msg["from"]
            msg_type = msg["type"]

            if msg_type == "text":
                text = msg["text"]["body"]
                await common.handle_text(wa_id, text, msg["id"])
            elif msg_type == "interactive":
                itype = msg["interactive"]["type"]
                if itype == "button_reply":
                    bid = msg["interactive"]["button_reply"]["id"]
                    await common.handle_button(wa_id, bid, msg["id"])
                elif itype == "list_reply":
                    lid = msg["interactive"]["list_reply"]["id"]
                    await common.handle_list(wa_id, lid, msg["id"])
    except Exception as e:
        import logging
        logging.getLogger("whatsapp").error(f"route_message error: {e}", exc_info=True)
```

```python
# whatsapp_bot/api.py — thin wrapper for Graph API calls
import httpx, os, logging

BASE_URL = "https://graph.facebook.com/v19.0"
PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
logger = logging.getLogger("whatsapp.api")


async def send_text(to: str, text: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text, "preview_url": False},
    }
    return await _post(f"{BASE_URL}/{PHONE_ID}/messages", payload)


async def send_buttons(to: str, body: str, buttons: list[dict]):
    """buttons: [{"id": "btn_1", "title": "Option 1"}, ...]  max 3"""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons[:3]
                ]
            },
        },
    }
    return await _post(f"{BASE_URL}/{PHONE_ID}/messages", payload)


async def send_list(to: str, body: str, button_label: str, sections: list[dict]):
    """sections: [{"title": "...", "rows": [{"id": "...", "title": "...", "description": "..."}]}]"""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {"button": button_label, "sections": sections},
        },
    }
    return await _post(f"{BASE_URL}/{PHONE_ID}/messages", payload)


async def mark_as_read(msg_id: str):
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": msg_id,
    }
    await _post(f"{BASE_URL}/{PHONE_ID}/messages", payload)


async def _post(url: str, payload: dict) -> dict:
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json=payload, headers=headers)
        if r.status_code != 200:
            logger.error(f"API error {r.status_code}: {r.text}")
        return r.json()
```

```python
# whatsapp_bot/fsm.py — simple in-memory FSM (replace with Redis for multi-instance)
import asyncio, time
from enum import Enum


class WAState(str, Enum):
    IDLE = "idle"
    BOOKING_NAME = "booking_name"
    BOOKING_DATE = "booking_date"
    BOOKING_GUESTS = "booking_guests"
    BOOKING_CONFIRM = "booking_confirm"


class FSMManager:
    def __init__(self, timeout: int = 3600):
        self._states: dict[str, dict] = {}
        self._timeout = timeout

    def get(self, wa_id: str) -> tuple[WAState, dict]:
        entry = self._states.get(wa_id)
        if not entry or time.time() - entry["ts"] > self._timeout:
            return WAState.IDLE, {}
        return WAState(entry["state"]), entry["data"]

    def set(self, wa_id: str, state: WAState, data: dict = None):
        self._states[wa_id] = {
            "state": state.value,
            "data": data or {},
            "ts": time.time(),
        }

    def clear(self, wa_id: str):
        self._states.pop(wa_id, None)


fsm = FSMManager()
```

---

### Slack

**Recommended framework:** **Slack Bolt for Python** (official, handles OAuth, Socket Mode, events)

**Core concepts:**
- Slack apps use **Socket Mode** (development/no-public-URL) or **HTTP webhooks** (production)
- Events API: receive events when users post messages, reactions, etc.
- Slash commands: `/mycommand args`
- Block Kit: rich interactive UI (buttons, select menus, modals, input blocks)
- Modals: multi-step form dialogs tied to a `trigger_id`
- Actions: button clicks, select changes — respond within 3 seconds or use `ack()` immediately

**Minimal production-ready bot:**

```python
# slack_bot/app.py
import os, logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_bot.handlers import commands, actions, events

logging.basicConfig(level=logging.INFO)

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Register handlers
commands.register(app)
actions.register(app)
events.register(app)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
```

```python
# slack_bot/handlers/commands.py
from slack_bolt import App


def register(app: App):

    @app.command("/catalog")
    def catalog_command(ack, body, client):
        ack()  # ALWAYS ack within 3 seconds
        user_id = body["user_id"]
        client.chat_postMessage(
            channel=body["channel_id"],
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Dubai Tours Catalog*\nChoose a category:"},
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {"type": "plain_text", "text": "Select category"},
                        "action_id": "select_category",
                        "options": [
                            {"text": {"type": "plain_text", "text": "Excursions"}, "value": "excursions"},
                            {"text": {"type": "plain_text", "text": "Desert Safari"}, "value": "safari"},
                            {"text": {"type": "plain_text", "text": "Theme Parks"}, "value": "parks"},
                        ],
                    },
                }
            ],
        )

    @app.command("/book")
    def book_command(ack, body, client, logger):
        ack()
        trigger_id = body["trigger_id"]
        # Open a modal for booking form
        client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "booking_modal",
                "title": {"type": "plain_text", "text": "Book a Tour"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "name_block",
                        "label": {"type": "plain_text", "text": "Full Name"},
                        "element": {"type": "plain_text_input", "action_id": "name_input"},
                    },
                    {
                        "type": "input",
                        "block_id": "date_block",
                        "label": {"type": "plain_text", "text": "Tour Date"},
                        "element": {
                            "type": "datepicker",
                            "action_id": "date_input",
                            "placeholder": {"type": "plain_text", "text": "Select date"},
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "guests_block",
                        "label": {"type": "plain_text", "text": "Number of Guests"},
                        "element": {
                            "type": "number_input",
                            "is_decimal_allowed": False,
                            "action_id": "guests_input",
                            "min_value": "1",
                            "max_value": "20",
                        },
                    },
                ],
            },
        )
```

```python
# slack_bot/handlers/actions.py
from slack_bolt import App


def register(app: App):

    @app.action("select_category")
    def handle_category(ack, body, client):
        ack()
        selected = body["actions"][0]["selected_option"]["value"]
        channel = body["channel"]["id"]
        client.chat_postMessage(
            channel=channel,
            text=f"You selected: *{selected}*. Here are the available tours..."
        )

    @app.view("booking_modal")
    def handle_booking_submit(ack, body, view, client, logger):
        ack()
        values = view["state"]["values"]
        name = values["name_block"]["name_input"]["value"]
        date = values["date_block"]["date_input"]["selected_date"]
        guests = values["guests_block"]["guests_input"]["value"]
        user_id = body["user"]["id"]

        logger.info(f"[booking] user={user_id} name={name} date={date} guests={guests}")

        # Save to DB, send confirmation
        client.chat_postMessage(
            channel=user_id,  # DM to user
            text=f"Booking received! Name: {name}, Date: {date}, Guests: {guests}. We'll confirm shortly."
        )
```

```python
# slack_bot/handlers/events.py
from slack_bolt import App


def register(app: App):

    @app.event("message")
    def handle_message(event, say, logger):
        # Ignore bot messages to avoid loops
        if event.get("bot_id"):
            return
        text = event.get("text", "").lower()
        if "hello" in text or "hi" in text:
            say(f"Hello <@{event['user']}>! Use /catalog to browse tours.")

    @app.event("app_mention")
    def handle_mention(event, say):
        say(f"Hi <@{event['user']}>! Type /catalog to get started.")
```

**HTTP mode (production, no Socket Mode):**

```python
# slack_bot/app_http.py
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)
```

---

## Common Patterns (Cross-Platform)

### FSM for Multi-Step Dialogs

Every platform needs a state machine for forms. Key rules:
1. State is per-user (keyed by user ID)
2. Always have a timeout (default: 1 hour) to auto-clear stale sessions
3. Always handle "cancel" at every step
4. Persist state to Redis (or DB) for multi-instance deployments

```python
# Universal FSM pattern (adapt for each platform)
class UniversalFSM:
    def __init__(self, storage: dict = None, timeout: int = 3600):
        self._data = storage if storage is not None else {}
        self.timeout = timeout

    def get_state(self, user_id: str) -> str | None:
        entry = self._data.get(user_id)
        if not entry:
            return None
        if time.time() - entry["ts"] > self.timeout:
            del self._data[user_id]
            return None
        return entry["state"]

    def set_state(self, user_id: str, state: str, **kwargs):
        existing_data = self._data.get(user_id, {}).get("context", {})
        existing_data.update(kwargs)
        self._data[user_id] = {"state": state, "context": existing_data, "ts": time.time()}

    def get_context(self, user_id: str) -> dict:
        return self._data.get(user_id, {}).get("context", {})

    def clear(self, user_id: str):
        self._data.pop(user_id, None)
```

### Error Handling

```python
# Wrap all handlers with structured error handling
import logging
import functools

logger = logging.getLogger(__name__)


def safe_handler(platform: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[{platform}] handler={func.__name__} error={e}", exc_info=True)
                # Optionally notify user
        return wrapper
    return decorator


# Usage
@safe_handler("telegram")
async def my_handler(message):
    ...
```

### Rate Limiting

```python
# Simple token bucket per user
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_calls: int = 5, window: float = 10.0):
        self.max_calls = max_calls
        self.window = window
        self._calls: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = time.monotonic()
        calls = self._calls[user_id]
        # Remove old calls outside window
        self._calls[user_id] = [t for t in calls if now - t < self.window]
        if len(self._calls[user_id]) >= self.max_calls:
            return False
        self._calls[user_id].append(now)
        return True
```

### Structured Logging

Always log at these points:
1. Incoming event (what arrived, from whom)
2. State transition (FSM: old state → new state)
3. External API call (service, method, params)
4. Result or error (what went out, or what failed)

```python
# Standard log format used throughout this project
logger.info(f"[telegram] incoming: user={user_id} text='{text[:50]}'")
logger.info(f"[booking] fsm: user={user_id} {old_state} -> {new_state}")
logger.info(f"[db] create_booking: user={user_id} block_id={block_id}")
logger.error(f"[whatsapp] send_text failed: to={to} error={e}")
```

### Database Async Pattern

Use `asyncpg` for PostgreSQL; avoid blocking calls in async handlers:

```python
# services/database.py
import asyncpg
import os


class BotDB:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def init(self):
        self._pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"), min_size=2, max_size=10)

    async def close(self):
        if self._pool:
            await self._pool.close()

    async def get_user(self, user_id: int) -> dict | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            return dict(row) if row else None

    async def upsert_user(self, user_id: int, name: str, platform: str):
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, name, platform, created_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id) DO UPDATE SET name = $2, last_active = NOW()
                """,
                user_id, name, platform,
            )
```

---

## Deployment Checklist

### Pre-deploy

- [ ] All secrets in `.env`, never hardcoded, `.env` in `.gitignore`
- [ ] Webhook URL is HTTPS with valid SSL certificate
- [ ] Bot token registered and webhook set (or polling started)
- [ ] Database migrations applied
- [ ] Rate limiting enabled
- [ ] HMAC signature verification enabled (WhatsApp/Facebook/Viber)
- [ ] Error logging to persistent sink (file, cloud logs)
- [ ] Graceful shutdown handler (clear webhook, close DB pool)

### Webhook Registration

```bash
# Telegram — set webhook
curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook" \
  -d "url=https://yourdomain.com/webhook/telegram"

# Verify
curl "https://api.telegram.org/bot{TOKEN}/getWebhookInfo"

# WhatsApp — registered in Meta Developer Portal manually
# Slack — set Request URL in App settings > Event Subscriptions
```

### Process Manager (production)

```ini
# supervisor config for production
[program:telegram-bot]
command=python -m bot.main
directory=/opt/my-bot
autostart=true
autorestart=true
stderr_logfile=/var/log/telegram-bot.err.log
stdout_logfile=/var/log/telegram-bot.out.log
```

```yaml
# docker-compose.yml (production pattern)
services:
  bot:
    build: .
    restart: unless-stopped
    env_file: .env.prod
    depends_on:
      - postgres
    command: python -m bot.main

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: botdb
      POSTGRES_USER: botuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}

volumes:
  pgdata:
```

### Required ENV vars per platform

| Variable | Telegram | WhatsApp | Slack |
|----------|----------|----------|-------|
| Bot token | `BOT_TOKEN` | `WHATSAPP_ACCESS_TOKEN` | `SLACK_BOT_TOKEN` |
| App secret | — | `META_APP_SECRET` | `SLACK_SIGNING_SECRET` |
| Verify token | — | `WHATSAPP_VERIFY_TOKEN` | — |
| App token (Socket) | — | — | `SLACK_APP_TOKEN` |
| Phone/Page ID | — | `WHATSAPP_PHONE_NUMBER_ID` | — |
| Webhook host | `WEBHOOK_HOST` | hosted externally | — |

---

## Quick Reference

| Platform | Framework (Python) | Entry mode | Key UI element | Rate limit |
|----------|--------------------|------------|----------------|------------|
| Telegram | aiogram 3.x | polling or webhook | InlineKeyboard | 30 msg/sec total |
| WhatsApp | FastAPI + httpx | webhook only | Interactive (buttons/list) | 80 msg/sec per WABA |
| Slack | slack-bolt | Socket Mode or HTTP | Block Kit / Modals | Tier 3: 50+/min |

| Task | Telegram | WhatsApp | Slack |
|------|----------|----------|-------|
| Send text | `message.answer(text)` | `send_text(to, text)` | `say(text)` / `client.chat_postMessage` |
| Send buttons | `InlineKeyboardMarkup` | `send_buttons(to, body, btns)` | Block Kit `actions` block |
| Multi-step form | `StatesGroup` + `FSMContext` | `FSMManager` + `state.set()` | `views_open` modal |
| Acknowledge event | automatic | return `200 OK` immediately | `ack()` within 3s |
| Edit message | `message.edit_text(...)` | not supported (resend) | `client.chat_update` |

---

## Common Mistakes

1. **Not acking immediately (WhatsApp/Slack)** — WhatsApp expects `200 OK` before processing; Slack needs `ack()` within 3 seconds. Do this first, then do async work.

2. **Hardcoding secrets** — Never put tokens in source code. Always use `.env` + `os.getenv()`.

3. **No FSM timeout** — Stale sessions accumulate. Always expire state after 1 hour of inactivity.

4. **Blocking calls in async handlers** — `time.sleep()`, synchronous DB calls, or `requests.get()` block the event loop. Use `asyncio.sleep()`, `asyncpg`, `httpx.AsyncClient`.

5. **Bot echo loop** — On Slack, always check `event.get("bot_id")` and skip bot's own messages. On Telegram, messages from bots have `from_user.is_bot = True`.

6. **No HMAC verification (webhooks)** — WhatsApp, Facebook, and Viber all sign requests. Without verification, anyone can send fake events to your webhook.

7. **Sharing one handler for all update types** — In aiogram, `callback_query` and `message` are different update types with different throttle buckets. Handle them separately.

8. **FSM state survives restart** — `MemoryStorage` (aiogram) loses all state on restart. For production with restarts, use `RedisStorage` or persist to DB.

9. **Not clearing FSM on cancel** — If the user hits /start mid-flow, always call `state.clear()` first to reset stale state.

10. **Sending messages outside 24h window (WhatsApp)** — After 24h of inactivity, only approved message templates can be sent. Proactive messages outside the window will fail silently.

---

## Sources

This skill was built from scratch using:
- Anthropic Claude Code built-in expertise (aiogram 3.x, Meta Cloud API v19, Slack Bolt)
- Meta WhatsApp Cloud API documentation patterns (production-tested in VIP-DXB-CatalogBot Phase 19)
- Slack Bolt for Python official patterns
- aiogram 3.x FSM patterns (production-tested in VIP-DXB-CatalogBot Telegram bot, 44 routers)
- Note: TerminalSkills/skills GitHub repository (https://github.com/TerminalSkills/skills) does not contain bot-builder skills — the three target URLs returned 404; this skill was authored independently.

File size: ~9KB
