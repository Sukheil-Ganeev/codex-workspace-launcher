#!/usr/bin/env python3
"""
API Connection Tester
Скрипт для проверки подключения к различным API

Использование:
    python test_api_connection.py <url> <api_key> [--method GET|POST] [--header name:value]

Примеры:
    python test_api_connection.py https://api.stripe.com/v1/charges sk_test_xxx
    python test_api_connection.py https://graph.facebook.com/v18.0/me EAAxxx --header "Content-Type:application/json"
"""

import argparse
import requests
import sys
import json
import time
from typing import Optional, Dict, List
from urllib.parse import urlparse


def test_connection(
    url: str,
    api_key: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> Dict:
    """
    Тестировать подключение к API

    Returns:
        Dict с результатами теста
    """
    result = {
        "url": url,
        "method": method,
        "success": False,
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "headers": {},
        "body_preview": None
    }

    # Подготовка headers
    request_headers = headers or {}

    # Определить тип аутентификации по URL/ключу
    parsed = urlparse(url)

    if "stripe" in parsed.netloc:
        # Stripe использует Basic Auth с API key как username
        auth = (api_key, "")
    elif "graph.facebook.com" in parsed.netloc:
        # Facebook/WhatsApp используют Bearer token
        request_headers["Authorization"] = f"Bearer {api_key}"
        auth = None
    elif "googleapis.com" in parsed.netloc:
        # Google использует query parameter
        if "?" in url:
            url += f"&key={api_key}"
        else:
            url += f"?key={api_key}"
        auth = None
    else:
        # По умолчанию Bearer token
        request_headers["Authorization"] = f"Bearer {api_key}"
        auth = None

    try:
        start_time = time.time()

        if method.upper() == "GET":
            response = requests.get(
                url,
                headers=request_headers,
                auth=auth,
                timeout=timeout
            )
        else:
            response = requests.post(
                url,
                headers=request_headers,
                auth=auth,
                timeout=timeout,
                json={}
            )

        elapsed = (time.time() - start_time) * 1000

        result["status_code"] = response.status_code
        result["response_time_ms"] = round(elapsed, 2)
        result["headers"] = dict(response.headers)

        # Превью body
        try:
            body = response.json()
            result["body_preview"] = json.dumps(body, indent=2)[:500]
        except:
            result["body_preview"] = response.text[:500]

        # Успех если 2xx или 4xx (4xx означает что API работает, но есть проблема с запросом)
        result["success"] = response.status_code < 500

    except requests.exceptions.Timeout:
        result["error"] = f"Timeout after {timeout} seconds"
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection error: {str(e)}"
    except Exception as e:
        result["error"] = f"Error: {str(e)}"

    return result


def print_result(result: Dict):
    """Вывести результат теста"""
    print("\n" + "=" * 60)
    print("API CONNECTION TEST")
    print("=" * 60)

    print(f"\nURL: {result['url']}")
    print(f"Method: {result['method']}")

    if result["success"]:
        print(f"\n{'='*20} SUCCESS {'='*20}")
        print(f"Status Code: {result['status_code']}")
        print(f"Response Time: {result['response_time_ms']} ms")

        # Показать важные headers
        important_headers = [
            "content-type", "x-ratelimit-remaining", "x-ratelimit-limit",
            "retry-after", "x-request-id"
        ]
        print("\nImportant Headers:")
        for header in important_headers:
            value = result["headers"].get(header)
            if value:
                print(f"  {header}: {value}")

        if result["body_preview"]:
            print("\nResponse Preview:")
            print("-" * 40)
            print(result["body_preview"])
            if len(result["body_preview"]) >= 500:
                print("... (truncated)")
    else:
        print(f"\n{'='*20} FAILED {'='*20}")
        if result["status_code"]:
            print(f"Status Code: {result['status_code']}")
        if result["error"]:
            print(f"Error: {result['error']}")
        if result["body_preview"]:
            print(f"\nError Details:")
            print(result["body_preview"])

    print("\n" + "=" * 60)


def test_common_apis(api_keys: Dict[str, str]):
    """Тестировать популярные API"""
    tests = [
        {
            "name": "Stripe",
            "url": "https://api.stripe.com/v1/charges",
            "key_name": "STRIPE_API_KEY"
        },
        {
            "name": "WhatsApp/Facebook",
            "url": "https://graph.facebook.com/v18.0/me",
            "key_name": "WHATSAPP_TOKEN"
        },
        {
            "name": "Google Maps",
            "url": "https://maps.googleapis.com/maps/api/geocode/json?address=Dubai",
            "key_name": "GOOGLE_MAPS_API_KEY"
        }
    ]

    print("\n" + "=" * 60)
    print("TESTING COMMON APIs")
    print("=" * 60)

    for test in tests:
        key = api_keys.get(test["key_name"])
        if key:
            print(f"\n Testing {test['name']}...")
            result = test_connection(test["url"], key)
            status = "OK" if result["success"] else "FAILED"
            code = result["status_code"] or "N/A"
            time_ms = result["response_time_ms"] or "N/A"
            print(f"   {status} | Status: {code} | Time: {time_ms}ms")
        else:
            print(f"\n {test['name']}: SKIPPED (no {test['key_name']})")


def main():
    parser = argparse.ArgumentParser(
        description="Test API connection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://api.stripe.com/v1/charges sk_test_xxx
  %(prog)s https://api.example.com/test YOUR_KEY --method POST
  %(prog)s --test-all  # Test common APIs from environment
        """
    )

    parser.add_argument("url", nargs="?", help="API URL to test")
    parser.add_argument("api_key", nargs="?", help="API key")
    parser.add_argument("--method", "-m", default="GET", choices=["GET", "POST"],
                        help="HTTP method (default: GET)")
    parser.add_argument("--header", "-H", action="append", metavar="name:value",
                        help="Additional headers")
    parser.add_argument("--timeout", "-t", type=int, default=10,
                        help="Timeout in seconds (default: 10)")
    parser.add_argument("--test-all", action="store_true",
                        help="Test common APIs using environment variables")

    args = parser.parse_args()

    if args.test_all:
        import os
        api_keys = {
            "STRIPE_API_KEY": os.getenv("STRIPE_API_KEY"),
            "WHATSAPP_TOKEN": os.getenv("WHATSAPP_TOKEN"),
            "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY"),
        }
        test_common_apis(api_keys)
        return

    if not args.url or not args.api_key:
        parser.print_help()
        print("\nError: URL and API key are required (or use --test-all)")
        sys.exit(1)

    # Parse additional headers
    headers = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                name, value = h.split(":", 1)
                headers[name.strip()] = value.strip()

    result = test_connection(
        url=args.url,
        api_key=args.api_key,
        method=args.method,
        headers=headers if headers else None,
        timeout=args.timeout
    )

    print_result(result)

    # Exit code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
