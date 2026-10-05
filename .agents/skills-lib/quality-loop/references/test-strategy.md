# Test Strategy — Quality Loop

Полная стратегия тестирования для VIP-DXB-CatalogBot (7 платформ, 2930 тестов).

---

## Testing Pyramid

```
              /\
             /  \
            / E2E \          10% — полный webhook flow
           /  ~293  \
          /──────────\
         /Integration \      20% — asyncpg + реальная БД
        /    ~586       \
       /─────────────────\
      /    Unit Tests      \  70% — mock_db + AsyncMock, < 10ms
     /       ~2051          \
    /─────────────────────────\
```

**Целевые метрики:**
- Unit тест: < 10ms
- Integration тест: < 1s
- E2e тест: < 5s
- Полный suite: < 5 минут (без DB), < 15 минут (с TEST_DATABASE_URL)

---

## Когда какой тест использовать

| Тип теста | Использовать когда | Пример |
|-----------|-------------------|--------|
| Unit | Чистая логика, форматирование, routing без БД | `format_block_card()`, `get_platform()`, `t()` |
| Integration | Пишет/читает в БД, критичный путь данных | `get_or_create_max_user()`, `create_booking()` |
| E2E | Точка входа webhook, HMAC validation | `POST /webhook/max`, `POST /webhook/instagram` |

**Правило выбора:**
- Функция — чистая логика без БД → **unit test** с `AsyncMock`
- Функция пишет в БД → **integration test** с `TEST_DATABASE_URL`
- Функция — входная точка HTTP → **e2e** с `TestClient + HMAC`

---

## Async Test Patterns

### Базовый async тест

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_basic_async():
    result = await some_async_function()
    assert result is not None
```

### Concurrency — race condition тест

```python
@pytest.mark.asyncio
async def test_concurrent_user_creation(mock_db):
    """Конкурентное создание — no duplicates."""
    mock_db.get_or_create_max_user = AsyncMock(return_value=(-4000, True))

    results = await asyncio.gather(*[
        mock_db.get_or_create_max_user("user_same", "Test")
        for _ in range(10)
    ])

    synthetic_ids = [r[0] for r in results]
    assert len(set(synthetic_ids)) == 1, "Race condition: разные synthetic_id!"
```

### asyncio.sleep(0) — уступить event loop

```python
@pytest.mark.asyncio
async def test_with_event_loop_yield():
    """asyncio.sleep(0) позволяет другим coroutines выполниться."""
    state = {"ready": False}

    async def setter():
        await asyncio.sleep(0)  # уступаем event loop
        state["ready"] = True

    task = asyncio.create_task(setter())
    await asyncio.sleep(0)  # ждём пока setter выполнится
    await task
    assert state["ready"] is True
```

### Timeout тест

```python
@pytest.mark.asyncio
async def test_handler_responds_within_timeout():
    """Хэндлер должен ответить за 2 секунды."""
    async with asyncio.timeout(2.0):
        result = await slow_handler(user_id=123)
    assert result is not None
```

---

## TEST_DATABASE_URL Стратегия

**Источник:** `docs/TEST_DATABASE_ACCESS.md` и `docs/WINDOWS_LOCAL_DB_VERIFICATION.md`.

### Локальный запуск (Windows + Docker)

```bash
# Запустить тест-контейнер
docker run -d --name vip-dxb-test-pg -p 54329:5432 \
  -e POSTGRES_PASSWORD=postgres postgres:15

# Запустить тесты с реальной БД
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres \
  pytest tests -q -p no:cacheprovider
```

### Паттерн skip если TEST_DATABASE_URL не задан

```python
import os
import pytest

@pytest.fixture(scope="session")
def test_database_url():
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set — пропускаем integration тесты")
    return url
```

### Fixture isolation: transactional rollback

```python
@pytest.fixture
async def db(test_database_url):
    """Изолированная БД с rollback после каждого теста."""
    from data.database import CatalogDB
    db = CatalogDB()
    await db.init(test_database_url)
    # Начало транзакции
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            yield db
            raise asyncio.CancelledError  # rollback транзакции
    await db.close()
```

Альтернатива — truncation fixtures (быстрее для bulk тестов):
```python
@pytest.fixture(autouse=True)
async def cleanup_test_data(db):
    yield
    await db.pool.execute("TRUNCATE max_users CASCADE")
```

---

## Платформенная Матрица Тестирования

### Telegram (aiogram 3.25+)

| Тип | Инструменты | Пример |
|-----|------------|--------|
| Unit | `AsyncMock(spec=Message)`, `AsyncMock(spec=CallbackQuery)` | Хэндлер возвращает правильный текст |
| Integration | asyncpg pool + TEST_DATABASE_URL | Бронирование сохраняется в БД |
| E2E | aiogram `MemoryStorage` | Полный FSM flow через несколько шагов |

```python
@pytest.fixture
def mock_message():
    msg = AsyncMock(spec=Message)
    msg.from_user = MagicMock(id=123456789, language_code="ru", first_name="Test")
    msg.chat = MagicMock(id=123456789)
    msg.answer = AsyncMock()
    return msg
