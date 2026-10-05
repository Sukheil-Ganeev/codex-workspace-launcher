#!/usr/bin/env python3
"""
Webhook Signature Validator
Скрипт для валидации подписей webhook от различных сервисов

Использование:
    python validate_webhook.py --service stripe --payload '{"id":"evt_xxx"}' --signature "t=xxx,v1=xxx" --secret "whsec_xxx"
    python validate_webhook.py --service whatsapp --payload '{"entry":[]}' --signature "sha256=xxx" --secret "app_secret"

Поддерживаемые сервисы:
    - stripe
    - whatsapp
    - github
    - generic (HMAC-SHA256)
"""

import argparse
import hmac
import hashlib
import time
import sys
import json
from typing import Optional


def validate_stripe_signature(
    payload: str,
    signature: str,
    secret: str,
    tolerance: int = 300
) -> dict:
    """
    Валидация подписи Stripe webhook

    Stripe signature format: t=timestamp,v1=signature

    Args:
        payload: Raw request body
        signature: Stripe-Signature header
        secret: Webhook secret (whsec_xxx)
        tolerance: Max age in seconds (default 5 min)
    """
    result = {
        "valid": False,
        "service": "stripe",
        "error": None,
        "details": {}
    }

    try:
        # Парсинг signature header
        elements = dict(item.split("=", 1) for item in signature.split(","))
        timestamp = elements.get("t")
        expected_sig = elements.get("v1")

        if not timestamp or not expected_sig:
            result["error"] = "Invalid signature format"
            return result

        result["details"]["timestamp"] = timestamp

        # Проверка timestamp
        age = int(time.time()) - int(timestamp)
        result["details"]["age_seconds"] = age

        if age > tolerance:
            result["error"] = f"Signature too old: {age} seconds (max {tolerance})"
            return result

        # Вычисление подписи
        signed_payload = f"{timestamp}.{payload}"
        computed_sig = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        result["details"]["computed_signature"] = computed_sig[:20] + "..."
        result["details"]["expected_signature"] = expected_sig[:20] + "..."

        # Сравнение
        if hmac.compare_digest(computed_sig, expected_sig):
            result["valid"] = True
        else:
            result["error"] = "Signature mismatch"

    except Exception as e:
        result["error"] = str(e)

    return result


def validate_whatsapp_signature(
    payload: str,
    signature: str,
    secret: str
) -> dict:
    """
    Валидация подписи WhatsApp/Facebook webhook

    Signature format: sha256=xxx

    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header
        secret: App secret
    """
    result = {
        "valid": False,
        "service": "whatsapp",
        "error": None,
        "details": {}
    }

    try:
        # Вычисление подписи
        computed_sig = hmac.new(
            secret.encode(),
            payload.encode() if isinstance(payload, str) else payload,
            hashlib.sha256
        ).hexdigest()

        expected_sig = signature.replace("sha256=", "")

        result["details"]["computed_signature"] = computed_sig[:20] + "..."
        result["details"]["expected_signature"] = expected_sig[:20] + "..."

        if hmac.compare_digest(computed_sig, expected_sig):
            result["valid"] = True
        else:
            result["error"] = "Signature mismatch"

    except Exception as e:
        result["error"] = str(e)

    return result


def validate_github_signature(
    payload: str,
    signature: str,
    secret: str
) -> dict:
    """
    Валидация подписи GitHub webhook

    Signature format: sha256=xxx

    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header
        secret: Webhook secret
    """
    result = {
        "valid": False,
        "service": "github",
        "error": None,
        "details": {}
    }

    try:
        # Вычисление подписи
        computed_sig = "sha256=" + hmac.new(
            secret.encode(),
            payload.encode() if isinstance(payload, str) else payload,
            hashlib.sha256
        ).hexdigest()

        result["details"]["computed_signature"] = computed_sig[:30] + "..."
        result["details"]["expected_signature"] = signature[:30] + "..."

        if hmac.compare_digest(computed_sig, signature):
            result["valid"] = True
        else:
            result["error"] = "Signature mismatch"

    except Exception as e:
        result["error"] = str(e)

    return result


