import tempfile
import json
import unittest
from pathlib import Path

from scripts import build_enrich_inventory as inventory


class BuildEnrichInventoryTests(unittest.TestCase):
    def test_mechanical_priority_does_not_claim_semantic_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            units = Path(tmp) / "units"
            for dirname in inventory.UNIT_DIRS:
                (units / dirname).mkdir(parents=True)
            self.write_unit(units / "terms" / "thin.md", "short", 1, "partially_verified")
            self.write_unit(units / "works" / "rich.md", "long body " * 100, 2, "externally_verified", "https://en.wikipedia.org/wiki/Test")

            rows = inventory.build_inventory(units)

        self.assertEqual(rows[0]["unit"], "terms/thin.md")
        self.assertEqual(rows[0]["enrich_status"], "pending_semantic_review")
        self.assertNotIn("enriched", rows[0])
        self.assertNotIn("verification_level", rows[0])

    def test_reviewed_triage_changes_status_without_inventing_a_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = root / "units"
            for dirname in inventory.UNIT_DIRS:
                (units / dirname).mkdir(parents=True)
            self.write_unit(units / "terms" / "example.md", "short", 1, "source_backed")
            triage = root / "enrich_triage.jsonl"
            triage.write_text(
                json.dumps({"unit": "terms/example.md", "enrich_status": "no_external_source_found"}) + "\n",
                encoding="utf-8",
            )
            rows = inventory.build_inventory(units)
            inventory.apply_reviewed_triage(rows, [triage])

        self.assertEqual(rows[0]["enrich_status"], "no_external_source_found")
        self.assertEqual(rows[0]["enrich_decision_source"], triage.as_posix())

    @staticmethod
    def write_unit(path: Path, body: str, source_count: int, evidence_status: str, link: str = "") -> None:
        path.write_text(
            "---\n"
            f"title: Example\nname_en: Example\ntype: {path.parent.name.removesuffix('s')}\n"
            f"source_count: {source_count}\nevidence_status: {evidence_status}\nconfidence: medium\n"
            "---\n"
            f"## 描述\n{body}\n{link}\n## 参考文献\n1. Example\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
