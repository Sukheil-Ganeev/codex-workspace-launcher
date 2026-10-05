#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAE Tourism Currency Calculator v3.0
Handles USD/AED/RUB/KZT/USDT conversions with API-based rates and progressive markups

INCOMING FLOWS (client pays us -> we get AED):
- RUB -> AED (rubles via crypto bridge)
- KZT -> AED (tenge via Kaspi)
- USDT -> AED (crypto)

OUTGOING FLOWS (we pay partner):
- AED -> USD (cash dollars)
- AED -> RUB (rubles to Russia)
- AED -> KZT (tenge to Kazakhstan)
"""

import sys
import requests
import time
import os
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass  # Python < 3.7

# Constants
USD_TO_AED = 3.6725  # Официальный курс ЦБ ОАЭ
USDT_TO_AED = 3.65   # Реальный курс обменников

# =============================================================================
# ПРОГРЕССИВНЫЕ ШКАЛЫ НАЦЕНОК
# =============================================================================

# ВХОДЯЩИЕ: RUB → AED (фиксированная наценка к курсу в рублях)
RUB_MARKUP_SCALE = [
    (200, 5.0),      # до 200 AED: +5 руб к курсу
    (500, 4.0),      # 200-500 AED: +4 руб
    (1500, 3.5),     # 500-1500 AED: +3.5 руб
    (3000, 3.0),     # 1500-3000 AED: +3 руб
    (float('inf'), 2.5),  # от 3000 AED: +2.5 руб
]

# ВХОДЯЩИЕ: KZT → AED (процентная наценка)
KZT_MARKUP_SCALE = [
    (200, 0.20),     # до 200 AED: 20%
    (500, 0.12),     # 200-500 AED: 12%
    (1500, 0.10),    # 500-1500 AED: 10%
    (3000, 0.08),    # 1500-3000 AED: 8%
    (float('inf'), 0.07),  # от 3000 AED: 7%
]

# ВХОДЯЩИЕ: USDT → AED (процентная наценка)
USDT_MARKUP_SCALE = [
    (100, 0.12),     # до 100 AED: 12%
    (500, 0.10),     # 100-500 AED: 10%
    (1500, 0.07),    # 500-1500 AED: 7%
    (3000, 0.05),    # 1500-3000 AED: 5%
    (float('inf'), 0.04),  # от 3000 AED: 4%
]

# ИСХОДЯЩИЕ: AED → USD (процентная наценка от суммы USD)
AED_TO_USD_MARKUP_SCALE = [
    (100, 0.05),     # до 100 USD: 5%
    (500, 0.03),     # 100-500 USD: 3%
    (1500, 0.02),    # 500-1500 USD: 2%
    (3000, 0.015),   # 1500-3000 USD: 1.5%
    (float('inf'), 0.01),  # от 3000 USD: 1%
]

# ИСХОДЯЩИЕ: AED → RUB (процентная наценка от суммы AED)
AED_TO_RUB_MARKUP_SCALE = [
    (500, 0.08),     # до 500 AED: 8%
    (1500, 0.06),    # 500-1500 AED: 6%
    (3000, 0.05),    # 1500-3000 AED: 5%
    (float('inf'), 0.04),  # от 3000 AED: 4%
]

# ИСХОДЯЩИЕ: AED → KZT (процентная наценка от суммы AED)
AED_TO_KZT_MARKUP_SCALE = [
    (500, 0.07),     # до 500 AED: 7%
    (1500, 0.05),    # 500-1500 AED: 5%
    (3000, 0.04),    # 1500-3000 AED: 4%
    (float('inf'), 0.03),  # от 3000 AED: 3%
]

# Для обратной совместимости (устаревшее)
MARKUP_RUB = 3.0  # Используется в старых функциях

# API Configuration
API_KEY = "PASTE_OPENEXCHANGERATES_APP_ID_HERE"
API_BASE_URL = "https://v6.exchangerate-api.com/v6"

# Cache settings (1 hour = 3600 seconds)
CACHE_DURATION = 3600

# Cached rates
_rate_cache = {
    "RUB": {"rate": None, "timestamp": 0},
    "KZT": {"rate": None, "timestamp": 0},
    "USD": {"rate": None, "timestamp": 0}
}


def _is_cache_valid(currency):
    """Check if cached rate is still valid (within 1 hour)"""
    if _rate_cache[currency]["rate"] is None:
        return False
    return (time.time() - _rate_cache[currency]["timestamp"]) < CACHE_DURATION


def _fetch_rate_from_api(target_currency):
    """Fetch exchange rate from ExchangeRate-API"""
    try:
        url = f"{API_BASE_URL}/{API_KEY}/pair/AED/{target_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") == "success":
            return data.get("conversion_rate")
        else:
            print(f"API error: {data.get('error-type', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        print(f"Network error fetching {target_currency} rate: {e}")
        return None


def get_current_rate(currency="RUB"):
    """
    Get current exchange rate for AED to specified currency.
    Automatically fetches from API if cache is expired.
    Returns rate WITH markup for RUB.

    Args:
        currency: Target currency (RUB, KZT, USD)

    Returns:
        Exchange rate or None if unavailable
    """
    if currency not in _rate_cache:
        print(f"Unsupported currency: {currency}")
        return None

    # Check cache
    if _is_cache_valid(currency):
        cached = _rate_cache[currency]
        cache_age = int(time.time() - cached["timestamp"])
        minutes = cache_age // 60
        print(f"Using cached {currency} rate (valid for {60 - minutes} more minutes)")
        return cached["rate"]

    # Fetch fresh rate
    print(f"Fetching fresh {currency} rate from API...")
    api_rate = _fetch_rate_from_api(currency)

    if api_rate is None:
        # Return cached rate if available, even if expired
        if _rate_cache[currency]["rate"] is not None:
            print(f"API unavailable, using expired cache")
            return _rate_cache[currency]["rate"]
        return None

    # Apply markup for RUB
    if currency == "RUB":
        final_rate = api_rate + MARKUP_RUB
        print(f"AED/RUB: {api_rate:.2f} + {MARKUP_RUB} markup = {final_rate:.2f}")
    else:
        final_rate = api_rate
        print(f"AED/{currency}: {final_rate:.2f}")

    # Update cache
    _rate_cache[currency] = {
        "rate": final_rate,
        "timestamp": time.time()
    }

    return final_rate


def get_all_rates():
    """Fetch and display all supported currency rates"""
    print("\n" + "=" * 40)
    print("CURRENT EXCHANGE RATES (AED base)")
    print("=" * 40)

    rub_rate = get_current_rate("RUB")
    kzt_rate = get_current_rate("KZT")
    usd_rate = get_current_rate("USD")

    print("-" * 40)
    if rub_rate:
        print(f"1 AED = {rub_rate:.2f} RUB (with +{MARKUP_RUB} markup)")
    if kzt_rate:
        print(f"1 AED = {kzt_rate:.2f} KZT")
    if usd_rate:
        print(f"1 AED = {usd_rate:.4f} USD")
        print(f"USDT rate (approx): 1 AED = {usd_rate:.4f} USDT")
    print("=" * 40 + "\n")

    return {"RUB": rub_rate, "KZT": kzt_rate, "USD": usd_rate}


def smart_round(amount, currency="RUB"):
    """Round to nearest 10 units (RUB/KZT) to avoid banking suspicions"""
    if currency in ["RUB", "KZT"]:
        return round(amount / 10) * 10
    return round(amount, 2)


def usd_to_aed(usd):
    """Convert USD to AED"""
    return usd * USD_TO_AED


def aed_to_currency(aed, currency="RUB"):
    """Convert AED to specified currency"""
    rate = get_current_rate(currency)
    if rate is None:
        return None
    return aed * rate


def calculate_service(name, usd_price, show_all_currencies=True):
    """
    Calculate single service price with automatic rate fetching.

    Args:
        name: Service name
        usd_price: Price in USD
        show_all_currencies: If True, shows RUB, KZT and USDT
    """
    aed = usd_to_aed(usd_price)

    rub = aed_to_currency(aed, "RUB")
    if rub is None:
        return "Error: Could not fetch RUB rate"
    rub = smart_round(rub, "RUB")

    result = f"""
