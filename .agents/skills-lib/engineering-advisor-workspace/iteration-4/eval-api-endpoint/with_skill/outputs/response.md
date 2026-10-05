# Engineering Advisor Response — eval-api-endpoint (with_skill)

**Trigger detected:** #13 — Creating API endpoint (authorization + validation + rate limit required)
**Level:** Recommended
**Date:** 2026-03-05

---

Engineering Advisor activated. 15+ lessons loaded from experience. Checking code with accumulated lessons in mind.

---

## Severity Output

```
=== Engineering Advisor ===
WARN (3): Missing authorization, input validation, rate limiting
INFO (1): Return of created order ID — addressed below
Experience: 0 lessons applied (new task, Python/FastAPI)
===========================
```

---

## What Is Wrong With the Current Code

Before adding the return ID, we need to address three open doors:

**1. No Authorization**
Anyone on the internet can POST to `/api/orders` and create an order in your database. Bots, competitors, random people.

**2. No Input Validation**
`data: dict` accepts literally anything. You can pass `{"price": -99999}`, or an empty object, or fields that don't exist in the model — and Python will crash with an unhandled error.

**3. No Rate Limiting**
One person can send 10,000 requests per second and take down the database.

---

## Fixed Code (with ID return + minimum security)

**Step 1: Create a Pydantic schema for the order** (instead of a bare `dict`)

```python
from pydantic import BaseModel, Field
from typing import Optional

class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    tour_name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)  # price must be > 0
    travel_date: Optional[str] = None
    # add your own fields
```

**Step 2: Updated endpoint**

```python
from fastapi import Depends, HTTPException, Header
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post('/api/orders', status_code=201)
@limiter.limit("10/minute")  # max 10 orders per minute per IP
async def create_order(
    data: OrderCreate,  # Pydantic validates automatically
    authorization: str = Header(...)  # requires Authorization header
):
    # Simple token check (replace with your own logic)
    if authorization != f"Bearer {settings.API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    order = Order(**data.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)  # refresh object from DB to get the ID

    return {
        "status": "ok",
        "order_id": order.id  # return ID as requested
    }
```

**Key change for your request** — one line `db.refresh(order)` before `return`. Without it, `order.id` will be `None` because SQLAlchemy assigns the ID only after commit, and you need to re-read the object from the database.

---

## What to Do Next (by priority)

| Priority | What | Why |
|----------|------|-----|
| Now | Add `db.refresh(order)` | Get the ID — your task |
| Now | Replace `dict` with Pydantic model | Protection from malformed data |
| Soon | Add authorization | Protection from outsiders |
| Soon | Add rate limit (`slowapi`) | Protection from overload |

Do you want a full working example with JWT token authorization, or is the minimum — Pydantic + `db.refresh()` — enough?

---

## Engineering Advisor Summary

```
=== Engineering Advisor Summary ===
Files changed: 0 (advisory response only)
Triggers fired: #13 (API endpoint — authorization + validation + rate limit required)
Checks: 4/4 identified
BLOCK: 0
WARN: 3 — missing auth, missing validation, missing rate limit
INFO: 1 — db.refresh() for ID return
Experience applied: none (new Python/FastAPI context)
New experience: none recorded
===================================
```
