import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.audit_repo import translation_index_integrity_check


def write_unit(root: Path, unit_type: str, slug: str) -> None:
    path = root / "04-knowledge" / "units" / unit_type / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\ntitle: Example\n---\n", encoding="utf-8")


class TranslationIndexIntegrityTests(unittest.TestCase):
    def test_reports_missing_stale_duplicate_and_declared_total_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_unit(root, "persons", "expected")
            index = root / "04-knowledge" / "quality" / "translation-index.yml"
            index.parent.mkdir(parents=True)
            index.write_text(
                yaml.safe_dump(
                    {
                        "generated": "2026-06-02",
                        "total": 99,
                        "index": [
                            {"slug": "persons/stale"},
                            {"slug": "persons/stale"},
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = translation_index_integrity_check(root)

        self.assertEqual(result["expected"], 1)
        self.assertEqual(result["indexed"], 2)
        self.assertEqual(result["declared_total"], 99)
        self.assertEqual(result["missing"], ["persons/expected"])
        self.assertEqual(result["stale"], ["persons/stale"])
        self.assertEqual(result["duplicate"], ["persons/stale"])
        self.assertTrue(result["declared_total_mismatch"])


if __name__ == "__main__":
    unittest.main()

