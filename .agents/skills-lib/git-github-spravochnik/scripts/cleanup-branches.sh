#!/bin/bash
# Cleanup Merged Branches
# Удаление локальных и remote веток, которые уже смержены
#
# Использование:
#   ./cleanup-branches.sh           # интерактивный режим
#   ./cleanup-branches.sh --dry-run # показать что будет удалено
#   ./cleanup-branches.sh --auto    # автоматическое удаление без подтверждения
#   ./cleanup-branches.sh --remote  # также удалить remote ветки
#
# Скрипт защищает основные ветки (main, master, develop) от удаления

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
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

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Параметры по умолчанию
DRY_RUN=false
AUTO_MODE=false
CLEAN_REMOTE=false

# Разбор аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --remote|-r)
            CLEAN_REMOTE=true
            shift
            ;;
        --help|-h)
            echo "Использование: $0 [опции]"
            echo "Удаление смерженных веток"
            echo ""
            echo "Опции:"
            echo "  --dry-run, -n   Показать что будет удалено (без удаления)"
            echo "  --auto, -a      Автоматическое удаление без подтверждения"
            echo "  --remote, -r    Также удалить remote ветки"
            echo "  --help, -h      Показать эту справку"
            echo ""
            echo "Защищённые ветки (не будут удалены):"
            echo "  main, master, develop, staging, production"
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

# Защищённые ветки (не будут удалены)
PROTECTED_BRANCHES=("main" "master" "develop" "staging" "production")

# Функция проверки защищённой ветки
is_protected() {
    local branch=$1
    for protected in "${PROTECTED_BRANCHES[@]}"; do
        if [ "$branch" = "$protected" ]; then
            return 0
        fi
    done
    return 1
}

# Получение текущей ветки
CURRENT_BRANCH=$(git branch --show-current)
print_info "Текущая ветка: $CURRENT_BRANCH"

# Определение базовой ветки (main или master)
if git show-ref --verify --quiet refs/heads/main; then
    BASE_BRANCH="main"
elif git show-ref --verify --quiet refs/heads/master; then
    BASE_BRANCH="master"
else
    print_error "Не найдена базовая ветка (main или master)"
    exit 1
fi

print_info "Базовая ветка: $BASE_BRANCH"
echo

# Обновление информации о remote ветках
if [ "$CLEAN_REMOTE" = true ]; then
    print_step "Обновление информации о remote ветках..."
    git fetch --prune
    print_success "Информация обновлена"
    echo
fi

# === ЛОКАЛЬНЫЕ ВЕТКИ ===
print_step "Поиск смерженных локальных веток..."

# Получение списка смерженных веток (исключая текущую и защищённые)
MERGED_BRANCHES=()
while IFS= read -r branch; do
    # Удаление пробелов и *
    branch=$(echo "$branch" | sed 's/^[* ]*//')

    # Пропуск текущей ветки и защищённых
    if [ "$branch" = "$CURRENT_BRANCH" ]; then
        continue
    fi

    if is_protected "$branch"; then
        continue
    fi

    MERGED_BRANCHES+=("$branch")
done < <(git branch --merged "$BASE_BRANCH" | grep -v "^*")

# Если нет смерженных веток
if [ ${#MERGED_BRANCHES[@]} -eq 0 ]; then
    print_success "Нет смерженных веток для удаления"
else
    echo "Найдено смерженных веток: ${#MERGED_BRANCHES[@]}"
    echo

    for branch in "${MERGED_BRANCHES[@]}"; do
        # Получение даты последнего коммита
        LAST_COMMIT_DATE=$(git log -1 --format="%ar" "$branch")
        echo "  • $branch (последний коммит: $LAST_COMMIT_DATE)"
    done
    echo

    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN: Эти ветки были бы удалены"
    else
        # Подтверждение удаления
        if [ "$AUTO_MODE" = false ]; then
            read -p "Удалить эти ветки? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_warning "Удаление отменено"
                MERGED_BRANCHES=()
            fi
        fi

        # Удаление веток
        if [ ${#MERGED_BRANCHES[@]} -gt 0 ]; then
            for branch in "${MERGED_BRANCHES[@]}"; do
                if git branch -d "$branch" 2>/dev/null; then
                    print_success "Удалена: $branch"
                else
                    print_error "Не удалось удалить: $branch (возможно, не полностью смержена)"
                    read -p "Принудительно удалить? (y/N): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        git branch -D "$branch"
                        print_success "Принудительно удалена: $branch"
                    fi
                fi
            done
        fi
    fi
fi

# === REMOTE ВЕТКИ ===
if [ "$CLEAN_REMOTE" = true ]; then
    echo
    print_step "Поиск смерженных remote веток..."

    # Получение списка remote веток
    REMOTE_MERGED_BRANCHES=()

    # Получаем список веток на remote
    while IFS= read -r branch; do
        # Извлечение имени ветки (убираем origin/)
        branch_name=$(echo "$branch" | sed 's|origin/||')

        # Пропуск HEAD и защищённых веток
        if [[ "$branch_name" == "HEAD" ]] || is_protected "$branch_name"; then
            continue
        fi

        # Проверка что ветка смержена в базовую ветку
        if git branch -r --merged "origin/$BASE_BRANCH" | grep -q "origin/$branch_name"; then
            REMOTE_MERGED_BRANCHES+=("$branch_name")
        fi
    done < <(git branch -r | grep "origin/" | sed 's/^  //')

    if [ ${#REMOTE_MERGED_BRANCHES[@]} -eq 0 ]; then
        print_success "Нет смерженных remote веток для удаления"
    else
        echo "Найдено смерженных remote веток: ${#REMOTE_MERGED_BRANCHES[@]}"
        echo

        for branch in "${REMOTE_MERGED_BRANCHES[@]}"; do
            echo "  • origin/$branch"
        done
        echo

        if [ "$DRY_RUN" = true ]; then
            print_warning "DRY RUN: Эти remote ветки были бы удалены"
        else
            print_warning "Это удалит ветки на remote сервере!"

            # Подтверждение удаления
            if [ "$AUTO_MODE" = false ]; then
                read -p "Удалить эти remote ветки? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    print_warning "Удаление remote веток отменено"
                    REMOTE_MERGED_BRANCHES=()
                fi
            fi

            # Удаление remote веток
            if [ ${#REMOTE_MERGED_BRANCHES[@]} -gt 0 ]; then
                for branch in "${REMOTE_MERGED_BRANCHES[@]}"; do
                    if git push origin --delete "$branch" 2>/dev/null; then
                        print_success "Удалена remote ветка: origin/$branch"
                    else
                        print_error "Не удалось удалить: origin/$branch"
                    fi
                done
            fi
        fi
    fi
fi

# Итоговая статистика
echo
print_success "Очистка завершена!"

if [ "$DRY_RUN" = false ]; then
    echo
    print_info "Текущие ветки:"
    git branch -vv
fi
