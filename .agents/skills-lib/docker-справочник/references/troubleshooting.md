# Docker Troubleshooting -- Решение типичных проблем

> Формат: Симптом -> Причина -> Решение
> Февраль 2026

---

## 1. Permission Denied при запуске docker

**Симптом:**
```
Got permission denied while trying to connect to the Docker daemon socket
```

**Причина:** Пользователь не в группе `docker`. Docker socket (`/var/run/docker.sock`) доступен только root и группе docker.

**Решение:**
```bash
sudo usermod -aG docker $USER
newgrp docker       # применить без перелогина
docker run hello-world  # проверить
```

Альтернатива: rootless Docker (`dockerd-rootless-setuptool.sh install`).

---

## 2. Port Already in Use

**Симптом:**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Причина:** Порт занят другим контейнером или процессом на хосте.

**Решение:**
```bash
# Найти, кто занимает порт
# Linux:
sudo lsof -i :8000
sudo ss -tlnp | grep :8000
# Windows:
netstat -ano | findstr :8000

# Docker: какой контейнер
docker ps --format '{{.Names}}\t{{.Ports}}' | grep 8000

# Освободить
docker stop <container>    # если Docker
kill <PID>                  # если процесс (Linux)
taskkill /PID <N> /F        # если процесс (Windows)
```

---

## 3. No Space Left on Device

**Симптом:**
```
write /var/lib/docker/tmp/...: no space left on device
```

**Причина:** Docker занял весь диск: неиспользуемые образы, остановленные контейнеры, build cache, volumes.

**Решение:**
```bash
# Диагностика
docker system df
docker system df -v

# Очистка
docker system prune -a           # образы, контейнеры, сети, build cache
docker system prune -a --volumes # + volumes (ОСТОРОЖНО: данные БД!)
docker builder prune --filter "until=168h"  # build cache старше 7 дней
docker image prune -a --filter "until=24h"  # образы старше 24ч
```

**Профилактика:** регулярно запускать `docker system prune` или настроить cron.

---

## 4. Image Not Found / Pull Access Denied

**Симптом:**
```
Error: pull access denied for myimage, repository does not exist
```

**Причина:** Опечатка в имени, приватный registry без авторизации, или Docker Hub rate limit.

**Решение:**
```bash
docker login                 # авторизация (Docker Hub)
docker login ghcr.io         # GitHub Container Registry
docker search <image-name>   # проверить существование
```

Rate limit без аутентификации: 10 pulls/час. Всегда авторизуйся в CI/CD.

---

## 5. DNS Resolution Failed

**Симптом:**
```
Could not resolve host: registry-1.docker.io
```

**Причина:** DNS-сервер хоста не отвечает, или DNS внутри контейнера неправильно настроен.

**Решение:**
```bash
# Проверить DNS в контейнере
docker run --rm alpine nslookup google.com

# Указать DNS явно
docker run --dns 8.8.8.8 myimage

# Глобально в /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
sudo systemctl restart docker
```

---

## 6. Контейнер сразу останавливается (exit code 0 или 1)

**Симптом:** `docker run` завершается мгновенно. `docker ps` пусто, `docker ps -a` показывает Exited.

**Причина:** Основной процесс (PID 1) завершился. Если exit code 0 -- нормальное завершение, 1 -- ошибка.

**Решение:**
```bash
# Посмотреть exit code
docker inspect -f '{{.State.ExitCode}}' <container>

# Логи
docker logs <container>

# Запустить интерактивно для отладки
docker run -it <image> /bin/sh

# Частая причина: CMD/ENTRYPOINT запускает фоновый процесс
# Правильно: процесс должен оставаться на переднем плане
# Пример: nginx -g "daemon off;"
```

---

## 7. Cannot connect to Docker daemon

**Симптом:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Причина:** Docker daemon не запущен.

**Решение:**
```bash
# Запустить демон
sudo systemctl start docker

# Проверить статус
sudo systemctl status docker

# Если ошибка в конфигурации
sudo journalctl -u docker -n 50  # последние 50 строк логов
```

Windows: убедись что Docker Desktop запущен. macOS: открой Docker.app.

---

## 8. OOM Killed (Out of Memory)

**Симптом:** Контейнер внезапно перезапускается. `docker inspect` показывает `"OOMKilled": true`.

**Причина:** Контейнер превысил лимит памяти (`--memory`), или хост нехватка RAM.

