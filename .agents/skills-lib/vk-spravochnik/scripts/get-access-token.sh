#!/bin/bash
# VK Access Token - Инструкция получения

cat << 'EOF'
========================================
VK API Access Token - Инструкция
========================================

## 1. Community Token (для ботов сообществ)

Шаги:
1. Перейти в настройки сообщества: https://vk.com/club{YOUR_GROUP_ID}?act=tokens
2. Настройки → Работа с API → Ключи доступа
3. Создать ключ → Выбрать права:
   ✅ Управление сообществом
   ✅ Управление постами
   ✅ Фотографии
   ✅ Видео
   ✅ Сообщения сообщества (для ботов)
4. Скопировать токен

Пример токена:
vk1.a.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

## 2. Standalone App Token (OAuth)

Для получения standalone токена:

1. Создать приложение: https://vk.com/apps?act=manage
2. Получить App ID
3. OAuth URL:

https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,photos,video,offline&response_type=token&v=5.199

4. Авторизоваться и скопировать access_token из URL

## 3. Service Token

Только для официальных приложений VK (требуется партнёрство).

========================================

ВАЖНО:
- НЕ публикуйте токены в публичных репозиториях!
- Используйте .env файлы
- Community Token: 3 запроса/сек
- Standalone Token: 20 запросов/сек

EOF
