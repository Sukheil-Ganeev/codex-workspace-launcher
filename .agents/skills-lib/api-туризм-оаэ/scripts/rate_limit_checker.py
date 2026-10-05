#!/usr/bin/env python3
"""
Rate Limit Checker
Скрипт для проверки rate limits различных API

Использование:
    python rate_limit_checker.py https://api.example.com/endpoint YOUR_API_KEY
    python rate_limit_checker.py --service stripe sk_test_xxx
    python rate_limit_checker.py --service whatsapp EAAxxxx

Функционал:
- Определение текущих лимитов
- Мониторинг использования
- Рекомендации по оптимизации
"""

import argparse
import requests
import time
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass
import json


@dataclass
class RateLimitInfo:
    """Информация о rate limits"""
    limit: Optional[int] = None           # Максимум запросов
    remaining: Optional[int] = None       # Осталось запросов
    reset_at: Optional[int] = None        # Timestamp сброса
    reset_in_seconds: Optional[int] = None
    window: Optional[str] = None          # Окно (per minute, per hour)
    headers: Dict = None


def extract_rate_limits_from_headers(headers: Dict) -> RateLimitInfo:
    """Извлечь информацию о rate limits из headers"""

    info = RateLimitInfo(headers=dict(headers))

    # Стандартные headers
    header_mappings = {
        "limit": [
            "x-ratelimit-limit",
            "x-rate-limit-limit",
            "ratelimit-limit",
            "x-ratelimit-requests-limit"
        ],
        "remaining": [
            "x-ratelimit-remaining",
            "x-rate-limit-remaining",
            "ratelimit-remaining",
            "x-ratelimit-requests-remaining"
        ],
        "reset": [
            "x-ratelimit-reset",
            "x-rate-limit-reset",
            "ratelimit-reset",
            "retry-after"
        ]
    }

    # Поиск headers
    headers_lower = {k.lower(): v for k, v in headers.items()}

    for attr, possible_headers in header_mappings.items():
        for header in possible_headers:
            if header in headers_lower:
                value = headers_lower[header]
                try:
                    if attr == "reset":
                        # reset может быть timestamp или seconds
                        reset_value = int(value)
                        if reset_value > 1000000000:  # Это timestamp
                            info.reset_at = reset_value
                            info.reset_in_seconds = reset_value - int(time.time())
                        else:  # Это секунды
                            info.reset_in_seconds = reset_value
                            info.reset_at = int(time.time()) + reset_value
                    else:
                        setattr(info, attr, int(value))
                except ValueError:
                    pass
                break

    return info


def check_rate_limits(
    url: str,
    api_key: str,
    auth_type: str = "bearer"
) -> RateLimitInfo:
    """
    Проверить rate limits для API

    Args:
        url: API endpoint URL
        api_key: API ключ
        auth_type: Тип аутентификации (bearer, basic, header)
    """
    headers = {}

    if auth_type == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    elif auth_type == "basic":
        import base64
        auth = base64.b64encode(f"{api_key}:".encode()).decode()
        headers["Authorization"] = f"Basic {auth}"
    elif auth_type == "header":
        headers["X-API-Key"] = api_key

    try:
        response = requests.get(url, headers=headers, timeout=10)
        return extract_rate_limits_from_headers(response.headers)
    except Exception as e:
        print(f"Error: {e}")
        return RateLimitInfo()


def check_stripe_limits(api_key: str) -> Dict:
    """Проверить rate limits для Stripe"""
    # Stripe не возвращает rate limit headers напрямую
    # но у них есть стандартные лимиты

    info = {
        "service": "Stripe",
        "documented_limits": {
            "test_mode": {
                "requests_per_second": 25,
                "notes": "Burst up to 100"
            },
            "live_mode": {
                "requests_per_second": 100,
                "notes": "Contact support for higher limits"
            }
        },
        "current_usage": None
    }

    # Попробовать сделать запрос
    try:
        response = requests.get(
            "https://api.stripe.com/v1/charges",
            auth=(api_key, ""),
            params={"limit": 1}
        )

        info["current_usage"] = {
            "status_code": response.status_code,
            "request_id": response.headers.get("request-id"),
            "stripe_version": response.headers.get("stripe-version")
        }

        # Stripe возвращает 429 при превышении
        if response.status_code == 429:
            info["rate_limited"] = True
            info["retry_after"] = response.headers.get("retry-after")
        else:
            info["rate_limited"] = False

    except Exception as e:
        info["error"] = str(e)

    return info


def check_whatsapp_limits(token: str, phone_id: str = None) -> Dict:
    """Проверить rate limits для WhatsApp Business API"""

    info = {
        "service": "WhatsApp Business API",
        "documented_limits": {
            "messages": {
                "per_second": 80,
                "per_phone_number": "Varies by tier"
            },
            "tiers": {
                "unverified": "250 unique recipients/24h",
                "verified": "1000 unique recipients/24h",
                "tier_1": "10000 unique recipients/24h",
                "tier_2": "100000 unique recipients/24h",
                "unlimited": "Unlimited"
            }
        },
        "current_status": None
    }

    if not phone_id:
        return info

    # Получить информацию об аккаунте
    try:
        response = requests.get(
            f"https://graph.facebook.com/v18.0/{phone_id}",
            params={
                "fields": "messaging_limit_tier,quality_score",
                "access_token": token
            }
        )

        data = response.json()

        if "error" not in data:
            info["current_status"] = {
                "messaging_limit_tier": data.get("messaging_limit_tier"),
                "quality_score": data.get("quality_score")
            }
        else:
            info["error"] = data["error"].get("message")

    except Exception as e:
        info["error"] = str(e)

    return info


