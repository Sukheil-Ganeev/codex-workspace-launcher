import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_partner_message.py"


class PartnerMessageValidatorTests(unittest.TestCase):
    def validate(self, text, *args):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as f:
            f.write(text)
            path = f.name
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), path, "--json", *args],
            text=True,
            capture_output=True,
        )
        return proc, json.loads(proc.stdout)

    def test_clean_offer_passes(self):
        text = """Хамра, добрый день!\n\nПо вашему запросу можем предложить билеты на *EVENT*.\n*Дата:* 1 октября 2026\n*Место проведения:* Venue\n*Стоимость:* *500 USD за билет*\n\n*Возрастные ограничения:* гости младше 16 лет — со взрослым.\nНаличие и окончательную стоимость необходимо повторно подтвердить перед оплатой.\n"""
        proc, data = self.validate(text)
        self.assertEqual(proc.returncode, 0, data)
        self.assertTrue(data["passed"])

    def test_internal_data_and_double_bold_fail(self):
        text = """**EVENT**\nЗакупочная стоимость: 100 AED\nНаша прибыль: 40%\nhttps://example.com/buy\n"""
        proc, data = self.validate(text)
        self.assertNotEqual(proc.returncode, 0)
        codes = {item["code"] for item in data["errors"]}
        self.assertIn("DOUBLE_ASTERISK", codes)
        self.assertIn("INTERNAL_DATA", codes)
        self.assertIn("DIRECT_URL", codes)

    def test_offer_requires_age_and_reconfirmation(self):
        text = """Добрый день!\n*Стоимость:* *500 USD за билет*\n"""
        proc, data = self.validate(text)
        self.assertNotEqual(proc.returncode, 0)
        codes = {item["code"] for item in data["errors"]}
        self.assertIn("AGE_RULE_MISSING", codes)
        self.assertIn("RECONFIRMATION_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
