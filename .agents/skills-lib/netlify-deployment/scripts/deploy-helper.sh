#!/bin/bash

###############################################################################
# Netlify Deploy Helper
#
# ИСПОЛЬЗОВАНИЕ:
#   ./deploy-helper.sh [preview|production]
#   ./deploy-helper.sh preview --message "Test deploy"
#   ./deploy-helper.sh production
#
# ОПИСАНИЕ:
#   - Проверяет наличие Netlify CLI
#   - Выполняет pre-deploy валидацию (netlify.toml, package.json)
#   - Деплоит с логированием
#   - Выполняет post-deploy проверки (HTTP status)
#   - Показывает deployment URL и последние деплои
#
# ОПЦИИ:
#   preview     - Deploy в preview environment
#   production  - Deploy в production (требует подтверждение)
#   --message   - Кастомное сообщение деплоя
#   --skip-validation - Пропустить валидацию
#
# ТРЕБОВАНИЯ:
#   - Netlify CLI (npm install -g netlify-cli)
#   - Node.js для валидации
#   - Авторизация (netlify login)
#   - Привязка к сайту (netlify link)
###############################################################################

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Переменные
DEPLOY_TYPE=""
DEPLOY_MESSAGE=""
SKIP_VALIDATION=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE=""

###############################################################################
# Вспомогательные функции
###############################################################################

print_header() {
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Функция для логирования
log_message() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$message" >> "$LOG_FILE"
}

###############################################################################
# Проверки окружения
###############################################################################

check_netlify_cli() {
    print_info "Проверка Netlify CLI..."

    if ! command -v netlify &> /dev/null; then
        print_error "Netlify CLI не установлен"
        echo ""
        echo "Установите с помощью:"
        echo "  npm install -g netlify-cli"
        echo ""
        exit 1
    fi

    local version=$(netlify --version 2>&1 | head -n 1)
    print_success "Netlify CLI найден: $version"
}

check_authentication() {
    print_info "Проверка авторизации..."

    if ! netlify status &> /dev/null; then
        print_error "Не авторизованы в Netlify"
        echo ""
        echo "Выполните авторизацию:"
        echo "  netlify login"
        echo ""
        exit 1
    fi

    print_success "Авторизация активна"
}

check_site_linked() {
    print_info "Проверка привязки к сайту..."

    if [ ! -f ".netlify/state.json" ]; then
        print_error "Проект не привязан к Netlify сайту"
        echo ""
        echo "Привяжите сайт с помощью:"
        echo "  netlify link"
        echo ""
        exit 1
    fi

    local site_id=$(cat .netlify/state.json | grep -o '"siteId":"[^"]*"' | cut -d'"' -f4)
    print_success "Проект привязан к сайту: $site_id"
}

###############################################################################
# Валидация
###############################################################################

run_validation() {
    if [ "$SKIP_VALIDATION" = true ]; then
        print_warning "Валидация пропущена (--skip-validation)"
        return 0
    fi

    print_header "PRE-DEPLOY ВАЛИДАЦИЯ"

    # Проверка netlify.toml
    if [ -f "netlify.toml" ]; then
        print_info "Валидация netlify.toml..."

        if [ -f "$SCRIPT_DIR/validate-netlify-toml.js" ]; then
            if node "$SCRIPT_DIR/validate-netlify-toml.js" netlify.toml; then
                print_success "netlify.toml валиден"
            else
                print_error "netlify.toml содержит ошибки"
                echo ""
                read -p "Продолжить деплой? (y/N): " -n 1 -r
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    exit 1
                fi
            fi
        else
            print_warning "Скрипт валидации не найден, пропускаем"
        fi
    else
        print_warning "netlify.toml не найден"
    fi

    # Проверка package.json
    if [ -f "package.json" ]; then
        print_info "Проверка package.json..."

        if ! node -e "JSON.parse(require('fs').readFileSync('package.json', 'utf8'))" 2>/dev/null; then
            print_error "package.json содержит ошибки синтаксиса"
            exit 1
        fi

        print_success "package.json валиден"
    fi

    # Проверка наличия критических файлов
    if [ -f "netlify.toml" ]; then
        local publish_dir=$(grep -E '^\s*publish\s*=' netlify.toml | sed 's/.*=\s*"\([^"]*\)".*/\1/')
        if [ -n "$publish_dir" ] && [ -d "$publish_dir" ]; then
            print_success "Publish директория существует: $publish_dir"
        fi
    fi

    echo ""
}

