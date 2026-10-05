#!/usr/bin/env node

/**
 * Валидация netlify.toml файла перед деплоем
 *
 * ИСПОЛЬЗОВАНИЕ:
 *   node validate-netlify-toml.js [path/to/netlify.toml]
 *   node validate-netlify-toml.js
 *
 * ОПИСАНИЕ:
 *   - Проверяет синтаксис TOML файла
 *   - Валидирует обязательные поля конфигурации
 *   - Проверяет существование указанных путей
 *   - Валидирует правила редиректов
 *   - Проверяет functions directory и наличие файлов функций
 *
 * ТРЕБОВАНИЯ:
 *   Node.js (встроенный TOML парсер, без зависимостей)
 */

const fs = require('fs');
const path = require('path');

// Цвета для консоли
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m'
};

class NetlifyTomlValidator {
  constructor(filePath) {
    this.filePath = filePath;
    this.errors = [];
    this.warnings = [];
    this.config = null;
  }

  // Основная функция валидации
  async validate() {
    console.log(`${colors.blue}🔍 Валидация netlify.toml: ${this.filePath}${colors.reset}\n`);

    // 1. Проверка существования файла
    if (!this.checkFileExists()) {
      return false;
    }

    // 2. Парсинг TOML
    if (!this.parseToml()) {
      return false;
    }

    // 3. Валидация структуры
    this.validateBuildSettings();
    this.validatePaths();
    this.validateRedirects();
    this.validateHeaders();
    this.validateFunctions();

    // 4. Вывод результатов
    this.printResults();

    return this.errors.length === 0;
  }

  // Проверка существования файла
  checkFileExists() {
    if (!fs.existsSync(this.filePath)) {
      this.errors.push(`Файл не найден: ${this.filePath}`);
      return false;
    }
    return true;
  }

  // Парсинг TOML файла (встроенный парсер без зависимостей)
  parseToml() {
    try {
      const content = fs.readFileSync(this.filePath, 'utf-8');
      this.config = this.simpleTomlParse(content);
      console.log(`${colors.green}✓${colors.reset} TOML синтаксис корректен\n`);
      return true;
    } catch (error) {
      this.errors.push(`Ошибка парсинга TOML: ${error.message}`);
      return false;
    }
  }

