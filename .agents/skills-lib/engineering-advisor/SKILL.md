---
name: engineering-advisor
description: "Автоматический советник по инженерным практикам. Определяет когда нужны тесты, ревью, рефакторинг. 26 триггеров, severity BLOCK/WARN/INFO, aiogram-чеклист, субагентные правила, Node.js/Fastify/Prisma паттерны. Группы - код, безопасность, деплой, повторные ошибки, сложные задачи, завершение, aiogram боты."
version: 4.1
---
## ПРОТОКОЛ АКТИВАЦИИ (ОБЯЗАТЕЛЬНО)

> **Этот протокол выполняется КАЖДЫЙ РАЗ при активации скилла. Без исключений.**

### При загрузке скилла:

1. **Прочитать** `experience/_index.md` — секцию "Критические уроки (топ-5)"
2. **Объявить команде:**
   > "Engineering Advisor активирован. Загружено N уроков из опыта. Буду проверять код с учётом накопленных ошибок."
3. **Применять уроки** из experience/ к текущей задаче на протяжении всей сессии

### При завершении сессии:

1. **Проверить** — были ли найдены новые баги, паттерны, или улучшения?
2. **Если да** — ОБЯЗАТЕЛЬНО предложить:
   > "Найден новый урок для Engineering Advisor. Записать в опыт? (тип: fix/pattern/warning, severity: critical/high/medium)"
3. **Записать** в соответствующую папку `experience/` по шаблону из `_experience-system/templates/`
4. **Обновить** `experience/_index.md` — добавить запись в общий список и при необходимости обновить топ-5
5. **Вывести итоговый отчёт:**

### Шаблон завершения сессии:

```
=== Engineering Advisor Summary ===
Файлы изменены: N
Триггеры сработали: #X (описание), #Y (описание)
Проверки: N/M пройдено
BLOCK: N — [описание если есть]
WARN: N — [описание если есть]
INFO: N
Опыт применён: EXP-XXX, EXP-YYY
Новый опыт: EXP-ZZZ записан (описание)
===================================
```

### Категории уроков:

| Тип | Когда записывать | Папка |
|-----|-----------------|-------|
| **fix** | Найден и исправлен баг, который скилл должен был поймать | `experience/fixes/` |
| **pattern** | Обнаружен повторяющийся успешный паттерн | `experience/patterns/` |
| **improvement** | Найден лучший способ делать что-то | `experience/improvements/` |
| **warning** | Найден анти-паттерн, который нужно избегать | `experience/warnings/` |

### Автоматические триггеры записи опыта:

- AttributeError на dataclass, MagicMock без spec скрыл баг, функция без тестов вызвала продакшн-ошибку
- Дублирование фильтров в фреймворке, await на синхронной функции, пропущен аргумент при вызове
- Урок из опыта предотвратил баг — увеличить счётчик `times_applied` в записи

### Самообновление:

Скилл Engineering Advisor **живой** — он учится на каждой сессии:
1. Опыт из `experience/` имеет приоритет над общими правилами SKILL.md
2. Если урок из experience/ противоречит SKILL.md — следовать experience/ (он новее)
3. Каждые 10 новых записей — предложить интеграцию лучших уроков в SKILL.md

---

# Engineering Advisor v4.1 -- Инженерный советник для вайб-кодера

## 1. Введение

Этот скилл — твой автоматический инженерный советник. Он определяет ситуации, где инженерные практики спасут от головной боли, и подсказывает что делать — простыми словами, без жаргона.

**Главный принцип: советует, не блокирует.** Ты всегда решаешь сам. Единственное исключение — код с оплатой и безопасностью (там ревью обязательно, точка).

**Этот скилл — маршрутизатор:** обнаруживает ситуацию, объясняет понятным языком и направляет к нужному инструменту (superpowers или другому скиллу). Сам он код не пишет и не тестирует.

---

## 2. Матрица обнаружения

Ядро скилла. 26 сценариев, которые автоматически определяются при работе с кодом.

### Быстрый выбор триггера: 3 вопроса

