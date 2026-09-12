import json
import tempfile
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

from scripts import audit_relation_consistency as relation_audit
from scripts import hierarchy_stress_test
from scripts.audit_repo import translation_coverage_gap_count, translation_health_check
from scripts.generate_governance_backlog import gen_p1


def write_work_with_triple_dash_url(root: Path) -> None:
    path = root / "04-knowledge" / "units" / "works" / "example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "---\n"
        "title: Example\n"
        "sources:\n"
        "  - url: https://example.test/item---record\n"
        "title_original: Example\n"
        "title_original_language: en\n"
        "title_zh: 示例\n"
        "---\n"
        "body\n",
        encoding="utf-8",
    )


def test_translation_health_ignores_triple_dash_inside_url():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_work_with_triple_dash_url(root)

        health = translation_health_check(root)

    assert health["works"]["coverage"]["title_original"] == "1/1"


def test_legacy_translation_coverage_remains_diagnostic_without_creating_backlog():
    translation = {"works": {"coverage": {"title_original": "1/2"}}}
    assert translation_coverage_gap_count(translation) == 1

    items = gen_p1({"translation_health": translation})
    assert not any(item["id"] == "P1-TRANSLATION-WORKS-TITLE_ORIGINAL" for item in items)


def test_isolated_total_is_not_limited_to_preview_size():
    units = {f"terms/u-{index}.md" for index in range(125)}
    isolated = relation_audit.collect_isolated_units(units, defaultdict(int))
    assert len(isolated) == 125
    assert len(isolated[:100]) == 100


def test_hierarchy_stress_uses_live_version_and_excludes_readme_theme():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        hierarchy = root / "hierarchy"
        themes = root / "themes"
        hierarchy.mkdir()
        themes.mkdir()
        (hierarchy / "index.md").write_text("---\ntitle: 层级知识体系 v6.1\n---\n", encoding="utf-8")
        (themes / "README.md").write_text("navigation", encoding="utf-8")
        (themes / "real-theme.md").write_text(
            "---\nnode_type: theme\ntheme_code: A.1\nprimary_dimension: A\n---\n",
            encoding="utf-8",
        )

        with patch.object(hierarchy_stress_test, "HIERARCHY", hierarchy), patch.object(
            hierarchy_stress_test, "THEMES", themes
        ):
            version = hierarchy_stress_test.hierarchy_version()
            coverage = hierarchy_stress_test.count_theme_coverage()

    assert version == "v6.1"
    assert set(coverage) == {"real-theme"}


def test_hierarchy_backfill_queue_is_explicit_and_non_applying():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        units = root / "units"
        unit = units / "terms" / "example.md"
        unit.parent.mkdir(parents=True)
        unit.write_text("---\ntitle: Example\nprimary_domain: history\n---\n", encoding="utf-8")
        output = root / "queue.jsonl"

        count = hierarchy_stress_test.write_hierarchy_backfill_queue(output, units)
        record = json.loads(output.read_text(encoding="utf-8"))

    assert count == 1
    assert record["missing_fields"] == ["primary_dimension", "primary_theme", "topic_memberships"]
    assert record["status"] == "needs_semantic_hierarchy_assignment"
    assert record["apply_permitted"] is False
