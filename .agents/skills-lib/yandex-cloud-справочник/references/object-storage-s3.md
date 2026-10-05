# Object Storage (S3-compatible)

**Назначение:** Хранение файлов, изображений, видео, документов и статических ресурсов

**Ключевые особенности:**
- S3-compatible API (работает с AWS SDK)
- Unlimited storage (петабайты данных)
- 99.999999999% durability (11 девяток)
- CDN integration из коробки
- Lifecycle policies для автоматической миграции данных

**Когда использовать:**
- Статические файлы сайта (HTML, CSS, JS, images)
- User-generated content (фото туров, отзывы)
- Backup и архивы
- Video hosting
- Data lake для аналитики

---

## Основы Object Storage

### Bucket (бакет)

Bucket - это контейнер для файлов. Аналог "папки верхнего уровня".

**Правила именования:**
- Уникальное имя глобально (не только в вашем аккаунте)
- 3-63 символа
- Только lowercase буквы, цифры, дефис
- НЕ может начинаться с "xn--" или заканчиваться на "-s3alias"

**Примеры:**
- `tourism-photos` ✓
- `tourism-videos-2026` ✓
- `Tourism-Photos` ✗ (uppercase)
- `a` ✗ (слишком короткое)

### Object (объект)

Object - это файл внутри bucket.

**Key (ключ)** - это полный путь к файлу, например:
- `tours/desert-safari/photo1.jpg`
- `backups/database-2026-02-05.sql.gz`

**Metadata** - дополнительная информация об объекте:
- `Content-Type` (MIME type)
- `Content-Encoding`
- Custom metadata (x-amz-meta-*)

### Storage Classes (классы хранения)

**Standard (стандартный):**
- Частый доступ к файлам
- Цена: 1.93₽/GB/месяц
- Use case: фото туров, видео, активные файлы

**Cold (холодный):**
- Редкий доступ (1-2 раза в месяц)
- Цена: 0.64₽/GB/месяц (66% дешевле)
- Минимальный срок хранения: 30 дней
- Use case: архивы, старые бэкапы

**Ice (ледяной):**
- Очень редкий доступ (1-2 раза в год)
- Цена: 0.40₽/GB/месяц (79% дешевле)
- Минимальный срок хранения: 90 дней
- Use case: compliance архивы, исторические данные

---

## Создание bucket

### Метод 1: Через Console

```
1. https://console.cloud.yandex.ru
2. Object Storage → Create bucket
3. Имя: tourism-photos
4. Storage class: Standard
5. Access: Limited (рекомендуется)
6. Создать
```

### Метод 2: Через yc CLI

```bash
# Создать bucket
yc storage bucket create \
  --name tourism-photos \
  --default-storage-class standard \
  --max-size 107374182400  # 100GB limit (опционально)

# Проверить
yc storage bucket list

# Получить детали bucket
yc storage bucket get tourism-photos
```

### Метод 3: Через AWS CLI

```bash
# Установить AWS CLI
pip install awscli

# Настроить credentials
aws configure
# AWS Access Key ID: <YC_ACCESS_KEY>
# AWS Secret Access Key: <YC_SECRET_KEY>
# Default region name: ru-central1
# Default output format: json

# Создать bucket
aws --endpoint-url=https://storage.yandexcloud.net s3 mb s3://tourism-photos

# Проверить
aws --endpoint-url=https://storage.yandexcloud.net s3 ls
```

### Метод 4: Через API (curl)

```bash
# Создать bucket
curl -X PUT \
  -H "Authorization: Bearer $(yc iam create-token)" \
  https://storage.yandexcloud.net/tourism-photos
```

---

## Работа с файлами

### Загрузка файлов

**AWS CLI:**

```bash
# Загрузить один файл
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp photo.jpg s3://tourism-photos/tours/desert-safari/photo.jpg

# Загрузить директорию рекурсивно
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp ./photos/ s3://tourism-photos/tours/desert-safari/ --recursive

# С метаданными
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp photo.jpg s3://tourism-photos/photo.jpg \
  --content-type image/jpeg \
  --metadata tour=desert-safari,photographer=john
```

**Python (boto3):**

