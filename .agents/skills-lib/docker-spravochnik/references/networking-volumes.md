# Networking и Volumes: полное руководство

> Reference для docker-справочник | Дата: 2026-02-17
> Docker Engine 29.x | Compose v2.40+ (CLI v5.x) | Февраль 2026

---

## 1. Типы сетей Docker

| Driver | Изоляция | DNS | Multi-host | Когда использовать |
|--------|----------|-----|------------|-------------------|
| **bridge** (default) | NAT, без DNS | Нет | Нет | Никогда -- создавай custom bridge |
| **bridge** (custom) | NAT, DNS | Да | Нет | 99% случаев: один хост, несколько контейнеров |
| **host** | Нет (разделяет сеть хоста) | Хоста | Нет | Максимальная производительность: HAProxy, Nginx, мониторинг |
| **overlay** | VXLAN-туннель | Да | Да | Docker Swarm, multi-host кластеры |
| **macvlan** | Свой MAC-адрес | Нет | Нет | Контейнер как устройство в физической LAN (IoT, legacy) |
| **none** | Полная | Нет | Нет | Изоляция: batch-задачи, обработка данных без сети |

**Правило:** всегда создавай custom bridge. Default bridge НЕ имеет DNS resolution -- контейнеры видят друг друга только по IP.

```bash
# Создание custom bridge
docker network create backend
docker network create --subnet 172.20.0.0/16 --gateway 172.20.0.1 custom-net

# Overlay для Swarm (multi-host)
docker network create --driver overlay --attachable my-overlay
```

---

## 2. DNS Resolution

### Автоматический DNS в custom bridge

В custom bridge сети каждый контейнер доступен по имени. Встроенный DNS-сервер Docker (127.0.0.11) автоматически резолвит имена контейнеров.

```bash
docker network create mynet
docker run -d --name db --network mynet postgres:17-alpine
docker run -d --name api --network mynet myapp
# api может обращаться к БД: postgres://db:5432
```

### DNS Aliases

Используй `--network-alias` для дополнительных DNS-имён одного контейнера:

```bash
docker run -d --name postgres-main --network mynet \
  --network-alias db --network-alias database \
  postgres:17-alpine
# Доступен по именам: postgres-main, db, database
```

### Extra Hosts

Добавь кастомные записи в `/etc/hosts` контейнера:

```bash
docker run --add-host=api.local:192.168.1.100 myapp
```

В Compose:

```yaml
services:
  app:
    extra_hosts:
      - "api.local:192.168.1.100"
      - "host.docker.internal:host-gateway"  # доступ к хосту
```

### DNS в Compose

Compose автоматически создаёт сеть `projectname_default`. Имя сервиса = DNS-имя. Если проект называется `booking`, сервис `db` доступен как `db` (внутри сети) или `booking-db-1` (полное имя контейнера).

---

## 3. nftables (Engine 29 -- экспериментально)

Docker исторически использует **iptables** для NAT и port forwarding. Engine 29 добавил экспериментальную поддержку **nftables** -- современной замены iptables.

### Включение nftables

В `daemon.json`:

```json
{
  "ip6tables": true,
  "iptables": false,
  "experimental": true
}
```

**Зачем:** nftables -- стандарт в современных дистрибутивах (Debian 12+, Ubuntu 22.04+). iptables-legacy может конфликтовать с firewalld/nftables на хосте.

**Ограничения:** экспериментальная фича, не все плагины сети совместимы. Для production рекомендуется дождаться GA-статуса.

---

## 4. Port Mapping

### Синтаксис

```bash
-p 8080:80                  # host:container (TCP)
-p 127.0.0.1:8080:80       # только localhost (безопасно!)
-p 8080:80/udp              # UDP
-p 8000-8005:8000-8005      # диапазон портов
-p 80                       # random host port -> container 80
-P                          # все EXPOSE порты на random host ports
```

### Безопасность port binding

По умолчанию Docker биндит на `0.0.0.0` -- порт доступен извне, **обходя firewall хоста** (ufw, iptables правила НЕ применяются к Docker). Для безопасности:

```bash
# Привязка только к localhost
docker run -p 127.0.0.1:8080:80 myapp

# Глобально в daemon.json
{
  "ip": "127.0.0.1"
}
```

В Compose:

```yaml
ports:
  - "127.0.0.1:8080:80"    # только localhost
  - "0.0.0.0:443:443"      # явно все интерфейсы
  - target: 8000
    published: 8000
    protocol: tcp
    host_ip: 127.0.0.1     # длинный формат
```

---

## 5. Multi-Network изоляция в Compose

Разделяй сервисы на изолированные сети для безопасности. Типичная схема для booking API туризма ОАЭ:

```yaml
# compose.yaml -- multi-network для booking API
services:
  nginx:
    image: nginx:1.27-alpine
    networks: [frontend]
    ports: ["80:80", "443:443"]

  booking-api:
    build: ./backend
    networks: [frontend, backend]
    environment:
      TOURS_CURRENCY: AED
      DEFAULT_LANGUAGE: ru
      TIMEZONE: Asia/Dubai

  db:
    image: postgres:17-alpine
    networks: [backend]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    networks: [backend]

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # Изолирована от внешнего мира!

volumes:
  pgdata:
```

**Логика:** nginx видит только booking-api. API видит nginx + db + redis. БД и Redis полностью изолированы от интернета. Внешний трафик заходит только через nginx.

---

## 6. Типы хранилищ