```

### VK (vkbottle 4.7.0)

| Тип | Инструменты | Пример |
|-----|------------|--------|
| Unit | `AsyncMock` handlers | VK callback routes к правильному handler |
| Integration | asyncpg pool | VK пользователь создаётся с VK_ID_OFFSET |
| E2E | Long Poll mock | Полный flow сообщение → ответ |

```python
# Проверка VK_ID_OFFSET (+10B)
def test_vk_user_id_offset():
    from core.user_ids import vk_to_db_id
    vk_id = 123456
    db_id = vk_to_db_id(vk_id)
    assert db_id == vk_id + 10_000_000_000
```

### Instagram / WhatsApp / Facebook / Viber (FastAPI webhooks)

| Тип | Инструменты | Пример |
|-----|------------|--------|
| Unit | мок FSM + мок formatter | FSM переходит в правильное состояние |
| Integration | asyncpg pool | synthetic_user_id создаётся в нужном диапазоне |
| E2E | `TestClient` + HMAC | POST /webhook → 200 + message processed |

```python
import hmac, hashlib, json
from fastapi.testclient import TestClient

def make_meta_signature(payload: bytes, secret: str) -> str:
    """HMAC-SHA256 для Meta API (IG/WA/FB)."""
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

def make_viber_signature(payload: bytes, auth_token: str) -> str:
    """HMAC-SHA256 для Viber (auth_token как ключ, не app_secret)."""
    sig = hmac.new(auth_token.encode(), payload, hashlib.sha256).hexdigest()
    return sig
```

### Mini App (FastAPI REST)

| Тип | Инструменты | Пример |
|-----|------------|--------|
| Unit | мок db + router | GET /catalog возвращает правильную структуру |
| Integration | asyncpg pool | Блоки из БД возвращаются корректно |
| E2E | `TestClient` | POST /bookings создаёт бронирование |

---

## Parametrize — Тесты для 4 Платформ сразу

```python
import pytest

WEBHOOK_PLATFORMS = [
    ("instagram",  "IG_GT",  -1,    -999,   "X-Hub-Signature-256"),
    ("whatsapp",   "WA_GT",  -1000, -1999,  "X-Hub-Signature-256"),
    ("facebook",   "FB_GT",  -2000, -2999,  "X-Hub-Signature-256"),
    ("viber",      "VB_GT",  -3000, -3999,  "X-Viber-Content-Signature"),
]

@pytest.mark.parametrize("platform,form_type,id_min,id_max,sig_header", WEBHOOK_PLATFORMS)
def test_synthetic_id_range(platform, form_type, id_min, id_max, sig_header):
    """Каждая платформа генерирует synthetic_user_id в своём диапазоне."""
    from core.user_ids import get_platform
    assert get_platform(id_min) == platform
    assert get_platform(id_max) == platform

@pytest.mark.parametrize("platform,form_type,id_min,id_max,sig_header", WEBHOOK_PLATFORMS)
def test_webhook_rejects_invalid_signature(platform, form_type, id_min, id_max, sig_header):
    """Все webhook endpoints отклоняют неверную подпись."""
    # ... platform-specific TestClient setup
    pass
```

---

## pytest-xdist Параллелизация

```bash
# Установить
pip install pytest-xdist

# Запустить параллельно (4 воркера)
pytest tests/ -n 4 -q

# Автоматическое количество воркеров (по числу CPU)
pytest tests/ -n auto -q

# С TEST_DATABASE_URL
TEST_DATABASE_URL=... pytest tests/ -n 4 -q -p no:cacheprovider
```

**Важно:** при параллелизации убедиться что тесты изолированы. Нельзя использовать одни и те же test user_id в разных тестах — используй уникальные ID:

```python
import uuid

@pytest.fixture
def unique_user_id():
    """Уникальный user_id для параллельных тестов."""
    return abs(hash(str(uuid.uuid4()))) % 100000 + 900000  # в диапазоне > 900K
```

---

## Минимальный Порог для Нового Хэндлера

```
[ ] happy path — основной сценарий работает
[ ] not found — пустой результат/None обрабатывается
[ ] invalid input — ошибка обрабатывается без краша
[ ] auth/permissions — роли проверяются (если есть)
[ ] concurrent — нет race condition (если модифицирует общее состояние)
```

**Smoke check перед PR:**
```bash
pytest tests --collect-only -q  # >= 2930 тестов собирается
pytest tests/ -k "new_feature_name" -v  # новые тесты проходят
pytest tests/ --lf -v  # нет регрессий в уже падавших
```
