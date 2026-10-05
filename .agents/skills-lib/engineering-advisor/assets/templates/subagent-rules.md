# Обязательные правила для субагента

> Копируй этот блок в КАЖДЫЙ промпт при использовании Task tool для делегации кода.
> Источник: WARN-006 — субагенты НЕ наследуют контекст скиллов.

---

## Минимальные правила (ВСЕГДА включать)

```
## Обязательные правила для субагента

1. БЭКАП: Перед Edit/Write — копия в backups/ с датой (YYYYMMDD_HHMMSS)
2. ТЕСТЫ: MagicMock(spec=RealClass), не голый MagicMock()
3. DATACLASS: Сверить все .field с @dataclass определением
4. AIOGRAM: Command() хэндлеры ВЫШЕ F.text catch-all
5. ASYNC: Нет time.sleep/requests.get в async — только aiohttp/asyncio.sleep
6. HTML: html.escape() на пользовательский ввод перед Telegram HTML
7. CALLBACK: Каждый CallbackQuery handler → callback.answer()
8. ВЕРИФИКАЦИЯ: Финал = python -c "import module" + pytest
```

---

## Расширенные правила (для сложных задач)

```
## Расширенные правила для субагента

### Базовые (всегда)
1. БЭКАП: Перед Edit/Write — копия в backups/ с датой (YYYYMMDD_HHMMSS)
2. ТЕСТЫ: MagicMock(spec=RealClass), не голый MagicMock()
3. DATACLASS: Сверить все .field с @dataclass определением

### Aiogram-специфичные
4. AIOGRAM: Command() хэндлеры ВЫШЕ F.text catch-all (EXP-053)
5. ASYNC: Нет time.sleep/requests.get в async — только aiohttp/asyncio.sleep (EXP-035)
6. HTML: html.escape() на пользовательский ввод перед Telegram HTML
7. CALLBACK: Каждый CallbackQuery handler → callback.answer()
8. DI: Нет bot["key"] — использовать middleware DI (aiogram 3.25+)

### Безопасность
9. ENV: API-ключи и токены ТОЛЬКО в .env, НИКОГДА в коде
10. GITIGNORE: .env, credentials.json, *.pem — в .gitignore

### Верификация
11. ИМПОРТ: python -c "import module" — без ошибок
12. ТЕСТЫ: pytest -x — все тесты зелёные
13. ЛИНТ: Нет SyntaxError, IndentationError
```

---

## Как использовать

### В промпте Task tool:

```python
# Пример делегации с правилами:
Task(
    description="Fix callback handlers",
    prompt="""
    Исправь callback handlers в bot/handlers/callback.py.

    ## Обязательные правила для субагента
    1. БЭКАП: Перед Edit/Write — копия в backups/
    2. ТЕСТЫ: MagicMock(spec=RealClass)
    3. CALLBACK: Каждый CallbackQuery handler → callback.answer()
    4. ВЕРИФИКАЦИЯ: pytest -x после изменений
    """,
    subagent_type="general-purpose",
    mode="bypassPermissions"
)
```

### Копируй блок правил в каждый промпт субагента:

1. Определи какие правила релевантны задаче
2. Минимум — 8 базовых правил (всегда)
3. Для aiogram — добавь aiogram-специфичные
4. Для деплоя — добавь безопасность
5. Вставь блок правил В НАЧАЛО промпта субагента

---

## Почему это важно

**Проблема (WARN-006):** Субагенты запускаются в чистом контексте. Они не знают про:
- Engineering Advisor и его правила
- Накопленный опыт (experience/)
- Конвенции проекта (CLAUDE.md)
- Предыдущие ошибки и фиксы

**Без правил субагент:**
- ❌ Не делает бэкапы → потеря кода при ошибке
- ❌ Использует MagicMock() без spec → тесты зелёные, прод красный
- ❌ Ставит F.text до Command() → команды молча не работают
- ❌ Пишет time.sleep() в async → бот замирает для всех

**С правилами субагент:**
- ✅ Делает бэкап перед каждым изменением
- ✅ Пишет правильные тесты с spec=
- ✅ Соблюдает порядок хэндлеров
- ✅ Использует async-альтернативы

---

## Связанные записи опыта

| Запись | Урок |
|--------|------|
| WARN-006 | Субагенты не наследуют контекст скиллов |
| WARN-005 | Бэкап ПЕРЕД редактированием, не после |
| WARN-002 | MagicMock без spec скрывает баги |
| EXP-053 | F.text catch-all перехватывает команды |
| EXP-035 | 92 пропущенных await в async-миграции |
| EXP-040 | result.text вместо result.transcription |
