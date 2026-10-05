"""
RedisFSMManager — Drop-in замена для core/fsm.py FSMManager.

Использование:
    # Было:
    from core.fsm import FSMManager
    ig_fsm = FSMManager("ig")

    # Стало (API идентичен):
    from core.fsm_redis import RedisFSMManager
    ig_fsm = RedisFSMManager("ig")

Ключ Redis: fsm:{platform}:{user_id}
Значение:   JSON {"state": "...", "form_data": {...}, "updated_at": "..."}
TTL:        3600s (1 час — совпадает с core/fsm.py timeout)

Graceful degradation: если Redis down → in-memory fallback автоматически.
"""

import json
import logging
from datetime import datetime
from typing import Optional

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

FSM_TTL = 3600  # 1 час

# In-memory fallback (используется при недоступности Redis)
_fallback_store: dict = {}


async def _get_redis() -> Optional[aioredis.Redis]:
    """Возвращает Redis клиент или None если недоступен."""
    try:
        from core.redis_client import get_redis
        return await get_redis()
    except Exception:
        return None


class RedisFSMManager:
    """
    Redis-backed FSM manager для webhook-ботов (IG, WA, FB, Viber).
    Drop-in замена для core/fsm.py FSMManager.

    Если Redis недоступен — автоматически использует in-memory fallback.
    Recovery: при старте сервиса сканирует прерванные сессии.
    """

    def __init__(self, platform: str):
        self.platform = platform

    def _key(self, user_id: str) -> str:
        return f"fsm:{self.platform}:{user_id}"

    def _fallback_key(self, user_id: str) -> str:
        return f"{self.platform}:{user_id}"

    # ------------------------------------------------------------------
    # Основной интерфейс (совместимый с core/fsm.py FSMManager)
    # ------------------------------------------------------------------

    async def get_state(self, user_id: str) -> Optional[str]:
        """Получить текущее состояние FSM."""
        r = await _get_redis()
        if r:
            try:
                raw = await r.get(self._key(user_id))
                if raw:
                    data = json.loads(raw)
                    return data.get("state")
                return None
            except Exception as e:
                logger.warning(f"[fsm:{self.platform}] get_state Redis error user={user_id}: {e}")

        # Fallback: in-memory
        data = _fallback_store.get(self._fallback_key(user_id), {})
        return data.get("state")

    async def set_state(self, user_id: str, state: str) -> None:
        """Установить состояние FSM (сохраняет form_data)."""
        r = await _get_redis()
        if r:
            try:
                raw = await r.get(self._key(user_id))
                data = json.loads(raw) if raw else {}
                data["state"] = state
                data["updated_at"] = datetime.utcnow().isoformat()
                await r.setex(self._key(user_id), FSM_TTL, json.dumps(data))
                logger.debug(f"[fsm:{self.platform}] set_state user={user_id} state={state}")
                return
            except Exception as e:
                logger.warning(f"[fsm:{self.platform}] set_state Redis error user={user_id}: {e}")

        # Fallback: in-memory
        key = self._fallback_key(user_id)
        data = _fallback_store.get(key, {})
        data["state"] = state
        data["updated_at"] = datetime.utcnow().isoformat()
        _fallback_store[key] = data

    async def get_data(self, user_id: str) -> dict:
        """Получить form_data из FSM состояния."""
        r = await _get_redis()
        if r:
            try:
                raw = await r.get(self._key(user_id))
                if raw:
                    data = json.loads(raw)
                    return data.get("form_data", {})
                return {}
            except Exception as e:
                logger.warning(f"[fsm:{self.platform}] get_data Redis error user={user_id}: {e}")

        # Fallback: in-memory
        data = _fallback_store.get(self._fallback_key(user_id), {})
        return data.get("form_data", {})

    async def update_data(self, user_id: str, **kwargs) -> None:
        """Добавить/обновить поля в form_data (merge, не replace)."""
        r = await _get_redis()
        if r:
            try:
                raw = await r.get(self._key(user_id))
                data = json.loads(raw) if raw else {}
                form_data = data.get("form_data", {})
                form_data.update(kwargs)
                data["form_data"] = form_data
                data["updated_at"] = datetime.utcnow().isoformat()
                await r.setex(self._key(user_id), FSM_TTL, json.dumps(data))
                logger.debug(f"[fsm:{self.platform}] update_data user={user_id} keys={list(kwargs.keys())}")
                return
            except Exception as e:
                logger.warning(f"[fsm:{self.platform}] update_data Redis error user={user_id}: {e}")

        # Fallback: in-memory
        key = self._fallback_key(user_id)
        data = _fallback_store.get(key, {})
        form_data = data.get("form_data", {})
        form_data.update(kwargs)
        data["form_data"] = form_data
        _fallback_store[key] = data

    async def clear(self, user_id: str) -> None:
        """Очистить FSM состояние (по завершении бронирования или отмене)."""
        r = await _get_redis()
        if r:
            try:
                await r.delete(self._key(user_id))
                logger.debug(f"[fsm:{self.platform}] cleared user={user_id}")
                return
            except Exception as e:
                logger.warning(f"[fsm:{self.platform}] clear Redis error user={user_id}: {e}")

        # Fallback: in-memory
        _fallback_store.pop(self._fallback_key(user_id), None)

    async def get_all(self, user_id: str) -> Optional[dict]:
        """Получить всё: state + form_data + updated_at."""
        r = await _get_redis()
        if r:
            try:
                raw = await r.get(self._key(user_id))
                return json.loads(raw) if raw else None
            except Exception as e:
                logger.warning(f"[fsm:{self.platform}] get_all Redis error user={user_id}: {e}")

        # Fallback: in-memory
        return _fallback_store.get(self._fallback_key(user_id))

    # ------------------------------------------------------------------
    # Recovery: восстановление после рестарта сервиса
    # ------------------------------------------------------------------

    async def get_active_sessions(self) -> list[dict]:
        """
        Вернуть список активных сессий платформы.
        Используется для recovery при старте FastAPI.

        Возвращает: [{"user_id": "...", "state": "...", "updated_at": "..."}]
        """
        r = await _get_redis()
        if not r:
            return []

        try:
            pattern = f"fsm:{self.platform}:*"
            keys = await r.keys(pattern)
            sessions = []
            for key in keys:
                raw = await r.get(key)
                if raw:
                    data = json.loads(raw)
                    user_id = key.split(":")[-1]
                    sessions.append({
                        "user_id": user_id,
                        "state": data.get("state"),
                        "updated_at": data.get("updated_at", "")
                    })
            return sessions
        except Exception as e:
            logger.warning(f"[fsm:{self.platform}] get_active_sessions error: {e}")
            return []