**Решение:**
```bash
# Проверить OOM
docker inspect -f '{{.State.OOMKilled}}' <container>

# Увеличить лимит или оптимизировать приложение
docker run --memory 1g --memory-swap 2g myapp

# Мониторинг потребления
docker stats <container>
```

---

## 9. Контейнеры не видят друг друга по имени

**Симптом:** `ping db` или `curl http://api:8000` не работает из контейнера.

**Причина:** Контейнеры в default bridge network (нет DNS resolution).

**Решение:**
```bash
# Создать custom network
docker network create mynet

# Запустить контейнеры в одной сети
docker run -d --name db --network mynet postgres:16
docker run -d --name app --network mynet myapp

# Теперь app может обращаться к db по имени
```

В Compose это работает автоматически -- все сервисы в одной сети.

---

## 10. Build context too large / slow build

**Симптом:** `docker build` долго отправляет context или использует много памяти.

**Причина:** В build context попали лишние файлы (.git, node_modules, data).

**Решение:** Создай `.dockerignore`:
```dockerignore
.git
node_modules
__pycache__
.venv
*.log
.env
```

Проверь размер context: `du -sh .` в директории сборки.

---

## 11. Alpine + Python: ошибки компиляции C-extensions

**Симптом:**
```
error: command 'gcc' failed with exit status 1
```
При `pip install` пакетов с C-расширениями (numpy, pandas, psycopg2).

**Причина:** Alpine использует musl libc вместо glibc. Многие Python-пакеты собраны только для glibc.

**Решение:** Используй Debian-based образ:
```dockerfile
# Вместо python:3.13-alpine
FROM python:3.13-slim-bookworm
```

---

## 12. Volumes: Permission Denied при записи

**Симптом:** Приложение в контейнере не может писать в mounted volume.

**Причина:** UID/GID внутри контейнера не совпадает с owner'ом на хосте.

**Решение:**
```bash
# Вариант 1: передать UID/GID при запуске
docker run --user $(id -u):$(id -g) -v mydata:/app/data myapp

# Вариант 2: в Dockerfile -- создать пользователя с нужным UID
ARG UID=1000
RUN adduser --uid $UID --disabled-password app
USER app

# Вариант 3: группа
docker run --group-add 1000 -v mydata:/app/data myapp
```

---

## 13. WSL2: vmmem съедает всю RAM

**Симптом:** Процесс `vmmem` в Task Manager потребляет 50%+ RAM. Windows тормозит.

**Причина:** WSL2 по умолчанию захватывает до 50% физической памяти и не отдаёт обратно.

**Решение:** Создай `C:\Users\<username>\.wslconfig`:
```ini
[wsl2]
memory=4GB
swap=2GB
processors=2
```
Затем: `wsl --shutdown` и перезапусти Docker Desktop.

---

## 14. WSL2: VHDX-файл растёт и не уменьшается

**Симптом:** Docker Data VHDX файл занимает десятки GB, даже после `docker system prune`.

**Причина:** Thin-provisioned VHDX растёт при записи, но не сжимается при удалении.

**Решение:**
```powershell
# Остановить Docker и WSL
wsl --shutdown

# Windows Pro/Enterprise
Optimize-VHD -Path "$env:LOCALAPPDATA\Docker\wsl\disk\docker_data.vhdx" -Mode Full

# Windows Home -- через diskpart
diskpart
select vdisk file="C:\Users\...\docker_data.vhdx"
compact vdisk
exit
```

---

## 15. Логи контейнера забивают диск

**Симптом:** `/var/lib/docker/containers/` занимает десятки GB.

**Причина:** Нет ротации логов. По умолчанию json-file driver без лимита.

**Решение:** Добавь в `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```
```bash
sudo systemctl restart docker
```
Это ограничит каждый лог-файл 10 MB, максимум 3 файла на контейнер.

---

## 16. docker compose up: service unhealthy

**Симптом:** Compose зависает на "Waiting for service to become healthy".

**Причина:** Healthcheck не проходит: неправильная команда, слишком маленький `start_period`, сервис не успевает запуститься.

**Решение:**
```bash
# Проверить healthcheck вручную
docker exec <container> curl -f http://localhost:8000/health

# Увеличить start_period и interval
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 10
  start_period: 60s   # дать больше времени на старт
```

---