───────────────
💰 *{name}*

*Цена:* {usd_price}$ / {aed:.0f} AED
*К оплате:* {rub:,.0f} руб"""

    if show_all_currencies:
        kzt = aed_to_currency(aed, "KZT")
        usd_rate = get_current_rate("USD")

        if kzt:
            kzt = smart_round(kzt, "KZT")
            result += f" / {kzt:,.0f} тенге"

        if usd_rate:
            usdt = round(aed * usd_rate, 2)
            result += f" / {usdt:.2f} USDT"

    result += "\n───────────────"

    print(result)
    return {"usd": usd_price, "aed": aed, "rub": rub}


def calculate_package(services, show_all_currencies=True):
    """
    Calculate package price with all services.

    Args:
        services: list of tuples (name, usd_price)
        show_all_currencies: If True, shows RUB, KZT and USDT
    """
    total_usd = sum(price for _, price in services)
    total_aed = usd_to_aed(total_usd)

    total_rub = aed_to_currency(total_aed, "RUB")
    if total_rub is None:
        return "Error: Could not fetch RUB rate"
    total_rub = smart_round(total_rub, "RUB")

    result = f"""
───────────────
💰 *Ваш пакет:*
"""

    for name, price in services:
        aed = usd_to_aed(price)
        rub = smart_round(aed_to_currency(aed, "RUB"), "RUB")
        result += f"\n{name}: {rub:,.0f} руб"

    result += f"""
