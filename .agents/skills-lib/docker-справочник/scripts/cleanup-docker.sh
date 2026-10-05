#!/usr/bin/env bash
# =============================================================================
# cleanup-docker.sh -- Очистка Docker-ресурсов
# Docker Engine 29.x | Февраль 2026
#
# Использование:
#   chmod +x cleanup-docker.sh
#   ./cleanup-docker.sh            # Интерактивный режим
#   ./cleanup-docker.sh --force    # Без подтверждения (кроме volumes!)
#
# Безопасно: volumes удаляются ТОЛЬКО с явным подтверждением.
# =============================================================================

set -euo pipefail

# --- Цвета для вывода ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FORCE=false
if [[ "${1:-}" == "--force" ]]; then
    FORCE=true
fi

echo -e "${GREEN}=== Docker Cleanup ===${NC}"
echo ""

# --- 1. Показать текущее использование ---
echo -e "${YELLOW}Текущее использование диска:${NC}"
docker system df
echo ""

# --- 2. Удалить остановленные контейнеры ---
echo -e "${YELLOW}Удаление остановленных контейнеров...${NC}"
docker container prune -f
echo ""

# --- 3. Удалить dangling images (без тега) ---
echo -e "${YELLOW}Удаление dangling images...${NC}"
docker image prune -f
echo ""

# --- 4. Удалить неиспользуемые сети ---
echo -e "${YELLOW}Удаление неиспользуемых сетей...${NC}"
docker network prune -f
echo ""

# --- 5. Удалить build cache старше 7 дней ---
echo -e "${YELLOW}Удаление build cache старше 7 дней...${NC}"
docker builder prune -f --filter "until=168h"
echo ""

# --- 6. Удалить неиспользуемые volumes (ОПАСНО -- с подтверждением!) ---
echo -e "${RED}Внимание: удаление volumes уничтожит данные!${NC}"
if [[ "$FORCE" == true ]]; then
    echo -e "${RED}Режим --force: volumes пропущены для безопасности.${NC}"
    echo "Для удаления volumes вручную: docker volume prune -f"
else
    read -p "Удалить неиспользуемые volumes? (y/N): " confirm
    if [[ "${confirm:-}" =~ ^[Yy]$ ]]; then
        docker volume prune -f
        echo -e "${GREEN}Volumes очищены.${NC}"
    else
        echo "Volumes пропущены."
    fi
fi
echo ""

# --- 7. Итоговый отчёт ---
echo -e "${GREEN}=== Результат ===${NC}"
docker system df
echo ""
echo -e "${GREEN}Готово!${NC}"