```python
import boto3

# Инициализация клиента
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id='YC_ACCESS_KEY',
    aws_secret_access_key='YC_SECRET_KEY',
    region_name='ru-central1'
)

# Загрузить файл
s3.upload_file(
    Filename='photo.jpg',
    Bucket='tourism-photos',
    Key='tours/desert-safari/photo.jpg',
    ExtraArgs={
        'ContentType': 'image/jpeg',
        'Metadata': {
            'tour': 'desert-safari',
            'photographer': 'john'
        }
    }
)

# Загрузить из памяти
import io
image_bytes = io.BytesIO(b'...')
s3.upload_fileobj(
    Fileobj=image_bytes,
    Bucket='tourism-photos',
    Key='tours/city-tour/photo.jpg'
)
```

**Node.js (AWS SDK):**

```javascript
const AWS = require('aws-sdk');
const fs = require('fs');

// Инициализация клиента
const s3 = new AWS.S3({
    endpoint: 'https://storage.yandexcloud.net',
    accessKeyId: 'YC_ACCESS_KEY',
    secretAccessKey: 'YC_SECRET_KEY',
    region: 'ru-central1',
    s3ForcePathStyle: true
});

// Загрузить файл
const fileContent = fs.readFileSync('photo.jpg');

s3.putObject({
    Bucket: 'tourism-photos',
    Key: 'tours/desert-safari/photo.jpg',
    Body: fileContent,
    ContentType: 'image/jpeg',
    Metadata: {
        'tour': 'desert-safari',
        'photographer': 'john'
    }
}, (err, data) => {
    if (err) console.error(err);
    else console.log('Upload successful:', data);
});

// Multipart upload для больших файлов (>100MB)
const upload = s3.upload({
    Bucket: 'tourism-photos',
    Key: 'videos/desert-safari.mp4',
    Body: fs.createReadStream('video.mp4'),
    ContentType: 'video/mp4'
});

upload.on('httpUploadProgress', (progress) => {
    console.log(`Progress: ${progress.loaded}/${progress.total}`);
});

upload.send((err, data) => {
    if (err) console.error(err);
    else console.log('Upload complete:', data.Location);
});
```

**curl (для простых случаев):**

```bash
# Получить presigned URL через API
PRESIGNED_URL=$(yc storage presigned-url create \
  --bucket tourism-photos \
  --key tours/photo.jpg \
  --method PUT \
  --expires-in 3600)

# Загрузить через presigned URL
curl -X PUT -T photo.jpg "$PRESIGNED_URL"
```

### Скачивание файлов

**AWS CLI:**

```bash
# Скачать один файл
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp s3://tourism-photos/tours/desert-safari/photo.jpg ./photo.jpg

# Скачать директорию
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp s3://tourism-photos/tours/desert-safari/ ./photos/ --recursive
```

**Python:**

```python
# Скачать в файл
s3.download_file(
    Bucket='tourism-photos',
    Key='tours/desert-safari/photo.jpg',
    Filename='photo.jpg'
)

# Скачать в память
import io
buffer = io.BytesIO()
s3.download_fileobj(
    Bucket='tourism-photos',
    Key='tours/desert-safari/photo.jpg',
    Fileobj=buffer
)
buffer.seek(0)
image_bytes = buffer.read()
```

**Node.js:**

```javascript
// Скачать файл
s3.getObject({
    Bucket: 'tourism-photos',
    Key: 'tours/desert-safari/photo.jpg'
}, (err, data) => {
    if (err) console.error(err);
    else {
        fs.writeFileSync('photo.jpg', data.Body);
        console.log('Download successful');
    }
});

// Stream download
const stream = s3.getObject({
    Bucket: 'tourism-photos',
    Key: 'videos/desert-safari.mp4'
}).createReadStream();

stream.pipe(fs.createWriteStream('video.mp4'));
```

### Список файлов

**AWS CLI:**

```bash
# Список всех файлов
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 ls s3://tourism-photos/

# Рекурсивно с размерами
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 ls s3://tourism-photos/tours/ --recursive --human-readable
```

**Python:**

```python
# Список объектов
response = s3.list_objects_v2(
    Bucket='tourism-photos',
    Prefix='tours/desert-safari/'
)

for obj in response.get('Contents', []):
    print(f"{obj['Key']} - {obj['Size']} bytes")

# Пагинация для больших списков
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(
    Bucket='tourism-photos',
    Prefix='tours/'
)

for page in pages:
    for obj in page.get('Contents', []):
        print(obj['Key'])
```

**Node.js:**

```javascript
// Список объектов
s3.listObjectsV2({
    Bucket: 'tourism-photos',
    Prefix: 'tours/desert-safari/'
}, (err, data) => {
    if (err) console.error(err);
    else {
        data.Contents.forEach(obj => {
            console.log(`${obj.Key} - ${obj.Size} bytes`);
        });
    }
});
```