───────────────
*ИТОГО:* {total_rub:,.0f} руб
_({total_aed:.0f} AED / {total_usd}$)_"""

    if show_all_currencies:
        total_kzt = aed_to_currency(total_aed, "KZT")
        usd_rate = get_current_rate("USD")

        if total_kzt:
            total_kzt = smart_round(total_kzt, "KZT")
            result += f"\n_{total_kzt:,.0f} тенге_"

        if usd_rate:
            total_usdt = round(total_aed * usd_rate, 2)
            result += f"\n_{total_usdt:.2f} USDT_"

    result += "\n───────────────"

    print(result)
    return {"usd": total_usd, "aed": total_aed, "rub": total_rub}


def calculate_group(adults, children, adult_price, child_price, show_all_currencies=True):
    """
    Calculate group price.

    Args:
        adults: Number of adults
        children: Number of children
        adult_price: Price per adult in USD
        child_price: Price per child in USD
        show_all_currencies: If True, shows RUB, KZT and USDT
    """
    adult_total_usd = adults * adult_price
    child_total_usd = children * child_price
    total_usd = adult_total_usd + child_total_usd

    adult_total_aed = usd_to_aed(adult_total_usd)
    child_total_aed = usd_to_aed(child_total_usd)
    total_aed = adult_total_aed + child_total_aed

    adult_total_rub = smart_round(aed_to_currency(adult_total_aed, "RUB"), "RUB")
    child_total_rub = smart_round(aed_to_currency(child_total_aed, "RUB"), "RUB")
    total_rub = smart_round(aed_to_currency(total_aed, "RUB"), "RUB")

    if total_rub is None:
        return "Error: Could not fetch RUB rate"

    result = f"""
───────────────
💰 *Расчёт группы*

Взрослые: {adults} x {adult_price}$ = {adult_total_rub:,.0f} руб
Дети: {children} x {child_price}$ = {child_total_rub:,.0f} руб
───────────────
*ИТОГО:* {total_rub:,.0f} руб
_({total_aed:.0f} AED / {total_usd}$)_"""

    if show_all_currencies:
        total_kzt = aed_to_currency(total_aed, "KZT")
        usd_rate = get_current_rate("USD")

        if total_kzt:
            total_kzt = smart_round(total_kzt, "KZT")
            result += f"\n_{total_kzt:,.0f} тенге_"

        if usd_rate:
            total_usdt = round(total_aed * usd_rate, 2)
            result += f"\n_{total_usdt:.2f} USDT_"

    result += "\n───────────────"

    print(result)
    return {"usd": total_usd, "aed": total_aed, "rub": total_rub}


def calculate_with_commission(price_aed, commission_aed):
    """Calculate price with agent commission"""
    client_price_rub = smart_round(aed_to_currency(price_aed, "RUB"), "RUB")
    if client_price_rub is None:
        return "Error: Could not fetch RUB rate"

    net_price_aed = price_aed - commission_aed
    net_price_rub = smart_round(aed_to_currency(net_price_aed, "RUB"), "RUB")
    profit_rub = client_price_rub - net_price_rub

    result = f"""
───────────────
💰 *Для агента:*

Цена клиента: {price_aed:.0f} AED ({client_price_rub:,.0f} руб)
Ваша комиссия: {commission_aed:.0f} AED
Ваша цена: {net_price_aed:.0f} AED ({net_price_rub:,.0f} руб)
───────────────
*Ваш доход:* {profit_rub:,.0f} руб
───────────────"""

    print(result)
    return {
        "client_price": client_price_rub,
        "agent_cost": net_price_rub,
        "profit": profit_rub
    }


def format_price_whatsapp(name, usd_price, description=""):
    """
    Format service price for WhatsApp according to style guide.
    Uses only allowed emojis: 💰 and ⚠️

    Args:
        name: Service name
        usd_price: Price in USD
        description: Optional description in italics
    """
    aed = usd_to_aed(usd_price)
    rub = smart_round(aed_to_currency(aed, "RUB"), "RUB")
    kzt = smart_round(aed_to_currency(aed, "KZT"), "KZT")
    usd_rate = get_current_rate("USD")

    if rub is None:
        return "Error: Could not fetch rates"

    result = f"*{name.upper()}*"
    if description:
        result += f"\n_{description}_"

    result += f"""
───────────────
💰 *ЦЕНА*

```{usd_price}$```  {aed:.0f} AED
*К оплате:* {rub:,.0f} руб"""

    if kzt:
        result += f" / {kzt:,.0f} тенге"

    if usd_rate:
        usdt = round(aed * usd_rate, 2)
        result += f" / {usdt:.2f} USDT"

    result += """
───────────────
⚠️ *ВАЖНО*