| Тип | Персистентность | Скорость | Управление | Когда использовать |
|-----|----------------|----------|-----------|-------------------|
| **Named Volume** | Да | Нативная (Linux) | Docker управляет | Данные БД, uploads, кэш. **Production** |
| **Bind Mount** | Да (хост) | macOS/Win медленнее | Ты управляешь путём | Разработка (hot-reload), конфиги `:ro` |
| **tmpfs** | Нет (RAM) | Максимальная | В памяти | Секреты, временные файлы, кэш сессий |
| **type=image** (v28+) | Нет (read-only) | Нативная | Из другого образа | Статика, ML-модели, конфиги из образа |

### Примеры

```bash
# Named volume
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres:17

# Bind mount (разработка)
docker run -v $(pwd)/src:/app/src:ro myapp    # :ro = read-only

# tmpfs (секреты в RAM)
docker run --tmpfs /app/tmp:rw,size=100m myapp

# type=image (Engine 28+)
docker run --mount type=image,source=static-assets:v1,target=/app/static myapp
```

### Compose

```yaml
services:
  app:
    volumes:
      - pgdata:/var/lib/postgresql/data       # named volume
      - ./src:/app/src:ro                      # bind mount
      - type: tmpfs
        target: /app/tmp
        tmpfs:
          size: 100000000                      # 100 MB

volumes:
  pgdata:
    driver: local
    labels:
      com.project: "booking-uae"
  shared-data:
    external: true    # Не создавать -- должен уже существовать
```

---

## 7. Backup и Restore Volumes

### Универсальный backup через tar

```bash
# Бэкап named volume в tar.gz
docker run --rm \
  -v pgdata:/data:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/pgdata_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore из tar.gz
docker run --rm \
  -v pgdata:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/pgdata_20260217_120000.tar.gz -C /data
```

### Backup через --volumes-from

```bash
# Скопировать данные из контейнера db
docker run --rm --volumes-from my_postgres \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres_data.tar.gz /var/lib/postgresql/data
```

### Логический dump БД (без остановки)

```bash
# PostgreSQL
docker exec my_postgres pg_dump -U postgres -Fc mydb > backup.dump

# Restore
docker exec -i my_postgres pg_restore -U postgres -d mydb < backup.dump

# MySQL
docker exec my_mysql mysqldump -u root -p mydb > backup.sql
```

### Стратегия бэкапов для production

| Метод | Когда | Downtime | Размер |
|-------|-------|----------|--------|
| `pg_dump` / `mysqldump` | Ежедневно | Нет | Только данные |
| tar volume | Еженедельно | Да (стоп контейнер) | Полная копия |
| `--volumes-from` | Ad-hoc | Нет (но нагрузка) | Полная копия |
| Внешний бэкап (restic/borg) | По расписанию | Нет | Инкрементальный |

**Для туризма ОАЭ:** бэкап БД бронирований ежедневно через `pg_dump` в cron, еженедельный полный tar. Храни 7 ежедневных + 4 еженедельных копии. Скрипт: `scripts/backup-volumes.sh`.

---

## 8. Производительность хранилищ

### Linux

Все типы хранилищ работают с нативной скоростью. Разницы между named volumes и bind mounts практически нет.

### macOS

**VirtioFS** -- дефолтный механизм file sharing (macOS 12.5+). Значительно быстрее legacy osxfs и gRPC FUSE.

```
Named volume:  ~100% нативной скорости (данные внутри VM)
Bind mount:    ~60-80% нативной скорости (VirtioFS)
Bind mount:    ~20-40% (legacy osxfs -- НЕ использовать)
```

**Совет:** для `node_modules` и `.venv` используй named volume, не bind mount:

```yaml
services:
  app:
    volumes:
      - ./src:/app/src         # bind: исходники для hot-reload
      - node_modules:/app/node_modules  # named: зависимости (быстро!)

volumes:
  node_modules:
```

### Windows (WSL2)

Храни код внутри WSL2 FS (`/home/user/project`), НЕ на монтированном Windows-диске (`/mnt/c/...`). Разница в производительности: 5-10x.

```bash
# Правильно (быстро)
cd /home/user/my-project && docker compose up

# Неправильно (медленно)
cd /mnt/c/Users/user/my-project && docker compose up
```

---

## 9. Networks и Volumes в Compose

### Networks секция

```yaml
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24

  backend:
    driver: bridge
    internal: true          # нет доступа в интернет
    labels:
      com.project: "booking"

  existing-net:
    external: true          # не создавать -- должна существовать
    name: my-external-net   # реальное имя сети
```

### Volumes секция

```yaml
volumes:
  pgdata:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/postgres    # привязка к конкретному пути хоста

  redis-data:
    driver: local

  shared:
    external: true              # не создавать -- должен существовать
    name: my-shared-volume
```

### Driver opts для NFS

Для общего хранилища между хостами (Swarm, кластер):

```yaml
volumes:
  nfs-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.1.100,rw,nfsvers=4
      device: ":/exports/data"
```

### Labels и фильтрация

```bash
# Найти все volumes проекта
docker volume ls --filter label=com.project=booking

# Удалить volumes по label
docker volume ls --filter label=com.project=booking -q | xargs docker volume rm
```

---

> **Связанные файлы:**
> - `cheatsheet.md` -- все CLI-команды для сетей и volumes
> - `troubleshooting.md` -- проблемы "контейнеры не видят друг друга", "permission denied на volume"
> - `security-production.md` -- read-only filesystem, resource limits
> - SKILL.md -- модули 5 (Volumes) и 6 (Networking)
