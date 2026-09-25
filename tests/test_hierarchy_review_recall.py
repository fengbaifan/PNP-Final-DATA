import hashlib

HDR = 'relation_id,subject_ku_id,object_ku_id,predicate,direction,time,role,scope,origin,status,evidence_doc_id,evidence_source_file,evidence_span'
import json
import tempfile
from pathlib import Path

import yaml

from scripts import hierarchy_stress_test


def write_unit(
    path: Path,
    *,
    title: str,
    doc_id: str,
    chapter: str,
    unit_type: str = "term",
    membership: str | None = None,
) -> None:
    hierarchy = ""
    if membership:
        hierarchy = (
            "primary_domain: test-domain\n"
            "primary_dimension: B\n"
            "primary_theme: B.1\n"
            "topic_memberships:\n"
            f"  - topic: {membership}\n"
            "    role: term_anchor\n"
            "    primary: true\n"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"title: {title}\n"
        f"type: {unit_type}\n"
        "sub_type: chart_type\n"
        "tags: [comparison]\n"
        "sources:\n"
        "  - citation: Example source\n"
        "    evidence_ref:\n"
        f"      doc_id: {doc_id}\n"
        f"      chapter_id: {chapter}\n"
        f"      source_file: 02-sources/{doc_id}/{chapter}.md\n"
        f"{hierarchy}"
        "---\n"
        f"## 描述\n\n{title} supports comparison.\n",
        encoding="utf-8",
    )


def test_source_review_queue_clusters_and_recalls_without_approving():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        units = root / "04-knowledge" / "units"
        topics = root / "04-knowledge" / "structure" / "topics"
        relation_index = root / "04-knowledge" / "tables" / "relations.csv"
        topic = topics / "comparison-topic.md"
        topic.parent.mkdir(parents=True)
        topic.write_text(
            "---\n"
            "title: How are comparisons standardized?\n"
            "node_type: topic\n"
            "primary_domain: test-domain\n"
            "primary_dimension: B\n"
            "parent_theme: B.1\n"
            "tags: [comparison]\n"
            "---\n"
            "## 研究问题\n\nHow are comparisons standardized?\n",
            encoding="utf-8",
        )
        write_unit(
            units / "terms" / "candidate-a.md",
            title="Candidate A",
            doc_id="source-book",
            chapter="ch01",
        )
        write_unit(
            units / "terms" / "candidate-b.md",
            title="Candidate B",
            doc_id="source-book",
            chapter="ch02",
        )
        write_unit(
            units / "terms" / "reviewed-neighbor.md",
            title="Reviewed Neighbor",
            doc_id="source-book",
            chapter="ch01",
            membership="topics/comparison-topic.md",
        )
        relation_only = units / "terms" / "relation-only.md"
        relation_only.write_text(
            "---\n"
            "title: Relation Only\n"
            "type: term\n"
            "sources:\n"
            "  - citation: Different source\n"
            "    evidence_ref:\n"
            "      doc_id: different-book\n"
            "      source_file: 02-sources/different-book/ch01.md\n"
            "relations:\n"
            "  - target: ../terms/reviewed-neighbor.md\n"
            "    relation_type: related_to\n"
            "    evidence_ref:\n"
            "      doc_id: source-book\n"
            "      source_file: 02-sources/source-book/ch01.md\n"
            "---\n"
            "## 描述\n\nA relation citation is not direct source support.\n",
            encoding="utf-8",
        )
        unlocated = units / "terms" / "unlocated-source.md"
        unlocated.write_text(
            "---\n"
            "title: Unlocated Source\n"
            "type: term\n"
            "sources:\n"
            "  - citation: Source without a locator\n"
            "    evidence_ref:\n"
            "      doc_id: source-book\n"
            "---\n"
            "## 描述\n\nA doc id without a source file is not replayable support.\n",
            encoding="utf-8",
        )
        relation_index.parent.mkdir(parents=True)
        relation_index.write_text(
            HDR + "\nrel-1,units/terms/candidate-a,units/terms/reviewed-neighbor,related_to,forward,,,,book,formal,,,\n",
            encoding="utf-8",
        )
        output = root / "06-runtime" / "automation" / "batch" / "hierarchy-review-queue.jsonl"
        manifest = output.with_name("recall-generation-manifest.json")

        count = hierarchy_stress_test.write_source_hierarchy_review_queue(
            output=output,
            manifest_output=manifest,
            source_doc_id="source-book",
            review_date="2026-08-04",
            checkpoint_size=1,
            recall_limit=3,
            units=units,
            topics=topics,
            relation_index=relation_index,
            root=root,
            generator_path=Path(hierarchy_stress_test.__file__),
        )

        records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        provenance = json.loads(manifest.read_text(encoding="utf-8"))
        queue_hash = hashlib.sha256(output.read_bytes()).hexdigest().upper()

    assert count == 2
    assert [record["payload"]["checkpoint"] for record in records] == ["checkpoint-01", "checkpoint-02"]
    assert records[0]["state"] == "ready_for_review"
    assert records[0]["decision"]["status"] == "pending"
    assert records[0]["apply_permitted"] is False
    assert records[0]["payload"]["candidate_topics"][0]["topic"] == "topics/comparison-topic.md"
    assert "terms/reviewed-neighbor.md" in records[0]["payload"]["candidate_topics"][0]["basis"]["relation_neighbors"]
    assert all(record["target_ref"].endswith(("candidate-a.md", "candidate-b.md")) for record in records)
    assert provenance["selection"]["selected_units"] == 2
    assert provenance["inputs"]["ku_state"]["file_count"] == 5
    assert provenance["outputs"][0]["sha256"] == queue_hash
    assert "no Topic membership is approved or applied" in provenance["semantic_boundary"]