```
Вопрос 1: Это существующий код или новое?
|
+-- НОВЫЙ КОД / ФАЙЛ
|   +-- Конфиг (.env, config.yaml)?  -->  #11
|   +-- API endpoint (@route)?  -->  #13
|   +-- Первое открытие проекта?  -->  #15
|   +-- Оплата, ключи, пароли, crypto?  -->  #4 (MANDATORY)
|   +-- Telegram-бот (aiogram)?  -->  #19-#22
|   +-- Webhook endpoint?  -->  #23 (MANDATORY)
|   +-- Обычный код  -->  #1 + проверь #3
|
+-- ИЗМЕНЕНИЕ СУЩЕСТВУЮЩЕГО
    +-- Удаляется код/файл?  -->  #14
    +-- Оплата/безопасность?  -->  #4 (MANDATORY)
    +-- Деплой / production?  -->  #5 (MANDATORY)
    +-- Миграция / "с нуля"?  -->  #9
    +-- 3+ файлов?  -->  #10
    +-- Ошибка 3+ раз? (файл --> #2, error --> #8)
    +-- Цикл по данным?  -->  #12
    +-- Монолитный файл >1000 строк?  -->  #22

Вопрос 2: Сколько задач в запросе?
+-- 1 задача  -->  один триггер выше
+-- 2-3 независимые  -->  #6 (параллельные агенты)
+-- 4+ или зависимости  -->  скилл командная-работа

Вопрос 3: Что сказал Claude в конце?
+-- "Готово" без вывода  -->  #7 (верификация)
+-- Есть реальный результат  -->  ОК
```

> **Правило усиления (EXP-023):** 5+ триггеров одновременно — все Advisory -> Recommended, все Recommended -> MANDATORY.

