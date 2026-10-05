# IAM & Authentication

## Service Account

```bash
# Создать
yc iam service-account create --name tourism-sa

# Роль
yc resource-manager folder add-access-binding $FOLDER_ID \
  --role editor \
  --subject serviceAccount:$SA_ID

# API key
yc iam api-key create --service-account-name tourism-sa
```

## OAuth Token vs API Key

**OAuth Token:**
- Для пользователей
- Срок жизни: 12 часов
- `yc iam create-token`

**API Key:**
- Для приложений
- Бессрочный
- Хранить в secrets

## Роли

- `viewer` - чтение
- `editor` - чтение + запись
- `admin` - полный контроль
- `serverless.functions.invoker` - вызов функций

**См. также:** `scripts/setup-service-account.sh`