def test_source_review_queue_can_select_one_explicit_unit_type():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        units = root / "04-knowledge" / "units"
        topics = root / "04-knowledge" / "structure" / "topics"
        relation_index = root / "04-knowledge" / "tables" / "relations.csv"
        topics.mkdir(parents=True)
        relation_index.parent.mkdir(parents=True)
        relation_index.write_text(HDR + "\n", encoding="utf-8")
        write_unit(
            units / "terms" / "term-a.md",
            title="Term A",
            doc_id="source-book",
            chapter="ch01",
        )
        write_unit(
            units / "persons" / "person-a.md",
            title="Person A",
            doc_id="source-book",
            chapter="ch01",
            unit_type="person",
        )
        output = root / "06-runtime" / "automation" / "batch" / "hierarchy-review-queue.jsonl"
        manifest = output.with_name("recall-generation-manifest.json")

        count = hierarchy_stress_test.write_source_hierarchy_review_queue(
            output=output,
            manifest_output=manifest,
            source_doc_id="source-book",
            review_date="2026-08-05",
            unit_type_filter="person",
            units=units,
            topics=topics,
            relation_index=relation_index,
            root=root,
            generator_path=Path(hierarchy_stress_test.__file__),
        )

        records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        provenance = json.loads(manifest.read_text(encoding="utf-8"))

    assert count == 1
    assert records[0]["target_ref"].endswith("persons/person-a.md")
    assert records[0]["payload"]["unit_type"] == "person"
    assert provenance["invocation"]["unit_type_filter"] == "person"
    assert provenance["selection"]["unit_type_filter"] == "person"
    assert "--unit-type" in provenance["invocation"]["rebuild_command"]


