> Часть 1 из 4. См. также: 07-integrations-deep-part2.md, 07-integrations-deep-part3.md, 07-integrations-deep-part4.md

# 07. Интеграции и AI -- Глубокий справочник

## Video 11: 11_Kalkuljator_TON
**Тема:** Создание калькулятора для расчета суммы криптовалюты TON по текущему курсу через API CoinGecko.
**PuzzleBot-элементы:** Переменные (глобальные интегрированные, персональные с формулой), Формы ввода (число), Маска ввода (число), JSON API интеграция (CoinGecko), Действие "Отправить команду".
**Категория:** Интеграции
**Ключевые техники:**
- Глобальная интегрированная переменная: берет значение (курс TON) со стороннего API через JSON-запрос
- API CoinGecko (бесплатный): получение курса криптовалюты по URL с параметрами
- Персональная переменная-формула: вычисляет результат на основе введенного пользователем значения и курса
- Форма ввода с маской "Число" для корректного получения суммы от пользователя
- Проверка JSON-запроса кнопкой "Проверить запрос" при создании интегрированной переменной
**Шаги реализации:**
1. В команде Start добавить текст и кнопку "Значения"
2. В команде "Значения": форма ввода с текстовым блоком, название для статистики, переменная "USD Value", тип "Отправка сообщения", маска "Число"
3. Перейти на сайт CoinGecko API, в разделе Simple > Simple Price: указать криптовалюту (the-open-network) и валюту (usd), выполнить запрос, скопировать URL
4. Во вкладке "Переменные" создать глобальную интегрированную переменную: название "Price TON", тип "Интегрированный", формат "Число", значение по умолчанию 0
5. Вставить URL JSON-запроса, нажать "Проверить запрос", выбрать нужный ответ с курсом, сохранить
6. Создать персональную переменную-формулу: вписать выражение с участием USD Value и Price TON
7. Создать команду вывода результата с переменной-формулой в текстовом блоке
8. В команде "Значения" добавить действие "Отправить команду" к команде с результатом
9. Опубликовать и проверить
**Полезные детали:**
- URL для CoinGecko API формируется из: `https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd`
- Название криптовалюты берется из URL страницы на CoinGecko (например, "the-open-network")
- Если JSON-запрос возвращает несколько ответов, нужный выбирается в поле "Ответ"
- Глобальная интегрированная переменная обновляется автоматически при каждом обращении

---

### Элементы интерфейса (OCR)
- UI: "Power your applications with CoinGecko's independently sourced crypto data such as live prices, trading volume, exchange volumes, trading pairs,"
- UI: "GET /simple/token_price/{id} Get current price of tokens (using contract addresses) for a given platform in any other currency that you need."
- UI: "/simple/token_price/{id} Get current price of tokens (using contract addresses) for a given platform in any other currency that you need."
- UI: "Our Free API* has a rate limit of 50 calls/minute. Need something more flexible and powerful? View our API plans now."
- UI: "/simple/price Get the current price of any cryptocurrencies in any other supported currencies that you need."
- UI: "Market Cap: $954,824,833,318 4.5% 24h Vol: $77,337,522,701 Dominance: BTC 40.7% ETH 14.5% Gas: 14 GWEI"
- UI: "historical data, contract address data, crypto categories, crypto derivatives, images and more."
- UI: "/coins/{id} Get current data (name, price, market, ... including exchange tickers) for a coin"
- UI: "/coins/markets List all supported coins price, market cap, volume, and market related data"
- UI: "'https://api.coingecko.com/api/v3/simple/price?ids-the-open-network&vs_currencies=usd'\"
- UI: "https://api.coingecko.com/api/v3/simple/price?ids-the-open-network&vs_currencies=usd"
- UI: "/coins/list List all supported coins id, name and symbol (no pagination required)"
- UI: "vs_currency of coins, comma-separated if querying more than 1 vs_currency"
- Поле: "Персональные Глобальные Свернуть / развернуть групп Название переменной:"
- UI: "/simple/supported_vs_currencies Get list of supported_vs_currencies."
- UI: "- Изменение переменных в Формах. Теперь создавать вариативные тесты"
- UI: "стало намного проще! В настройках каждого варианта ответа у Формы"
- UI: "true/false to include last_updated_at of price, default: false"
- Поле: "Глобальные Свернуть / развернуть групп Название переменной:"
- UI: "id of coins, comma-separated if querying more than 1 coin"

