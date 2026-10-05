# Refactor Safety — Quality Loop

Безопасный рефакторинг: characterization tests, strangler fig, feature flags, rollback.

---

## Characterization Tests (Golden-Master)

Characterization test — тест, который фиксирует текущее поведение системы, **не проверяя его корректность**. Единственная цель: обнаружить, что поведение изменилось во время рефакторинга.

### Когда писать

- Перед рефакторингом функции, у которой нет тестов
- Перед изменением сложного обработчика (> 50 строк, > 4 уровня вложенности)
- Перед миграцией DB-метода на новую схему

### Паттерн

```python
def test_catalog_price_display_snapshot():
    """Characterization test — фиксирует текущее поведение catalog_price_display.
    НЕ проверяет правильность бизнес-логики, только что поведение не изменилось.
    Baseline создан: 2026-03-12, commit: [SHA]"""
    from bot.services.catalog_price_display import get_price_display

    # Фиксируем ТЕКУЩИЙ вывод для всех категорий
    assert "USD" in get_price_display(category="excursion", price=150)
    assert "USD" in get_price_display(category="safari", price=200)
    assert "AED" in get_price_display(category="ticket", price=300)
    assert "AED" in get_price_display(category="other", price=100)
```

### Что фиксировать

```python
# ФИКСИРОВАТЬ: ключевые слова в выводе
assert "Dubai" in format_block_card(block_id=1)

# ФИКСИРОВАТЬ: тип возвращаемого значения
assert isinstance(result, dict)
assert "id" in result

# ФИКСИРОВАТЬ: наличие/отсутствие ключей
assert result.get("synthetic_user_id") is not None

# ФИКСИРОВАТЬ: диапазоны чисел
assert -4999 <= result["synthetic_user_id"] <= -4000

# НЕ ФИКСИРОВАТЬ: конкретные строки с датами или случайными данными
# assert result["created_at"] == "2026-03-12"  — сломается завтра
```

---

## Strangler Fig Pattern

Для крупных миграций, когда нельзя переписать всё за один раз. Оборачиваем legacy-код, постепенно перенаправляем трафик.

### Применение для VIP-DXB-CatalogBot

```python
# bot/handlers/catalog.py

# Шаг 1: Добавляем feature flag
USE_NEW_CATALOG_HANDLER = os.getenv("USE_NEW_CATALOG_HANDLER", "false") == "true"

async def handle_catalog_start(callback: CallbackQuery):
    """Entry point — роутит к новой или старой реализации."""
    if USE_NEW_CATALOG_HANDLER:
        return await _new_catalog_start(callback)
    return await _legacy_catalog_start(callback)

# Шаг 2: Новая реализация живёт рядом
async def _new_catalog_start(callback: CallbackQuery):
    """Новая реализация с оптимизированными запросами."""
    ...

# Шаг 3: Старая реализация остаётся нетронутой
async def _legacy_catalog_start(callback: CallbackQuery):
    """Legacy — не трогать до завершения миграции."""
    ...
```

### Для Omni Inbox коннекторов

```python
# bot/services/omni_inbox.py

USE_OMNI_ROUTING = os.getenv("USE_OMNI_ROUTING", "false") == "true"

async def on_incoming_message(platform, platform_user_id, text):
    if USE_OMNI_ROUTING:
        return await _new_omni_routing(platform, platform_user_id, text)
    # legacy: прямой routing к платформенному handler
    return await _legacy_routing(platform, platform_user_id, text)
```

---

## Feature Flag Rollout

Поэтапный ввод нового кода в production. Стратегия снижает риск при деплое.

### Стратегия VIP-DXB-CatalogBot

```
Stage 0: 0%   — feature flag OFF, только тесты
Stage 1: 5%   — 5% пользователей (первые 24 часа)
Stage 2: 25%  — расширить если нет ошибок в логах
Stage 3: 50%  — мониторинг ещё 24 часа
Stage 4: 100% — полный переход
Stage 5: cleanup — убрать legacy код после одного полного цикла на 100%
```

### Простой процентный rollout

```python
import hashlib

def should_use_new_feature(user_id: int, feature_name: str, rollout_percent: int) -> bool:
    """Детерминированный rollout: один user_id всегда получает одно решение."""
    hash_input = f"{feature_name}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    return (hash_value % 100) < rollout_percent

# Использование:
if should_use_new_feature(user_id, "new_catalog_handler", rollout_percent=5):
    return await _new_catalog_start(callback)
return await _legacy_catalog_start(callback)
```

### Env-var флаг (проще, для первых шагов)

