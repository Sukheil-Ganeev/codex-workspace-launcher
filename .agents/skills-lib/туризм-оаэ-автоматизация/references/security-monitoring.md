# Безопасность, мониторинг и алерты

Полное руководство по безопасности данных, GDPR, маскированию PII, алертам и аудиту.

---

## Безопасность персональных данных

### GDPR соответствие
- Хранить данные в EU/UAE регионах
- Шифровать PII (телефоны, email, паспорта)
- Логировать все доступы к данным
- Обеспечить право на удаление данных (GDPR Art. 17)
- Получать согласие на обработку данных

### Маскирование данных в логах

```python
def mask_phone(phone: str) -> str:
    """Маскирует телефон: +971****4567"""
    if len(phone) < 8:
        return "****"
    return phone[:4] + "****" + phone[-4:]

def mask_card(card: str) -> str:
    """Маскирует карту: **** **** **** 4567"""
    digits = ''.join(filter(str.isdigit, card))
    if len(digits) < 4:
        return "****"
    return "**** **** **** " + digits[-4:]

def mask_iban(iban: str) -> str:
    """Маскирует IBAN: AE72****642584"""
    if len(iban) < 10:
        return "****"
    return iban[:4] + "****" + iban[-6:]
```

**Примеры маскирования:**
- Телефоны: `+971501234567` -> `+971****4567`
- Карты: `4111 1111 1111 1234` -> `**** **** **** 1234`
- IBAN: `AE720331234567890642584` -> `AE72****642584`
- Email: `user@domain.com` -> `u***@domain.com`

### Ротация ключей API
- Менять ключи каждые 90 дней
- Хранить в .env файле (не в коде!)
- Использовать разные ключи для dev/prod
- Настроить алерты при компрометации

### Безопасное хранение

```bash
# .env НЕ коммитить в git!
echo ".env" >> .gitignore

# Использовать secrets manager для production
# AWS Secrets Manager / Azure Key Vault / GCP Secret Manager
```

---

## Настройка алертов

```python
# Примеры алертов
alerts = {
    "api_latency": {
        "condition": "latency > 5s",
        "action": "slack",
        "channel": "#alerts-critical",
        "message": "API latency exceeded 5s: {latency}s"
    },
    "error_rate": {
        "condition": "error_rate > 5%",
        "action": "email",
        "to": "ops@company.com",
        "message": "Error rate alert: {error_rate}%"
    },
    "daily_cost": {
        "condition": "daily_cost > $100",
        "action": "sms",
        "to": "+971501234567",
        "message": "Daily API cost exceeded $100: ${cost}"
    }
}
```

---

## Логи для аудита

```python
import json
from datetime import datetime

def audit_log(action: str, user: str, data: dict):
    """Запись в аудит лог"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user": user,
        "data": mask_sensitive(data),
        "ip": get_client_ip()
    }

    # Записать в файл/БД
    with open("audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## Логирование

```python
import logging

logging.basicConfig(
    filename='D:/Downloads/туризм-оаэ-автоматизация/logs/automation.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

logger = logging.getLogger('ai_agent')
logger.info("Message classified", extra={'type': 'inquiry', 'priority': 'medium'})
```
