# EXP-035-038: Rassilka Bot v3.0 — 4 критических урока

**Дата:** 2026-02-19
**Проект:** Rassilka Bot v3.0 (WhatsApp рассылки, 9 волн, Telegram-бот aiogram 3.x)
**Источник:** Production debugging и рефакторинг 9 волн

---

## EXP-035 (FIX-RASSILKA-001): Async Migration — 92 missing await

**Проблема:** При миграции sync → aiosqlite только 46% функций вызывались с await в call sites.

**Ошибка:**
```python
# Было правильно:
async def get_user(id):
    return await db.query(...)

# Но вызовы забыли await:
user = get_user(id)  # ✗ вернул coroutine, не данные
message_text = f"{user.name}"  # ✗ TypeError: coroutine object is not subscriptable
```

**Почему тесты не нашли:** Unit-тесты мокируют DB, не видят что функция вернула coroutine.

**Решение:**
1. grep всех call sites: `grep -r "= get_" bot/handlers | grep -v "= await get_"`
2. Integration tests: каждая async функция — минимум один тест с реальным await
3. Статический анализ: mypy с `--no-implicit-optional`

**Урок:** Триггер #9 (миграция) → обязательный этап "full grep + integration tests" перед QA.

---

## EXP-036 (FIX-RASSILKA-002): God Object Refactoring — __init__.py

**Проблема:** Разбили `db.py` на 3 файла, но забыли реэкспортировать в `__init__.py`.

```python
# Старый код ожидал
from bot.db import UserModel, get_user, init_db

# Новый код при пустом __init__.py → ImportError
```

**Решение:**
```python
# bot/db/__init__.py ОБЯЗАН содержать
from .models import UserModel, Campaign, Message
from .queries import get_user, create_user, update_user, delete_user, get_campaign
from .migrations import init_db, migrate_v1_to_v2

__all__ = ['UserModel', 'Campaign', 'Message', 'get_user', 'create_user', ...]
```

**Backward-compatibility:** Включать legacy имена функций если переименованы:
```python
get_user_safe = get_user_with_validation  # alias
```

**Урок:** При разделении монолита → `__init__.py` реэкспортирует ВСЕ public API.

---

## EXP-037 (PAT-019): QA Gate Check Pattern

**Проблема:** 92 missing await не поймали unit-тесты, потому что нет quality gate между волнами.

**Решение: Обязательный gate check между волнами**

```bash
# gate_check.sh
python -m py_compile bot/**/*.py  # syntax
python -c "import bot; import bot.handlers"  # imports
grep -r "= get_" bot/handlers | grep -v "= await get_"  # await
pytest -q  # tests
```

**Метрика:** Gate Check поймал 92 missing await ДО deployment. Без gate = production crash.

**Правило:** 3+ волны рефакторинга → обязательный quality gate между этапами.

---

## EXP-038 (PAT-020): Shared Session Pattern — aiohttp.ClientSession

**Проблема:** Каждый handler создавал `aiohttp.ClientSession()` → 50+ сессий в памяти.

**Решение: Singleton session через DI**

```python
# main.py
async def main():
    session = ClientSession()
    dp["session"] = session  # DI injection

    # cleanup при shutdown
    await dp.feed_shutdown()
    await session.close()

# handler использует
async def send_message(message: Message):
    session = message.bot["session"]
    async with session.post(...) as resp: ...
```

**Для scheduler (нет dp):**
```python
_scheduler_session = None

async def get_scheduler_session():
    global _scheduler_session
    if _scheduler_session is None:
        _scheduler_session = ClientSession()
    return _scheduler_session
```

**Паттерны:**
- DI через `dp["key"]` — для handlers
- Global singleton — для scheduler/background
- Temporary — если 1-2 запроса
- Connection pool — для 100+ запросов/мин

**Правило:** Не создавать ClientSession в функции вызываемой 100+ раз/час.

---

## Интеграция с engineering-advisor

Все 4 урока подтверждают триггеры:
- **#9 (Миграция)** → тесты + grep обязательны
- **#10 (Фича 3+ файлов)** → __init__.py реэкспорт
- **#10 (План)** → gate check между волнами
- **#4 (Безопасность)** → singleton + cleanup для ресурсов

