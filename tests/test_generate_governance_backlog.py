import unittest

from scripts.generate_governance_backlog import gen_completed, gen_p0, gen_p1, gen_p1_ingest_coverage, gen_p2_content, gen_p2_runtime, generate_md


class GovernanceBacklogTranslationIndexTests(unittest.TestCase):
    def test_retired_semantic_density_proxy_does_not_create_backlog(self):
        health = {"content_quality": {"body_quality_issues": 22}}

        self.assertEqual(gen_p2_content(health), [])

    def test_completed_signals_do_not_count_as_active_items(self):
        health = {
            "summary": {"deprecated_type_drift": 0},
            "content_quality": {"total_findings": 0},
        }

        self.assertEqual(gen_p0(health), [])
        self.assertEqual(gen_p2_content(health), [])
        completed_ids = {item["id"] for item in gen_completed(health)}
        self.assertIn("C-SCHEMA", completed_ids)
        self.assertIn("C-CONTENT", completed_ids)

    def test_translation_index_drift_routes_to_p1(self):
        items = gen_p1(
            {
                "translation_index_integrity": {
                    "index_exists": True,
                    "expected": 2,
                    "indexed": 1,
                    "declared_total": 1,
                    "missing": ["persons/missing"],
                    "stale": [],
                    "duplicate": [],
                    "declared_total_mismatch": True,
                }
            }
        )

        self.assertIn("P1-TRANSLATION-INDEX-DRIFT", [item["id"] for item in items])

    def test_retired_fields_and_historical_inventory_do_not_create_p1(self):
        health = {
            "execution_scope": {
                "knowledge_inputs": "accepted_catalog",
                "processing_inventory_is_research_progress": False,
            },
            "translation_health": {
                "persons": {"total": 2, "coverage": {"name_original": "0/2"}},
            },
            "verification_schema": {
                "missing_verification_level_when_not_tentative": {"count": 2},
            },
            "dataflow_issues": ["legacy inventory"],
            "translation_index_integrity": {
                "index_exists": True,
                "expected": 2,
                "indexed": 2,
                "missing": [],
                "stale": [],
                "duplicate": [],
                "declared_total_mismatch": False,
            },
            "semantic_artifact_integrity": {"chapters_without_reading_ledger": ["legacy package"]},
            "recall_quality": {"chapters_without_candidate": ["legacy package"]},
        }

        self.assertEqual(gen_p1(health), [])
        self.assertEqual(gen_p1_ingest_coverage(health), [])

    def test_failed_rule_audit_is_not_reported_as_negative_drift(self):
        items = gen_p0({"rule_drift": {"findings": -1, "error": "import failed"}})

        self.assertEqual(items[0]["id"], "P0-RULE-AUDIT")
        self.assertEqual(items[0]["scope"], "import failed")

    def test_runtime_retention_gaps_route_to_p2(self):
        items = gen_p2_runtime(
            {
                "runtime_artifact_retention": {
                    "review_required": 2,
                    "ephemeral_residue": 1,
                }
            }
        )

        self.assertEqual(
            [entry["id"] for entry in items],
            ["P2-RUNTIME-R2-PROVENANCE", "P2-RUNTIME-EPHEMERAL"],
        )

    def test_backlog_dates_come_from_health_snapshot(self):
        markdown = generate_md(
            {
                "timestamp": "2020-01-02T03:04:05",
                "structural_health": {"total": 130, "max_score": 130},
                "summary": {"total_units": 1, "hierarchy_version": "v6.1"},
                "rule_authority": {
                    "legacy_references": 0,
                    "claude_settings_exists": False,
                    "claude_active_skills_exists": False,
                },
                "verification_semantic_issues": {},
                "verification_state_conflicts": [],
                "required_field_missing": {},
                "body_only_field_issues": [],
                "chunk_meta": {"chunk_meta_missing": 0},
                "verification_schema": {"missing_evidence_status": {"count": 0}},
                "dataflow_issues": [],
            }
        )

        self.assertIn("Snapshot: 2020-01-02 03:04", markdown)
        self.assertIn("| 2020-01-02 | completed |", markdown)


if __name__ == "__main__":
    unittest.main()