| # | Сигнал | Как определить | Уровень | Действие | Аналогия |
|---|--------|---------------|---------|----------|----------|
| 1 | Создание/правка файлов кода | Write/Edit на .py/.js/.ts/.html/.css/.sql | Advisory | Объяснить что делает код | "Контракт на иностранном языке — сначала прочитай" |
| 2 | 3+ итерации фикса одного файла | Повторные правки одного участка | Advisory | Предложить рефакторинг | "Куртку латаешь третий раз — проще новую" |
| 3 | Функция с бизнес-логикой | price, total, calculate, AED, booking, order, скидка, маржа | Recommended | Добавить тесты | "Калькулятор — сначала проверь что считает правильно" |
| 4 | Оплата/безопасность | payment, token, api_key, secret, HMAC, crypto, wallet, web3 | **MANDATORY** | Ревью + тесты обязательно | "Ключ от офиса не кладут под коврик" |
| 5 | Деплой / Production | deploy, prod, сервер, systemd, nginx, SSL | **MANDATORY** | Сначала план 5-7 шагов | "Джип-сафари без брифинга — группа потеряна в дюнах" |
| 6 | 3+ независимых задач | Перечисление через «и», «плюс», нумерация | Advisory | Параллельные агенты | "4 блюда, 4 повара = 15 минут" |
| 7 | "Готово" без доказательств | "Готово"/"работает" БЕЗ вывода/скриншота | Recommended | Верификация | "Строитель говорит готово — проверь сантехнику" |
| 8 | Петля ошибок | Похожий error 2+ раз | Advisory | Системный дебаг | "Не пей все таблетки — иди к врачу" |
| 9 | Миграция / переписывание | migrate, rewrite, refactor, "с нуля" | Recommended | Сначала план | "Смена системы бронирований без проверки = потерянные заказы" |
| 10 | Новая фича в 3+ файлах | Функциональность затрагивает 3+ файлов | Recommended | План: файлы + изменения + тесты | "Пристройка — сначала чертёж" |
| 11 | .env / конфиг-файлы | .env, config.yaml, settings.json, credentials | Recommended | Проверить gitignore, секреты | "GPS: тренировочный маршрут != реальный для клиентов" |
| 12 | Циклы по большим данным / N+1 | SELECT в цикле, API в итерации | Advisory | Батчинг или JOIN | "100 звонков -> 1 групповой WhatsApp" |
| 13 | Создание API endpoint | @app.route, router.get/post | Recommended | Авторизация + валидация + rate limit | "Новое окошко в кассе — сначала турникет" |
| 14 | Удаление кода / файлов | delete, rm, DROP TABLE | Advisory | Проверить зависимости + бэкап | "Снос виллы — сначала проверь что жильцы съехали" |
| 15 | Первый запуск в новом проекте | "объясни структуру", новый репозиторий | Advisory | Onboarding checklist | "Новый гид изучает маршрут перед работой" |
| 16 | Новая зависимость / пакет | pip install, npm install, новый import | Recommended | requirements.txt + совместимость | "Новый поставщик — сначала договор в базу" |
| 17 | Архитектурный выбор | "как лучше", "какой вариант" | Advisory | 3 варианта с плюсами/минусами | "Выбор маршрута — сравни по цене, времени, сложности" |
| 18 | Dataclass/DTO attribute mismatch | result.text вместо result.transcription | **MANDATORY** | Сверить ВСЕ .field с @dataclass | "Адрес с опечаткой — посылка не дойдёт" |
| 19 | Порядок хэндлеров в фреймворке | Catch-all фильтры перехватывают до специфичных (F.text до Command). EXP-053 | Recommended | Проверить порядок регистрации | "Турникеты в метро: 'пропускай всех' перед 'проверяй билет' -- контроль бесполезен" |
| 20 | Блокирующие вызовы в async | time.sleep(), requests.get(), sync DB в async хэндлерах | **MANDATORY** | Заменить на async-альтернативы | "Шлагбаум на автостраде: один остановился -- стоят ВСЕ" |
| 21 | Пропущенный callback.answer() | CallbackQuery handler без .answer() -- спиннер до 30 сек | Advisory | Добавить callback.answer() | "Не класть трубку после звонка -- клиент слышит тишину" |
| 22 | Большой монолитный файл (>1000 строк) | Файл-God Object с 10+ функциями разной ответственности | Advisory | Предложить план разделения на модули | "Магазин где все товары свалены в кучу" |
| 23 | Webhook без верификации подписи | Webhook endpoint без HMAC-SHA256 проверки, или verify-функция определена но не вызвана | **MANDATORY** | Добавить crypto.timingSafeEqual + rawBody | "Дверь с замком, который не заперт" |
| 24 | In-memory коллекции без cleanup | Map/Set для rate-limiting, кэша, сессий — без setInterval cleanup | Recommended | Добавить периодическую очистку (5-60 мин) | "Мусорка без вывоза — через месяц не войти" |
| 25 | findMany + JS агрегация вместо DB | prisma.findMany() → .filter()/.reduce() вместо groupBy/count/aggregate | Recommended | Заменить на DB-level aggregation | "Перебирать полки вручную вместо инвентаризации" |
| 26 | Дублирование утилит между файлами | Одинаковый helper скопирован в 3+ файлов (getFlowInput, formatPrice и т.п.) | Advisory | Извлечь в shared src/utils/ модуль | "Один рецепт — одна карточка, а не 14 копий" |

### Три уровня рекомендаций

- **Advisory** (зелёный) — совет друга. Можешь проигнорировать без последствий.
- **Recommended** (жёлтый) — совет врача. Пропуск создаёт реальный риск. Можешь отложить, но не стоит.
- **MANDATORY** (красный) — техника безопасности. Только оплата, безопасность, блокирующие вызовы в async. Ревью обязательно, без вариантов.

---

## 3. Действия при срабатывании

> Подробные карточки действий для каждого из 22 триггеров вынесены в **references/action-cards.md**.
>
> Каждая карточка содержит: что происходит, что сказать пользователю, готовый промпт для копирования, делегация к superpowers-скиллу.
>
> **Как использовать:** При срабатывании триггера -- найди соответствующую карточку (3.1-3.22) в action-cards.md и следуй инструкции.

---

## 4. Цикл Compound Engineering

Каждый раз когда ты работаешь с кодом, используй этот цикл из 6 шагов:

