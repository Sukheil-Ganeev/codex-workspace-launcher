#!/bin/bash
# VK wall.post - Публикация на стену через curl

# ========== НАСТРОЙКИ ==========
VK_TOKEN="${VK_TOKEN:-your_token_here}"
GROUP_ID="${GROUP_ID:-12345678}"
API_VERSION="5.199"

# ========== ФУНКЦИЯ ПУБЛИКАЦИИ ==========

post_to_wall() {
    local message="$1"
    local attachments="$2"

    curl -X POST "https://api.vk.com/method/wall.post" \
        -d "owner_id=-${GROUP_ID}" \
        -d "from_group=1" \
        -d "message=${message}" \
        -d "attachments=${attachments}" \
        -d "access_token=${VK_TOKEN}" \
        -d "v=${API_VERSION}"
}

# ========== ПРИМЕРЫ ==========

# 1. Простой текстовый пост
example_text_post() {
    echo "📝 Публикация текстового поста..."
    post_to_wall "Привет из VK API! 🌴" ""
}

# 2. Пост с фото
example_photo_post() {
    echo "📸 Публикация поста с фото..."
    # Сначала загрузите фото и получите attachment (photo-123_456)
    post_to_wall "Desert Safari Adventure! 🏜️" "photo-${GROUP_ID}_456239017"
}

# 3. Отложенная публикация (через 1 час)
example_delayed_post() {
    echo "⏰ Отложенная публикация..."
    local publish_date=$(date -d "+1 hour" +%s)

    curl -X POST "https://api.vk.com/method/wall.post" \
        -d "owner_id=-${GROUP_ID}" \
        -d "from_group=1" \
        -d "message=Этот пост опубликуется через час!" \
        -d "publish_date=${publish_date}" \
        -d "access_token=${VK_TOKEN}" \
        -d "v=${API_VERSION}"
}

# ========== MAIN ==========

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    cat << 'EOF'
VK wall.post - Публикация на стену

Использование:
  ./post-to-wall.sh                    # Примеры
  ./post-to-wall.sh "Ваш текст"        # Опубликовать текст
  export VK_TOKEN=xxx GROUP_ID=123     # Установить токен и ID группы

Примеры:
  ./post-to-wall.sh "Hello from VK!"
  ./post-to-wall.sh "Dubai Tours 🌴" "photo-123_456"

EOF
    exit 0
fi

# Если передан аргумент - опубликовать текст
if [ -n "$1" ]; then
    post_to_wall "$1" "$2"
else
    # Показать примеры
    echo "Выберите пример:"
    echo "1) Текстовый пост"
    echo "2) Пост с фото"
    echo "3) Отложенная публикация"
    read -p "Выбор: " choice

    case $choice in
        1) example_text_post ;;
        2) example_photo_post ;;
        3) example_delayed_post ;;
        *) echo "Неверный выбор" ;;
    esac
fi
