"""
Test stub template для VIP-DXB-CatalogBot.
Использование: скопировать в tests/test_<module_name>.py, заполнить заглушки.

Пример: tests/test_max_user.py
"""
import os
import asyncio
import hmac
import hashlib
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ─────────────────────────────────────────────
# FIXTURES: Database
# ─────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_database_url():
    """TEST_DATABASE_URL из environment. Пропускает integration тесты если не задан."""
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set — пропускаем integration тесты")
    return url


@pytest.fixture
async def db(test_database_url):
    """Реальное asyncpg соединение для integration тестов."""
    from data.database import CatalogDB
    catalog_db = CatalogDB()
    await catalog_db.init(test_database_url)
    yield catalog_db
    await catalog_db.close()


@pytest.fixture
def mock_db():
    """Мок CatalogDB для unit тестов (без реальной БД)."""
    db = AsyncMock()
    # Настроить возвращаемые значения для часто используемых методов
    db.get_or_create_max_user = AsyncMock(return_value=(-4000, True))
    db.get_user = AsyncMock(return_value={"user_id": 123, "username": "test_user"})
    db.search_blocks = AsyncMock(return_value=[])
    return db


# ─────────────────────────────────────────────
# FIXTURES: Telegram (aiogram)
# ─────────────────────────────────────────────

@pytest.fixture
def mock_message():
    """Мок aiogram Message для unit тестов Telegram хэндлеров."""
    from aiogram.types import Message, User, Chat
    msg = AsyncMock(spec=Message)
    msg.from_user = MagicMock(spec=User)
    msg.from_user.id = 123456789
    msg.from_user.language_code = "ru"
    msg.from_user.first_name = "Test"
    msg.from_user.username = "test_user"
    msg.chat = MagicMock(spec=Chat)
    msg.chat.id = 123456789
    msg.text = "Тестовое сообщение"
    msg.answer = AsyncMock()
    msg.reply = AsyncMock()
    return msg


@pytest.fixture
def mock_callback():
    """Мок aiogram CallbackQuery для unit тестов Telegram callback хэндлеров."""
    from aiogram.types import CallbackQuery, User
    cb = AsyncMock(spec=CallbackQuery)
    cb.from_user = MagicMock(spec=User)
    cb.from_user.id = 123456789
    cb.from_user.language_code = "ru"
    cb.from_user.first_name = "Test"
    cb.data = "catalog:dubai"
    cb.answer = AsyncMock()
    cb.message = AsyncMock()
    cb.message.edit_text = AsyncMock()
    cb.message.edit_reply_markup = AsyncMock()
    return cb


# ─────────────────────────────────────────────
# FIXTURES: Webhook (FastAPI + HMAC)
# ─────────────────────────────────────────────

def _make_meta_hmac(payload: bytes, secret: str) -> str:
    """HMAC-SHA256 для Meta API (Instagram / WhatsApp / Facebook)."""
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def _make_viber_hmac(payload: bytes, auth_token: str) -> str:
    """HMAC-SHA256 для Viber (auth_token как ключ, не app_secret)."""
    return hmac.new(auth_token.encode(), payload, hashlib.sha256).hexdigest()


@pytest.fixture
def app_secret():
    return "test_meta_app_secret_for_hmac_testing"


@pytest.fixture
def meta_headers(app_secret):
    """Factory для генерации корректных HMAC заголовков Meta webhook."""
    def _make(payload: dict | bytes) -> dict:
        if isinstance(payload, dict):
            payload = json.dumps(payload).encode()
        return {
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _make_meta_hmac(payload, app_secret),
        }
    return _make


# ─────────────────────────────────────────────
# ТЕСТЫ: get_or_create_max_user()
# ─────────────────────────────────────────────

