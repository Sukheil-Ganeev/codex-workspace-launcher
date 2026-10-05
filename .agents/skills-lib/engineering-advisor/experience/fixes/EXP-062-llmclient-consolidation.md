# EXP-062: Консолидация LLMClient — единый AI-клиент через DI

**Тип:** fix
**Severity:** high
**Проект:** VoiceTranscriptionBot
**Дата:** 2026-02-28

## Проблема

5 модулей создавали собственный `genai.Client()` при каждом вызове, обходя shared LLMClient из DI-контейнера. Один модуль (`accounting.py`) содержал threading-баг: синхронные Gemini-вызовы блокировали event loop.

## Корневая причина

Исторически модули писались до создания `LLMClient`. При добавлении нового кода — копипаста из старых модулей вместо использования DI. Нет линтера/проверки на прямое создание `genai.Client()`.

## Решение

**Phase B** — все 5 модулей рефакторены на `services.llm.generate()` или `services.llm.generate_with_image()`. Ноль собственных клиентов. Для Vision-задач (OCR чеков) добавлен `generate_with_image()` в LLMClient, использующий `PIL.Image` напрямую в Gemini `contents[]`.

## Правило

**Анти-паттерн: НИКОГДА не создавай `genai.Client()` внутри бизнес-логики.** Используй DI-контейнер singleton (`services.llm`).

```python
# ПРАВИЛЬНО: через DI
from core.services import services
result = await services.llm.generate(prompt, task_type=TaskType.CLASSIFICATION)

# НЕПРАВИЛЬНО: собственный клиент
from google import genai
client = genai.Client(api_key=config.GEMINI_API_KEY)  # утечка ресурсов, нет retry
response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
```

## Ключевой инсайт по Vision

Для обработки изображений (OCR чеков, фото) — передавай `PIL.Image` напрямую в `contents[]`. Это проще чем `client.files.upload()` и работает для типичных фото с телефона (<10 MB).

```python
# generate_with_image() — PIL.Image в contents
contents = [prompt_text, pil_image]  # Gemini принимает PIL напрямую
```

## Чек-лист

- [ ] Grep по проекту: `genai.Client(` должен встречаться только в `llm_client.py`
- [ ] Все AI-вызовы идут через `services.llm.generate()` или `services.llm.generate_with_image()`
- [ ] Нет синхронных Gemini-вызовов (проверка `await`)
- [ ] При добавлении нового AI-модуля — импорт из services, не создание клиента

## Связанные уроки

- EXP-061: Deprecated model migration (Phase A)
- EXP-063: TaskType routing (Phase C)