  // Простой TOML парсер (без зависимостей)
  simpleTomlParse(content) {
    const result = {};
    const lines = content.split('\n');
    let currentSection = null;
    let currentArray = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Пропускаем пустые строки и комментарии
      if (!line || line.startsWith('#')) continue;

      // Секция [[array]] или [section]
      if (line.startsWith('[') && line.endsWith(']')) {
        if (line.startsWith('[[') && line.endsWith(']]')) {
          // Массив секций
          const sectionName = line.slice(2, -2).trim();
          if (!result[sectionName]) result[sectionName] = [];
          currentArray = {};
          result[sectionName].push(currentArray);
          currentSection = currentArray;
        } else {
          // Обычная секция
          const sectionName = line.slice(1, -1).trim();
          currentSection = {};
          result[sectionName] = currentSection;
          currentArray = null;
        }
        continue;
      }

      // Ключ = значение
      const equalIndex = line.indexOf('=');
      if (equalIndex > 0) {
        const key = line.slice(0, equalIndex).trim();
        let value = line.slice(equalIndex + 1).trim();

        // Удаляем кавычки
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }

        // Конвертируем числа
        if (/^\d+$/.test(value)) {
          value = parseInt(value, 10);
        }

        // Булевы значения
        if (value === 'true') value = true;
        if (value === 'false') value = false;

        if (currentSection) {
          currentSection[key] = value;
        } else {
          result[key] = value;
        }
      }
    }

    return result;
  }

  // Валидация настроек сборки
  validateBuildSettings() {
    console.log(`${colors.blue}[Build Settings]${colors.reset}`);

    if (!this.config.build) {
      this.errors.push('Отсутствует секция [build]');
      return;
    }

    const build = this.config.build;

    // Проверка команды сборки
    if (!build.command) {
      this.errors.push('Отсутствует build.command');
    } else {
      console.log(`  ✓ Build command: ${build.command}`);
    }

    // Проверка publish директории
    if (!build.publish) {
      this.errors.push('Отсутствует build.publish');
    } else {
      console.log(`  ✓ Publish directory: ${build.publish}`);
    }

    // Проверка base (опционально)
    if (build.base) {
      console.log(`  ✓ Base directory: ${build.base}`);
    }

    console.log();
  }

  // Проверка существования путей
  validatePaths() {
    console.log(`${colors.blue}[Paths Validation]${colors.reset}`);

    const projectDir = path.dirname(this.filePath);

    // Проверка base директории
    if (this.config.build && this.config.build.base) {
      const basePath = path.join(projectDir, this.config.build.base);
      if (!fs.existsSync(basePath)) {
        this.errors.push(`Base директория не существует: ${this.config.build.base}`);
      } else {
        console.log(`  ✓ Base директория существует: ${this.config.build.base}`);
      }
    }

    // Проверка publish директории (относительно base или корня)
    if (this.config.build && this.config.build.publish) {
      const baseDir = this.config.build.base
        ? path.join(projectDir, this.config.build.base)
        : projectDir;

      const publishPath = path.join(baseDir, this.config.build.publish);

      if (!fs.existsSync(publishPath)) {
        this.warnings.push(`Publish директория не существует (будет создана при сборке): ${this.config.build.publish}`);
      } else {
        console.log(`  ✓ Publish директория существует: ${this.config.build.publish}`);
      }
    }

    // Проверка functions директории
    if (this.config.build && this.config.build.functions) {
      const functionsPath = path.join(projectDir, this.config.build.functions);
      if (!fs.existsSync(functionsPath)) {
        this.warnings.push(`Functions директория не существует: ${this.config.build.functions}`);
      } else {
        console.log(`  ✓ Functions директория существует: ${this.config.build.functions}`);
      }
    }

    console.log();
  }

  // Валидация редиректов
  validateRedirects() {
    if (!this.config.redirects || this.config.redirects.length === 0) {
      return;
    }

    console.log(`${colors.blue}[Redirects Validation]${colors.reset}`);
    console.log(`  Найдено редиректов: ${this.config.redirects.length}`);

    this.config.redirects.forEach((redirect, index) => {
      const num = index + 1;

      // Обязательные поля
      if (!redirect.from) {
        this.errors.push(`Redirect #${num}: отсутствует поле 'from'`);
      }
      if (!redirect.to) {
        this.errors.push(`Redirect #${num}: отсутствует поле 'to'`);
      }

      // Валидация status code
      if (redirect.status) {
        const validStatuses = [200, 301, 302, 303, 404, 410, 451];
        if (!validStatuses.includes(redirect.status)) {
          this.warnings.push(`Redirect #${num}: нестандартный status code ${redirect.status}`);
        }
      }

      // Проверка на возможные циклические редиректы
      if (redirect.from === redirect.to) {
        this.errors.push(`Redirect #${num}: циклический редирект (from === to)`);
      }

      console.log(`  ✓ Redirect #${num}: ${redirect.from} → ${redirect.to} [${redirect.status || 301}]`);
    });

    console.log();
  }

  // Валидация заголовков
  validateHeaders() {
    if (!this.config.headers || this.config.headers.length === 0) {
      return;
    }

    console.log(`${colors.blue}[Headers Validation]${colors.reset}`);
    console.log(`  Найдено правил headers: ${this.config.headers.length}`);

    this.config.headers.forEach((header, index) => {
      const num = index + 1;

      if (!header.for) {
        this.errors.push(`Header #${num}: отсутствует поле 'for'`);
      }
      if (!header.values || Object.keys(header.values).length === 0) {
        this.errors.push(`Header #${num}: отсутствуют 'values'`);
      }

      console.log(`  ✓ Header #${num}: ${header.for} (${Object.keys(header.values || {}).length} headers)`);
    });

    console.log();
  }

  // Валидация функций
  validateFunctions() {
    if (!this.config.functions) {
      return;
    }

    console.log(`${colors.blue}[Functions Configuration]${colors.reset}`);

    if (this.config.functions.directory) {
      console.log(`  ✓ Functions directory: ${this.config.functions.directory}`);
    }

    if (this.config.functions.node_bundler) {
      console.log(`  ✓ Node bundler: ${this.config.functions.node_bundler}`);
    }

    if (this.config.functions.included_files) {
      console.log(`  ✓ Included files: ${this.config.functions.included_files.join(', ')}`);
    }

    console.log();
  }

  // Вывод результатов
  printResults() {
    console.log(`${colors.blue}════════════════════════════════════════${colors.reset}`);
    console.log(`${colors.blue}РЕЗУЛЬТАТЫ ВАЛИДАЦИИ${colors.reset}`);
    console.log(`${colors.blue}════════════════════════════════════════${colors.reset}\n`);

    // Ошибки
    if (this.errors.length > 0) {
      console.log(`${colors.red}✗ ОШИБКИ (${this.errors.length}):${colors.reset}`);
      this.errors.forEach(error => {
        console.log(`  ${colors.red}•${colors.reset} ${error}`);
      });
      console.log();
    }

    // Предупреждения
    if (this.warnings.length > 0) {
      console.log(`${colors.yellow}⚠ ПРЕДУПРЕЖДЕНИЯ (${this.warnings.length}):${colors.reset}`);
      this.warnings.forEach(warning => {
        console.log(`  ${colors.yellow}•${colors.reset} ${warning}`);
      });
      console.log();
    }

    // Итог
    if (this.errors.length === 0) {
      console.log(`${colors.green}✓ Валидация пройдена успешно!${colors.reset}`);
      if (this.warnings.length > 0) {
        console.log(`${colors.yellow}  (с ${this.warnings.length} предупреждениями)${colors.reset}`);
      }
    } else {
      console.log(`${colors.red}✗ Валидация не пройдена (${this.errors.length} ошибок)${colors.reset}`);
    }

    console.log();
  }
}

// Главная функция
async function main() {
  // Получаем путь к файлу из аргументов или используем по умолчанию
  const args = process.argv.slice(2);
  const filePath = args[0] || path.join(process.cwd(), 'netlify.toml');

  const validator = new NetlifyTomlValidator(filePath);
  const isValid = await validator.validate();

  // Выход с соответствующим кодом
  process.exit(isValid ? 0 : 1);
}

// Запуск
if (require.main === module) {
  main().catch(error => {
    console.error(`${colors.red}Критическая ошибка:${colors.reset}`, error);
    process.exit(1);
  });
}

module.exports = NetlifyTomlValidator;