### Удаление файлов

**AWS CLI:**

```bash
# Удалить один файл
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 rm s3://tourism-photos/tours/old-photo.jpg

# Удалить директорию
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 rm s3://tourism-photos/tours/old-tour/ --recursive
```

**Python:**

```python
# Удалить объект
s3.delete_object(
    Bucket='tourism-photos',
    Key='tours/old-photo.jpg'
)

# Удалить много объектов (до 1000 за раз)
s3.delete_objects(
    Bucket='tourism-photos',
    Delete={
        'Objects': [
            {'Key': 'tours/photo1.jpg'},
            {'Key': 'tours/photo2.jpg'},
            {'Key': 'tours/photo3.jpg'}
        ]
    }
)
```

---

## Public access (публичный доступ)

### Сделать bucket публичным

```bash
# Включить public read для всех объектов
yc storage bucket update tourism-photos \
  --public-read

# Теперь файлы доступны по URL:
# https://storage.yandexcloud.net/tourism-photos/tours/photo.jpg
```

### ACL для конкретных объектов

**AWS CLI:**

```bash
# Сделать объект публичным
aws --endpoint-url=https://storage.yandexcloud.net \
  s3api put-object-acl \
  --bucket tourism-photos \
  --key tours/photo.jpg \
  --acl public-read
```

**Python:**

```python
# Public ACL
s3.put_object_acl(
    Bucket='tourism-photos',
    Key='tours/photo.jpg',
    ACL='public-read'
)

# Private ACL (по умолчанию)
s3.put_object_acl(
    Bucket='tourism-photos',
    Key='tours/private-doc.pdf',
    ACL='private'
)
```

### Presigned URLs (временные ссылки)

**Python:**

```python
# Создать presigned URL (валиден 1 час)
url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': 'tourism-photos',
        'Key': 'tours/photo.jpg'
    },
    ExpiresIn=3600  # секунды
)

print(url)
# https://storage.yandexcloud.net/tourism-photos/tours/photo.jpg?...

# Presigned URL для загрузки
upload_url = s3.generate_presigned_url(
    ClientMethod='put_object',
    Params={
        'Bucket': 'tourism-photos',
        'Key': 'tours/new-photo.jpg',
        'ContentType': 'image/jpeg'
    },
    ExpiresIn=3600
)
```

**Node.js:**

```javascript
// Presigned URL для скачивания
const url = s3.getSignedUrl('getObject', {
    Bucket: 'tourism-photos',
    Key: 'tours/photo.jpg',
    Expires: 3600  // секунды
});

console.log(url);
```

**Use case:** Временный доступ к приватным файлам (счета, документы клиентов)

---

## CDN Integration

### Создать CDN resource

```bash
# Создать CDN для bucket
yc cdn resource create \
  --cname photos.tourism-dubai.com \
  --origin-bucket tourism-photos \
  --origin-protocol https \
  --enable-edge-cache

# Настроить DNS
# Добавить CNAME запись:
# photos.tourism-dubai.com → <CDN_DOMAIN>.cdn.yandexcloud.net
```

**Преимущества CDN:**
- Быстрая доставка контента globally
- Кэширование на edge серверах
- HTTPS из коробки
- Защита от DDoS

**Pricing CDN:**
- Трафик в РФ: 1.50₽/GB
- Трафик за рубеж: 3.00₽/GB

---

## Lifecycle Policies

**Автоматическая миграция данных по возрасту:**

```xml
<!-- lifecycle.xml -->
<LifecycleConfiguration>
  <Rule>
    <ID>move-to-cold-after-90-days</ID>
    <Status>Enabled</Status>
    <Filter>
      <Prefix>tours/</Prefix>
    </Filter>
    <Transition>
      <Days>90</Days>
      <StorageClass>COLD</StorageClass>
    </Transition>
  </Rule>

  <Rule>
    <ID>delete-old-backups</ID>
    <Status>Enabled</Status>
    <Filter>
      <Prefix>backups/</Prefix>
    </Filter>
    <Expiration>
      <Days>365</Days>
    </Expiration>
  </Rule>
</LifecycleConfiguration>
```

```bash
# Применить lifecycle policy
aws --endpoint-url=https://storage.yandexcloud.net \
  s3api put-bucket-lifecycle-configuration \
  --bucket tourism-photos \
  --lifecycle-configuration file://lifecycle.xml
```

**Python:**

