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

    def test_markup_after_bank_reserve_and_rounding(self):
        # NOTE: the 5% reserve here is caller-provided mechanics input, not an
        # endorsement of 5% on AED (R010/R011: 5% non-AED only). The tool applies
        # whatever percent it is given; the business decision stays with the caller.
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

    def test_rejects_non_finite_inputs_cleanly(self):
        for bad in ("inf", "-inf", "nan"):
            proc = self.run_cli(
                f"--base={bad}", "--source-per-usd", "3.65",
                "--markup-percent", "10",
                expected_code=2,
            )
            self.assertIn("invalid number", proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)

    def test_rounding_keeps_exact_multiple(self):
        proc = self.run_cli(
            "--base", "100", "--source-per-usd", "1",
            "--markup-percent", "50", "--round-up-usd", "5",
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["selling_price_usd_per_unit"], 150.0)
        self.assertAlmostEqual(data["actual_profit_percent"], 50.0, places=2)

    def test_conversion_divides_by_source_per_usd(self):
        proc = self.run_cli(
            "--base", "200", "--source-per-usd", "2",
            "--markup-percent", "100", "--round-up-usd", "1",
        )
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["full_cost_usd_per_unit"], 100.0, places=2)
        self.assertEqual(data["selling_price_usd_per_unit"], 200.0)
        self.assertAlmostEqual(data["profit_source_per_unit"], 200.0, places=2)

    def test_allow_combined_applies_markup_then_fixed_profit(self):
        proc = self.run_cli(
            "--base", "100", "--source-per-usd", "1",
            "--markup-percent", "10", "--fixed-profit-usd", "5",
            "--allow-combined", "--round-up-usd", "1",
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["selling_price_usd_per_unit"], 115.0)
        self.assertAlmostEqual(data["profit_usd_per_unit"], 15.0, places=2)

    def test_delivery_order_is_allocated_by_quantity(self):
        proc = self.run_cli(
            "--base", "100", "--source-per-usd", "1",
            "--delivery-order", "30", "--quantity", "3",
            "--markup-percent", "10", "--round-up-usd", "1",
        )
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["full_cost_source_per_unit"], 110.0, places=2)
        self.assertEqual(data["selling_price_usd_per_unit"], 121.0)

    def test_zero_base_reports_zero_actual_percent(self):
        proc = self.run_cli(
            "--base", "0", "--source-per-usd", "3.65",
            "--fixed-profit-usd", "10", "--round-up-usd", "1",
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["selling_price_usd_per_unit"], 10.0)
        self.assertEqual(data["actual_profit_percent"], 0.0)


if __name__ == "__main__":
    unittest.main()
