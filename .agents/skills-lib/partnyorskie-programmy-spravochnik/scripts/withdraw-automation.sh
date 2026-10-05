#!/bin/bash
# Автоматизация проверки балансов и напоминаний о выводе средств

# Конфигурация
MIN_BALANCE_VK=500      # Минимум для вывода VK AdBlogger
MIN_BALANCE_TELEGRAM=50 # Минимум для вывода Telegram (в TON)
MIN_BALANCE_DZEN=1000   # Минимум для вывода Дзен
NOTIFY_TELEGRAM_BOT=""  # Telegram Bot API token (опционально)
NOTIFY_CHAT_ID=""       # Telegram Chat ID (опционально)

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "AFFILIATE WITHDRAWAL AUTOMATION"
echo "======================================"
echo ""

# Функция отправки уведомления в Telegram
send_telegram_notification() {
    local message=$1
    if [ -n "$NOTIFY_TELEGRAM_BOT" ] && [ -n "$NOTIFY_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${NOTIFY_TELEGRAM_BOT}/sendMessage" \
            -d "chat_id=${NOTIFY_CHAT_ID}" \
            -d "text=${message}" \
            -d "parse_mode=Markdown" > /dev/null
    fi
}

# Проверка баланса VK AdBlogger (заглушка, нужна интеграция API)
check_vk_balance() {
    echo "Проверка VK AdBlogger..."
    # TODO: Интегрировать VK API для проверки баланса
    # Пока что заглушка
    local balance=780

    echo -e "  Текущий баланс: ${GREEN}${balance}₽${NC}"

    if [ $balance -ge $MIN_BALANCE_VK ]; then
        echo -e "  ${YELLOW}✓ Доступно для вывода!${NC}"
        echo "  Минимум: ${MIN_BALANCE_VK}₽"
        echo "  Ссылка: https://dev.vk.com/adblogger (Выплаты)"

        send_telegram_notification "💰 VK AdBlogger: ${balance}₽ доступно для вывода! (Минимум: ${MIN_BALANCE_VK}₽)"
        return 0
    else
        echo "  Недостаточно для вывода (минимум: ${MIN_BALANCE_VK}₽)"
        local remaining=$((MIN_BALANCE_VK - balance))
        echo "  Осталось заработать: ${remaining}₽"
        return 1
    fi
}

# Проверка баланса Telegram TON Ads
check_telegram_balance() {
    echo ""
    echo "Проверка Telegram TON Ads..."
    # TODO: Интегрировать Telegram API для проверки баланса
    local balance_ton=120
    local balance_rub=$((balance_ton * 50)) # Курс TON/RUB примерный

    echo -e "  Текущий баланс: ${GREEN}${balance_ton} TON${NC} (~${balance_rub}₽)"

    if [ $balance_ton -ge $MIN_BALANCE_TELEGRAM ]; then
        echo -e "  ${YELLOW}✓ Доступно для вывода!${NC}"
        echo "  Минимум: ${MIN_BALANCE_TELEGRAM} TON"
        echo "  Вывод: через TON Wallet"

        send_telegram_notification "💰 Telegram Ads: ${balance_ton} TON (~${balance_rub}₽) доступно для вывода!"
        return 0
    else
        echo "  Недостаточно для вывода (минимум: ${MIN_BALANCE_TELEGRAM} TON)"
        local remaining=$((MIN_BALANCE_TELEGRAM - balance_ton))
        echo "  Осталось заработать: ${remaining} TON"
        return 1
    fi
}

# Проверка баланса Яндекс.Дзен
check_dzen_balance() {
    echo ""
    echo "Проверка Яндекс.Дзен..."
    # TODO: Интегрировать Дзен API
    local balance=2500

    echo -e "  Текущий баланс: ${GREEN}${balance}₽${NC}"

    if [ $balance -ge $MIN_BALANCE_DZEN ]; then
        echo -e "  ${YELLOW}✓ Доступно для вывода!${NC}"
        echo "  Минимум: ${MIN_BALANCE_DZEN}₽"
        echo "  Ссылка: https://dzen.ru (Монетизация → Выплаты)"

        send_telegram_notification "💰 Яндекс.Дзен: ${balance}₽ доступно для вывода! (Минимум: ${MIN_BALANCE_DZEN}₽)"
        return 0
    else
        echo "  Недостаточно для вывода (минимум: ${MIN_BALANCE_DZEN}₽)"
        local remaining=$((MIN_BALANCE_DZEN - balance))
        echo "  Осталось заработать: ${remaining}₽"
        return 1
    fi
}

# Проверка affiliate программ
check_affiliate_balances() {
    echo ""
    echo "Проверка Affiliate программ..."
    echo "  (Booking.com, Aviasales, GetYourGuide)"
    echo "  Обычно выплаты автоматические при достижении минимума"
    echo "  Проверьте личный кабинет каждой программы:"
    echo "    - Booking: https://partners.booking.com"
    echo "    - Aviasales: https://aviasales.ru/partner"
    echo "    - GetYourGuide: https://getyourguide.com/affiliate"
}

# Напоминание о самозанятости
remind_nalog() {
    echo ""
    echo "======================================"
    echo -e "${RED}ВАЖНО: Налоги (Самозанятость)${NC}"
    echo "======================================"
    echo "После каждого вывода средств:"
    echo "  1. Открыть приложение 'Мой налог'"
    echo "  2. Создать чек на полученную сумму"
    echo "  3. Налог 6% (с юрлиц) списывается автоматически"
    echo ""
    echo "Примеры:"
    echo "  VK AdBlogger → 780₽ → налог 47₽ → чистыми 733₽"
    echo "  Telegram Ads → 6000₽ → налог 360₽ → чистыми 5640₽"
    echo ""
}

# Главная функция
main() {
    local can_withdraw=0

    check_vk_balance && can_withdraw=1
    check_telegram_balance && can_withdraw=1
    check_dzen_balance && can_withdraw=1
    check_affiliate_balances

    echo ""
    echo "======================================"
    if [ $can_withdraw -eq 1 ]; then
        echo -e "${GREEN}✓ Есть средства для вывода!${NC}"
    else
        echo -e "${YELLOW}Пока недостаточно для вывода${NC}"
    fi
    echo "======================================"

    remind_nalog

    echo "Дата проверки: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

# Запустить
main

# Добавить в cron для автоматической проверки:
# crontab -e
# 0 10 * * * /path/to/withdraw-automation.sh  # Каждый день в 10:00
