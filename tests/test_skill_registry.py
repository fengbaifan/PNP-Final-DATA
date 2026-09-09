import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import skill_registry


class SkillRegistryTests(unittest.TestCase):
    def test_skill_frontmatter_names_are_unique_and_registry_is_valid(self):
        registry = skill_registry.build_registry()

        self.assertEqual(skill_registry.validate(registry), [])
        self.assertEqual(len(registry), 8)
        self.assertEqual(sum(entry["kind"] == "leaf" for entry in registry.values()), 8)
        self.assertEqual(sum(entry["kind"] == "router" for entry in registry.values()), 0)
        self.assertIn("inspector", registry)
        self.assertNotIn("system-review", registry)
        self.assertNotIn("inspection", registry)
        self.assertNotIn("review", registry)
        self.assertNotIn("sys-audit", registry)

    def test_registry_entries_are_derived_from_skill_contracts(self):
        registry = skill_registry.build_registry()

        self.assertEqual(registry["synthesize"]["path"], ".agents/skills/synthesize/SKILL.md")
        self.assertEqual(registry["synthesize"]["phase"], "later")
        self.assertNotIn("display_name", registry["synthesize"])
        self.assertNotIn("category", registry["synthesize"])
        self.assertIn("知识元对齐", registry["verify"]["triggers"])
        self.assertIn("页面展示", registry["compose"]["triggers"])
        self.assertNotIn("knowledge-graph", registry)
        self.assertEqual(registry["relate"]["phase"], "current")

    def test_external_skill_root_is_detected(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            active = root / ".agents" / "skills" / "ingest"
            active.mkdir(parents=True)
            (active / "SKILL.md").write_text("---\nname: ingest\n---\n", encoding="utf-8")
            legacy = root / ".legacy" / "old-skills" / "ingest"
            legacy.mkdir(parents=True)
            legacy_skill = legacy / "SKILL.md"
            legacy_skill.write_text("---\nname: ingest\n---\n", encoding="utf-8")

            self.assertEqual(skill_registry.external_skill_files(root), [legacy_skill])

    def test_legacy_stage_directory_fails_validation(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / ".agents" / "skills" / "01-intake" / "ingest"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: ingest\nkind: leaf\nphase: current\n"
                "triggers: [ingest]\ndescription: test\n---\n",
                encoding="utf-8",
            )
            issues = skill_registry.validate(skill_registry.build_registry(root), root)
            self.assertTrue(any("扁平规范路径" in issue for issue in issues))

    def test_unreferenced_reference_fails_validation(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / ".agents" / "skills" / "ingest"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: ingest\nkind: leaf\ntriggers: [ingest]\n"
                "description: test\n---\n",
                encoding="utf-8",
            )
            orphan = references / "orphan.md"
            orphan.write_text("# Orphan\n", encoding="utf-8")

            issues = skill_registry.validate(skill_registry.build_registry(root), root)

            self.assertIn(
                "未被任何 Skill 显式引用的 reference: "
                ".agents/skills/ingest/references/orphan.md",
                issues,
            )

    def test_duplicate_frontmatter_key_is_rejected(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "SKILL.md"
            path.write_text(
                "---\nname: example\nkind: leaf\ntriggers: [one]\ntriggers: [two]\n---\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate YAML key: triggers"):
                skill_registry._frontmatter(path)

    def test_nested_reference_must_be_declared_by_skill(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / ".agents" / "skills" / "ingest"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: ingest\nkind: leaf\ntriggers: [ingest]\ndescription: test\n---\n"
                "- `references/first.md`\n",
                encoding="utf-8",
            )
            (references / "first.md").write_text("See `second.md`.\n", encoding="utf-8")
            (references / "second.md").write_text("# Hidden\n", encoding="utf-8")

            registry = skill_registry.build_registry(root)
            issues = skill_registry.validate(registry, root)

            self.assertTrue(any("隐藏第二层必读规则" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
