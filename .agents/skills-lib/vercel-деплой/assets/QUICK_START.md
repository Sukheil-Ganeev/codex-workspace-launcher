# Quick Start - Быстрое начало работы

Три сценария быстрого старта для разных задач.

## Сценарий 1: Простой статичный сайт (2 минуты)

```bash
# 1. Создать проект
mkdir my-website && cd my-website

# 2. Скопировать шаблон
cp ~/.claude/skills/vercel-деплой/assets/templates/vercel-static-basic.json ./vercel.json

# 3. Создать index.html
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Мой сайт</title>
</head>
<body>
    <h1>Привет, Vercel!</h1>
</body>
</html>
EOF

# 4. Деплой
vercel --prod
```

Готово! Сайт задеплоен.

---

## Сценарий 2: Использовать готовый пример (30 секунд)

```bash
# Скопировать готовый лендинг
cp -r ~/.claude/skills/vercel-деплой/assets/examples/static-landing ~/my-landing

# Перейти и деплоить
cd ~/my-landing
vercel --prod
```

Готово! Красивый лендинг онлайн.

**Что внутри:**
- Gradient дизайн
- Responsive верстка
- Полностью готов к использованию

---

## Сценарий 3: API endpoint (1 минута)

```bash
# 1. Создать структуру
mkdir -p my-api/api && cd my-api

# 2. Скопировать пример API
cp ~/.claude/skills/vercel-деплой/assets/examples/serverless-api/api/hello.js ./api/

# 3. Скопировать конфиг
cp ~/.claude/skills/vercel-деплой/assets/templates/vercel-static-with-api.json ./vercel.json

# 4. Деплой
vercel --prod
```

Готово! API доступен по адресу:
```
https://your-domain.vercel.app/api/hello
```

Тест:
```bash
curl https://your-domain.vercel.app/api/hello?name=Сухейль
```

---

## Автоматизированная настройка

Для новых проектов используйте скрипт setup:

```bash
cd your-project
bash ~/.claude/skills/vercel-деплой/scripts/setup-vercel.sh
```

Скрипт:
1. Проверит Node.js и Vercel CLI
2. Авторизует в Vercel
3. Предложит выбрать шаблон
4. Настроит проект

---

## Что дальше?

### Кастомизация
Отредактируйте HTML/CSS/JS под свои нужды

### Добавить API
Создайте файлы в папке `api/`:
```bash
mkdir api
echo "export default (req, res) => res.json({ ok: true })" > api/status.js
```

### Environment Variables
```bash
vercel env add MY_SECRET
```

### Просмотр логов
```bash
vercel logs
```

### Локальная разработка
```bash
vercel dev
```

---

## Troubleshooting

**Команда vercel не найдена:**
```bash
npm install -g vercel
```

**Не залогинен:**
```bash
vercel login
```

**Ошибка деплоя:**
```bash
# Проверить конфиг
node ~/.claude/skills/vercel-деплой/scripts/validate-config.js

# Посмотреть логи
vercel logs
```

---

## Полезные ссылки

- [Все шаблоны](./templates/) - Готовые конфигурации
- [Все примеры](./examples/) - Рабочие проекты
- [Документация assets](./README.md) - Подробное описание
- [Документация scripts](../scripts/README.md) - Автоматизация
- [Vercel Docs](https://vercel.com/docs) - Официальная документация
