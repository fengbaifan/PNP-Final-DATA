import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import generate_claim_support_candidates as generator


class ClaimSupportCandidateGeneratorTests(unittest.TestCase):
    def test_collects_residual_rows_without_auto_approval_or_relation_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "works/source.md")
            claims = [{"claim_id": "claim-one", "source": {"doc_id": "doc-one"}}]
            rows = [
                {
                    "batch": "batch-29",
                    "source": "works/source.md",
                    "source_type": "work",
                    "target": "claim/claim-one",
                    "target_type": "claim",
                    "reason": "needs_claim_evidence",
                }
            ]

            candidates, blockers = generator.build_candidates(claims, rows, root)

        self.assertEqual(blockers, [])
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["signals"]["claim_source_doc_id"], "doc-one")
        self.assertEqual(candidates[0]["signals"]["source_unit_type"], "work")
        self.assertNotIn("approval_status", candidates[0])
        self.assertNotIn("relation_type", candidates[0])

    def test_routes_missing_claim_and_unit_to_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [
                {
                    "batch": "batch-29",
                    "source": "works/missing.md",
                    "target": "claim/missing-claim",
                    "target_type": "claim",
                }
            ]

            candidates, blockers = generator.build_candidates([], rows, root)

        self.assertEqual(candidates, [])
        self.assertIn("claim_missing", blockers[0]["blocker_reasons"])
        self.assertIn("source_unit_missing", blockers[0]["blocker_reasons"])

    def test_routes_existing_supported_by_binding_to_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "works/source.md")
            claims = [
                {
                    "claim_id": "claim-one",
                    "source": {"doc_id": "doc-one"},
                    "supported_by": ["works/source.md"],
                }
            ]
            rows = [
                {
                    "batch": "batch-29",
                    "source": "works/source.md",
                    "target": "claim/claim-one",
                    "target_type": "claim",
                }
            ]

            candidates, blockers = generator.build_candidates(claims, rows, root)

        self.assertEqual(candidates, [])
        self.assertIn("duplicate_supported_by_binding", blockers[0]["blocker_reasons"])

    def test_records_existing_source_span_as_signal_without_generating_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "terms/source.md")
            span = {"file": "02-sources/doc/ch01.md", "line_start": 10, "line_end": 12}
            claims = [{"claim_id": "claim-one", "source": {"doc_id": "doc-one", "source_span": span}}]
            rows = [
                {
                    "batch": "batch-29",
                    "source": "terms/source.md",
                    "source_type": "term",
                    "target": "claim/claim-one",
                    "target_type": "claim",
                }
            ]

            candidates, blockers = generator.build_candidates(claims, rows, root)

        self.assertEqual(blockers, [])
        self.assertEqual(candidates[0]["signals"]["claim_source_span"], span)
        self.assertNotIn("generated_source_span", candidates[0]["signals"])

    def test_resolves_legacy_claim_slug_through_migrated_from(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "works/source.md")
            claims = [
                {
                    "claim_id": "claim_legacy-slug",
                    "migrated_from": "ideas/legacy-slug.md",
                    "source": {"doc_id": "doc-one"},
                }
            ]
            rows = [
                {
                    "batch": "batch-29",
                    "source": "works/source.md",
                    "source_type": "work",
                    "target": "claim/legacy-slug.md",
                    "target_type": "claim",
                }
            ]

            candidates, blockers = generator.build_candidates(claims, rows, root)

        self.assertEqual(blockers, [])
        self.assertEqual(candidates[0]["claim_id"], "claim_legacy-slug")
        self.assertEqual(candidates[0]["residual_claim_slug"], "legacy-slug")

    def test_excludes_claim_with_complete_existing_binding_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "works/source.md")
            claims = [
                {
                    "claim_id": "claim-one",
                    "source": {"doc_id": "doc-one"},
                    "supports": ["evidence-one"],
                    "supported_by": ["works/other.md"],
                }
            ]
            rows = [
                {
                    "batch": "batch-29",
                    "source": "works/source.md",
                    "target": "claim/claim-one",
                    "target_type": "claim",
                }
            ]

            candidates, blockers, excluded = generator.build_candidates(
                claims,
                rows,
                root,
                exclude_complete_claims=True,
            )

        self.assertEqual(candidates, [])
        self.assertEqual(blockers, [])
        self.assertEqual(excluded[0]["excluded_reason"], "claim_already_has_complete_binding")

    def test_records_resolvable_unit_evidence_ref_as_signal_without_auto_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_file = root / "02-sources" / "doc-one" / "ch01.md"
            source_file.parent.mkdir(parents=True, exist_ok=True)
            source_file.write_text("source\n", encoding="utf-8")
            self.write_unit(
                root,
                "works/source.md",
                {
                    "sources": [
                        {
                            "evidence_ref": {
                                "evidence_id": "unit-evidence-one",
                                "source_file": "02-sources/doc-one/ch01.md",
                            }
                        }
                    ]
                },
            )
            claims = [{"claim_id": "claim-one", "source": {"doc_id": "doc-one"}}]
            rows = [
                {
                    "batch": "batch-29",
                    "source": "works/source.md",
                    "source_type": "work",
                    "target": "claim/claim-one",
                    "target_type": "claim",
                }
            ]

            candidates, blockers = generator.build_candidates(claims, rows, root)

        self.assertEqual(blockers, [])
        self.assertTrue(candidates[0]["signals"]["source_unit_evidence_ref_resolvable"])
        self.assertEqual(candidates[0]["signals"]["source_unit_evidence_ref"]["evidence_id"], "unit-evidence-one")
        self.assertNotIn("approval_status", candidates[0])

    @staticmethod
    def write_unit(root: Path, relative_path: str, frontmatter: dict | None = None) -> None:
        path = root / "04-knowledge" / "units" / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\n{yaml.safe_dump(frontmatter or {'title': path.stem}, allow_unicode=True)}---\nbody\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
