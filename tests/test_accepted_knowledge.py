from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import yaml

import io
import csv as _csv

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

from scripts import audit_repo, build_knowledge_graph_data
from scripts._accepted_knowledge import load_catalog


class AcceptedKnowledgeTests(unittest.TestCase):
    def test_empty_catalog_excludes_legacy_data_and_new_admission_updates_graph(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            units = base / "04-knowledge/units/terms"
            units.mkdir(parents=True)
            first = units / "first.md"
            second = units / "second.md"
            for path in (first, second):
                path.write_text(f"---\ntitle: {path.stem}\ntype: term\nsources: []\ncreated: 2026-09-09\nupdated: 2026-09-09\n---\n", encoding="utf-8")
            tables = base / "04-knowledge" / "tables"
            tables.mkdir(parents=True)
            (tables / "relations.csv").write_text(rel_csv([
                {"source": "terms/first.md", "target": "terms/second.md", "relation_type": "supports"}
            ]), encoding="utf-8")
            catalog = base / "04-knowledge/accepted.yml"
            catalog.write_text("units: []\nclaims: []\nstructure: []\n", encoding="utf-8")
            empty = build_knowledge_graph_data.build_graph(base)
            self.assertEqual(empty["nodes"], [])
            self.assertEqual(empty["stats"]["relation_index_total"], 0)
            self.assertEqual(audit_repo.iter_unit_files(base), [])
            self.assertEqual(audit_repo.relation_health_check(base)["relation_index_total"], 0)
            data = {"units": [first.relative_to(base).as_posix()], "claims": [], "structure": []}
            catalog.write_text(yaml.safe_dump(data), encoding="utf-8")
            self.assertEqual(build_knowledge_graph_data.build_graph(base)["stats"]["total_links"], 0)
            data["units"].append(second.relative_to(base).as_posix())
            catalog.write_text(yaml.safe_dump(data), encoding="utf-8")
            graph = build_knowledge_graph_data.build_graph(base)
            self.assertEqual(graph["stats"]["total_nodes"], 2)
            self.assertEqual(graph["stats"]["total_links"], 1)
            self.assertEqual(audit_repo.relation_health_check(base)["relation_index_total"], 1)
            topics = base / "04-knowledge/structure/topics"
            topics.mkdir(parents=True)
            topic = topics / "actual-topic.md"
            members = [{"ref": first.relative_to(base).as_posix(), "role": "supporting_case"}]
            topic.write_text("---\n" + yaml.safe_dump({"node_type": "topic", "title": "An observed question", "members": members, "basis": "Shared evidence"}) + "---\n", encoding="utf-8")
            data["structure"] = [topic.relative_to(base).as_posix()]
            catalog.write_text(yaml.safe_dump(data), encoding="utf-8")
            structure = build_knowledge_graph_data.build_graph(base)["structure"]
            self.assertEqual(structure["topics"][0]["members"], members)
            self.assertEqual(structure["themes"], [])
            self.assertEqual(structure["domains"], [])
            self.assertTrue(first.exists())  # Filtering never removes historical files.

    def test_bad_catalog_does_not_fall_back_to_all_files(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "04-knowledge").mkdir()
            catalog = base / "04-knowledge/accepted.yml"
            for text in ("units: null\nclaims: []\nstructure: []", "units: [../outside.md]\nclaims: []\nstructure: []"):
                catalog.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_catalog(base)
