import tempfile
import unittest
import csv
import io
from datetime import date
from pathlib import Path

import yaml
HDR = "relation_id,subject_ku_id,object_ku_id,predicate,direction,time,role,scope,origin,status,evidence_doc_id,evidence_source_file,evidence_span"

def rel_csv(rows):
    import io, csv as _csv
    out = io.StringIO()
    w = _csv.writer(out)
    w.writerow(HDR.split(","))
    for i, r in enumerate(rows, 1):
        src = r.get("source", "").replace(".md", "")
        tgt = r.get("target", "").replace(".md", "")
        if not src.startswith("units/"): src = "units/" + src
        if not tgt.startswith("units/"): tgt = "units/" + tgt
        w.writerow([f"rel-{i}", src, tgt, r.get("relation_type", ""), "forward", "", "", "", r.get("origin", "book"), "formal", "", "", ""])
    return out.getvalue()


from scripts import build_knowledge_graph_data


class BuildKnowledgeGraphDataTests(unittest.TestCase):
    def test_uses_current_taxonomy_and_authoritative_relation_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = root / "04-knowledge" / "units"
            quality = root / "04-knowledge" / "quality"
            (units / "terms").mkdir(parents=True)
            (units / "procedures").mkdir(parents=True)
            quality.mkdir(parents=True)
            (units / "terms" / "source.md").write_text(
                "---\ntitle: Source\nname_en: Source\ntype: term\nrelated: [../procedures/ignored.md]\n---\n## 定义\nSource description.\n",
                encoding="utf-8",
            )
            (units / "procedures" / "target.md").write_text(
                "---\ntitle: Target\nname_en: Target\ntype: procedure\n---\n",
                encoding="utf-8",
            )
            relation = {
                "source": "terms/source.md",
                "target": "procedures/target.md",
                "relation_type": "operationalizes",
                "relation_source": "explicit",
                "review_status": "evidence_backed_relation",
                "confidence": "high",
            }
            (root / "04-knowledge" / "tables" / "relations.csv").parent.mkdir(parents=True, exist_ok=True)
            (root / "04-knowledge" / "tables" / "relations.csv").write_text(
                rel_csv([relation]), encoding="utf-8"
            )

            data = build_knowledge_graph_data.build_graph(root)

        self.assertEqual(data["stats"]["total_nodes"], 2)
        self.assertEqual(data["stats"]["total_links"], 1)
        self.assertEqual(data["links"][0]["relation_type"], "operationalizes")
        source_node = next(node for node in data["nodes"] if node["id"] == "terms:source")
        self.assertEqual(source_node["type_zh"], build_knowledge_graph_data.TYPE_ZH["term"])
        self.assertNotEqual(source_node["color"], "#9CA3AF")

    def test_skips_relation_endpoints_that_are_not_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = root / "04-knowledge" / "units" / "persons"
            quality = root / "04-knowledge" / "quality"
            units.mkdir(parents=True)
            quality.mkdir(parents=True)
            (units / "person.md").write_text(
                "---\ntitle: Person\ntype: person\n---\n", encoding="utf-8"
            )
            (root / "04-knowledge" / "tables").mkdir(parents=True, exist_ok=True)
            (root / "04-knowledge" / "tables" / "relations.csv").write_text(
                rel_csv([{"source": "persons/person.md", "target": "claim/example.md", "relation_type": "supports"}]),
                encoding="utf-8",
            )

            data = build_knowledge_graph_data.build_graph(root)

        self.assertEqual(data["links"], [])
        self.assertEqual(data["stats"]["skipped_non_unit_relations"], 1)

    def test_data_script_exposes_graph_without_fetch(self):
        data = {"nodes": [{"id": "terms:example", "title": "示例"}], "links": [], "stats": {}}

        rendered = build_knowledge_graph_data.render_data_script(data)

        self.assertTrue(rendered.startswith("window.KNOWLEDGE_GRAPH_DATA="))
        self.assertIn('"terms:example"', rendered)

    def test_normalizes_yaml_dates_before_json_serialization(self):
        nested = {
            "sources": [{"accessed": date(2026, 9, 11)}],
            "evidence_ref": {"reviewed": date(2026, 9, 12)},
        }

        normalized = build_knowledge_graph_data.json_compatible(nested)
        rendered = build_knowledge_graph_data.render_data_script(normalized)

        self.assertEqual(normalized["sources"][0]["accessed"], "2026-09-11")
        self.assertEqual(normalized["evidence_ref"]["reviewed"], "2026-09-12")
        self.assertIn('"accessed":"2026-09-11"', rendered)

    def test_preserves_formal_hierarchy_and_topic_membership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = root / "04-knowledge" / "units" / "terms"
            quality = root / "04-knowledge" / "quality"
            theme_dir = root / "04-knowledge" / "structure" / "themes"
            units.mkdir(parents=True)
            quality.mkdir(parents=True)
            theme_dir.mkdir(parents=True)
            (units / "example.md").write_text(
                "---\ntitle: Example\ntype: term\nprimary_domain: domain-a\nprimary_dimension: B\nprimary_theme: B.2\ntopic_memberships:\n  - topic: topic-a\n    theme: B.2\n    role: example\n---\n",
                encoding="utf-8",
            )
            (theme_dir / "b2.md").write_text(
                "---\ntitle: Theme B2\nnode_type: theme\ntheme_code: B.2\nprimary_dimension: B\n---\n",
                encoding="utf-8",
            )
            (quality / "relation-index.yml").write_text("[]\n", encoding="utf-8")

            data = build_knowledge_graph_data.build_graph(root)

        self.assertEqual(data["nodes"][0]["topic_memberships"], [{"topic": "topic-a", "role": "example", "theme": "B.2"}])
        self.assertEqual(data["stats"]["hierarchy"]["topic_assigned"], 1)
        self.assertEqual(data["structure"]["themes"][0]["code"], "B.2")
