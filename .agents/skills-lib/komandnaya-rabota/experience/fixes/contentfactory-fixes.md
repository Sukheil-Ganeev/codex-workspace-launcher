# ContentFactory — Исправления

## Fix 1: AIAdapter() без аргументов
- **Файл:** bot/main.py:123
- **Проблема:** `ai_adapter = AIAdapter()` — TypeError missing required args
- **Причина:** Агент bot-core не знал про конструктор AIAdapter
- **Решение:** `AIAdapter(gemini_api_key=config.GEMINI_API_KEY, groq_api_key=config.GROQ_API_KEY)`
- **Урок:** В промпте агента указывать точные вызовы конструкторов с аргументами

## Fix 2: Publisher() без аргументов
- **Файл:** bot/main.py:130
- **Проблема:** `publisher = Publisher()` — вместо фабрики create_publisher
- **Причина:** Агент не знал про фабричную функцию
- **Решение:** `publisher = create_publisher(db, bot)`
- **Урок:** Когда есть фабричная функция — указывать её в промпте явно

## Fix 3: seed.py мутация SEED_LESSONS
- **Файл:** core/lessons/seed.py:107
- **Проблема:** `lesson_data.pop("is_pinned")` мутирует глобальный список
- **Причина:** Python передаёт dict по ссылке
- **Решение:** `data = dict(lesson_data)` перед pop
- **Урок:** Тесты обязательны для seed/init функций
