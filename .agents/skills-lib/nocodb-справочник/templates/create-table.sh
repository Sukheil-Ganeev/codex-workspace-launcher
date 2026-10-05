#!/usr/bin/env bash
# =============================================================================
# NocoDB -- Создание таблицы через API v2
# =============================================================================
# Использование:
#   1. Заполнить переменные ниже (BASE_URL, API_TOKEN, BASE_ID)
#   2. chmod +x create-table.sh
#   3. ./create-table.sh
#
# Скрипт создаст таблицу "Bookings" с полями разных типов.
# Адаптируйте под свои нужды.
# =============================================================================

set -euo pipefail

# --- Настройки (ОБЯЗАТЕЛЬНО заполнить) ---
BASE_URL="${NOCODB_BASE_URL:-https://app.nocodb.com}"   # URL вашего NocoDB
API_TOKEN="${NOCODB_API_TOKEN:-YOUR_API_TOKEN_HERE}"      # API Token из Settings -> Tokens
BASE_ID="${NOCODB_BASE_ID:-YOUR_BASE_ID_HERE}"            # ID базы (формат: p_xxxxxxxx)

# --- Заголовки ---
AUTH_HEADER="xc-token: ${API_TOKEN}"
CONTENT_TYPE="Content-Type: application/json"

echo "=== Создание таблицы в NocoDB ==="
echo "URL: ${BASE_URL}"
echo "Base ID: ${BASE_ID}"
echo ""

# --- Шаг 1: Создать таблицу ---
echo "[1/3] Создание таблицы 'Bookings'..."

TABLE_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/api/v2/meta/bases/${BASE_ID}/tables" \
  -H "${AUTH_HEADER}" \
  -H "${CONTENT_TYPE}" \
  -d '{
    "table_name": "Bookings",
    "title": "Bookings",
    "columns": [
      {
        "title": "Название",
        "column_name": "title",
        "uidt": "SingleLineText"
      }
    ]
  }')

# Извлекаем ID таблицы из ответа
TABLE_ID=$(echo "${TABLE_RESPONSE}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")

if [ -z "${TABLE_ID}" ]; then
  echo "ОШИБКА: Не удалось создать таблицу."
  echo "Ответ сервера: ${TABLE_RESPONSE}"
  exit 1
fi

echo "Таблица создана. ID: ${TABLE_ID}"
echo ""

# --- Шаг 2: Добавить поля разных типов ---
echo "[2/3] Добавление полей..."

# Функция для добавления поля
add_column() {
  local field_json="$1"
  local field_title="$2"

  local response=$(curl -s -X POST \
    "${BASE_URL}/api/v2/meta/tables/${TABLE_ID}/columns" \
    -H "${AUTH_HEADER}" \
    -H "${CONTENT_TYPE}" \
    -d "${field_json}")

  local col_id=$(echo "${response}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

  if [ -n "${col_id}" ]; then
    echo "  + ${field_title} (ID: ${col_id})"
  else
    echo "  ! Ошибка при создании поля '${field_title}': ${response}"
  fi
}

# Текстовое поле (LongText)
add_column '{
  "title": "Описание",
  "uidt": "LongText"
}' "Описание (LongText)"

# Число
add_column '{
  "title": "Количество",
  "uidt": "Number"
}' "Количество (Number)"

# Валюта
add_column '{
  "title": "Цена продажи",
  "uidt": "Currency",
  "meta": {"currency_locale": "en-AE", "currency_code": "AED"}
}' "Цена продажи (Currency)"

# Валюта (себестоимость)
add_column '{
  "title": "Себестоимость",
  "uidt": "Currency",
  "meta": {"currency_locale": "en-AE", "currency_code": "AED"}
}' "Себестоимость (Currency)"

# Дата
add_column '{
  "title": "Дата экскурсии",
  "uidt": "Date",
  "meta": {"date_format": "YYYY-MM-DD"}
}' "Дата экскурсии (Date)"

# SingleSelect -- выпадающий список
add_column '{
  "title": "Статус",
  "uidt": "SingleSelect",
  "dtxp": "'\''Заявка'\'','\''Подтверждено'\'','\''Оплачено'\'','\''Завершено'\'','\''Отменено'\'','\''Возврат'\''"
}' "Статус (SingleSelect)"

# SingleSelect -- способ оплаты
add_column '{
  "title": "Способ оплаты",
  "uidt": "SingleSelect",
  "dtxp": "'\''Cash'\'','\''Bank Transfer'\'','\''Kaspi'\'','\''Sber'\'','\''Crypto'\''"
}' "Способ оплаты (SingleSelect)"

# SingleSelect -- валюта оплаты
add_column '{
  "title": "Валюта оплаты",
  "uidt": "SingleSelect",
  "dtxp": "'\''AED'\'','\''USD'\'','\''RUB'\'','\''KZT'\'','\''Crypto'\''"
}' "Валюта оплаты (SingleSelect)"

# Email
add_column '{
  "title": "Email клиента",
  "uidt": "Email"
}' "Email клиента (Email)"

# PhoneNumber
add_column '{
  "title": "Телефон клиента",
  "uidt": "PhoneNumber"
}' "Телефон клиента (PhoneNumber)"

# Checkbox
add_column '{
  "title": "VIP",
  "uidt": "Checkbox"
}' "VIP (Checkbox)"

# Rating
add_column '{
  "title": "Оценка",
  "uidt": "Rating",
  "meta": {"max": 5}
}' "Оценка (Rating)"

# URL
add_column '{
  "title": "Ссылка на продукт",
  "uidt": "URL"
}' "Ссылка на продукт (URL)"

echo ""

# --- Шаг 3: Создать тестовую запись ---
echo "[3/3] Создание тестовой записи..."

RECORD_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/api/v2/tables/${TABLE_ID}/records" \
  -H "${AUTH_HEADER}" \
  -H "${CONTENT_TYPE}" \
  -d '{
    "Название": "Desert Safari VIP",
    "Описание": "Джип-сафари в пустыне с ужином и шоу",
    "Количество": 4,
    "Цена продажи": 600,
    "Себестоимость": 400,
    "Дата экскурсии": "2026-03-01",
    "Статус": "Подтверждено",
    "Способ оплаты": "Cash",
    "Валюта оплаты": "AED",
    "Email клиента": "client@example.com",
    "Телефон клиента": "+971501234567",
    "VIP": true,
    "Оценка": 5,
    "Ссылка на продукт": "https://example.com/desert-safari"
  }')

echo "Тестовая запись создана."
echo ""

# --- Итог ---
echo "=== Готово! ==="
echo "Таблица: Bookings"
echo "Table ID: ${TABLE_ID}"
echo "URL: ${BASE_URL}/dashboard/#/nc/${BASE_ID}"
echo ""
echo "Следующие шаги:"
echo "  1. Откройте NocoDB и проверьте таблицу"
echo "  2. Настройте Views (Kanban по Статус, Calendar по Дата)"
echo "  3. Создайте Links к другим таблицам (Clients, Products, Suppliers)"