### Шаг 1: Планируй (30 секунд)
Напиши 3-5 пунктов: что код должен делать. Не как — а что.

### Шаг 2: Работай
Сгенерируй код. Одна функция или один логический блок за раз.

### Шаг 3: Проверяй (1 минута)
Прочитай код, сравни с планом из шага 1. Каждый пункт реализован? Запусти — работает?

**Формат вывода (Severity-Driven Output):**
```
=== Engineering Advisor ===
BLOCK (N): файл:строка -- описание критической проблемы
WARN (N): описание предупреждения
INFO (N): описание рекомендации
Опыт: применено N уроков (EXP-XXX, EXP-YYY)
===========================
```

- **BLOCK** — остановка. Код нельзя использовать пока не исправлено (безопасность, блокирующие вызовы в async)
- **WARN** — предупреждение. Работает, но создаёт риск (MagicMock без spec, пропущенный callback.answer)
- **INFO** — совет. Улучшение качества (разделение файла, оптимизация)

### Шаг 4: Документируй (2 минуты)
Три записи: **Что сделал** (одно предложение), **Почему так** (если нетривиально), **Что ещё нужно** (открытые вопросы). Если был полезный урок — предложи записать в experience.

### Шаг 5: Извлекай уроки
Что получилось? Что сломалось? Что запомнить? Если урок — запиши в experience.

### Шаг 6: Повторяй
Следующий кусок. Снова планируй-работай-проверяй-документируй.

**Compound-эффект:** Каждая проверка делает СЛЕДУЮЩИЙ кусок лучше. Как сложные проценты — маленькие улучшения накапливаются. Через 10 итераций качество кратно выше.

---

## 5. Красные флаги в ответах AI

Фразы, которые означают "я не проверял, но звучит убедительно":

| AI говорит | На самом деле | Что делать |
|-----------|--------------|-----------|
| "should work" / "должно работать" | "Я не проверял" | "Запусти и покажи результат" |
| "probably" / "вероятно" | "Я угадываю" | "Проверь в документации" |
| "seems correct" / "выглядит правильно" | "Я не тестировал" | "Напиши тест" |
| "Great!" / "Готово!" | Преждевременная победа | "Покажи вывод" |
| "just add this line" / "просто добавь" | Может сломать другое | "Не сломает что-то ещё?" |
| "I've fixed the issue" | Возможно создал новую | "Покажи что старое И новое работает" |
| "This is straightforward" | Недооценка сложности | "Покажи за 1 минуту" |

**Правило:** AI отвечает утвердительно без доказательств — он не проверял. Требуй доказательства.

---

## 6. Когда нужна команда

```
Одна задача --> просто сделай, без команды
2-3 связанных --> последовательно, один агент
2-3 независимых --> dispatching-parallel-agents
4+ задач ИЛИ зависимости --> командная-работа (волны, координация)
Сложный проект (исследование + создание + проверка) --> команда с волнами
```

**Независимые** = задача А не нуждается в результате задачи Б. **Зависимые** = каждая следующая нуждается в предыдущей.

Промпты: параллельные -- "Запусти параллельно отдельными агентами"; команда -- "Создай команду: исследователь, разработчик, ревьюер"; сложный проект -- "Используй скилл командная-работа, раздели на волны".

---

## 7. Чек-листы

> 5 практических чек-листов вынесены в **references/checklists.md**:
> 1. Перед вставкой сгенерированного кода
> 2. Перед тем как сказать "готово"
> 3. После третьего фикса одной проблемы
> 4. Перед деплоем на production (НОВЫЙ)
> 5. Перед коммитом / пуш (НОВЫЙ)
>
> Aiogram-специфичный чеклист (10 авто-проверяемых правил): **references/aiogram-checklist.md**

---

## 8. Интеграция с superpowers

Engineering-advisor **обнаруживает** ситуацию. Superpowers-скиллы **выполняют** практику.

