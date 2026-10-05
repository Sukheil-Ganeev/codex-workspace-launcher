#!/bin/bash
# Git Repository Init Helper
# Быстрая инициализация нового Git репозитория с настройками
#
# Использование:
#   ./init-repo-helper.sh [project-name]
#   ./init-repo-helper.sh my-awesome-project
#
# Если project-name не указан, будет использовано имя текущей папки

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода цветных сообщений
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Получение имени проекта
if [ -z "$1" ]; then
    PROJECT_NAME=$(basename "$PWD")
    print_warning "Имя проекта не указано, использую имя папки: $PROJECT_NAME"
else
    PROJECT_NAME="$1"
fi

# Проверка что мы не в существующем Git репозитории
if [ -d ".git" ]; then
    print_error "Эта папка уже является Git репозиторием!"
    read -p "Переинициализировать? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 1. Инициализация Git репозитория
print_step "Инициализация Git репозитория..."
git init
print_success "Git репозиторий инициализирован"

# 2. Создание .gitignore
print_step "Создание .gitignore..."
echo "Выберите шаблон .gitignore:"
echo "  1) Node.js"
echo "  2) Python"
echo "  3) Java"
echo "  4) C/C++"
echo "  5) Go"
echo "  6) Базовый (OS, IDE)"
echo "  0) Пропустить"
read -p "Ваш выбор [6]: " gitignore_choice
gitignore_choice=${gitignore_choice:-6}

case $gitignore_choice in
    1)
        cat > .gitignore << 'EOF'
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache
dist/
build/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
        ;;
    2)
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
        ;;
    3)
        cat > .gitignore << 'EOF'
# Java
*.class
*.log
*.jar
*.war
*.ear
target/
.gradle/
build/
.mvn/

# IDE
.vscode/
.idea/
*.iml
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
        ;;
    4)
        cat > .gitignore << 'EOF'
# C/C++
*.o
*.obj
*.exe
*.out
*.app
*.dll
*.so
*.dylib
*.a
*.lib
build/
cmake-build-*/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
        ;;
    5)
        cat > .gitignore << 'EOF'
# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/
go.work

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
        ;;
    6)
        cat > .gitignore << 'EOF'
# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Temporary files
*.tmp
*.bak
*.log
EOF
        ;;
    0)
        print_warning ".gitignore пропущен"
        ;;
esac

if [ $gitignore_choice -ne 0 ]; then
    print_success ".gitignore создан"
fi

# 3. Создание README.md
if [ ! -f "README.md" ]; then
    print_step "Создание README.md..."
    cat > README.md << EOF
# $PROJECT_NAME

Описание проекта.

## Установка

\`\`\`bash
# Команды для установки
\`\`\`

## Использование

\`\`\`bash
# Примеры использования
\`\`\`

## Лицензия

[Выберите лицензию]
EOF
    print_success "README.md создан"
else
    print_warning "README.md уже существует, пропускаю"
fi

# 4. Initial commit
print_step "Создание initial commit..."
git add .
git commit -m "Initial commit: setup project structure" --quiet
print_success "Initial commit создан"

# 5. Создание GitHub репозитория (опционально)
if command -v gh &> /dev/null; then
    echo
    read -p "Создать репозиторий на GitHub? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Создание GitHub репозитория..."

        echo "Выберите видимость:"
        echo "  1) Public"
        echo "  2) Private"
        read -p "Ваш выбор [1]: " visibility_choice
        visibility_choice=${visibility_choice:-1}

        if [ "$visibility_choice" = "2" ]; then
            visibility="--private"
        else
            visibility="--public"
        fi

        gh repo create "$PROJECT_NAME" $visibility --source=. --remote=origin --push
        print_success "GitHub репозиторий создан и код загружен"
    fi
else
    print_warning "GitHub CLI (gh) не установлен, пропускаю создание репозитория на GitHub"
    echo
    read -p "Добавить remote origin вручную? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Введите URL репозитория: " repo_url
        git remote add origin "$repo_url"
        print_success "Remote origin добавлен: $repo_url"
        echo
        print_warning "Не забудьте выполнить: git push -u origin main"
    fi
fi

# Итоговая информация
echo
print_success "Репозиторий готов к работе!"
echo
echo "Следующие шаги:"
echo "  1. Отредактируйте README.md"
echo "  2. Добавьте свои файлы"
echo "  3. Создайте коммиты: git add . && git commit -m 'message'"
if ! git remote get-url origin &> /dev/null; then
    echo "  4. Добавьте remote: git remote add origin <url>"
    echo "  5. Отправьте код: git push -u origin main"
else
    echo "  4. Отправьте код: git push"
fi
