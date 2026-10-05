# Quick Start: Deploy за 30 минут

**Цель:** С нуля до работающего приложения на Yandex Cloud за 30 минут

**Что получим:**
- Аккаунт Yandex Cloud
- Установленный CLI
- Первый Cloud Function (REST API)
- PostgreSQL база данных
- Public URL для тестирования

**Требования:**
- Аккаунт в Яндексе (Yandex ID)
- Банковская карта (для billing account)
- Терминал (Bash/PowerShell)

---

## Шаг 1: Регистрация в Yandex Cloud (5 минут)

### 1.1. Создание аккаунта

```bash
# 1. Перейти на https://cloud.yandex.ru
# 2. Нажать "Попробовать бесплатно"
# 3. Войти через Яндекс ID (или создать новый)
```

### 1.2. Создание Billing Account

```bash
# 4. Привязать банковскую карту
# 5. Указать тип плательщика (физлицо/ИП/компания)
# 6. Заполнить данные для счетов
```

**Бонусы при регистрации (2026):**
- 4000₽ на 60 дней (пробный период)
- После окончания пробного периода - pay-as-you-go

**Важно:** Карта НЕ списывается до окончания пробного периода.

### 1.3. Создание первого Cloud

```bash
# 7. В консоли нажать "Создать cloud"
# 8. Имя: "tourism-cloud"
# 9. Organization: создать новую или выбрать существующую
```

**Cloud** - это логический контейнер для всех ресурсов.

### 1.4. Создание Folder

```bash
# 10. Внутри cloud создать folder: "tourism-dev"
```

**Folder** - это логическая группировка ресурсов внутри cloud (аналог AWS account).

---

## Шаг 2: Установка Yandex Cloud CLI (5 минут)

### 2.1. Linux/macOS

```bash
# Скачивание и установка
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

# Перезагрузить shell или выполнить
exec -l $SHELL

# Проверка версии
yc version
```

### 2.2. Windows (PowerShell от имени администратора)

```powershell
# Скачивание и установка
iex (New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1')

# Проверка версии
yc version
```

### 2.3. Альтернативный способ (Docker)

```bash
# Если не хочется устанавливать локально
docker run -it --rm \
  -v ~/.config/yandex-cloud:/root/.config/yandex-cloud \
  cr.yandex/yc/cli:latest \
  yc version
```

### 2.4. Инициализация CLI

```bash
# Запустить интерактивную настройку
yc init

# Вам предложат:
# 1. Получить OAuth токен (откроется браузер)
# 2. Выбрать cloud
# 3. Выбрать folder
# 4. Выбрать compute zone (ru-central1-a рекомендуется)
```

**Вывод после успешной инициализации:**

```
Your current folder has been set to 'tourism-dev' (b1g...)
Your current cloud has been set to 'tourism-cloud' (b1g...)
Your current compute zone has been set to 'ru-central1-a'
```

### 2.5. Проверка конфигурации

```bash
# Посмотреть текущий профиль
yc config list

# Вывод:
# token: AQA...
# cloud-id: b1g...
# folder-id: b1g...
# compute-default-zone: ru-central1-a
```

---

## Шаг 3: Создание Service Account (3 минуты)

Service Account - это специальный аккаунт для приложений (не для людей).

### 3.1. Создание Service Account

```bash
# Создать service account
yc iam service-account create \
  --name tourism-sa \
  --description "Service account for tourism apps"

# Получить ID service account
SA_ID=$(yc iam service-account get tourism-sa --format json | jq -r '.id')
echo $SA_ID
```

### 3.2. Назначение роли

```bash
# Получить ID текущего folder
FOLDER_ID=$(yc config get folder-id)

# Назначить роль editor (полные права в folder)
yc resource-manager folder add-access-binding $FOLDER_ID \
  --role editor \
  --subject serviceAccount:$SA_ID
```

**Роли:**
- `viewer` - только чтение
- `editor` - чтение и запись
- `admin` - полный контроль

### 3.3. Создание API ключа

