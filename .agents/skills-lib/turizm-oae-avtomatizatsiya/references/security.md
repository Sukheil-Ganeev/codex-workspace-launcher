# Руководство по безопасности

## Обзор

Это руководство описывает практики безопасности для AI-агента туристического бизнеса ОАЭ. Система обрабатывает персональные данные клиентов (PII), финансовую информацию и бизнес-данные.

---

## Классификация данных

### Уровни конфиденциальности

| Уровень | Описание | Примеры | Требования |
|---------|----------|---------|------------|
| **Critical** | Финансовые данные | Карты, IBAN, пароли | Шифрование, аудит, маскирование |
| **High** | Персональные данные | Паспорта, телефоны, email | Шифрование, согласие, удаление |
| **Medium** | Бизнес-данные | Бронирования, цены | Контроль доступа |
| **Low** | Публичные данные | Описания туров, FAQ | Базовая защита |

---

## GDPR и защита персональных данных

### Основные принципы GDPR

1. **Законность обработки** - иметь правовое основание
2. **Ограничение цели** - собирать только нужные данные
3. **Минимизация данных** - не хранить лишнее
4. **Точность** - поддерживать данные актуальными
5. **Ограничение хранения** - удалять устаревшие данные
6. **Целостность и конфиденциальность** - защищать данные

### Права субъектов данных

```python
class DataSubjectRights:
    """Реализация прав субъектов данных по GDPR"""

    def right_to_access(self, user_id: str) -> dict:
        """Право на доступ (Art. 15)"""
        return {
            "personal_data": get_all_user_data(user_id),
            "processing_purposes": get_processing_purposes(),
            "retention_period": get_retention_period(),
            "recipients": get_data_recipients()
        }

    def right_to_rectification(self, user_id: str, corrections: dict):
        """Право на исправление (Art. 16)"""
        update_user_data(user_id, corrections)
        log_audit("data_rectification", user_id, corrections)

    def right_to_erasure(self, user_id: str):
        """Право на удаление (Art. 17)"""
        # Удаляем из всех систем
        delete_from_airtable(user_id)
        delete_from_logs(user_id)
        delete_from_backups(user_id)
        log_audit("data_erasure", user_id)

    def right_to_data_portability(self, user_id: str) -> bytes:
        """Право на переносимость (Art. 20)"""
        data = get_all_user_data(user_id)
        return export_to_json(data)
```

### Согласие на обработку

```python
CONSENT_TEXT = """
Нажимая "Отправить", вы соглашаетесь на обработку персональных данных
(телефон, email, имя) для целей бронирования туристических услуг.

Ваши данные:
- Хранятся на защищенных серверах в ОАЭ/ЕС
- Используются только для оказания услуг
- Могут быть удалены по вашему запросу

Подробнее: [Политика конфиденциальности]
"""

def record_consent(user_id: str, consent_type: str):
    """Запись согласия в базу"""
    consent_record = {
        "user_id": user_id,
        "consent_type": consent_type,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": get_client_ip(),
        "user_agent": get_user_agent(),
        "consent_text_version": "v1.2"
    }
    save_consent(consent_record)
```

---

## Шифрование данных

### Шифрование в покое (At Rest)

```python
from cryptography.fernet import Fernet
import os

# Ключ шифрования (хранить безопасно!)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_pii(data: str) -> str:
    """Шифрует персональные данные"""
    return cipher.encrypt(data.encode()).decode()

def decrypt_pii(encrypted_data: str) -> str:
    """Расшифровывает персональные данные"""
    return cipher.decrypt(encrypted_data.encode()).decode()

# Пример использования
client_data = {
    "name": "Иван Петров",
    "phone": encrypt_pii("+971501234567"),
    "passport": encrypt_pii("AB1234567"),
    "email": encrypt_pii("ivan@example.com")
}
```

### Шифрование в передаче (In Transit)

```python
# Всегда используйте HTTPS
API_BASE_URL = "https://api.example.com"  # НЕ http://

# Проверка SSL сертификатов
import requests
response = requests.get(url, verify=True)  # verify=True по умолчанию

# Для внутренних сервисов
import ssl
context = ssl.create_default_context()
context.check_hostname = True
context.verify_mode = ssl.CERT_REQUIRED
```

### Хранение ключей

```python
# НИКОГДА не храните ключи в коде!

# Правильно: переменные окружения
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

# Правильно: secrets manager
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
secret = client.access_secret_version(name="projects/xxx/secrets/api-key/versions/latest")
API_KEY = secret.payload.data.decode()

# Правильно: vault
import hvac
vault_client = hvac.Client(url='https://vault.example.com')
API_KEY = vault_client.secrets.kv.read_secret_version(path='api-keys')['data']['anthropic']
```

---

## Маскирование данных

### Функции маскирования

