# Ответ

Добавляю отдельный словарь `ai_limit_map` и функцию `check_ai_rate` по той же схеме, что и существующие лимиты:

```python
# rate_limiter.py
from datetime import datetime, timedelta

# Хранит счётчики запросов в памяти
rate_limit_map = {}
message_limit_map = {}
ai_limit_map = {}

def check_message_rate(user_id: int) -> bool:
    """Проверяет: не более 10 сообщений в минуту на пользователя"""
    now = datetime.now()
    key = str(user_id)

    if key not in message_limit_map:
        message_limit_map[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    entry = message_limit_map[key]
    if now > entry['reset_at']:
        message_limit_map[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    if entry['count'] >= 10:
        return False

    entry['count'] += 1
    return True

def check_voice_rate(user_id: int) -> bool:
    """Проверяет: не более 5 голосовых в минуту"""
    now = datetime.now()
    key = str(user_id)

    if key not in rate_limit_map:
        rate_limit_map[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    entry = rate_limit_map[key]
    if now > entry['reset_at']:
        rate_limit_map[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    if entry['count'] >= 5:
        return False

    entry['count'] += 1
    return True

def check_ai_rate(user_id: int) -> bool:
    """Проверяет: не более 3 запросов к AI в минуту на пользователя"""
    now = datetime.now()
    key = str(user_id)

    if key not in ai_limit_map:
        ai_limit_map[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    entry = ai_limit_map[key]
    if now > entry['reset_at']:
        ai_limit_map[key] = {'count': 1, 'reset_at': now + timedelta(minutes=1)}
        return True

    if entry['count'] >= 3:
        return False

    entry['count'] += 1
    return True
```

Использование — перед вызовом AI проверяешь:

```python
if not check_ai_rate(user_id):
    await message.answer("Слишком много запросов к AI. Подожди минуту.")
    return
```
