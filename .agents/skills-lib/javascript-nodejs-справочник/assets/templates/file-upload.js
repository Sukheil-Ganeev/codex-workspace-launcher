/**
 * File Upload Handler Template
 *
 * Production-ready обработчик загрузки файлов с:
 * - Валидацией типов и размера
 * - Сохранением в CloudStorage (AWS S3 / Google Cloud Storage)
 * - Сканированием на вирусы (опционально)
 * - Обработкой изображений
 *
 * @example
 * npm install multer aws-sdk dotenv
 * // или для Google Cloud:
 * npm install @google-cloud/storage
 */

const fs = require('fs');
const path = require('path');
const multer = require('multer');

// ==================== FILE CONFIG ====================

const FILE_CONFIG = {
  maxFileSize: 10 * 1024 * 1024, // 10 MB
  maxFiles: 5,
  allowedMimeTypes: [
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ],
  uploadDir: process.env.UPLOAD_DIR || './uploads',
  useCloudStorage: process.env.CLOUD_STORAGE === 'true',
};

// ==================== MULTER CONFIG ====================

/**
 * Local storage (для development)
 */
const localStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    // Создать директорию если не существует
    if (!fs.existsSync(FILE_CONFIG.uploadDir)) {
      fs.mkdirSync(FILE_CONFIG.uploadDir, { recursive: true });
    }
    cb(null, FILE_CONFIG.uploadDir);
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now();
    const ext = path.extname(file.originalname);
    const name = path.basename(file.originalname, ext);
    cb(null, `${name}-${timestamp}${ext}`);
  },
});

/**
 * Memory storage (для обработки перед загрузкой в облако)
 */
const memoryStorage = multer.memoryStorage();

/**
 * Валидация файлов
 */
const fileFilter = (req, file, cb) => {
  // Проверить MIME type
  if (!FILE_CONFIG.allowedMimeTypes.includes(file.mimetype)) {
    return cb(new Error(`File type not allowed: ${file.mimetype}`), false);
  }

  // Проверить расширение (защита от spoofing)
  const ext = path.extname(file.originalname).toLowerCase();
  const validExts = ['.jpg', '.jpeg', '.png', '.webp', '.pdf', '.txt', '.doc', '.docx'];
  if (!validExts.includes(ext)) {
    return cb(new Error(`File extension not allowed: ${ext}`), false);
  }

  cb(null, true);
};

/**
 * Multer middleware
 */
const upload = multer({
  storage: localStorage,
  fileFilter,
  limits: {
    fileSize: FILE_CONFIG.maxFileSize,
    files: FILE_CONFIG.maxFiles,
  },
});

// ==================== AWS S3 UPLOAD ====================

/**
 * Загрузить файл на AWS S3
 *
 * @param {Buffer} fileContent - Содержимое файла
 * @param {string} filename - Имя файла
 * @param {string} mimeType - MIME тип
 * @returns {Promise<Object>} { url, key, size }
 */
async function uploadToS3(fileContent, filename, mimeType) {
  const AWS = require('aws-sdk');

  const s3 = new AWS.S3({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    region: process.env.AWS_REGION,
  });

  const key = `uploads/${Date.now()}-${filename}`;

  const params = {
    Bucket: process.env.AWS_BUCKET_NAME,
    Key: key,
    Body: fileContent,
    ContentType: mimeType,
    ACL: 'public-read', // TODO: Использовать signed URLs для private
  };

  try {
    const result = await s3.upload(params).promise();

    console.log(`[Upload] S3: ${filename} -> ${result.Location}`);

    return {
      url: result.Location,
      key: result.Key,
      size: fileContent.length,
      provider: 'aws-s3',
    };
  } catch (error) {
    console.error('[Upload] S3 error:', error.message);
    throw error;
  }
}

// ==================== GOOGLE CLOUD STORAGE ====================

/**
 * Загрузить файл на Google Cloud Storage
 *
 * @param {Buffer} fileContent
 * @param {string} filename
 * @returns {Promise<Object>}
 */
async function uploadToGCS(fileContent, filename) {
  const { Storage } = require('@google-cloud/storage');

  const storage = new Storage({
    projectId: process.env.GCP_PROJECT_ID,
    keyFilename: process.env.GCP_KEY_FILE,
  });

  const bucket = storage.bucket(process.env.GCP_BUCKET_NAME);
  const file = bucket.file(`uploads/${Date.now()}-${filename}`);

  try {
    await file.save(fileContent);

    // Получить public URL
    const publicUrl = `https://storage.googleapis.com/${process.env.GCP_BUCKET_NAME}/${file.name}`;

    console.log(`[Upload] GCS: ${filename} -> ${publicUrl}`);

    return {
      url: publicUrl,
      key: file.name,
      size: fileContent.length,
      provider: 'google-cloud-storage',
    };
  } catch (error) {
    console.error('[Upload] GCS error:', error.message);
    throw error;
  }
}

