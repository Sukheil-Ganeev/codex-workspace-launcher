#!/bin/bash
# Fork Sync Helper
# Синхронизация форка с upstream репозиторием
#
# Использование:
#   ./sync-fork.sh
#   ./sync-fork.sh --branch develop  # синхронизировать другую ветку
#
# Скрипт проверит наличие upstream, получит обновления и смержит их

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функции для вывода
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

# Разбор аргументов
BRANCH="main"
while [[ $# -gt 0 ]]; do
    case $1 in
        --branch|-b)
            BRANCH="$2"
            shift 2
            ;;
        --help|-h)
            echo "Использование: $0 [--branch <branch-name>]"
            echo "Синхронизация форка с upstream репозиторием"
            echo ""
            echo "Опции:"
            echo "  --branch, -b <name>  Ветка для синхронизации (по умолчанию: main)"
            echo "  --help, -h           Показать эту справку"
            exit 0
            ;;
        *)
            print_error "Неизвестная опция: $1"
            exit 1
            ;;
    esac
done

# Проверка что мы в Git репозитории
if [ ! -d ".git" ]; then
    print_error "Это не Git репозиторий!"
    exit 1
fi

# Проверка наличия несохранённых изменений
if ! git diff-index --quiet HEAD --; then
    print_error "Есть несохранённые изменения!"
    echo "Сохраните или спрячьте изменения перед синхронизацией:"
    echo "  git stash"
    echo "  git add . && git commit -m 'message'"
    exit 1
fi

# Проверка текущей ветки
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    print_warning "Вы находитесь в ветке '$CURRENT_BRANCH', переключаюсь на '$BRANCH'..."
    git checkout "$BRANCH"
    print_success "Переключено на ветку '$BRANCH'"
fi

# Проверка наличия upstream remote
print_step "Проверка upstream remote..."
if ! git remote get-url upstream &> /dev/null; then
    print_warning "Upstream remote не настроен"
    echo
    echo "Для синхронизации форка нужно настроить upstream remote."
    echo "Upstream - это оригинальный репозиторий, от которого был создан форк."
    echo
    read -p "Введите URL оригинального репозитория: " upstream_url

    if [ -z "$upstream_url" ]; then
        print_error "URL не может быть пустым"
        exit 1
    fi

    git remote add upstream "$upstream_url"
    print_success "Upstream remote добавлен: $upstream_url"
else
    UPSTREAM_URL=$(git remote get-url upstream)
    print_success "Upstream remote найден: $UPSTREAM_URL"
fi

# Получение обновлений из upstream
print_step "Получение обновлений из upstream..."
git fetch upstream
print_success "Обновления получены"

# Проверка наличия ветки в upstream
if ! git rev-parse --verify upstream/$BRANCH &> /dev/null; then
    print_error "Ветка '$BRANCH' не найдена в upstream!"
    echo "Доступные ветки в upstream:"
    git branch -r | grep upstream/
    exit 1
fi

# Показ статистики изменений
echo
print_step "Статистика изменений:"
COMMITS_BEHIND=$(git rev-list --count HEAD..upstream/$BRANCH)
COMMITS_AHEAD=$(git rev-list --count upstream/$BRANCH..HEAD)

echo "  Коммитов позади upstream: $COMMITS_BEHIND"
echo "  Коммитов впереди upstream: $COMMITS_AHEAD"

if [ "$COMMITS_BEHIND" -eq 0 ]; then
    print_success "Форк уже синхронизирован с upstream!"

    if [ "$COMMITS_AHEAD" -gt 0 ]; then
        echo
        read -p "Отправить ваши изменения в origin? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin "$BRANCH"
            print_success "Изменения отправлены в origin"
        fi
    fi

    exit 0
fi

# Показ новых коммитов
if [ "$COMMITS_BEHIND" -gt 0 ]; then
    echo
    print_step "Новые коммиты в upstream:"
    git log --oneline HEAD..upstream/$BRANCH | head -n 10
    if [ "$COMMITS_BEHIND" -gt 10 ]; then
        echo "  ... и ещё $(($COMMITS_BEHIND - 10)) коммитов"
    fi
fi

# Подтверждение merge
echo
read -p "Выполнить merge с upstream/$BRANCH? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Синхронизация отменена"
    exit 0
fi

# Merge upstream в локальную ветку
print_step "Выполняется merge с upstream/$BRANCH..."

# Попытка merge
if git merge upstream/$BRANCH --no-edit; then
    print_success "Merge выполнен успешно!"
else
    print_error "Возникли конфликты при merge!"
    echo
    echo "Конфликтующие файлы:"
    git diff --name-only --diff-filter=U
    echo
    echo "Для разрешения конфликтов:"
    echo "  1. Отредактируйте конфликтующие файлы"
    echo "  2. Отметьте как разрешённые: git add <файл>"
    echo "  3. Завершите merge: git commit"
    echo "  4. Отправьте изменения: git push origin $BRANCH"
    echo
    echo "Для отмены merge: git merge --abort"
    exit 1
fi

# Отправка обновлений в origin
echo
read -p "Отправить обновления в ваш форк (origin)? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_step "Отправка обновлений в origin..."
    git push origin "$BRANCH"
    print_success "Обновления отправлены в origin"
fi

# Итог
echo
print_success "Синхронизация завершена!"
echo
echo "Статус:"
echo "  • Локальная ветка '$BRANCH' синхронизирована с upstream"
echo "  • Изменения отправлены в ваш форк (origin)"
echo
if [ "$COMMITS_AHEAD" -gt 0 ]; then
    print_warning "У вас есть $COMMITS_AHEAD локальных коммита(ов), которые не в upstream"
    echo "Возможно, вы хотите создать Pull Request?"
fi
