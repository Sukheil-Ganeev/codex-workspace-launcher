#!/usr/bin/env bash
# =============================================================================
# docker-backup.sh — Бэкап Docker named volumes с ротацией
# Docker Engine 29.x | Февраль 2026
# =============================================================================
# Использование:
#   ./docker-backup.sh                     # бэкап всех named volumes
#   ./docker-backup.sh pgdata redis-data   # бэкап указанных volumes
#   BACKUP_DIR=/opt/backups ./docker-backup.sh  # в указанную директорию
#
# Переменные окружения:
#   BACKUP_DIR  — папка для бэкапов (по умолчанию: ./backups)
#   KEEP_LAST   — сколько бэкапов хранить (по умолчанию: 5)
# =============================================================================

set -euo pipefail

# --- Конфигурация ---
BACKUP_DIR="${BACKUP_DIR:-./backups}"
KEEP_LAST="${KEEP_LAST:-5}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_COUNT=0
ERROR_COUNT=0

# --- Цвета для вывода ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# --- Функции ---
log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Проверка Docker
check_docker() {
    if ! command -v docker &>/dev/null; then
        log_error "Docker не установлен или не в PATH"
        exit 1
    fi
    if ! docker info &>/dev/null; then
        log_error "Docker daemon не запущен"
        exit 1
    fi
}

# Бэкап одного volume
backup_volume() {
    local volume="$1"
    local backup_file="${BACKUP_DIR}/${volume}_${DATE}.tar.gz"

    # Проверяем что volume существует
    if ! docker volume inspect "$volume" &>/dev/null; then
        log_error "Volume '$volume' не найден"
        ((ERROR_COUNT++)) || true
        return 1
    fi

    log_info "Бэкап volume: $volume -> $(basename "$backup_file")"

    # Определяем тип данных для специализированного бэкапа
    # Проверяем: это PostgreSQL volume?
    local pg_container
    pg_container=$(docker ps --filter "volume=$volume" --format '{{.Names}}' | head -1)

    if [ -n "$pg_container" ]; then
        # Проверяем, запущен ли PostgreSQL в этом контейнере
        local is_postgres
        is_postgres=$(docker inspect "$pg_container" --format '{{.Config.Image}}' 2>/dev/null || echo "")
        if echo "$is_postgres" | grep -qi "postgres"; then
            log_info "  Обнаружен PostgreSQL — выполняю pg_dumpall..."
            local pg_dump_file="${BACKUP_DIR}/${volume}_pgdump_${DATE}.sql.gz"
            if docker exec "$pg_container" pg_dumpall -U postgres 2>/dev/null | gzip > "$pg_dump_file"; then
                log_info "  pg_dump сохранён: $(basename "$pg_dump_file") ($(du -h "$pg_dump_file" | cut -f1))"
            else
                log_warn "  pg_dumpall не удался, делаю файловый бэкап"
            fi
        fi
    fi

    # Файловый бэкап через tar (универсальный)
    if docker run --rm \
        -v "${volume}:/data:ro" \
        -v "$(cd "$BACKUP_DIR" && pwd):/backup" \
        alpine tar czf "/backup/$(basename "$backup_file")" -C /data . 2>/dev/null; then
        local size
        size=$(du -h "$backup_file" | cut -f1)
        log_info "  Готово: $(basename "$backup_file") ($size)"
        ((BACKUP_COUNT++)) || true
    else
        log_error "  Ошибка бэкапа volume '$volume'"
        ((ERROR_COUNT++)) || true
        return 1
    fi
}

# Ротация старых бэкапов
rotate_backups() {
    local volume="$1"
    local pattern="${BACKUP_DIR}/${volume}_*.tar.gz"
    local count
    count=$(ls -1 $pattern 2>/dev/null | wc -l)

    if [ "$count" -gt "$KEEP_LAST" ]; then
        local to_delete=$((count - KEEP_LAST))
        log_info "Ротация '$volume': удаляю $to_delete старых бэкапов (храним последние $KEEP_LAST)"
        ls -1t $pattern | tail -n "$to_delete" | while read -r f; do
            rm -f "$f"
            log_info "  Удалён: $(basename "$f")"
        done

        # Ротация pg_dump если есть
        local pg_pattern="${BACKUP_DIR}/${volume}_pgdump_*.sql.gz"
        local pg_count
        pg_count=$(ls -1 $pg_pattern 2>/dev/null | wc -l)
        if [ "$pg_count" -gt "$KEEP_LAST" ]; then
            local pg_to_delete=$((pg_count - KEEP_LAST))
            ls -1t $pg_pattern | tail -n "$pg_to_delete" | while read -r f; do
                rm -f "$f"
            done
        fi
    fi
}

# --- Основной скрипт ---
main() {
    echo "=== Docker Volume Backup ==="
    echo "Дата: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    check_docker

    # Создаём директорию для бэкапов
    mkdir -p "$BACKUP_DIR"
    log_info "Директория бэкапов: $BACKUP_DIR"
    log_info "Хранение: последние $KEEP_LAST бэкапов"
    echo ""

    # Определяем volumes для бэкапа
    local volumes=()
    if [ $# -gt 0 ]; then
        # Указанные volumes
        volumes=("$@")
    else
        # Все named volumes (исключаем анонимные -- с длинным hash именем)
        while IFS= read -r vol; do
            # Пропускаем volumes с именем длиннее 64 символов (анонимные)
            if [ "${#vol}" -lt 64 ]; then
                volumes+=("$vol")
            fi
        done < <(docker volume ls -q 2>/dev/null)
    fi

    if [ ${#volumes[@]} -eq 0 ]; then
        log_warn "Нет volumes для бэкапа"
        exit 0
    fi

    log_info "Volumes для бэкапа: ${volumes[*]}"
    echo ""

    # Бэкап каждого volume
    for vol in "${volumes[@]}"; do
        backup_volume "$vol"
        rotate_backups "$vol"
        echo ""
    done

    # Итог
    echo "=== Результат ==="
    log_info "Успешно: $BACKUP_COUNT"
    if [ "$ERROR_COUNT" -gt 0 ]; then
        log_error "Ошибок: $ERROR_COUNT"
    fi
    echo ""

    # Показываем содержимое папки бэкапов
    log_info "Файлы в $BACKUP_DIR:"
    ls -lh "$BACKUP_DIR"/ 2>/dev/null || true
    echo ""
    echo "Готово!"
}

main "$@"
