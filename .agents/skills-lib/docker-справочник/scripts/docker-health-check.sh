#!/usr/bin/env bash
# =============================================================================
# docker-health-check.sh — Проверка здоровья Docker Compose стека
# Docker Engine 29.x | Февраль 2026
# =============================================================================
# Использование:
#   ./docker-health-check.sh                    # проверка всех контейнеров
#   ./docker-health-check.sh --compose          # проверка Compose стека (текущая папка)
#   ./docker-health-check.sh --compose /opt/app # проверка стека в указанной папке
#   ./docker-health-check.sh --service app db   # проверка указанных сервисов
#
# Коды возврата:
#   0 — все сервисы здоровы
#   1 — есть проблемные сервисы
#   2 — ошибка запуска скрипта
# =============================================================================

set -euo pipefail

# --- Цвета ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Счётчики ---
HEALTHY=0
UNHEALTHY=0
STARTING=0
NO_HEALTHCHECK=0
STOPPED=0

# --- Функции ---
log_ok()    { echo -e "  ${GREEN}[OK]${NC}      $*"; }
log_warn()  { echo -e "  ${YELLOW}[WARN]${NC}    $*"; }
log_fail()  { echo -e "  ${RED}[FAIL]${NC}    $*"; }
log_info()  { echo -e "  ${BLUE}[INFO]${NC}    $*"; }

# Проверка Docker
check_docker() {
    if ! command -v docker &>/dev/null; then
        echo -e "${RED}Docker не установлен или не в PATH${NC}"
        exit 2
    fi
    if ! docker info &>/dev/null; then
        echo -e "${RED}Docker daemon не запущен${NC}"
        exit 2
    fi
}

# Проверка одного контейнера
check_container() {
    local container="$1"
    local name state health status image

    name=$(docker inspect "$container" --format '{{.Name}}' 2>/dev/null | sed 's/^\/\?//')
    state=$(docker inspect "$container" --format '{{.State.Status}}' 2>/dev/null)
    health=$(docker inspect "$container" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null)
    image=$(docker inspect "$container" --format '{{.Config.Image}}' 2>/dev/null)

    # Контейнер остановлен
    if [ "$state" != "running" ]; then
        log_fail "$name -- $state (image: $image)"
        ((STOPPED++)) || true
        return
    fi

    # Проверка healthcheck
    case "$health" in
        healthy)
            log_ok "$name -- healthy (image: $image)"
            ((HEALTHY++)) || true
            ;;
        unhealthy)
            log_fail "$name -- UNHEALTHY (image: $image)"
            # Показываем последний лог healthcheck
            local last_log
            last_log=$(docker inspect "$container" --format '{{if .State.Health}}{{(index .State.Health.Log 0).Output}}{{end}}' 2>/dev/null | head -1)
            if [ -n "$last_log" ]; then
                echo -e "           Лог: $last_log"
            fi
            ((UNHEALTHY++)) || true
            ;;
        starting)
            log_warn "$name -- starting (image: $image)"
            ((STARTING++)) || true
            ;;
        none)
            log_info "$name -- running, нет healthcheck (image: $image)"
            ((NO_HEALTHCHECK++)) || true
            ;;
    esac
}

# Проверка ресурсов системы
check_system_resources() {
    echo ""
    echo "=== Системные ресурсы ==="

    # Использование диска Docker
    local disk_usage
    disk_usage=$(docker system df --format "table {{.Type}}\t{{.Size}}\t{{.Reclaimable}}" 2>/dev/null)
    echo "$disk_usage"

    # Предупреждение если много dangling images
    local dangling
    dangling=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l)
    if [ "$dangling" -gt 5 ]; then
        echo ""
        log_warn "Dangling images: $dangling (запусти docker image prune -f)"
    fi

    # Предупреждение если много остановленных контейнеров
    local stopped_containers
    stopped_containers=$(docker ps -f "status=exited" -q 2>/dev/null | wc -l)
    if [ "$stopped_containers" -gt 3 ]; then
        log_warn "Остановленные контейнеры: $stopped_containers (запусти docker container prune -f)"
    fi
}