```bash
# Создать API ключ
yc iam api-key create \
  --service-account-name tourism-sa \
  --description "API key for Cloud Functions" \
  --format json > api-key.json

# Посмотреть ключ
cat api-key.json

# Сохранить ключ в переменную
API_KEY=$(jq -r '.secret' api-key.json)
```

**ВАЖНО:** Сохраните api-key.json в надежном месте. Ключ показывается только один раз.

---

## Шаг 4: Первый Cloud Function (7 минут)

### 4.1. Создать простую функцию

```bash
# Создать директорию для функции
mkdir hello-function
cd hello-function

# Создать index.js
cat > index.js << 'EOF'
module.exports.handler = async (event, context) => {
  // Логируем входящий запрос
  console.log('Event:', JSON.stringify(event));

  // Получаем query параметры
  const name = event.queryStringParameters?.name || 'Guest';

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: `Hello, ${name}!`,
      timestamp: new Date().toISOString(),
      requestId: context.requestId
    })
  };
};
EOF
```

### 4.2. Deploy функции

```bash
# Создать функцию в облаке
yc serverless function create \
  --name hello-tourism

# Загрузить код и создать версию
yc serverless function version create \
  --function-name hello-tourism \
  --runtime nodejs18 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 3s \
  --source-path .
```

**Параметры:**
- `runtime` - Node.js 18 (также доступны: nodejs20, python311, python312, go121, java17, etc.)
- `entrypoint` - точка входа (файл.функция)
- `memory` - от 128MB до 4GB
- `execution-timeout` - макс время выполнения (до 10 минут)

### 4.3. Сделать функцию публичной

```bash
# Разрешить вызов без аутентификации
yc serverless function allow-unauthenticated-invoke hello-tourism

# Получить public URL
FUNCTION_URL=$(yc serverless function get hello-tourism --format json | jq -r '.http_invoke_url')
echo "Function URL: $FUNCTION_URL"
```

### 4.4. Тестирование

```bash
# Простой запрос
curl "$FUNCTION_URL"

# Вывод:
# {"message":"Hello, Guest!","timestamp":"2026-02-05T10:30:00.000Z","requestId":"abc123"}

# С параметром
curl "$FUNCTION_URL?name=Sukheil"

# Вывод:
# {"message":"Hello, Sukheil!","timestamp":"2026-02-05T10:30:00.000Z","requestId":"def456"}
```

### 4.5. Посмотреть логи

```bash
# Получить ID последней версии функции
VERSION_ID=$(yc serverless function version list --function-name hello-tourism --limit 1 --format json | jq -r '.[0].id')

# Посмотреть логи
yc logging read --resource-ids=$VERSION_ID

# Вывод:
# 2026-02-05 10:30:00  INFO  START RequestId: abc123
# 2026-02-05 10:30:00  INFO  Event: {"queryStringParameters":{"name":"Sukheil"}}
# 2026-02-05 10:30:00  INFO  END RequestId: abc123
```

---

## Шаг 5: Добавление PostgreSQL (10 минут)

### 5.1. Получить ID подсети

```bash
# Список сетей
yc vpc network list

# Если нет сети, создать
yc vpc network create --name tourism-network

# Список подсетей
yc vpc subnet list

# Если нет подсети, создать
yc vpc subnet create \
  --name tourism-subnet-a \
  --network-name tourism-network \
  --zone ru-central1-a \
  --range 10.1.0.0/24

# Получить ID подсети
SUBNET_ID=$(yc vpc subnet get tourism-subnet-a --format json | jq -r '.id')
echo $SUBNET_ID
```

### 5.2. Создать PostgreSQL кластер

```bash
# Создать кластер (займет 3-5 минут)
yc managed-postgresql cluster create \
  --name tourism-db \
  --environment production \
  --network-name tourism-network \
  --host zone-id=ru-central1-a,subnet-id=$SUBNET_ID \
  --postgresql-version 15 \
  --resource-preset s2.micro \
  --disk-type network-ssd \
  --disk-size 10 \
  --backup-window-start time=03:00,tz=UTC
```

**Параметры:**
- `environment` - production или prestable
- `resource-preset` - тип инстанса (s2.micro = 2 vCPU, 8GB RAM)
- `disk-type` - network-ssd или network-hdd
- `disk-size` - размер в GB (минимум 10GB)
- `backup-window-start` - время для автоматических backup

