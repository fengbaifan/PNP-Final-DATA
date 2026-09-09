import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import build_output_gallery


def record() -> dict:
    return {
        "output_id": "example",
        "output_type": "research_memo",
        "artifact_patterns": ["05-outputs/drafts/example.md"],
        "used_units": [],
        "used_claims": [],
        "used_relations": [],
        "source_refs": [],
        "uncertain_points": ["Needs review"],
        "candidate_refs": [],
        "file_back_status": "candidates_deferred",
    }


class BuildOutputGalleryTests(unittest.TestCase):
    def make_root(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "05-outputs" / "drafts").mkdir(parents=True)
        (root / "05-outputs" / "index").mkdir(parents=True)
        (root / "05-outputs" / "drafts" / "example.md").write_text("# Example\n", encoding="utf-8")
        (root / "05-outputs" / "output-registry.yml").write_text(
            yaml.safe_dump({"version": "1.0", "records": [record()]}, sort_keys=False),
            encoding="utf-8",
        )
        records = build_output_gallery.load_records(root)
        (root / "05-outputs" / "index" / "output-gallery.md").write_text(
            build_output_gallery.render_gallery(records, root), encoding="utf-8"
        )
        return root

    def test_valid_registry_covers_output_and_gallery(self):
        root = self.make_root()

        findings = build_output_gallery.validate_output_metadata(root)

        self.assertEqual(findings, [])

    def test_unregistered_output_is_reported(self):
        root = self.make_root()
        (root / "05-outputs" / "drafts" / "unregistered.md").write_text("# Missing\n", encoding="utf-8")

        findings = build_output_gallery.validate_output_metadata(root)

        self.assertIn("output_artifact_unregistered", {item["issue"] for item in findings})

    def test_navigation_snapshot_uses_current_health_values(self):
        template = (
            "| 知识元总数 | **1**（以 `current-health.json` 当前快照为准） | — |\n"
            "| claim 数 | **2** | — |\n"
            "| relation 数 | **3** | — |\n"
            "| structural_health | **4/130** | ≥ 120/130 |\n"
            "| traceability | **5/15** | 15/15 |\n"
        )
        health = {
            "summary": {"total_units": 1637},
            "claim_traceability": {"total_claims": 280},
            "relation_health": {"relation_index_total": 2865},
            "structural_health": {"total": 130, "traceability": 15},
        }

        rendered = build_output_gallery.render_navigation_snapshot(template, health)

        self.assertIn("| 知识元总数 | **1637**", rendered)
        self.assertIn("| relation 数 | **2865** |", rendered)
        self.assertIn("| structural_health | **130/130** |", rendered)