---

## Video 13: 13_Baza_Dannyh_Google_Sheets_Integromat
**Тема:** Создание базы данных через Google Sheets с использованием Integromat (Make) для интеграции с Telegram-ботом. Регистрация/авторизация пользователей с проверкой в таблице.
**PuzzleBot-элементы:** Подписки на события (Настройки > Подписки на события), Вебхуки (для связи с Integromat/Make), Google Sheets (как база данных).
**Категория:** Интеграции
**Ключевые техники:**
- Использование Integromat (Make) как связующего звена между PuzzleBot и Google Sheets
- Сценарий в Integromat: Webhooks (Custom webhook) -> Google Sheets (Search Rows) -> Router -> Telegram Bot (Send Message)
- Поиск пользователя в Google Sheets по USER_ID: если найден -- авторизация, если нет -- регистрация (добавление в таблицу)
- Router в Integromat для ветвления: "Пользователь есть" / "Пользователя нет"
- Фильтры на ветках Router для определения маршрута (Label: "Добавление в БД", Condition: Equal to)
- Настройка подписок на события в PuzzleBot для отправки данных в Integromat через webhook
- Структура Google Sheets: USER_ID, USERNAME, NAME, CATEGORY, SOURCE
**Шаги реализации:**
1. Создать Google Sheets таблицу с колонками: USER_ID, USERNAME, NAME, CATEGORY, SOURCE
2. В Integromat (Make) создать сценарий "Рега/авторизация"
3. Добавить модуль Webhooks > Custom webhook, получить URL
4. Добавить модуль Google Sheets > Search Rows, подключить таблицу
5. Добавить Router с двумя ветками: "Пользователя нет" и "Пользователь есть"
6. На ветку "Пользователя нет": добавить Telegram Bot > Send a Text Message (сообщение о регистрации) и Google Sheets > Add a Row
7. На ветку "Пользователь есть": добавить Router > Telegram Bot > Send Message (для разных типов авторизации)
8. Настроить фильтры на ветках Router
9. В PuzzleBot: Настройки > Подписки на события > Добавить подписку на событие > указать URL webhook
10. Включить авторизацию
11. Запустить сценарий в Integromat (Run once), протестировать
**Полезные детали:**
- Транскрипция видео отсутствует (без звука, экранная запись). Информация извлечена из ключевых кадров
- Длительность: 3:20
- На кадрах видна полная цепочка в Integromat: Webhooks -> Google Sheets (Search Rows) -> Router -> Telegram Bot
- Google Sheets используется как простая база данных с полями USER_ID, USERNAME, NAME, CATEGORY, SOURCE
- Подписки на события в PuzzleBot находятся в разделе Настройки (левое меню)
- Integromat = Make (ребрендинг); интерфейс может отличаться

---

