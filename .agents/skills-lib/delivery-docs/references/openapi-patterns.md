# OpenAPI Patterns Reference

FastAPI + asyncpg OpenAPI conventions для VIP-DXB-CatalogBot.
Webhook servers, Mini App API, drift detection.

---

## Как FastAPI генерирует OpenAPI автоматически

FastAPI автоматически создаёт OpenAPI 3.x spec из кода при запуске.

```bash
# Запустить бот (локально или на сервере)
uvicorn instagram_bot.app:app --host 0.0.0.0 --port 8081

# Получить автоматически сгенерированный spec
curl http://localhost:8081/openapi.json

# Красивый интерактивный UI (Swagger)
open http://localhost:8081/docs

# Альтернативный UI (ReDoc)
open http://localhost:8081/redoc
```

Если бот не запущен — генерируем spec вручную по шаблону ниже.

---

## Документирование Pydantic models (request/response)

FastAPI автоматически включает Pydantic models в OpenAPI spec.

### Базовый webhook payload

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class IncomingMessage(BaseModel):
    """Incoming message from a messaging platform.

    Attributes:
        platform: Source platform identifier.
        sender_id: Platform-native user identifier.
        message_type: Type of message content.
        text: Text content (present when message_type is 'text').
        timestamp: Unix timestamp of the message.
    """
    platform: str = Field(..., description="Source platform: instagram, whatsapp, facebook, viber, max")
    sender_id: str = Field(..., description="Platform-native user identifier (e.g. PSID for FB, IGSID for IG)")
    message_type: str = Field(..., description="Message type: text, postback, quick_reply, attachment")
    text: Optional[str] = Field(None, description="Text content for message_type='text'")
    timestamp: int = Field(..., description="Unix timestamp (milliseconds)")

class WebhookResponse(BaseModel):
    """Standard response for webhook POST requests."""
    status: str = Field("ok", description="Always 'ok' — platform expects 200 immediately")
```

### Response models для Mini App API

```python
class BlockCard(BaseModel):
    """Catalog block (excursion / ticket / attraction)."""
    id: int
    title: str
    description: Optional[str]
    price: float = Field(..., description="Price in AED or USD depending on category")
    currency: str = Field(..., description="AED or USD")
    category: str
    emirate: str
    image_url: Optional[str]
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)

class BookingRequest(BaseModel):
    """POST /api/bookings request body."""
    block_id: int
    user_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., description="International format: +971XXXXXXXXX")
    date: str = Field(..., description="ISO 8601: YYYY-MM-DD")
    adults: int = Field(1, ge=1, le=20)
    children: int = Field(0, ge=0, le=20)
    language: str = Field("ru", description="ISO 639-1: ru, en, ar")
    comment: Optional[str] = Field(None, max_length=500)
```

---

## Patterns для webhook endpoints

### GET — верификация (Meta платформы)

```python
from fastapi import FastAPI, Request, HTTPException, Query

app = FastAPI(
    title="Instagram DM Bot",
    description="VIP-DXB-CatalogBot Instagram webhook receiver",
    version="1.0.0"
)

@app.get(
    "/webhook",
    summary="Webhook verification",
    description="Meta platform calls this endpoint to verify webhook ownership. "
                "Returns hub.challenge if hub.verify_token matches.",
    response_description="Returns hub.challenge integer as plain text",
    tags=["Webhook"]
)
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: int = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    ...
```

### POST — приём сообщений

```python
@app.post(
    "/webhook",
    summary="Receive messages",
    description="Receives incoming messages from Meta platform. "
                "HMAC-SHA256 signature verified via X-Hub-Signature-256 header. "
                "Always returns 200 immediately, processing is async.",
    response_model=WebhookResponse,
    tags=["Webhook"]
)
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str = Header(..., alias="X-Hub-Signature-256")
):
    ...
```

### GET — health check

```python
@app.get(
    "/health",
    summary="Health check",
    description="Returns service status. Used by Docker healthcheck and load balancer.",
    tags=["System"]
)
async def health():
    return {"status": "ok", "platform": "instagram", "version": "1.0.0"}
