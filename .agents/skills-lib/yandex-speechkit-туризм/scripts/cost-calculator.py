#!/usr/bin/env python3
"""Cost Calculator for Yandex SpeechKit"""
import argparse, sys
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    print("ERROR: pip install rich")
    sys.exit(1)

console = Console()

YANDEX_PRICING = {
    "sync_api": {"price_per_15_sec": 0.12},
    "async_api": {"price_per_15_sec": 0.12},
    "streaming_api": {"price_per_15_sec": 0.24}
}

COMPETITOR_PRICING = {
    "openai_whisper": {"price_per_minute": 0.006},
    "google_speech": {"price_per_15_sec": 0.006, "free_tier_minutes": 60},
    "aws_transcribe": {"price_per_second": 0.0004}
}

USD_TO_RUB = 95.0

@dataclass
class CostEstimate:
    service: str
    api_type: Optional[str]
    duration_sec: float
    units: float
    price_rub: float
    price_usd: float

class CostCalculator:
    def __init__(self, usd_rate: float = USD_TO_RUB):
        self.usd_rate = usd_rate

    def calculate_yandex_cost(self, duration_sec: float, api_type: str = "sync") -> CostEstimate:
        pricing = YANDEX_PRICING[f"{api_type}_api"]
        units = int(duration_sec / 15) + (1 if duration_sec % 15 != 0 else 0)
        price_rub = units * pricing["price_per_15_sec"]
        return CostEstimate("Yandex SpeechKit", api_type.upper(), duration_sec, units, price_rub, price_rub / self.usd_rate)

    def calculate_whisper_cost(self, duration_sec: float) -> CostEstimate:
        duration_min = duration_sec / 60
        price_usd = duration_min * COMPETITOR_PRICING["openai_whisper"]["price_per_minute"]
        return CostEstimate("OpenAI Whisper", None, duration_sec, duration_min, price_usd * self.usd_rate, price_usd)

    def calculate_google_cost(self, duration_sec: float, free_tier: bool = False) -> CostEstimate:
        units = int(duration_sec / 15) + (1 if duration_sec % 15 != 0 else 0)
        if free_tier:
            units = max(0, units - COMPETITOR_PRICING["google_speech"]["free_tier_minutes"] * 4)
        price_usd = units * COMPETITOR_PRICING["google_speech"]["price_per_15_sec"]
        return CostEstimate("Google Speech-to-Text", None, duration_sec, units, price_usd * self.usd_rate, price_usd)

    def calculate_aws_cost(self, duration_sec: float) -> CostEstimate:
        price_usd = duration_sec * COMPETITOR_PRICING["aws_transcribe"]["price_per_second"]
        return CostEstimate("AWS Transcribe", None, duration_sec, duration_sec, price_usd * self.usd_rate, price_usd)

    def calculate_all(self, duration_sec: float) -> List[CostEstimate]:
        return [
            self.calculate_yandex_cost(duration_sec, "sync"),
            self.calculate_yandex_cost(duration_sec, "async"),
            self.calculate_yandex_cost(duration_sec, "streaming"),
            self.calculate_whisper_cost(duration_sec),
            self.calculate_google_cost(duration_sec, True),
            self.calculate_aws_cost(duration_sec)
        ]

def main():
    parser = argparse.ArgumentParser(description="Calculate Yandex SpeechKit costs")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--duration", "-d", type=float, help="Duration in seconds")
    input_group.add_argument("--file", "-f", type=Path, help="Audio file")
    parser.add_argument("--yandex-only", action="store_true")
    parser.add_argument("--usd-rate", type=float, default=USD_TO_RUB)
    args = parser.parse_args()

    if args.file:
        try:
            from pydub import AudioSegment
            duration_sec = len(AudioSegment.from_file(str(args.file))) / 1000.0
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    else:
        duration_sec = args.duration

    calculator = CostCalculator(args.usd_rate)
    estimates = ([calculator.calculate_yandex_cost(duration_sec, t) for t in ["sync", "async", "streaming"]] 
                 if args.yandex_only else calculator.calculate_all(duration_sec))

    table = Table(title="Cost Comparison")
    table.add_column("Service", style="cyan")
    table.add_column("API", style="yellow")
    table.add_column("RUB", justify="right", style="green")
    table.add_column("USD", justify="right", style="blue")

    for est in sorted(estimates, key=lambda x: x.price_rub):
        table.add_row(est.service, est.api_type or "-", f"{est.price_rub:.2f}", f"${est.price_usd:.4f}")

    console.print(table)

if __name__ == "__main__":
    main()