# Проверка лог-ротации
check_log_rotation() {
    echo ""
    echo "=== Проверка логов ==="

    local has_issues=false
    while IFS= read -r container_id; do
        local name log_driver max_size
        name=$(docker inspect "$container_id" --format '{{.Name}}' 2>/dev/null | sed 's/^\/\?//')
        log_driver=$(docker inspect "$container_id" --format '{{.HostConfig.LogConfig.Type}}' 2>/dev/null)
        max_size=$(docker inspect "$container_id" --format '{{index .HostConfig.LogConfig.Config "max-size"}}' 2>/dev/null || echo "")

        if [ "$log_driver" = "json-file" ] && [ -z "$max_size" ]; then
            log_warn "$name: json-file без max-size (логи могут заполнить диск!)"
            has_issues=true
        fi
    done < <(docker ps -q 2>/dev/null)

    if [ "$has_issues" = false ]; then
        log_ok "Лог-ротация настроена для всех контейнеров"
    fi
}

# --- Режимы работы ---
check_all_containers() {
    echo "=== Все Docker контейнеры ==="
    echo ""

    local containers
    containers=$(docker ps -a -q 2>/dev/null)

    if [ -z "$containers" ]; then
        echo "Нет запущенных контейнеров"
        exit 0
    fi

    for container in $containers; do
        check_container "$container"
    done
}

check_compose_stack() {
    local compose_dir="${1:-.}"

    if [ ! -f "$compose_dir/compose.yml" ] && [ ! -f "$compose_dir/compose.yaml" ] && [ ! -f "$compose_dir/docker-compose.yml" ]; then
        echo -e "${RED}Compose файл не найден в: $compose_dir${NC}"
        exit 2
    fi

    echo "=== Docker Compose стек: $compose_dir ==="
    echo ""

    local services
    services=$(docker compose -f "$compose_dir/compose.yml" ps -q 2>/dev/null || \
               docker compose -f "$compose_dir/compose.yaml" ps -q 2>/dev/null || \
               docker compose -f "$compose_dir/docker-compose.yml" ps -q 2>/dev/null)

    if [ -z "$services" ]; then
        echo "Нет запущенных сервисов в стеке"
        exit 1
    fi

    for container in $services; do
        check_container "$container"
    done
}

check_specific_services() {
    echo "=== Проверка сервисов: $* ==="
    echo ""

    for service in "$@"; do
        local container_id
        container_id=$(docker ps -q -f "name=$service" 2>/dev/null | head -1)
        if [ -z "$container_id" ]; then
            log_fail "$service -- контейнер не найден"
            ((STOPPED++)) || true
        else
            check_container "$container_id"
        fi
    done
}

# --- Вывод итогов ---
print_summary() {
    local total=$((HEALTHY + UNHEALTHY + STARTING + NO_HEALTHCHECK + STOPPED))

    echo ""
    echo "=== Итог ==="
    echo -e "  Всего:            $total"
    echo -e "  ${GREEN}Здоровы:          $HEALTHY${NC}"
    [ "$STARTING" -gt 0 ]       && echo -e "  ${YELLOW}Запускаются:      $STARTING${NC}"
    [ "$NO_HEALTHCHECK" -gt 0 ] && echo -e "  ${BLUE}Без healthcheck:  $NO_HEALTHCHECK${NC}"
    [ "$UNHEALTHY" -gt 0 ]      && echo -e "  ${RED}Нездоровы:        $UNHEALTHY${NC}"
    [ "$STOPPED" -gt 0 ]        && echo -e "  ${RED}Остановлены:      $STOPPED${NC}"
    echo ""

    if [ "$UNHEALTHY" -gt 0 ] || [ "$STOPPED" -gt 0 ]; then
        echo -e "${RED}Есть проблемные сервисы!${NC}"
        return 1
    else
        echo -e "${GREEN}Все сервисы в норме.${NC}"
        return 0
    fi
}

# --- Основной скрипт ---
main() {
    echo "=== Docker Health Check ==="
    echo "Дата: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    check_docker

    # Парсинг аргументов
    case "${1:-}" in
        --compose)
            shift
            check_compose_stack "${1:-.}"
            ;;
        --service)
            shift
            check_specific_services "$@"
            ;;
        --help|-h)
            echo "Использование:"
            echo "  $0                      # все контейнеры"
            echo "  $0 --compose [DIR]      # Compose стек"
            echo "  $0 --service NAME...    # указанные сервисы"
            echo ""
            echo "Переменные:"
            echo "  CHECK_RESOURCES=1  # проверить ресурсы системы"
            echo "  CHECK_LOGS=1       # проверить лог-ротацию"
            exit 0
            ;;
        *)
            check_all_containers
            ;;
    esac

    # Дополнительные проверки
    [ "${CHECK_RESOURCES:-0}" = "1" ] && check_system_resources
    [ "${CHECK_LOGS:-0}" = "1" ] && check_log_rotation

    # Итог
    print_summary
}

main "$@"