def check_google_maps_limits(api_key: str) -> Dict:
    """Проверить rate limits для Google Maps API"""

    info = {
        "service": "Google Maps API",
        "documented_limits": {
            "directions": {
                "requests_per_minute": 3000,
                "requests_per_day": "Depends on billing"
            },
            "geocoding": {
                "requests_per_minute": 3000,
                "requests_per_day": 40000
            },
            "places": {
                "requests_per_minute": 6000
            }
        },
        "billing_status": None
    }

    # Тестовый запрос
    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": "Dubai",
                "key": api_key
            }
        )

        data = response.json()

        if data.get("status") == "OK":
            info["api_status"] = "Active"
        elif data.get("status") == "OVER_QUERY_LIMIT":
            info["api_status"] = "Rate limited"
            info["rate_limited"] = True
        elif data.get("status") == "REQUEST_DENIED":
            info["api_status"] = "Denied"
            info["error"] = data.get("error_message")
        else:
            info["api_status"] = data.get("status")

    except Exception as e:
        info["error"] = str(e)

    return info


def run_burst_test(url: str, api_key: str, requests_count: int = 10) -> Dict:
    """
    Запустить burst test для определения лимитов

    Отправляет несколько запросов подряд и отслеживает ответы
    """
    results = {
        "total_requests": requests_count,
        "successful": 0,
        "rate_limited": 0,
        "errors": 0,
        "response_times": [],
        "first_rate_limit_at": None
    }

    headers = {"Authorization": f"Bearer {api_key}"}

    for i in range(requests_count):
        start = time.time()

        try:
            response = requests.get(url, headers=headers, timeout=10)
            elapsed = (time.time() - start) * 1000

            results["response_times"].append(elapsed)

            if response.status_code == 429:
                results["rate_limited"] += 1
                if results["first_rate_limit_at"] is None:
                    results["first_rate_limit_at"] = i + 1

                # Проверить retry-after
                retry_after = response.headers.get("retry-after")
                if retry_after:
                    results["retry_after"] = retry_after
                    break  # Остановиться при rate limit

            elif response.status_code < 400:
                results["successful"] += 1
            else:
                results["errors"] += 1

        except Exception as e:
            results["errors"] += 1

    # Статистика
    if results["response_times"]:
        results["avg_response_time_ms"] = round(
            sum(results["response_times"]) / len(results["response_times"]), 2
        )
        results["max_response_time_ms"] = round(max(results["response_times"]), 2)

    return results


def print_info(info: Dict, title: str = "Rate Limit Information"):
    """Вывести информацию о rate limits"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(json.dumps(info, indent=2, default=str))
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Check API rate limits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generic API:
    %(prog)s https://api.example.com/endpoint YOUR_API_KEY

  Stripe:
    %(prog)s --service stripe sk_test_xxx

  WhatsApp:
    %(prog)s --service whatsapp EAAxxxx --phone-id 123456

  Burst test:
    %(prog)s https://api.example.com/endpoint KEY --burst 20
        """
    )

    parser.add_argument("url", nargs="?", help="API URL to check")
    parser.add_argument("api_key", nargs="?", help="API key")
    parser.add_argument("--service", "-s",
                        choices=["stripe", "whatsapp", "google-maps"],
                        help="Check specific service")
    parser.add_argument("--phone-id", help="WhatsApp phone number ID")
    parser.add_argument("--burst", "-b", type=int,
                        help="Run burst test with N requests")
    parser.add_argument("--auth-type", "-a", default="bearer",
                        choices=["bearer", "basic", "header"],
                        help="Authentication type")

    args = parser.parse_args()

    # Проверка конкретного сервиса
    if args.service:
        if not args.api_key:
            print("Error: API key is required")
            sys.exit(1)

        if args.service == "stripe":
            info = check_stripe_limits(args.api_key)
        elif args.service == "whatsapp":
            info = check_whatsapp_limits(args.api_key, args.phone_id)
        elif args.service == "google-maps":
            info = check_google_maps_limits(args.api_key)

        print_info(info, f"{args.service.upper()} Rate Limits")
        return

    # Burst test
    if args.burst:
        if not args.url or not args.api_key:
            print("Error: URL and API key are required for burst test")
            sys.exit(1)

        print(f"\nRunning burst test ({args.burst} requests)...")
        results = run_burst_test(args.url, args.api_key, args.burst)
        print_info(results, "Burst Test Results")
        return

    # Обычная проверка
    if not args.url or not args.api_key:
        parser.print_help()
        sys.exit(1)

    info = check_rate_limits(args.url, args.api_key, args.auth_type)

    print("\n" + "=" * 60)
    print("RATE LIMIT CHECK")
    print("=" * 60)

    if info.limit:
        print(f"\nLimit: {info.limit} requests")
    if info.remaining is not None:
        print(f"Remaining: {info.remaining} requests")
    if info.reset_in_seconds:
        print(f"Reset in: {info.reset_in_seconds} seconds")

    if not any([info.limit, info.remaining, info.reset_at]):
        print("\nNo rate limit headers found.")
        print("This API may not expose rate limit information.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
