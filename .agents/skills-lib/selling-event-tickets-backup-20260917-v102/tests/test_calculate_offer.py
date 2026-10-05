import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "calculate_offer.py"


class CalculateOfferTests(unittest.TestCase):
    def run_cli(self, *args, expected_code=0):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--json"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, expected_code, proc.stderr)
        return proc

    def test_aed_markup_after_bank_reserve_and_rounding(self):
        proc = self.run_cli(
            "--base", "1100", "--source-per-usd", "3.65",
            "--bank-reserve-percent", "5", "--markup-percent", "60",
            "--round-up-usd", "5", "--quantity", "2",
        )
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["full_cost_source_per_unit"], 1155.0, places=2)
        self.assertEqual(data["selling_price_usd_per_unit"], 510.0)
        self.assertAlmostEqual(data["profit_usd_per_unit"], 193.56, places=2)
        self.assertAlmostEqual(data["profit_usd_order"], 387.12, places=2)

    def test_order_fee_is_allocated_by_quantity(self):
        proc = self.run_cli(
            "--base", "100", "--source-per-usd", "1",
            "--confirmed-fee", "10", "--order-fee", "20",
            "--quantity", "2", "--markup-percent", "50",
            "--round-up-usd", "1",
        )
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["full_cost_source_per_unit"], 120.0, places=2)
        self.assertEqual(data["selling_price_usd_per_unit"], 180.0)

    def test_fixed_profit_is_added_after_full_cost(self):
        proc = self.run_cli(
            "--base", "365", "--source-per-usd", "3.65",
            "--confirmed-fee", "36.5", "--fixed-profit-usd", "150",
            "--round-up-usd", "5",
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["selling_price_usd_per_unit"], 260.0)
        self.assertAlmostEqual(data["profit_usd_per_unit"], 150.0, places=2)

    def test_combining_markup_and_fixed_profit_requires_explicit_permission(self):
        proc = self.run_cli(
            "--base", "100", "--source-per-usd", "1",
            "--markup-percent", "35", "--fixed-profit-usd", "50",
            expected_code=2,
        )
        self.assertIn("--allow-combined", proc.stderr)


if __name__ == "__main__":
    unittest.main()
