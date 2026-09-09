import tempfile
import unittest
from pathlib import Path

from scripts import audit_relation_consistency as audit
from scripts import audit_repo


class GenericEvidenceBackedAuditTest(unittest.TestCase):
    def test_only_unbaselined_generic_evidence_backed_relation_is_flagged(self):
        grandfathered = {
            "source": "terms/existing.md",
            "target": "terms/term.md",
            "relation_type": "relates_to_term",
            "relation_source": "explicit",
            "review_status": "evidence_backed_relation",
        }
        new_generic = {
            "source": "terms/new.md",
            "target": "terms/term.md",
            "relation_type": "relates_to_term",
            "relation_source": "explicit",
            "review_status": "evidence_backed_relation",
        }
        precise = {
            "source": "terms/derived.md",
            "target": "terms/term.md",
            "relation_type": "derived_from",
            "relation_source": "explicit",
            "review_status": "evidence_backed_relation",
        }

        issues = audit.find_unbaselined_generic_evidence_backed(
            [grandfathered, new_generic, precise],
            [grandfathered],
        )

        self.assertEqual(issues, [new_generic])


class RelationAuditExitGateTests(unittest.TestCase):
    def test_commissioner_relation_pair_is_controlled_vocabulary(self):
        self.assertIn("commissioner_of", audit.VALID_TYPES)
        self.assertIn("commissioned_by", audit.VALID_TYPES)
        self.assertEqual(audit.INVERSE_MAP["commissioner_of"], "commissioned_by")
        self.assertEqual(audit.INVERSE_MAP["commissioned_by"], "commissioner_of")

    def test_blocks_all_relation_integrity_failures(self):
        issues = {
            "broken_target": [{"target": "works/missing.md"}],
            "invalid_relation_type": [{"relation_type": "unsupported"}],
            "missing_inverse": [{"relation_type": "supports_claim"}],
            "weak_evidence": [{"relation_type": "derived_from"}],
            "unbaselined_generic_evidence_backed": [{"relation_type": "related_to"}],
        }

        self.assertEqual(audit.blocking_issue_count(issues), 5)

    def test_does_not_block_on_review_signals(self):
        self.assertEqual(
            audit.blocking_issue_count(
                {
                    "broken_target": [],
                    "invalid_relation_type": [],
                    "missing_inverse": [],
                    "weak_evidence": [],
                    "unbaselined_generic_evidence_backed": [],
                }
            ),
            0,
        )

    def test_weak_association_does_not_require_generated_inverse(self):
        self.assertFalse(audit.requires_inverse({
            "relation_type": "cites",
            "review_status": "weak_association",
            "bidirectional_required": True,
        }))

    def test_evidence_ref_satisfies_relation_evidence_gate(self):
        self.assertTrue(audit.has_direct_relation_evidence({
            "evidence_ref": {
                "doc_id": "source-example",
                "source_file": "02-sources/example/original.md",
            }
        }))

    def test_empty_evidence_fields_do_not_satisfy_gate(self):
        self.assertFalse(audit.has_direct_relation_evidence({
            "evidence": "",
            "evidence_ref": None,
            "claim_id": None,
        }))


class ClaimLinkAuditTests(unittest.TestCase):
    def test_recognizes_hyphen_and_underscore_claim_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            registry = root / "04-knowledge" / "quality" / "claim-registry.yml"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                "- claim_id: claim-hyphenated-id\n"
                "- claim_id: claim_underscored_id\n",
                encoding="utf-8",
            )

            self.assertEqual(
                audit_repo._registry_claim_slugs(root),
                {"hyphenated-id", "underscored_id"},
            )


if __name__ == "__main__":
    unittest.main()
