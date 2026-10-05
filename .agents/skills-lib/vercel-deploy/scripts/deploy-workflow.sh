#!/bin/bash
# Vercel Deploy Workflow
# Упрощённый workflow деплоя с проверками
# Использование: ./deploy-workflow.sh [preview|production]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

echo "=================================="
echo "  Vercel Deploy Workflow"
echo "=================================="
echo ""

# Определить режим деплоя
DEPLOY_MODE=${1:-preview}

if [ "$DEPLOY_MODE" != "preview" ] && [ "$DEPLOY_MODE" != "production" ]; then
    error "Неверный режим. Используйте: preview или production"
    exit 1
fi

if [ "$DEPLOY_MODE" = "production" ]; then
    info "Режим: Production Deploy"
else
    info "Режим: Preview Deploy"
fi
echo ""

# PRE-DEPLOY ПРОВЕРКИ
echo "=== Pre-deploy проверки ==="
echo ""

# 1. Проверка Vercel CLI
info "Проверка Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    error "Vercel CLI не установлен!"
    info "Установите: npm install -g vercel"
    exit 1
fi
success "Vercel CLI доступен"

# 2. Проверка авторизации
info "Проверка авторизации..."
if ! vercel whoami &> /dev/null; then
    error "Вы не залогинены в Vercel!"
    info "Выполните: vercel login"
    exit 1
fi
VERCEL_USER=$(vercel whoami)
success "Залогинен как: $VERCEL_USER"

# 3. Проверка vercel.json (если существует)
if [ -f "vercel.json" ]; then
    info "Валидация vercel.json..."
    
    # Использовать Node.js для валидации JSON
    if node -e "JSON.parse(require('fs').readFileSync('vercel.json', 'utf8'))" 2> /dev/null; then
        success "vercel.json валиден"
    else
        error "vercel.json содержит ошибки синтаксиса!"
        info "Используйте: node scripts/validate-config.js"
        exit 1
    fi
else
    warning "vercel.json не найден (опционально)"
fi

# 4. Проверка .vercelignore или .gitignore
if [ -f ".vercelignore" ]; then
    success ".vercelignore найден"
elif [ -f ".gitignore" ]; then
    success ".gitignore найден (будет использован как .vercelignore)"
else
    warning "Нет .vercelignore или .gitignore"
fi

echo ""

# ПОДТВЕРЖДЕНИЕ
if [ "$DEPLOY_MODE" = "production" ]; then
    echo -e "${RED}⚠ ВНИМАНИЕ: Production Deploy${NC}"
    echo ""
    read -p "Вы уверены, что хотите задеплоить в production? [y/N]: " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        info "Деплой отменен"
        exit 0
    fi
fi

echo ""
echo "=== Начало деплоя ==="
echo ""

# ДЕПЛОЙ
DEPLOY_START=$(date +%s)

if [ "$DEPLOY_MODE" = "production" ]; then
    info "Запуск production деплоя..."
    vercel --prod 2>&1 | tee deploy.log
else
    info "Запуск preview деплоя..."
    vercel 2>&1 | tee deploy.log
fi

DEPLOY_END=$(date +%s)
DEPLOY_TIME=$((DEPLOY_END - DEPLOY_START))

echo ""
success "Деплой завершен за ${DEPLOY_TIME}s"
echo ""

# ПОЛУЧЕНИЕ DEPLOYMENT URL
echo "=== Информация о деплое ==="
echo ""

if [ "$DEPLOY_MODE" = "production" ]; then
    DEPLOYMENT_URL=$(grep -oP 'https://[^\s]+' deploy.log | tail -1)
    info "Production URL: $DEPLOYMENT_URL"
else
    DEPLOYMENT_URL=$(grep -oP 'https://[^\s]+' deploy.log | tail -1)
    info "Preview URL: $DEPLOYMENT_URL"
fi

# Получить информацию о последнем деплое
echo ""
info "Получение информации о деплое..."
vercel inspect $(basename $DEPLOYMENT_URL) 2>/dev/null || true

echo ""

# ОПЦИИ ПОСЛЕ ДЕПЛОЯ
echo "=== Что дальше? ==="
echo ""
echo "1. Открыть в браузере"
echo "2. Посмотреть логи"
echo "3. Скопировать URL в буфер обмена"
echo "4. Завершить"
echo ""
read -p "Выберите действие [1-4]: " action

case $action in
    1)
        info "Открываю в браузере..."
        if command -v xdg-open &> /dev/null; then
            xdg-open "$DEPLOYMENT_URL"
        elif command -v open &> /dev/null; then
            open "$DEPLOYMENT_URL"
        else
            start "$DEPLOYMENT_URL" 2>/dev/null || warning "Не удалось открыть браузер"
        fi
        ;;
    2)
        info "Получение логов..."
        vercel logs
        ;;
    3)
        info "Копирование URL..."
        echo "$DEPLOYMENT_URL" | clip.exe 2>/dev/null || \
        echo "$DEPLOYMENT_URL" | pbcopy 2>/dev/null || \
        echo "$DEPLOYMENT_URL" | xclip -selection clipboard 2>/dev/null || \
        warning "Не удалось скопировать (скопируйте вручную): $DEPLOYMENT_URL"
        success "URL скопирован в буфер обмена"
        ;;
    4)
        info "Завершение"
        ;;
    *)
        warning "Неверный выбор"
        ;;
esac

# Очистка временного лог файла
rm -f deploy.log

echo ""
success "Готово!"
echo ""