### Элементы интерфейса (OCR)
- UI: "Файл Правка Вид Вставка Формат Данные Инструменты Дополнения Справка Последнее изменение: Dev, только что"
- UI: "Файл Правка Вид Вставка Формат Данные Инструменты Дополнения Справка Последнее изменение: только что"
- UI: "14:45 Test has been stopped, but the request has not been processed y"
- UI: "Файл Правка Вид Вставка Формат Данные Инструменты Дополнения Справка"
- UI: "Choose if to send the message silently. iOS users will not receive"
- UI: "Enter the unique identifier for the target chat or username of the"
- UI: "14:45 Test has been stopped, but the request has not been processe"
- UI: "a notification, Android users will receive a notification with no"
- UI: "Telegram apps to show bold, italic, fixed-width text or inline"
- UI: "Подписки на события предназначены для отправки различного рода"
- UI: "Choose if to disable link previews for links in this message."
- UI: "Select Markdown-style or HTML-style of the text, if you want"
- UI: "For more information on how to create a webhook in Webhooks,"
- UI: "14:45 Test has been stopped, but the request has not been |"
- UI: "14:45 Test has been stopped, but the request has not been"
- UI: "https://hook.integromat.com/mkmgqax2twfojncp44gvuie9sam9"
- UI: "данных о сообщениях пользователей, событиях внутри бота."
- UI: "https://hook.integromat.com/mkmgqax2twfojncp4lgvuie9sam9"
- UI: "The fallback route. It will be used in the case where a"
- UI: "ходимо пройти быструю регистрацию и ответить на пару во"

---

## Video 22: 22_Google_Tablica_Registracija
**Тема:** Подключение Google Sheets к PuzzleBot и создание регистрации на мероприятие с проверкой дублей
**PuzzleBot-элементы:** Настройки -> Интеграция -> Google Sheets, действие "Создать строку" (Spreadsheets), системные переменные (User ID Text, User Name Text, First Name Text, Last Name Text, Join Date), условие с проверкой строки, инлайн-клавиатура, команды ("Регистрация", "Есть регистрация")
**Категория:** Интеграции
**Ключевые техники:**
- Подключение Google Sheets: Настройки -> Интеграция -> авторизация через Google-аккаунт (обязательно все галочки)
- Действие "Создать строку": выбор таблицы/листа, маппинг колонок к переменным
- Системные переменные для данных пользователя: User ID Text, User Name Text, First Name Text, Last Name Text, Join Date
- Условие с проверкой строки: поиск по колонке (например, Telegram User ID) для проверки наличия записи
- Исключающее правило в условии: срабатывает, когда основное правило не выполняется
- Защита от повторной регистрации через условие перед командой регистрации
**Шаги реализации:**
1. В настройках бота перейти в Интеграция -> Google Sheets, авторизоваться через Google (поставить все галочки)
2. Создать таблицу в Google Sheets с заголовками колонок (Telegram User ID, Username, Имя, Фамилия, Дата)
3. В Конструкторе в команде "Старт" добавить текст и инлайн-кнопку "Регистрация"
4. В команде "Регистрация" добавить действие "Создать строку": выбрать таблицу, лист, заполнить переменные
5. Добавить текстовый блок с подтверждением регистрации
6. Создать команду "Есть регистрация" с текстом о повторной регистрации
7. Создать условие с двумя правилами:
   - Правило 1: Проверка строки (поиск по User ID) -> если найдено, отправить команду "Есть регистрация"
   - Правило 2 (исключающее): если не найдено, отправить команду "Регистрация"
8. В команде "Старт" изменить кнопку на переход к условию (вместо прямого перехода к регистрации)
9. Опубликовать изменения
**Полезные детали:** Бот записывает данные в таблицу в реальном времени. Обязательно ставить все галочки при авторизации Google-аккаунта. Первая строка таблицы -- заголовки колонок. Условие с исключающим правилом -- стандартный паттерн "если найдено / если не найдено".

---