```python
lifecycle_config = {
    'Rules': [
        {
            'ID': 'move-to-cold-after-90-days',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'tours/'},
            'Transitions': [{
                'Days': 90,
                'StorageClass': 'COLD'
            }]
        },
        {
            'ID': 'delete-old-backups',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'backups/'},
            'Expiration': {'Days': 365}
        }
    ]
}

s3.put_bucket_lifecycle_configuration(
    Bucket='tourism-photos',
    LifecycleConfiguration=lifecycle_config
)
```

---

## Versioning (версионирование)

**Защита от случайного удаления:**

```bash
# Включить versioning
yc storage bucket update tourism-photos --versioning

# Теперь при удалении объект не удаляется, а создается delete marker
```

**Работа с версиями:**

```python
# Список версий объекта
response = s3.list_object_versions(
    Bucket='tourism-photos',
    Prefix='tours/photo.jpg'
)

for version in response.get('Versions', []):
    print(f"Version {version['VersionId']} - {version['LastModified']}")

# Скачать конкретную версию
s3.get_object(
    Bucket='tourism-photos',
    Key='tours/photo.jpg',
    VersionId='version-id-here'
)

# Удалить конкретную версию (permanent delete)
s3.delete_object(
    Bucket='tourism-photos',
    Key='tours/photo.jpg',
    VersionId='version-id-here'
)
```

---

## Object Lock (защита от удаления)

**WORM (Write Once Read Many) режим:**

```python
# Включить Object Lock при создании bucket
s3.create_bucket(
    Bucket='tourism-archives',
    ObjectLockEnabledForBucket=True
)

# Установить retention для объекта
s3.put_object_retention(
    Bucket='tourism-archives',
    Key='contracts/2026/contract-123.pdf',
    Retention={
        'Mode': 'COMPLIANCE',  # или 'GOVERNANCE'
        'RetainUntilDate': '2027-02-05T00:00:00Z'
    }
)
```

**Use case:** Хранение юридических документов, контрактов (compliance требования)

---

## CORS (Cross-Origin Resource Sharing)

**Для загрузки файлов из браузера:**

```xml
<!-- cors.xml -->
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>https://tourism-dubai.com</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedHeader>*</AllowedHeader>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
  </CORSRule>
</CORSConfiguration>
```

```bash
# Применить CORS
aws --endpoint-url=https://storage.yandexcloud.net \
  s3api put-bucket-cors \
  --bucket tourism-photos \
  --cors-configuration file://cors.xml
```

**Python:**

```python
cors_config = {
    'CORSRules': [{
        'AllowedOrigins': ['https://tourism-dubai.com'],
        'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE'],
        'AllowedHeaders': ['*'],
        'MaxAgeSeconds': 3000
    }]
}

s3.put_bucket_cors(
    Bucket='tourism-photos',
    CORSConfiguration=cors_config
)
```

---

## Static Website Hosting

**Хостинг статического сайта из bucket:**

```bash
# Настроить website hosting
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 website s3://tourism-photos \
  --index-document index.html \
  --error-document error.html

# Сайт будет доступен по URL:
# http://tourism-photos.website.yandexcloud.net
```

**Загрузить сайт:**

```bash
# Загрузить HTML, CSS, JS
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp ./website/ s3://tourism-photos/ --recursive

# Установить правильные Content-Type
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp ./website/ s3://tourism-photos/ --recursive \
  --content-type "text/html" --exclude "*" --include "*.html" \
  --content-type "text/css" --exclude "*" --include "*.css" \
  --content-type "application/javascript" --exclude "*" --include "*.js"
```

---

## Туристические use cases

### Use Case 1: Фото туров с автоматической оптимизацией

```python
# app.py
import boto3
from PIL import Image
import io

s3 = boto3.client('s3', endpoint_url='https://storage.yandexcloud.net')

def upload_tour_photo(tour_id, photo_file):
    """Загрузить фото тура с созданием thumbnail"""

    # Оригинал
    original_key = f"tours/{tour_id}/original/{photo_file.filename}"
    s3.upload_fileobj(
        Fileobj=photo_file,
        Bucket='tourism-photos',
        Key=original_key,
        ExtraArgs={'ContentType': 'image/jpeg'}
    )

    # Создать thumbnail
    photo_file.seek(0)
    image = Image.open(photo_file)
    image.thumbnail((300, 300))

    thumbnail_bytes = io.BytesIO()
    image.save(thumbnail_bytes, format='JPEG', quality=85)
    thumbnail_bytes.seek(0)

    thumbnail_key = f"tours/{tour_id}/thumbnails/{photo_file.filename}"
    s3.upload_fileobj(
        Fileobj=thumbnail_bytes,
        Bucket='tourism-photos',
        Key=thumbnail_key,
        ExtraArgs={'ContentType': 'image/jpeg'}
    )

    return {
        'original': f"https://storage.yandexcloud.net/tourism-photos/{original_key}",
        'thumbnail': f"https://storage.yandexcloud.net/tourism-photos/{thumbnail_key}"
    }
```

