#!/bin/bash
# Vercel Setup Helper
# Автоматическая установка и настройка Vercel CLI
# Использование: ./setup-vercel.sh

set -e

echo "=================================="
echo "  Vercel Setup Helper"
echo "=================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода успешных сообщений
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Функция для вывода ошибок
error() {
    echo -e "${RED}✗${NC} $1"
}

# Функция для вывода предупреждений
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Функция для вывода информации
info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# 1. Проверка Node.js
echo "Шаг 1: Проверка Node.js..."
if ! command -v node &> /dev/null; then
    error "Node.js не установлен!"
    info "Установите Node.js с https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v)
success "Node.js установлен: $NODE_VERSION"
echo ""

# 2. Выбор пакетного менеджера
echo "Шаг 2: Выбор пакетного менеджера..."
echo "Какой пакетный менеджер использовать?"
echo "1) npm (по умолчанию)"
echo "2) pnpm"
echo "3) yarn"
read -p "Ваш выбор [1-3]: " pm_choice

case $pm_choice in
    2)
        PM="pnpm"
        INSTALL_CMD="pnpm add -g"
        ;;
    3)
        PM="yarn"
        INSTALL_CMD="yarn global add"
        ;;
    *)
        PM="npm"
        INSTALL_CMD="npm install -g"
        ;;
esac

success "Выбран: $PM"
echo ""

# 3. Установка Vercel CLI
echo "Шаг 3: Проверка Vercel CLI..."
if command -v vercel &> /dev/null; then
    VERCEL_VERSION=$(vercel --version)
    warning "Vercel CLI уже установлен: $VERCEL_VERSION"
    read -p "Переустановить? [y/N]: " reinstall
    if [[ $reinstall =~ ^[Yy]$ ]]; then
        echo "Переустановка Vercel CLI..."
        $INSTALL_CMD vercel
        success "Vercel CLI переустановлен"
    fi
else
    echo "Установка Vercel CLI..."
    $INSTALL_CMD vercel
    success "Vercel CLI установлен"
fi
echo ""

# 4. Авторизация в Vercel
echo "Шаг 4: Авторизация в Vercel..."
if vercel whoami &> /dev/null; then
    VERCEL_USER=$(vercel whoami)
    success "Вы уже залогинены как: $VERCEL_USER"
    read -p "Перелогиниться? [y/N]: " relogin
    if [[ $relogin =~ ^[Yy]$ ]]; then
        vercel logout
        vercel login
    fi
else
    info "Откроется браузер для авторизации..."
    sleep 2
    vercel login
    success "Авторизация завершена"
fi
echo ""

# 5. Линковка проекта
echo "Шаг 5: Настройка проекта..."
read -p "Настроить текущую директорию как Vercel проект? [Y/n]: " setup_project

if [[ ! $setup_project =~ ^[Nn]$ ]]; then
    # Проверка наличия vercel.json
    if [ -f "vercel.json" ]; then
        warning "vercel.json уже существует"
    else
        echo ""
        echo "Выберите шаблон vercel.json:"
        echo "1) Статичный сайт (static)"
        echo "2) Статичный сайт + API (static + serverless)"
        echo "3) Next.js"
        echo "4) SPA (React/Vue с client-side routing)"
        echo "5) Пропустить создание vercel.json"
        read -p "Ваш выбор [1-5]: " template_choice
        
        TEMPLATES_DIR="$HOME/.claude/skills/vercel-деплой/assets/templates"
        
        case $template_choice in
            1)
                cp "$TEMPLATES_DIR/vercel-static-basic.json" "vercel.json"
                success "Создан vercel.json для статичного сайта"
                ;;
            2)
                cp "$TEMPLATES_DIR/vercel-static-with-api.json" "vercel.json"
                success "Создан vercel.json для статичного сайта + API"
                ;;
            3)
                cp "$TEMPLATES_DIR/vercel-nextjs.json" "vercel.json"
                success "Создан vercel.json для Next.js"
                ;;
            4)
                cp "$TEMPLATES_DIR/vercel-spa.json" "vercel.json"
                success "Создан vercel.json для SPA"
                ;;
            5)
                info "Создание vercel.json пропущено"
                ;;
            *)
                warning "Неверный выбор, пропускаю создание vercel.json"
                ;;
        esac
    fi
    
    echo ""
    info "Запуск vercel link для линковки проекта..."
    vercel link
    success "Проект настроен"
else
    info "Настройка проекта пропущена"
fi

echo ""
echo "=================================="
echo "  ✓ Установка завершена!"
echo "=================================="
echo ""
echo "Следующие шаги:"
echo "1. Для деплоя preview: vercel"
echo "2. Для деплоя production: vercel --prod"
echo "3. Для локальной разработки: vercel dev"
echo "4. Для просмотра логов: vercel logs"
echo ""
echo "Документация: https://vercel.com/docs"
echo ""