**Доступные presets:**

| Preset | vCPU | RAM | Цена/месяц |
|--------|------|-----|------------|
| s2.micro | 2 | 8GB | ~8,000₽ |
| s2.small | 4 | 16GB | ~16,000₽ |
| s2.medium | 8 | 32GB | ~32,000₽ |

### 5.3. Создать базу данных

```bash
# Создать БД
yc managed-postgresql database create tourism \
  --cluster-name tourism-db \
  --owner postgres

# Проверить
yc managed-postgresql database list --cluster-name tourism-db
```

### 5.4. Создать пользователя

```bash
# Создать пользователя приложения
yc managed-postgresql user create app_user \
  --cluster-name tourism-db \
  --password 'MySecurePassword123!' \
  --permissions tourism

# Проверить
yc managed-postgresql user list --cluster-name tourism-db
```

### 5.5. Получить connection string

```bash
# Получить хосты кластера
yc managed-postgresql cluster list-hosts tourism-db

# Вывод:
# +-------------------+-------+------+--------+--------+
# |       NAME        | ROLE  | ZONE | HEALTH | SUBNET |
# +-------------------+-------+------+--------+--------+
# | rc1a-abc123...    | MASTER| a    | ALIVE  | ...    |
# +-------------------+-------+------+--------+--------+

# Connection string
HOST=$(yc managed-postgresql cluster list-hosts tourism-db --format json | jq -r '.[0].name')
echo "Host: $HOST"

# Формат подключения
echo "postgresql://app_user:MySecurePassword123!@$HOST:6432/tourism"
```

**Порт 6432** - это connection pooler (Odyssey). Порт 6432 рекомендуется вместо 5432.

### 5.6. Подключиться и создать таблицу

```bash
# Установить psql (если нет)
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Windows
# Скачать с https://www.postgresql.org/download/windows/

# Подключиться
psql "postgresql://app_user:MySecurePassword123!@$HOST:6432/tourism?sslmode=require"

# В psql создать таблицу
CREATE TABLE tours (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  duration_hours INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Вставить тестовые данные
INSERT INTO tours (name, description, price, duration_hours) VALUES
  ('Desert Safari', 'Exciting desert adventure with dune bashing', 250.00, 6),
  ('Dubai City Tour', 'Explore iconic landmarks of Dubai', 150.00, 4),
  ('Burj Khalifa Tour', 'Visit the tallest building in the world', 180.00, 2);

# Проверить
SELECT * FROM tours;

# Выход
\q
```

---

## Шаг 6: Подключение функции к БД (5 минут)

### 6.1. Обновить код функции

```bash
cd hello-function

# Создать package.json
cat > package.json << 'EOF'
{
  "name": "hello-tourism",
  "version": "1.0.0",
  "dependencies": {
    "pg": "^8.11.3"
  }
}
EOF

# Установить зависимости локально (для разработки)
npm install

# Обновить index.js
cat > index.js << 'EOF'
const { Pool } = require('pg');

// Connection pool (создается один раз при cold start)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

module.exports.handler = async (event, context) => {
  try {
    // Получить все туры
    const result = await pool.query('SELECT * FROM tours ORDER BY id');

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tours: result.rows,
        count: result.rowCount
      })
    };
  } catch (error) {
    console.error('Database error:', error);

    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: 'Database error',
        message: error.message
      })
    };
  }
};
EOF
```

### 6.2. Deploy с environment variables

```bash
# Получить connection string
HOST=$(yc managed-postgresql cluster list-hosts tourism-db --format json | jq -r '.[0].name')
DATABASE_URL="postgresql://app_user:MySecurePassword123!@$HOST:6432/tourism?sslmode=require"

# Deploy новой версии с environment variable
yc serverless function version create \
  --function-name hello-tourism \
  --runtime nodejs18 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 5s \
  --source-path . \
  --environment DATABASE_URL="$DATABASE_URL"
```

### 6.3. Тестирование

