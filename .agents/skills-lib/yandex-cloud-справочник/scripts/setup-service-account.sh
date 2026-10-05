#!/bin/bash
# Создание Service Account с API ключом

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <service-account-name>"
    echo "Example: $0 tourism-sa"
    exit 1
fi

SA_NAME="$1"

echo "=== Creating Service Account: $SA_NAME ==="

# Получить folder ID
FOLDER_ID=$(yc config get folder-id)
echo "Folder ID: $FOLDER_ID"

# Создать service account
echo "Creating service account..."
yc iam service-account create --name "$SA_NAME" --description "Service account for tourism apps"

# Получить SA ID
SA_ID=$(yc iam service-account get "$SA_NAME" --format json | jq -r '.id')
echo "Service Account ID: $SA_ID"

# Назначить роль editor
echo "Assigning editor role..."
yc resource-manager folder add-access-binding "$FOLDER_ID" \
    --role editor \
    --subject serviceAccount:$SA_ID

# Создать API ключ
echo "Creating API key..."
yc iam api-key create \
    --service-account-name "$SA_NAME" \
    --description "API key for $SA_NAME" \
    --format json > "${SA_NAME}-api-key.json"

echo ""
echo "✓ Service account created successfully!"
echo ""
echo "API key saved to: ${SA_NAME}-api-key.json"
echo "IMPORTANT: Keep this file secure! The secret is shown only once."
echo ""
echo "To use in environment variables:"
echo "export YC_SERVICE_ACCOUNT_KEY=\$(cat ${SA_NAME}-api-key.json)"
