#!/bin/bash
# VK Photo Upload - 3-этапный процесс загрузки фото

# ========== НАСТРОЙКИ ==========
VK_TOKEN="${VK_TOKEN:-your_token_here}"
GROUP_ID="${GROUP_ID:-12345678}"
API_VERSION="5.199"

# ========== ФУНКЦИИ ==========

# Шаг 1: Получить upload server URL
get_upload_server() {
    echo "📡 Шаг 1: Получение upload server..."

    response=$(curl -s "https://api.vk.com/method/photos.getWallUploadServer" \
        -d "group_id=${GROUP_ID}" \
        -d "access_token=${VK_TOKEN}" \
        -d "v=${API_VERSION}")

    upload_url=$(echo "$response" | jq -r '.response.upload_url')
    echo "✅ Upload URL: $upload_url"
    echo "$upload_url"
}

# Шаг 2: Загрузить фото на upload server
upload_photo() {
    local upload_url="$1"
    local photo_path="$2"

    echo "📤 Шаг 2: Загрузка фото на сервер..."

    response=$(curl -s -X POST "$upload_url" \
        -F "photo=@${photo_path}")

    echo "✅ Фото загружено"
    echo "$response"
}

# Шаг 3: Сохранить фото через VK API
save_wall_photo() {
    local photo_data="$1"

    echo "💾 Шаг 3: Сохранение фото..."

    photo=$(echo "$photo_data" | jq -r '.photo')
    server=$(echo "$photo_data" | jq -r '.server')
    hash=$(echo "$photo_data" | jq -r '.hash')

    response=$(curl -s "https://api.vk.com/method/photos.saveWallPhoto" \
        -d "group_id=${GROUP_ID}" \
        -d "photo=${photo}" \
        -d "server=${server}" \
        -d "hash=${hash}" \
        -d "access_token=${VK_TOKEN}" \
        -d "v=${API_VERSION}")

    owner_id=$(echo "$response" | jq -r '.response[0].owner_id')
    photo_id=$(echo "$response" | jq -r '.response[0].id')
    attachment="photo${owner_id}_${photo_id}"

    echo "✅ Фото сохранено: $attachment"
    echo "$attachment"
}

# Полный процесс загрузки
upload_photo_complete() {
    local photo_path="$1"

    if [ ! -f "$photo_path" ]; then
        echo "❌ Файл не найден: $photo_path"
        exit 1
    fi

    echo "🚀 Загрузка фото в VK..."
    echo "📁 Файл: $photo_path"
    echo ""

    # Шаг 1
    upload_url=$(get_upload_server)
    sleep 0.5

    # Шаг 2
    upload_data=$(upload_photo "$upload_url" "$photo_path")
    sleep 0.5

    # Шаг 3
    attachment=$(save_wall_photo "$upload_data")

    echo ""
    echo "✅ ЗАГРУЗКА ЗАВЕРШЕНА!"
    echo "📎 Attachment: $attachment"
    echo ""
    echo "Используйте это в wall.post:"
    echo "  attachments=$attachment"
}

# ========== MAIN ==========

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    cat << 'EOF'
VK Photo Upload - Загрузка фото через API

Процесс (3 шага):
1. photos.getWallUploadServer - получить upload URL
2. POST на upload URL - загрузить файл
3. photos.saveWallPhoto - сохранить фото

Использование:
  ./upload-photo.sh <photo_path>
  export VK_TOKEN=xxx GROUP_ID=123  # Установить токен

Примеры:
  ./upload-photo.sh ./photo.jpg
  ./upload-photo.sh ~/Desktop/dubai.jpg

Требования:
  - curl
  - jq (для парсинга JSON)

EOF
    exit 0
fi

if [ -z "$1" ]; then
    echo "❌ Укажите путь к фото"
    echo "Использование: ./upload-photo.sh <photo_path>"
    exit 1
fi

# Проверка зависимостей
if ! command -v jq &> /dev/null; then
    echo "❌ jq не установлен"
    echo "Установите: sudo apt-get install jq"
    exit 1
fi

# Загрузка
upload_photo_complete "$1"