```python
# .env.prod
USE_NEW_CATALOG_HANDLER=false   # Stage 0
# USE_NEW_CATALOG_HANDLER=true  # Stage 4

# В коде
USE_NEW_CATALOG_HANDLER = os.getenv("USE_NEW_CATALOG_HANDLER", "false") == "true"
```

### Когда убирать legacy путь

- feature flag на 100% в течение 7+ дней без инцидентов
- Все characterization tests проходят с новым кодом
- Monitoring: нет новых ошибок в логах на GCP VM tourist-bot
- Выполнено: отдельный PR "cleanup: retire legacy catalog handler"

---

## Rollback Procedure

Если что-то пошло не так после деплоя — пошаговый откат.

### Шаг 1: Быстрый откат через feature flag (< 5 минут)

```bash
# На GCP VM tourist-bot
ssh $SERVER_USER@$SERVER_HOST

# Изменить feature flag без деплоя
echo "USE_NEW_CATALOG_HANDLER=false" >> /opt/catalog-bot/.env.prod

# Перезапустить контейнер
docker compose --env-file .env.prod -f deploy/docker-compose.prod.yml restart catalog-bot
```

### Шаг 2: Git revert (если нет feature flag)

```bash
# Найти коммит, который нужно откатить
git log --oneline -10

# Создать revert коммит (не destructive)
git revert abc1234 --no-edit
git push origin main

# GitHub Actions задеплоит автоматически
```

### Шаг 3: Проверить деплой

```bash
# Статус GitHub Actions
gh run list --limit 5

# Логи контейнера на сервере
ssh $SERVER_USER@$SERVER_HOST "docker logs catalog-bot --tail 50"
```

### Что нельзя откатить без ручного вмешательства

- DB миграции (таблицы, колонки) — нужен `ALTER TABLE DROP COLUMN`
- Данные уже записанные новым кодом
- Изменения в Meta webhook endpoint URLs

**Поэтому:** тестировать DB миграции на копии production данных перед применением.

---

## Backward-Compatible API Changes

При изменении сигнатур функций в `data/database.py`:

### Deprecation warning паттерн

```python
import warnings

async def get_user(self, user_id: int, include_loyalty: bool = True):
    """New signature. Old callers passing positional args still work."""
    ...

async def get_user_legacy(self, user_id: int):
    """
    DEPRECATED: используй get_user(user_id).
    Будет удалён в следующей версии.
    """
    warnings.warn(
        "get_user_legacy() deprecated, use get_user()",
        DeprecationWarning,
        stacklevel=2
    )
    return await self.get_user(user_id)
```

### Backward-compatible kwargs

```python
# Старая сигнатура: search_blocks(query, limit=20)
# Новая сигнатура: search_blocks(query, limit=20, lang="ru", emirate=None)

async def search_blocks(
    self,
    query: str,
    limit: int = 20,
    lang: str = "ru",          # новый параметр с default
    emirate: str | None = None  # новый параметр с default
):
    """Backward-compatible: старый код с (query, limit) продолжает работать."""
    ...
```

---

## DB Migrations Safety

Правила безопасных миграций для VIP-DXB-CatalogBot:

### Идемпотентность обязательна

```python
# НЕВЕРНО — сломает повторный деплой
async def _migrate_v22_max_bot(self):
    await self.pool.execute("CREATE TABLE max_users (...)")

# ВЕРНО — безопасно запускать многократно
async def _migrate_v22_max_bot(self):
    await self.pool.execute("""
        CREATE TABLE IF NOT EXISTS max_users (
            max_id VARCHAR(64) PRIMARY KEY,
            synthetic_user_id BIGINT UNIQUE NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    # Добавление колонки — проверить через information_schema
    exists = await self.pool.fetchval("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name='max_users' AND column_name='language'
    """)
    if not exists:
        await self.pool.execute(
            "ALTER TABLE max_users ADD COLUMN language VARCHAR(10) DEFAULT 'ru'"
        )
```

### Тестирование миграций

```python
@pytest.mark.asyncio
async def test_migration_v22_idempotent(db):
    """Миграция v22 должна быть безопасна при повторном запуске."""
    # Запускаем дважды — не должно быть ошибок
    await db._migrate_v22_max_bot()
    await db._migrate_v22_max_bot()  # второй раз — не падает

    # Проверяем что таблица создана
    result = await db.pool.fetchval("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_name='max_users'
    """)
    assert result == 1
```

### Rollback DB change

```sql
-- Если нужно откатить добавленную колонку
ALTER TABLE max_users DROP COLUMN IF EXISTS language;

-- Если нужно откатить таблицу
DROP TABLE IF EXISTS max_users;
```

**Важно:** перед `DROP TABLE` убедиться что нет FK constraints из других таблиц.