### Элементы интерфейса (OCR)
- UI: "Адрес вебхука для дублирования запросов Telegram Bot API, подробнее в"
- UI: "Генерация АРІ ключа для отправки запросов, подробнее о работе с АРІ в"
- UI: "Все настройки из данного блока изменяются только через официального"
- UI: "Для работы с Google Таблицами необходимо подключить Google Аккаунт,"
- UI: "Функция, позволяющая подключить группу для совместного управления"
- Кнопка: "• Кнопка-условие - условие, которое определяет настройки инлайн-"
- UI: "• Обычное условие - условие, которое можно вызвать также, как и"
- UI: "команду (по названию, переходом, кнопкой и другими способами)."
- UI: "Перед началом настройки условия необходимо определить его тип:"
- UI: "Вы можете Дублировать бота, Перенести бота или Отвязать бота,"
- UI: "Если ни одно из правил више не было выполнено, то произойдёт"
- UI: "бота @BotFather - Открыть @BotFather или Открыть инструкцию"
- UI: "Правило будет выполнено при соответствии пользователя всем"
- UI: "To continue, Google will share your name, email address,"
- UI: "language preference and profile picture with PuzzleBot."
- UI: "File Edit View Insert Format Data Tools Extensions Help"
- UI: "отображаться таблицы, в которых предоставлен доступ к"
- UI: "Подробная инструкция по работе Условий в Базе Знаний."
- UI: "Важно! Изменить тип Условия после сохранения нельзя."
- UI: "Вы уже за Хотите зарегистрироваться на мероприятие?"

---

## Video 32: 32_Webhook_Integromat_Chast_1
**Тема:** Интеграция PuzzleBot с Integromat (Make) через Webhook -- часть 1
**PuzzleBot-элементы:** Webhook, Integromat (Make)
**Категория:** Интеграции
**Ключевые техники:**
- Транскрипция отсутствует (файл пустой)
**Шаги реализации:**
- Нет данных (транскрипция пуста)
**Полезные детали:** Файл транскрипции пуст (0 байт). Судя по названию, видео показывает настройку вебхука в PuzzleBot и подключение к сервису автоматизации Integromat (ныне Make.com), но без транскрипции детали недоступны. Является первой частью -- предположительно, есть продолжение.

---

### Элементы интерфейса (OCR)
- UI: "Start by clicking here and select the first"
- UI: "Передача данных с secure gravatar.com..."
- UI: "What services do you want to integrate?"
- UI: "Открыть ссылку в новом приватном окне"
- UI: "Исходный код выделенного фрагмента"
- UI: "Integration Webhooks, Telegram Bot"
- UI: "Искать <<https://hook.in Google"
- UI: "Отправить ссылку на устройство"
- UI: "Открыть ссылку в новой вкладке"
- UI: "Открыть ссылку в новом окне"
- Кнопка: "Добавить ссылку в закладки"
- UI: "You can change this later."
- UI: "module for your scenario."
- UI: "Integromat is now liste"
- Кнопка: "Сохранить объект как..."
- UI: "+ Create a new scenario"
- UI: "data structure from thi"
- UI: "this, please send your"
- UI: "© For more informatio"
- UI: "see the online Help."

---

## Video 33: 33_Webhook_Integromat_Chast_2
**Тема:** Транскрипция отсутствует (файл пуст)
**PuzzleBot-элементы:** Неизвестно
**Категория:** Интеграции
**Ключевые техники:**
- Не удалось извлечь (транскрипция пуста)
**Шаги реализации:**
1. Не удалось извлечь
**Полезные детали:** Видео является второй частью серии по интеграции Webhook + Integromat (Make). Для контекста см. часть 1 и часть 3.

---

### Элементы интерфейса (OCR)
- UI: "Подписки на события преднозначены для отправки различного рода"
- UI: "For more information on how to create a webhook in Webhooks,"
- UI: "данных о сообщениях пользователей, событиях внутри бота."
- UI: "s://hook.integromat.com/xpq3vt86n63novu63xsexon1yetuzor"
- UI: "По тарифу Расширенный доступно 13 подписок на события."
- UI: "По тарифу Расширенный доступно 14 подписок на события."
- UI: "Re-determine data structure Copy address to clipboard"
- UI: "https://hook.integromat.com/jmndkifxdytd..."
- UI: "Тип события: Вызов команды из группы команд"
- UI: "tg://resolve?domain=testtt puzzlebot"
- UI: "tg://resolve?domain=testtt_puzzlebo"
- UI: "https://tele.gg/testtt_puzzlebot"
- UI: "Ссылка на открытие в Telegram:"
- UI: "https://t.me/testtt_puzzlebot"
- Кнопка: "Добавить подписку на событие"
- UI: "PuzzleBot :// Личный кабинет"
- UI: "Отлично. Подписка на событие"
- UI: "Show advanced settings"
- UI: "Доступ администраторов"
- UI: "Ссылка альтернативная:"

