import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReferenceCoverageTests(unittest.TestCase):
    def test_rule_registry_has_70_rules(self):
        text = (ROOT / "references" / "rule-registry.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^## R\d{3}\b", text, re.M)), 70)

    def test_all_ten_chat_extractions_are_present(self):
        files = sorted((ROOT / "references" / "source-evidence" / "chat-extractions").glob("chat-*.md"))
        self.assertEqual(len(files), 10)

    def test_event_playbooks_are_present(self):
        files = sorted((ROOT / "references" / "event-playbooks").glob("*.md"))
        self.assertGreaterEqual(len(files), 10)

    def test_skill_relative_links_resolve(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        local_links = [link for link in links if not re.match(r"^[a-z]+://", link)]
        self.assertTrue(local_links)
        for link in local_links:
            target = (ROOT / link).resolve()
            self.assertTrue(target.exists(), f"broken link: {link}")

    def test_source_integrity_record_exists_and_matches(self):
        record_path = ROOT / "references" / "source-evidence" / "source-integrity.json"
        self.assertTrue(record_path.is_file())
        record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertRegex(record["sha256"], r"^[0-9a-f]{64}$")
        archive = ROOT.parents[1] / "source" / record["archive_name"]
        if archive.is_file():
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(digest, record["sha256"])


if __name__ == "__main__":
    unittest.main()