def validate_generic_hmac(
    payload: str,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> dict:
    """
    Валидация generic HMAC подписи

    Args:
        payload: Raw request body
        signature: Expected signature (hex)
        secret: Secret key
        algorithm: Hash algorithm (sha256, sha1, etc.)
    """
    result = {
        "valid": False,
        "service": "generic",
        "error": None,
        "details": {"algorithm": algorithm}
    }

    try:
        hash_func = getattr(hashlib, algorithm)
        computed_sig = hmac.new(
            secret.encode(),
            payload.encode() if isinstance(payload, str) else payload,
            hash_func
        ).hexdigest()

        # Убрать возможный prefix
        expected_sig = signature
        for prefix in ["sha256=", "sha1=", "sha512="]:
            if expected_sig.startswith(prefix):
                expected_sig = expected_sig[len(prefix):]
                break

        result["details"]["computed_signature"] = computed_sig[:20] + "..."
        result["details"]["expected_signature"] = expected_sig[:20] + "..."

        if hmac.compare_digest(computed_sig, expected_sig):
            result["valid"] = True
        else:
            result["error"] = "Signature mismatch"

    except Exception as e:
        result["error"] = str(e)

    return result


def print_result(result: dict):
    """Вывести результат валидации"""
    print("\n" + "=" * 50)
    print(f"WEBHOOK SIGNATURE VALIDATION ({result['service'].upper()})")
    print("=" * 50)

    if result["valid"]:
        print("\n VALID - Signature is correct\n")
    else:
        print(f"\n INVALID - {result['error']}\n")

    if result["details"]:
        print("Details:")
        for key, value in result["details"].items():
            print(f"  {key}: {value}")

    print("=" * 50)

    return result["valid"]


def main():
    parser = argparse.ArgumentParser(
        description="Validate webhook signatures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Stripe:
    %(prog)s --service stripe --payload '{"id":"evt_xxx"}' \\
             --signature "t=1234,v1=abc123" --secret "whsec_xxx"

  WhatsApp:
    %(prog)s --service whatsapp --payload '{"entry":[]}' \\
             --signature "sha256=abc123" --secret "app_secret"

  Generic HMAC-SHA256:
    %(prog)s --service generic --payload '{"data":"test"}' \\
             --signature "abc123" --secret "my_secret"

  From file:
    %(prog)s --service stripe --payload-file request.json \\
             --signature "t=1234,v1=abc123" --secret "whsec_xxx"
        """
    )

    parser.add_argument("--service", "-s", required=True,
                        choices=["stripe", "whatsapp", "github", "generic"],
                        help="Webhook service type")
    parser.add_argument("--payload", "-p", help="Request payload")
    parser.add_argument("--payload-file", "-f", help="Read payload from file")
    parser.add_argument("--signature", "-g", required=True,
                        help="Signature header value")
    parser.add_argument("--secret", "-k", required=True,
                        help="Webhook secret key")
    parser.add_argument("--tolerance", "-t", type=int, default=300,
                        help="Timestamp tolerance in seconds (Stripe only)")

    args = parser.parse_args()

    # Получить payload
    if args.payload_file:
        with open(args.payload_file, "r") as f:
            payload = f.read()
    elif args.payload:
        payload = args.payload
    else:
        print("Error: --payload or --payload-file is required")
        sys.exit(1)

    # Валидация
    if args.service == "stripe":
        result = validate_stripe_signature(
            payload, args.signature, args.secret, args.tolerance
        )
    elif args.service == "whatsapp":
        result = validate_whatsapp_signature(payload, args.signature, args.secret)
    elif args.service == "github":
        result = validate_github_signature(payload, args.signature, args.secret)
    else:
        result = validate_generic_hmac(payload, args.signature, args.secret)

    valid = print_result(result)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
