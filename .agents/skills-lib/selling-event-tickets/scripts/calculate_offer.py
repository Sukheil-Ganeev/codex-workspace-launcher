#!/usr/bin/env python3
"""Calculate ticket full cost, selling price and profit without external dependencies."""

from __future__ import annotations

import argparse
import json
import math
import sys
from decimal import Decimal, ROUND_CEILING
from typing import Any

D = Decimal


def positive_decimal(value: str) -> Decimal:
    try:
        number = D(value)
    except Exception as exc:  # pragma: no cover - argparse formats the message
        raise argparse.ArgumentTypeError(f"invalid number: {value}") from exc
    if not number.is_finite():
        raise argparse.ArgumentTypeError(f"invalid number: {value}")
    if number < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return number


def strictly_positive_decimal(value: str) -> Decimal:
    number = positive_decimal(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return number


def ceil_to_step(value: Decimal, step: Decimal) -> Decimal:
    units = (value / step).to_integral_value(rounding=ROUND_CEILING)
    return units * step


def q2(value: Decimal) -> float:
    return float(value.quantize(D("0.01")))


def calculate(args: argparse.Namespace) -> dict[str, Any]:
    if args.markup_percent is None and args.fixed_profit_usd is None:
        raise ValueError("provide --markup-percent or --fixed-profit-usd")
    if (
        args.markup_percent is not None
        and args.fixed_profit_usd is not None
        and not args.allow_combined
    ):
        raise ValueError(
            "markup and fixed profit cannot be combined unless --allow-combined is set"
        )

    quantity = D(args.quantity)
    allocated_order_fee = args.order_fee / quantity
    allocated_delivery = args.delivery_order / quantity

    confirmed_subtotal = (
        args.base
        + args.confirmed_fee
        + allocated_order_fee
        + args.tax_amount
        + allocated_delivery
        + args.payment_cost
    )
    reserve = confirmed_subtotal * args.bank_reserve_percent / D("100")
    full_cost_source = confirmed_subtotal + reserve
    full_cost_usd = full_cost_source / args.source_per_usd

    sale_usd = full_cost_usd
    if args.markup_percent is not None:
        sale_usd *= D("1") + args.markup_percent / D("100")
    if args.fixed_profit_usd is not None:
        sale_usd += args.fixed_profit_usd

    rounded_sale_usd = ceil_to_step(sale_usd, args.round_up_usd)
    profit_usd = rounded_sale_usd - full_cost_usd
    profit_source = profit_usd * args.source_per_usd
    actual_percent = D("0") if full_cost_usd == 0 else profit_usd / full_cost_usd * D("100")

    result = {
        "quantity": args.quantity,
        "source_currency": args.source_currency,
        "source_per_usd": q2(args.source_per_usd),
        "base_source_per_unit": q2(args.base),
        "confirmed_fee_source_per_unit": q2(args.confirmed_fee),
        "order_fee_source_total": q2(args.order_fee),
        "allocated_order_fee_source_per_unit": q2(allocated_order_fee),
        "tax_source_per_unit": q2(args.tax_amount),
        "delivery_source_total": q2(args.delivery_order),
        "allocated_delivery_source_per_unit": q2(allocated_delivery),
        "payment_cost_source_per_unit": q2(args.payment_cost),
        "bank_reserve_percent": q2(args.bank_reserve_percent),
        "bank_reserve_source_per_unit": q2(reserve),
        "full_cost_source_per_unit": q2(full_cost_source),
        "full_cost_usd_per_unit": q2(full_cost_usd),
        "markup_percent": None if args.markup_percent is None else q2(args.markup_percent),
        "fixed_profit_usd": None if args.fixed_profit_usd is None else q2(args.fixed_profit_usd),
        "selling_price_usd_per_unit": q2(rounded_sale_usd),
        "selling_price_usd_order": q2(rounded_sale_usd * quantity),
        "profit_usd_per_unit": q2(profit_usd),
        "profit_source_per_unit": q2(profit_source),
        "profit_usd_order": q2(profit_usd * quantity),
        "actual_profit_percent": q2(actual_percent),
    }
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Calculate ticket FULL COST and selling price. All cost inputs are in the source currency."
    )
    p.add_argument("--base", type=positive_decimal, required=True, help="base price per unit")
    p.add_argument(
        "--source-per-usd",
        type=strictly_positive_decimal,
        required=True,
        help="units of source currency equal to 1 USD, e.g. 3.65 for AED",
    )
    p.add_argument("--source-currency", default="AED")
    p.add_argument("--confirmed-fee", type=positive_decimal, default=D("0"), help="confirmed fee per unit")
    p.add_argument("--order-fee", type=positive_decimal, default=D("0"), help="confirmed fee for the whole order")
    p.add_argument("--tax-amount", type=positive_decimal, default=D("0"), help="confirmed tax amount per unit; do not guess a rate")
    p.add_argument("--delivery-order", type=positive_decimal, default=D("0"), help="delivery/transfer cost for the whole order")
    p.add_argument("--payment-cost", type=positive_decimal, default=D("0"), help="confirmed payment cost per unit")
    p.add_argument("--bank-reserve-percent", type=positive_decimal, default=D("0"), help="internal reserve percentage; caller sets it per R010/R011 (5%% non-AED only, AED none automatic)")
    p.add_argument("--markup-percent", type=positive_decimal)
    p.add_argument("--fixed-profit-usd", type=positive_decimal)
    p.add_argument("--allow-combined", action="store_true", help="explicitly allow both markup and fixed profit")
    p.add_argument("--round-up-usd", type=strictly_positive_decimal, default=D("5"))
    p.add_argument("--quantity", type=int, default=1)
    p.add_argument("--json", action="store_true")
    return p


def main() -> int:
    p = parser()
    args = p.parse_args()
    if args.quantity <= 0:
        p.error("--quantity must be greater than zero")
    try:
        result = calculate(args)
    except ValueError as exc:
        p.error(str(exc))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    rows = [
        ("Full cost / unit", f"{result['full_cost_source_per_unit']:.2f} {result['source_currency']} / ${result['full_cost_usd_per_unit']:.2f}"),
        ("Selling price / unit", f"${result['selling_price_usd_per_unit']:.2f}"),
        ("Selling price / order", f"${result['selling_price_usd_order']:.2f}"),
        ("Profit / unit", f"${result['profit_usd_per_unit']:.2f} / {result['profit_source_per_unit']:.2f} {result['source_currency']}"),
        ("Profit / order", f"${result['profit_usd_order']:.2f}"),
        ("Actual profit %", f"{result['actual_profit_percent']:.2f}%"),
    ]
    width = max(len(k) for k, _ in rows)
    for key, value in rows:
        print(f"{key:<{width}} : {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