*ОПЛАТА*
USD | Рубли СПБ | AED (курс 3.65) | Тенге | USDT
───────────────"""

    print(result)
    return result


def format_price_telegram(name, usd_price, description=""):
    """
    Format service price for Telegram according to style guide.
    Uses double asterisks for bold, double underscores for italic.

    Args:
        name: Service name
        usd_price: Price in USD
        description: Optional description in italics
    """
    aed = usd_to_aed(usd_price)
    rub = smart_round(aed_to_currency(aed, "RUB"), "RUB")
    kzt = smart_round(aed_to_currency(aed, "KZT"), "KZT")
    usd_rate = get_current_rate("USD")

    if rub is None:
        return "Error: Could not fetch rates"

    result = f"**{name.upper()}**"
    if description:
        result += f"\n__{description}__"

    result += f"""
──────────────────
💰 **ЦЕНА**

**{usd_price}$** — {aed:.0f} AED
**К оплате:** {rub:,.0f} руб"""

    if kzt:
        result += f" / {kzt:,.0f} тенге"

    if usd_rate:
        usdt = round(aed * usd_rate, 2)
        result += f" / {usdt:.2f} USDT"

    result += """
──────────────────
⚠️ **ВАЖНО**

**ОПЛАТА**
USD | Рубли СПБ | AED (курс 3.65) | Тенге | USDT
──────────────────"""

    print(result)
    return result


def get_rate_info():
    """Display current rate information and cache status"""
    print("\n" + "=" * 40)
    print("RATE CACHE STATUS")
    print("=" * 40)

    now = time.time()

    for currency, cache in _rate_cache.items():
        if cache["rate"] is None:
            print(f"{currency}: Not cached")
        else:
            age = int(now - cache["timestamp"])
            remaining = CACHE_DURATION - age
            if remaining > 0:
                print(f"{currency}: {cache['rate']:.2f} (valid for {remaining // 60} min)")
            else:
                print(f"{currency}: {cache['rate']:.2f} (EXPIRED)")

    print("=" * 40 + "\n")


# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ПРОГРЕССИВНЫХ НАЦЕНОК
# =============================================================================

def _get_markup_from_scale(amount, scale):
    """
    Получить наценку из шкалы по сумме.

    Args:
        amount: Сумма для определения диапазона
        scale: Шкала наценок [(limit, markup), ...]

    Returns:
        Значение наценки для данной суммы
    """
    for limit, markup in scale:
        if amount < limit:
            return markup
    return scale[-1][1]  # Вернуть последнее значение если ничего не подошло


def _format_markup_scale_info(amount, scale, unit="%"):
    """Форматировать информацию о шкале наценок"""
    markup = _get_markup_from_scale(amount, scale)
    if unit == "%":
        return f"{markup * 100:.1f}%"
    else:
        return f"+{markup} {unit}"


# =============================================================================
# ВХОДЯЩИЕ ПОТОКИ (клиент платит нам → мы получаем AED)
# =============================================================================

def calculate_rub_to_aed(aed_amount):
    """
    Рассчитать сколько RUB должен заплатить клиент за услугу в AED.
    Использует прогрессивную наценку к курсу.

    Схема: Клиент RUB → криптомост → мы получаем AED

    Args:
        aed_amount: Сумма в AED которую нужно получить

    Returns:
        dict с информацией о расчёте
    """
    api_rate = _fetch_rate_from_api("RUB")
    if api_rate is None:
        api_rate = _rate_cache["RUB"].get("rate", 27.0)  # Fallback

    markup = _get_markup_from_scale(aed_amount, RUB_MARKUP_SCALE)
    our_rate = api_rate + markup
    rub_amount = smart_round(aed_amount * our_rate, "RUB")

    result = f"""
┌─────────────────────────────────────────────────────────────┐
│               RUB → AED (ВХОДЯЩИЙ ПОТОК)                    │
├─────────────────────────────────────────────────────────────┤
│ Услуга стоит:          {aed_amount:.0f} AED                               │
│ API курс:              1 AED = {api_rate:.2f} RUB                    │
│ Наценка:               +{markup} руб (диапазон до {_get_scale_limit(aed_amount, RUB_MARKUP_SCALE)} AED)         │
│ Наш курс:              1 AED = {our_rate:.2f} RUB                    │
├─────────────────────────────────────────────────────────────┤
│ КЛИЕНТ ПЛАТИТ:         {rub_amount:,.0f} RUB                          │
└─────────────────────────────────────────────────────────────┘"""

    print(result)
    return {
        "aed_amount": aed_amount,
        "api_rate": api_rate,
        "markup": markup,
        "our_rate": our_rate,
        "client_pays_rub": rub_amount
    }


def calculate_kzt_to_aed(aed_amount):
    """
    Рассчитать сколько KZT должен заплатить клиент за услугу в AED.
    Использует процентную прогрессивную наценку.

    Схема: Клиент KZT (Kaspi) → банкомат ОАЭ → мы получаем AED

    Args:
        aed_amount: Сумма в AED которую нужно получить

    Returns:
        dict с информацией о расчёте
    """
    api_rate = _fetch_rate_from_api("KZT")
    if api_rate is None:
        api_rate = _rate_cache["KZT"].get("rate", 120.0)  # Fallback

    markup_pct = _get_markup_from_scale(aed_amount, KZT_MARKUP_SCALE)
    our_rate = api_rate * (1 + markup_pct)
    kzt_amount = smart_round(aed_amount * our_rate, "KZT")

    result = f"""