```bash
# Получить URL функции
FUNCTION_URL=$(yc serverless function get hello-tourism --format json | jq -r '.http_invoke_url')

# Запросить список туров
curl "$FUNCTION_URL"

# Вывод:
# {
#   "tours": [
#     {"id":1,"name":"Desert Safari","description":"Exciting desert adventure...","price":"250.00","duration_hours":6,"created_at":"2026-02-05T10:35:00.000Z"},
#     {"id":2,"name":"Dubai City Tour","description":"Explore iconic landmarks...","price":"150.00","duration_hours":4,"created_at":"2026-02-05T10:35:00.000Z"},
#     {"id":3,"name":"Burj Khalifa Tour","description":"Visit the tallest building...","price":"180.00","duration_hours":2,"created_at":"2026-02-05T10:35:00.000Z"}
#   ],
#   "count": 3
# }
```

---

## Что мы получили

1. **Working REST API** на Yandex Cloud Functions
2. **PostgreSQL база данных** с managed backups
3. **Public URL** для доступа к API
4. **Автоматический scaling** (functions масштабируются под нагрузку)
5. **Мониторинг** и логи через Yandex Cloud Console

## Стоимость этой инфраструктуры

**Cloud Function:**
- Free tier: 1M invocations/month (хватит на старте)
- После free tier: ~50₽/месяц (10k requests)

**PostgreSQL (s2.micro):**
- ~8,000₽/месяц
- Включает automatic backups

**Итого:** ~8,050₽/месяц (~$85 по курсу 2026)

## Следующие шаги

### Добавить больше endpoints

```javascript
// В index.js добавить роутинг
module.exports.handler = async (event, context) => {
  const path = event.url;
  const method = event.httpMethod;

  // GET /tours - список туров
  if (method === 'GET' && path === '/tours') {
    return await getTours();
  }

  // GET /tours/:id - один тур
  if (method === 'GET' && path.startsWith('/tours/')) {
    const id = path.split('/')[2];
    return await getTour(id);
  }

  // POST /bookings - создать бронирование
  if (method === 'POST' && path === '/bookings') {
    const body = JSON.parse(event.body);
    return await createBooking(body);
  }

  return { statusCode: 404, body: 'Not Found' };
};
```

### Добавить API Gateway

Вместо одной функции с роутингом - использовать API Gateway:

```yaml
# api-gateway.yaml
openapi: 3.0.0
info:
  title: Tourism API
  version: 1.0.0

paths:
  /tours:
    get:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: <FUNCTION_ID>
  /tours/{id}:
    get:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: <FUNCTION_ID>
```

### Добавить Object Storage для фото

```bash
# Создать бакет
yc storage bucket create tourism-photos

# Настроить public access
yc storage bucket update tourism-photos --public-read
```

## Troubleshooting

### Функция не запускается

```bash
# Посмотреть логи последних вызовов
yc serverless function logs hello-tourism

# Посмотреть детали функции
yc serverless function get hello-tourism

# Посмотреть все версии
yc serverless function version list --function-name hello-tourism
```

### Не могу подключиться к PostgreSQL

```bash
# Проверить статус кластера
yc managed-postgresql cluster get tourism-db

# Проверить хосты
yc managed-postgresql cluster list-hosts tourism-db

# Проверить Security Groups (firewall)
yc vpc security-group list
```

### Ошибка "Access Denied"

```bash
# Проверить роли service account
yc iam service-account list-access-bindings tourism-sa

# Добавить недостающие роли
yc resource-manager folder add-access-binding $(yc config get folder-id) \
  --role serverless.functions.invoker \
  --subject serviceAccount:$SA_ID
```

## Чистка ресурсов

Если нужно удалить все созданное:

```bash
# Удалить функцию
yc serverless function delete hello-tourism

# Удалить PostgreSQL кластер
yc managed-postgresql cluster delete tourism-db

# Удалить подсеть
yc vpc subnet delete tourism-subnet-a

# Удалить сеть
yc vpc network delete tourism-network

# Удалить service account
yc iam service-account delete tourism-sa
```

---

**Время выполнения:** ~30 минут
**Сложность:** Beginner
**Следующий шаг:** `references/serverless-functions.md` (углубленное изучение Cloud Functions)
