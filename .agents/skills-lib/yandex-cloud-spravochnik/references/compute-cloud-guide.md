# Compute Cloud: Виртуальные машины

**Назначение:** Полное руководство по созданию и управлению виртуальными машинами в Yandex Cloud

**Когда использовать Compute Cloud:**
- Монолитные приложения (не microservices)
- Legacy системы, которые нельзя переписать
- Долгоживущие процессы (workers, background jobs)
- Нужен полный контроль над ОС
- Специфичные требования к софту

**Когда НЕ использовать:**
- Простые API endpoints → используй Cloud Functions
- Stateless приложения → используй Cloud Run
- Scheduled tasks → используй Cloud Functions с triggers

---

## Основы Compute Cloud

### Типы инстансов

**Standard (универсальные):**
- Сбалансированное соотношение CPU/RAM
- Для веб-серверов, приложений, БД

**High-Memory (много RAM):**
- Соотношение 1 vCPU : 8GB RAM
- Для in-memory БД (Redis, Memcached)
- Для приложений с большими datasets

**High-Performance (много CPU):**
- Соотношение 1 vCPU : 2GB RAM
- Для вычислений, video encoding
- Batch processing

**GPU (для ML/AI):**
- NVIDIA Tesla V100, T4, A100
- Для обучения моделей, inference
- Для рендеринга, симуляций

### Платформы (CPU архитектуры)

**Intel Ice Lake (3rd Gen Xeon):**
- Лучшая производительность
- Рекомендуется для production

**Intel Cascade Lake (2nd Gen Xeon):**
- Дешевле на 10-15%
- Хорошо для dev/staging

**AMD EPYC:**
- Альтернатива Intel
- Конкурентная цена

### Preemptible VMs (прерываемые)

**Что это:**
- VM с гарантией работы максимум 24 часа
- Могут быть остановлены в любой момент (с предупреждением за 30 секунд)
- До 40% дешевле обычных VM

**Когда использовать:**
- Batch обработка данных
- CI/CD runners
- Обучение ML моделей
- Любые stateless задачи

**Пример:** ETL pipeline для аналитики туров (запускается ночью, результат сохраняется в БД)

---

## Создание VM

### Метод 1: Через Console (веб-интерфейс)

```
1. Перейти в https://console.cloud.yandex.ru
2. Выбрать folder → Compute Cloud → Create VM
3. Настроить параметры (см. ниже)
4. Нажать "Create"
```

### Метод 2: Через yc CLI

```bash
# Базовая VM (Ubuntu 22.04, 2 vCPU, 4GB RAM)
yc compute instance create \
  --name web-server-1 \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 2 \
  --memory 4 \
  --create-boot-disk image-folder-id=standard-images,image-family=ubuntu-2204-lts,size=20 \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub
```

**Параметры:**
- `--name` - имя VM (уникальное в folder)
- `--zone` - зона доступности (ru-central1-a/b/d)
- `--platform` - тип CPU (standard-v3, standard-v2, amd-epyc)
- `--cores` - количество vCPU (2, 4, 8, 16, ...)
- `--memory` - RAM в GB (4, 8, 16, 32, ...)
- `--create-boot-disk` - образ ОС и размер диска
- `--network-interface` - сетевые настройки
- `--ssh-key` - публичный SSH ключ для доступа

### Метод 3: Через Terraform

```hcl
# main.tf
resource "yandex_compute_instance" "web_server" {
  name        = "web-server-1"
  platform_id = "standard-v3"
  zone        = "ru-central1-a"

  resources {
    cores  = 2
    memory = 4
  }

  boot_disk {
    initialize_params {
      image_id = "fd8fte6bebi857ortlja" # Ubuntu 22.04
      size     = 20
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.default.id
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
  }
}
```

### Метод 4: Через API (curl)

```bash
# Получить IAM токен
IAM_TOKEN=$(yc iam create-token)
FOLDER_ID=$(yc config get folder-id)

# Создать VM
curl -X POST \
  -H "Authorization: Bearer $IAM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "folderId": "'$FOLDER_ID'",
    "name": "web-server-1",
    "zoneId": "ru-central1-a",
    "platformId": "standard-v3",
    "resourcesSpec": {
      "memory": 4294967296,
      "cores": 2
    },
    "bootDiskSpec": {
      "diskSpec": {
        "size": 21474836480,
        "imageId": "fd8fte6bebi857ortlja"
      }
    },
    "networkInterfaceSpecs": [{
      "subnetId": "'$SUBNET_ID'",
      "primaryV4AddressSpec": {
        "oneToOneNatSpec": {
          "ipVersion": "IPV4"
        }
      }
    }]
  }' \
  https://compute.api.cloud.yandex.net/compute/v1/instances
```