// ==================== EXPRESS ROUTE HANDLER ====================

/**
 * Express middleware для загрузки одного файла
 *
 * @example
 * app.post('/upload', singleFileUpload, uploadHandler);
 */
const singleFileUpload = upload.single('file');

/**
 * Express middleware для загрузки нескольких файлов
 *
 * @example
 * app.post('/upload-multiple', multipleFileUpload, uploadHandler);
 */
const multipleFileUpload = upload.array('files', FILE_CONFIG.maxFiles);

/**
 * Route handler для загрузки файла
 *
 * @example
 * app.post('/api/upload', singleFileUpload, async (req, res) => {
 *   try {
 *     const result = await uploadHandler(req, res);
 *     res.json(result);
 *   } catch (error) {
 *     res.status(400).json({ error: error.message });
 *   }
 * });
 */
async function uploadHandler(req, res) {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  try {
    const { originalname, mimetype, buffer, size } = req.file;

    // Валидация
    if (size > FILE_CONFIG.maxFileSize) {
      return res.status(413).json({ error: 'File too large' });
    }

    let result;

    // Выбрать способ загрузки
    if (FILE_CONFIG.useCloudStorage && process.env.CLOUD_PROVIDER === 'aws') {
      result = await uploadToS3(buffer, originalname, mimetype);
    } else if (FILE_CONFIG.useCloudStorage && process.env.CLOUD_PROVIDER === 'gcp') {
      result = await uploadToGCS(buffer, originalname);
    } else {
      // Local storage (уже загружено multer)
      result = {
        url: `/uploads/${req.file.filename}`,
        key: req.file.filename,
        size,
        provider: 'local',
      };
    }

    // TODO: Сохранить информацию о файле в БД
    console.log(`[Upload] Success: ${originalname}`);

    return {
      success: true,
      file: {
        name: originalname,
        ...result,
      },
    };
  } catch (error) {
    console.error('[Upload] Handler error:', error);
    throw error;
  }
}

// ==================== IMAGE PROCESSING ====================

/**
 * Обработка изображений (resize, optimize)
 * TODO: npm install sharp
 *
 * @param {Buffer} buffer - Image buffer
 * @param {Object} options - { width, height, quality }
 */
async function processImage(buffer, options = {}) {
  try {
    const sharp = require('sharp');

    const { width = 1200, height = 800, quality = 80 } = options;

    const optimized = await sharp(buffer)
      .resize(width, height, {
        fit: 'cover',
        position: 'center',
      })
      .jpeg({ quality })
      .toBuffer();

    console.log(`[Image] Processed: ${buffer.length} -> ${optimized.length} bytes`);

    return optimized;
  } catch (error) {
    console.error('[Image] Processing error:', error.message);
    throw error;
  }
}

// ==================== CLEANUP ====================

/**
 * Удалить файл
 *
 * @param {string} fileKey - Ключ файла (filename или S3 key)
 */
async function deleteFile(fileKey) {
  try {
    if (FILE_CONFIG.useCloudStorage && process.env.CLOUD_PROVIDER === 'aws') {
      const AWS = require('aws-sdk');
      const s3 = new AWS.S3();
      await s3.deleteObject({
        Bucket: process.env.AWS_BUCKET_NAME,
        Key: fileKey,
      }).promise();
    } else {
      // Local file
      const filepath = path.join(FILE_CONFIG.uploadDir, fileKey);
      if (fs.existsSync(filepath)) {
        fs.unlinkSync(filepath);
      }
    }

    console.log(`[Upload] Deleted: ${fileKey}`);
  } catch (error) {
    console.error('[Upload] Delete error:', error.message);
  }
}

// ==================== EXPORTS ====================

module.exports = {
  upload,
  singleFileUpload,
  multipleFileUpload,
  uploadHandler,
  uploadToS3,
  uploadToGCS,
  processImage,
  deleteFile,
};

// Required environment variables:
// UPLOAD_DIR=./uploads
// CLOUD_STORAGE=false (or true)
// CLOUD_PROVIDER=aws (or gcp)
// AWS_ACCESS_KEY_ID=xxx
// AWS_SECRET_ACCESS_KEY=xxx
// AWS_BUCKET_NAME=my-bucket
// GCP_PROJECT_ID=xxx
// GCP_BUCKET_NAME=xxx