###############################################################################
# Деплой
###############################################################################

run_build() {
    print_header "СБОРКА ПРОЕКТА"

    # Проверяем наличие build команды в package.json
    if [ -f "package.json" ] && grep -q '"build"' package.json; then
        print_info "Запуск npm run build..."

        if npm run build; then
            print_success "Сборка завершена успешно"
            log_message "BUILD SUCCESS"
        else
            print_error "Ошибка сборки"
            log_message "BUILD FAILED"
            exit 1
        fi
    else
        print_warning "Build скрипт не найден, пропускаем"
    fi

    echo ""
}

deploy_preview() {
    print_header "PREVIEW DEPLOY"

    log_message "Starting preview deploy"

    local deploy_cmd="netlify deploy"

    if [ -n "$DEPLOY_MESSAGE" ]; then
        deploy_cmd="$deploy_cmd --message \"$DEPLOY_MESSAGE\""
    fi

    print_info "Запуск: $deploy_cmd"
    echo ""

    if eval "$deploy_cmd"; then
        print_success "Preview deploy завершён успешно"
        log_message "PREVIEW DEPLOY SUCCESS"
        return 0
    else
        print_error "Preview deploy завершился с ошибкой"
        log_message "PREVIEW DEPLOY FAILED"
        return 1
    fi
}

deploy_production() {
    print_header "PRODUCTION DEPLOY"

    # Подтверждение для production
    echo -e "${YELLOW}⚠ ВЫ СОБИРАЕТЕСЬ ЗАДЕПЛОИТЬ В PRODUCTION${NC}"
    echo ""
    read -p "Вы уверены? (yes/no): " -r
    echo ""

    if [[ ! $REPLY =~ ^(yes|YES)$ ]]; then
        print_warning "Production deploy отменён"
        exit 0
    fi

    log_message "Starting production deploy"

    local deploy_cmd="netlify deploy --prod"

    if [ -n "$DEPLOY_MESSAGE" ]; then
        deploy_cmd="$deploy_cmd --message \"$DEPLOY_MESSAGE\""
    fi

    print_info "Запуск: $deploy_cmd"
    echo ""

    if eval "$deploy_cmd"; then
        print_success "Production deploy завершён успешно"
        log_message "PRODUCTION DEPLOY SUCCESS"
        return 0
    else
        print_error "Production deploy завершился с ошибкой"
        log_message "PRODUCTION DEPLOY FAILED"
        return 1
    fi
}

###############################################################################
# Post-deploy проверки
###############################################################################

