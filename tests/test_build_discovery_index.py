import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import build_discovery_index


def candidate(candidate_id: str, origin_type: str = "relation_graph", candidate_type: str = "relation") -> dict:
    return {
        "candidate_id": candidate_id,
        "origin_type": origin_type,
        "origin_ref": "fixture",
        "candidate_type": candidate_type,
        "target_ref": "terms/example.md",
        "payload": {},
        "evidence_refs": [],
        "state": "needs_evidence",
        "lifecycle_class": "active",
        "decision": {"status": "pending", "reason": None, "decided_by": None, "decided_at": None},
        "created_at": "2026-08-01",
        "updated_at": "2026-08-01",
    }


class DiscoveryIndexTests(unittest.TestCase):
    def test_topic_candidate_type_is_accepted(self):
        item = candidate("topic-a", candidate_type="topic")
        self.assertEqual(build_discovery_index.validate_candidate(item), [])

    def test_cluster_candidate_requires_cross_layer_discovery_contract(self):
        invalid = candidate("cluster-invalid", candidate_type="cluster")
        issues = build_discovery_index.validate_candidate(invalid)
        self.assertTrue(any("cluster payload missing target_level" in issue for issue in issues))

        valid = candidate("cluster-valid", candidate_type="cluster")
        valid["payload"] = {
            "target_level": "topic",
            "scope": "current-domain",
            "basis": "semantic similarity plus relation density",
            "input_snapshot": {"hash": "sha256:example"},
            "members": ["terms/example.md", "works/example.md"],
            "boundary": "Excludes merely co-tagged objects.",
            "counterexamples": [],
            "stability_across_runs": "provisional",
        }
        self.assertEqual(build_discovery_index.validate_candidate(valid), [])

    def test_cross_origin_candidates_share_one_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relation = root / "04-knowledge" / "quality" / "relation-candidates.yml"
            relation.parent.mkdir(parents=True)
            relation.write_text(yaml.safe_dump([candidate("relation-a")]), encoding="utf-8")
            processing = root / "03-processing" / "example" / "candidate-ledger.jsonl"
            processing.parent.mkdir(parents=True)
            processing.write_text(json.dumps(candidate("source-a", "source")) + "\n", encoding="utf-8")
            (root / "06-runtime" / "automation").mkdir(parents=True)

            candidates, manifest = build_discovery_index.build(root)

        self.assertEqual([item["candidate_id"] for item in candidates], ["relation-a", "source-a"])
        self.assertEqual(manifest["candidate_counts"]["by_origin_type"], {"relation_graph": 1, "source": 1})
        self.assertEqual(manifest["actionable_candidate_counts"]["total"], 2)
        self.assertEqual(manifest["issues"], [])

    def test_conflicting_duplicate_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relation = root / "04-knowledge" / "quality" / "relation-candidates.yml"
            relation.parent.mkdir(parents=True)
            relation.write_text(yaml.safe_dump([candidate("same")]), encoding="utf-8")
            runtime = root / "06-runtime" / "automation" / "batch" / "candidate-ledger.jsonl"
            runtime.parent.mkdir(parents=True)
            other = candidate("same")
            other["target_ref"] = "terms/different.md"
            runtime.write_text(json.dumps(other) + "\n", encoding="utf-8")
            (root / "03-processing").mkdir(parents=True)

            _, manifest = build_discovery_index.build(root)

        self.assertIn("same: conflicting duplicate definitions", manifest["issues"])

    def test_malformed_candidate_reports_schema_issue_without_crashing_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "06-runtime" / "automation" / "batch" / "candidate-ledger.jsonl"
            runtime.parent.mkdir(parents=True)
            malformed = candidate("missing-origin")
            malformed.pop("origin_type")
            runtime.write_text(json.dumps(malformed) + "\n", encoding="utf-8")
            (root / "03-processing").mkdir(parents=True)

            _, manifest = build_discovery_index.build(root)

        self.assertIn("missing-origin: missing origin_type", manifest["issues"])
        self.assertEqual(manifest["candidate_counts"]["by_origin_type"], {"<missing>": 1})

    def test_legacy_state_spellings_are_normalized_in_current_projection(self):
        item = candidate("legacy", origin_type="source", candidate_type="unit")
        item.pop("lifecycle_class")
        item["state"] = "applied"
        item["decision"] = {"status": "applied", "reason": "legacy", "decided_at": "2026-08-01"}
        item["payload"] = {
            "knowledge_match": {"status": "existing", "target_refs": ["terms/example.md"]}
        }

        normalized, changes = build_discovery_index.canonical_candidate(item)

        self.assertEqual(normalized["decision"]["status"], "approved")
        self.assertEqual(normalized["decision"]["decided_by"], "legacy-record-unattributed")
        self.assertEqual(normalized["payload"]["knowledge_match"]["status"], "existing_target")
        self.assertEqual(normalized["lifecycle_class"], "terminal")
        self.assertIn("decision_applied_to_approved", changes)

    def test_read_only_legacy_defer_is_not_actionable_debt(self):
        item = candidate("legacy-defer", origin_type="source", candidate_type="unit")
        item.pop("lifecycle_class")
        item["state"] = "deferred"
        item["decision"]["status"] = "deferred"
        item["payload"] = {"migration_mode": "read_only_reference"}

        normalized, _ = build_discovery_index.canonical_candidate(item)

        self.assertEqual(normalized["lifecycle_class"], "historical_non_replay")

    def test_retired_relation_signal_cannot_reenter_active_backlog(self):
        for signal in ("s2_legacy_related", "s8_same_structure"):
            item = candidate(f"retired-{signal}")
            item["payload"] = {"signal": signal}

            issues = build_discovery_index.validate_candidate(item)

            self.assertIn(
                f"retired-{signal}: retired relation signal cannot remain active",
                issues,
            )

            item["state"] = "rejected"
            item["decision"] = {
                "status": "rejected",
                "reason": "The signal was retired after semantic calibration.",
                "decided_by": "Codex",
                "decided_at": "2026-08-08",
            }
            normalized, _ = build_discovery_index.canonical_candidate(item)
            self.assertEqual(normalized["lifecycle_class"], "terminal")
            self.assertNotIn(
                f"retired-{signal}: retired relation signal cannot remain active",
                build_discovery_index.validate_candidate(normalized),
            )

    def test_append_only_candidate_transition_updates_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "03-processing" / "example" / "candidate-ledger.jsonl"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps(candidate("creator-a", "source", "unit")) + "\n", encoding="utf-8")
            transition_path = (
                root / "06-runtime" / "automation" / "batch" / "candidate-decision-ledger.jsonl"
            )
            transition_path.parent.mkdir(parents=True)
            transition = {
                "candidate_id": "creator-a",
                "expected_state": "needs_evidence",
                "state": "deferred",
                "decision": {
                    "status": "deferred",
                    "reason": "Identity remains ambiguous.",
                    "decided_by": "Codex",
                    "decided_at": "2026-08-09",
                },
                "updated_at": "2026-08-09",
            }
            transition_path.write_text(json.dumps(transition) + "\n", encoding="utf-8")

            candidates, manifest = build_discovery_index.build(root)

        self.assertEqual(candidates[0]["state"], "deferred")
        self.assertEqual(candidates[0]["decision"]["status"], "deferred")
        self.assertEqual(manifest["applied_candidate_transition_counts"], {"needs_evidence->deferred": 1})
        self.assertEqual(manifest["issues"], [])

    def test_candidate_transition_rejects_unknown_or_stale_expected_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "03-processing" / "example" / "candidate-ledger.jsonl"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps(candidate("creator-a", "source", "unit")) + "\n", encoding="utf-8")
            transition_path = (
                root / "06-runtime" / "automation" / "batch" / "candidate-decision-ledger.jsonl"
            )
            transition_path.parent.mkdir(parents=True)
            stale = {
                "candidate_id": "creator-a",
                "expected_state": "approved",
                "state": "deferred",
                "decision": {
                    "status": "deferred",
                    "reason": "stale transition",
                    "decided_by": "Codex",
                    "decided_at": "2026-08-09",
                },
                "updated_at": "2026-08-09",
            }
            unknown = dict(stale, candidate_id="unknown", expected_state="needs_evidence")
            transition_path.write_text(
                json.dumps(stale) + "\n" + json.dumps(unknown) + "\n", encoding="utf-8"
            )

            candidates, manifest = build_discovery_index.build(root)

        self.assertEqual(candidates[0]["state"], "needs_evidence")
        self.assertTrue(any("transition expected state approved but found needs_evidence" in issue for issue in manifest["issues"]))
        self.assertTrue(any("unknown candidate unknown" in issue for issue in manifest["issues"]))
