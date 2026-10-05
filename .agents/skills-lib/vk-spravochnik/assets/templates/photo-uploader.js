#!/usr/bin/env node
/**
 * VK Photo Uploader Template (Node.js)
 * =====================================
 *
 * Шаблон для загрузки фотографий в VK через API.
 *
 * Процесс загрузки (3 шага):
 * 1. photos.getWallUploadServer - получить upload URL
 * 2. POST на upload URL - загрузить файл
 * 3. photos.saveWallPhoto - сохранить фото
 *
 * Установка:
 * ----------
 * npm install axios form-data dotenv
 *
 * Настройка:
 * ----------
 * Создать .env файл:
 * VK_TOKEN=your_community_token
 * GROUP_ID=your_group_id
 * API_VERSION=5.199
 *
 * Использование:
 * -------------
 * node photo-uploader.js /path/to/photo.jpg
 *
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// ========== НАСТРОЙКИ ==========
const VK_TOKEN = process.env.VK_TOKEN;
const GROUP_ID = parseInt(process.env.GROUP_ID || '0');
const API_VERSION = process.env.API_VERSION || '5.199';
const VK_API_URL = 'https://api.vk.com/method';

if (!VK_TOKEN) {
    console.error('❌ VK_TOKEN не найден в .env файле!');
    process.exit(1);
}

if (!GROUP_ID) {
    console.error('❌ GROUP_ID не найден в .env файле!');
    process.exit(1);
}

// ========== VK API ФУНКЦИИ ==========

/**
 * Вызов метода VK API
 *
 * @param {string} method - Название метода (например, 'photos.getWallUploadServer')
 * @param {object} params - Параметры метода
 * @returns {Promise<object>} Ответ API
 */
async function vkApiCall(method, params = {}) {
    const url = `${VK_API_URL}/${method}`;

    const requestParams = {
        ...params,
        access_token: VK_TOKEN,
        v: API_VERSION
    };

    try {
        const response = await axios.get(url, { params: requestParams });

        if (response.data.error) {
            throw new Error(
                `VK API Error ${response.data.error.error_code}: ${response.data.error.error_msg}`
            );
        }

        return response.data.response;

    } catch (error) {
        if (error.response) {
            console.error('❌ HTTP Error:', error.response.status, error.response.data);
        }
        throw error;
    }
}

// ========== ЗАГРУЗКА ФОТО ==========

/**
 * Шаг 1: Получить upload server URL
 *
 * @param {number} groupId - ID группы
 * @returns {Promise<string>} Upload URL
 */
async function getUploadServer(groupId) {
    console.log('📡 Шаг 1: Получение upload server...');

    const response = await vkApiCall('photos.getWallUploadServer', {
        group_id: groupId
    });

    console.log('✅ Upload server получен:', response.upload_url);
    return response.upload_url;
}

/**
 * Шаг 2: Загрузить фото на upload server
 *
 * @param {string} uploadUrl - URL для загрузки
 * @param {string} photoPath - Путь к файлу фото
 * @returns {Promise<object>} Данные загруженного фото
 */
async function uploadPhoto(uploadUrl, photoPath) {
    console.log('📤 Шаг 2: Загрузка фото на сервер...');

    // Проверить существование файла
    if (!fs.existsSync(photoPath)) {
        throw new Error(`Файл не найден: ${photoPath}`);
    }

    // Создать form data
    const form = new FormData();
    form.append('photo', fs.createReadStream(photoPath));

    try {
        const response = await axios.post(uploadUrl, form, {
            headers: form.getHeaders()
        });

        if (response.data.photo === undefined) {
            throw new Error('Ошибка загрузки: photo не получен от сервера');
        }

        console.log('✅ Фото загружено на сервер');
        return response.data;

    } catch (error) {
        console.error('❌ Ошибка загрузки:', error.message);
        throw error;
    }
}

/**
 * Шаг 3: Сохранить фото через VK API
 *
 * @param {number} groupId - ID группы
 * @param {object} uploadData - Данные из шага 2
 * @returns {Promise<object>} Сохранённое фото
 */
async function saveWallPhoto(groupId, uploadData) {
    console.log('💾 Шаг 3: Сохранение фото...');

    const photos = await vkApiCall('photos.saveWallPhoto', {
        group_id: groupId,
        photo: uploadData.photo,
        server: uploadData.server,
        hash: uploadData.hash
    });

    if (!photos || photos.length === 0) {
        throw new Error('Ошибка сохранения: фото не сохранено');
    }

    const photo = photos[0];
    console.log('✅ Фото сохранено:', `photo${photo.owner_id}_${photo.id}`);

    return photo;
}