## 17. Кросс-платформенная сборка зависает / очень медленная

**Симптом:** `docker buildx build --platform linux/arm64` на x86 зависает или идёт 30+ минут.

**Причина:** QEMU эмуляция в 5-8x медленнее нативной. Тяжёлые операции (npm install, pip install с компиляцией) критически долгие.

**Решение:**
```bash
# Убедиться что QEMU установлен
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

# Для тяжёлых билдов -- использовать нативные решения:
# 1. Docker Build Cloud -- облачные builders (linux/amd64 + linux/arm64 нативно)
docker buildx create --driver cloud org/builder
# 2. Self-hosted ARM runner (GitHub Actions, GitLab, etc.)
# 3. Собирать на целевом ARM-сервере напрямую (Oracle Cloud Free Tier)
```

---

## 18. COPY failed: file not found in build context

**Симптом:** `COPY failed: file not found in build context` при сборке.

**Причина:** Файл вне build context или исключён .dockerignore.

**Решение:**
```bash
# Проверь build context: точка = текущая папка
docker build -f Dockerfile .

# Проверь .dockerignore: не исключён ли нужный файл?
cat .dockerignore

# Используй --no-cache для исключения проблем с кэшем
docker build --no-cache .

# Проверь что файл существует в context
ls -la <путь-к-файлу>
```

---

## 19. Network has active endpoints

**Симптом:** `network has active endpoints` при удалении сети.

**Причина:** Контейнеры подключены к сети.

**Решение:**
```bash
# Посмотри подключенные контейнеры
docker network inspect <network> --format '{{range .Containers}}{{.Name}} {{end}}'

# Отключи контейнеры
docker network disconnect <network> <container>

# Или останови все контейнеры в сети (для Compose)
docker compose down
```

---

## 20. exec format error

**Симптом:** `exec user process caused: exec format error`

**Причина:** Архитектура образа не совпадает с хостом (ARM-образ на x86 или наоборот).

**Решение:**
```bash
# Проверь архитектуру образа
docker image inspect myimage --format '{{.Architecture}}'

# Собери для нужной платформы
docker buildx build --platform linux/amd64 -t myimage .

# Или используй QEMU для эмуляции
docker run --privileged --rm tonistiigi/binfmt --install all
```

---

## 21. Too Many Requests (Rate Limiting)

**Симптом:** `toomanyrequests: You have reached your pull rate limit` в CI.

**Причина:** Docker Hub ограничивает pulls: 10/час без авторизации (с 1 апреля 2025).

**Решение:**
```bash
# Авторизуйся (Personal = 100/час, Pro/Team = безлимитно)
echo $DOCKER_TOKEN | docker login -u $DOCKER_USER --password-stdin

# Используй GHCR как зеркало для базовых образов
# Или Docker Hub mirror: --registry-mirror в daemon.json

# В CI: всегда добавляй docker login step перед pull
# Кэшируй образы: --pull=missing вместо --pull=always
```

---

## 22. Conflict: container name already in use

**Симптом:** `Conflict. The container name "/myapp" is already in use`

**Причина:** Контейнер с таким именем уже существует (даже если остановлен).

**Решение:**
```bash
# Удали старый контейнер
docker rm myapp

# Или удали принудительно (даже работающий)
docker rm -f myapp

# Или используй --rm при запуске (удаляет после остановки)
docker run --rm --name myapp myimage
```

---

## Диагностические команды -- шпаргалка

| Команда | Что показывает |
|---------|---------------|
| `docker logs <c>` | stdout/stderr контейнера |
| `docker logs -f --tail 100 <c>` | Последние 100 строк + follow |
| `docker compose logs --tail=100 <service>` | Логи конкретного сервиса Compose |
| `docker inspect <c>` | Полная конфигурация (JSON) |
| `docker events` | События daemon в реальном времени |
| `docker system df` | Использование диска |
| `docker stats` | CPU, RAM, I/O в реальном времени |
| `docker top <c>` | Процессы внутри контейнера |
| `docker debug <c>` | Shell с инструментами (даже в distroless) |

**Полезные фильтры inspect:**
```bash
# IP-адрес
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <c>

# Статус и exit code
docker inspect -f '{{.State.Status}} (exit {{.State.ExitCode}})' <c>

# OOM killed?
docker inspect -f '{{.State.OOMKilled}}' <c>
```
