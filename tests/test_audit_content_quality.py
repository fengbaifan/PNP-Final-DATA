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
created: 2026-09-12
updated: 2026-09-12
evidence_status: source_backed
verification_level: L7
sources:
- citation: Test source
  location: test section
  sentence_summary: test summary
---

## 内容

### 描述

{description}

## 关系与证据

当前没有正式关系。
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

    def test_current_three_part_body_is_the_required_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unit = self.write_unit(root, "中英文描述均已保存。 English description is saved.")
            with patch.object(audit_content_quality, "BASE", root):
                findings = audit_content_quality.check_missing_sections([unit])

        self.assertEqual(findings, [])

    def test_optional_empty_fields_and_descriptive_heading_are_not_defects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unit = self.write_unit(root, "中英文描述。 English description.")
            text = unit.read_text(encoding="utf-8")
            text = text.replace("sub_type: test", "sub_type:").replace("tags:\n- 测试", "tags: []")
            text = text.replace("## 关系与证据", "### 本章相关内容\n\n正文。\n\n## 关系与证据")
            unit.write_text(text, encoding="utf-8")
            with patch.object(audit_content_quality, "BASE", root):
                results = audit_content_quality.run_all_checks([unit])

        self.assertEqual(results["empty_frontmatter_values"], [])
        self.assertEqual(results["placeholder_content"], [])


if __name__ == "__main__":
    unittest.main()