┌─────────────────────────────────────────────────────────────┐
│               KZT → AED (ВХОДЯЩИЙ ПОТОК)                    │
├─────────────────────────────────────────────────────────────┤
│ Услуга стоит:          {aed_amount:.0f} AED                               │
│ API курс:              1 AED = {api_rate:.2f} KZT                   │
│ Наценка:               {markup_pct * 100:.0f}% (диапазон до {_get_scale_limit(aed_amount, KZT_MARKUP_SCALE)} AED)            │
│ Наш курс:              1 AED = {our_rate:.2f} KZT                   │
├─────────────────────────────────────────────────────────────┤
│ КЛИЕНТ ПЛАТИТ:         {kzt_amount:,.0f} KZT                         │
└─────────────────────────────────────────────────────────────┘"""

    print(result)
    return {
        "aed_amount": aed_amount,
        "api_rate": api_rate,
        "markup_pct": markup_pct,
        "our_rate": our_rate,
        "client_pays_kzt": kzt_amount
    }


def calculate_usdt_to_aed(aed_amount):
    """
    Рассчитать сколько USDT должен заплатить клиент за услугу в AED.
    Использует процентную прогрессивную наценку.

    Схема: Клиент USDT (TRC20) → обменник в Дубае → мы получаем AED

    Args:
        aed_amount: Сумма в AED которую нужно получить

    Returns:
        dict с информацией о расчёте
    """
    official_rate = USD_TO_AED  # 3.6725

    markup_pct = _get_markup_from_scale(aed_amount, USDT_MARKUP_SCALE)
    our_rate = official_rate * (1 - markup_pct)  # Уменьшаем курс для клиента
    usdt_amount = round(aed_amount / our_rate, 2)

    # Расчёт нашей экономики
    exchanger_rate = USDT_TO_AED  # 3.65 (реальный курс обменника)
    we_receive_aed = usdt_amount * exchanger_rate
    our_profit_aed = we_receive_aed - aed_amount

    result = f"""
┌─────────────────────────────────────────────────────────────┐
│               USDT → AED (ВХОДЯЩИЙ ПОТОК)                   │
├─────────────────────────────────────────────────────────────┤
│ Услуга стоит:          {aed_amount:.0f} AED                               │
│ Офиц. курс:            1 USDT = {official_rate:.4f} AED                │
│ Наценка:               {markup_pct * 100:.0f}% (диапазон до {_get_scale_limit(aed_amount, USDT_MARKUP_SCALE)} AED)            │
│ Наш курс:              1 USDT = {our_rate:.4f} AED                │
├─────────────────────────────────────────────────────────────┤
│ КЛИЕНТ ПЛАТИТ:         {usdt_amount:.2f} USDT                        │
├─────────────────────────────────────────────────────────────┤
│ Твоя экономика:                                             │
│ Получишь USDT:         {usdt_amount:.2f}                              │
│ Обменяешь по {exchanger_rate}:      {we_receive_aed:.2f} AED                        │
│ Клиенту нужно:         {aed_amount:.0f} AED                               │
│ ПРИБЫЛЬ:               {our_profit_aed:.2f} AED ({our_profit_aed/aed_amount*100:.1f}%)                 │
└─────────────────────────────────────────────────────────────┘"""

    print(result)
    return {
        "aed_amount": aed_amount,
        "official_rate": official_rate,
        "markup_pct": markup_pct,
        "our_rate": our_rate,
        "client_pays_usdt": usdt_amount,
        "we_receive_aed": we_receive_aed,
        "profit_aed": our_profit_aed
    }


# =============================================================================
# ИСХОДЯЩИЕ ПОТОКИ (мы платим партнёру)
# =============================================================================

def calculate_aed_to_usd(usd_amount):
    """
    Рассчитать сколько AED нужно потратить чтобы получить USD.
    Использует процентную прогрессивную наценку.

    Схема: Наличные AED → обменник → наличные USD

    Args:
        usd_amount: Сумма в USD которую нужно получить

    Returns:
        dict с информацией о расчёте
    """
    official_rate = USD_TO_AED  # 3.6725
    exchanger_rate = 3.69  # Средний курс обменников при покупке USD

    markup_pct = _get_markup_from_scale(usd_amount, AED_TO_USD_MARKUP_SCALE)
    our_rate = exchanger_rate * (1 + markup_pct)
    aed_needed = round(usd_amount * our_rate, 2)

    # Наша прибыль
    real_cost_aed = usd_amount * exchanger_rate
    our_profit_aed = aed_needed - real_cost_aed

    result = f"""