---

## Образы операционных систем

### Официальные образы Yandex Cloud

```bash
# Список всех образов
yc compute image list --folder-id standard-images

# Популярные семейства:
# - ubuntu-2204-lts (Ubuntu 22.04)
# - ubuntu-2004-lts (Ubuntu 20.04)
# - centos-7 (CentOS 7)
# - centos-stream-8 (CentOS Stream 8)
# - debian-11 (Debian 11)
# - windows-2022 (Windows Server 2022)
```

### Найти образ по семейству

```bash
# Последний Ubuntu 22.04
IMAGE_ID=$(yc compute image get-latest-from-family ubuntu-2204-lts --folder-id standard-images --format json | jq -r '.id')

echo $IMAGE_ID
# fd8fte6bebi857ortlja
```

### Создать собственный образ

```bash
# 1. Создать VM с нужным софтом
# 2. Настроить всё что нужно
# 3. Остановить VM
yc compute instance stop web-server-1

# 4. Создать snapshot диска
DISK_ID=$(yc compute instance get web-server-1 --format json | jq -r '.boot_disk.disk_id')

yc compute disk create-snapshot $DISK_ID \
  --name web-server-snapshot

# 5. Создать image из snapshot
yc compute image create \
  --name my-custom-image \
  --source-snapshot-name web-server-snapshot
```

---

## Конфигурации для туристического бизнеса

### Конфигурация 1: Простой веб-сервер

**Use case:** Сайт-визитка с информацией о турах

```bash
yc compute instance create \
  --name tourism-web \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 2 \
  --memory 2 \
  --preemptible false \
  --create-boot-disk image-family=ubuntu-2204-lts,size=20,type=network-ssd \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub \
  --metadata-from-file user-data=cloud-init.yaml
```

**cloud-init.yaml** (автоматическая настройка при первом запуске):

```yaml
#cloud-config
packages:
  - nginx
  - nodejs
  - npm
  - git

runcmd:
  - systemctl enable nginx
  - systemctl start nginx
  - git clone https://github.com/your-repo/tourism-site.git /var/www/tourism
  - cd /var/www/tourism && npm install
  - npm install -g pm2
  - pm2 start app.js
  - pm2 startup
  - pm2 save
```

**Стоимость:** ~2,000₽/месяц

### Конфигурация 2: API сервер с БД

**Use case:** Backend для booking системы

```bash
# VM для приложения
yc compute instance create \
  --name tourism-api \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 4 \
  --memory 8 \
  --create-boot-disk image-family=ubuntu-2204-lts,size=30,type=network-ssd \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub
```

**Стоимость:** ~6,000₽/месяц

**Лучше использовать:** Managed PostgreSQL вместо VM с БД (надежнее и проще)

### Конфигурация 3: Worker для обработки фото

**Use case:** Автоматическое изменение размера и оптимизация фото туров

```bash
# Preemptible VM (дешевле на 40%)
yc compute instance create \
  --name photo-worker \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 4 \
  --memory 8 \
  --preemptible true \
  --create-boot-disk image-family=ubuntu-2204-lts,size=50,type=network-ssd \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub
```

**Стоимость:** ~2,400₽/месяц (vs 4,000₽ для обычной VM)

### Конфигурация 4: High-performance для аналитики

**Use case:** Обработка больших объемов данных о бронированиях

```bash
yc compute instance create \
  --name analytics-server \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 16 \
  --memory 64 \
  --create-boot-disk image-family=ubuntu-2204-lts,size=100,type=network-ssd \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub
```

**Стоимость:** ~48,000₽/месяц

**Лучше использовать:** Managed ClickHouse для аналитики (проще и эффективнее)

---

## Управление дисками

### Типы дисков

**network-ssd (SSD):**
- Скорость: до 40k IOPS
- Цена: 8₽/GB/месяц
- Для БД, приложений

**network-hdd (HDD):**
- Скорость: до 300 IOPS
- Цена: 2₽/GB/месяц
- Для архивов, бекапов

**network-ssd-nonreplicated:**
- Fastest: до 75k IOPS
- Цена: 7₽/GB/месяц
- НЕТ репликации (риск потери данных)

### Добавить дополнительный диск