# ------------------------------------------------------------------
# Singleton экземпляры для каждой платформы
# ------------------------------------------------------------------
# Использование в обработчиках:
#
#   from core.fsm_redis import ig_fsm, wa_fsm, fb_fsm, vb_fsm
#
#   state = await ig_fsm.get_state(sender_id)
#   await ig_fsm.set_state(sender_id, "WAITING_NAME")
#   await ig_fsm.update_data(sender_id, name="Иван")
#   await ig_fsm.clear(sender_id)

ig_fsm = RedisFSMManager("ig")   # Instagram: sender IGSID
wa_fsm = RedisFSMManager("wa")   # WhatsApp: wa_id (номер телефона)
fb_fsm = RedisFSMManager("fb")   # Facebook: PSID
vb_fsm = RedisFSMManager("vb")   # Viber: viber_user_id


# ------------------------------------------------------------------
# Recovery функция — вызывать при startup FastAPI
# ------------------------------------------------------------------

async def recover_interrupted_sessions(notify_fn=None) -> int:
    """
    При старте сервиса: найти сессии, прерванные при падении,
    уведомить пользователей что нужно начать заново.

    notify_fn: async callable(platform, user_id, message) — для отправки сообщений
    Возвращает: количество восстановленных сессий

    Пример в app.py:
        from core.fsm_redis import recover_interrupted_sessions

        @app.on_event("startup")
        async def startup():
            await recover_interrupted_sessions(notify_fn=send_restart_message)
    """
    total = 0
    for fsm in [ig_fsm, wa_fsm, fb_fsm, vb_fsm]:
        sessions = await fsm.get_active_sessions()
        for session in sessions:
            user_id = session["user_id"]
            state = session["state"]
            if state:  # есть активная сессия
                logger.info(f"[fsm:recovery] {fsm.platform}:{user_id} was in state={state}")
                await fsm.clear(user_id)  # сбрасываем прерванную сессию
                total += 1
                if notify_fn:
                    try:
                        await notify_fn(
                            fsm.platform,
                            user_id,
                            "Ваша сессия была прервана из-за перезапуска сервера. "
                            "Нажмите /start для нового бронирования."
                        )
                    except Exception as e:
                        logger.warning(f"[fsm:recovery] notify failed {fsm.platform}:{user_id}: {e}")

    logger.info(f"[fsm:recovery] cleared {total} interrupted sessions")
    return total