┌─────────────────────────────────────────────────────────────┐
│               AED → USD (ИСХОДЯЩИЙ ПОТОК)                   │
├─────────────────────────────────────────────────────────────┤
│ Партнёру нужно:        {usd_amount:.0f} USD                              │
│ Офиц. курс:            1 USD = {official_rate:.4f} AED                │
│ Курс обменника:        1 USD = {exchanger_rate:.2f} AED                   │
│ Наценка:               {markup_pct * 100:.1f}% (диапазон до {_get_scale_limit(usd_amount, AED_TO_USD_MARKUP_SCALE)} USD)           │
│ Наш курс:              1 USD = {our_rate:.4f} AED                │
├─────────────────────────────────────────────────────────────┤
│ С КЛИЕНТА БЕРЁМ:       {aed_needed:.2f} AED                        │
│ Реальные расходы:      {real_cost_aed:.2f} AED                        │
│ ПРИБЫЛЬ:               {our_profit_aed:.2f} AED ({markup_pct * 100:.1f}%)                 │
└─────────────────────────────────────────────────────────────┘"""

    print(result)
    return {
        "usd_amount": usd_amount,
        "official_rate": official_rate,
        "exchanger_rate": exchanger_rate,
        "markup_pct": markup_pct,
        "our_rate": our_rate,
        "client_pays_aed": aed_needed,
        "real_cost_aed": real_cost_aed,
        "profit_aed": our_profit_aed
    }


def calculate_aed_to_rub(aed_amount, target_rub=None):
    """
    Рассчитать перевод AED → RUB (в Россию).
    Использует криптомост: AED → USDT → P2P → RUB

    Args:
        aed_amount: Сумма в AED которую тратим
        target_rub: (опционально) если указано, рассчитает сколько AED нужно

    Returns:
        dict с информацией о расчёте
    """
    # Курсы
    aed_to_usdt_rate = 1 / USDT_TO_AED  # ~0.274 USDT за 1 AED
    usdt_to_rub_p2p = 99.0  # Курс P2P продажи (хуже чем ЦБ)

    markup_pct = _get_markup_from_scale(aed_amount, AED_TO_RUB_MARKUP_SCALE)

    # Расчёт
    usdt_from_aed = aed_amount * aed_to_usdt_rate * 0.99  # -1% обменник
    rub_from_p2p = usdt_from_aed * usdt_to_rub_p2p
    rub_after_markup = rub_from_p2p * (1 - markup_pct)  # Отдаём меньше из-за наценки
    rub_final = smart_round(rub_after_markup, "RUB")

    our_profit_rub = rub_from_p2p - rub_final

    result = f"""
┌─────────────────────────────────────────────────────────────┐
│               AED → RUB (ИСХОДЯЩИЙ ПОТОК)                   │
│               Криптомост: AED → USDT → P2P → RUB            │
├─────────────────────────────────────────────────────────────┤
│ Имеем:                 {aed_amount:.0f} AED                               │
│ Обменник ({USDT_TO_AED} AED):     {usdt_from_aed:.2f} USDT (минус 1% потери)    │
│ P2P продажа ({usdt_to_rub_p2p} RUB):  {rub_from_p2p:.0f} RUB                        │
│ Наценка:               {markup_pct * 100:.0f}% (диапазон до {_get_scale_limit(aed_amount, AED_TO_RUB_MARKUP_SCALE)} AED)            │
├─────────────────────────────────────────────────────────────┤
│ ПОЛУЧАТЕЛЬ В РФ:       {rub_final:,.0f} RUB                         │
│ НАША ПРИБЫЛЬ:          {our_profit_rub:,.0f} RUB                         │
└─────────────────────────────────────────────────────────────┘"""

    print(result)
    return {
        "aed_amount": aed_amount,
        "usdt_received": usdt_from_aed,
        "rub_from_p2p": rub_from_p2p,
        "markup_pct": markup_pct,
        "recipient_gets_rub": rub_final,
        "profit_rub": our_profit_rub
    }


def calculate_aed_to_kzt(aed_amount):
    """
    Рассчитать перевод AED → KZT (в Казахстан).
    Использует криптомост: AED → USDT → P2P → KZT

    Args:
        aed_amount: Сумма в AED которую тратим

    Returns:
        dict с информацией о расчёте
    """
    # Курсы
    aed_to_usdt_rate = 1 / USDT_TO_AED  # ~0.274 USDT за 1 AED
    usdt_to_kzt_p2p = 515.0  # Курс P2P продажи

    markup_pct = _get_markup_from_scale(aed_amount, AED_TO_KZT_MARKUP_SCALE)

    # Расчёт
    usdt_from_aed = aed_amount * aed_to_usdt_rate * 0.99  # -1% обменник
    kzt_from_p2p = usdt_from_aed * usdt_to_kzt_p2p
    kzt_after_markup = kzt_from_p2p * (1 - markup_pct)  # Отдаём меньше из-за наценки
    kzt_final = smart_round(kzt_after_markup, "KZT")

    our_profit_kzt = kzt_from_p2p - kzt_final

    result = f"""
