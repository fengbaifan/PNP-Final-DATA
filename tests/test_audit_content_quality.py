import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import audit_content_quality


UNIT_TEMPLATE = """---
title: 测试对象（Test Object）
name_en: Test Object
type: term
sub_type: test
tags:
- 测试
evidence_status: source_backed
verification_level: L7
---

## 描述

{description}

## 验证状态

- **证据状态**: source_backed
- **验证层级**: L7
"""


class DeterministicContentIntegrityTests(unittest.TestCase):
    def write_unit(self, root: Path, description: str) -> Path:
        path = root / "04-knowledge" / "units" / "terms" / "test-object.md"
        path.parent.mkdir(parents=True)
        path.write_text(UNIT_TEMPLATE.format(description=description), encoding="utf-8")
        return path

    def test_year_without_dashes_is_not_treated_as_low_semantic_density(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unit = self.write_unit(
                root,
                "该对象于2011年形成，并由来源给出明确名称、媒介和用途。",
            )
            with (
                patch.object(audit_content_quality, "BASE", root),
                patch.object(audit_content_quality, "iter_units", return_value=[unit]),
            ):
                results = audit_content_quality.run_all_checks([unit])
                summary = audit_content_quality.get_content_quality_summary()

        self.assertNotIn("body_quality_issues", results)
        self.assertNotIn("body_quality_issues", summary)
        self.assertEqual(summary["total_findings"], 0)
        self.assertIn("不评估语义细节密度", summary["metric_boundary"])

    def test_deterministic_placeholder_signal_remains_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unit = self.write_unit(root, "待补充")
            with patch.object(audit_content_quality, "BASE", root):
                results = audit_content_quality.run_all_checks([unit])

        self.assertEqual(len(results["placeholder_content"]), 1)


if __name__ == "__main__":
    unittest.main()
