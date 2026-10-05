---
name: puzzlebot-spravochnik-unified
description: "Production-ready справочник по конструктору Telegram-ботов PuzzleBot. Охватывает всё: платформу, конструктор (112 видео-туториалов), и глубокие данные (OCR, транскрипты, community knowledge)."
---
# PuzzleBot Unified Справочник

## Обзор

Объединённый справочник по PuzzleBot -- no-code конструктору Telegram-ботов N1. Три слоя глубины:

| Слой | Директория | Что содержит | Файлов |
|------|-----------|--------------|--------|
| **docs/** | Платформенный справочник | Полный гайд по платформе, тарифы, лимиты, FAQ, troubleshooting, cheatsheet | 4 |
| **learn/** | Обучающий справочник | Полный гайд по конструктору (112 уроков), 12 тематических модулей, видео-индекс, паттерны, готовые сценарии | 17 |
| **deep/** | Глубокий справочник | 30 видео-файлов, 45 транскриптов, 10 OCR интерфейса, карта интерфейса, 3 файла community knowledge | 89 |

**Источники данных:** 112 видеоуроков (YouTube PuzzleBot), 68,659 сообщений сообщества (8,712 Q&A), OCR 3,859 кадров (3 млн символов экранного текста, 164 кнопки, 238 команд). Период: 2024-03 -- 2026-02.

**Платформа:** https://puzzlebot.top | **Документация:** https://docs.puzzlebot.top | **Поддержка:** @HelpMePuzzleBot

---

## Триггеры активации

Активировать этот скилл когда пользователь спрашивает о:

**Платформа и общее:**
- PuzzleBot, пазлбот, puzzlebot.top
- Конструктор ботов, no-code бот, Telegram бот конструктор
- Тарифы PuzzleBot, лимиты, ограничения
- Создание Telegram-бота без кода

**Конструктор и функции:**
- Блоки, команды, условия, формы ввода, действия
- Кнопки (inline, reply, динамические), клавиатуры, кнопки условия
- Переменные, формулы, вычисления, `{{переменная}}`
- Сценарии, автопостинг, таймеры, напоминания
- Мини-приложения (Mini Apps), HTML-блоки, вкладки
- Рассылки, постинг, мультипостинг, сегментация
- Магазин, оплата, Telegram Stars, Prodamus, промокоды
- Группы, каналы, проверка подписки, модерация, бусты
- Геймификация, баллы, лидерборд, чекбоксы

**Интеграции:**
- Google Sheets, NocoDB, Bitrix24, AmoCRM
- ChatGPT / AI в боте, API, Webhooks
- Make (Integromat), n8n, Apix-Drive
- CoinGecko, QR-коды, формирование документов

**Глубокие вопросы:**
- Точное расположение элементов интерфейса, названия кнопок
- Пошаговая инструкция из конкретного видео
- Реальные вопросы и ответы из сообщества
- OCR-данные: какие кнопки есть на экране, точные надписи

**Бизнес-контекст:**
- Бот для туристического бизнеса в ОАЭ (Дубай)
- Мультивалютность (USD, AED, RUB, KZT), мультиязычность
- Программа лояльности, бронирования, каталог экскурсий

---

## Стратегия поиска (3 уровня)

При поступлении вопроса применяй каскадную стратегию. Начинай с уровня, наиболее подходящего по типу вопроса. При недостаточности данных -- спускайся глубже.

### Уровень 1: docs/ -- Платформенный справочник

**Когда искать здесь:**
- Общие вопросы о платформе PuzzleBot (тарифы, регистрация, подключение)
- Быстрый обзор любой темы (блоки, кнопки, переменные, интеграции)
- Лимиты и ограничения платформы
- FAQ по типовым вопросам
- Шпаргалка для быстрого ответа
- Troubleshooting по распространённым проблемам

**Файлы:**

| Файл | Описание |
|------|----------|
| `references/docs/platform-guide.md` | Полный гайд по платформе: обзор, тарифы, быстрый старт, конструктор, переменные, магазин и платежи, постинг, рассылки, события, триггеры, диалоги, интеграции, модерация, аудит, лимиты, применение в туризме ОАЭ, шаблоны |
| `references/docs/faq.md` | Часто задаваемые вопросы по платформе |
| `references/docs/troubleshooting.md` | Решение типичных проблем |
| `references/docs/cheatsheet.md` | Шпаргалка: ключевые формулы, синтаксис, лимиты |

### Уровень 2: learn/ -- Обучающий справочник

**Когда искать здесь:**
- Практические инструкции "как сделать X в PuzzleBot"
- Детальное описание блоков, настроек, действий конструктора
- Синтаксис формул, функций, регулярных выражений
- Конкретные паттерны и сценарии (регистрация, оплата, таймеры, лидерборд)
- Настройка интеграций (Google Sheets, NocoDB, ChatGPT, Bitrix24, Make)
- Мини-приложения: создание, блоки, навигация, HTML-блоки
- Типичные ошибки и решения (10 ошибок с объяснениями)
- Готовые сценарии ботов (такси, знакомства, магазин, обратная связь)

**Файлы:**

| Файл | Описание |
|------|----------|
| `references/learn/full-guide.md` | Полный гайд по конструктору: 112 уроков, все блоки, формы, кнопки, условия, действия, переменные, формулы, интеграции, мини-приложения, оплата, магазин, рассылки, группы, геймификация, паттерны, готовые сценарии, лимиты, FAQ |
| `references/learn/video-index.md` | Индекс 112 видеоуроков: номер, название, тема, привязка к модулю |
| `references/learn/faq.md` | FAQ конструктора: практические вопросы по функциям |
| `references/learn/troubleshooting.md` | Решение проблем конструктора: 10+ типичных ошибок |
| `references/learn/cheatsheet.md` | Шпаргалка конструктора: синтаксис, формулы, команды |

**Тематические модули (references/learn/modules/):**

| Файл | Тема | Ключевое содержание |
|------|------|---------------------|
| `01-basics.md` | Основы | Quick start, архитектура, типы команд, группы, события, ресурсы |
| `02-forms.md` | Формы ввода | Типы ввода, маски, валидация, тестирование, объединение уведомлений |
| `03-buttons-menu.md` | Кнопки и меню | Обычная/инлайн клавиатура, действия кнопок, кнопки условия, проверка подписки |
| `04-variables.md` | Переменные | Персональные, глобальные, stats, интегрированные, формулы, if/else, даты, regex |
| `05-scenarios.md` | Сценарии | Автопостинг, таймеры, напоминания, подписки, зацикливание, дублирование |
| `06-payments.md` | Оплата | Telegram Stars, Prodamus, ЮKassa, кнопка "Платеж", подписки, рекуррентные платежи |
| `07-integrations.md` | Интеграции | Google Sheets, NocoDB, Bitrix24, AmoCRM, ChatGPT, Webhooks, Make, n8n, API |
| `08-mini-apps.md` | Мини-приложения | Создание, блоки, формы, HTML, навигация, popup, поиск, вкладки |
| `09-groups.md` | Группы и каналы | Ресурсы, проверка подписки, капча, приветствия, триггеры, бусты, модерация |
| `10-broadcasts.md` | Рассылки | Постинг, категории, условия, напоминания, Google Sheets, мультипостинг |
| `11-posting.md` | Постинг | Создание постов, черновики, редактирование, расписание, реакции |
| `12-gamification.md` | Геймификация | Баланс, баллы, бонусы, лидерборд, чекбоксы, энергия, доступ за баллы |

### Уровень 3: deep/ -- Глубокий справочник

**Когда искать здесь:**
- Нужны ТОЧНЫЕ детали интерфейса (названия кнопок, поля, надписи, URL)
- Нужна полная пошаговая инструкция из конкретного видео
- Недостаточно данных из docs/ и learn/
- Вопрос о точном расположении элементов на экране
- Нужен контекст из сообщества (реальные вопросы и ответы пользователей)
- Нужна дословная речь из видеоурока (транскрипт)

**Видео-справочники (references/deep/videos/) -- 30 файлов:**

| Файл | Тема | Видео |
|------|------|-------|
| `01-basics-deep-part1.md` | Основы, первые шаги | V10, V23, V24, V26 |
| `01-basics-deep-part2.md` | Основы (продолжение) | V28, V31, V48, V52, V98, V112 |
| `02-forms-deep.md` | Формы ввода | V05, V07, V09, V19, V62 |
| `03-buttons-menu-deep.md` | Кнопки и меню | V06, V08, V14, V18 |
| `04-variables-deep-part1.md` | Переменные и условия | V01, V12, V21, V38 |
| `04-variables-deep-part2.md` | Переменные (статистика, формулы) | V42, V50, V51, V71 |
| `04-variables-deep-part3.md` | Переменные (стандартные, чекбокс) | V78, V105 |
| `05-scenarios-deep-part1.md` | Сценарии | V03, V17, V20, V25 |
| `05-scenarios-deep-part2.md` | Сценарии (такси, напоминания, пароль) | V55, V95, V99, V107 |
| `06-payments-deep-part1.md` | Оплата и магазин | V34, V53, V60, V72 |
| `06-payments-deep-part2.md` | Магазин (обзор, Stars, выдача) | V73, V76, V84, V91 |
| `06-payments-deep-part3.md` | Оплата (доступ, магазин-бот, подписка) | V96, V97, V102, V103 |
| `06-payments-deep-part4.md` | Оплата (прием оплат, Stars+Prodamus) | V110 |
| `07-integrations-deep-part1.md` | Интеграции (API, Google Sheets, Make) | V11, V13, V22, V32, V33, V35, V36 |
| `07-integrations-deep-part2.md` | Интеграции (QR, нейросети, Sheets, Битрикс) | V37, V44, V47, V54, V65 |
| `07-integrations-deep-part3.md` | Интеграции и AI (ChatGPT, NocoDB, Tilda) | V83, V85, V86, V87 |
| `07-integrations-deep-part4.md` | Интеграции (донаты+Make, NocoDB отзывы) | V104, V111 |
| `08-mini-apps-deep-part1.md` | Мини-приложения (основы, поиск, ссылки) | V40, V61, V63, V68, V69 |
| `08-mini-apps-deep-part2.md` | Мини-приложения (меню, модальные, заявки) | V70, V77, V79, V93 |
| `08-mini-apps-deep-part3.md` | Мини-приложения (отправка, конструктор) | V94, V100 |
| `09-groups-deep-part1.md` | Группы и каналы (доступ, заявки) | V02, V41, V43, V46 |
| `09-groups-deep-part2.md` | Группы (подписка, доступ, бизнес-чат) | V56, V80, V88, V89, V101 |
| `09-groups-deep-part3.md` | Группы (бусты, реакции) | V108, V109 |
| `10-broadcasts-deep.md` | Рассылки | V04, V15, V57 |
| `11-posting-deep.md` | Постинг | V29, V74, V81 |
| `12-gamification-deep-part1.md` | Геймификация (баланс, баллы, лидерборд) | V59, V66, V67, V82 |
| `12-gamification-deep-part2.md` | Геймификация (списание, доступ) | V106 |
| `13-special-topics-deep-part1.md` | Модерация и спецтемы (диалоги, настройки) | V16, V27, V30, V39, V45 |
| `13-special-topics-deep-part2.md` | Спецтемы (лид-магнит, админка, обратная связь) | V49, V58, V64, V75 |
| `13-special-topics-deep-part3.md` | Спецтемы (заявки, капча) | V90, V92 |

**OCR -- Элементы интерфейса (references/deep/ocr/) -- 10 файлов:**

| Файл | Раздел интерфейса |
|------|-------------------|
| `ocr-constructor.md` | Конструктор (блоки, кнопки, настройки команд) |
| `ocr-variables.md` | Переменные (персональные, глобальные, интегрированные) |
| `ocr-payments.md` | Оплата (платежные системы, настройки) |
| `ocr-scenarios.md` | Сценарии (автопостинг, настройки) |
| `ocr-shop.md` | Магазин (товары, доставка, промокоды) |
| `ocr-miniapps.md` | Мини-приложения (блоки, настройки) |
| `ocr-posting.md` | Постинг (создание постов, рассылки) |
| `ocr-moderation.md` | Модерация (пользователи, категории) |
| `ocr-settings.md` | Настройки (интеграции, уведомления) |
| `ocr-entrance.md` | Вход и ссылки (многоразовые, промо, реферальные) |

**Дополнительные файлы:**

| Файл | Описание |
|------|----------|
| `references/deep/ocr-interface-map.md` | Полная карта интерфейса PuzzleBot по данным OCR |
| `references/deep/community-knowledge-full-part1a.md` | Community knowledge: вопросы и ответы (часть 1a) |
| `references/deep/community-knowledge-full-part1b.md` | Community knowledge: вопросы и ответы (часть 1b) |
| `references/deep/community-knowledge-full-part2.md` | Community knowledge: вопросы и ответы (часть 2) |

**Транскрипции (references/deep/transcripts/) -- 45 файлов:**

| Файл | Тема | Видео |
|------|------|-------|
| `transcripts-basics-part1.md` | Бот заявок, конструктор | V10, V23, V24 |
| `transcripts-basics-part2.md` | Вход, создание бота, авторизация, дублирование | V26, V28, V31, V48, V52, V98 |
| `transcripts-basics-part3.md` | Форматирование текста | V112 |
| `transcripts-forms-part1.md` | Квиз, регистрация, тест, уведомления | V05, V07, V09, V19 |
| `transcripts-forms-part2.md` | Regex, popup, меню, слайдер инлайн | V62, V06, V14, V18 |
| `transcripts-variables-part1.md` | Приветственный бонус, условия | V01, V12 |
| `transcripts-variables-part2.md` | Переменные, пароль, статистика | V21, V38, V42 |
| `transcripts-variables-part3.md` | Трафик, формулы и выражения | V50, V51, V71 |
| `transcripts-variables-part4.md` | Стандартные переменные, чекбоксы | V78, V105 |
| `transcripts-scenarios-part1.md` | Бот-такси (начало) | V03 |
| `transcripts-scenarios-part2a.md` | Бот-такси (часть 2) | V03 (прод.) |
| `transcripts-scenarios-part2b.md` | Бот-такси (часть 2, окончание) | V03 (прод.) |
| `transcripts-scenarios-part3.md` | Бот-такси (связка) | V03 (прод.) |
| `transcripts-scenarios-part4.md` | Бот-такси (связка) | V03 (прод.) |
| `transcripts-scenarios-part5.md` | Напоминания, сценарии, подписка | V17, V20, V25 |
| `transcripts-scenarios-part6.md` | Бот-такси расширенный (начало) | V55 |
| `transcripts-scenarios-part7a.md` | Бот-такси расширенный (связка) | V55 (прод.) |
| `transcripts-scenarios-part7b.md` | Бот-такси расширенный (связка) | V55 (прод.) |
| `transcripts-scenarios-part8.md` | Бот-такси расширенный (связка) | V55 (прод.) |
| `transcripts-scenarios-part9.md` | Бот-такси расширенный (связка) | V55 (прод.) |
| `transcripts-scenarios-part10.md` | Напоминания в мини-приложении, пароль | V95, V107 |
| `transcripts-payments-part1.md` | Мультивалютный магазин, платный канал, подписка | V34, V53, V60 |
| `transcripts-payments-part2.md` | Магазин (обзор) | V72, V73 |
| `transcripts-payments-part3.md` | Магазин в мини-приложениях, Stars | V76, V84 |
| `transcripts-payments-part4.md` | Подарок за покупку, доступ, магазин одежды | V91, V96, V97 |
| `transcripts-payments-part5.md` | Платная подписка, уник. ссылка, Stars+Prodamus | V102, V103, V110 |
| `transcripts-integrations-part1.md` | Калькулятор TON, Google Sheets, нейросети | V11, V22, V44, V47 |
| `transcripts-integrations-part2.md` | Сбор базы GSheets, Битрикс24, ChatGPT | V54, V65, V83 |
| `transcripts-integrations-part3.md` | AmoCRM, NocoDB, Tilda, донаты+Make | V85, V86, V87, V104 |
| `transcripts-integrations-part4.md` | Форма отзывов + NocoDB | V111 |
| `transcripts-miniapps-part1.md` | Вводный урок, поиск, ссылки, мини-истории | V40, V61, V63, V68 |
| `transcripts-miniapps-part2.md` | Новые функции, StartPayload, модальное окно | V69, V70, V77 |
| `transcripts-miniapps-part3.md` | Обработка заявок, админ мини-приложение | V79, V93, V94 |
| `transcripts-miniapps-part4.md` | Создание мини-приложения (полный обзор) | V100 |
| `transcripts-groups-part1.md` | Pro-доступ за подписку | V02 |
| `transcripts-groups-part2.md` | Заявки на вступление, комментарии, проверка подписки | V41, V43, V46 |
| `transcripts-groups-part3.md` | Проверка нескольких каналов, ограничение мини-приложения | V56, V80 |
| `transcripts-groups-part4.md` | Бизнес-аккаунт, ресурс, триггеры, бусты, реакции, рассылка | V88, V89, V101, V108, V109, V15 |
| `transcripts-groups-part5.md` | Категории и рассылка | V57 |
| `transcripts-other-part1.md` | Постинг, баланс | V29, V74, V81, V59 |
| `transcripts-other-part2.md` | Баллы за активность, ручное начисление, лидерборд | V66, V67, V82 |
| `transcripts-other-part3.md` | Списание баллов, обратная связь, модерация, знакомства | V106, V16, V27, V45 |
| `transcripts-other-part4.md` | Лид-магнит, админка, бот обратной связи | V49, V58, V64 |
| `transcripts-other-part5.md` | Крупное обновление, одобрение заявок | V75, V90 |
| `transcripts-other-part6.md` | Капча для защиты канала | V92 |

**Как найти нужный транскрипт:**
1. Определи тему -- найди номер видео в таблице видео-справочников (выше)
2. Найди файл транскрипта с тем же номером видео в таблице транскриптов
3. Альтернативно: используй `references/learn/video-index.md` для поиска по ключевым словам

---

## Routing по темам (15 тем x 3 слоя)

Для каждой темы указан приоритетный файл в каждом слое. Если данных недостаточно -- переходи к следующему слою.

| N | Тема | docs/ | learn/ | deep/ |
|---|------|-------|--------|-------|
| 1 | **Основы и Quick Start** | `docs/platform-guide.md` (разд. 1-2) | `learn/full-guide.md` (разд. 1-2), `learn/modules/01-basics.md` | `deep/videos/01-basics-deep-part1.md`, `part2` |
| 2 | **Блоки и команды** | `docs/platform-guide.md` (разд. 3) | `learn/full-guide.md` (разд. 3.1), `learn/modules/01-basics.md` | `deep/ocr/ocr-constructor.md` |
| 3 | **Кнопки и клавиатуры** | `docs/platform-guide.md` (разд. 3.2) | `learn/full-guide.md` (разд. 3.2-3.3), `learn/modules/03-buttons-menu.md` | `deep/videos/03-buttons-menu-deep.md`, `deep/ocr/ocr-constructor.md` |
| 4 | **Формы ввода** | `docs/platform-guide.md` (разд. 3.5) | `learn/full-guide.md` (разд. 3.4), `learn/modules/02-forms.md` | `deep/videos/02-forms-deep.md` |
| 5 | **Переменные и формулы** | `docs/platform-guide.md` (разд. 4) | `learn/full-guide.md` (разд. 4), `learn/modules/04-variables.md` | `deep/videos/04-variables-deep-part1.md`...`part3`, `deep/ocr/ocr-variables.md` |
| 6 | **Условия и логика** | `docs/platform-guide.md` (разд. 3.4) | `learn/full-guide.md` (разд. 3.6) | `deep/videos/04-variables-deep-part1.md` |
| 7 | **Сценарии и автоматизация** | `docs/platform-guide.md` (разд. 3.6) | `learn/full-guide.md` (разд. 3.7, 11), `learn/modules/05-scenarios.md` | `deep/videos/05-scenarios-deep-part1.md`, `part2`, `deep/ocr/ocr-scenarios.md` |
| 8 | **Оплата и платежи** | `docs/platform-guide.md` (разд. 5) | `learn/full-guide.md` (разд. 7), `learn/modules/06-payments.md` | `deep/videos/06-payments-deep-part1.md`...`part4`, `deep/ocr/ocr-payments.md` |
| 9 | **Магазин** | `docs/platform-guide.md` (разд. 5.1, 5.3) | `learn/full-guide.md` (разд. 7.2), `learn/modules/06-payments.md` | `deep/videos/06-payments-deep-part2.md`, `deep/ocr/ocr-shop.md` |
| 10 | **Рассылки и постинг** | `docs/platform-guide.md` (разд. 6) | `learn/full-guide.md` (разд. 8), `learn/modules/10-broadcasts.md`, `learn/modules/11-posting.md` | `deep/videos/10-broadcasts-deep.md`, `deep/videos/11-posting-deep.md`, `deep/ocr/ocr-posting.md` |
| 11 | **Интеграции (GSheets, NocoDB, API)** | `docs/platform-guide.md` (разд. 9) | `learn/full-guide.md` (разд. 5), `learn/modules/07-integrations.md` | `deep/videos/07-integrations-deep-part1.md`...`part4`, `deep/ocr/ocr-settings.md` |
| 12 | **Мини-приложения** | `docs/platform-guide.md` (разд. 3.7) | `learn/full-guide.md` (разд. 6), `learn/modules/08-mini-apps.md` | `deep/videos/08-mini-apps-deep-part1.md`...`part3`, `deep/ocr/ocr-miniapps.md` |
| 13 | **Группы, каналы, модерация** | `docs/platform-guide.md` (разд. 8, 10) | `learn/full-guide.md` (разд. 9), `learn/modules/09-groups.md` | `deep/videos/09-groups-deep-part1.md`...`part3`, `deep/ocr/ocr-moderation.md` |
| 14 | **Геймификация и баллы** | -- | `learn/full-guide.md` (разд. 10), `learn/modules/12-gamification.md` | `deep/videos/12-gamification-deep-part1.md`, `part2` |
| 15 | **Спецтемы (диалоги, лид-магнит, капча, админка)** | `docs/platform-guide.md` (разд. 8) | `learn/full-guide.md` (разд. 11) | `deep/videos/13-special-topics-deep-part1.md`...`part3` |

---

## Routing по типам задач (12 типов)

| N | Тип задачи | Пример запроса | Смотреть первым | Смотреть вторым |
|---|------------|----------------|-----------------|-----------------|
| 1 | **Как настроить...** | "Как настроить оплату Stars?" | `learn/modules/` по теме | `deep/videos/` по теме |
| 2 | **Не работает...** | "Не работает Google Sheets при рассылке" | `learn/troubleshooting.md`, `docs/troubleshooting.md` | `deep/community-knowledge-full-*.md` |
| 3 | **Нужен пример...** | "Нужен пример бота-магазина" | `learn/full-guide.md` (Приложение B -- готовые сценарии) | `deep/videos/` по теме |
| 4 | **Какие лимиты...** | "Какие лимиты на рассылки?" | `docs/cheatsheet.md`, `docs/platform-guide.md` (разд. 14) | `learn/cheatsheet.md` |
| 5 | **Какой синтаксис...** | "Какой синтаксис формул?" | `learn/modules/04-variables.md`, `learn/cheatsheet.md` | `docs/cheatsheet.md` |
| 6 | **Где в интерфейсе...** | "Где в интерфейсе настройки NocoDB?" | `deep/ocr/` по теме, `deep/ocr-interface-map.md` | `learn/modules/` по теме |
| 7 | **Сделай бота для...** | "Сделай бота для приема заявок" | `learn/full-guide.md` (Приложение B), `learn/modules/` по теме | `deep/videos/` по теме |
| 8 | **В чём разница...** | "В чём разница обычной и инлайн команды?" | `learn/modules/01-basics.md` | `docs/platform-guide.md` |
| 9 | **Как интегрировать...** | "Как интегрировать ChatGPT?" | `learn/modules/07-integrations.md` | `deep/videos/07-integrations-deep-part3.md` |
| 10 | **Покажи паттерн...** | "Покажи паттерн проверки подписки" | `learn/full-guide.md` (Приложение -- паттерны) | `learn/modules/09-groups.md` |
| 11 | **Что говорили в сообществе...** | "Что говорили о рекуррентных платежах?" | `deep/community-knowledge-full-*.md` | `learn/full-guide.md` (разд. 7.6) |
| 12 | **Пошаговая инструкция из видео...** | "Как делали бота для такси в видео?" | `deep/videos/` по теме | `deep/transcripts/` по теме |

---

## Быстрая справка

### Синтаксис переменных

```
{{ПЕРЕМЕННАЯ}}                    -- вставка значения
{{=выражение}}                    -- формула в тексте
{{=if {{x}} > 5 ; да ; нет}}     -- условие в тексте
{переменная}                      -- формат docs/ (платформенный гайд)
{{FIRST_NAME_TEXT}}               -- имя пользователя
{{USER_ID_TEXT}}                  -- Telegram ID
{{START_PAYLOAD}}                 -- deep link параметр
{{stats.total.users}}             -- встроенная статистика
```

### Ключевые формулы

```
round(число)                          -- округление
random(от, до)                        -- случайное число
plure(число, "день", "дня", "дней")   -- склонение
numberFormat(число, " ", 2)           -- форматирование
ADD_DAYS("дата", N)                   -- прибавить дни
DAYS_BETWEEN("дата1", "дата2")        -- разница в днях
DATE_FORMAT("дата", "d F Y")          -- форматирование даты
match(текст, "/паттерн/флаги")        -- regex: первое совпадение
match_all(текст, "/паттерн/", индекс) -- regex: все совпадения
replace(текст, "что", "на_что")       -- замена в тексте
```

### Типы команд

| Тип | Цвет | Клавиатуры | Поведение |
|-----|------|------------|-----------|
| Обычная | Синий | Обычная + инлайн | Новое сообщение |
| Инлайн | Розовый | Только инлайн | Замена текущего сообщения |

### Лимиты (топ-10)

| Параметр | Лимит |
|----------|-------|
| Telegram: текст | 4096 символов |
| Telegram: caption | 1024 символа |
| Telegram: файл | 50 МБ (фото 10 МБ) |
| Файл через ID `/cp` | до 2 ГБ |
| Inline кнопок в ряду | 8 |
| Медиа в альбоме | 10 |
| Google Sheets | 60 запросов/мин |
| NocoDB | 10 запросов/сек |
| Сценарий (мин. цикл) | 1 минута |
| Мини-приложение: вкладки | до 24 |

### Тарифы

| Тариф | Цена/мес | Боты | Подписчики | Блоки |
|-------|----------|------|------------|-------|
| Бесплатный | 0 | 1 | 150 | 15 |
| Креативный | 990 руб | 2 | 1,000 | 100 |
| Расширенный | 1,690 руб | 4 | 10,000 | 200 |
| Профессиональный | 2,990 руб | 8 | 20,000 | 400 |

Скидка 20% при годовой оплате.

### Платежные системы

| Система | Регион | Особенности |
|---------|--------|-------------|
| Telegram Stars | Весь мир | Подключается одним нажатием |
| Prodamus | Россия, СНГ | URL + секретный ключ |
| ЮKassa | Россия | 2.8-3.5%, карты + SberPay |
| Робокасса | Россия, СНГ | 3-5% |
| CryptoPay | Весь мир | BTC, ETH, USDT, TON |

### Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Платформа | https://puzzlebot.top |
| Документация | https://docs.puzzlebot.top |
| Панель управления | https://cp.puzzlebot.top |
| NocoDB | https://nocodb.puzzlebot.top |
| Поддержка | @HelpMePuzzleBot |
| Сообщество | @LovePuzzleBot |
| Шаблоны | @Sample_PuzzleBot |
| YouTube | youtube.com/@puzzlebot |

---

## QA и Experience

| Ресурс | Путь | Описание |
|--------|------|----------|
| QA-проверки | `references/_qa/` | Результаты проверки качества данных |
| Накопленный опыт | `experience/_index.md` | Критические уроки (11 уроков) -- читать при активации скилла |

**Протокол experience:**
1. При активации -- прочитать `experience/_index.md` (топ-5 уроков).
2. При завершении работы, если был полезный урок -- предложить записать в experience/.
