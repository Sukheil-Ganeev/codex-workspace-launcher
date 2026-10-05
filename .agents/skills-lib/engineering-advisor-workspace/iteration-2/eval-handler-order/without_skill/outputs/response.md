# Почему /start и /help не работают

## Причина проблемы

Хэндлер `F.text` перехватывает **все** текстовые сообщения, включая команды вроде `/start` и `/help`. Aiogram проверяет хэндлеры в том порядке, в котором они зарегистрированы. Поскольку `handle_text` с фильтром `F.text` стоит **первым**, он срабатывает на `/start` и `/help` раньше, чем дело доходит до специфичных хэндлеров команд.

Команды `/start` и `/help` — это тоже текстовые сообщения (тип `text`), поэтому `F.text` их захватывает.

## Как исправить

Переставить хэндлеры так, чтобы специфичные (команды) шли **раньше** общего (`F.text`):

```python
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

# Сначала — специфичные команды
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Справка по командам...")

# В конце — общий обработчик текста
@router.message(F.text)
async def handle_text(message: Message):
    await message.answer(f"Вы написали: {message.text}")
```

## Альтернатива: исключить команды из F.text

Если по каким-то причинам порядок менять нельзя, можно явно исключить команды из `F.text`:

```python
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

# Только обычный текст, не команды
@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    await message.answer(f"Вы написали: {message.text}")

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Справка по командам...")
```

## Правило на будущее

В aiogram (и большинстве роутер-фреймворков) действует принцип **"первый подошедший хэндлер выигрывает"**. Регистрируй хэндлеры от частного к общему:

1. Сначала точные команды (`Command("start")`, `Command("help")`)
2. Потом специфичные фильтры (конкретный текст, callback data)
3. В самом конце — широкие "catch-all" хэндлеры (`F.text`, `F.photo`)

Первый способ (переставить порядок) — предпочтительный: он чище и не требует хитрых фильтров.
