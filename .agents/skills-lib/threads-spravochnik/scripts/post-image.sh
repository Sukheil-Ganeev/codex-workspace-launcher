#!/bin/bash

# Публикация изображения в Threads (2-step process)
# Автор: Claude Code Agent
# Дата: 05 февраля 2026

# Использование:
# ./post-image.sh <IMAGE_URL> <CAPTION> <IG_USER_ID> <ACCESS_TOKEN>
#
# Пример:
# ./post-image.sh "https://example.com/desert.jpg" "Desert Safari Dubai 🏜️" "123456789" "YOUR_TOKEN"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help message
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  echo "Threads API - Публикация изображения"
  echo ""
  echo "Использование:"
  echo "  ./post-image.sh <IMAGE_URL> <CAPTION> <IG_USER_ID> <ACCESS_TOKEN>"
  echo ""
  echo "Параметры:"
  echo "  IMAGE_URL      Публичный HTTPS URL изображения"
  echo "  CAPTION        Текст поста (до 500 символов)"
  echo "  IG_USER_ID     Instagram User ID (для Threads)"
  echo "  ACCESS_TOKEN   Access token (Instagram/Threads)"
  echo ""
  echo "Примеры:"
  echo "  ./post-image.sh \"https://example.com/image.jpg\" \"Hello Threads!\" \"123456\" \"YOUR_TOKEN\""
  echo ""
  echo "Примечание:"
  echo "  - Изображение публикуется в 2 шага (create container → publish)"
  echo "  - URL должен быть публичным и доступным по HTTPS"
  echo "  - Caption обрезается до 500 символов (лимит Threads)"
  exit 0
fi

# Проверка аргументов
if [ $# -lt 4 ]; then
  echo -e "${RED}Ошибка: Недостаточно аргументов${NC}"
  echo "Используйте -h для справки"
  exit 1
fi

IMAGE_URL=$1
CAPTION=$2
IG_USER_ID=$3
ACCESS_TOKEN=$4

# Валидация IMAGE_URL
if [[ ! $IMAGE_URL =~ ^https:// ]]; then
  echo -e "${RED}Ошибка: IMAGE_URL должен начинаться с https://${NC}"
  exit 1
fi

# Обрезка caption до 500 символов
CAPTION=${CAPTION:0:500}

# Base URL
BASE_URL="https://graph.threads.net/v1.0"

echo -e "${YELLOW}📸 Публикация изображения в Threads...${NC}"
echo ""
echo "Image URL: $IMAGE_URL"
echo "Caption: ${CAPTION:0:50}..."
echo ""

# ============================================
# Шаг 1: Создание media container
# ============================================

echo -e "${YELLOW}Шаг 1: Создание media container...${NC}"

CREATE_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/${IG_USER_ID}/threads" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"media_type\": \"IMAGE\",
    \"image_url\": \"${IMAGE_URL}\",
    \"text\": \"${CAPTION}\"
  }")

# Проверка на ошибки
if echo "$CREATE_RESPONSE" | grep -q '"error"'; then
  echo -e "${RED}❌ Ошибка при создании container:${NC}"
  echo "$CREATE_RESPONSE" | jq '.'
  exit 1
fi

# Извлечение CONTAINER_ID
CONTAINER_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')

if [ -z "$CONTAINER_ID" ] || [ "$CONTAINER_ID" == "null" ]; then
  echo -e "${RED}❌ Не удалось получить Container ID${NC}"
  echo "$CREATE_RESPONSE" | jq '.'
  exit 1
fi

echo -e "${GREEN}✅ Container создан: ${CONTAINER_ID}${NC}"

# ============================================
# Задержка для обработки медиа
# ============================================

echo -e "${YELLOW}⏳ Ожидание обработки изображения (5 секунд)...${NC}"
sleep 5

# ============================================
# Шаг 2: Публикация container
# ============================================

echo -e "${YELLOW}Шаг 2: Публикация container...${NC}"

PUBLISH_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/${CONTAINER_ID}/publish" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

# Проверка на ошибки
if echo "$PUBLISH_RESPONSE" | grep -q '"error"'; then
  echo -e "${RED}❌ Ошибка при публикации:${NC}"
  echo "$PUBLISH_RESPONSE" | jq '.'
  exit 1
fi

# Извлечение POST_ID
POST_ID=$(echo "$PUBLISH_RESPONSE" | jq -r '.id')

if [ -z "$POST_ID" ] || [ "$POST_ID" == "null" ]; then
  echo -e "${RED}❌ Не удалось опубликовать пост${NC}"
  echo "$PUBLISH_RESPONSE" | jq '.'
  exit 1
fi

echo ""
echo -e "${GREEN}✅ Изображение опубликовано в Threads!${NC}"
echo ""
echo "Post ID: $POST_ID"
echo "Container ID: $CONTAINER_ID"
echo ""

# ============================================
# Опционально: Получение информации о посте
# ============================================

echo -e "${YELLOW}Получение информации о посте...${NC}"

POST_INFO=$(curl -s -X GET \
  "${BASE_URL}/${POST_ID}?fields=id,text,media_type,media_url,timestamp,permalink" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "$POST_INFO" | jq '.'

echo ""
echo -e "${GREEN}✅ Готово!${NC}"