```python
import re

def mask_phone(phone: str) -> str:
    """
    Маскирует телефонный номер
    +971501234567 -> +971****4567
    """
    if not phone or len(phone) < 8:
        return "****"
    return phone[:4] + "****" + phone[-4:]

def mask_email(email: str) -> str:
    """
    Маскирует email
    user@domain.com -> u***@domain.com
    """
    if not email or '@' not in email:
        return "***@***"
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        return f"**@{domain}"
    return f"{local[0]}***@{domain}"

def mask_card(card_number: str) -> str:
    """
    Маскирует номер карты
    4111111111111234 -> **** **** **** 1234
    """
    digits = re.sub(r'\D', '', card_number)
    if len(digits) < 4:
        return "****"
    return f"**** **** **** {digits[-4:]}"

def mask_iban(iban: str) -> str:
    """
    Маскирует IBAN
    AE720331234567890642584 -> AE72****642584
    """
    if not iban or len(iban) < 10:
        return "****"
    return f"{iban[:4]}****{iban[-6:]}"

def mask_passport(passport: str) -> str:
    """
    Маскирует номер паспорта
    AB1234567 -> AB****567
    """
    if not passport or len(passport) < 6:
        return "****"
    return f"{passport[:2]}****{passport[-3:]}"

def mask_sensitive_data(data: dict) -> dict:
    """Маскирует все чувствительные поля в словаре"""
    masked = data.copy()

    sensitive_fields = {
        'phone': mask_phone,
        'email': mask_email,
        'card_number': mask_card,
        'iban': mask_iban,
        'passport': mask_passport,
        'password': lambda x: '********',
        'api_key': lambda x: x[:8] + '...' if x else '****'
    }

    for field, mask_func in sensitive_fields.items():
        if field in masked and masked[field]:
            masked[field] = mask_func(str(masked[field]))

    return masked
```

### Использование в логах

```python
import logging

class SensitiveDataFilter(logging.Filter):
    """Фильтр для маскирования данных в логах"""

    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Маскируем телефоны
            record.msg = re.sub(
                r'\+?\d{10,15}',
                lambda m: mask_phone(m.group()),
                record.msg
            )
            # Маскируем email
            record.msg = re.sub(
                r'[\w\.-]+@[\w\.-]+\.\w+',
                lambda m: mask_email(m.group()),
                record.msg
            )
        return True

# Применение фильтра
logger = logging.getLogger('api')
logger.addFilter(SensitiveDataFilter())
```

---

## Управление доступом

### Ролевая модель (RBAC)

```python
from enum import Enum
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    VIEWER = "viewer"

PERMISSIONS = {
    Role.ADMIN: ["read", "write", "delete", "admin"],
    Role.MANAGER: ["read", "write", "delete"],
    Role.AGENT: ["read", "write"],
    Role.VIEWER: ["read"]
}

def require_permission(permission: str):
    """Декоратор проверки прав доступа"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            user_permissions = PERMISSIONS.get(user.role, [])

            if permission not in user_permissions:
                log_audit("access_denied", user.id, {
                    "action": func.__name__,
                    "required": permission
                })
                raise PermissionError(f"Permission denied: {permission}")

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Использование
@require_permission("write")
def update_booking(booking_id: str, data: dict):
    # Только manager и admin могут обновлять
    pass

@require_permission("delete")
def delete_client(client_id: str):
    # Только manager и admin могут удалять
    pass
```

### Принцип минимальных привилегий

```python
# Отдельные API ключи для разных сервисов
KEYS = {
    "classification": os.getenv('CLAUDE_KEY_READONLY'),  # Только чтение
    "response_gen": os.getenv('CLAUDE_KEY_STANDARD'),    # Стандартный
    "admin_ops": os.getenv('CLAUDE_KEY_ADMIN')           # Полный доступ
}

def get_client_for_task(task_type: str):
    """Возвращает клиент с минимальными правами для задачи"""
    key = KEYS.get(task_type, KEYS['classification'])
    return anthropic.Anthropic(api_key=key)
```

---

## Аудит и логирование

### Структура аудит-логов

```python
import json
from datetime import datetime
from typing import Optional

def audit_log(
    action: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    details: Optional[dict] = None,
    status: str = "success"
):
    """Записывает событие в аудит лог"""

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": mask_sensitive_data(details or {}),
        "status": status,
        "ip_address": get_client_ip(),
        "user_agent": get_user_agent(),
        "session_id": get_session_id()
    }

    # Запись в файл
    with open("audit.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Отправка в SIEM (опционально)
    if action in ["delete", "admin_access", "data_export"]:
        send_to_siem(log_entry)

# Примеры использования
audit_log("read", user_id, "client", "C123", {"fields": ["name", "phone"]})
audit_log("update", user_id, "booking", "B456", {"changes": {"status": "confirmed"}})
audit_log("delete", user_id, "client", "C789", status="denied")
```

### Обязательные события для логирования