┌─────────────────────────────────────────────────────────────┐
│               AED → KZT (ИСХОДЯЩИЙ ПОТОК)                   │
│               Криптомост: AED → USDT → P2P → KZT            │
├─────────────────────────────────────────────────────────────┤
│ Имеем:                 {aed_amount:.0f} AED                               │
│ Обменник ({USDT_TO_AED} AED):     {usdt_from_aed:.2f} USDT (минус 1% потери)    │
│ P2P продажа ({usdt_to_kzt_p2p} KZT): {kzt_from_p2p:.0f} KZT                        │
│ Наценка:               {markup_pct * 100:.0f}% (диапазон до {_get_scale_limit(aed_amount, AED_TO_KZT_MARKUP_SCALE)} AED)            │
├─────────────────────────────────────────────────────────────┤
│ ПОЛУЧАТЕЛЬ В КЗ:       {kzt_final:,.0f} KZT                        │
│ НАША ПРИБЫЛЬ:          {our_profit_kzt:,.0f} KZT                        │
└─────────────────────────────────────────────────────────────┘"""

    print(result)
    return {
        "aed_amount": aed_amount,
        "usdt_received": usdt_from_aed,
        "kzt_from_p2p": kzt_from_p2p,
        "markup_pct": markup_pct,
        "recipient_gets_kzt": kzt_final,
        "profit_kzt": our_profit_kzt
    }


def _get_scale_limit(amount, scale):
    """Получить верхний лимит текущего диапазона"""
    for limit, _ in scale:
        if amount < limit:
            return limit if limit != float('inf') else "∞"
    return "∞"


# =============================================================================
# УНИВЕРСАЛЬНАЯ ФУНКЦИЯ КОНВЕРТАЦИИ
# =============================================================================

def convert_currency(amount, from_currency, to_currency):
    """
    Универсальная функция конвертации валют с прогрессивными наценками.

    Args:
        amount: Сумма в исходной валюте
        from_currency: Исходная валюта (RUB, KZT, USDT, AED)
        to_currency: Целевая валюта (AED, USD, RUB, KZT)

    Returns:
        dict с результатами конвертации
    """
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()

    # ВХОДЯЩИЕ ПОТОКИ (клиент платит → мы получаем AED)
    if to_curr == "AED":
        if from_curr == "RUB":
            # Обратный расчёт: сколько AED получим за RUB
            api_rate = get_current_rate("RUB")
            aed_approx = amount / api_rate if api_rate else 0
            return calculate_rub_to_aed(aed_approx)
        elif from_curr == "KZT":
            api_rate = get_current_rate("KZT")
            aed_approx = amount / api_rate if api_rate else 0
            return calculate_kzt_to_aed(aed_approx)
        elif from_curr == "USDT":
            aed_approx = amount * USDT_TO_AED
            return calculate_usdt_to_aed(aed_approx)

    # ИСХОДЯЩИЕ ПОТОКИ (мы платим → партнёр получает валюту)
    if from_curr == "AED":
        if to_curr == "USD":
            # amount это AED, нужно узнать сколько USD получит партнёр
            usd_approx = amount / USD_TO_AED
            return calculate_aed_to_usd(usd_approx)
        elif to_curr == "RUB":
            return calculate_aed_to_rub(amount)
        elif to_curr == "KZT":
            return calculate_aed_to_kzt(amount)

    print(f"Конвертация {from_curr} → {to_curr} не поддерживается")
    return None


def show_all_markup_scales():
    """Показать все шкалы наценок"""
    print("""
