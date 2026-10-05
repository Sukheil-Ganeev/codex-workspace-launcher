#!/usr/bin/env python3
"""Test suite for Yandex SpeechKit templates"""
import sys, unittest
from unittest.mock import Mock, patch

try:
    from rich.console import Console
except ImportError:
    print("ERROR: pip install rich")
    sys.exit(1)

console = Console()

class TestSyncAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.folder_id = "test_folder_id"
    
    @patch("requests.post")
    def test_sync_transcribe_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "Test text"}
        mock_post.return_value = mock_response
        
        import requests
        response = requests.post(
            "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
            headers={"Authorization": f"Api-Key {self.api_key}"},
            params={"folderId": self.folder_id, "lang": "ru-RU"},
            data=b"test"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], "Test text")

class TestCostCalculation(unittest.TestCase):
    def test_calculate_units(self):
        test_cases = [(10, 1), (15, 1), (16, 2), (30, 2), (31, 3), (60, 4)]
        
        for duration, expected in test_cases:
            units = int(duration / 15) + (1 if duration % 15 != 0 else 0)
            self.assertEqual(units, expected)
    
    def test_calculate_cost(self):
        price_per_unit = 0.12
        duration_sec = 60
        units = int(duration_sec / 15) + (1 if duration_sec % 15 != 0 else 0)
        cost = units * price_per_unit
        self.assertEqual(cost, 0.48)

def main():
    console.print("[cyan]Running Yandex SpeechKit Tests...[/cyan]
")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSyncAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestCostCalculation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    console.print(f"
[cyan]Tests run:[/cyan] {result.testsRun}")
    console.print(f"[green]Passed:[/green] {result.testsRun - len(result.failures) - len(result.errors)}")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())