def test_decision_log_requires_exact_agent_authored_coverage():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        queue = root / "queue.jsonl"
        decision_map = root / "decision-map.yml"
        output = root / "decision-log.jsonl"
        queue.write_text(
            json.dumps(
                {
                    "candidate_id": "hierarchy:book:terms/a.md",
                    "origin_type": "source",
                    "origin_ref": "book",
                    "candidate_type": "hierarchy_change",
                    "target_ref": "04-knowledge/units/terms/a.md",
                    "payload": {
                        "checkpoint": "checkpoint-01",
                        "unit_sha256": "A" * 64,
                        "candidate_topics": [{"topic": "topics/recalled.md"}],
                    },
                    "created_at": "2026-08-04",
                },
                ensure_ascii=False,
            )
            + "\n"
            + json.dumps(
                {
                    "candidate_id": "hierarchy:book:terms/b.md",
                    "origin_type": "source",
                    "origin_ref": "book",
                    "candidate_type": "hierarchy_change",
                    "target_ref": "04-knowledge/units/terms/b.md",
                    "payload": {
                        "checkpoint": "checkpoint-01",
                        "unit_sha256": "B" * 64,
                        "candidate_topics": [],
                    },
                    "created_at": "2026-08-04",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        decision_map.write_text(
            "reviewed_by: Codex-Agent\n"
            "reviewed_at: 2026-08-04\n"
            "topics:\n"
            "  - topic: topics/approved.md\n"
            "    reason: Agent read the object and approved this boundary.\n"
            "    members:\n"
            "      04-knowledge/units/terms/a.md: term_anchor\n"
            "deferred:\n"
            "  04-knowledge/units/terms/b.md: Evidence is insufficient for a Topic.\n",
            encoding="utf-8",
        )

        count = hierarchy_stress_test.materialize_hierarchy_decision_log(
            queue_input=queue,
            decision_map=decision_map,
            output=output,
        )
        rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

    assert count == 2
    assert rows[0]["state"] == "approved"
    assert rows[0]["decision"]["memberships"] == [
        {"primary": True, "role": "term_anchor", "topic": "topics/approved.md"}
    ]
    assert rows[0]["automatic_recall"] == ["topics/recalled.md"]
    assert rows[1]["state"] == "deferred"
    assert rows[1]["decision"]["memberships"] == []
    assert all(row["apply_permitted"] is False for row in rows)


def test_plan_materializer_preserves_decisions_and_excludes_other_topic_links():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        topics = root / "04-knowledge" / "structure" / "topics"
        units = root / "04-knowledge" / "units" / "terms"
        topics.mkdir(parents=True)
        units.mkdir(parents=True)
        topic = topics / "approved.md"
        topic.write_text(
            "---\n"
            "title: Approved Topic\n"
            "node_type: topic\n"
            "primary_domain: test-domain\n"
            "primary_dimension: B\n"
            "parent_theme: B.1\n"
            "---\n"
            "- [A](../../units/terms/a.md)\n"
            "- [B](../../units/terms/b.md)\n",
            encoding="utf-8",
        )
        for name in ("a", "b"):
            (units / f"{name}.md").write_text(
                f"---\ntitle: {name}\ntype: term\n---\n## 描述\n\n{name}\n",
                encoding="utf-8",
            )
        decision_log = root / "decision-log.jsonl"
        decision_log.write_text(
            json.dumps(
                {
                    "target_ref": "04-knowledge/units/terms/a.md",
                    "state": "approved",
                    "apply_permitted": False,
                    "decision": {
                        "status": "approved",
                        "reason": "Agent approved A as a boundary case.",
                        "decided_by": "Codex-Agent",
                        "decided_at": "2026-08-04",
                        "memberships": [
                            {"topic": "topics/approved.md", "role": "boundary_case", "primary": True}
                        ],
                    },
                },
                ensure_ascii=False,
            )
            + "\n"
            + json.dumps(
                {
                    "target_ref": "04-knowledge/units/terms/b.md",
                    "state": "deferred",
                    "apply_permitted": False,
                    "decision": {
                        "status": "deferred",
                        "reason": "Evidence is insufficient.",
                        "decided_by": "Codex-Agent",
                        "decided_at": "2026-08-04",
                        "memberships": [],
                    },
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        output = root / "topic-membership-plan.yml"

        result = hierarchy_stress_test.materialize_topic_membership_plan(
            decision_log=decision_log,
            output=output,
            base_commit="a" * 40,
            batch_label="Batch Test",
            topics=topics,
            root=root,
        )
        plan = yaml.safe_load(output.read_text(encoding="utf-8"))

    assert result["approved_units"] == 1
    assert result["deferred_units"] == 1
    assert plan["existing_hierarchy_policy"] == "merge"
    assert plan["topics"][0]["exclude"] == {
        "04-knowledge/units/terms/b.md": "既有或非本批显式材料链接；保留当前状态，不在 Batch Test 中重写。"
    }
    assert plan["topics"][0]["role_overrides"]["04-knowledge/units/terms/a.md"] == "boundary_case"
    assert plan["hierarchy_overrides"]["04-knowledge/units/terms/a.md"]["role_in_theme"] == "boundary_case"
