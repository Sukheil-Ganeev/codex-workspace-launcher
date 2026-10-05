# Ответ на запрос

Да, всё это можно сделать. Это четыре отдельных задачи, и я готов помочь с каждой. Давай разберём их по порядку.

---

## 1. Авторизация через JWT в API

Зависит от стека. Приведу пример для **Python (FastAPI)** и **Node.js (Express)**.

### FastAPI + python-jose

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"  # вынести в .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
```

### Node.js + Express + jsonwebtoken

```bash
npm install jsonwebtoken bcryptjs
```

```js
// middleware/auth.js
const jwt = require('jsonwebtoken');

const SECRET = process.env.JWT_SECRET;

function signToken(payload) {
  return jwt.sign(payload, SECRET, { expiresIn: '30m' });
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer <token>

  if (!token) return res.status(401).json({ error: 'No token' });

  jwt.verify(token, SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid token' });
    req.user = user;
    next();
  });
}

module.exports = { signToken, authMiddleware };
```

---

## 2. Endpoint для заказов с валидацией

### FastAPI + Pydantic

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from typing import List
from datetime import date

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderItem(BaseModel):
    product_id: int
    quantity: int

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class OrderCreate(BaseModel):
    items: List[OrderItem]
    delivery_date: date
    customer_note: str = ""

    @field_validator('items')
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

@router.post("/")
def create_order(order: OrderCreate, current_user=Depends(get_current_user)):
    # Здесь логика создания заказа в БД
    return {"status": "created", "user_id": current_user["sub"], "order": order}

@router.get("/{order_id}")
def get_order(order_id: int, current_user=Depends(get_current_user)):
    # Здесь запрос к БД
    return {"order_id": order_id}
```

### Express + Joi (Node.js)

```bash
npm install joi
```

```js
// routes/orders.js
const express = require('express');
const Joi = require('joi');
const { authMiddleware } = require('../middleware/auth');

const router = express.Router();

const orderSchema = Joi.object({
  items: Joi.array().items(
    Joi.object({
      product_id: Joi.number().integer().required(),
      quantity: Joi.number().integer().min(1).required()
    })
  ).min(1).required(),
  delivery_date: Joi.date().min('now').required(),
  customer_note: Joi.string().max(500).optional()
});

router.post('/', authMiddleware, (req, res) => {
  const { error, value } = orderSchema.validate(req.body);
  if (error) return res.status(400).json({ error: error.details[0].message });

  // Создание заказа в БД
  res.status(201).json({ status: 'created', order: value });
});

module.exports = router;
```

---

## 3. Redis для кэширования сессий

### Установка Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Python (aioredis / redis-py)

```bash
pip install redis
```

```python
# cache.py
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_session(user_id: str, session_data: dict, ttl: int = 1800):
    """Сохранить сессию на 30 минут"""
    r.setex(f"session:{user_id}", ttl, json.dumps(session_data))

def get_session(user_id: str) -> dict | None:
    data = r.get(f"session:{user_id}")
    return json.loads(data) if data else None

def delete_session(user_id: str):
    r.delete(f"session:{user_id}")
```

```python
# Использование в FastAPI
@router.post("/login")
def login(credentials: LoginForm):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    cache_session(str(user.id), {"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
```

### Node.js (ioredis)

```bash
npm install ioredis
```

```js
// cache.js
const Redis = require('ioredis');
const redis = new Redis({ host: 'localhost', port: 6379 });

async function cacheSession(userId, data, ttl = 1800) {
  await redis.setex(`session:${userId}`, ttl, JSON.stringify(data));
}

async function getSession(userId) {
  const data = await redis.get(`session:${userId}`);
  return data ? JSON.parse(data) : null;
}

async function deleteSession(userId) {
  await redis.del(`session:${userId}`);
}

module.exports = { cacheSession, getSession, deleteSession };
```

---

## 4. Деплой на продакшн с nginx и systemd

### systemd — запуск приложения как сервис

Создай файл `/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=My API Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
# Для Node.js: ExecStart=/usr/bin/node /var/www/myapp/index.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production
EnvironmentFile=/var/www/myapp/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
sudo systemctl status myapp
```

### nginx — reverse proxy

Создай файл `/etc/nginx/sites-available/myapp`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Редирект на HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # Статические файлы (если есть)
    location /static/ {
        alias /var/www/myapp/static/;
        expires 30d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t          # проверка конфига
sudo systemctl reload nginx
```

### SSL через Let's Encrypt (бесплатно)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Что нужно уточнить для реализации

Чтобы я мог дать более точные инструкции или написать готовый код под твой проект:

1. **Стек** — Python (FastAPI/Flask/Django) или Node.js (Express/Fastify)?
2. **База данных** — PostgreSQL, MySQL, MongoDB?
3. **ОС сервера** — Ubuntu, Debian, CentOS?
4. **Уже есть Redis на сервере?** Или нужно установить с нуля?
5. **Домен уже настроен?** DNS указывает на сервер?

Всё четыре задачи реальны и решаемы. Приведённые примеры — рабочие шаблоны, которые легко адаптировать под конкретный проект.
