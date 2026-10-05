#!/usr/bin/env python3
"""
Калькулятор потенциального дохода от партнёрских программ
"""

def calculate_vk_adblogger(subscribers, err_percent, posts_per_month):
    """
    Рассчитать доход от VK AdBlogger

    Args:
        subscribers: количество подписчиков
        err_percent: engagement rate (%)
        posts_per_month: количество рекламных постов в месяц

    Returns:
        dict: доход и детали расчёта
    """
    # Базовые ставки по подписчикам
    if subscribers < 5000:
        base_rate = 400
    elif subscribers < 10000:
        base_rate = 650
    elif subscribers < 50000:
        base_rate = 1400
    elif subscribers < 100000:
        base_rate = 3500
    else:
        base_rate = 10000

    # Множитель engagement rate
    if err_percent < 1:
        err_multiplier = 0.7
    elif err_percent < 2:
        err_multiplier = 1.0
    elif err_percent < 5:
        err_multiplier = 1.2
    elif err_percent < 10:
        err_multiplier = 1.5
    else:
        err_multiplier = 2.0

    price_per_post = base_rate * err_multiplier
    monthly_income = price_per_post * posts_per_month

    # Налог 6% (самозанятость)
    tax = monthly_income * 0.06
    net_income = monthly_income - tax

    return {
        'platform': 'VK AdBlogger',
        'price_per_post': round(price_per_post),
        'posts_per_month': posts_per_month,
        'gross_income': round(monthly_income),
        'tax': round(tax),
        'net_income': round(net_income)
    }


def calculate_telegram_ads(subscribers, cpm, posts_per_day, ads_per_10_posts):
    """
    Рассчитать доход от Telegram Ads (TON Ads)

    Args:
        subscribers: количество подписчиков
        cpm: ставка CPM (за 1000 показов)
        posts_per_day: количество постов в день
        ads_per_10_posts: сколько реклам на каждые 10 постов (обычно 1)

    Returns:
        dict: доход и детали расчёта
    """
    # Охват = 60% от подписчиков (средний)
    reach = subscribers * 0.60

    # Рекламный охват = 60% от обычного охвата
    ad_reach = reach * 0.60

    # Сколько реклам в месяц
    ads_per_month = (posts_per_day * 30) / 10 * ads_per_10_posts

    # Доход за 1 рекламу
    income_per_ad = (ad_reach / 1000) * cpm

    # Месячный доход
    monthly_income = income_per_ad * ads_per_month

    # Налог 6%
    tax = monthly_income * 0.06
    net_income = monthly_income - tax

    return {
        'platform': 'Telegram Ads',
        'reach': round(reach),
        'ad_reach': round(ad_reach),
        'income_per_ad': round(income_per_ad),
        'ads_per_month': round(ads_per_month),
        'gross_income': round(monthly_income),
        'tax': round(tax),
        'net_income': round(net_income)
    }


def calculate_affiliate(clicks_per_month, conversion_rate, avg_commission):
    """
    Рассчитать доход от affiliate программ

    Args:
        clicks_per_month: количество кликов по ссылкам в месяц
        conversion_rate: конверсия клик → продажа (%)
        avg_commission: средняя комиссия за продажу (₽)

    Returns:
        dict: доход и детали расчёта
    """
    sales = clicks_per_month * (conversion_rate / 100)
    monthly_income = sales * avg_commission

    # Налог 6%
    tax = monthly_income * 0.06
    net_income = monthly_income - tax

    return {
        'platform': 'Affiliate (Booking/Aviasales)',
        'clicks_per_month': clicks_per_month,
        'conversion_rate': conversion_rate,
        'sales': round(sales),
        'avg_commission': avg_commission,
        'gross_income': round(monthly_income),
        'tax': round(tax),
        'net_income': round(net_income)
    }


def calculate_total(scenarios):
    """
    Рассчитать общий доход от всех платформ

    Args:
        scenarios: список результатов от calculate_*

    Returns:
        dict: общий доход
    """
    total_gross = sum(s['gross_income'] for s in scenarios)
    total_tax = sum(s['tax'] for s in scenarios)
    total_net = sum(s['net_income'] for s in scenarios)

    return {
        'total_gross': total_gross,
        'total_tax': total_tax,
        'total_net': total_net,
        'scenarios': scenarios
    }


def print_report(result):
    """Распечатать красивый отчёт"""
    print("\n" + "="*60)
    print("РАСЧЁТ ПОТЕНЦИАЛЬНОГО ДОХОДА")
    print("="*60)

    for scenario in result['scenarios']:
        print(f"\n{scenario['platform']}:")
        print("-" * 60)
        for key, value in scenario.items():
            if key != 'platform':
                print(f"  {key}: {value:,}₽" if isinstance(value, (int, float)) else f"  {key}: {value}")

    print("\n" + "="*60)
    print("ИТОГО:")
    print(f"  Валовой доход: {result['total_gross']:,}₽")
    print(f"  Налоги (6%): {result['total_tax']:,}₽")
    print(f"  Чистый доход: {result['total_net']:,}₽")
    print("="*60 + "\n")


# Пример использования

if __name__ == "__main__":
    print("Калькулятор дохода от партнёрских программ\n")

    # Сценарий: Канал 10K подписчиков
    print("Сценарий: Канал 10,000 подписчиков (туризм ОАЭ)")

    # VK AdBlogger
    vk = calculate_vk_adblogger(
        subscribers=10000,
        err_percent=3.5,
        posts_per_month=12
    )

    # Telegram Ads
    telegram = calculate_telegram_ads(
        subscribers=10000,
        cpm=350,
        posts_per_day=3,
        ads_per_10_posts=1
    )

    # Affiliate
    affiliate = calculate_affiliate(
        clicks_per_month=300,
        conversion_rate=3,
        avg_commission=900
    )

    # Общий доход
    total = calculate_total([vk, telegram, affiliate])
    print_report(total)

    # Другой сценарий: 100K подписчиков
    print("\n" + "="*60)
    print("Сценарий: Канал 100,000 подписчиков")
    print("="*60)

    vk_large = calculate_vk_adblogger(
        subscribers=100000,
        err_percent=4.0,
        posts_per_month=20
    )

    telegram_large = calculate_telegram_ads(
        subscribers=100000,
        cpm=400,
        posts_per_day=5,
        ads_per_10_posts=1
    )

    affiliate_large = calculate_affiliate(
        clicks_per_month=3000,
        conversion_rate=4,
        avg_commission=1000
    )

    total_large = calculate_total([vk_large, telegram_large, affiliate_large])
    print_report(total_large)
