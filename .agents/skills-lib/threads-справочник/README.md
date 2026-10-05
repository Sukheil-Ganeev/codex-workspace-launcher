# Threads API - Справочник для туристического бизнеса ОАЭ

Production-ready руководство по интеграции Threads API для автоматизации постинга и аналитики.

## Структура справочника

```
threads-справочник/
├── SKILL.md                    # Основной файл с обзором API (~2500 слов)
├── README.md                   # Этот файл
├── references/                 # Детальная документация (6 файлов)
│   ├── api-overview.md
│   ├── posting-text-images.md
│   ├── auto-publish-2025.md
│   ├── instagram-integration.md
│   ├── cross-posting.md
│   └── make-integration.md
├── assets/
│   ├── templates/              # Готовые шаблоны кода
│   │   ├── post-creator.js
│   │   └── cross-poster.js
│   └── examples/               # Полные рабочие примеры
│       ├── auto-posting/
│       └── cross-platform/
├── scripts/                    # Bash/curl скрипты
│   ├── setup-threads-api.sh
│   ├── post-text.sh
│   └── post-image.sh
└── experience/                 # Накопленный опыт
    └── _index.md
```

## Быстрый старт

### 1. Прочитать основы
```bash
# Открыть главный файл
cat SKILL.md
```

### 2. Изучить нужную тему
```bash
# OAuth и авторизация
cat references/instagram-integration.md

# Публикация контента
cat references/posting-text-images.md

# Новинка 2025
cat references/auto-publish-2025.md
```

### 3. Использовать готовый код
```bash
# Скопировать шаблон
cp assets/templates/post-creator.js ~/my-project/

# Запустить пример
cd assets/examples/auto-posting/
npm install
node index.js
```

### 4. Быстрые команды
```bash
# Опубликовать текстовый пост
bash scripts/post-text.sh "Amazing Dubai tour!" USER_ID TOKEN

# Опубликовать с изображением
bash scripts/post-image.sh "https://example.com/photo.jpg" "Caption" USER_ID TOKEN
```

## Ключевые особенности

### Новинка 2025: auto_publish_text
Публикация текста одним запросом (вместо двухшагового процесса)

### Интеграция с Instagram
OAuth через Instagram Business/Creator аккаунт - единый токен для обеих платформ

### Кросс-постинг
Одновременная публикация на Instagram и Threads

### Rate Limits
- 250 постов/24 часа
- ~200 API запросов/час (зависит от Instagram App)

## Применение для туризма ОАЭ

1. **Детальные описания туров** - Threads позволяет 500 символов текста
2. **Истории клиентов** - отзывы и рекомендации
3. **FAQ и советы** - полезная информация для путешественников
4. **Кросс-промо с Instagram** - визуал в IG, детали в Threads

## Примеры кода

Все примеры представлены на 4 языках:
- Node.js (основной)
- Python
- PHP
- Bash (curl)

## Требования

- Instagram Business или Creator аккаунт
- Facebook Page (привязанная к Instagram)
- Threads профиль
- Meta App с Threads API access

## Документация

- **references/** - детальные руководства по каждой теме
- **SKILL.md** - начинайте отсюда для общего понимания
- **experience/_index.md** - критические уроки из практики

## Поддержка

При возникновении проблем:
1. Проверьте Troubleshooting в SKILL.md
2. Изучите соответствующий файл в references/
3. Посмотрите примеры в assets/examples/

## Актуальность

Документация обновлена: **05 февраля 2026**
Включает новинки: **2025-2026 года**

## Лицензия

Для личного и коммерческого использования в туристическом бизнесе ОАЭ.

---

**Автор:** Claude Code Agent
**Версия:** 1.0.0
**Для:** Сухейль - Экскурсии и туризм, Дубай/ОАЭ
