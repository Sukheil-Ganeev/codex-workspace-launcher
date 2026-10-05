# EXP-066 (PAT-033): Mixin-based database decomposition

**Date:** 2026-02-28
**Severity:** high
**Type:** pattern
**Project:** Spy Bot v4 (MLCR Leads Bot)
**Times applied:** 1

## Context

Spy Bot v3 имел монолитный `database.py` на 1200+ строк с 45+ CRUD методами для 15 таблиц. Все домены (users, leads, chats, keywords, bans, stats, competitors, hotwords) в одном файле. При апгрейде v3 -> v4 нужно было разделить БД на модули БЕЗ изменения импортов в 20+ файлах.

## Pattern: Mixin Decomposition

### Шаг 1: Создать базовый класс с подключением
```python
# core/db/connection.py
class BaseConnection:
    _db: aiosqlite.Connection = None

    async def init(self):
        self._db = await aiosqlite.connect(DB_PATH)
        await self._db.execute("PRAGMA journal_mode=WAL")

    async def close(self):
        if self._db:
            await self._db.close()
```

### Шаг 2: Создать mixin для каждого домена
```python
# core/db/leads_mixin.py
class LeadsMixin:
    async def save_lead(self, lead: Lead) -> int:
        async with self._db.execute(...) as cursor:
            return cursor.lastrowid

    async def get_lead(self, lead_id: int) -> Optional[Lead]:
        ...

# core/db/users_mixin.py
class UsersMixin:
    async def get_user(self, user_id: int) -> Optional[dict]:
        ...
```

### Шаг 3: Композиция через множественное наследование
```python
# core/db/__init__.py
from .connection import BaseConnection
from .leads_mixin import LeadsMixin
from .users_mixin import UsersMixin
from .chats_mixin import ChatsMixin
# ... остальные миксины

class Database(
    LeadsMixin,
    UsersMixin,
    ChatsMixin,
    KeywordsMixin,
    BansMixin,
    StatsMixin,
    CompetitorsMixin,
    HotwordsMixin,
    BaseConnection
):
    """Composed database with all domain mixins."""
    pass
```

### Шаг 4: Тонкий реэкспорт в оригинальном файле
```python
# core/database.py (оригинальный путь — для backward compatibility)
from core.db import Database

__all__ = ["Database"]
```

## Результат

- **12 модулей** вместо 1 монолита (1200+ строк → ~100 строк/модуль)
- **0 изменений импортов** — все 20+ файлов продолжают делать `from core.database import Database`
- **Каждый mixin тестируется изолированно** — mock только BaseConnection._db
- **MRO (Method Resolution Order)** — Python корректно разрешает все методы через C3 linearization
- **Новые домены** — добавить mixin + включить в Database class

## Когда использовать

- Файл >800 строк с 3+ доменами (domain = набор таблиц/CRUD для одной сущности)
- Особенно актуально для database/repository/service классов
- Когда нужна backward compatibility при рефакторинге

## Когда НЕ использовать

- Файл <400 строк — overhead mixins не оправдан
- Один домен — просто разделить на модуль без mixin
- Методы сильно связаны (cross-domain joins) — mixin не поможет, нужен иной подход

## Anti-patterns

- НЕ делать mixin с `__init__` — только BaseConnection имеет `__init__`/`init()`
- НЕ хранить state в mixins (кроме `self._db` из Base) — shared state = баги в MRO
- НЕ забыть BaseConnection ПОСЛЕДНИМ в MRO (первый вызов `__init__`)

## Keywords

mixin, database, decomposition, backward-compatibility, multiple-inheritance, MRO, monolith, repository-pattern, spy-bot