| Ситуация | Скилл для делегации | Что он делает |
|----------|-------------------|--------------|
| Нужны тесты | superpowers:test-driven-development | Red-Green-Refactor цикл |
| Баг не уходит | superpowers:systematic-debugging | 4-фазный анализ корневой причины |
| Нужно ревью | superpowers:requesting-code-review | Независимая проверка |
| "Готово" | superpowers:verification-before-completion | Доказательства перед утверждением |
| Много задач | superpowers:dispatching-parallel-agents | Параллельное выполнение |
| Сложный проект | командная-работа | Многоволновая координация |
| План (деплой, миграция, 3+ файлов) | superpowers:writing-plans | Структурированный план |
| .env / конфиг (#11) | superpowers:requesting-code-review | Проверка утечки секретов |
| N+1 / циклы (#12) | superpowers:systematic-debugging | Анализ производительности |
| API endpoint (#13) | superpowers:requesting-code-review + TDD | Безопасность + тесты |
| Удаление (#14) | superpowers:writing-plans | Пошаговый план |
| Новый проект (#15) | superpowers:dispatching-parallel-agents | Параллельное изучение |
| Архитектура (#17) | superpowers:brainstorming | Исследование вариантов |
| Порядок хэндлеров (#19) | superpowers:systematic-debugging | Если команды молча не работают |
| Блокирующие вызовы (#20) | superpowers:systematic-debugging | Поиск всех блокирующих вызовов |
| Пропущенный callback.answer() (#21) | нет | Простая проверка grep |
| Монолитный файл (#22) | superpowers:writing-plans | План разделения на модули |
| Webhook без верификации (#23) | superpowers:requesting-code-review | HMAC-SHA256 + timingSafeEqual + rawBody |
| In-memory без cleanup (#24) | нет | Простая проверка: Map/Set + setInterval |
| findMany + JS агрегация (#25) | superpowers:systematic-debugging | Анализ DB queries + оптимизация |
| Дублирование утилит (#26) | superpowers:writing-plans | План извлечения в shared utils |
| Aiogram-чеклист (все) | references/aiogram-checklist.md | 10 авто-проверяемых правил |

**Как использовать:** При срабатывании триггера -- advisor сам вызывает нужный superpowers-скилл. Если скилл недоступен -- каждая карточка в action-cards.md содержит готовый промпт.

---

## 9. Краткая справочная карточка

| # | Сигнал | Уровень | Действие | Промпт |
|---|--------|---------|----------|--------|
| 1 | Создание/правка файлов | Advisory | Объясни | "Объясни каждую часть простыми словами" |
| 2 | 3+ фикса одного файла | Advisory | Перепиши | "Перепиши с нуля, добавь тесты" |
| 3 | Бизнес-логика (деньги) | Recommended | Тесты | "Тесты: норма, ошибки, граничные случаи" |
| 4 | Оплата / ключи / crypto | **MANDATORY** | Ревью + тесты | "Ревью безопасности, потом тесты" |
| 5 | Деплой / Production | **MANDATORY** | Сначала план | "План деплоя 5-7 шагов + откат" |
| 6 | 3+ независимых задач | Advisory | Параллель | "Параллельно отдельными агентами" |
| 7 | "Готово" без доказательств | Recommended | Проверка | "Запусти и покажи реальный результат" |
| 8 | Петля ошибок | Advisory | Системный дебаг | "Найди корневую причину" |
| 9 | Миграция / переписывание | Recommended | Сначала план | "План из 5-7 шагов" |
| 10 | Фича в 3+ файлах | Recommended | Сначала план | "Список файлов + изменения + тесты" |
| 11 | .env / конфиги | Recommended | Проверь gitignore | ".env в .gitignore? Prod != dev?" |
| 12 | N+1 / циклы по данным | Advisory | Оптимизируй | "Замени N запросов на батчинг/JOIN" |
| 13 | API endpoint | Recommended | Безопасность | "Авторизация + валидация + rate limit" |
| 14 | Удаление кода/файлов | Advisory | Зависимости | "Поиск по проекту + git бэкап" |
| 15 | Новый проект | Advisory | Onboarding | "README + зависимости + структура" |
| 16 | Новая зависимость | Recommended | requirements | "requirements.txt + версия + конфликты" |
| 17 | Архитектурный выбор | Advisory | Варианты | "3 варианта + рекомендация" |
| 18 | Dataclass mismatch | **MANDATORY** | Сверь поля | "Все .field совпадают с @dataclass?" |
| 19 | Порядок хэндлеров | Recommended | Проверь порядок | "Command() до F.text catch-all" |
| 20 | Блокирующие вызовы в async | **MANDATORY** | Замени на async | "time.sleep->asyncio.sleep, requests->aiohttp" |
| 21 | Пропущенный callback.answer() | Advisory | Добавь .answer() | "callback.answer() в каждом CallbackQuery handler" |
| 22 | Монолитный файл >1000 строк | Advisory | План разделения | "Разделить на модули по ответственности" |
| 23 | Webhook без верификации | **MANDATORY** | HMAC + timingSafeEqual | "crypto.timingSafeEqual + rawBody" |
| 24 | In-memory без cleanup | Recommended | setInterval очистка | "Добавь cleanup каждые N минут" |
| 25 | findMany + JS агрегация | Recommended | DB aggregation | "groupBy/count вместо filter/reduce" |
| 26 | Дублирование утилит | Advisory | Extract to utils/ | "Общий helper в src/utils/" |

**Мнемоника:** Зелёный — совет друга. Жёлтый — совет врача. Красный — техника безопасности.

---

## 10. Ресурсы

| Ресурс | Путь | Описание |
|--------|------|----------|
| Action Cards | references/action-cards.md | 22 карточки действий для каждого триггера |
| FAQ | references/faq.md | Частые вопросы: "Зачем тесты?", "Как отключить?" |
| Troubleshooting | references/troubleshooting.md | Когда советы замедляют работу |
| Cheatsheet | references/cheatsheet.md | Копируй-вставляй промпты для 22 ситуаций |
| Checklists | references/checklists.md | 5 практических чек-листов |
| Aiogram Checklist | references/aiogram-checklist.md | 10 авто-проверяемых правил для Telegram-ботов |
| Subagent Rules | assets/templates/subagent-rules.md | Шаблон правил для субагентов |
| Experience | experience/_index.md | Накопленные уроки использования скилла |
| Superpowers | obra/superpowers v4.0.x+ | Плагинные скиллы (TDD, debugging, review и др.) |

---

## 11. Шаблон для субагентов

> **Проблема (WARN-006):** Субагенты НЕ наследуют контекст скиллов. Без правил они не делают бэкапы, используют MagicMock без spec=, ставят F.text до Command().

**При каждом Task tool call для делегации кода** -- вставляй блок правил из `assets/templates/subagent-rules.md` в начало промпта субагента.

**Минимальный блок (8 правил для Python):**
```
1. БЭКАП: Перед Edit/Write — копия в backups/ с датой
2. ТЕСТЫ: MagicMock(spec=RealClass), не голый MagicMock()
3. DATACLASS: Сверить все .field с @dataclass определением
4. AIOGRAM: Command() хэндлеры ВЫШЕ F.text catch-all
5. ASYNC: Нет time.sleep/requests.get в async
6. HTML: html.escape() на пользовательский ввод
7. CALLBACK: Каждый CallbackQuery handler -> callback.answer()
8. ВЕРИФИКАЦИЯ: python -c "import module" + pytest
```

**Минимальный блок (10 правил для Node.js/TypeScript/Fastify):**
```
1. WEBHOOK: Всегда ВЫЗЫВАТЬ verify-функцию, не только определять. HMAC-SHA256 + crypto.timingSafeEqual
2. RAWBODY: JSON.stringify(body) != raw bytes. Использовать Fastify rawBody plugin для webhook verification
3. CORS: Никогда origin: true в production. Указывать конкретные домены
4. MIDDLEWARE: Всегда return после reply.code(4xx).send() в preHandler
5. JWT: Никогда default = '' для JWT secrets. Zod schema с .min(1)
6. PRISMA: body as any запрещён. Zod schema перед каждым Prisma вызовом
7. PRISMA INDEX: @@index на всех FK колонках (orderId, customerId, productId)
8. MEMORY: Map/Set для rate-limiting → обязательный setInterval cleanup
9. DB QUERIES: groupBy/count/aggregate вместо findMany + JS filter/reduce
10. ВЕРИФИКАЦИЯ: npx tsc --noEmit + npm test
```

Полный шаблон с расширенными правилами: `assets/templates/subagent-rules.md`

---

## 12. Протокол синхронизации опыта

> **Проблема (EXP-039):** Критические уроки из experience/ не попадают в SKILL.md -- триггеры устаревают.

### Протокол (каждые 10 новых записей):
1. Прочитать все записи с severity=critical за последний месяц
2. Для каждой: есть ли соответствующий триггер в матрице обнаружения?
   - Нет -- добавить новый триггер или расширить существующий
   - Да -- обновить карточку действий в action-cards.md
3. Обновить топ-5 критических уроков в `experience/_index.md`
4. Архивировать записи >180 дней без применений

### Автоматические триггеры синхронизации:
- Новая запись с severity=critical -- немедленная проверка матрицы
- 10+ записей без синхронизации -- предложить обновление
- Новый проект завершён -- review всех уроков проекта

---

## 13. Уроки из аудита abaya-bot (Node.js/TypeScript/Fastify/Prisma)

> **Источник:** Полный аудит кодовой базы abaya-bot (2,607 тестов, 64 файла, 29 сервисов, 7 волн разработки). Дата: 2026-03-02.

### 13.1 Безопасность (Security) -- BLOCK/MANDATORY

| Урок | Проблема | Решение |
|------|----------|---------|
| Verify-функция определена, но не вызвана | `verifyWebhookSignature()` существует в коде, но webhook endpoint не вызывает её | Grep по проекту: каждая `verify*Signature` должна иметь вызов в соответствующем handler |
| BNPL signature = `length > 0` | Stub проверка `signature.length > 0` вместо реального HMAC | Использовать `crypto.createHmac('sha256', secret).update(rawBody).digest('hex')` |
| Timing attack на HMAC | `===` для сравнения подписей уязвимо к timing attacks | `crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b))` |
| `JSON.stringify(body)` != raw bytes | Fastify парсит JSON, stringify не гарантирует исходный порядок ключей | Fastify `rawBody` plugin: `fastify.register(rawBody)`, затем `request.rawBody` |
| CORS `origin: true` | Разрешает запросы с любого домена | `origin: ['https://admin.example.com']` -- whitelist конкретных доменов |
| Missing `return` after error response | `reply.code(401).send({error})` без `return` -- код продолжает выполняться | Всегда `return reply.code(4xx).send()` в preHandler hooks |
| JWT secret default = `''` | `process.env.JWT_SECRET \|\| ''` -- пустой secret принимает любой токен | Zod schema: `z.string().min(32)` для JWT secrets. Crash при старте если не задан |
| Admin API: `body as any` | `prisma.create({ data: request.body as any })` -- SQL injection через Prisma | Zod schema + `.parse(request.body)` перед каждым Prisma вызовом |

### 13.2 Производительность (Performance) -- WARN/Recommended

| Урок | Проблема | Решение |
|------|----------|---------|
| findMany + JS aggregation | `prisma.order.findMany()` + `.filter().reduce()` для подсчёта статистики | `prisma.order.groupBy({ by: ['status'], _count: true })` или `prisma.order.count({ where })` |
| Missing @@index на FK | `Shipment.orderId`, `BnplTransaction.orderId` без индексов | `@@index([orderId])` в schema.prisma на все FK колонки |
| `Array.includes()` в циклах | `VALID_STATES.includes(state)` в hot path -- O(n) каждый раз | `const VALID_STATES = new Set([...])`, затем `VALID_STATES.has(state)` |
| Dead queries in Promise.all | `const [orders, customers, _unused] = await Promise.all([...])` -- `_unused` query всё равно выполняется | Удалить неиспользуемые queries из Promise.all |
| In-memory Map без cleanup | `new Map<string, { count, timestamp }>()` для rate limiting -- растёт бесконечно | `setInterval(() => { map.forEach((v, k) => { if (Date.now() - v.timestamp > TTL) map.delete(k) }) }, 60000)` |
| `await import()` on hot path | Динамический импорт модуля, который уже статически импортирован в другом месте | Использовать статический `import` на top-level. Динамический только для lazy-loading |

### 13.3 Организация кода (Code Organization) -- INFO/Advisory

| Урок | Проблема | Решение |
|------|----------|---------|
| Дублирование helpers в 14+ файлах | `getFlowInput()` скопирован в 14 flow handlers с минимальными вариациями | Один shared helper: `export function getFlowInput(msg, opts?: { lowercase?: boolean })` в `src/utils/flow-helpers.ts` |
| Multi-channel flow duplication | WhatsApp и Instagram flow registries дублируют один и тот же список handlers | Экспортировать `registerAllFlows(machine)` и вызывать из обоих каналов |
| Shared flow handler exports | Flow handlers определены как `function`, не экспортированы | `export function handleGreeting(...)` -- позволяет reuse в разных каналах |

### 13.4 Конфигурация (Configuration) -- WARN/Recommended

| Урок | Проблема | Решение |
|------|----------|---------|
| `.gitignore` неполный | `admin/.next/`, `.claude/worktrees/` не в gitignore | Добавить build artifacts всех подпроектов |
| `.env.example` устарел | Zod schema валидирует 20 env vars, .env.example содержит только 8 | Скрипт: `grep -oP 'z\.string\(\).*?(\w+)' src/config/env.ts` -> сравнить с .env.example |
| ESLint v10+ flat config | `.eslintrc` не работает с ESLint v10+ | `eslint.config.js` (flat config format) |
| Prisma enum != app types | Prisma `Language` enum: `en`, `ar`. Приложение поддерживает `ru` | Синхронизировать: добавить `ru` в Prisma enum + миграция |
| tsconfig rootDir | `rootDir: "src"` но `prisma/seed.ts` вне src/ -- TS ошибка | `rootDir: "."` или отдельный tsconfig для seed |

### 13.5 Тестирование (Testing) -- WARN/Recommended

| Урок | Проблема | Решение |
|------|----------|---------|
| mockResolvedValueOnce chain fragility | Цепочка `.mockResolvedValueOnce(a).mockResolvedValueOnce(b)` ломается если Promise.all переупорядочен | Использовать `.mockImplementation()` с условной логикой, или отдельные mock-объекты |
| bcrypt salt rounds в тестах | `bcrypt.hash(pw, 12)` в тестах -- таймауты в CI | `bcrypt.hash(pw, 4)` в тестовом окружении (env check или test helper) |
| Prisma mock coverage | Сервис использует `aggregate`, `groupBy`, `$transaction` -- но mock setup не включает их | `tests/setup.ts`: добавить mock для всех Prisma методов, используемых в сервисах |

### 13.6 Чеклист для Node.js/Fastify проектов

При создании или ревью Node.js/Fastify/Prisma проекта, пройти по списку:

```
[ ] Webhook endpoints: verify-функция определена И вызывается
[ ] HMAC: crypto.timingSafeEqual, не ===
[ ] rawBody: Fastify rawBody plugin для webhook verification
[ ] CORS: конкретные домены, не origin: true
[ ] JWT secrets: Zod .min(32), crash при пустом
[ ] Admin API: Zod schema на каждый endpoint, не body as any
[ ] Prisma FK: @@index на всех FK колонках
[ ] In-memory Maps: setInterval cleanup
[ ] DB queries: groupBy/count вместо findMany + JS
[ ] .env.example: синхронизирован с Zod env schema
[ ] .gitignore: build artifacts всех подпроектов
[ ] Middleware: return после error response
[ ] Tests: bcrypt salt=4, mock aggregate/groupBy/$transaction
[ ] Утилиты: shared helpers в src/utils/, не дубли
```