```bash
# Создать диск
yc compute disk create \
  --name data-disk \
  --zone ru-central1-a \
  --type network-ssd \
  --size 100

# Подключить к VM
yc compute instance attach-disk tourism-api \
  --disk-name data-disk

# На VM примонтировать диск
ssh ubuntu@<VM_IP>

# Найти новый диск
lsblk
# vdb    252:16   0  100G  0 disk

# Отформатировать
sudo mkfs.ext4 /dev/vdb

# Создать mount point
sudo mkdir /mnt/data

# Примонтировать
sudo mount /dev/vdb /mnt/data

# Добавить в /etc/fstab для автоматического монтирования
echo "/dev/vdb /mnt/data ext4 defaults 0 0" | sudo tee -a /etc/fstab
```

### Snapshot (снимок диска)

```bash
# Создать snapshot
DISK_ID=$(yc compute instance get tourism-api --format json | jq -r '.boot_disk.disk_id')

yc compute snapshot create \
  --name tourism-api-snapshot-$(date +%Y%m%d) \
  --disk-id $DISK_ID \
  --description "Backup before update"

# Список snapshots
yc compute snapshot list

# Восстановить из snapshot
yc compute disk create \
  --name restored-disk \
  --source-snapshot-name tourism-api-snapshot-20260205

# Создать VM из snapshot
yc compute instance create \
  --name tourism-api-restored \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 4 \
  --memory 8 \
  --use-boot-disk disk-name=restored-disk \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub
```

### Автоматические snapshots

```bash
# Создать snapshot schedule
yc compute snapshot-schedule create \
  --name daily-backup \
  --expression "0 3 * * *" \
  --retention-period 7d \
  --disk-id $DISK_ID

# Формат expression: cron (минуты часы день месяц день_недели)
# 0 3 * * * = каждый день в 3:00 UTC
```

---

## Networking

### Публичный IP

```bash
# Создать VM с публичным IP
yc compute instance create \
  --name web-server \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  ...

# Узнать публичный IP
yc compute instance get web-server --format json | jq -r '.network_interfaces[0].primary_v4_address.one_to_one_nat.address'
```

### Статический IP

```bash
# Зарезервировать статический IP
yc vpc address create \
  --name web-server-ip \
  --external-ipv4 zone=ru-central1-a

# Получить адрес
STATIC_IP=$(yc vpc address get web-server-ip --format json | jq -r '.external_ipv4_address.address')

# Создать VM с этим IP
yc compute instance create \
  --name web-server \
  --network-interface subnet-name=default-ru-central1-a,nat-address=$STATIC_IP \
  ...
```

**Цена статического IP:** 200₽/месяц

### Internal-only (без публичного IP)

```bash
# VM без публичного IP
yc compute instance create \
  --name internal-app \
  --network-interface subnet-name=default-ru-central1-a \
  ...

# Доступ только из VPC (через bastion host или VPN)
```

### Security Groups (Firewall)

```bash
# Создать security group
yc vpc security-group create \
  --name web-server-sg \
  --rule "direction=ingress,port=22,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=ingress,port=80,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=ingress,port=443,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=egress,protocol=any,v4-cidrs=[0.0.0.0/0]" \
  --network-name default

# Применить к VM
yc compute instance update web-server \
  --network-interface subnet-name=default-ru-central1-a,security-group-ids=<SG_ID>
```

---

## Instance Groups (Auto-scaling)

**Когда использовать:**
- Нагрузка меняется в течение дня
- Нужна высокая доступность
- Горизонтальное масштабирование

### Создать Instance Group

```yaml
# instance-group.yaml
name: web-servers
service_account_id: <SA_ID>
instance_template:
  platform_id: standard-v3
  resources_spec:
    memory: 2147483648  # 2GB
    cores: 2
  boot_disk_spec:
    mode: READ_WRITE
    disk_spec:
      image_id: fd8fte6bebi857ortlja  # Ubuntu 22.04
      type_id: network-ssd
      size: 21474836480  # 20GB
  network_interface_specs:
    - subnet_ids:
        - <SUBNET_ID>
      primary_v4_address_spec:
        one_to_one_nat_spec:
          ip_version: IPV4
  metadata:
    ssh-keys: "ubuntu:ssh-rsa AAAA..."
    user-data: |
      #cloud-config
      runcmd:
        - apt-get update
        - apt-get install -y nginx
        - systemctl start nginx

deploy_policy:
  max_unavailable: 1
  max_creating: 2

scale_policy:
  auto_scale:
    initial_size: 2
    min_zone_size: 1
    max_size: 10
    measurement_duration: 60s
    warmup_duration: 60s
    stabilization_duration: 120s
    cpu_utilization_rule:
      utilization_target: 70

allocation_policy:
  zones:
    - zone_id: ru-central1-a
    - zone_id: ru-central1-b

load_balancer_spec:
  target_group_spec:
    name: web-servers-tg
```

