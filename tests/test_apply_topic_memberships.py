import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts import apply_topic_memberships


class ApplyTopicMembershipsTests(unittest.TestCase):
    DEFAULT_SCOPE_NOTE = "Topic 文件显式材料链接经本批逐对象语义复读确认；层级挂载不改变置信度、共识或验证状态。"

    def make_fixture(self, root: Path, *, existing_hierarchy: bool = False) -> Path:
        topics = root / "04-knowledge" / "structure" / "topics"
        units = root / "04-knowledge" / "units" / "terms"
        topics.mkdir(parents=True)
        units.mkdir(parents=True)
        hierarchy = "primary_theme: B.2\n" if existing_hierarchy else ""
        unit = units / "example.md"
        unit.write_text(
            "---\n"
            "title: Example\n"
            "type: term\n"
            f"{hierarchy}"
            "updated: 2026-08-01\n"
            "version: 2\n"
            "---\n"
            "\nExample body.\n",
            encoding="utf-8",
        )
        topic = topics / "example-topic.md"
        topic.write_text(
            "---\n"
            "title: Example Topic\n"
            "node_type: topic\n"
            "primary_domain: example-domain\n"
            "primary_dimension: B\n"
            "parent_theme: B.4\n"
            "secondary_themes: []\n"
            "---\n"
            "\n## 材料\n"
            "\n- [Example](../../units/terms/example.md)\n",
            encoding="utf-8",
        )
        plan = {
            "schema_version": "topic-membership-plan-v1",
            "base_commit": "a" * 40,
            "reviewed_by": "test-agent",
            "reviewed_at": "2026-08-03",
            "topics": [
                {
                    "topic": "example-topic.md",
                    "sha256": hashlib.sha256(topic.read_bytes()).hexdigest().upper(),
                    "approve_explicit_links": True,
                    "role_overrides": {"terms/example.md": "historical_context"},
                }
            ],
            "hierarchy_overrides": {
                "terms/example.md": {
                    "primary_theme": "B.2",
                    "extra_secondary_themes": ["B.4"],
                    "role_in_theme": "term_anchor",
                }
            },
        }
        plan_path = root / "plan.yml"
        plan_path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return plan_path

    def add_complete_hierarchy(self, root: Path, *, same_topic: bool) -> None:
        unit = root / "04-knowledge" / "units" / "terms" / "example.md"
        topic = "topics/example-topic.md" if same_topic else "topics/old-topic.md"
        role = "historical_context" if same_topic else "term_anchor"
        secondary_themes = "[B.4]" if same_topic else "[]"
        text = unit.read_text(encoding="utf-8")
        block = (
            "primary_domain: example-domain\n"
            "secondary_domains: []\n"
            "primary_dimension: B\n"
            "secondary_dimensions: []\n"
            "primary_theme: B.2\n"
            f"secondary_themes: {secondary_themes}\n"
            "role_in_theme: term_anchor\n"
            "topic_memberships:\n"
            f"  - topic: {topic}\n"
            f"    role: {role}\n"
            "    primary: true\n"
            f'hierarchy_scope_note: "{self.DEFAULT_SCOPE_NOTE}"\n'
        )
        unit.write_text(text.replace("type: term\n", "type: term\n" + block), encoding="utf-8")

    def enable_merge(self, plan_path: Path) -> None:
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
        plan["existing_hierarchy_policy"] = "merge"
        plan_path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")

    def build(self, plan_path: Path):
        with mock.patch.object(apply_topic_memberships, "current_head", return_value="a" * 40), mock.patch.object(
            apply_topic_memberships, "dirty_targets", return_value=[]
        ):
            return apply_topic_memberships.build_changes(plan_path, plan_path.parent)

    def test_expands_only_reviewed_explicit_link_and_preserves_primary_theme_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root)
            changes, result = self.build(plan_path)

        self.assertEqual(result["units_planned"], 1)
        self.assertEqual(result["memberships_approved"], 1)
        after = changes[0].after
        self.assertIn("primary_theme: B.2", after)
        self.assertIn("secondary_themes: [B.4]", after)
        self.assertIn("topic: topics/example-topic.md", after)
        self.assertIn("role: historical_context", after)
        self.assertIn("primary: true", after)
        self.assertIn("updated: 2026-08-03", after)
        self.assertIn("version: 3", after)

    def test_exclusion_requires_reason_and_produces_no_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root)
            plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
            plan["topics"][0]["role_overrides"] = {}
            plan["topics"][0]["exclude"] = {"terms/example.md": "语义边界不成立"}
            plan["hierarchy_overrides"] = {}
            plan_path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
            changes, result = self.build(plan_path)

        self.assertEqual(changes, [])
        self.assertEqual(result["memberships_rejected"], 1)
        self.assertEqual(result["rejected"][0]["reason"], "语义边界不成立")

    def test_refuses_to_overwrite_existing_hierarchy_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root, existing_hierarchy=True)
            with self.assertRaisesRegex(apply_topic_memberships.PlanError, "已有层级字段"):
                self.build(plan_path)

    def test_merge_preserves_existing_primary_and_adds_reviewed_membership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root)
            self.add_complete_hierarchy(root, same_topic=False)
            self.enable_merge(plan_path)
            changes, result = self.build(plan_path)

        self.assertEqual(result["units_planned"], 1)
        self.assertEqual(result["memberships_added"], 1)
        after = changes[0].after
        self.assertIn("topic: topics/old-topic.md\n    role: term_anchor\n    primary: true", after)
        self.assertIn("topic: topics/example-topic.md\n    role: historical_context\n    primary: false", after)
        self.assertIn("secondary_themes: [B.4]", after)
        self.assertIn("version: 3", after)

    def test_merge_skips_semantically_identical_hierarchy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root)
            self.add_complete_hierarchy(root, same_topic=True)
            self.enable_merge(plan_path)
            changes, result = self.build(plan_path)

        self.assertEqual(changes, [])
        self.assertEqual(result["memberships_added"], 0)
        self.assertEqual(result["memberships_updated"], 0)
        self.assertEqual(result["units_no_delta"], 1)

    def test_merge_completes_valid_theme_only_hierarchy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root)
            unit = root / "04-knowledge" / "units" / "terms" / "example.md"
            text = unit.read_text(encoding="utf-8")
            core = (
                "primary_domain: example-domain\n"
                "primary_dimension: B\n"
                "primary_theme: B.2\n"
                "secondary_themes: []\n"
                "role_in_theme: term_anchor\n"
            )
            unit.write_text(text.replace("type: term\n", "type: term\n" + core), encoding="utf-8")
            self.enable_merge(plan_path)
            changes, result = self.build(plan_path)

        self.assertEqual(result["units_planned"], 1)
        self.assertEqual(result["memberships_added"], 1)
        self.assertIn("topic: topics/example-topic.md", changes[0].after)
        self.assertIn("secondary_themes: [B.4]", changes[0].after)

    def test_refuses_topic_hash_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = self.make_fixture(root)
            topic = root / "04-knowledge" / "structure" / "topics" / "example-topic.md"
            topic.write_text(topic.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
            with self.assertRaisesRegex(apply_topic_memberships.PlanError, "Topic 哈希漂移"):
                self.build(plan_path)


if __name__ == "__main__":
    unittest.main()
