# Monitoring & Backup

## Yandex Monitoring

```bash
# Создать алерт
yc monitoring alert create \
  --name high-cpu \
  --condition "cpu_utilization > 80" \
  --notify-email admin@tourism.com
```

## Automated Backups

```bash
# PostgreSQL (автоматически)
# Настраивается при создании кластера

# VM snapshots (schedule)
yc compute snapshot-schedule create \
  --name daily-backup \
  --expression "0 3 * * *" \
  --retention-period 7d \
  --disk-id $DISK_ID
```

## Hystax Disaster Recovery

```bash
# DR для критичной инфраструктуры
# Настройка через console
```

**См. также:** `assets/templates/monitoring-alerts.yaml`, `scripts/backup-database.sh`