### Use Case 2: Presigned URLs для клиентов

```javascript
// generateUploadUrl.js (Cloud Function)
const AWS = require('aws-sdk');

const s3 = new AWS.S3({
    endpoint: 'https://storage.yandexcloud.net',
    accessKeyId: process.env.YC_ACCESS_KEY,
    secretAccessKey: process.env.YC_SECRET_KEY
});

module.exports.handler = async (event) => {
    const { customerId, fileName } = JSON.parse(event.body);

    // Генерация presigned URL для загрузки
    const uploadUrl = s3.getSignedUrl('putObject', {
        Bucket: 'tourism-photos',
        Key: `customer-uploads/${customerId}/${fileName}`,
        Expires: 3600,  // 1 час
        ContentType: 'image/jpeg'
    });

    return {
        statusCode: 200,
        body: JSON.stringify({ uploadUrl })
    };
};
```

### Use Case 3: Backup базы данных

```bash
#!/bin/bash
# backup-to-s3.sh

DATE=$(date +%Y-%m-%d)
BACKUP_FILE="database-backup-$DATE.sql.gz"

# Backup PostgreSQL
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER tourism | gzip > $BACKUP_FILE

# Upload to S3
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 cp $BACKUP_FILE s3://tourism-backups/database/$BACKUP_FILE

# Удалить локальный файл
rm $BACKUP_FILE

echo "Backup uploaded: $BACKUP_FILE"
```

---

## Мониторинг и метрики

```bash
# Размер bucket
aws --endpoint-url=https://storage.yandexcloud.net \
  s3 ls s3://tourism-photos --recursive --summarize

# Вывод:
# Total Objects: 15234
# Total Size: 52345678901

# Метрики через Yandex Monitoring
yc monitoring metric-data read \
  --folder-id=$FOLDER_ID \
  --selectors='service=storage,resource_id=tourism-photos,name=bucket_size_bytes' \
  --from='2026-02-01T00:00:00Z' \
  --to='2026-02-05T23:59:59Z'
```

---

## Pricing (2026)

### Storage

| Класс | Цена/GB/месяц | Min срок |
|-------|---------------|----------|
| Standard | 1.93₽ | - |
| Cold | 0.64₽ | 30 дней |
| Ice | 0.40₽ | 90 дней |

### Операции

| Операция | Цена/10k |
|----------|----------|
| PUT, POST, LIST | 3.20₽ |
| GET, HEAD | 0.32₽ |
| DELETE | бесплатно |

### Трафик

- Исходящий (outbound): 1.50₽/GB
- Входящий (inbound): бесплатно

### Расчет для туризма

**100GB фото туров:**
- Storage: 100GB × 1.93₽ = 193₽/месяц
- GET requests (100k/месяц): 100k × 0.32₽ / 10k = 3.20₽
- Трафик (500GB/месяц): 500GB × 1.50₽ = 750₽

**Итого: ~950₽/месяц (~$10)**

---

## Best Practices

### Naming

```
✓ Хорошо:
tours/desert-safari/2026/photo-001.jpg
backups/database/2026-02-05.sql.gz
customer-documents/123/passport.pdf

✗ Плохо:
photo.jpg (неинформативно)
Тур в пустыне.jpg (кириллица, пробелы)
../../../etc/passwd (path traversal)
```

### Security

1. **НЕ делайте bucket публичным без необходимости**
2. **Используйте presigned URLs для временного доступа**
3. **Включите versioning для критичных данных**
4. **Настройте lifecycle для автоматического удаления старых версий**

### Performance

1. **Используйте CDN для часто запрашиваемых файлов**
2. **Multipart upload для файлов >100MB**
3. **Правильный Content-Type (для browser caching)**
4. **Сжимайте файлы (gzip) перед загрузкой**

---

**Следующие шаги:**
- `databases-guide.md` - managed БД
- `cdn-guide.md` - детальная настройка CDN
- `tourism-business-cases.md` - кейс #2 (photo storage система)