```

---

## Patterns для Mini App API

```python
@app.get(
    "/api/catalog",
    response_model=List[BlockCard],
    summary="Get catalog blocks",
    description="Returns catalog items filtered by emirate and/or category. "
                "Sorted by popularity (booking count) descending.",
    tags=["Catalog"]
)
async def get_catalog(
    emirate: Optional[str] = Query(None, description="Filter by emirate: dubai, abudhabi, ras-al-khaimah, fujairah"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    lang: str = Query("ru", description="Response language: ru, en, ar"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    ...

@app.post(
    "/api/bookings",
    response_model=BookingConfirmation,
    summary="Create booking",
    description="Creates a new booking and sends Telegram notification to manager. "
                "Requires valid Telegram Mini App initData in Authorization header.",
    tags=["Bookings"]
)
async def create_booking(
    booking: BookingRequest,
    authorization: str = Header(..., description="Telegram Mini App initData for auth verification")
):
    ...
```

---

## Пример полного OpenAPI 3.x spec — Instagram webhook

```yaml
openapi: 3.0.3
info:
  title: Instagram DM Bot — VIP DXB CatalogBot
  version: 1.0.0
  description: |
    Instagram DM webhook receiver for VIP-DXB-CatalogBot.
    Handles incoming messages, provides catalog browsing and booking.

    Security: All POST requests verified via HMAC-SHA256 (X-Hub-Signature-256).
    Platform: Meta Graph API, webhook v18.0+.

servers:
  - url: http://localhost:8081
    description: Local development
  - url: https://your-domain.com
    description: Production (via nginx reverse proxy)

security:
  - HmacSignature: []

paths:
  /webhook:
    get:
      summary: Webhook verification
      operationId: verifyWebhook
      tags: [Webhook]
      security: []
      parameters:
        - name: hub.mode
          in: query
          required: true
          schema:
            type: string
            enum: [subscribe]
        - name: hub.challenge
          in: query
          required: true
          schema:
            type: integer
        - name: hub.verify_token
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Returns hub.challenge as plain text
          content:
            text/plain:
              schema:
                type: integer
              example: 1234567890
        '403':
          description: Invalid verify token

    post:
      summary: Receive incoming messages
      operationId: receiveWebhook
      tags: [Webhook]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InstagramPayload'
            example:
              object: instagram
              entry:
                - id: "17841400008460056"
                  messaging:
                    - sender:
                        id: "7654321"
                      recipient:
                        id: "17841400008460056"
                      timestamp: 1709290000000
                      message:
                        mid: "m_abc123"
                        text: "Привет, что есть в Дубае?"
      responses:
        '200':
          description: Always returns 200 immediately
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WebhookResponse'
        '403':
          description: Invalid HMAC signature

  /health:
    get:
      summary: Health check
      operationId: healthCheck
      tags: [System]
      security: []
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok
                  platform:
                    type: string
                    example: instagram
                  version:
                    type: string
                    example: 1.0.0

components:
  securitySchemes:
    HmacSignature:
      type: apiKey
      in: header
      name: X-Hub-Signature-256
      description: HMAC-SHA256 of request body using META_APP_SECRET

  schemas:
    WebhookResponse:
      type: object
      properties:
        status:
          type: string
          example: ok

    InstagramPayload:
      type: object
      required: [object, entry]
      properties:
        object:
          type: string
          enum: [instagram]
        entry:
          type: array
          items:
            $ref: '#/components/schemas/InstagramEntry'

    InstagramEntry:
      type: object
      properties:
        id:
          type: string
          description: Instagram Business Account ID
        messaging:
          type: array
          items:
            $ref: '#/components/schemas/InstagramMessagingEvent'

    InstagramMessagingEvent:
      type: object
      properties:
        sender:
          type: object
          properties:
            id:
              type: string
              description: Instagram Scoped ID (IGSID) of the sender
        recipient:
          type: object
          properties:
            id:
              type: string
        timestamp:
          type: integer
          description: Unix timestamp in milliseconds
        message:
          type: object
          properties:
            mid:
              type: string
            text:
              type: string
        postback:
          type: object
          properties:
            title:
              type: string
            payload:
              type: string
```

---

## Drift Detection — как сравнить spec с кодом

### Шаг 1: Собрать реальные endpoints из кода

```bash
# Найти все route definitions в FastAPI app
grep -n "@app\.\(get\|post\|put\|delete\|patch\)" instagram_bot/app.py

# Или через router
grep -rn "@router\.\(get\|post\|put\|delete\|patch\)" instagram_bot/

# Список путей из работающего приложения
curl http://localhost:8081/openapi.json | python -c "
import json, sys
spec = json.load(sys.stdin)
for path, methods in spec['paths'].items():
    for method in methods:
        print(f'{method.upper()} {path}')
"
```

### Шаг 2: Собрать endpoints из существующего spec

```bash
# Из YAML
grep "^\s\{2\}/" docs/openapi/instagram_bot.yaml

# Или через python
python -c "
import yaml
with open('docs/openapi/instagram_bot.yaml') as f:
    spec = yaml.safe_load(f)
for path, methods in spec.get('paths', {}).items():
    for method in methods:
        print(f'{method.upper()} {path}')
"
```

### Шаг 3: Сравнить и сообщить

Формат drift report:
```
DRIFT REPORT: instagram_bot
  + Added (in code, not in spec):
    POST /webhook/test  [NEW - нужно добавить в spec]
  - Removed (in spec, not in code):
    GET /debug  [REMOVED - нужно удалить из spec]
  = Unchanged: GET /webhook, POST /webhook, GET /health

ACTION: обновить docs/openapi/instagram_bot.yaml
```

---

## Куда сохранять spec файлы

```
docs/
└── openapi/
    ├── instagram_bot.yaml
    ├── whatsapp_bot.yaml
    ├── facebook_bot.yaml
    ├── viber_bot.yaml
    ├── max_bot.yaml          ← Phase 22
    └── miniapp.yaml
```

---

## Специфика для VIP-DXB-CatalogBot

| Аспект | Конвенция |
|--------|-----------|
| Версии API | Без `/v1/` prefix — боты stateless, версионирование через CHANGELOG |
| Auth для webhooks | HMAC-SHA256 через header (X-Hub-Signature-256 или X-Viber-Content-Signature) |
| Auth для Mini App | Telegram initData в Authorization header |
| Успешный ответ webhook | Всегда HTTP 200 + `{"status": "ok"}` немедленно |
| Обработка | Асинхронная, после ответа 200 |
| Порты | IG:8081 WA:8082 FB:8083 VB:8084 MAX:8085 MiniApp:8080 |
| Формат дат | ISO 8601: `YYYY-MM-DD` |
| Формат цен | float, отдельное поле currency: "AED" или "USD" |

---

## Sources

- OpenAPI 3.0.3 spec: https://swagger.io/specification/
- FastAPI docs: https://fastapi.tiangolo.com/tutorial/openapi-extra-fields/
- Pydantic v2: https://docs.pydantic.dev/latest/
- Meta Webhook format: https://developers.facebook.com/docs/messenger-platform/webhooks