class TestGetOrCreateMaxUser:
    """Unit тесты для get_or_create_max_user() — без реальной БД."""

    @pytest.mark.asyncio
    async def test_creates_new_user(self, mock_db):
        """Новый max_id → synthetic_user_id < 0, created=True."""
        mock_db.get_or_create_max_user = AsyncMock(return_value=(-4000, True))
        result_id, created = await mock_db.get_or_create_max_user("user_new", "Test User")
        assert created is True
        assert result_id < 0

    @pytest.mark.asyncio
    async def test_returns_existing_user(self, mock_db):
        """Повторный вызов → тот же synthetic_user_id, created=False."""
        mock_db.get_or_create_max_user = AsyncMock(side_effect=[
            (-4000, True),   # первый вызов: создание
            (-4000, False),  # второй вызов: существующий
        ])
        id1, c1 = await mock_db.get_or_create_max_user("user_same", "Test")
        id2, c2 = await mock_db.get_or_create_max_user("user_same", "Test")
        assert id1 == id2
        assert c1 is True
        assert c2 is False

    @pytest.mark.asyncio
    async def test_synthetic_id_in_max_range(self, mock_db):
        """synthetic_user_id должен быть в диапазоне -4000..-4999 для Max Bot."""
        mock_db.get_or_create_max_user = AsyncMock(return_value=(-4042, True))
        result_id, _ = await mock_db.get_or_create_max_user("user123", "Test")
        assert -4999 <= result_id <= -4000, f"ID {result_id} вне диапазона Max Bot"

    @pytest.mark.asyncio
    async def test_concurrent_calls_no_race_condition(self, mock_db):
        """Конкурентные вызовы с одним max_id — не должно быть дублей."""
        mock_db.get_or_create_max_user = AsyncMock(return_value=(-4000, True))
        results = await asyncio.gather(*[
            mock_db.get_or_create_max_user("user_concurrent", "Test")
            for _ in range(10)
        ])
        synthetic_ids = [r[0] for r in results]
        assert len(set(synthetic_ids)) == 1, "Race condition: разные synthetic_id!"

    @pytest.mark.asyncio
    async def test_empty_max_id_edge_case(self, mock_db):
        """Пустой max_id → заглушка (реализовать логику в цикле)."""
        pytest.skip("not implemented — заполнить после определения поведения")


# ─────────────────────────────────────────────
# ТЕСТЫ: Integration (требуют TEST_DATABASE_URL)
# ─────────────────────────────────────────────

class TestGetOrCreateMaxUserIntegration:
    """Integration тесты — требуют реального asyncpg подключения."""

    @pytest.mark.asyncio
    async def test_insert_and_retrieve(self, db):
        """Реальная вставка в БД и повторное получение."""
        pytest.skip("not implemented")

    @pytest.mark.asyncio
    async def test_idempotent_on_duplicate(self, db):
        """Дублирующий вызов не создаёт вторую запись в max_users."""
        pytest.skip("not implemented")


# ─────────────────────────────────────────────
# ТЕСТЫ: Parametrize по 4 платформам
# ─────────────────────────────────────────────

WEBHOOK_PLATFORMS = [
    ("instagram",  "IG_GT",  -1,    -999),
    ("whatsapp",   "WA_GT",  -1000, -1999),
    ("facebook",   "FB_GT",  -2000, -2999),
    ("viber",      "VB_GT",  -3000, -3999),
]


@pytest.mark.parametrize("platform,form_type,id_min,id_max", WEBHOOK_PLATFORMS)
def test_synthetic_user_id_range(platform, form_type, id_min, id_max):
    """Каждая платформа генерирует synthetic_user_id в своём диапазоне."""
    from core.user_ids import get_platform
    assert get_platform(id_min) == platform
    assert get_platform(id_max) == platform


@pytest.mark.parametrize("platform,form_type,id_min,id_max", WEBHOOK_PLATFORMS)
def test_form_type_per_platform(platform, form_type, id_min, id_max):
    """Каждая платформа использует правильный form_type."""
    pytest.skip(f"not implemented — проверить form_type={form_type} для {platform}")