post_deploy_checks() {
    print_header "POST-DEPLOY ПРОВЕРКИ"

    # Получаем URL сайта через netlify status
    local site_url=$(netlify status 2>&1 | grep -i "site url" | awk '{print $NF}')

    if [ -z "$site_url" ]; then
        # Альтернативный способ через API
        site_url=$(netlify api getSite 2>&1 | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    fi

    if [ -n "$site_url" ]; then
        print_info "URL сайта: $site_url"

        # Проверка доступности (простой HTTP код)
        if command -v curl &> /dev/null; then
            print_info "Проверка доступности сайта..."

            local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$site_url" --max-time 10)

            if [ "$http_code" = "200" ]; then
                print_success "Сайт доступен (HTTP $http_code)"
                log_message "Site is accessible: $site_url (HTTP $http_code)"
            elif [ "$http_code" = "301" ] || [ "$http_code" = "302" ]; then
                print_success "Сайт доступен с редиректом (HTTP $http_code)"
                log_message "Site is accessible with redirect: $site_url (HTTP $http_code)"
            else
                print_warning "Сайт вернул код: HTTP $http_code"
                log_message "Site returned: HTTP $http_code"
            fi
        else
            print_warning "curl не установлен, пропускаем проверку доступности"
        fi
    else
        print_warning "Не удалось получить URL сайта"
    fi

    # Показываем последние деплои
    print_info "Последние деплои:"
    netlify deploy:list --limit 3 2>&1

    echo ""
}

###############################################################################
# Парсинг аргументов
###############################################################################

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            preview|production)
                DEPLOY_TYPE="$1"
                shift
                ;;
            --message)
                DEPLOY_MESSAGE="$2"
                shift 2
                ;;
            --skip-validation)
                SKIP_VALIDATION=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Неизвестный аргумент: $1"
                echo ""
                show_help
                exit 1
                ;;
        esac
    done

    # Если тип деплоя не указан, спрашиваем
    if [ -z "$DEPLOY_TYPE" ]; then
        echo "Выберите тип деплоя:"
        echo "  1) Preview"
        echo "  2) Production"
        echo ""
        read -p "Ваш выбор (1/2): " -n 1 -r
        echo ""

        case $REPLY in
            1) DEPLOY_TYPE="preview" ;;
            2) DEPLOY_TYPE="production" ;;
            *)
                print_error "Некорректный выбор"
                exit 1
                ;;
        esac
    fi
}

show_help() {
    cat << EOF
Netlify Deploy Helper

ИСПОЛЬЗОВАНИЕ:
    ./deploy-helper.sh [preview|production] [опции]

АРГУМЕНТЫ:
    preview         Deploy в preview environment
    production      Deploy в production

ОПЦИИ:
    --message MSG   Кастомное сообщение деплоя
    --skip-validation  Пропустить pre-deploy валидацию
    --help, -h      Показать эту справку

ПРИМЕРЫ:
    ./deploy-helper.sh preview
    ./deploy-helper.sh production --message "Release v1.2.3"
    ./deploy-helper.sh preview --skip-validation

ТРЕБОВАНИЯ:
    - Netlify CLI (npm install -g netlify-cli)
    - Авторизация (netlify login)
    - Привязка к сайту (netlify link)
EOF
}

###############################################################################
# Главная функция
###############################################################################

main() {
    # Создаём директорию для логов
    mkdir -p "$LOG_DIR"
    LOG_FILE="$LOG_DIR/deploy-$(date +%Y%m%d-%H%M%S).log"

    # Заголовок
    print_header "NETLIFY DEPLOY HELPER"

    log_message "Deploy started"

    # Парсим аргументы
    parse_arguments "$@"

    # Выводим конфигурацию
    print_info "Тип деплоя: $DEPLOY_TYPE"
    if [ -n "$DEPLOY_MESSAGE" ]; then
        print_info "Сообщение: $DEPLOY_MESSAGE"
    fi
    echo ""

    # Проверки окружения
    check_netlify_cli
    check_authentication
    check_site_linked
    echo ""

    # Валидация
    run_validation

    # Сборка (опционально)
    # run_build

    # Деплой
    if [ "$DEPLOY_TYPE" = "preview" ]; then
        deploy_preview
    else
        deploy_production
    fi

    deploy_result=$?
    echo ""

    # Post-deploy проверки
    if [ $deploy_result -eq 0 ]; then
        post_deploy_checks

        print_header "DEPLOY ЗАВЕРШЁН"
        print_success "Все операции выполнены успешно"
        print_info "Логи сохранены в: $LOG_FILE"

        log_message "Deploy completed successfully"
    else
        print_header "DEPLOY ЗАВЕРШЁН С ОШИБКАМИ"
        print_error "Проверьте логи: $LOG_FILE"

        log_message "Deploy failed"
        exit 1
    fi
}

# Запуск
main "$@"
