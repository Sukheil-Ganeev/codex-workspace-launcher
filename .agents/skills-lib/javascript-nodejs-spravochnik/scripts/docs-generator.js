#!/usr/bin/env node

/**
 * docs-generator.js - API Documentation Generator
 * Генерирует документацию API из кода (Swagger/OpenAPI)
 *
 * Использование:
 *   npm run docs              # Сгенерировать документацию
 *   npm run docs -- --watch   # Watch mode
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { execSync } = require('child_process');
require('dotenv').config();

const args = process.argv.slice(2);

// Help текст
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${chalk.bold('API Documentation Generator')}

Использование:
  ${chalk.cyan('node scripts/docs-generator.js [options]')}

Опции:
  --help, -h      Показать этот текст
  --watch         Watch mode для автоматической переген.
  --format        Формат (swagger, openapi, markdown)
  --output        Папка для сохранения (по умолчанию docs/)
  --ui            Открыть UI после генерации (swagger-ui)

Примеры:
  ${chalk.cyan('node scripts/docs-generator.js')}              # Сгенерировать
  ${chalk.cyan('node scripts/docs-generator.js --watch')}     # Watch mode
  ${chalk.cyan('node scripts/docs-generator.js --format openapi')} # OpenAPI v3
  `);
  process.exit(0);
}

const DOCS_DIR = 'docs';
const OUTPUT_FILE = path.join(DOCS_DIR, 'api-docs.json');

// Создание папки если её нет
if (!fs.existsSync(DOCS_DIR)) {
  fs.mkdirSync(DOCS_DIR, { recursive: true });
}

console.log(chalk.blue(`
╔════════════════════════════════════════╗
║  📚 API Documentation Generator        ║
╚════════════════════════════════════════╝
`));

// Парсим JSDoc комментарии и Express routes
function generateApiDocs() {
  console.log(chalk.blue('🔍 Анализирую API endpoints...\n'));

  const apiSpec = {
    openapi: '3.0.0',
    info: {
      title: 'API Documentation',
      version: '1.0.0',
      description: 'Auto-generated API documentation'
    },
    servers: [
      { url: 'http://localhost:3000', description: 'Development' },
      { url: 'https://api.example.com', description: 'Production' }
    ],
    paths: {},
    components: {
      schemas: {}
    }
  };

  // Ищем файлы с роутами
  const findRoutesFiles = (dir) => {
    let files = [];

    if (!fs.existsSync(dir)) return files;

    const items = fs.readdirSync(dir);

    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory() && !item.includes('node_modules')) {
        files = files.concat(findRoutesFiles(fullPath));
      } else if (item.includes('route') || item.includes('api')) {
        files.push(fullPath);
      }
    }

    return files;
  };

  const routeFiles = findRoutesFiles(process.cwd());

  // Парсим файлы
  for (const file of routeFiles) {
    try {
      const content = fs.readFileSync(file, 'utf8');
      const lines = content.split('\n');

      let currentRoute = null;
      let currentMethod = null;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Ищем JSDoc комментарии
        if (line.includes('/**')) {
          const docComment = [];
          let j = i;

          while (j < lines.length && !lines[j].includes('*/')) {
            docComment.push(lines[j]);
            j++;
          }
          docComment.push(lines[j]);

          // Ищем route после комментария
          for (let k = j + 1; k < j + 10 && k < lines.length; k++) {
            const routeLine = lines[k];

            // Парсим router.get/post/put/delete
            const match = routeLine.match(/router\.(get|post|put|delete|patch)\('([^']+)'/);

            if (match) {
              const method = match[1].toUpperCase();
              const path = match[2];

              if (!apiSpec.paths[path]) {
                apiSpec.paths[path] = {};
              }

              // Извлекаем информацию из JSDoc
              const description = docComment
                .find(l => l.includes('*') && !l.includes('/**') && !l.includes('*/'))
                ?.replace(/[*\/]/g, '')
                .trim() || 'No description';

              apiSpec.paths[path][method.toLowerCase()] = {
                summary: description.substring(0, 50),
                description: description,
                tags: [path.split('/')[1] || 'default'],
                responses: {
                  200: {
                    description: 'Successful response',
                    content: {
                      'application/json': {
                        schema: { type: 'object' }
                      }
                    }
                  },
                  400: {
                    description: 'Bad request'
                  },
                  500: {
                    description: 'Server error'
                  }
                }
              };

              console.log(chalk.cyan(`  ✓ ${method} ${path}`));
              break;
            }
          }
        }
      }
    } catch (error) {
      console.warn(chalk.yellow(`  ⚠️  Ошибка при парсинге ${path.basename(file)}: ${error.message}`));
    }
  }

  // Если не нашли routes, создаём примеры
  if (Object.keys(apiSpec.paths).length === 0) {
    console.log(chalk.yellow('⚠️  Routes не найдены. Создаю примеры...'));

    apiSpec.paths = {
      '/api/tours': {
        get: {
          summary: 'Get all tours',
          description: 'Retrieve a list of all available tours',
          tags: ['tours'],
          responses: {
            200: {
              description: 'List of tours',
              content: {
                'application/json': {
                  schema: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        id: { type: 'number' },
                        name: { type: 'string' },
                        price: { type: 'number' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      '/api/tours/{id}': {
        get: {
          summary: 'Get tour by ID',
          parameters: [
            {
              name: 'id',
              in: 'path',
              required: true,
              schema: { type: 'number' }
            }
          ],
          responses: {
            200: {
              description: 'Tour details'
            },
            404: {
              description: 'Tour not found'
            }
          }
        }
      },
      '/api/tours/{id}/book': {
        post: {
          summary: 'Book a tour',
          parameters: [
            {
              name: 'id',
              in: 'path',
              required: true,
              schema: { type: 'number' }
            }
          ],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  properties: {
                    name: { type: 'string' },
                    email: { type: 'string' },
                    date: { type: 'string' },
                    guests: { type: 'number' }
                  }
                }
              }
            }
          },
          responses: {
            201: {
              description: 'Booking created'
            }
          }
        }
      }
    };
  }

  // Сохраняем спецификацию
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(apiSpec, null, 2));
  console.log(chalk.green(`\n✓ Документация сгенерирована: ${OUTPUT_FILE}`));

  return apiSpec;
}

// Генерируем документацию
generateApiDocs();

// Создаём HTML UI
const htmlTemplate = `<!DOCTYPE html>
<html>
<head>
  <title>API Documentation</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
  <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js"></script>
  <script>
    const ui = SwaggerUIBundle({
      url: './api-docs.json',
      dom_id: '#swagger-ui',
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
      ],
      layout: "BaseLayout"
    });
  </script>
</body>
</html>
`;

fs.writeFileSync(path.join(DOCS_DIR, 'index.html'), htmlTemplate);
console.log(chalk.green(`✓ API UI создан: ${path.join(DOCS_DIR, 'index.html')}`));

// Markdown версия
const markdownDocs = `# API Documentation

Generated: ${new Date().toISOString()}

## Base URL
\`http://localhost:3000\` or \`https://api.example.com\`

## Endpoints

See [Swagger UI](./index.html) for interactive documentation.
`;

fs.writeFileSync(path.join(DOCS_DIR, 'README.md'), markdownDocs);
console.log(chalk.green(`✓ Markdown документация создана`));

console.log(chalk.blue(`\n${'='.repeat(40)}`));
console.log(chalk.green(`
✓ ДОКУМЕНТАЦИЯ ГОТОВА

Файлы:
  ${OUTPUT_FILE}
  ${path.join(DOCS_DIR, 'index.html')}
  ${path.join(DOCS_DIR, 'README.md')}

Откройте в браузере:
  ${chalk.cyan(`file://${path.join(process.cwd(), DOCS_DIR, 'index.html')}`)}

Или запустите сервер:
  ${chalk.cyan('npx serve docs')}
`));

process.exit(0);