```bash
# Создать group
yc compute instance-group create --file instance-group.yaml

# Проверить статус
yc compute instance-group list-instances web-servers
```

**Pricing:** Оплачиваются только VM, сам Instance Group - бесплатно

---

## Подключение к VM

### SSH (Linux/macOS)

```bash
# Узнать IP
IP=$(yc compute instance get web-server --format json | jq -r '.network_interfaces[0].primary_v4_address.one_to_one_nat.address')

# Подключиться
ssh ubuntu@$IP

# Если нужен конкретный ключ
ssh -i ~/.ssh/my-key ubuntu@$IP
```

### SSH через Serial Console (если нет сети)

```bash
# Включить serial console
yc compute instance update web-server --serial-port-enable

# Подключиться
yc compute connect-to-serial-port web-server
```

### RDP (Windows)

```bash
# Получить пароль (при создании VM с Windows)
yc compute instance get-serial-port-output windows-server | grep Password

# Подключиться через RDP клиент
# IP: <VM_IP>
# User: Administrator
# Password: <из вывода выше>
```

---

## Мониторинг и метрики

### Базовые метрики (бесплатно)

```bash
# Посмотреть в консоли
# https://console.cloud.yandex.ru/folders/<FOLDER_ID>/compute/instances/<INSTANCE_ID>/monitoring

# Доступные метрики:
# - CPU utilization (%)
# - Disk read/write (bytes/sec)
# - Network in/out (bytes/sec)
```

### Yandex Monitoring

```bash
# Получить метрики через API
yc monitoring metric-data read \
  --folder-id=$FOLDER_ID \
  --selectors='service=compute,resource_id=<INSTANCE_ID>,name=cpu_utilization' \
  --from='2026-02-05T00:00:00Z' \
  --to='2026-02-05T23:59:59Z'
```

### Установить monitoring agent

```bash
# На VM установить Unified Agent
ssh ubuntu@<VM_IP>

# Скачать и установить
curl -sSL https://storage.yandexcloud.net/monitoring-public/unified_agent/download.sh | bash

# Конфигурация в /etc/yandex/unified_agent/config.yml
# После настройки - получите детальные метрики:
# - Memory usage
# - Disk I/O по устройствам
# - Network по интерфейсам
# - Custom metrics из приложений
```

---

## Pricing (2026)

### Standard VM (Intel Ice Lake)

| vCPU | RAM | Цена/час | Цена/месяц |
|------|-----|----------|------------|
| 2 | 4GB | 2.5₽ | ~2,000₽ |
| 4 | 8GB | 5.0₽ | ~4,000₽ |
| 8 | 16GB | 10.0₽ | ~8,000₽ |
| 16 | 32GB | 20.0₽ | ~16,000₽ |

### Preemptible VM (скидка 40%)

| vCPU | RAM | Цена/час | Цена/месяц |
|------|-----|----------|------------|
| 2 | 4GB | 1.5₽ | ~1,200₽ |
| 4 | 8GB | 3.0₽ | ~2,400₽ |
| 8 | 16GB | 6.0₽ | ~4,800₽ |

### Диски

- network-ssd: 8₽/GB/месяц
- network-hdd: 2₽/GB/месяц
- Snapshots: 2₽/GB/месяц

### IP адреса

- Публичный динамический: бесплатно
- Статический: 200₽/месяц

---

## Best Practices

### Security

1. **НЕ открывайте SSH (port 22) для 0.0.0.0/0**
   - Используйте bastion host
   - Или ограничьте доступ по IP вашего офиса

2. **Используйте SSH ключи, не пароли**

3. **Регулярно обновляйте ОС**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

4. **Настройте fail2ban** (защита от brute-force)
   ```bash
   sudo apt-get install fail2ban
   ```

### Reliability

1. **Делайте регулярные snapshots**
   - Автоматизируйте через snapshot schedules

2. **Используйте Instance Groups для критичных сервисов**

3. **Мониторьте disk space**
   ```bash
   # Alerting при заполнении диска >80%
   ```

### Cost Optimization

1. **Используйте Preemptible VM где возможно**

2. **Правильный sizing**
   - Начните с малого, масштабируйте по мере роста
   - Мониторьте CPU/RAM utilization

3. **Удаляйте unused resources**
   ```bash
   # Старые snapshots
   # Неиспользуемые диски
   # Orphaned IPs
   ```

4. **Останавливайте dev/staging VM на ночь**
   ```bash
   yc compute instance stop dev-server
   ```

---

**Следующие шаги:**
- `object-storage-s3.md` - хранение файлов
- `databases-guide.md` - managed БД
- `serverless-functions.md` - альтернатива VM для stateless workloads