---

## Video 35: 35_Webhook_Integromat_Chast_3
**Тема:** Транскрипция отсутствует (файл пуст)
**PuzzleBot-элементы:** Неизвестно
**Категория:** Интеграции
**Ключевые техники:**
- Не удалось извлечь (транскрипция пуста)
**Шаги реализации:**
1. Не удалось извлечь
**Полезные детали:** Третья часть серии по интеграции Webhook + Integromat (Make). См. части 1 и 2 для полного контекста.

---

### Элементы интерфейса (OCR)
- UI: "Подписки на события преднозначены для отправки различного рода"
- UI: "А теперь отправь мне секретную фразу, что я тебе передал...."
- UI: "А теперь отправь мне секретную фразу, что я тебе передал..."
- UI: "А теперь отправь мне секретную фразу, что я тебе передал."
- UI: "данных о сообщениях пользователей, событиях внутри бота."
- UI: "По тарифу Расширенный доступно 14 подписок на события."
- UI: "1:53. The request was accepted. Waiting for data."
- UI: "А теперь отправь мне секретную фразу, что я тебе"
- UI: "1:53 The request was accepted. Waiting for data."
- UI: "- Твой выбор: блаженная иллюзия неизвестности."
- UI: "♡ start by clicking here and select the first"
- UI: "ACTIVE SCENARIOS INACTIVE SCENARIOS CONCEPTS"
- UI: "9 To add another module, click the handler"
- UI: "Твой выбор: мучительная правда реальности."
- UI: "type subscribe_event: custom_form_answers"
- UI: "Секретная фраза, что ты мне передал 16:50"
- UI: "Секретная фраза, что ты мне передал 16:53"
- UI: "блака Секретная фраза, что ты мне передал"
- UI: "and the data that the module worked with."
- UI: "To add another module, click the handler"

---

## Video 36: 36_Forma_Vvoda_Integromat_Zakreplenie
**Тема:** Транскрипция отсутствует (файл пуст)
**PuzzleBot-элементы:** Неизвестно
**Категория:** Интеграции
**Ключевые техники:**
- Не удалось извлечь (транскрипция пуста)
**Шаги реализации:**
1. Не удалось извлечь
**Полезные детали:** Закрепляющий урок по формам ввода в связке с Integromat (Make).

---

### Элементы интерфейса (OCR)
- UI: "Send a Text Message or a Reply Select Markdown-style or HTML-style of the text, if you want"
- UI: "Enter the unique identifier for the target chat or username of the"
- UI: "receive a notification, Android users will receive a notification"
- UI: "notification, Android users will receive a notification with no"
- UI: "Enter the unique identifier for the target chat or username of"
- UI: "Telegram apps to show bold, italic, fixed-width text or inline"
- UI: "То самое сообщение, которое необходимо закрепить в чате "Ин..."
- UI: "For more information on how to create a connection to Telegram"
- UI: "Choose if to disable link previews for links in this message."
- UI: "9:23. The request was accepted. Waitir Disable Link Previews"
- UI: "Select Markdown-style or HTML-style of the text, if you want"
- UI: "Пользователь из особой категории Черное Эльмир (@elmir_viv"
- UI: "Choose if to send the message silently. iOS users will not"
- UI: "Пользователь из особой категории Черное Макс (@maxbortnik)"
- UI: "Sends the message silently. iOS users will not receive a"
- UI: "То самое сообщение, которое необходимо закрепить в чате"
- UI: "the target channel (in the format @channelusername, or"
- UI: "Следующее ваше сообщение будет закреплено в чате: 0:23"
- UI: "Следующее ваше сообщение будет закреплено в чате: 0:24"
- UI: "For more information on how to create a connection to"

---