╔═════════════════════════════════════════════════════════════╗
║              ШКАЛЫ ПРОГРЕССИВНЫХ НАЦЕНОК                    ║
╠═════════════════════════════════════════════════════════════╣
║                                                             ║
║  ВХОДЯЩИЕ ПОТОКИ (клиент платит → мы получаем AED)          ║
║  ─────────────────────────────────────────────────          ║
║                                                             ║
║  RUB → AED (фиксированная наценка к курсу):                 ║
║  ┌─────────────┬─────────────┐                              ║
║  │ Сумма (AED) │ Наценка     │                              ║
║  ├─────────────┼─────────────┤                              ║
║  │ до 200      │ +5 руб      │                              ║
║  │ 200–500     │ +4 руб      │                              ║
║  │ 500–1,500   │ +3.5 руб    │                              ║
║  │ 1,500–3,000 │ +3 руб      │                              ║
║  │ от 3,000    │ +2.5 руб    │                              ║
║  └─────────────┴─────────────┘                              ║
║                                                             ║
║  KZT → AED (процентная наценка):                            ║
║  ┌─────────────┬─────────────┐                              ║
║  │ Сумма (AED) │ Наценка     │                              ║
║  ├─────────────┼─────────────┤                              ║
║  │ до 200      │ 20%         │                              ║
║  │ 200–500     │ 12%         │                              ║
║  │ 500–1,500   │ 10%         │                              ║
║  │ 1,500–3,000 │ 8%          │                              ║
║  │ от 3,000    │ 7%          │                              ║
║  └─────────────┴─────────────┘                              ║
║                                                             ║
║  USDT → AED (процентная наценка):                           ║
║  ┌─────────────┬─────────────┐                              ║
║  │ Сумма (AED) │ Наценка     │                              ║
║  ├─────────────┼─────────────┤                              ║
║  │ до 100      │ 12%         │                              ║
║  │ 100–500     │ 10%         │                              ║
║  │ 500–1,500   │ 7%          │                              ║
║  │ 1,500–3,000 │ 5%          │                              ║
║  │ от 3,000    │ 4%          │                              ║
║  └─────────────┴─────────────┘                              ║
║                                                             ║
╠═════════════════════════════════════════════════════════════╣
║                                                             ║
║  ИСХОДЯЩИЕ ПОТОКИ (мы платим → партнёр получает)            ║
║  ─────────────────────────────────────────────────          ║
║                                                             ║
║  AED → USD (процентная наценка от USD):                     ║
║  ┌─────────────┬─────────────┐                              ║
║  │ Сумма (USD) │ Наценка     │                              ║
║  ├─────────────┼─────────────┤                              ║
║  │ до 100      │ 5%          │                              ║
║  │ 100–500     │ 3%          │                              ║
║  │ 500–1,500   │ 2%          │                              ║
║  │ 1,500–3,000 │ 1.5%        │                              ║
║  │ от 3,000    │ 1%          │                              ║
║  └─────────────┴─────────────┘                              ║
║                                                             ║
║  AED → RUB (процентная наценка от AED):                     ║
║  ┌─────────────┬─────────────┐                              ║
║  │ Сумма (AED) │ Наценка     │                              ║
║  ├─────────────┼─────────────┤                              ║
║  │ до 500      │ 8%          │                              ║
║  │ 500–1,500   │ 6%          │                              ║
║  │ 1,500–3,000 │ 5%          │                              ║
║  │ от 3,000    │ 4%          │                              ║
║  └─────────────┴─────────────┘                              ║
║                                                             ║
║  AED → KZT (процентная наценка от AED):                     ║
║  ┌─────────────┬─────────────┐                              ║
║  │ Сумма (AED) │ Наценка     │                              ║
║  ├─────────────┼─────────────┤                              ║
║  │ до 500      │ 7%          │                              ║
║  │ 500–1,500   │ 5%          │                              ║
║  │ 1,500–3,000 │ 4%          │                              ║
║  │ от 3,000    │ 3%          │                              ║
║  └─────────────┴─────────────┘                              ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    print("=" * 60)
    print("UAE Tourism Currency Calculator v3.0")
    print("Progressive markups for all currency flows")
    print("=" * 60)

    print("\n[IN] INCOMING FLOWS (client pays -> we get AED):")
    print("  calculate_rub_to_aed(aed_amount)   - RUB -> AED")
    print("  calculate_kzt_to_aed(aed_amount)   - KZT -> AED")
    print("  calculate_usdt_to_aed(aed_amount)  - USDT -> AED")

    print("\n[OUT] OUTGOING FLOWS (we pay -> partner receives):")
    print("  calculate_aed_to_usd(usd_amount)   - AED -> USD")
    print("  calculate_aed_to_rub(aed_amount)   - AED -> RUB")
    print("  calculate_aed_to_kzt(aed_amount)   - AED -> KZT")

    print("\n[*] UNIVERSAL FUNCTIONS:")
    print("  convert_currency(amount, from, to) - Any pair conversion")
    print("  show_all_markup_scales()           - Show all markups")

    print("\n[+] BASE FUNCTIONS:")
    print("  get_all_rates()          - Get all rates")
    print("  get_current_rate('RUB')  - Get specific rate")
    print("  calculate_service(name, usd_price)")
    print("  format_price_whatsapp(name, usd_price)")
    print("  format_price_telegram(name, usd_price)")

    print("\n" + "=" * 60)
    print("Examples:")
    print("  >>> calculate_usdt_to_aed(500)    # Service for 500 AED")
    print("  >>> calculate_aed_to_rub(1000)    # Send 1000 AED to Russia")
    print("  >>> show_all_markup_scales()      # Show all markups")
    print("=" * 60)