/**
 * Полный процесс загрузки фото (3 шага)
 *
 * @param {string} photoPath - Путь к файлу фото
 * @param {number} groupId - ID группы
 * @returns {Promise<object>} Сохранённое фото с attachment строкой
 */
async function uploadPhotoComplete(photoPath, groupId) {
    console.log('\n🚀 Начало загрузки фото в VK...');
    console.log(`📁 Файл: ${photoPath}`);
    console.log(`📋 Группа ID: ${groupId}\n`);

    try {
        // Шаг 1: Получить upload server
        const uploadUrl = await getUploadServer(groupId);

        // Пауза (rate limiting)
        await sleep(500);

        // Шаг 2: Загрузить фото
        const uploadData = await uploadPhoto(uploadUrl, photoPath);

        // Пауза (rate limiting)
        await sleep(500);

        // Шаг 3: Сохранить фото
        const photo = await saveWallPhoto(groupId, uploadData);

        // Attachment строка для использования в wall.post
        const attachment = `photo${photo.owner_id}_${photo.id}`;

        console.log('\n✅ ЗАГРУЗКА ЗАВЕРШЕНА!');
        console.log(`📎 Attachment: ${attachment}`);
        console.log(`🔗 URL: https://vk.com/${attachment.replace('_', '-')}`);

        return {
            ...photo,
            attachment
        };

    } catch (error) {
        console.error('\n❌ ОШИБКА ЗАГРУЗКИ:', error.message);
        throw error;
    }
}

// ========== BATCH UPLOAD ==========

/**
 * Batch загрузка нескольких фото
 *
 * @param {string[]} photoPaths - Массив путей к файлам
 * @param {number} groupId - ID группы
 * @returns {Promise<string[]>} Массив attachment строк
 */
async function uploadPhotoBatch(photoPaths, groupId) {
    console.log(`\n📦 Batch загрузка ${photoPaths.length} фото...\n`);

    const attachments = [];

    for (let i = 0; i < photoPaths.length; i++) {
        const photoPath = photoPaths[i];
        console.log(`[${i + 1}/${photoPaths.length}] Загрузка: ${path.basename(photoPath)}`);

        try {
            const photo = await uploadPhotoComplete(photoPath, groupId);
            attachments.push(photo.attachment);

            // Пауза между загрузками (rate limiting)
            if (i < photoPaths.length - 1) {
                console.log('⏳ Пауза 1 сек (rate limiting)...\n');
                await sleep(1000);
            }

        } catch (error) {
            console.error(`❌ Ошибка загрузки ${photoPath}:`, error.message);
            // Продолжить загрузку остальных
        }
    }

    console.log(`\n✅ Batch загрузка завершена: ${attachments.length}/${photoPaths.length} успешно`);
    console.log(`📎 Attachments: ${attachments.join(',')}`);

    return attachments;
}

// ========== УТИЛИТЫ ==========

/**
 * Пауза (для rate limiting)
 *
 * @param {number} ms - Миллисекунды
 * @returns {Promise<void>}
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ========== MAIN ==========

async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.log(`
📷 VK Photo Uploader

Использование:
  node photo-uploader.js <photo_path>
  node photo-uploader.js <photo1> <photo2> <photo3> ...

Примеры:
  node photo-uploader.js ./photo.jpg
  node photo-uploader.js ./photo1.jpg ./photo2.jpg ./photo3.jpg

Настройка:
  Создайте .env файл с параметрами:
  VK_TOKEN=your_community_token
  GROUP_ID=your_group_id
        `);
        process.exit(0);
    }

    try {
        if (args.length === 1) {
            // Одно фото
            await uploadPhotoComplete(args[0], GROUP_ID);
        } else {
            // Batch загрузка
            await uploadPhotoBatch(args, GROUP_ID);
        }

    } catch (error) {
        console.error('\n❌ Критическая ошибка:', error.message);
        process.exit(1);
    }
}

// Запуск
if (require.main === module) {
    main();
}

// ========== ЭКСПОРТ ==========

module.exports = {
    vkApiCall,
    getUploadServer,
    uploadPhoto,
    saveWallPhoto,
    uploadPhotoComplete,
    uploadPhotoBatch
};
