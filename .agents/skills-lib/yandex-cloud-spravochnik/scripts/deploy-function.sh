#!/bin/bash
# Deploy Cloud Function

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <function-name> <source-path>"
    echo ""
    echo "Example:"
    echo "  $0 tourism-api ./src"
    echo ""
    echo "Options:"
    echo "  -r, --runtime RUNTIME     Runtime (nodejs18, python312, etc.)"
    echo "  -e, --entrypoint ENTRY    Entrypoint (default: index.handler)"
    echo "  -m, --memory MEMORY       Memory in MB (default: 256)"
    echo "  -t, --timeout TIMEOUT     Timeout in seconds (default: 5)"
    exit 1
fi

FUNCTION_NAME="$1"
SOURCE_PATH="$2"
RUNTIME="${RUNTIME:-nodejs18}"
ENTRYPOINT="${ENTRYPOINT:-index.handler}"
MEMORY="${MEMORY:-256}"
TIMEOUT="${TIMEOUT:-5}"

echo "=== Deploying Function: $FUNCTION_NAME ==="
echo "Source: $SOURCE_PATH"
echo "Runtime: $RUNTIME"
echo "Entrypoint: $ENTRYPOINT"
echo ""

# Проверить существование функции
if yc serverless function get "$FUNCTION_NAME" &>/dev/null; then
    echo "Function exists, creating new version..."
else
    echo "Creating new function..."
    yc serverless function create --name "$FUNCTION_NAME"
fi

# Deploy
echo "Uploading code..."
yc serverless function version create \
    --function-name "$FUNCTION_NAME" \
    --runtime "$RUNTIME" \
    --entrypoint "$ENTRYPOINT" \
    --memory "${MEMORY}m" \
    --execution-timeout "${TIMEOUT}s" \
    --source-path "$SOURCE_PATH"

# Получить URL
FUNCTION_URL=$(yc serverless function get "$FUNCTION_NAME" --format json | jq -r '.http_invoke_url')

echo ""
echo "✓ Function deployed successfully!"
echo ""
echo "Function URL: $FUNCTION_URL"
echo ""
echo "To make it public:"
echo "  yc serverless function allow-unauthenticated-invoke $FUNCTION_NAME"
