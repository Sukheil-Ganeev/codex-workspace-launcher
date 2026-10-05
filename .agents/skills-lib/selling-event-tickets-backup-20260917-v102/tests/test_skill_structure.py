import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "SKILL.md",
            "README.md",
            "references/core-context.md",
            "references/rule-registry.md",
            "references/source-freshness.md",
            "templates/partner-offer-ru.txt",
            "templates/internal-calculation.md",
            "scripts/calculate_offer.py",
            "scripts/validate_partner_message.py",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_frontmatter_is_discoverable(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        name = re.search(r"^name:\s*(.+)$", frontmatter, re.M).group(1).strip()
        description = re.search(r"^description:\s*(.+)$", frontmatter, re.M).group(1).strip()
        self.assertRegex(name, r"^[a-z0-9-]+$")
        self.assertTrue(description.startswith("Use when"))
        self.assertLess(len(frontmatter), 1024)

    def test_skill_contains_core_safety_contract(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in [
            "full cost",
            "real-name",
            "partner txt",
            "official platinum",
            "reconfirm",
            "local pricing rule",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