| Событие | Важность | Детали |
|---------|----------|--------|
| Вход в систему | High | user_id, IP, успех/неудача |
| Доступ к PII | High | какие данные, цель |
| Изменение данных | High | старое/новое значение |
| Удаление данных | Critical | что удалено, кем |
| Экспорт данных | Critical | объем, формат |
| Изменение прав | Critical | кому, какие права |
| API вызовы | Medium | endpoint, параметры |
| Ошибки | Medium | тип, stack trace |

---

## Ротация ключей API

### Процедура ротации

```python
import os
from datetime import datetime, timedelta

KEY_ROTATION_DAYS = 90

def check_key_age():
    """Проверяет возраст ключей"""
    key_created = datetime.fromisoformat(os.getenv('KEY_CREATED_DATE'))
    age = (datetime.utcnow() - key_created).days

    if age > KEY_ROTATION_DAYS:
        send_alert(
            "API key rotation required",
            f"Key age: {age} days (limit: {KEY_ROTATION_DAYS})"
        )
        return True

    if age > KEY_ROTATION_DAYS - 7:
        send_warning(f"API key rotation due in {KEY_ROTATION_DAYS - age} days")

    return False

def rotate_api_key(service: str):
    """Процедура ротации ключа"""

    # 1. Создать новый ключ в консоли сервиса
    # 2. Обновить в secrets manager
    update_secret(f"{service}_api_key", new_key)

    # 3. Обновить в .env (для dev)
    # 4. Развернуть обновление
    trigger_deployment()

    # 5. Проверить работоспособность
    if verify_new_key(service):
        # 6. Удалить старый ключ
        revoke_old_key(service)
        audit_log("key_rotation", "system", "api_key", service)
    else:
        # Откат
        rollback_key(service)
        alert_ops("Key rotation failed")
```

### Безопасное хранение .env

```bash
# .gitignore
.env
.env.local
.env.production
*.pem
*.key
credentials.json

# Права доступа к файлу
chmod 600 .env

# Проверка что .env не в git
git status --porcelain | grep -E "\.env"
```

---

## Инциденты безопасности

### Процедура реагирования

```python
class SecurityIncident:
    """Управление инцидентами безопасности"""

    SEVERITY_LEVELS = {
        "critical": {"response_time": 15, "notify": ["cto", "security", "legal"]},
        "high": {"response_time": 60, "notify": ["security", "ops"]},
        "medium": {"response_time": 240, "notify": ["security"]},
        "low": {"response_time": 1440, "notify": ["security"]}
    }

    def report_incident(self, incident_type: str, severity: str, details: dict):
        """Регистрация инцидента"""

        incident = {
            "id": generate_incident_id(),
            "type": incident_type,
            "severity": severity,
            "details": details,
            "reported_at": datetime.utcnow().isoformat(),
            "status": "open"
        }

        # Сохранить
        save_incident(incident)

        # Уведомить
        config = self.SEVERITY_LEVELS[severity]
        for recipient in config["notify"]:
            send_urgent_notification(recipient, incident)

        # Для critical - немедленные действия
        if severity == "critical":
            self.emergency_response(incident)

        return incident["id"]

    def emergency_response(self, incident: dict):
        """Экстренные меры при критических инцидентах"""

        if incident["type"] == "data_breach":
            # Заблокировать доступ
            disable_affected_accounts()
            # Отозвать токены
            revoke_all_tokens()
            # Уведомить регулятора (GDPR требует в течение 72 часов)
            schedule_regulator_notification()

        if incident["type"] == "api_key_leak":
            # Немедленная ротация ключей
            rotate_all_keys()
            # Проверить использование утекших ключей
            audit_key_usage()
```

### Типы инцидентов

| Тип | Описание | Действия |
|-----|----------|----------|
| data_breach | Утечка данных | Блокировка, уведомление, расследование |
| api_key_leak | Утечка ключей | Ротация, аудит использования |
| unauthorized_access | Несанкционированный доступ | Блокировка, расследование |
| ddos_attack | DDoS атака | WAF, rate limiting, масштабирование |
| malware | Вредоносное ПО | Изоляция, сканирование, восстановление |

---

## Чек-лист безопасности

### При разработке

- [ ] API ключи в переменных окружения, не в коде
- [ ] Шифрование PII данных
- [ ] Маскирование в логах
- [ ] Валидация входных данных
- [ ] Защита от инъекций (SQL, XSS)
- [ ] HTTPS для всех соединений
- [ ] Аудит всех критических операций

### При деплое

- [ ] .env не в git
- [ ] Права доступа к файлам настроены
- [ ] SSL сертификаты валидны
- [ ] Firewall настроен
- [ ] Rate limiting включен
- [ ] Мониторинг активен
- [ ] Бэкапы настроены

### Регулярно (ежемесячно)

- [ ] Обзор логов доступа
- [ ] Проверка возраста ключей
- [ ] Обновление зависимостей
- [ ] Тест восстановления из бэкапа
- [ ] Ревизия прав доступа
- [ ] Pentest (ежеквартально)
